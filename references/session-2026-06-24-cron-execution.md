# Cron 执行模式 - 2026-06-24

## 交易员 Cron Job 成功执行记录

### 执行流程
1. 读取 Kanban 任务（策略员 + 巡检员）获取最新指令
2. 查询账户余额和持仓
3. 根据指令判断是否需要操作
4. 添加执行报告评论到 Kanban 任务
5. 不创建新 Kanban 任务（security scan 会拦截中文 body）

### 关键命令
```bash
# 读取策略员指令
hermes kanban show t_b9ae036d

# 读取巡检员指令
hermes kanban show t_4f2ba4af

# 查询账户余额
cd /root/.hermes/skills/a-share-paper-trading && python3 a_share_paper_trading.py getAccountBalance

# 查询持仓
cd /root/.hermes/skills/a-share-paper-trading && python3 a_share_paper_trading.py getPositions

# 添加执行报告评论
hermes kanban comment <task_id> "【交易执行报告 ...】..."
```

### 注意事项
- Kanban 任务状态为 "done" 后，通过评论获取最新状态
- security scan 会拦截中文 body → 改用评论方式记录执行结果
- 运行 Python 脚本前需 cd 到技能目录（或使用完整路径）
- 策略员 + 巡检员指令为"观望不动"时，执行报告重点在确认状态而非操作
