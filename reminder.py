import os
import time
import json
import base64
import urllib.request
from datetime import datetime, timedelta

# 设置时区
os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

NTFY_SERVER = os.environ.get("NTFY_SERVER")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

STATE_FILE = "state.json"
EVENTS = "events.txt"

REPEAT_INTERVAL = 5  # 分钟
EXPIRE_HOURS = 24    # 小时


def load():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        return json.load(open(STATE_FILE, "r", encoding="utf-8"))
    except:
        return {}


def save(data):
    try:
        json.dump(data, open(STATE_FILE, "w", encoding="utf-8"))
    except Exception as e:
        print("保存 state.json 失败:", e)


def send(title, msg):
    if not NTFY_SERVER or not NTFY_TOPIC:
        print("NTFY_SERVER 或 NTFY_TOPIC 未设置")
        return

    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req = urllib.request.Request(
        url,
        data=msg.encode("utf-8"),
        method="POST"
    )

    title_b64 = base64.b64encode(title.encode("utf-8")).decode()
    req.add_header("Title", f"=?UTF-8?B?{title_b64}?=")
    req.add_header("Content-Type", "text/plain; charset=utf-8")

    try:
        urllib.request.urlopen(req, timeout=10)
        print("发送成功:", title, msg)
    except Exception as e:
        print("发送失败:", e)


def main():
    state = load()
    now = datetime.now()

    events = []
    if os.path.exists(EVENTS):
        try:
            events = open(EVENTS, encoding="utf-8").read().splitlines()
        except:
            events = []

    new_events = []

    for line in events:
        try:
            parts = line.split(" ", 2)
            t = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M")
            event = parts[2] if len(parts) > 2 else ""
        except:
            continue

        diff = (now - t).total_seconds() / 60

        # 保留未来事件或未超过24小时的事件
        if diff <= EXPIRE_HOURS * 60:
            new_events.append(line)

        # 到点提醒
        if diff >= 0:
            key = line
            last = state.get(key)
            if not last or (now - datetime.fromisoformat(last)).total_seconds() >= REPEAT_INTERVAL * 60:
                send("提醒", event)
                state[key] = now.isoformat()

    tmp = EVENTS + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(new_events))
        os.replace(tmp, EVENTS)
    except Exception as e:
        print("写入 events.txt 失败:", e)

    save(state)
    print("完成")


if __name__ == "__main__":
    main()
