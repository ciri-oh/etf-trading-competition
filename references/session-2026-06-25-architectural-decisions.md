# 2026-06-25 架构决策与踩坑记录（2026-07-02更新）

## 最终方案：4 Cron + Kanban

共4个独立cron job + Gateway Dispatcher自动流转看板链。
建链员（脚本）、策略员、交易员、巡检员各司其职。
信息员通过建链员08:30创建的看板链自动流转（Gateway Dispatcher 派发）。

## 统一策略来源（2026-06-25修正，2026-07-02确认）

所有角色从看板 `strategist-morning` 任务下最新 `[STRATEGY]` 标签评论读取策略。
交易员、巡检员、策略员全部从同一个位置读，保证策略统一。

## 技术踩坑

### Cron prompt长度限制
创建长度~200+字符的prompt会报错 `'<=' not supported between instances of 'str' and 'int'`。
短prompt（~50字符）成功。长prompt（~500+）失败。
**方案：** 精简prompt到核心规则，或用长prompt但避免同时传 `deliver` + `repeat` 参数。
**绕路方案：** 先创建短prompt job，然后直接编辑 `~/.hermes/cron/jobs.json` 覆盖prompt字段。

### Kanban schedule限制
`hermes kanban schedule <task_id>` 对done任务返回"cannot schedule"。
只有ready/blocked/scheduled状态才能被重新调度。

### Kanban daemon已弃用
`hermes kanban daemon` 报错提示dispatcher已集成到Gateway。
配置: `kanban.dispatch_in_gateway: true`（config.yaml默认值）。

### strategist-morning 由策略员cron自行创建（2026-07-02）
建链脚本不创建 strategist-morning，避免 Gateway Dispatcher 与策略员 cron 竞争。
策略员 cron 在 08:40 自行创建 strategist-morning 并直接写 [STRATEGY]。

## 交易员执行纪律（2026-06-25修正）

策略员说"买入X,目标价≤Y" → 交易员只在**当前价≤Y**时执行。
策略员说"持有/观望" → **不操作**。
策略员说"买入但当前价>目标价" → 不追高。
没有指令 → 绝对静默。
事在KANBAN里解决，有事找策略员，不直接反馈给用户。

## 当前活跃Job ID

| 角色 | Job ID | Schedule |
|------|--------|----------|
| 建链员 | 6a2228d9b04a | 30 8 * * 1-5 |
| 策略员 | 0a8fc560ccea | 40 8,11,14 * * 1-5 |
| 交易员 | 61744362a58e | 5,15,25,35,45,55 9-10,13-14 * * 1-5 |
| 巡检员 | 133c1110de1b | 25 9-10,13-14 * * 1-5 |