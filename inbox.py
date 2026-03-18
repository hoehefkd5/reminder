import os

INBOX="inbox.txt"
EVENTS="events.txt"
DONE="done.txt"

if not os.path.exists(INBOX):
    exit()

lines=open(INBOX).read().splitlines()

events=open(EVENTS).read().splitlines()

for cmd in lines:

    cmd=cmd.strip()

    if cmd.startswith("add "):
        events.append(cmd[4:])

    elif cmd.startswith("done "):
        with open(DONE,"a") as f:
            f.write(cmd[5:]+"\n")

    elif cmd.startswith("del "):
        events=[e for e in events if cmd[4:] not in e]

open(EVENTS,"w").write("\n".join(events))
open(INBOX,"w").write("")
