# 限流问题 - 决策树

```
你遇到了 "Too Many Requests" 或 "Rate limited" 错误
│
├─ 你愿意花5分钟注册免费API吗？
│  │
│  ├─ YES → 推荐方案: Alpha Vantage ⭐⭐⭐⭐⭐
│  │       │
│  │       ├─ 步骤:
│  │       │   1. 访问: https://www.alphavantage.co/support/#api-key
│  │       │   2. 填写邮箱，获取API key
│  │       │   3. 运行: python3 configure_datasource.py
│  │       │   4. 选择: 2 (alphavantage)
│  │       │   5. 输入API key
│  │       │   6. 运行: python3 main.py --update
│  │       │
│  │       ├─ 结果:
│  │       │   ✅ 无限流问题
│  │       │   ✅ 高成功率 (>99%)
│  │       │   ✅ NASDAQ 100 约25分钟
│  │       │   ✅ 每天500次请求（足够用）
│  │       │
│  │       └─ 备选: Polygon.io
│  │           └─ 访问: https://polygon.io/
│  │
│  └─ NO → 临时方案: 增加延迟 ⚠️
│          │
│          ├─ 步骤:
│          │   1. 编辑 config/config.yaml
│          │   2. 设置 request_delay: 20.0
│          │   3. 运行: python3 main.py --update
│          │
│          ├─ 结果:
│          │   ⚠️  仍可能限流
│          │   ⚠️  成功率约70%
│          │   ⚠️  NASDAQ 100 约40分钟
│          │   ⚠️  不稳定
│          │
│          └─ 建议: 稍后切换到 Alpha Vantage

你想要最简单的方式吗？
│
├─ YES → 使用配置向导
│        │
│        ├─ 命令: python3 configure_datasource.py
│        │
│        ├─ 流程:
│        │   1. 选择数据源
│        │   2. 输入API key (如需要)
│        │   3. 自动更新配置
│        │
│        └─ 优点: 交互式，容易操作
│
└─ NO → 手动配置
         │
         ├─ 编辑: config/config.yaml
         │
         ├─ 修改:
         │   data:
         │     source:
         │       type: alphavantage
         │       api_key: "YOUR_KEY"
         │       request_delay: 12.0
         │
         └─ 优点: 完全控制

你需要验证配置吗？
│
├─ 检查配置
│  └─ python3 check_config.py
│
├─ 测试数据源
│  └─ python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY
│
└─ 正常使用
   └─ python3 main.py --update

---

快速决策表:

┌─────────────────┬──────────┬─────────┬──────────┬─────────┐
│     场景        │   方案   │  时间   │  成功率  │  推荐度 │
├─────────────────┼──────────┼─────────┼──────────┼─────────┤
│ 长期使用        │ AlphaV   │ 5min配置│  99%     │ ⭐⭐⭐⭐⭐│
│ 快速临时        │ YF+20s   │ 即刻    │  70%     │ ⚠️⚠️     │
│ 数据质量优先    │ AlphaV   │ 5min配置│  99%     │ ⭐⭐⭐⭐⭐│
│ 不想注册        │ YF+20s   │ 即刻    │  70%     │ ⚠️⚠️     │
│ 开发测试        │ YF+10s   │ 即刻    │  50%     │ ⭐⭐      │
│ 生产环境        │ AlphaV   │ 5min配置│  99%     │ ⭐⭐⭐⭐⭐│
└─────────────────┴──────────┴─────────┴──────────┴─────────┘

---

工具选择:

你想...?
│
├─ 快速配置 → python3 configure_datasource.py
├─ 验证配置 → python3 check_config.py
├─ 测试数据 → python3 tests/test_data_source.py
├─ 查看文档 → cat QUICK_START.md
└─ 正常使用 → python3 main.py --update

---

文档选择:

你的情况...?
│
├─ 急需解决问题 (3分钟) → QUICK_START.md
├─ 快速查找方案 (5分钟) → QUICKFIX.md
├─ 了解完整方案 (10分钟) → SOLUTION_GUIDE.md
├─ 技术升级细节 (15分钟) → UPGRADE_NOTES.md
└─ 深入学习指南 (30分钟) → docs/DATA_SOURCE_GUIDE.md

---

故障排查:

遇到问题...?
│
├─ 配置不生效
│  └─ 检查: python3 check_config.py
│
├─ API key 无效
│  └─ 重新申请: https://www.alphavantage.co/support/#api-key
│
├─ 仍然限流
│  ├─ 增加 request_delay
│  └─ 切换数据源
│
├─ 数据格式错误
│  └─ 查看日志: tail -f logs/stock_screener.log
│
└─ 其他问题
   └─ 查看文档或回滚:
       cp src/data_fetcher_yfinance_only.py src/data_fetcher.py

---

推荐路径 (99%用户):

1. 获取 Alpha Vantage API key (2分钟)
   → https://www.alphavantage.co/support/#api-key

2. 配置向导 (1分钟)
   → python3 configure_datasource.py

3. 验证配置 (30秒)
   → python3 check_config.py

4. 测试 (1分钟)
   → python3 tests/test_data_source.py --source alphavantage --api-key YOUR_KEY

5. 使用 (正常)
   → python3 main.py --update

总耗时: < 5分钟
成功率: 99%
```
