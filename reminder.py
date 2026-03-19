import os
import json
import urllib.request
from datetime import datetime, timedelta
from ai_parser import parse, parse_advance

NTFY_SERVER = os.environ.get("NTFY_SERVER")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

CHECK_WINDOW = 180  # 分钟

STATE_FILE = "state.json"


def load():
    if not os.path.exists(STATE_FILE):
        return {}
    return json.load(open(STATE_FILE))


def save(data):
    json.dump(data, open(STATE_FILE, "w"))


def send(title, msg):
    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req = urllib.request.Request(
        url,
        data=msg.encode("utf-8"),
        method="POST"
    )

    req.add_header("Title", title)

    urllib.request.urlopen(req)

send("强制测试")

state = load()
now = datetime.now()

print("当前时间:", now)

with open("events.txt", encoding="utf-8") as f:

    for line in f:

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        # 解析格式
        parts = line.split(",", 1)

        if len(parts) == 2:
            time_part, event = parts
        else:
            sp = line.split(" ", 1)
            time_part = sp[0]
            event = sp[1] if len(sp) > 1 else ""

        # 🔥 拆提前时间
        base_time, advance = parse_advance(time_part)

        t = parse(base_time)

        print("事件:", line)
        print("时间:", t)
        print("提前(分钟):", advance)

        if not isinstance(t, datetime):
            continue

        key_base = line
        today = now.strftime("%Y-%m-%d")

        # =========================
        # 🟡 提前提醒
        # =========================
        if advance > 0:

            advance_time = t - timedelta(minutes=advance)

            diff = (now - advance_time).total_seconds()

            print("提前diff:", diff)

            if -CHECK_WINDOW * 60 <= diff2 <= CHECK_WINDOW * 60:

                key = key_base + "_advance"

                if state.get(key) != today:
                    send("提前提醒", event)
                    state[key] = today

        # =========================
        # 🔴 准时提醒
        # =========================
        diff2 = (now - t).total_seconds()

        print("准时diff:", diff2)

        if 0 <= diff2 <= CHECK_WINDOW * 60:

            key = key_base + "_ontime"

            if state.get(key) != today:
                send("准时提醒", event)
                state[key] = today

save(state)

print("执行完成")
