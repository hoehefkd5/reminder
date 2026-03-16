import os
import urllib.request

TOPIC=os.environ.get("NTFY_TOPIC")

url=f"https://ntfy.sh/{TOPIC}/json?poll=1"

resp=urllib.request.urlopen(url)

for line in resp:

    msg=line.decode()

    if "add " in msg:

        task=msg.split("add ")[1].split('"')[0]

        with open("events.txt","a",encoding="utf-8") as f:
            f.write(task+"\n")

    if "done " in msg:

        task=msg.split("done ")[1].split('"')[0]

        with open("done.txt","a",encoding="utf-8") as f:
            f.write(task+"\n")
