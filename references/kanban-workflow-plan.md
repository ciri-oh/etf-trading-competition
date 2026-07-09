# Kanban 工作流方案（方案B2）

> 2026-06-25 创建
> 目的：将6个独立 cron job 简化为混合 Kanban + Cron 架构

## 架构总结

```
Kanban 任务链（一次性任务）
    08:25 Cron Job → 创建主任务
        ↓ Gateway Dispatcher 自动 dispatch
    信息员 → 采集数据 → 完成
        ↓ 自动解锁
    策略员 → 出策略 → 完成
        ↓ 自动解锁
    （下游任务等待循环 cron job 触发）

独立 Cron Job（循环任务）
    交易员（每10分钟）→ 检查价格 → 执行
    巡检员（每30分钟）→ 巡视市场 → 写 Kanban
```

## 为什么不全用 Kanban？

- Kanban 任务被 dispatch 一次后变为 done 状态，无法循环
- 交易员需要每10分钟、巡检员需要每30分钟精确执行
- Kanban schedule 只能放回队列，无法精确控制时间间隔
- **方案B2**：一次性任务通过 Kanban（自动流转），循环任务用 cron job（精确时间）

## 当前部署状态

### Cron Jobs（已暂停，准备拆除）
| Job ID | 名称 | Schedule | 状态 |
|--------|------|----------|------|
| e399c9d89e95 | 信息员 | 08:30 | paused |
| f6f2aac7e6e5 | 策略员-盘前 | 09:00 | paused |
| f56c50539a35 | 策略员-午盘 | 12:30 | paused |
| f6f227767194 | 策略员-尾盘 | 14:35 | paused |
| b0c321546a0d | 交易员 | */10 | paused |
| 709c073a2b8f | 巡检员 | 每30分钟 | paused |

### Kanban 任务链
- 主任务：t_49337580
- 信息员：t_ea0b4cf2 → 策略员：t_b9ae036d → 巡检员：t_4f2ba4af + 交易员：t_6f2004c8

## 注意事项

1. Gateway Dispatcher 默认每60秒检查一次就绪任务
2. Kanban comment 可被 security scan 拦截，中文内容需写入临时文件再管道提交
3. Kanban 任务完成后不会自动重新创建，每日需由总控 cron 重新创建
4. 交易员/巡检员 cron job 保留独立 prompt 以维持精确时间控制
