"""
Reporter - 报告生成模块
生成筛选报告（CSV/Excel/JSON格式）
"""

import os
import logging
from datetime import datetime
from typing import List, Dict
import pandas as pd
from pathlib import Path
import json


class Reporter:
    """报告生成器"""
    
    def __init__(self, output_dir: str = 'reports'):
        """
        初始化报告生成器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self, results: List[Dict], format: str = 'both', 
                       include_details: bool = True) -> str:
        """
        生成筛选报告
        
        Args:
            results: 筛选结果列表
            format: 输出格式 (csv, excel, both)
            include_details: 是否包含详细信息
        
        Returns:
            str: 报告文件路径
        """
        if not results:
            self.logger.warning("没有筛选结果，不生成报告")
            return None
        
        # 转换为DataFrame
        df = self._results_to_dataframe(results, include_details)
        
        # 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"stock_screening_{timestamp}"
        
        saved_files = []
        
        # 保存为CSV
        if format in ['csv', 'both']:
            csv_path = self.output_dir / f"{base_filename}.csv"
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            saved_files.append(str(csv_path))
            self.logger.info(f"CSV报告已保存: {csv_path}")
        
        # 保存为Excel
        if format in ['excel', 'both']:
            excel_path = self.output_dir / f"{base_filename}.xlsx"
            self._save_excel_report(df, excel_path)
            saved_files.append(str(excel_path))
            self.logger.info(f"Excel报告已保存: {excel_path}")
        
        return saved_files[0] if saved_files else None
    
    def _results_to_dataframe(self, results: List[Dict], 
                             include_details: bool = True) -> pd.DataFrame:
        """
        将筛选结果转换为DataFrame
        
        Args:
            results: 筛选结果列表
            include_details: 是否包含详细信息
        
        Returns:
            pd.DataFrame: 整理后的数据
        """
        rows = []
        
        for result in results:
            row = {
                '股票代码': result.get('ticker', ''),
                '信号类型': result.get('signal', ''),
                '当前价格': result.get('price', 0),
            }
            
            # 添加详细信息
            if include_details and 'details' in result:
                details = result['details']
                if isinstance(details, dict):
                    for key, value in details.items():
                        # 转换键名为中文（可选）
                        column_name = self._translate_key(key)
                        row[column_name] = value
                else:
                    row['详细信息'] = str(details)
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # 添加生成时间
        df.insert(0, '筛选时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return df
    
    def _translate_key(self, key: str) -> str:
        """
        翻译字段名为中文
        
        Args:
            key: 英文键名
        
        Returns:
            str: 中文键名
        """
        translation_map = {
            'short_ma': '短期均线',
            'long_ma': '长期均线',
            'volume_ratio': '成交量倍数',
            'price_change': '涨跌幅(%)',
            'volume': '成交量',
            'recent_high': '前期高点',
            'breakout_pct': '突破幅度(%)',
            'rsi': 'RSI指标',
            'rsi_prev': '前日RSI',
            'macd': 'MACD',
            'signal_line': '信号线',
        }
        
        return translation_map.get(key, key)
    
    def _save_excel_report(self, df: pd.DataFrame, file_path: Path):
        """
        保存Excel报告并添加格式化
        
        Args:
            df: 数据DataFrame
            file_path: 文件路径
        """
        try:
            # 创建Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='筛选结果')
                
                # 获取worksheet对象
                worksheet = writer.sheets['筛选结果']
                
                # 自动调整列宽
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # 冻结首行
                worksheet.freeze_panes = 'A2'
            
            self.logger.info(f"Excel报告已格式化并保存")
            
        except Exception as e:
            self.logger.error(f"保存Excel报告时出错: {e}")
            # 如果失败，使用简单保存
            df.to_excel(file_path, index=False)
    
    def generate_summary_report(self, all_results: Dict[str, List[Dict]], 
                               format: str = 'both') -> str:
        """
        生成汇总报告（按策略分类）
        
        Args:
            all_results: 所有策略的结果 {strategy_name: results}
            format: 输出格式
        
        Returns:
            str: 报告文件路径
        """
        if not all_results:
            self.logger.warning("没有结果，不生成汇总报告")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format in ['excel', 'both']:
            # Excel格式：多个sheet
            excel_path = self.output_dir / f"summary_report_{timestamp}.xlsx"
            
            try:
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    # 创建汇总sheet
                    summary_data = []
                    for strategy_name, results in all_results.items():
                        summary_data.append({
                            '策略名称': strategy_name,
                            '筛选数量': len(results)
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='汇总', index=False)
                    
                    # 为每个策略创建单独的sheet
                    for strategy_name, results in all_results.items():
                        if results:
                            df = self._results_to_dataframe(results, include_details=True)
                            # 限制sheet名称长度
                            sheet_name = strategy_name[:31]
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                self.logger.info(f"汇总报告已保存: {excel_path}")
                return str(excel_path)
                
            except Exception as e:
                self.logger.error(f"生成Excel汇总报告时出错: {e}")
        
        # CSV格式：合并所有结果
        if format in ['csv', 'both']:
            all_rows = []
            for strategy_name, results in all_results.items():
                for result in results:
                    result_copy = result.copy()
                    result_copy['strategy'] = strategy_name
                    all_rows.append(result_copy)
            
            if all_rows:
                df = self._results_to_dataframe(all_rows, include_details=True)
                csv_path = self.output_dir / f"summary_report_{timestamp}.csv"
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                self.logger.info(f"CSV汇总报告已保存: {csv_path}")
                return str(csv_path)
        
        return None
    
    def get_report_history(self, days: int = 7) -> List[str]:
        """
        获取最近的报告历史
        
        Args:
            days: 查询最近几天的报告
        
        Returns:
            List[str]: 报告文件路径列表
        """
        reports = []
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for file_path in self.output_dir.glob('*.csv'):
            if file_path.stat().st_mtime >= cutoff_time:
                reports.append(str(file_path))
        
        for file_path in self.output_dir.glob('*.xlsx'):
            if file_path.stat().st_mtime >= cutoff_time:
                reports.append(str(file_path))
        
        # 按修改时间排序
        reports.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return reports
    
    def clean_old_reports(self, keep_days: int = 30):
        """
        清理旧报告
        
        Args:
            keep_days: 保留最近几天的报告
        """
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
        deleted_count = 0
        
        for file_path in self.output_dir.glob('*.csv'):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted_count += 1
        
        for file_path in self.output_dir.glob('*.xlsx'):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            self.logger.info(f"已清理 {deleted_count} 个旧报告")
    
    def generate_json_report(self, results: List[Dict], 
                            output_path: str = None) -> str:
        """
        生成JSON格式报告
        
        Args:
            results: 筛选结果（来自scoring_engine的标准格式）
            output_path: 输出路径（可选）
        
        Returns:
            str: JSON文件路径
        """
        if not results:
            self.logger.warning("没有结果，不生成JSON报告")
            return None
        
        # 生成文件名
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"screening_results_{timestamp}.json"
        
        # 添加报告元数据
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_stocks': len(results),
                'report_version': '1.0.0',
                'level': 'Level 1 Hard Screening'
            },
            'results': results
        }
        
        # 保存JSON
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON报告已保存: {output_path}")
            return str(output_path)
        
        except Exception as e:
            self.logger.error(f"保存JSON报告失败: {e}")
            return None

