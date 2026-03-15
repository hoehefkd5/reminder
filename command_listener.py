import os
import urllib.request

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
EVENT_FILE = "events.txt"

url = f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1"

print("监听 ntfy 命令...")

resp = urllib.request.urlopen(url)

for line in resp:

    try:
        data = line.decode()

        if "add " in data:

            cmd=data.split("add ")[1].split('"')[0]

            print("收到任务:",cmd)

            with open(EVENT_FILE,"a",encoding="utf-8") as f:
                f.write(cmd+"\n")

    except:
        pass
