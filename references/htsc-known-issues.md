# HTSC Skills 已知问题与修复

## 1. API Key配置问题

### 症状
- 调用skill返回`{"code": "1001", "msg": "API Key无效或已删除"}`
- select-stock返回`{"code": -2, "message": "未知错误", "category": "business"}`

### 原因
- config文件内容被截断（heredoc写入时EOF格式问题）
- 环境变量未正确加载到Python进程
- config文件权限不正确

### 修复步骤
```bash
# 1. 检查config文件内容和大小
cat /root/.htsc-skills/config
wc -c /root/.htsc-skills/config  # 应该是55字节左右

# 2. 用Python写入（最可靠）
python3 -c "
key = 'your-full-api-key-here'
with open('/root/.htsc-skills/config', 'w') as f:
    f.write('HT_APIKEY=' + key + '\n')
"

# 3. 验证Python能正确读取
python3 -c "
from pathlib import Path
config_path = Path.home() / '.htsc-skills' / 'config'
content = config_path.read_text()
key = content.split('=')[1].strip()
print(f'Key length: {len(key)}')  # 应该是44
"
```

## 2. select-stock查询部分ETF类型失败

### 症状
- 查询货币ETF、债券ETF、跨境ETF返回业务错误
- 查询行业ETF、主题ETF正常

### 解决方案
- 优先使用行业/主题/宽基ETF筛选
- 货币ETF、债券ETF改用web搜索获取信息

## 3. query-indicator对指数查询不稳定

### 症状
- 查询"上证指数"、"A股大盘"返回验证错误

### 解决方案
- 改用`financial-analysis`的`marketInsight`工具

## 4. a-share-paper-trading交易功能需比赛开通

### 症状
- `getQuote`、`submitOrder`等返回API Key无效

### 解决方案
- 比赛开始前只使用数据查询类skill
- 比赛开始后再次测试交易功能

## 5. 环境变量加载问题（重要！）

### 症状
- `export HT_APIKEY=*** 直接写死key后，Python读取到空值或长度只有3
- skill返回`{"code": -2, "message": "未知错误"}`

### ✅ 正确方式
```bash
# 从config文件动态读取key，inline传递
HT_APIKEY=*** HT_APIKEY ~/.htsc-skills/config | cut -d= -f2) python3 /path/to/script.py ...
```

### ❌ 错误方式
```bash
# 直接写死key → 不可靠
export HT_APIKEY=*** python3 xxx.py
```

### 验证
```bash
wc -c /root/.htsc-skills/config  # 应该55字节
cat /root/.htsc-skills/config    # 确认key完整
```
