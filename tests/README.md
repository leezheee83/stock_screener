# 测试工具集

本目录包含股票筛选系统的测试和诊断工具。

## 📁 文件说明

### 核心测试工具

#### `test_data_source.py` - 数据源测试工具 ⭐
**用途**: 测试不同数据源（yfinance, Alpha Vantage, Polygon）的连接和数据获取

**使用方法**:
```bash
# 测试 Yahoo Finance
python3 tests/test_data_source.py --source yfinance

# 测试 Alpha Vantage
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 测试 Polygon.io
python3 tests/test_data_source.py --source polygon --api-key YOUR_KEY

# 测试指定股票
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY --tickers AAPL MSFT GOOGL
```

**输出示例**:
```
✓ 数据采集器初始化成功
正在获取 AAPL 数据... ✓ 成功 (20 条记录, 耗时 2.0秒)
  最新数据: 日期=2025-12-05, 收盘价=$278.78
测试完成: 3/3 成功
✅ 所有测试通过，数据源可用
```

---

### 诊断工具

#### `debug_alphavantage.py` - Alpha Vantage API 诊断
**用途**: 深度诊断 Alpha Vantage API 连接问题，显示详细的请求和响应信息

**使用方法**:
```bash
python3 tests/debug_alphavantage.py
```

**输出内容**:
- API连接状态
- 响应状态码
- 原始响应结构
- 数据字段检查
- 数据解析过程
- 日期过滤结果

**适用场景**:
- API连接失败
- 数据格式不正确
- 需要查看原始响应
- 调试数据解析问题

---

#### `test_alphavantage_direct.py` - Alpha Vantage 直接测试
**用途**: 直接测试 Alpha Vantage 数据源的数据获取功能

**使用方法**:
```bash
python3 tests/test_alphavantage_direct.py
```

**说明**: 
- 简化版的测试脚本
- 直接调用 AlphaVantageSource
- 显示数据获取结果
- 用于快速验证

---

#### `test_fetch.py` - 原始数据获取测试
**用途**: 测试原始的数据获取功能（早期版本）

**使用方法**:
```bash
python3 tests/test_fetch.py
```

**说明**: 
- 遗留测试文件
- 用于测试基础数据获取
- 可能需要更新以支持新架构

---

## 🎯 快速开始

### 1. 首次测试数据源
```bash
# 使用 Alpha Vantage（推荐）
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
```

### 2. 如果测试失败
```bash
# 运行详细诊断
python3 tests/debug_alphavantage.py
```

### 3. 快速验证
```bash
# 测试单个股票
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY --tickers AAPL
```

---

## 📊 测试流程建议

### 配置新数据源时
```bash
1. 运行配置向导
   python3 configure_datasource.py

2. 验证配置
   python3 check_config.py

3. 测试数据源
   python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

4. 如果失败，运行诊断
   python3 tests/debug_alphavantage.py
```

### 日常测试
```bash
# 快速测试（3个股票）
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 完整测试（更多股票）
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY --tickers AAPL MSFT GOOGL TSLA NVDA
```

---

## 🐛 故障排查

### 问题：所有测试失败
**解决方案**:
1. 检查网络连接
2. 验证 API key 是否正确
3. 运行 `debug_alphavantage.py` 查看详细错误
4. 查看 `logs/stock_screener.log`

### 问题：部分测试失败
**解决方案**:
1. 检查股票代码是否正确
2. 增加请求延迟（修改 config.yaml 中的 `request_delay`）
3. 检查是否达到 API 限流

### 问题：数据格式错误
**解决方案**:
1. 运行 `debug_alphavantage.py` 查看原始响应
2. 检查数据源版本是否更新
3. 查看错误日志

---

## 📝 开发测试

### 添加新测试
1. 在 `tests/` 目录创建新文件
2. 命名格式: `test_*.py` 或 `debug_*.py`
3. 添加文档说明

### 测试命名规范
- `test_*.py` - 功能测试
- `debug_*.py` - 诊断工具
- `check_*.py` - 配置检查（放在根目录）

---

## 🔗 相关文档

- **配置指南**: `../docs/DATA_SOURCE_GUIDE.md`
- **快速开始**: `../QUICK_START.md`
- **问题修复**: `../QUICKFIX.md`
- **Bug修复记录**: `../BUGFIX_ALPHAVANTAGE.md`

---

## 💡 提示

1. **测试前先配置**: 使用 `configure_datasource.py` 配置数据源
2. **验证配置**: 使用 `check_config.py` 确认配置正确
3. **小范围测试**: 先测试1-3个股票，确认无误后再测试更多
4. **注意延迟**: Alpha Vantage 免费版限制每分钟5次请求，建议延迟12秒以上
5. **保存日志**: 测试日志保存在 `logs/stock_screener.log`

---

**测试工具版本**: 1.0  
**最后更新**: 2025-12-06  
**维护状态**: ✅ 活跃维护
