# Daily Kanban Cleanup & Strategy Source Protocol

> Created: 2026-06-26 — Root cause analysis and fix for [STRATEGY] tag missing bug that caused patrol officer to read stale strategy from 6/24.

## The Bug (2026-06-26)

- Strategist-morning task executed via Kanban dispatch
- Its strategy was stored in `latest_summary` (via `--summary` flag on `kanban complete`), NOT as a tagged `[STRATEGY]` comment
- Patrol officer searched comments for `[STRATEGY]` — found nothing from today
- Fallback logic (reading latest comment without date filter) picked up a 3-day-old strategy from `t_b9ae036d`
- Result: patrol officer reported "仓位严重偏离" when actual position was 68% (correct)

## Daily Cleanup Protocol

**执行者：** 用户说「打开比赛」→ 助手手动创建当日看板链

**步骤：**
1. 清理旧看板（归档所有 done/archived 状态的旧任务）
2. 创建今日全新看板链：morning-analysis → info-collector → strategist-morning
3. 主任务完成后 dispatcher 自动派发信息员 → 信息员完成后派发策略员

**⚠️ 重要：链创建是手动步骤，不是交易员 cron 的职责。** 交易员 cron（`61744362a58e`）是纯执行者，不创建看板链。

```bash
# 清理旧看板（归档所有 done/archived 状态的旧任务）
hermes kanban list --status archived 2>&1 | grep 't_' | awk '{print $1}' | while read tid; do
    hermes kanban archive "$tid" 2>/dev/null
done
```

## 2026-06-29 清理记录

**清理了 14 个归档任务：**
- 旧链任务：`t_49337580`（晨间分析）、`t_ea0b4cf2`（info-collector）、`t_b9ae036d`（strategist）、`t_4f2ba4af`（patrol-officer）、`t_6f2004c8`（trader）
- 旧链任务（重复）：`t_e94df75b`（morning-analysis）、`t_eeca28f7`（info-collector）、`t_f3438419`（strategist-morning）
- 测试任务：`t_743315a2`、`t_13e90123`、`t_ff18b991`、`t_8d47ecfa`、`t_46e60118`、`t_fed806d3`
- 旧任务：`t_521b52ea`（ETF交易比赛）、`t_6418efb6`（信息员-数据采集）、`t_708e666a`（策略员-盘前决策）

**保留的活跃任务：** `t_e8c8fa4d`（morning-analysis）、`t_9d01fef3`（info-collector）、`t_5bd381f7`（strategist-morning）

## Unified Strategy Source Rules

1. **策略员出策略** → 写 Kanban 评论，前缀 `[STRATEGY]`，内容含完整操作指令
2. **交易员读策略** → 按 `[STRATEGY]` 标签 + 日期过滤
3. **巡检员读策略** → 按 `[STRATEGY]` 标签 + 日期过滤
4. **策略员盘中读输出** → 按 `[TRADE]` / `[PATROL]` + 日期过滤

## [STRATEGY] Tag Fallback

如果 comments 中找不到 `[STRATEGY]` 标签的策略：
1. 检查 `latest_summary` 字段（可能由 `kanban complete --summary` 写入）
2. 验证日期是否为今天
3. 如果今天没有有效策略 → **绝对静默**，不要用旧策略

```bash
# 读取策略（带 fallback）
hermes kanban show --json <task_id> > /tmp/strat_check.json
python3 -c "
import json, datetime
data = json.load(open('/tmp/strat_check.json'))
today = datetime.date.today().isoformat()

# 辅助函数：将 int 时间戳转为日期字符串
def ts_to_date(ts):
    if isinstance(ts, (int, float)):
        return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    return str(ts)

comments = data.get('comments', [])

# 方法1：在 comments 中找 [STRATEGY]
strat = [c for c in comments if '[STRATEGY]' in c.get('body','') and today in ts_to_date(c.get('created_at',0))]
if strat:
    print(strat[-1]['body'][:2000])
    exit(0)

# 方法2：在 latest_summary 中找
summary = data.get('task', {}).get('latest_summary', '')
if summary and today in summary:
    print(summary)
    exit(0)

# 方法3：找评论中含'策略'关键词的最新今天评论
strat2 = [c for c in comments if any(kw in c.get('body','') for kw in ['策略','决策','操作计划']) and today in ts_to_date(c.get('created_at',0))]
if strat2:
    print(strat2[-1]['body'][:2000])
    exit(0)

# 找不到 → 静默
print('NO_STRATEGY')
"
```

## Task ID Rotation

- 旧的 `t_b9ae036d` 是原始 strategist 任务，包含历史策略，不应硬编码
- 每日交易员新建的任务 ID 每天不同（如 `t_f3438419`）
- 读取策略前先 `hermes kanban list` 找到当日 `strategist-morning` 任务
- 验证方法：检查策略的日期戳是否为今天
