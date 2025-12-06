# 🚀 MAG7 快速测试配置

## ✅ 已完成配置

你的系统现在已配置为使用 **MAG7 测试集**！

### 当前配置
```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/mag7_tickers.txt
```

### MAG7 股票列表
1. **MSFT** - Microsoft (微软)
2. **AAPL** - Apple (苹果)
3. **GOOGL** - Google (谷歌)
4. **AMZN** - Amazon (亚马逊)
5. **NVDA** - Nvidia (英伟达)
6. **META** - Meta (Facebook)
7. **TSLA** - Tesla (特斯拉)

---

## 🎯 为什么使用 MAG7？

### 优势对比

| 指标 | MAG7 测试集 | NASDAQ 100 |
|------|------------|-----------|
| 股票数量 | 7只 | 102只 |
| 更新时间 | **~2分钟** ⚡ | ~25分钟 |
| API调用 | **21次** | 306次 |
| 迭代速度 | **快12倍** | 慢 |
| 适用场景 | 开发测试 | 生产环境 |

### 代表性
- ✅ 覆盖科技、消费、AI、汽车等多个领域
- ✅ 全是大盘股，流动性极好
- ✅ 数据质量高，波动性好
- ✅ 市值占NASDAQ很大比重

---

## 🚀 快速开始

### 1. 更新 MAG7 数据（约2分钟）
```bash
python3 main.py --update
```

**预期输出**：
```
获取 7 只股票的 daily 数据
✓ MSFT (1/7)
✓ AAPL (2/7)
✓ GOOGL (3/7)
✓ AMZN (4/7)
✓ NVDA (5/7)
✓ META (6/7)
✓ TSLA (7/7)
数据获取完成: 成功 7/7
```

### 2. 运行筛选（使用本地数据）
```bash
python3 main.py --run-once --skip-update
```

### 3. 完整运行（更新+筛选）
```bash
python3 main.py --run-once
```

---

## 📊 性能对比

### MAG7 模式（当前）
```bash
$ time python3 main.py --update

# 预期：
- 耗时: ~2分钟
- API调用: 21次
- 成功率: 100%
```

### NASDAQ 100 模式
```bash
$ time python3 main.py --update

# 预期：
- 耗时: ~25分钟
- API调用: 306次
- 可能遇到限流
```

---

## 🔄 切换股票池

### 切换到 NASDAQ 100（生产环境）
编辑 `config/config.yaml`:
```yaml
data:
  stock_universe: nasdaq100
  # 删除或注释掉 custom_tickers_file
```

### 切换回 MAG7（测试环境）
编辑 `config/config.yaml`:
```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/mag7_tickers.txt
```

### 快速切换命令
```bash
# 切换到 MAG7
sed -i '' 's/stock_universe: .*/stock_universe: custom/' config/config.yaml

# 切换到 NASDAQ100
sed -i '' 's/stock_universe: nasdaq100/stock_universe: nasdaq100/' config/config.yaml
sed -i '' '/custom_tickers_file/d' config/config.yaml
```

---

## 🎨 自定义测试集

### 创建自己的股票列表

**示例：创建 3 只股票的最小测试集**
```bash
cat > config/mini_test.txt << 'EOF'
# 最小测试集
AAPL
MSFT
TSLA
EOF
```

**更新配置**：
```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/mini_test.txt
```

**其他预设选项**：
- `config/mag7_tickers.txt` - 7只科技巨头（推荐）
- `config/custom_tickers.txt` - 你的自定义列表
- 创建新的 `.txt` 文件

---

## 📈 推荐工作流

### 开发阶段（快速迭代）
```bash
# 1. 使用 MAG7
vim config/config.yaml  # stock_universe: custom

# 2. 快速测试（~2分钟）
python3 main.py --update

# 3. 运行筛选
python3 main.py --run-once --skip-update

# 4. 查看结果
ls -lh reports/
```

### 生产部署
```bash
# 1. 切换到 NASDAQ 100
vim config/config.yaml  # stock_universe: nasdaq100

# 2. 定时运行
python3 main.py --daemon
```

---

## 💰 API 额度管理

### Alpha Vantage 免费版
- **限制**: 每天 500次请求
- **MAG7**: 21次/运行 → 可运行 **23次/天**
- **NASDAQ100**: 306次/运行 → 只能运行 **1次/天**

### 建议
- 🔧 **开发**: 使用MAG7，每天可以测试20+次
- 📊 **生产**: 使用NASDAQ100，每天定时运行1次
- 🎯 **最佳实践**: 开发用MAG7，部署前切换到NASDAQ100验证

---

## ✅ 验证配置

```bash
# 检查当前配置
python3 check_config.py

# 查看当前股票池
grep -A1 "stock_universe" config/config.yaml

# 查看MAG7列表
cat config/mag7_tickers.txt

# 测试单只股票
python3 tests/test_data_source.py --source alphavantage --api-key JCYHE2IJVOIWUA52 --tickers AAPL
```

---

## 🎯 快速命令参考

```bash
# 更新MAG7数据
python3 main.py --update                    # ~2分钟

# 运行筛选（使用本地数据）
python3 main.py --run-once --skip-update    # 秒级

# 完整运行
python3 main.py --run-once                   # ~2分钟

# 查看结果
cat reports/screening_results_*.json        # JSON格式
open reports/screening_*.xlsx               # Excel格式

# 查看日志
tail -f logs/stock_screener.log
```

---

## 📚 相关文档

- **详细指南**: `docs/STOCK_UNIVERSE_GUIDE.md`
- **快速开始**: `QUICK_START.md`
- **配置说明**: `README.md`

---

## 💡 提示

1. **快速验证策略**: MAG7只需2分钟，可以快速测试不同参数
2. **节省API额度**: 开发阶段用MAG7，节省90%的API调用
3. **代表性好**: MAG7包含了市场各个热门板块
4. **随时切换**: 一行配置即可切换股票池

---

**当前状态**: ✅ MAG7 测试集已配置  
**下一步**: 运行 `python3 main.py --update` 开始快速测试！  
**预计时间**: ~2分钟完成数据更新 ⚡
