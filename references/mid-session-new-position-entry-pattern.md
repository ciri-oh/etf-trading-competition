# Mid-Session New Position Entry Pattern

**Discovered**: 2026-07-08
**Scenario**: Strategist issues a new buy instruction for a **previously unheld** ticker during the 11:40午盘评估 (not the morning strategy), and the trader executes it in the afternoon session.

## Key Differences from Morning Strategy Execution

| Aspect | Morning Strategy | Mid-Session New Entry |
|--------|-----------------|----------------------|
| Strategy source | 08:40 [STRATEGY] (盘前) | 11:40 [STRATEGY] (午盘更新) |
| Position type | Planned new position | **Unexpected** new position (not in morning plan) |
| Quantity basis | Pre-calculated in strategy | May need **recalculation** if price differs from strategist's estimate |
| Price check | Standard (currentPrice <= targetUpper) | Same, but strategist's estimated price may be stale |

## Execution Flow (Verified 2026-07-08)

**Context**: Strategist's 11:40午盘评估报告更新 included:
```
新增指令：加仓港股创新药ETF 513120 SH, 5%仓位
买入数量：58,100 / 1.136 = 51,144股 -> 取整51,100股
执行方式：限价单，价格<=1.145
```

**Trader execution at 13:05**:

### Step 1: Read the latest [STRATEGY]
Find today's info-collector task, read comments, find the latest `[STRATEGY]` comment (the 午盘更新, not the 盘前).

### Step 2: Verify price condition
```bash
env -u HT_APIKEY python3 <skill_dir>/a_share_paper_trading.py getQuote --stock-code 513120 --exchange SH
```
Returns: `currentPrice: 1.132, prevClose: 1.142` -> 1.132 <= 1.145 OK

### Step 3: Verify account
```bash
env -u HT_APIKEY python3 <skill_dir>/a_share_paper_trading.py getAccountBalance
```
Returns: `totalAssets: 1,161,147.84, availableBalance: 675,027.14`

### Step 4: Recalculate quantity (important!)
Strategist estimated: 51,100 shares @ 1.136 = 58,100元
Actual calculation: 1,161,147.84 x 5% = 58,057元 -> 58,057 / 1.132 = 51,286 -> **round down to 51,200** (100-share multiple)

**Why recalculate**: The strategist's estimated price (1.136) was based on the 11:40 snapshot. By 13:05, the actual price was 1.132. Using the strategist's estimated quantity would result in buying slightly less than 5% of current assets. Recalculating based on actual current price ensures the correct percentage allocation.

### Step 5: Submit order
```bash
env -u HT_APIKEY python3 <skill_dir>/a_share_paper_trading.py submitOrder \
  --direction buy --stock-code 513120 --exchange SH \
  --quantity 51200 --order-type limit --price 1.132
```

### Step 6: Write [TRADE] to Kanban
```bash
hermes kanban comment <task_id> "[TRADE] 交易执行报告 - 2026-07-08 13:06

买入 港股创新药ETF广发(513120 SH) 51,200股, 限价1.13, 预估金额57,958元, 订单号44842, 状态pending

策略来源: 午盘策略[STRATEGY]指令 - 加仓港股创新药5%, 价格<=1.145"
```

## Rules for Mid-Session New Position Entry

1. **Treat the latest [STRATEGY] as authoritative** -- even if it contradicts the morning strategy. The 午盘更新 supersedes the 盘前策略 for new instructions.
2. **Always re-verify price** -- the strategist's estimated price may be 1-2 hours old. Use `getQuote` for current price.
3. **Recalculate quantity** when the strategist's estimated price differs from actual price:
   - `targetAmount = totalAssets x targetPercentage`
   - `actualQuantity = floor(targetAmount / currentPrice / 100) x 100`
   - Do NOT blindly use the strategist's estimated quantity
4. **Check the position doesn't already exist** -- `getPositions` to confirm the ticker is not already held (prevents duplicate position buildup).
5. **Write [TRADE] with clear source attribution** -- mention "午盘策略[STRATEGY]指令" so the strategist can verify their instruction was followed.
6. **Standard price condition still applies** -- currentPrice <= targetUpper. No special relaxation for mid-session entries.

## Distinguishing Actionable Instructions from Conditional Considerations

**Critical pattern**: Strategists often use conditional/consideration language that is NOT an actionable buy instruction. The trader must distinguish:

