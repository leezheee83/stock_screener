# 多时间框架分析 - 周趋势确认

## 概述

多时间框架分析是一种通过验证日线信号与周线趋势一致性来减少虚假信号的技术。当日线显示买入信号但周线趋势下跌时，信号可能是假突破，应被过滤。

## 核心原理

### 趋势一致性验证

```
日线信号 + 周线确认 = 高质量信号
日线信号 + 周线冲突 = 潜在假信号（过滤）
```

### 判断逻辑

| 日线趋势 | 周线趋势 | 结果 |
|----------|----------|------|
| 上升 ↑ | 上升 ↑ | ✅ 通过（趋势一致） |
| 下降 ↓ | 下降 ↓ | ✅ 通过（趋势一致） |
| 上升 ↑ | 下降 ↓ | ❌ 拒绝（趋势冲突） |
| 下降 ↓ | 上升 ↑ | ❌ 拒绝（趋势冲突） |
| 任意 | 横盘 → | ✅ 通过（横盘不阻挡） |
| 任意 | 未知 | ✅ 通过（优雅降级） |

## 技术实现

### 模块结构

```
src/filters/
├── __init__.py
├── base_filter.py           # 过滤器基类
└── weekly_trend_filter.py   # 周趋势过滤器
    ├── WeeklyTrendState     # 趋势状态数据类
    └── WeeklyTrendFilter    # 过滤器实现
```

### WeeklyTrendState 数据类

```python
@dataclass
class WeeklyTrendState:
    ticker: str                              # 股票代码
    weekly_ma20: Optional[float]             # 周线MA20当前值
    weekly_ma20_slope: Optional[float]       # 周线MA20斜率
    weekly_trend: str = 'unknown'            # 'up', 'down', 'sideways', 'unknown'
    daily_trend: str = 'unknown'             # 'up', 'down', 'sideways', 'unknown'
    is_aligned: bool = False                 # 日/周趋势是否一致
    rejection_reason: Optional[str] = None   # 拒绝原因
```

### 趋势判断算法

**周线趋势判断**:
1. 计算周线MA20（20周移动平均线）
2. 计算过去4周的MA20斜率：`slope = (MA_now - MA_4weeks_ago) / MA_4weeks_ago`
3. 根据斜率判断趋势：
   - `slope > 0.5%` → 上升
   - `slope < -0.5%` → 下降
   - 其他 → 横盘

**日线趋势判断**:
1. 使用日线MA20的5日斜率
2. 判断标准同上

## 配置说明

在 `config/config.yaml` 中配置：

```yaml
screening:
  filters:
    weekly_trend:
      enabled: true              # 是否启用
      weekly_ma_period: 20       # 周线MA周期
      slope_lookback_weeks: 4    # 计算斜率的回看周数
      min_weekly_slope: 0.0      # 最小周线斜率
      require_alignment: true    # 是否要求日/周趋势一致
      sideways_threshold: 0.005  # 横盘判断阈值（0.5%）
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `enabled` | true | 是否启用周趋势过滤 |
| `weekly_ma_period` | 20 | 周线MA周期（20周≈5个月） |
| `slope_lookback_weeks` | 4 | 计算斜率的回看周数（4周≈1个月） |
| `min_weekly_slope` | 0.0 | 最小周线斜率要求 |
| `require_alignment` | true | 是否要求日/周趋势一致 |
| `sideways_threshold` | 0.005 | 横盘判断阈值（±0.5%内视为横盘） |

## 使用示例

### 筛选流程集成

```python
from src.filters import WeeklyTrendFilter
from src.data_storage import DataStorage

# 初始化
storage = DataStorage()
config = {
    'enabled': True,
    'weekly_ma_period': 20,
    'slope_lookback_weeks': 4
}
weekly_filter = WeeklyTrendFilter(config, data_storage=storage)

# 过滤
passed_stocks, rejected_stocks = weekly_filter.filter(stock_data)
```

### 单股票分析

```python
# 分析单只股票的周趋势状态
state = weekly_filter.analyze_stock('AAPL', daily_df)
print(f"日线趋势: {state.daily_trend}")
print(f"周线趋势: {state.weekly_trend}")
print(f"周MA20斜率: {state.weekly_ma20_slope}")
print(f"趋势一致: {state.is_aligned}")
```

## 运行输出示例

```
WeeklyTrendFilter - INFO - 周趋势过滤: 通过 8/8, 拒绝 0 | 趋势一致=4, 冲突=0, 横盘=4, 数据缺失=0
```

输出解读：
- **通过 8/8**: 8只股票全部通过
- **趋势一致=4**: 4只股票日/周趋势完全一致
- **冲突=0**: 没有日/周趋势冲突的股票
- **横盘=4**: 4只股票有一方趋势为横盘
- **数据缺失=0**: 没有缺少周线数据的股票

## 优雅降级

当周线数据不可用时，过滤器会自动优雅降级：

1. **周线数据缺失** → 允许通过，记录到 `unknown` 统计
2. **周线数据不足** → 趋势标记为 `unknown`，允许通过
3. **计算错误** → 记录警告，允许通过

这确保系统不会因为数据问题而完全阻断筛选流程。

## 性能影响

| 指标 | 值 |
|------|-----|
| 额外加载时间 | <100ms（周线数据缓存） |
| 每股票处理时间 | <5ms |
| 内存占用 | ~10KB/股票（周线数据缓存） |

## 最佳实践

1. **调整阈值**: 根据市场环境调整 `sideways_threshold`
   - 牛市: 可以降低（0.003）
   - 熊市: 可以提高（0.008）

2. **监控拒绝率**: 正常范围 10-30%
   - 如果拒绝率过高（>50%），考虑放宽阈值
   - 如果拒绝率为0，可能需要收紧阈值

3. **结合其他过滤器**: 周趋势过滤应在趋势硬门槛过滤之后使用

## 相关文档

- [趋势评分设计](trend_scoring_design.md)
- [过滤器架构](../src/filters/__init__.py)
- [配置指南](STOCK_UNIVERSE_GUIDE.md)

---

**版本**: 1.0.0  
**创建日期**: 2025-12-07  
**对应任务**: Phase 1 (T001-T011)

