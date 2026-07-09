# 2026-07-02 系统审查：策略来源统一与Dispatcher冲突

## 发现的核心问题

### 问题1：策略来源不统一

交易员、巡检员 cron prompt 中的策略来源指向 `info-collector`，而非 `strategist-morning`。

**根因：** 早期架构中 `t_b9ae036d`（原始 strategist 任务）是统一信源，后来改为 `info-collector`，但最终统一到了 `strategist-morning`。cron prompt 未同步更新。

**修复：** 修改 jobs.json 中所有角色的 prompt：
- 交易员（61744362a58e）：策略来源 → `strategist-morning`
- 巡检员（133c1110de1b）：策略来源 → `strategist-morning`
- 策略员（0a8fc560ccea）：输出 → `strategist-morning`

### 问题2：build-chain.sh 创建 strategist-morning 导致 Dispatcher 冲突

**场景：** 建链脚本创建 `morning-analysis → info-collector → strategist-morning`，其中 `strategist-morning` 的 `--assignee strategist`。

**冲突链：**
1. 08:30 建链 cron 创建 `strategist-morning`（status=todo）
2. Gateway Dispatcher 每60秒扫描，发现 `strategist-morning` ready → 派发新 `strategist` profile 实例
3. 08:40 策略员 cron（profile=strategist）同时运行 → 也想创建/写 strategist-morning
4. **两个实例竞争同一任务** — 不可控

**修复：** 建链脚本只创建 `morning-analysis → info-collector`，不创建 `strategist-morning`。策略员 cron 在 08:40 自行创建 `strategist-morning` 并直接写 `[STRATEGY]`。

## 统一策略来源铁律

> **所有角色统一从 `strategist-morning` 读 `[STRATEGY]`。单一信源，不允许分裂。**

```
info-collector    [INFO]
strategist-morning [STRATEGY] ← 策略员写出
                        ↓
                 交易员读取  巡检员读取
```

## 修复文件清单

| 文件 | 修改内容 |
|------|---------|
| `~/.hermes/cron/jobs.json` | 交易员prompt策略来源→strategist-morning |
| `~/.hermes/cron/jobs.json` | 巡检员prompt策略来源→strategist-morning |
| `~/.hermes/cron/jobs.json` | 策略员prompt→不建链，只读kanban出策略 |
| `/root/.hermes/scripts/create-chain.sh` | 删除strategist-morning创建步骤 |
| `cron-prompt-templates.md` | 更新为4 Cron架构，策略来源→strategist-morning |
| `session-2026-06-25-architectural-decisions.md` | 更新job ID和架构描述 |
| `etf-trading-competition/SKILL.md` | cron架构表、关键规则表、统一策略来源节 |