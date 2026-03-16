import json
import os
import urllib.request
from datetime import datetime,timedelta
from ai_parser import parse

TOPIC=os.environ.get("NTFY_TOPIC")

CHECK_WINDOW=60

def send(msg):

    url=f"https://ntfy.sh/{TOPIC}"

    req=urllib.request.Request(url,data=msg.encode())

    urllib.request.urlopen(req)

now=datetime.now()

with open("events.txt",encoding="utf-8") as f:

    for line in f:

        t=parse(line)

        if isinstance(t,datetime):

            if now>=t and now<=t+timedelta(minutes=CHECK_WINDOW):

                send("提醒："+line)
