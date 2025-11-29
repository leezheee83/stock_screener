# 示例脚本说明

这个目录包含一些实用的示例脚本，帮助您更好地使用股票数据。

## 📊 analyze_stock.py - 股票分析工具

### 功能
- 读取和分析CSV数据文件
- 计算并显示所有技术指标
- 提供价格、成交量、趋势分析
- 支持多股票对比

### 使用方法

#### 1. 分析单只股票

```bash
# 分析META的日线数据
python examples/analyze_stock.py META

# 分析AAPL的周线数据
python examples/analyze_stock.py AAPL --period weekly

# 分析GOOGL的月线数据
python examples/analyze_stock.py GOOGL -p monthly
```

#### 2. 分析多只股票

```bash
# 依次分析多只股票
python examples/analyze_stock.py META AAPL GOOGL TSLA
```

#### 3. 对比多只股票

```bash
# 对比分析模式
python examples/analyze_stock.py META AAPL GOOGL TSLA --compare
```

### 输出示例

```
======================================================================
股票分析: META (daily)
======================================================================

📊 数据概况:
   数据范围: 2024-06-01 至 2024-11-28
   数据条数: 127 条

💰 最新价格 (2024-11-28):
   开盘: $656.00
   收盘: $633.61
   最高: $659.33
   最低: $581.25
   成交量: 420,432,008

📈 价格分析:
   日涨跌: -3.45%
   5日涨跌: -5.12%

📉 均线分析:
   MA  5: $645.50 (价格在均线下方 1.85%)
   MA 10: $658.20 (价格在均线下方 3.74%)
   MA 20: $672.45 (价格在均线下方 5.78%)
   MA 50: $705.30 (价格在均线下方 10.17%)

🎯 技术指标:
   RSI(14): 38.50 (中性)
   MACD: -12.45, 信号线: -8.30, 柱状: -4.15 (空头)
   布林带: 上轨$720.50, 中轨$672.45, 下轨$624.40 (跌破下轨)

📊 成交量分析:
   当前成交量: 420,432,008
   平均成交量: 285,000,000
   成交量比率: 1.48x (放大)

🔮 趋势判断:
   趋势: 空头趋势 📉
   近期支撑位: $581.25
   近期阻力位: $735.00
   ATR: $18.50 (2.92%, 波动率中等)
```

## 💡 如何在策略中使用数据

### 在自定义策略中读取数据

编辑 `src/strategy/custom_strategies.py`:

```python
from .base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        results = []
        
        for ticker, df in data.items():
            # df 就是从CSV读取的数据，已包含所有技术指标
            
            latest = self.get_latest_row(df)
            previous = self.get_previous_row(df)
            
            # 示例：寻找突破20日均线且成交量放大的股票
            if (previous['close'] < previous['sma_20'] and 
                latest['close'] > latest['sma_20'] and
                latest['volume_ratio'] > 1.5):
                
                results.append({
                    'ticker': ticker,
                    'signal': '突破20日均线',
                    'price': latest['close'],
                    'details': {
                        'sma_20': latest['sma_20'],
                        'volume_ratio': latest['volume_ratio']
                    }
                })
        
        return results
```

## 🔧 直接使用pandas分析

```python
import pandas as pd

# 读取数据
df = pd.read_csv('data/daily/META.csv')
df['date'] = pd.to_datetime(df['date'])

# 计算简单指标
df['returns'] = df['close'].pct_change() * 100
df['ma_20'] = df['close'].rolling(20).mean()

# 筛选条件
bullish = df[df['close'] > df['ma_20']]
high_volume = df[df['volume'] > df['volume'].quantile(0.75)]

# 统计分析
print(f"平均收益率: {df['returns'].mean():.2f}%")
print(f"波动率: {df['returns'].std():.2f}%")
print(f"最大涨幅: {df['returns'].max():.2f}%")
print(f"最大跌幅: {df['returns'].min():.2f}%")
```

## 📈 可视化数据

如果需要图表，可以安装matplotlib：

```bash
pip install matplotlib
```

然后创建可视化脚本：

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/daily/META.csv')
df['date'] = pd.to_datetime(df['date'])

# 绘制价格和均线
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['close'], label='收盘价', linewidth=2)
plt.title(f'META 价格走势')
plt.xlabel('日期')
plt.ylabel('价格 ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('META_chart.png')
plt.show()
```

## 🎓 更多资源

- pandas文档: https://pandas.pydata.org/docs/
- 技术分析教程: https://school.stockcharts.com/
- yfinance文档: https://pypi.org/project/yfinance/

