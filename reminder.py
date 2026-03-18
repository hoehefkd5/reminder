import os
import json
import urllib.request
from datetime import datetime,timedelta
from ai_parser import parse

NTFY_SERVER=os.environ.get("NTFY_SERVER")
NTFY_TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=180

STATE_FILE="state.json"

def load():
    if not os.path.exists(STATE_FILE):
        return {}
    return json.load(open(STATE_FILE))

def save(data):
    json.dump(data,open(STATE_FILE,"w"))

def send(msg):

    url=f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req=urllib.request.Request(
        url,
        data=msg.encode("utf-8"),
        method="POST"
    )

    req.add_header("Title","提醒")

    urllib.request.urlopen(req)

state=load()

now=datetime.now()

with open("events.txt",encoding="utf-8") as f:

    for line in f:

        line=line.strip()

        if not line or line.startswith("#"):
            continue

        parts=line.split(",",1)

        if len(parts)==2:
            time_part,event=parts
        else:
            sp=line.split(" ",1)
            time_part=sp[0]
            event=sp[1] if len(sp)>1 else ""

        t=parse(time_part)

        print("事件:",line)
        print("解析:",t)

        if not isinstance(t,datetime):
            continue

        diff=abs((now-t).total_seconds())

        key=line

        if diff<=CHECK_WINDOW*60:

            if state.get(key)==now.strftime("%Y-%m-%d"):
                continue

            send(f"提醒：{event}")

            state[key]=now.strftime("%Y-%m-%d")

save(state)
