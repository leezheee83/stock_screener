#!/usr/bin/env python3
"""
数据源配置向导
交互式配置数据源
"""

import os
import sys
import yaml
from pathlib import Path


def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")


def print_section(text):
    """打印小节"""
    print("\n" + "-"*60)
    print(text)
    print("-"*60)


def get_user_choice(prompt, choices, default=None):
    """获取用户选择"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip() or default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input in choices:
            return user_input
        else:
            print(f"❌ 无效选择，请输入: {', '.join(choices)}")


def get_api_key(source_name, url):
    """获取API Key"""
    print(f"\n📝 {source_name} 需要API Key")
    print(f"   获取地址: {url}")
    print(f"   注册免费，立即可用\n")
    
    while True:
        api_key = input("请输入你的API Key (或输入 'skip' 跳过): ").strip()
        
        if api_key.lower() == 'skip':
            return None
        
        if len(api_key) > 5:  # 简单验证
            return api_key
        else:
            print("❌ API Key 格式不正确，请重新输入")


def update_config_file(config_path, source_type, api_key, request_delay):
    """更新配置文件"""
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 更新数据源配置
        if 'data' not in config:
            config['data'] = {}
        
        config['data']['source'] = {
            'type': source_type,
            'api_key': api_key or "",
            'request_delay': request_delay,
            'max_retries': 3,
            'max_workers': 1,
            'batch_size': 10
        }
        
        # 写回配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False


def main():
    """主函数"""
    print_header("股票筛选系统 - 数据源配置向导")
    
    print("欢迎！本向导将帮助你配置数据源。")
    print("\n当前问题：Yahoo Finance 限流严重")
    print("解决方案：切换到更稳定的数据源")
    
    # 选择数据源
    print_section("步骤 1/3: 选择数据源")
    print("\n可用的数据源:")
    print("  1. yfinance      - Yahoo Finance (免费，但限流严重) ⚠️")
    # api key : JCYHE2IJVOIWUA52
    print("  2. alphavantage  - Alpha Vantage (免费需注册，推荐) ✅")
    print("  3. polygon       - Polygon.io (免费需注册) ✅")
    
    choice = get_user_choice("\n请选择数据源", ['1', '2', '3'], default='2')
    
    source_map = {
        '1': ('yfinance', 15.0, False),
        '2': ('alphavantage', 12.0, True),
        '3': ('polygon', 12.0, True)
    }
    
    source_type, request_delay, needs_api_key = source_map[choice]
    
    # 获取API Key
    api_key = None
    if needs_api_key:
        print_section("步骤 2/3: 配置API Key")
        
        if source_type == 'alphavantage':
            api_key = get_api_key(
                "Alpha Vantage",
                "https://www.alphavantage.co/support/#api-key"
            )
        elif source_type == 'polygon':
            api_key = get_api_key(
                "Polygon.io",
                "https://polygon.io/"
            )
        
        if not api_key:
            print("\n⚠️  你选择跳过API Key配置")
            print("   你需要手动编辑 config/config.yaml 添加API key")
            print("   否则数据获取将失败")
            
            proceed = get_user_choice("\n是否继续?", ['y', 'n'], default='n')
            if proceed == 'n':
                print("\n已取消配置")
                sys.exit(0)
    else:
        print_section("步骤 2/3: 配置API Key")
        print("✓ Yahoo Finance 不需要API Key")
    
    # 确认配置
    print_section("步骤 3/3: 确认配置")
    print(f"\n数据源:    {source_type}")
    print(f"API Key:   {'已设置' if api_key else '未设置'}")
    print(f"请求延迟:  {request_delay} 秒")
    print(f"重试次数:  3")
    print(f"并发数:    1 (串行)")
    print(f"批次大小:  10")
    
    confirm = get_user_choice("\n确认应用此配置?", ['y', 'n'], default='y')
    
    if confirm == 'n':
        print("\n已取消配置")
        sys.exit(0)
    
    # 更新配置文件
    print_section("应用配置")
    
    config_path = Path(__file__).parent / 'config' / 'config.yaml'
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)
    
    print(f"正在更新配置文件: {config_path}")
    
    if update_config_file(config_path, source_type, api_key, request_delay):
        print("✅ 配置已成功更新！")
    else:
        print("❌ 配置更新失败")
        sys.exit(1)
    
    # 后续步骤
    print_header("配置完成")
    
    print("✅ 数据源配置已完成！\n")
    print("下一步:")
    print(f"  1. 测试数据源:")
    if api_key:
        print(f"     python3 test_data_source.py --source {source_type} --api-key {api_key[:8]}...")
    else:
        print(f"     python3 test_data_source.py --source {source_type}")
    
    print(f"\n  2. 更新数据:")
    print(f"     python3 main.py --update")
    
    print(f"\n  3. 运行筛选:")
    print(f"     python3 main.py --run-once")
    
    if source_type == 'yfinance':
        print("\n⚠️  注意:")
        print("   Yahoo Finance 限流严重，建议切换到 Alpha Vantage")
        print("   重新运行此向导选择选项 2")
    
    if not api_key and needs_api_key:
        print("\n⚠️  注意:")
        print("   你还没有设置API Key")
        print(f"   请编辑 config/config.yaml，添加 api_key 配置")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消配置")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
