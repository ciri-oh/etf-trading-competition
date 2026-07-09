# ETF Trading Competition — Session Learnings

Captured from the 2026-06-16 09:00 cron run (trader job) and 2026-06-24 09:38 cron run.

## Bug 1 — Wrong exchange in example

`etf-trading-competition` SKILL.md listed `159516` with `--exchange SH`.
Correct: `159516` is SZ (shenzhen). Fix was applied to SKILL.md.

## Bug 2 — Market-not-open silent path

`getQuote` for 512760 / 516160 / 512660 / 512700 / 159516 returned
`change: 0.0` and `currentPrice == prevClose`. This means the market data
feed had not updated yet for the trading session. Any price-based trigger
evaluation under those conditions is meaningless.

Rule: when `change == 0.0` AND `currentPrice == prevClose`, emit [SILENT]
immediately and do not attempt to evaluate triggers or submit orders.

## Bug 3 — Stale buy target vs current price

Strategy target buy zone was 1.35–1.37 for 159516; current quote was 1.386.
The buy condition was already obsolete. Correct behavior is [SILENT]; do
not chase price because the target was missed.

## Bug 4 — Unauthorized sell by trader (2026-06-16 14:41)

Trader submitted sell orders for 新能源（516160, +6.51%）and 军工ETF（512660,
+4.08%）without any trigger in the decision table firing. Root cause: the trader
misread per-name P&L percentages as total-asset percentages, and conflated the
"skip tiny positions" rule with "I can decide when to sell".

Correct behavior:
- Sell only when a decision-table condition is satisfied.
- Compare `abs(profit) / totalAssets` against 3%/4%/5%/8%/10% thresholds, not
  `profitPct` directly.
- The "skip tiny position" exemption applies only when the morning strategy
  already labels a position for reduction; it does not authorize ad-hoc sells.

## Decision thresholds (trader cron prompt vs SKILL.md mismatch)

The cron prompt in this session used single-name P&L thresholds (5% cut / 8% clear
for loss; 8% partial / 15% clear for profit). The SKILL.md "五、风险控制" section
uses total-asset-amount thresholds (e.g., 3%/4% of total assets). These two
bases cannot be mixed. The cron prompt is what the automated trader actually
follows; SKILL.md should document the same basis or call out the divergence
explicitly.

## 2026-06-24 Session Learnings

### Kanban评论是读取策略的最可靠方式

交易员读取策略员指令有三种方式，按可靠性排序：
1. **直接读kanban评论**（最可靠）：`hermes kanban show t_b9ae036d --json 2>&1 | grep -A 20 '"comments"'`
2. **读磁盘cron输出文件**：`ls -lt /root/.hermes/cron/output/f6f2aac7e6e5/ | head -3`（策略员已改为 deliver=origin，此方法可能失效，优先用方法1）
3. **session_search**（不可靠）：常返回prompt模板而非实际策略

本次session中，kanban评论直接返回了完整的策略报告，包括操作计划表、目标价区间、止损价。

### 巡检员输出可能只是prompt模板

巡检员的cron输出文件（`/root/.hermes/cron/output/709c073a2b8f/2026-06-24_09-38-01.md`）末尾只有prompt模板，没有实际的巡检报告。这说明巡检员可能没有成功执行其职责。

**处理方式**：交易员不应依赖巡检员输出，应以策略员输出为准。

### 策略员"观望不动"时的正确行为

策略员明确说"今日观望不动"，交易员正确执行了[SILENT]，没有自行判断买卖。这是正确的行为。

### 账户数据与策略评论的差异

策略员评论提到"今日盈利+3.6%"，但API返回`dayProfit: -2591.70 (-0.63%)`。可能原因：
1. 策略员评论是基于更早的数据（开盘时市场大涨）
2. 盘中市场回落，导致当日盈亏转负

**教训**：交易员执行时应以API实时数据为准，不以策略评论中的历史数据为准。

### 巡检员输出可能只是prompt模板

巡检员的cron输出文件（`/root/.hermes/cron/output/709c073a2b8f/2026-06-24_09-38-01.md`）末尾只有prompt模板，没有实际的巡检报告。这说明巡检员可能没有成功执行其职责。

**处理方式**：交易员不应依赖巡检员输出，应以策略员输出为准。