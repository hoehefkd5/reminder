import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

EVENT_FILE = "events.txt"

NTFY_SERVER = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
BARK_KEY = os.environ.get("BARK_KEY")

CHECK_WINDOW = 15

WEEKMAP = {
"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6
}

def send_notification(title, content):

    if NTFY_TOPIC:
        try:
            url = NTFY_SERVER.rstrip("/")
            data = {"topic":NTFY_TOPIC,"title":title,"message":content}

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                method="POST"
            )

            req.add_header("Content-Type","application/json")

            urllib.request.urlopen(req)

            print("ntfy 推送成功")

        except Exception as e:
            print("ntfy 推送失败",e)

    elif BARK_KEY:
        try:
            url=f"https://api.day.app/{BARK_KEY}/{urllib.parse.quote(title)}/{urllib.parse.quote(content)}"
            urllib.request.urlopen(url)
            print("Bark 推送成功")
        except Exception as e:
            print("Bark 推送失败",e)


def in_window(event_time):

    now=datetime.now()

    diff=now-event_time

    return timedelta(minutes=0)<=diff<=timedelta(minutes=CHECK_WINDOW)


def check_daily(t,event):

    today=datetime.now().strftime("%Y-%m-%d")

    event_time=datetime.strptime(today+" "+t,"%Y-%m-%d %H:%M")

    if in_window(event_time):
        send_notification("每日提醒",event)


def check_weekly(day,t,event):

    today=datetime.now()

    if today.weekday()==WEEKMAP[day]:

        event_time=datetime.strptime(
            today.strftime("%Y-%m-%d")+" "+t,
            "%Y-%m-%d %H:%M"
        )

        if in_window(event_time):
            send_notification("每周提醒",event)


def check_monthly(d,t,event):

    today=datetime.now()

    if today.day==int(d):

        event_time=datetime.strptime(
            today.strftime("%Y-%m-%d")+" "+t,
            "%Y-%m-%d %H:%M"
        )

        if in_window(event_time):
            send_notification("每月提醒",event)


print("开始检查任务")

if not os.path.exists(EVENT_FILE):
    print("events.txt 不存在")
    exit()

today=datetime.now().strftime("%Y-%m-%d")

with open(EVENT_FILE,"r",encoding="utf-8") as f:

    for line in f:

        line=line.strip()

        if not line or line.startswith("#"):
            continue

        try:

            time_part,event=line.split(",",1)

            event=event.strip()

            if "|" in time_part:

                base,advance=time_part.split("|")

                advance=int(advance)

                event_time=datetime.strptime(base,"%Y-%m-%d %H:%M")

                event_time-=timedelta(minutes=advance)

                if in_window(event_time):
                    send_notification("提前提醒",event)

            elif time_part.startswith("daily"):

                t=time_part.split()[1]

                check_daily(t,event)

            elif time_part.startswith("weekly"):

                _,day,t=time_part.split()

                check_weekly(day,t,event)

            elif time_part.startswith("monthly"):

                _,d,t=time_part.split()

                check_monthly(d,t,event)

            elif len(time_part)==16:

                event_time=datetime.strptime(time_part,"%Y-%m-%d %H:%M")

                if in_window(event_time):
                    send_notification("事件提醒",event)

            elif len(time_part)==10:

                if time_part==today:
                    send_notification("今日待办",event)

        except Exception as e:

            print("解析失败",line,e)

print("任务检查完成")
