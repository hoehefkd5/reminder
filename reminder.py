import os
import time
import json
import base64
import urllib.request
from datetime import datetime
from ai_parser import parse  # 使用你写的 ai_parser

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
    json.dump(data, open(STATE_FILE, "w", encoding="utf-8"))


def send(title, msg):
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
        print("发送成功:", msg)
    except Exception as e:
        print("发送失败:", e)


def split_event(line):
    parts = line.split(" ", 2)
    if len(parts) < 2:
        return None, None

    time_part = parts[0] + " " + parts[1]
    event = parts[2] if len(parts) > 2 else ""

    return time_part, event


def main():
    state = load()
    now = datetime.now()

    events = []
    if os.path.exists(EVENTS):
        events = open(EVENTS, encoding="utf-8").read().splitlines()

    new_events = []

    for line in events:

        # 提取时间和事件
        time_part, event = split_event(line)

        if not time_part:
            # 解析失败，保留原事件
            new_events.append(line)
            continue

        t = parse(time_part)  # 只解析时间部分

        if not t:
            print("解析失败(保留):", line)
            new_events.append(line)  # 解析失败时保留事件
            continue

        diff = (now - t).total_seconds() / 60

        # 默认保留所有事件
        new_events.append(line)

        # 超过 24 小时才删除
        if diff > EXPIRE_HOURS * 60:
            new_events.remove(line)
            continue

        # 到点提醒
        if diff >= 0:
            key = line
            last = state.get(key)

            if not last or (now - datetime.fromisoformat(last)).total_seconds() >= REPEAT_INTERVAL * 60:
                send("提醒", event)
                state[key] = now.isoformat()

    tmp = EVENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(new_events))
    os.replace(tmp, EVENTS)

    save(state)

    print("完成")


if __name__ == "__main__":
    main()
