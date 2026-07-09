#!/usr/bin/env python3
"""
个股资金流向查询工具（带重试）
用法:
    python3 fund_flow.py 688525        # 佰维存储（沪市）
    python3 fund_flow.py 688041        # 海光信息（沪市）
    python3 fund_flow.py 000063 sz     # 中兴通讯（深市）
"""

import subprocess, json, sys, os, time

stock = sys.argv[1] if len(sys.argv) > 1 else "688525"
market = sys.argv[2] if len(sys.argv) > 2 else "sh"
market_map = {"sh": 1, "sz": 0, "bj": 0}

url = (
    f"https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    f"?lmt=10&klt=101&secid={market_map[market]}.{stock}"
    f"&fields1=f1,f2,f3,f7"
    f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
)

cmd = ["curl", "-s", url, "-H", "User-Agent: Mozilla/5.0", "-H", "Referer: https://data.eastmoney.com/"]
clean_env = {k: v for k, v in os.environ.items() if k != "SSL_CERT_FILE"}

# 重试3次，间隔递增
for attempt in range(3):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=clean_env)
    if result.stdout and result.returncode == 0:
        break
    print(f"⏳ 第{attempt+1}次失败，等待{10*(attempt+1)}秒重试...")
    time.sleep(10 * (attempt + 1))
else:
    print("❌ 请求失败，API频率限制，过一会儿再试")
    sys.exit(1)

data = json.loads(result.stdout)
lines = data["data"]["klines"]

def fmt(v):
    if abs(v) >= 1e8: return f"{v/1e8:.2f}亿"
    elif abs(v) >= 1e4: return f"{v/1e4:.2f}万"
    return str(int(v))

print(f"\n{'='*90}")
print(f"  {stock}  近10日资金流向")
print(f"{'='*90}")
print(f"{'日期':<12} {'收盘价':>8} {'涨跌幅':>7} {'主力净流入':>16} {'占比':>6} {'超大单':>16} {'大单':>16}")
print(f"{'-'*12} {'-'*8} {'-'*7} {'-'*16} {'-'*6} {'-'*16} {'-'*16}")

total_main = 0
for line in lines:
    p = line.split(",")
    date, close, chg = p[0], round(float(p[11]), 2), round(float(p[12]), 2)
    main, main_pct = float(p[1]), round(float(p[6]), 2)
    super_big, big = float(p[5]), float(p[4])
    total_main += main
    print(f"{date:<12} {close:>8.2f} {chg:>6.2f}% {fmt(main):>16} {main_pct:>5.2f}% {fmt(super_big):>16} {fmt(big):>16}")

inflow = sum(1 for l in lines if float(l.split(",")[1]) > 0)
outflow = sum(1 for l in lines if float(l.split(",")[1]) < 0)
print(f"{'='*90}")
print(f"  近10日主力累计净流入: {fmt(total_main)}  |  净流入{inflow}天  净流出{outflow}天")
print(f"{'='*90}")
