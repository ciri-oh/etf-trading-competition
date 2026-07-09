# Kanban 数据库损坏恢复记录

## 事件概要

- **日期：** 2026-06-30
- **发现时间：** 09:25（用户查看交易状态时发现看板无今日任务）
- **根因：** `/root/.hermes/kanban.db` 文件损坏
- **影响：** 整个看板流转静默失败——建链 cron 显示 ok，但信息员/策略员未触发

## 诊断过程

### 1. 看板任务检查
```bash
hermes kanban list --json
```
结果：只有 6月29日（昨天）的 3 个任务，无今日任务。

### 2. Cron Job 状态检查
```bash
hermes cron list --json
```
结果：建链 cron `ee714aa5d69b` 显示 `last_status: ok`，`last_run_at: 2026-06-30T08:45:33`，但看板无新任务。

### 3. 建链 cron 输出检查
```bash
ls -la ~/.hermes/cron/output/ee714aa5d69b/
```
结果：有输出文件 `2026-06-30_08-45-32.md`，但内容被截断（最后只剩 `[\n`），说明执行过程异常。

### 4. Gateway 日志检查（关键步骤）
```bash
journalctl -u hermes-gateway --since "09:25" --no-pager
```
发现关键错误：
```
ERROR gateway.run: kanban dispatcher: board default database /root/.hermes/kanban.db is not a valid SQLite database; pausing dispatch for this board until the file changes, the gateway restarts, or the quarantine timer expires.
```

### 5. 数据库完整性验证
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/root/.hermes/kanban.db')
cur = conn.execute('SELECT count(*) FROM tasks')
print('Tasks:', cur.fetchone()[0])
conn.close()
"
```
结果：`ERROR: file is not a database`

## 修复步骤

1. 备份损坏文件：`mv /root/.hermes/kanban.db /root/.hermes/kanban.db.corrupted.202606300925`
2. 重建数据库：`hermes kanban init`
3. 软链接到新路径：`ln -sf /root/.hermes/kanban/boards/etf-trading/kanban.db /root/.hermes/kanban.db`
4. 手动补建看板链：
   - `morning-analysis` → `t_324e25c8`（done）
   - `info-collector` → `t_574e1dc0`（running）
   - `strategist-morning` → `t_fab6a036`（todo）

## 关键教训

1. **Gateway 日志是诊断看板问题的第一入口**：`journalctl -u hermes-gateway | grep -i "kanban\|dispatcher\|database"` 能直接定位问题
2. **建链 cron 显示 ok 不代表看板流转成功**：cron 执行成功但 Gateway dispatcher 被暂停时，任务不会创建
3. **数据库损坏是静默失败**：不报错、不通知用户，只有人工检查看板才能发现
4. **Gateway 进程内无法重启自身**：`systemctl restart hermes-gateway` 和 `hermes gateway restart` 都会报 Blocked，需从外部 shell 执行

## 预防措施

- 定期检查 Gateway 日志中的 kanban dispatcher 错误
- 考虑添加 cron job 每日检查 kanban.db 完整性
- 数据库损坏后重建会丢失旧任务数据，建议定期 `hermes kanban archive --rm` + `gc` 清理旧数据