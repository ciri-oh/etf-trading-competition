# Kanban 策略统一来源踩坑记录

> 2026-06-26 发现。记录策略来源不统一问题和解决方案。

## 问题

所有角色（交易员、巡检员、策略员盘中）应从看板同一份 `[STRATEGY]` 策略执行。但实际发现各角色读到不同的策略：

- 交易员读到的是今天新出的策略
- 巡检员读到了6天前的旧策略
- 策略员看到的又是另一个时段的数据

## 根因分析

### 1. `[STRATEGY]` 标签缺失

策略员通过 Kanban 自动派发执行后，其策略内容通常写入 `--summary` 参数（`kanban complete --summary "..."`），而非 `kanban comment`。

- 策略输出存在 `task.latest_summary` 字段中
- 但巡检员/交易员按 `[STRATEGY]` 标签搜索 comments，找不到任何内容
- Fallback 机制不完善，读到了旧任务中的历史策略

### 2. 看板任务复用旧 ID

每日应该创建新的看板任务链，但实际复用 `t_b9ae036d` 这个旧任务。

- 旧任务有3天的历史评论堆积
- 各角色定位策略时容易读到错误日期的评论
- 每天重建新任务可彻底避免此问题

### 4. info-collector 任务处于 running 状态（2026-07-02 发现）

**场景**：策略员 08:40 运行时，info-collector 任务状态为 `running`（非 `done`），信息员尚未完成数据采集。此时：
- `[INFO]` 评论数为 0
- `latest_summary` 字段为空
- 任务仍在执行中，不可读取

**根因**：建链员 08:30 创建任务后，Gateway Dispatcher 需要约 60s 派发，信息员完成数据采集也需要时间。08:40 策略员运行时信息员可能仍在执行。

**解决方案**：
1. 策略员不应因无信息而放弃出策略——信息不足也要出策略（后续补充后再刷新）
2. 从历史数据或知识库获取背景信息
3. 出策略时注明「信息员数据采集仍在进行中，策略基于已有信息」
4. 后续盘中刷新（11:40/14:40）会自动读到完整信息后刷新策略

**正确行为示例**：
```
[STRATEGY] 盘前策略 - 2026-07-02 08:40

[策略内容]
...

[背景]
信息员数据采集仍在进行中，策略基于已有信息制定
```
## 踩坑：`created_at` 是 Unix 时间戳（int），不是字符串

用 Python 解析 kanban comments 时，`created_at` 字段是 **int 类型的 Unix 时间戳**（如 `1782455545`），不是字符串。

**错误写法（会报 TypeError）：**
```python
# ❌ TypeError: argument of type 'int' is not iterable
strategy_comments = [c for c in comments if '[STRATEGY]' in c.get('body', '') and today in c.get('created_at', '')]
```

**正确写法：**
```python
import datetime
today = datetime.date.today().strftime('%Y-%m-%d')
for c in comments:
    ts = c.get('created_at', 0)
    if isinstance(ts, int):
        dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    else:
        dt = str(ts)
    # 然后用 dt 做日期比较
```

**避坑：** 不要用 `in` 检查 int 是否包含日期字符串。先将 int 时间戳转为日期字符串再比较。

## 修复方案

### 短期：读 `latest_summary` 作为备选

当搜索 `[STRATEGY]` 标签找不到结果时：
```bash
# 先找当日 info-collector 任务
hermes kanban list | grep info-collector

# 读该任务的 latest_summary 字段
hermes kanban show --json <task_id> | python3 -c "
import json,sys
data = json.load(sys.stdin)
task = data['task'] if isinstance(data, dict) and 'task' in data else data
summary = task.get('latest_summary', '')
print(summary)
"
```

### 长期：规范策略输出流程

1. 策略员任务 body 必须要求：
   - 写 `kanban comment` 带 `[STRATEGY]` 标签
   - 同时用 `kanban complete --summary "..."` 写入概要

2. 交易员/巡检员读策略时按优先级：
   - ① 找当日 info-collector 任务
   - ② 搜索 comments 中 `[STRATEGY]` 标签的最新评论
   - ③ 读 `latest_summary` 字段
   - ④ 以上均无 → 静默，不执行

3. 每天建新任务链，不复用旧任务
