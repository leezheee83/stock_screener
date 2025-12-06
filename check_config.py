#!/usr/bin/env python3
"""
配置验证脚本
检查系统配置是否正确，数据源是否可用
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import yaml
from pathlib import Path


def check_mark(condition, message):
    """打印检查结果"""
    if condition:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("系统配置验证".center(60))
    print("="*60 + "\n")
    
    all_passed = True
    
    # 1. 检查配置文件
    print("📋 检查配置文件...")
    config_path = Path('config/config.yaml')
    
    if not check_mark(config_path.exists(), f"配置文件存在: {config_path}"):
        print("\n❌ 配置文件不存在，请先创建配置文件")
        return False
    
    # 2. 读取配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        check_mark(True, "配置文件格式正确")
    except Exception as e:
        check_mark(False, f"配置文件格式错误: {e}")
        return False
    
    print()
    
    # 3. 检查数据源配置
    print("🔌 检查数据源配置...")
    
    source_config = config.get('data', {}).get('source', {})
    
    if not source_config:
        print("⚠️  警告: 未找到 data.source 配置")
        print("   系统将使用默认配置（yfinance, 可能遇到限流）")
        print("   建议运行: python3 configure_datasource.py")
        source_type = 'yfinance'
        request_delay = 15.0
        api_key = None
    else:
        source_type = source_config.get('type', 'yfinance')
        api_key = source_config.get('api_key')
        request_delay = source_config.get('request_delay', 15.0)
        max_retries = source_config.get('max_retries', 3)
        max_workers = source_config.get('max_workers', 1)
        
        check_mark(True, f"数据源类型: {source_type}")
        
        # 检查API key
        if source_type in ['alphavantage', 'polygon']:
            if api_key and len(api_key) > 5:
                check_mark(True, f"API Key: 已配置 ({api_key[:8]}...)")
            else:
                check_mark(False, "API Key: 未配置或无效")
                print(f"   {source_type} 需要 API key")
                if source_type == 'alphavantage':
                    print("   获取地址: https://www.alphavantage.co/support/#api-key")
                else:
                    print("   获取地址: https://polygon.io/")
                all_passed = False
        else:
            check_mark(True, "API Key: 不需要")
        
        check_mark(request_delay >= 10, f"请求延迟: {request_delay}秒")
        if request_delay < 10:
            print("   ⚠️  建议至少10秒以避免限流")
        
        check_mark(max_workers == 1, f"并发数: {max_workers} (建议1)")
        if max_workers > 1:
            print("   ⚠️  并发可能导致限流，建议设为1")
    
    print()
    
    # 4. 检查目录结构
    print("📁 检查目录结构...")
    
    required_dirs = [
        'data',
        'data/daily',
        'data/weekly',
        'data/monthly',
        'logs',
        'reports'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            check_mark(True, f"创建目录: {dir_path}")
        else:
            check_mark(True, f"目录存在: {dir_path}")
    
    print()
    
    # 5. 检查依赖
    print("📦 检查Python依赖...")
    
    required_packages = [
        ('yaml', 'PyYAML'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
    ]
    
    # 根据数据源类型检查依赖
    if source_type == 'yfinance':
        required_packages.append(('yfinance', 'yfinance'))
    elif source_type in ['alphavantage', 'polygon']:
        required_packages.append(('requests', 'requests'))
    
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            check_mark(True, f"已安装: {package_name}")
        except ImportError:
            check_mark(False, f"未安装: {package_name}")
            print(f"   安装命令: pip install {package_name}")
            all_passed = False
    
    print()
    
    # 6. 总结和建议
    print("="*60)
    if all_passed:
        print("✅ 所有检查通过！")
        print()
        print("下一步:")
        print("  1. 测试数据源:")
        if source_type == 'yfinance':
            print("     python3 test_data_source.py --source yfinance")
        else:
            print(f"     python3 test_data_source.py --source {source_type} --api-key YOUR_KEY")
        print()
        print("  2. 初始化数据 (首次使用):")
        print("     python3 main.py --init")
        print()
        print("  3. 更新数据:")
        print("     python3 main.py --update")
        
        # 限流警告
        if source_type == 'yfinance':
            print()
            print("⚠️  注意: Yahoo Finance 限流严重")
            print("   建议切换到 Alpha Vantage")
            print("   运行: python3 configure_datasource.py")
        
    else:
        print("❌ 发现问题，请先解决上述错误")
        print()
        print("常见解决方案:")
        print("  1. 配置数据源:")
        print("     python3 configure_datasource.py")
        print()
        print("  2. 安装依赖:")
        print("     pip install -r requirements.txt")
        print()
        print("  3. 查看详细文档:")
        print("     cat QUICKFIX.md")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
