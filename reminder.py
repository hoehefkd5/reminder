import json
import os
import urllib.request
from datetime import datetime,timedelta
from ai_parser import parse

NTFY_SERVER=os.environ.get("NTFY_SERVER")
NTFY_TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=180

def send(msg):

    url=f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req=urllib.request.Request(url,data=msg.encode())

    urllib.request.urlopen(req)

#send("GitHub提醒系统测试")

now = datetime.now()

with open("events.txt", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        time_part = line.split(",")[0]

        t = parse(time_part)

        print("当前时间:", now)
        print("事件:", line)
        print("解析时间:", t)

        if isinstance(t, datetime):

            diff = abs((now - t).total_seconds())

            print("时间差(秒):", diff)

            if diff <= CHECK_WINDOW * 60:

                print("触发提醒:", line)

                send("提醒：" + line)
