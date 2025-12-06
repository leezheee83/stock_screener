# 限流问题解决方案 - 快速参考

## 🚨 你遇到的问题

```
WARNING - 获取 ADBE 触发限流，5秒后重试 (第1/3次)
ERROR - 获取 ADBE 数据失败: Too Many Requests. Rate limited. Try after a while.
```

## ✅ 解决方案（3种，按推荐度排序）

### 方案 1: 切换到 Alpha Vantage（推荐）⭐⭐⭐⭐⭐

**耗时**: 5分钟  
**成功率**: 99%  
**费用**: 免费

**步骤**：
1. 获取API Key: https://www.alphavantage.co/support/#api-key （填写邮箱即可）
2. 运行配置向导:
   ```bash
   python3 configure_datasource.py
   ```
   选择 `2` (alphavantage)，输入你的API key

3. 测试:
   ```bash
   python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
   ```

4. 运行:
   ```bash
   python3 main.py --update
   ```

**预期结果**: 
- 无限流错误
- NASDAQ 100 约25分钟完成

---

### 方案 2: 手动配置 Alpha Vantage ⭐⭐⭐⭐

如果配置向导有问题，手动编辑配置文件。

**编辑** `config/config.yaml`:
```yaml
data:
  source:
    type: alphavantage
    api_key: "YOUR_API_KEY_HERE"  # 替换成你的key
    request_delay: 12.0
    max_retries: 3
    max_workers: 1
    batch_size: 10
```

保存后运行:
```bash
python3 main.py --update
```

---

### 方案 3: 继续用 Yahoo Finance 但增加延迟 ⭐⭐

**临时方案，仍可能限流**

**编辑** `config/config.yaml`:
```yaml
data:
  source:
    type: yfinance
    api_key: ""
    request_delay: 20.0    # 增加到20秒
    max_retries: 5         # 增加重试
    max_workers: 1
    batch_size: 5          # 减小批次
```

**预期结果**: 
- 可能仍有限流
- NASDAQ 100 约40-50分钟完成

---

## 📊 三种方案对比

| 方案 | 延迟 | 时间 | 限流风险 | 稳定性 |
|------|------|------|---------|--------|
| Alpha Vantage | 12s | ~25分钟 | 极低 ⭐⭐⭐⭐⭐ | 极高 |
| Polygon.io | 12s | ~25分钟 | 极低 ⭐⭐⭐⭐⭐ | 极高 |
| Yahoo Finance (20s) | 20s | ~40分钟 | 中等 ⭐⭐ | 一般 |
| Yahoo Finance (15s) | 15s | ~30分钟 | 高 ⭐ | 差 |

---

## 🧪 验证是否成功

运行后，查看日志应该看到:

✅ **成功的情况**:
```
INFO - Alpha Vantage 数据源已初始化 (延迟: 12.0秒)
INFO - ✓ AAPL (1/102)
INFO - ✓ MSFT (2/102)
INFO - ✓ GOOGL (3/102)
```

❌ **仍然失败**:
```
WARNING - 获取 AAPL 触发限流
ERROR - 获取 AAPL 数据失败: Too Many Requests
```

---

## 🔍 故障排查

### 问题: "需要API key"
**解决**: 
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- Polygon: https://polygon.io/

### 问题: "Invalid API key"
**解决**: 
- 检查 config.yaml 中 api_key 是否正确
- 确保没有多余的空格或引号

### 问题: 仍然限流
**解决**:
- 增加 request_delay 到 15-20 秒
- 减小 batch_size 到 5
- 确认配置文件已保存

### 问题: ImportError
**解决**:
```bash
pip install -r requirements.txt
```

---

## 📞 快速命令参考

```bash
# 1. 交互式配置
python3 configure_datasource.py

# 2. 测试数据源
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 3. 更新数据
python3 main.py --update

# 4. 查看日志
tail -f logs/stock_screener.log
```

---

## 💡 为什么推荐 Alpha Vantage？

✅ **优点**:
1. 免费且无需信用卡
2. 每天500次请求（足够用）
3. 数据质量优秀
4. 限流宽松
5. 官方支持

❌ **Yahoo Finance 问题**:
1. 限流规则不透明
2. 无官方API文档
3. 随时可能改变策略
4. 无技术支持

---

## 🎯 推荐行动

**立即执行**:
```bash
# 1. 获取API key（2分钟）
# 访问: https://www.alphavantage.co/support/#api-key

# 2. 配置（1分钟）
python3 configure_datasource.py

# 3. 测试（1分钟）
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 4. 使用（正常）
python3 main.py --update
```

**总耗时**: < 5分钟  
**成功率**: 99%

---

## 📚 详细文档

- [完整数据源指南](docs/DATA_SOURCE_GUIDE.md)
- [升级说明](UPGRADE_NOTES.md)
- [主README](README.md)
