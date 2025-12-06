# 📊 股票池配置说明

## 可用的股票池

### 1. NASDAQ 100（生产环境）
适用于：完整筛选，生产环境

```yaml
data:
  stock_universe: nasdaq100
```

- **股票数量**：102只
- **更新时间**：约25分钟（Alpha Vantage）
- **适用场景**：完整筛选、生产运行

---

### 2. S&P 500（大规模）
适用于：更大范围筛选

```yaml
data:
  stock_universe: sp500
```

- **股票数量**：500只
- **更新时间**：约2小时（Alpha Vantage）
- **适用场景**：全市场扫描

---

### 3. MAG7 测试集（推荐用于开发）⭐
适用于：快速测试、策略验证、开发调试

```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/mag7_tickers.txt
```

**包含股票**：
- MSFT (Microsoft - 微软)
- AAPL (Apple - 苹果)
- GOOGL (Alphabet/Google - 谷歌)
- AMZN (Amazon - 亚马逊)
- NVDA (Nvidia - 英伟达)
- META (Meta/Facebook)
- TSLA (Tesla - 特斯拉)

**优势**：
- ✅ **快速**：7只股票，约1-2分钟完成
- ✅ **代表性**：覆盖科技、消费、AI等多个领域
- ✅ **高流动性**：全是大盘股，数据质量好
- ✅ **省API额度**：节省Alpha Vantage调用次数

**性能对比**：
| 股票池 | 数量 | 更新时间 | API调用 | 适用场景 |
|--------|------|----------|---------|----------|
| MAG7 | 7只 | ~2分钟 | 21次 | 开发测试 ⭐ |
| NASDAQ100 | 102只 | ~25分钟 | 306次 | 生产环境 |
| S&P500 | 500只 | ~2小时 | 1500次 | 全市场 |

---

## 使用方法

### 切换到 MAG7 测试集

1. **编辑配置文件** `config/config.yaml`:
```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/mag7_tickers.txt
```

2. **运行测试**:
```bash
# 更新数据（约2分钟）
python3 main.py --update

# 运行筛选
python3 main.py --run-once
```

### 切换回 NASDAQ 100

```yaml
data:
  stock_universe: nasdaq100
  # 注释掉或删除 custom_tickers_file 行
```

---

## 自定义股票列表

### 创建自己的测试集

1. **创建股票列表文件**：
```bash
cat > config/my_test_stocks.txt << 'EOF'
# 我的测试股票
AAPL
MSFT
TSLA
# 可以添加注释
NVDA
EOF
```

2. **更新配置**：
```yaml
data:
  stock_universe: custom
  custom_tickers_file: config/my_test_stocks.txt
```

### 文件格式

- 每行一个股票代码
- 支持 `#` 注释
- 忽略空行和空白
- 不区分大小写

**示例**：
```
# 科技股
AAPL    # Apple
MSFT    # Microsoft
GOOGL   # Google

# AI概念
NVDA    # Nvidia
AMD     # AMD
```

---

## 其他预设测试集

### 创建 FAANG 测试集
```bash
cat > config/faang_tickers.txt << 'EOF'
# FAANG 五大科技股
META    # Facebook/Meta
AAPL    # Apple
AMZN    # Amazon
NFLX    # Netflix
GOOGL   # Google
EOF
```

### 创建 小测试集（3只）
```bash
cat > config/mini_test.txt << 'EOF'
# 最小测试集 - 3只股票
AAPL
MSFT
TSLA
EOF
```

---

## 推荐工作流

### 开发和测试阶段
```yaml
# 使用 MAG7 快速验证
data:
  stock_universe: custom
  custom_tickers_file: config/mag7_tickers.txt
```

```bash
# 快速迭代（1-2分钟/次）
python3 main.py --run-once
```

### 生产环境
```yaml
# 切换到完整股票池
data:
  stock_universe: nasdaq100
```

```bash
# 定时运行
python3 main.py --daemon
```

---

## API 额度考虑

### Alpha Vantage 免费版限制
- 每分钟：5次请求
- 每天：500次请求

### 各股票池消耗

**MAG7 (7只股票)**：
- Daily: 7次
- Weekly: 7次
- Monthly: 7次
- **总计**: 21次请求
- **耗时**: ~2分钟

**NASDAQ 100 (102只股票)**：
- Daily: 102次
- Weekly: 102次
- Monthly: 102次
- **总计**: 306次请求
- **耗时**: ~25分钟

### 建议
- 🔧 **开发测试**: 使用MAG7，快速迭代
- 🔄 **每日更新**: 可以使用NASDAQ100
- 📊 **全市场**: 需要付费版或分批次运行

---

## 快速命令

```bash
# 查看当前股票池
grep "stock_universe" config/config.yaml

# 切换到MAG7
sed -i '' 's/stock_universe: .*/stock_universe: custom/' config/config.yaml

# 切换到NASDAQ100
sed -i '' 's/stock_universe: .*/stock_universe: nasdaq100/' config/config.yaml

# 查看MAG7列表
cat config/mag7_tickers.txt

# 运行快速测试
python3 main.py --run-once --skip-update  # 使用本地数据
```

---

## 验证配置

```bash
# 检查配置是否正确
python3 check_config.py

# 测试数据获取（只测试AAPL）
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY --tickers AAPL
```

---

**推荐设置**：在开发阶段使用 MAG7，可以：
- ⚡ 提高开发效率（2分钟 vs 25分钟）
- 💰 节省API额度（21次 vs 306次）
- 🎯 快速验证策略效果
- 🔄 更快的迭代周期