| Language | Type | Trader Action |
|----------|------|---------------|
| "买入X，价格<=Y" | **Actionable** | Execute when price condition met |
| "卖出X" | **Actionable** | Execute immediately |
| "考虑加仓X" | **Consideration** | Do NOT execute -- strategist is thinking, not instructing |
| "关注X回调至Y以下可考虑" | **Conditional consideration** | Do NOT execute -- "可考虑" means strategist needs to decide later |
| "午后评估是否..." | **Future evaluation** | Do NOT execute -- wait for the next [STRATEGY] update |
| "若...则..." (hypothetical) | **Scenario planning** | Do NOT execute -- not a directive |

**Verified 2026-07-08**: Strategist's午盘评估 included:
```
午后关注：半导体方向午后能否守住涨幅
若午后市场持续强势，尾盘评估是否考虑小幅加仓（如159516回调至1.78以下可考虑）
```
The trader correctly identified this as **conditional consideration**, not a buy instruction. At 13:45, 159516 was at 1.782 (above 1.78), and more importantly, the strategist's language was "可考虑" (could consider) -- not "买入" (buy). Correct action: SILENT.

### Decision Framework

When reading a [STRATEGY] comment, scan for these keywords:

1. **Actionable keywords**: 买入, 卖出, 执行, 下单, 建仓, 加仓 (when paired with specific price/quantity)
2. **Non-actionable keywords**: 考虑, 关注, 评估, 观察, 等待, 若...则..., 可考虑, 是否, 建议(without explicit directive)

**Rule of thumb**: If the strategist wanted you to buy, they would say "买入". If they say "考虑买入" or "可考虑", they are thinking out loud -- do not act.

## Verification

After execution, confirm:
- `listPendingOrders` shows the new order (or it's already filled)
- `getPositions` shows the new ticker in holdings (once filled)
- The [TRADE] comment is visible on the info-collector task

## Subsequent Run: Already Executed (Prevent Double-Execution)

**Scenario**: A later cron run (e.g., 13:25) finds the same [STRATEGY] instruction that was already executed by a previous run (e.g., 13:05). The trader must NOT re-execute.

**Verified 2026-07-08**: The 13:25 trader run found the 513120 buy instruction in the latest [STRATEGY] but correctly detected it was already executed:

### Detection Flow

```
1. Read latest [STRATEGY] -> "买入 513120 SH, 价格<=1.145"
2. Check listPendingOrders -> empty (no pending orders for 513120)
3. Check listTradeHistory for today -> found filled trade: 51,200股 @ 1.13, order 44842
4. Check [TRADE] comments on info-collector -> found "[TRADE] 交易执行报告 - 2026-07-08 13:06"
5. No new [STRATEGY] comments -> go SILENT
```

### Additional Validation: 13:55 Run

**Verified 2026-07-08 13:55**: A later trader cron run at 13:55 also correctly detected the instruction was already executed:

```
1. listPendingOrders -> empty (order 44842 already filled)
2. Read [STRATEGY] -> same 午盘策略 with 513120 buy instruction
3. Check [TRADE] -> "[TRADE] 交易执行报告 - 2026-07-08 13:06" exists
4. No new [STRATEGY] after 13:06 -> SILENT
```

This validates that the detection chain works across multiple subsequent runs, not just the immediate next one. The key signal is: **no new [STRATEGY] after the [TRADE]**.

### Key Principles

1. **listPendingOrders is the first check** -- if it's empty for the target stockCode+direction, the order was either filled or cancelled. This is the fastest signal.
2. **listTradeHistory confirms filling** -- use `--stock-code` and `--exchange` filters to narrow down. If found, the instruction is fully executed.
3. **[TRADE] comments are the audit trail** -- check the info-collector task for [TRADE] comments with matching stockCode. If found, the instruction was already acted upon.
4. **Do NOT re-read [STRATEGY] and re-execute** -- even if the price condition is still met. The instruction was already processed. Re-executing would double the position.
5. **Only execute if ALL three are true**: (a) no pending order for this stockCode+direction, (b) no filled trade for this stockCode+direction today matching the instruction, (c) no [TRADE] comment referencing this instruction.

### When to Re-Execute

The only case where re-execution is correct: the strategist posts a **new** [STRATEGY] comment (with a later timestamp) that explicitly repeats or modifies the instruction. Always use the latest [STRATEGY] timestamp as the authoritative version.

### Why This Matters

Without this check, a trader cron running every 10 minutes could execute the same mid-session buy instruction 6+ times between 13:00 and 14:00, each time doubling the position. The `listPendingOrders -> listTradeHistory -> [TRADE] comment` chain is the safety gate.
