# Profile 管理指南

## 当前 Profile 列表（2026-07-01）

| Profile | 用途 | 模型 | 思考模式 |
|---------|------|------|---------|
| `default` | 主会话 | sensenova-6.7-flash-lite | high |
| `info-collector` | 信息员（看板任务） | arkcode/deepseek-v4-flash | high |
| `strategist` | 策略员（盘前看板 + 盘中 cron） | arkcode/deepseek-v4-flash | xhigh |
| `expert` | 专家（原"专家"profile） | — | — |

## 创建 Profile

```bash
# 从 default 克隆
hermes profile create <name> --clone --description "描述"

# 修改 profile 的 config.yaml 中的模型
# ~/.hermes/profiles/<name>/config.yaml
# 将 default: sensenova-6.7-flash-lite 改为目标模型
# 将 provider: custom 改为目标 provider
```

## Profile 重命名

`hermes profile rename` 不支持中文字符。如需重命名含中文的 profile，直接 mv 目录：

```bash
mv ~/.hermes/profiles/专家 ~/.hermes/profiles/expert
```

然后同步更新 cron jobs.json 中的 `--assignee` 和 cron job 的 `profile` 字段。

## 修改 Profile 后

必须从外部 shell 执行 `hermes gateway restart` 使新配置生效。Gateway 进程内无法执行此命令。

## 关联更新

修改 profile 后需要同步更新：
1. cron jobs.json 中的 `profile` 字段（如果 cron job 使用该 profile）
2. 建链 cron prompt 中的 `--assignee` 参数
3. 本文件中的 Profile 列表