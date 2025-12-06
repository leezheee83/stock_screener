# 多数据源配置指南

## 概述

系统现已支持多个数据源，解决Yahoo Finance限流问题。你可以选择：

1. **Yahoo Finance (yfinance)** - 免费，但限流严格
2. **Alpha Vantage** - 免费但需要API key，限流较宽松
3. **Polygon.io** - 免费但需要API key，数据更全面

## 当前问题

Yahoo Finance的免费API限流非常严格，即使设置了15秒延迟和串行下载，仍然经常触发限流：
```
Too Many Requests. Rate limited. Try after a while.
```

## 推荐方案

### 方案A：切换到 Alpha Vantage（推荐）

**优点**：
- 免费，数据质量高
- 限流宽松：每分钟5次请求，每天500次
- 获取NASDAQ 100需要约25分钟（102只股票 × 15秒延迟）

**步骤**：

1. **获取API Key**（免费）：
   - 访问：https://www.alphavantage.co/support/#api-key
   - 填写邮箱即可立即获得免费API key

2. **修改配置文件** `config/config.yaml`：

```yaml
data:
  source:
    type: alphavantage           # 改为 alphavantage
    api_key: "YOUR_API_KEY_HERE" # 填入你的API key
    request_delay: 12.0          # 每分钟5次 = 12秒延迟
    max_retries: 3
    max_workers: 1
    batch_size: 10
```

3. **运行程序**：
```bash
python3 main.py --update
```

### 方案B：切换到 Polygon.io

**优点**：
- 免费层级包含更多数据
- 限流：每分钟5次请求
- API更现代化

**步骤**：

1. **获取API Key**：
   - 访问：https://polygon.io/
   - 注册免费账户获取API key

2. **修改配置文件** `config/config.yaml`：

```yaml
data:
  source:
    type: polygon                # 改为 polygon
    api_key: "YOUR_API_KEY_HERE" # 填入你的API key
    request_delay: 12.0
    max_retries: 3
    max_workers: 1
    batch_size: 10
```

### 方案C：继续使用 Yahoo Finance（临时方案）

如果你不想注册API key，可以增加延迟来降低限流概率：

**修改配置文件** `config/config.yaml`：

```yaml
data:
  source:
    type: yfinance
    api_key: ""
    request_delay: 20.0          # 增加到20秒（非常慢）
    max_retries: 5               # 增加重试次数
    max_workers: 1
    batch_size: 5                # 减小批次大小
```

**注意**：
- 即使设置20秒延迟，仍可能遇到限流
- 获取102只股票需要约40分钟
- 不推荐用于生产环境

## 性能对比

| 数据源 | 延迟设置 | 完成时间（102只股票） | 限流风险 | 需要API Key |
|--------|----------|----------------------|----------|-------------|
| Yahoo Finance | 15秒 | ~30分钟 | 高 | 否 |
| Yahoo Finance | 20秒 | ~40分钟 | 中 | 否 |
| Alpha Vantage | 12秒 | ~25分钟 | 低 | 是（免费）|
| Polygon.io | 12秒 | ~25分钟 | 低 | 是（免费）|

## 常见问题

### Q1: Alpha Vantage 需要付费吗？
**A**: 不需要，免费层级足够使用：
- 每分钟5次请求
- 每天500次请求
- 对于NASDAQ 100（102只股票×3个周期=306次请求），完全够用

### Q2: 如何检查当前使用的数据源？
**A**: 运行程序时，日志会显示：
```
INFO - 数据采集器初始化完成 - 数据源: alphavantage, 延迟: 12.0秒
```

### Q3: 可以混合使用多个数据源吗？
**A**: 目前不支持，但可以在配置文件中快速切换

### Q4: Alpha Vantage 的数据质量如何？
**A**: 
- 数据来自官方金融数据提供商
- 质量与Yahoo Finance相当或更好
- 支持实时和历史数据

### Q5: 我还是遇到限流怎么办？
**A**: 按以下顺序尝试：
1. 增加 `request_delay`（建议15秒以上）
2. 减小 `batch_size`（建议5）
3. 增加 `max_retries`（建议5）
4. 考虑切换到 Alpha Vantage 或 Polygon

## 推荐配置

### 开发/测试环境
```yaml
data:
  stock_universe: custom         # 使用小范围股票列表
  source:
    type: yfinance
    request_delay: 10.0
    batch_size: 5
```

### 生产环境
```yaml
data:
  stock_universe: nasdaq100
  source:
    type: alphavantage           # 推荐
    api_key: "YOUR_API_KEY"
    request_delay: 12.0
    max_retries: 3
    batch_size: 10
```

## 测试新数据源

运行以下命令测试数据源是否工作正常：

```bash
# 只测试少量股票
python3 main.py --update
```

如果成功，你会看到类似输出：
```
INFO - Alpha Vantage 数据源已初始化 (延迟: 12.0秒)
INFO - ✓ AAPL (1/102)
INFO - ✓ MSFT (2/102)
...
```

## 文件说明

- `src/data_fetcher.py` - 主数据采集器（兼容旧版接口）
- `src/data_fetcher_multi.py` - 多数据源实现
- `src/data_fetcher_yfinance_only.py` - 原始yfinance版本（备份）

## 回滚到旧版本

如果遇到问题，可以恢复到仅支持yfinance的旧版本：

```bash
cp src/data_fetcher_yfinance_only.py src/data_fetcher.py
```

## 下一步优化建议

1. **使用自定义股票列表**：只关注特定股票，减少API调用
2. **增量更新**：只更新最新数据，不是每次都下载全部历史
3. **缓存数据**：使用本地缓存，避免重复下载
4. **定时任务**：设置在非高峰时段更新数据

## 支持

如有问题，请查看日志文件：`logs/stock_screener.log`
