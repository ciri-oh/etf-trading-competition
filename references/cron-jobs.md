# Cron Job 配置记录

> **2026-07-02 更新：** 3个 cron job + Kanban 看板自动流转

---

## 一、架构概览

```
Cron触发（3个）          Kanban自动流转（1个）
─────                  ──────────────
策略员统一调度 (08:40建链+盘前策略, 11:40/14:40盘中刷新)
交易员 (每10分钟)       信息员 (策略员创建链后自动派发)
巡检员 (每30分钟)
```

Gateway 内置 Dispatcher 每60秒检查一次 Kanban，自动派发就绪任务。

---

## 二、策略员统一调度（0a8fc560ccea）

**Job ID:** `0a8fc560ccea`
**Schedule:** `40 8,11,14 * * 1-5`（每天 08:40 / 11:40 / 14:40）
**Model:** deepseek-v4-flash / arkcode
**Skills:** etf-trading-competition, query-indicator, financial-analysis
**Profile:** strategist
**deliver:** origin

**职责：** 合并了原建链员 cron、策略员盘前自动流转、策略员盘中 cron 的所有职责。

### 08:40 执行（早盘启动）
1. 创建今日看板链（morning-analysis → info-collector → strategist-morning，**--tenant etf-trading**）
2. 等待 info-collector 完成（每30秒检查，最多5分钟）
3. 读取 [INFO] + 知识库
4. 出完整盘前策略，写 [STRATEGY] 到 Kanban
5. 推送策略报告给用户

### 11:40 / 14:40 执行（盘中刷新）
1. 找到今日 strategist-morning 任务
2. 读取 [INFO] / [PATROL] / [TRADE] 评论
3. 判断是否需要刷新策略
4. 有变化 → 更新 [STRATEGY] 并推送
5. 无变化 → 静默

---

## 三、交易员-执行交易

**Job ID:** `61744362a58e`
**Schedule:** `5,15,25,35,45,55 9-10,13-14 * * 1-5`（每10分钟）
**Model:** deepseek-v4-flash / arkcode
**Skills:** a-share-paper-trading, query-indicator
**Profile:** trader
**deliver:** (none — silent unless trade executed)

**职责：**
- 09:25前静默
- 每10分钟读 Kanban 获取策略指令，按指令执行
- 有交易 → 写 [TRADE] + 输出报告
- 无交易 → 绝对静默
- **动态查找策略**：自动查找当日 strategist-morning 任务，不硬编码任务 ID

---

## 四、巡检员-盘中巡视

**Job ID:** `133c1110de1b`
**Schedule:** `25 9-10,13-14 * * 1-5`
**Model:** deepseek-v4-flash / arkcode
**Skills:** a-share-paper-trading, query-indicator, financial-analysis
**Profile:** inspector
**deliver:** origin

**职责：**
- 09:25前静默
- 每30分钟巡视市场
- 有异动 → 写 [PATROL] + 输出简报
- 无异常 → 绝对静默

---

## 五、Kanban 自动流转角色

**信息员：** 策略员 08:40 cron 创建看板链 → Dispatcher自动派发 → 采集数据 → 写[INFO] → complete

⚠️ **信息员是唯一的 Kanban 自动流转角色**，策略员不再通过 Kanban 自动派发。

---

## 六、规则速查

| 场景 | 规则 |
|------|------|
| 仓位<50% | 禁止建议减仓 |
| 策略员 | 08:40必须出盘前策略；11:40/14:40有变动才出 |
| 交易员无交易 | 绝对静默 |
| 交易员有交易 | 输出+写 Kanban |
| 巡检无异动 | 绝对静默 |
| 巡检有异动 | 输出+写 Kanban |
| 减仓后成本变化 | 虚假高收益不算止盈 |
| 创建看板链 | **必须加 --tenant etf-trading** |
