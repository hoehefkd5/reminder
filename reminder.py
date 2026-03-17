import json
import os
import urllib.request
from datetime import datetime,timedelta
from ai_parser import parse

NTFY_SERVER=os.environ.get("NTFY_SERVER")
NTFY_TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=60

def send(msg):

    url=f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req=urllib.request.Request(url,data=msg.encode())

    urllib.request.urlopen(req)

#send("GitHub提醒系统测试")

now=datetime.now()

with open("events.txt",encoding="utf-8") as f:

    for line in f:

        line=line.strip()

        if not line:
            continue

        t=parse(line)

        if isinstance(t,datetime):

            if now>=t and now<=t+timedelta(minutes=CHECK_WINDOW):

                send("提醒："+line)
