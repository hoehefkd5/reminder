import os
import json
import urllib.request
import urllib.parse
from datetime import datetime,timedelta,timezone

EVENT_FILE="events.txt"
STATE_FILE="state.json"
DONE_FILE="done.txt"

NTFY_SERVER=os.environ.get("NTFY_SERVER","https://ntfy.sh")
NTFY_TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=20

UTC8=timezone(timedelta(hours=8))

def now():
    return datetime.now(UTC8)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def save_json(path,data):
    with open(path,"w") as f:
        json.dump(data,f)

def load_done():
    if not os.path.exists(DONE_FILE):
        return []
    with open(DONE_FILE) as f:
        return [x.strip() for x in f]

def send(title,msg):

    print(title,msg)

    if not NTFY_TOPIC:
        return

    url=f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req=urllib.request.Request(
        url,
        data=msg.encode(),
        method="POST"
    )

    req.add_header("Title",title)

    urllib.request.urlopen(req)

def in_window(t):

    diff=now()-t

    return timedelta(minutes=0)<=diff<=timedelta(minutes=CHECK_WINDOW)

def sent_today(state,key):

    today=now().strftime("%Y-%m-%d")

    if key in state and state[key]==today:
        return True

    state[key]=today

    return False

def check_once(time_str,event,state):

    t=datetime.strptime(time_str,"%Y-%m-%d %H:%M").replace(tzinfo=UTC8)

    key="once_"+event

    if in_window(t) and not sent_today(state,key):

        send("事件提醒",event)

def check_daily(t,event,state):

    today=now().strftime("%Y-%m-%d")

    et=datetime.strptime(today+" "+t,"%Y-%m-%d %H:%M").replace(tzinfo=UTC8)

    key="daily_"+event

    if in_window(et) and not sent_today(state,key):

        send("每日提醒",event)

print("开始扫描")

state=load_json(STATE_FILE)
done=load_done()

with open(EVENT_FILE,encoding="utf-8") as f:

    for line in f:

        line=line.strip()

        if not line or line.startswith("#"):
            continue

        try:

            time_part,event,_=line.split(",")

        except:

            parts=line.split(",")

            time_part=parts[0]
            event=parts[1]

        if event in done:
            continue

        if time_part.startswith("daily"):

            t=time_part.split()[1]

            check_daily(t,event,state)

        elif len(time_part)==16:

            check_once(time_part,event,state)

save_json(STATE_FILE,state)

print("扫描结束")
