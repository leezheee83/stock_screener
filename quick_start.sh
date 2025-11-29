#!/bin/bash
# Quick Start Script for Stock Screener
# 美股筛选系统快速启动脚本

echo "=================================="
echo "美股定时筛选系统 - 快速启动"
echo "=================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version

if [ $? -ne 0 ]; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

echo ""

# 检查是否已安装依赖
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    
    echo "激活虚拟环境..."
    source venv/bin/activate
    
    echo "安装依赖包..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo ""
    echo "✓ 依赖安装完成"
else
    echo "激活现有虚拟环境..."
    source venv/bin/activate
fi

echo ""
echo "=================================="
echo "选择操作:"
echo "=================================="
echo "1. 初始化数据（首次使用，下载历史数据）"
echo "2. 手动执行一次筛选"
echo "3. 启动定时任务（后台运行）"
echo "4. 仅更新数据"
echo "5. 查看配置"
echo "0. 退出"
echo ""

read -p "请选择 [0-5]: " choice

case $choice in
    1)
        echo ""
        echo "开始初始化数据（可能需要30-60分钟）..."
        python main.py --init
        ;;
    2)
        echo ""
        echo "执行一次性筛选..."
        python main.py --run-once
        ;;
    3)
        echo ""
        echo "启动定时任务..."
        echo "提示: 使用 Ctrl+C 停止"
        python main.py --daemon
        ;;
    4)
        echo ""
        echo "更新数据..."
        python main.py --update
        ;;
    5)
        echo ""
        echo "当前配置:"
        cat config/config.yaml
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "操作完成！"

