# 2026-07-02 系统审查与修复记录

## 背景

全面审查了 ETF 交易巅峰赛自动化系统的所有配置、cron prompt、建链脚本、profile 配置和文档。发现并修复了多个问题。

## 发现的问题

### 🔴 严重

1. **交易员 prompt 中有无效命令**：`hermes kanban list -c "import json..."` — `-c` 参数不存在，会被 bash 当 flag 解析失败，导致交易员找不到 info-collector 任务 ID，写不了 [TRADE]。
   - **修复**：改为 `hermes kanban list 2>/dev/null | grep info-collector | grep done | awk '{print $2}'`

2. **交易员写 [TRADE] 后不输出给用户**：prompt 写"有交易 → 写 [TRADE] 到 Kanban，不输出任何内容"——交易执行了用户不知道。
   - **修复**：改为"有交易 → 写 [TRADE] 到 Kanban，输出执行报告（不超过3行）"

3. **巡检员 prompt 没有午休规则**：交易员有 `11:30-13:00午休`，巡检员没有。巡检员 schedule 是 `13-14`，13:00 开盘就触发。
   - **修复**：添加 `11:30-13:00午休 → 直接结束`

### 🟡 中等

4. **安全扫描拦截 pipe to python3**：`hermes kanban list --json | python3 -c "..."` 会被安全扫描拦截（报 `Pipe to interpreter: hermes | python3`）。巡检员和交易员 prompt 中都有此模式。
   - **修复**：巡检员改为 `hermes kanban list` + `hermes kanban show --json` 两步；交易员改为 `grep + awk`

5. **策略员 prompt 中 pipe 替换不完整**：之前把 `| python3` 替换掉后留下了无效的 `-c "import json..."` 参数。

6. **SKILL.md 踩坑记录大量重复**：同一踩坑条目（如"Cron job create 对长 prompt 有限制"、"Kanban 工作流不适合循环任务"）出现 3 次。

7. **文档中残留旧 job ID**：`d058d60f5948`（已删除的策略员盘中 cron）、`ee714aa5d69b`（已删除的旧建链 cron）在 SKILL.md 踩坑记录中仍有引用。

### 🟢 轻微

8. **Profile config.yaml 中 agent.provider 配了 edge**：不影响 cron job（cron 有独立 model/provider），但看板任务（info-collector）如果走 Dispatcher 派发，会走 edge 模型而非 arkcode。

## 修复总结

| 文件 | 修改内容 |
|------|---------|
| `cron/jobs.json` | 交易员: 修复无效 -c 参数 + 交易后输出报告 |
| `cron/jobs.json` | 巡检员: 添加午休规则 |
| `cron/jobs.json` | 巡检员: 移除 pipe to python3 |
| `cron/jobs.json` | 交易员: 移除 pipe to python3 残留 |
| `create-chain.sh` | 仅创建 morning-analysis + info-collector（删除 strategist-morning） |
| `SKILL.md` | 更新 cron 架构描述、策略来源、建链说明 |
| `cron-prompt-templates.md` | 全面重写，匹配当前 4 Cron 架构 |
| `architectural-decisions.md` | 更新 job ID 和架构描述 |

## 关键教训

1. **Cron prompt 中禁止 pipe to python3**：安全扫描会拦截 `hermes | python3` 模式。用 `grep + awk` 或分两步执行替代。
2. **Cron prompt 中禁止无效参数**：`hermes kanban list -c "..."` 的 `-c` 不存在，不会报错但会静默失败。
3. **交易员有交易必须输出报告**：执行了 submitOrder 后必须输出执行报告，不能静默。
4. **巡检员必须有午休规则**：`11:30-13:00` 午休期间应跳过。
5. **策略员不创建任何看板任务**：创建任务会导致 Gateway Dispatcher 抢派，与策略员 cron 自身产生冲突。
6. **建链脚本仅创建 2 个任务**：`morning-analysis → info-collector`，不创建 `strategist-morning`。
7. **所有角色统一从 info-collector 读 [STRATEGY]**：单一信源，避免策略分裂。
