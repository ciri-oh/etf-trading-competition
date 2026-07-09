# 巡检报告数据准确性与信息来源规范（2026-06-30）

## 问题1：巡检报告数据不准确

**事件**：2026-06-30 巡检员报告半导体板块 +2.62%，实际 API 查询为 +3.46%（板块代码 991334）。

**根因**：巡检员未通过 `queryIndicator` 实际查询板块涨跌幅，而是凭印象或估算填写。

**铁律**：
- 巡检报告中的板块涨跌幅必须标注板块代码（如 991334）
- 必须通过 `queryIndicator` 实际查询验证，不能凭印象填写
- 报告中注明数据来源和查询时间
- 用户可随时要求核验数据，巡检员必须能提供查询命令和原始结果

**验证方法**：
```bash
# 查询半导体板块实际涨跌幅
env -u HT_APIKEY python3 /root/.hermes/skills/query-indicator/query_indicator.py queryIndicator --query "半导体板块今日涨跌幅"
# 返回：涨跌幅、最新价、昨收价、板块代码
```

## 问题2：信息员 kanban 评论写 "-"

**事件**：2026-06-30 信息员任务完成后，kanban 评论只写了 "-"，完整报告在 `latest_summary` 字段中。

**影响**：策略员读不到 [INFO] 评论，只能依赖 summary 字段。如果 summary 也缺失，策略员将无数据可用。

**修复**：信息员 cron prompt 必须明确要求将完整报告写入 kanban 评论（带 [INFO] 标签），不能只写 summary。

**验证方法**：信息员完成后检查：
```bash
hermes kanban show --json <info-collector-id>
# 检查 comments 数组是否包含完整报告内容
```

## 巡检报告格式要求

巡检报告必须包含：
1. 板块代码（如 991334）
2. 实际查询的涨跌幅
3. 数据来源（queryIndicator / getQuote）
4. 查询时间戳
5. 与策略员预期的偏差分析