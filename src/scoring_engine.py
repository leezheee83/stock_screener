"""
Scoring Engine - 综合评分引擎
整合流动性、趋势、策略信号的综合评分
"""

import logging
from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime


class ScoringEngine:
    """综合评分引擎"""
    
    def __init__(self, config: dict):
        """
        初始化综合评分引擎
        
        Args:
            config: {
                'weights': {
                    'liquidity': 0.20,
                    'trend': 0.30,
                    'signal': 0.40,
                    'multi_strategy': 0.10
                },
                'output_count': 20
            }
        """
        self.config = config
        self.weights = config.get('weights', {
            'liquidity': 0.20,
            'trend': 0.30,
            'signal': 0.40,
            'multi_strategy': 0.10
        })
        self.output_count = config.get('output_count', 20)
        self.logger = logging.getLogger(__name__)
    
    def score_all(self, 
                  liquidity_scores: Dict[str, float],
                  trend_scores: Dict[str, Dict],
                  strategy_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        综合评分并排序
        
        Args:
            liquidity_scores: {ticker: liquidity_score}
            trend_scores: {ticker: trend_score_dict}
            strategy_results: {strategy_name: [results]}
        
        Returns:
            排序后的Top N股票列表
        """
        # 1. 整合所有策略信号，按股票分组
        ticker_signals = self._group_signals_by_ticker(strategy_results)
        
        self.logger.info(f"共有 {len(ticker_signals)} 只股票触发了策略信号")
        
        # 2. 为每只股票计算综合得分
        all_scores = []
        
        for ticker in ticker_signals.keys():
            # 确保该股票有流动性和趋势得分
            if ticker not in liquidity_scores or ticker not in trend_scores:
                self.logger.debug(f"{ticker}: 缺少流动性或趋势得分，跳过")
                continue
            
            score_result = self._calculate_final_score(
                ticker,
                liquidity_scores[ticker],
                trend_scores[ticker],
                ticker_signals[ticker]
            )
            
            all_scores.append(score_result)
        
        # 3. 按总分排序
        all_scores.sort(key=lambda x: x['final_score']['total'], reverse=True)
        
        # 4. 取Top N
        top_n = all_scores[:self.output_count]
        
        # 5. 添加排名和置信度
        for rank, item in enumerate(top_n, 1):
            item['final_score']['rank'] = rank
            item['final_score']['confidence'] = self._calculate_confidence(item)
        
        self.logger.info(f"综合评分完成，共 {len(all_scores)} 只股票，输出Top {len(top_n)}")
        
        return top_n
    
    def _group_signals_by_ticker(self, strategy_results: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        将策略信号按股票分组
        
        Args:
            strategy_results: {strategy_name: [results]}
        
        Returns:
            {ticker: [signals]}
        """
        ticker_signals = {}
        
        for strategy_name, results in strategy_results.items():
            for result in results:
                ticker = result['ticker']
                if ticker not in ticker_signals:
                    ticker_signals[ticker] = []
                
                ticker_signals[ticker].append({
                    'strategy': strategy_name,
                    'signal': result['signal'],
                    'price': result['price'],
                    'details': result.get('details', {})
                })
        
        return ticker_signals
    
    def _calculate_final_score(self,
                               ticker: str,
                               liquidity_score: float,
                               trend_score: Dict,
                               signals: List[Dict]) -> Dict:
        """
        计算单只股票的最终得分
        
        Args:
            ticker: 股票代码
            liquidity_score: 流动性得分
            trend_score: 趋势得分字典
            signals: 策略信号列表
        
        Returns:
            完整的得分结果
        """
        # 1. 流动性得分 (已经是0-100)
        liq_score = liquidity_score
        
        # 2. 趋势得分 (已经是0-100)
        trend_total = trend_score['total']
        
        # 3. 策略信号得分 (0-100)
        signal_score = self._score_signals(signals)
        
        # 4. 多策略共振得分 (0-100)
        multi_strategy_score = self._score_multi_strategy(signals)
        
        # 加权总分
        final_total = (
            liq_score * self.weights['liquidity'] +
            trend_total * self.weights['trend'] +
            signal_score * self.weights['signal'] +
            multi_strategy_score * self.weights['multi_strategy']
        )
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'basic_info': {
                'price': signals[0]['price'] if signals else 0
            },
            'liquidity_score': round(liq_score, 2),
            'trend_score': trend_score,
            'strategy_signals': signals,
            'signal_score': round(signal_score, 2),
            'multi_strategy_score': round(multi_strategy_score, 2),
            'final_score': {
                'total': round(final_total, 2),
                'components': {
                    'liquidity': round(liq_score * self.weights['liquidity'], 2),
                    'trend': round(trend_total * self.weights['trend'], 2),
                    'signal': round(signal_score * self.weights['signal'], 2),
                    'multi_strategy': round(multi_strategy_score * self.weights['multi_strategy'], 2)
                }
            }
        }
    
    def _score_signals(self, signals: List[Dict]) -> float:
        """
        评估策略信号强度 (0-100)
        
        Args:
            signals: 信号列表
        
        Returns:
            信号得分
        """
        if not signals:
            return 0
        
        # 基础分：有信号就有50分
        base_score = 50
        
        # 根据信号类型加分
        signal_types = [s['signal'] for s in signals]
        
        # 不同信号类型的权重
        signal_weights = {
            '均线金叉': 30,
            '价格突破': 35,
            '成交量放大': 25,
            'RSI超卖反弹': 20,
            'RSI超买回落': 10
        }
        
        bonus = 0
        for signal_type in signal_types:
            bonus += signal_weights.get(signal_type, 15)
        
        # 最多加50分
        bonus = min(bonus, 50)
        
        total = base_score + bonus
        return min(total, 100)
    
    def _score_multi_strategy(self, signals: List[Dict]) -> float:
        """
        评估多策略共振 (0-100)
        
        Args:
            signals: 信号列表
        
        Returns:
            共振得分
        """
        num_strategies = len(signals)
        
        if num_strategies >= 3:
            return 100  # 3个或以上策略共振
        elif num_strategies == 2:
            return 70   # 2个策略
        elif num_strategies == 1:
            return 30   # 单一策略
        else:
            return 0
    
    def _calculate_confidence(self, score_result: Dict) -> str:
        """
        计算置信度标签
        
        Args:
            score_result: 评分结果
        
        Returns:
            置信度标签: high/medium/low
        """
        total = score_result['final_score']['total']
        trend_score = score_result['trend_score']['total']
        num_signals = len(score_result['strategy_signals'])
        
        # 高置信度：总分高、趋势强、多策略
        if total >= 80 and trend_score >= 70 and num_signals >= 2:
            return "high"
        # 中等置信度
        elif total >= 65 and trend_score >= 50:
            return "medium"
        # 低置信度
        else:
            return "low"
    
    def calculate_liquidity_score(self, df: pd.DataFrame, config: dict) -> float:
        """
        计算流动性得分 (0-100)
        
        Args:
            df: 股票数据
            config: 流动性配置
        
        Returns:
            流动性得分
        """
        try:
            # 计算平均成交额
            volume_period = config.get('volume_period', 20)
            recent_data = df.tail(volume_period)
            
            if len(recent_data) < volume_period:
                return 50  # 数据不足，给中等分
            
            avg_volume = recent_data['volume'].mean()
            avg_price = recent_data['close'].mean()
            avg_dollar_volume = avg_volume * avg_price
            
            # 基准值（超过这个值得满分）
            excellent_threshold = config.get('excellent_threshold', 10000000)  # 1000万美元
            min_threshold = config.get('min_avg_dollar_volume', 1000000)  # 100万美元
            
            if avg_dollar_volume >= excellent_threshold:
                score = 100
            elif avg_dollar_volume >= min_threshold:
                # 线性插值
                score = 60 + 40 * (avg_dollar_volume - min_threshold) / (excellent_threshold - min_threshold)
            else:
                # 低于门槛，得分很低（不应该出现，因为过滤器会拦截）
                score = 50 * (avg_dollar_volume / min_threshold)
            
            return min(score, 100)
        
        except Exception as e:
            self.logger.error(f"计算流动性得分时出错: {e}")
            return 50

