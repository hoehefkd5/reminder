import os
import json
import urllib.request
import urllib.parse
from datetime import datetime,timedelta

EVENT_FILE="events.txt"
STATE_FILE="state.json"
DONE_FILE="done.txt"

NTFY_SERVER=os.environ.get("NTFY_SERVER","https://ntfy.sh")
NTFY_TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=20

WEEKMAP={
"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6
}

def load_json(file):

    if not os.path.exists(file):
        return {}

    with open(file,"r") as f:
        return json.load(f)

def save_json(file,data):

    with open(file,"w") as f:
        json.dump(data,f)

def send(title,msg):

    if not NTFY_TOPIC:
        return

    url=NTFY_SERVER.rstrip("/")

    data={
    "topic":NTFY_TOPIC,
    "title":title,
    "message":msg
    }

    req=urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        method="POST"
    )

    req.add_header("Content-Type","application/json")

    urllib.request.urlopen(req)

def in_window(t):

    now=datetime.now()

    return timedelta(0)<=now-t<=timedelta(minutes=CHECK_WINDOW)

state=load_json(STATE_FILE)

done=set()

if os.path.exists(DONE_FILE):

    with open(DONE_FILE) as f:

        for l in f:
            done.add(l.strip())

today=datetime.now().strftime("%Y-%m-%d")

with open(EVENT_FILE,encoding="utf-8") as f:

    for line in f:

        line=line.strip()

        if not line or line.startswith("#"):
            continue

        try:

            time_part,event=line.split(",",1)

            key=line

            if event in done:
                continue

            if key in state and state[key]==today:
                continue

            if "|" in time_part:

                base,adv=time_part.split("|")

                adv=int(adv)

                t=datetime.strptime(base,"%Y-%m-%d %H:%M")

                t-=timedelta(minutes=adv)

                if in_window(t):

                    send("提前提醒",event)

                    state[key]=today

            elif time_part.startswith("daily"):

                t=time_part.split()[1]

                t=datetime.strptime(today+" "+t,"%Y-%m-%d %H:%M")

                if in_window(t):

                    send("每日提醒",event)

                    state[key]=today

            elif time_part.startswith("weekly"):

                _,d,t=time_part.split()

                if datetime.now().weekday()==WEEKMAP[d]:

                    t=datetime.strptime(today+" "+t,"%Y-%m-%d %H:%M")

                    if in_window(t):

                        send("每周提醒",event)

                        state[key]=today

            elif time_part.startswith("monthly"):

                _,d,t=time_part.split()

                if datetime.now().day==int(d):

                    t=datetime.strptime(today+" "+t,"%Y-%m-%d %H:%M")

                    if in_window(t):

                        send("每月提醒",event)

                        state[key]=today

            elif len(time_part)==16:

                t=datetime.strptime(time_part,"%Y-%m-%d %H:%M")

                if in_window(t):

                    send("事件提醒",event)

                    state[key]=today

            elif len(time_part)==10:

                if time_part==today:

                    send("今日任务",event)

                    state[key]=today

        except Exception as e:

            print("解析错误",line,e)

save_json(STATE_FILE,state)

print("任务检查完成")
