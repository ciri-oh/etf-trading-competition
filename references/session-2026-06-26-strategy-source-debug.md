# 2026-06-26 — 策略统一来源调试记录

## 背景

Kanban + 3 Cron 新架构第一天运行。巡检员13:25报"仓位严重偏离"，但实际仓位68%为正常范围。

## 排查过程

1. 查看板 `t_b9ae036d` 评论 → 14条评论，3天数据堆积，无今日 `[STRATEGY]` 标签
2. 策略员盘前通过 Kanban 自动派发执行，其策略输出通过 `kanban complete --summary` 写入 `latest_summary` 字段
3. 巡检员按 `[STRATEGY]` 标签搜索 comments → 找不到 → fallback 到旧策略
4. `hermes kanban list` 发现当日 `strategist-morning` 任务 ID 是 `t_f3438419`（非 `t_b9ae036d`）

## 结论

- **Kanban 自动派发的任务**：策略写入 `latest_summary`（`--summary` 参数），而非 comments
- **旧任务复用**：`t_b9ae036d` 是原始 strategist 任务，不应硬编码
- **每天重建链**：交易员09:05建链后，新 ID 每日不同

## 修复

1. 清理旧看板任务
2. 创建今日全新看板链
3. 巡检员读策略时增加 `latest_summary` fallback + 日期过滤

## 关键命令

```bash
# 找到当日 strategist 任务
hermes kanban list | grep strategist-morning

# 读 latest_summary（如果 [STRATEGY] 标签缺失）
hermes kanban show --json <task_id> | python3 -c "import json,sys; d=json.load(sys.stdin); t=d.get('task',d); print(t.get('latest_summary',''))"

# 验证日期
hermes kanban show --json <task_id> | python3 -c "import json,sys; d=json.load(sys.stdin); t=d.get('task',d); print('created:', t.get('created_at','')[:10])"
```
