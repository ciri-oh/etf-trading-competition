# 每日交易策略模板

## 收盘分析模板

```
📊 {{date}} 收盘分析

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【大盘表现】
• 上证指数：{{sh_index}} ({{sh_change}})
• 深证成指：{{sz_index}} ({{sz_change}})
• 创业板指：{{cy_index}} ({{cy_change}})
• 成交额：{{volume}}

【板块涨跌TOP5】
涨幅：
1. {{sector_1}} +{{change_1}}
2. {{sector_2}} +{{change_2}}
...

跌幅：
1. {{sector_d1}} {{change_d1}}
2. {{sector_d2}} {{change_d2}}
...

【主力资金流向】
净流入TOP3：
• {{flow_in_1}} +{{amount_1}}
• {{flow_in_2}} +{{amount_2}}
• {{flow_in_3}} +{{amount_3}}

净流出TOP3：
• {{flow_out_1}} {{amount_out_1}}
• {{flow_out_2}} {{amount_out_2}}
• {{flow_out_3}} {{amount_out_3}}

【持仓盈亏】（如有）
• 总资产：{{total_assets}}
• 持仓市值：{{position_value}}
• 当日盈亏：{{day_profit}} ({{day_profit_pct}})
• 总盈亏：{{total_profit}} ({{total_profit_pct}})

【明日关注】
• {{focus_1}}
• {{focus_2}}
• {{focus_3}}
```

---

## 交易策略模板

```
🎯 {{date}} 交易策略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【外盘影响】
美股收盘：
• 道琼斯：{{djia}} ({{djia_change}})
• 标普500：{{sp500}} ({{sp500_change}})
• 纳斯达克：{{nasdaq}} ({{nasdaq_change}})

关键事件：
• {{event_1}}
• {{event_2}}

富时A50期货：{{a50_futures}}
离岸人民币：{{usdcnh}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【今日策略】

📌 操作1：{{action_1_type}} {{etf_1_name}}
• 代码：{{etf_1_code}}
• 交易所：{{etf_1_exchange}}
• 仓位：{{position_1_pct}}%
• 目标价：{{target_price_1}}
• 止损价：{{stop_loss_1}}
• 逻辑：{{logic_1}}

📌 操作2：{{action_2_type}} {{etf_2_name}}
• 代码：{{etf_2_code}}
• 交易所：{{etf_2_exchange}}
• 仓位：{{position_2_pct}}%
• 目标价：{{target_price_2}}
• 止损价：{{stop_loss_2}}
• 逻辑：{{logic_2}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【风险提示】
• {{risk_1}}
• {{risk_2}}

⏳ 策略已就绪，盯盘员将自动执行
```

---

## 盘中监控模板

```
⏰ {{time}} 盘中监控

【关注标的实时行情】
| ETF | 现价 | 涨跌幅 | 距目标价 |
|-----|------|--------|----------|
| {{etf_1}} | {{price_1}} | {{change_1}} | {{gap_1}} |
| {{etf_2}} | {{price_2}} | {{change_2}} | {{gap_2}} |

【触发条件】
• {{trigger_1}}
• {{trigger_2}}

【建议操作】
• {{suggestion}}
```

---

## 成交确认模板

```
✅ 成交确认

【订单信息】
• 订单号：{{order_id}}
• 标的：{{etf_name}} ({{etf_code}})
• 方向：{{direction}}
• 价格：{{price}}
• 数量：{{quantity}}
• 金额：{{amount}}
• 状态：{{status}}

【当前持仓】
{{positions_table}}
```
