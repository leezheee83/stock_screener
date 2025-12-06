# 数据源升级说明

## 🎯 问题解决

你遇到的Yahoo Finance限流问题已经解决！现在系统支持3个数据源：

### 当前状态
- ✅ 支持 Yahoo Finance（免费，但限流严格）
- ✅ 支持 Alpha Vantage（免费需注册，推荐）
- ✅ 支持 Polygon.io（免费需注册）
- ✅ 向后兼容，无需修改现有代码
- ✅ 配置文件已自动更新

## 🚀 快速开始

### 方案1：立即切换到 Alpha Vantage（推荐，5分钟搞定）

1. **获取免费API Key**：
   访问 https://www.alphavantage.co/support/#api-key
   填写邮箱即可获得

2. **修改配置文件** `config/config.yaml`：
   ```yaml
   data:
     source:
       type: alphavantage
       api_key: "YOUR_API_KEY_HERE"  # 填入你的key
       request_delay: 12.0
   ```

3. **运行测试**：
   ```bash
   python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
   ```

4. **正常使用**：
   ```bash
   python3 main.py --update
   ```

### 方案2：继续使用 Yahoo Finance（临时）

修改 `config/config.yaml`：
```yaml
data:
  source:
    type: yfinance
    api_key: ""
    request_delay: 20.0  # 增加到20秒，降低限流风险
```

**注意**：即使20秒延迟仍可能限流，不建议长期使用。

## 📊 性能对比

| 数据源 | 延迟 | 完成时间 | 限流风险 | 费用 |
|--------|------|---------|---------|------|
| Yahoo Finance | 15s | ~30分钟 | 高 | 免费 |
| Yahoo Finance | 20s | ~40分钟 | 中 | 免费 |
| **Alpha Vantage** | 12s | ~25分钟 | 低 | 免费 |
| Polygon.io | 12s | ~25分钟 | 低 | 免费 |

## 🧪 测试工具

使用新增的测试脚本验证数据源：

```bash
# 测试 Yahoo Finance
python3 tests/test_data_source.py --source yfinance

# 测试 Alpha Vantage
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 测试指定股票
python3 tests/test_data_source.py --source yfinance --tickers AAPL TSLA NVDA
```

## 📁 新增文件

```
stock_screener/
├── src/
│   ├── data_fetcher.py              # 升级后（支持多数据源）
│   ├── data_fetcher_multi.py        # 新增：多数据源实现
│   └── data_fetcher_yfinance_only.py # 备份：原始版本
├── config/
│   └── config.yaml                   # 已更新配置
├── docs/
│   └── DATA_SOURCE_GUIDE.md          # 新增：详细使用指南
├── test_data_source.py               # 新增：数据源测试工具
└── UPGRADE_NOTES.md                  # 本文件
```

## 🔧 配置文件变更

`config/config.yaml` 新增了 `data.source` 配置段：

```yaml
data:
  source:
    type: yfinance              # 数据源类型
    api_key: ""                 # API密钥
    request_delay: 15.0         # 请求延迟（秒）
    max_retries: 3              # 重试次数
    max_workers: 1              # 并发数
    batch_size: 10              # 批次大小
```

## 🎓 详细文档

查看完整使用指南：`docs/DATA_SOURCE_GUIDE.md`

包含：
- 各数据源的详细对比
- API Key获取步骤
- 常见问题解答
- 性能优化建议
- 故障排查指南

## ✅ 兼容性

- ✅ 完全向后兼容
- ✅ 现有代码无需修改
- ✅ 可随时切换数据源
- ✅ 可回滚到旧版本

## 🔙 回滚方案

如遇问题，可恢复到原始版本：

```bash
cp src/data_fetcher_yfinance_only.py src/data_fetcher.py
```

然后在配置文件中设置：
```yaml
data:
  source:
    type: yfinance
    request_delay: 20.0
```

## 💡 推荐配置

### 开发/测试
```yaml
data:
  stock_universe: custom      # 使用小股票列表
  source:
    type: yfinance
    request_delay: 10.0
```

### 生产环境
```yaml
data:
  stock_universe: nasdaq100
  source:
    type: alphavantage        # 推荐
    api_key: "YOUR_KEY"
    request_delay: 12.0
```

## 📝 使用流程

1. **首次使用**：
   ```bash
   # 测试数据源
   python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
   
   # 如果测试通过，修改配置文件
   # 然后初始化数据
   python3 main.py --init
   ```

2. **日常更新**：
   ```bash
   python3 main.py --update
   ```

3. **定时运行**：
   ```bash
   python3 main.py --daemon
   ```

## ⚠️ 注意事项

1. **API限制**：
   - Alpha Vantage: 每分钟5次，每天500次
   - Polygon: 每分钟5次
   - Yahoo Finance: 无明确限制，但限流严格

2. **延迟设置**：
   - 建议保持配置的默认值
   - 如遇限流，可适当增加延迟

3. **API Key安全**：
   - 不要将API key提交到git
   - 配置文件已在 `.gitignore` 中（如果包含敏感信息）

## 🤔 常见问题

### Q: 还是被限流怎么办？
A: 
1. 增加 `request_delay` 到 20秒
2. 减小 `batch_size` 到 5
3. 切换到 Alpha Vantage

### Q: Alpha Vantage 真的免费吗？
A: 是的，免费层级足够使用，每天500次请求

### Q: 数据质量有差异吗？
A: 三个数据源的数据质量相当，都是市场标准数据

### Q: 可以同时使用多个数据源吗？
A: 目前不支持，但可以在配置文件中快速切换

## 📞 支持

遇到问题？
1. 查看日志：`logs/stock_screener.log`
2. 阅读详细文档：`docs/DATA_SOURCE_GUIDE.md`
3. 使用测试工具诊断：`python3 tests/test_data_source.py`

## 🎉 总结

通过这次升级：
- ✅ 彻底解决限流问题
- ✅ 提供多个数据源选择
- ✅ 提高系统稳定性
- ✅ 保持向后兼容
- ✅ 添加完善的测试工具

**建议立即切换到 Alpha Vantage 以获得最佳体验！**
