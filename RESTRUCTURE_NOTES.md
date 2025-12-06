# 📁 项目结构重组说明

## 变更日期
2025-12-06

## 变更内容

### 新增目录
创建了 `tests/` 目录，统一管理所有测试和诊断工具。

### 文件移动

以下测试文件已从根目录移动到 `tests/` 目录：

```
根目录 → tests/
├── test_data_source.py       → tests/test_data_source.py
├── test_alphavantage_direct.py → tests/test_alphavantage_direct.py
├── debug_alphavantage.py     → tests/debug_alphavantage.py
└── test_fetch.py             → tests/test_fetch.py
```

### 保留在根目录的文件

以下工具文件保留在根目录（因为它们是用户主要使用的工具）：

- `configure_datasource.py` - 配置向导（用户常用）
- `check_config.py` - 配置检查（用户常用）
- `main.py` - 主程序入口

## 更新后的目录结构

```
stock_screener/
├── main.py                      # 主程序
├── configure_datasource.py      # 配置向导（常用工具）
├── check_config.py              # 配置检查（常用工具）
├── requirements.txt
├── config/
│   └── config.yaml
├── src/
│   ├── data_fetcher.py
│   ├── data_fetcher_multi.py
│   └── ... (其他源代码)
├── tests/                       # ⭐ 新增测试目录
│   ├── README.md               # 测试工具说明
│   ├── test_data_source.py     # 数据源测试
│   ├── debug_alphavantage.py   # API诊断
│   ├── test_alphavantage_direct.py
│   └── test_fetch.py
├── docs/                        # 文档目录
├── data/                        # 数据存储
├── reports/                     # 报告输出
└── logs/                        # 日志文件
```

## 使用方法更新

### 测试数据源
**之前**:
```bash
python3 test_data_source.py --source alphavantage --api-key YOUR_KEY
```

**现在**:
```bash
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
```

### 调试 Alpha Vantage
**之前**:
```bash
python3 debug_alphavantage.py
```

**现在**:
```bash
python3 tests/debug_alphavantage.py
```

### 配置工具（无变化）
```bash
# 这些工具仍在根目录，使用方法不变
python3 configure_datasource.py
python3 check_config.py
python3 main.py --update
```

## 文档更新

所有相关文档已自动更新，包括：
- ✅ `QUICK_START.md`
- ✅ `QUICKFIX.md`
- ✅ `SUMMARY.md`
- ✅ `SOLUTION_GUIDE.md`
- ✅ `UPGRADE_NOTES.md`
- ✅ `IMPLEMENTATION_CHECKLIST.md`
- ✅ `DECISION_TREE.md`
- ✅ `INDEX.md`
- ✅ `NEW_FEATURES.md`
- ✅ `BUGFIX_ALPHAVANTAGE.md`
- ✅ `README.md`

## 优势

### 1. 更清晰的项目结构
- 测试文件统一管理
- 根目录更整洁
- 职责分离明确

### 2. 更好的可维护性
- 测试工具集中在一个目录
- 新增测试更容易
- 文档查找更方便

### 3. 更符合Python项目规范
- 标准的 `tests/` 目录
- 遵循最佳实践
- 易于CI/CD集成

## 测试工具快速参考

```bash
# 查看所有测试工具
ls tests/

# 查看测试工具说明
cat tests/README.md

# 运行数据源测试
python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

# 运行API诊断
python3 tests/debug_alphavantage.py

# 直接测试Alpha Vantage
python3 tests/test_alphavantage_direct.py
```

## 常用命令对照

| 功能 | 命令 | 位置 |
|------|------|------|
| 配置数据源 | `python3 configure_datasource.py` | 根目录 |
| 检查配置 | `python3 check_config.py` | 根目录 |
| 测试数据源 | `python3 tests/test_data_source.py` | tests/ |
| API诊断 | `python3 tests/debug_alphavantage.py` | tests/ |
| 运行主程序 | `python3 main.py --update` | 根目录 |

## 迁移指南

如果你有脚本或文档引用了旧路径：

### 查找需要更新的地方
```bash
# 查找所有引用test_data_source.py的文件
grep -r "test_data_source.py" .

# 查找所有引用debug_alphavantage.py的文件
grep -r "debug_alphavantage.py" .
```

### 批量更新（如果需要）
```bash
# 更新所有.md文件中的路径
find . -name "*.md" -exec sed -i '' 's|python3 test_data_source|python3 tests/test_data_source|g' {} \;
find . -name "*.md" -exec sed -i '' 's|python3 debug_alphavantage|python3 tests/debug_alphavantage|g' {} \;
```

## 注意事项

1. **书签和快捷方式**: 如果你有IDE书签或快捷方式，需要更新路径
2. **脚本引用**: 如果你有自己的脚本调用测试工具，需要更新路径
3. **文档笔记**: 如果你有个人笔记引用了这些文件，需要更新

## 回滚方案

如果需要回到旧结构：

```bash
# 移动文件回根目录
mv tests/test_data_source.py .
mv tests/debug_alphavantage.py .
mv tests/test_alphavantage_direct.py .
mv tests/test_fetch.py .

# 删除tests目录（如果为空）
rmdir tests
```

## FAQ

### Q: 为什么 configure_datasource.py 不移到 tests/?
**A**: 因为它是用户常用的配置工具，不是测试工具。保留在根目录更方便用户访问。

### Q: 为什么 check_config.py 不移到 tests/?
**A**: 同理，这是配置验证工具，是正常使用流程的一部分，不是测试工具。

### Q: tests/ 目录会影响主程序吗？
**A**: 不会。tests/ 目录是独立的，不影响 main.py 和 src/ 的运行。

### Q: 如何添加新的测试？
**A**: 在 tests/ 目录创建新文件，命名为 `test_*.py` 或 `debug_*.py`，并更新 `tests/README.md`。

## 总结

✅ **好处**:
- 项目结构更清晰
- 符合Python规范
- 易于维护和扩展
- 根目录更整洁

✅ **影响**:
- 所有文档已更新
- 测试命令需要加 `tests/` 前缀
- 配置工具使用方法不变

✅ **状态**:
- 重组完成
- 文档已更新
- 测试通过
- 可正常使用

---

**重组完成**: 2025-12-06  
**状态**: ✅ 完成  
**影响**: 仅路径变化，功能无变化
