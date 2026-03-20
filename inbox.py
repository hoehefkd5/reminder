import os
import json
import requests
from datetime import datetime, timedelta
import re

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

INBOX_STATE = "inbox_state.json"
EVENTS = "events.txt"


def load_state():
    if not os.path.exists(INBOX_STATE):
        return []
    return json.load(open(INBOX_STATE))


def save_state(data):
    json.dump(data[-100:], open(INBOX_STATE, "w"))  # 保留最近100条消息


def parse_text(text):
    text = text.strip()

    # 支持删除任务
    if text.startswith("del "):
        return {"action": "del", "content": text[4:].strip()}

    # 支持 add 前缀
    if text.startswith("add "):
        text = text[4:]

    # 明天
    if text.startswith("明天"):
        rest = text.replace("明天", "").strip()
        parts = rest.split(" ", 1)
        time_part = parts[0]
        event = parts[1] if len(parts) > 1 else "提醒"

        t = datetime.now() + timedelta(days=1)
        return {"action": "add", "content": f"{t.strftime('%Y-%m-%d')} {time_part} {event}"}

    # HH:MM 格式
    m = re.match(r"(\d{1,2}:\d{2})(.*)", text)
    if m:
        time_part = m.group(1)
        event = m.group(2).strip() or "提醒"

        today = datetime.now()
        t = datetime.strptime(today.strftime("%Y-%m-%d") + " " + time_part, "%Y-%m-%d %H:%M")

        # 如果时间已过 → 自动改为明天
        if t < today:
            t += timedelta(days=1)

        return {"action": "add", "content": f"{t.strftime('%Y-%m-%d %H:%M')} {event}"}

    return None


def main():
    # 🔹 获取 ntfy 消息，增加超时和异常捕获，防止 GitHub Actions 卡住
    url = f"https://ntfy.sh/{NTFY_TOPIC}/json"
    try:
        resp = requests.get(url, timeout=10)
        data = []
        for line in resp.text.strip().split("\n"):
            if line.strip():
                try:
                    data.append(json.loads(line))
                except:
                    continue
    except Exception as e:
        print("获取 ntfy 消息失败:", e)
        data = []

    seen = load_state()
    new_seen = seen[:]

    events = []
    if os.path.exists(EVENTS):
        events = open(EVENTS, encoding="utf-8").read().splitlines()

    added, removed = [], []

    for msg in data:
        msg_id = msg.get("id")
        text = msg.get("message", "")

        if msg_id in seen or not text:
            continue

        parsed = parse_text(text)

        if parsed:
            if parsed["action"] == "add":
                if parsed["content"] not in events:
                    events.append(parsed["content"])
                    added.append(parsed["content"])
            elif parsed["action"] == "del":
                before = len(events)
                events = [e for e in events if parsed["content"] not in e]
                removed.append(f"{parsed['content']} ({before-len(events)} removed)")

        new_seen.append(msg_id)

    # 去重
    events = list(dict.fromkeys(events))

    # 安全写入 events.txt
    tmp = EVENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(events))
    os.replace(tmp, EVENTS)

    if added:
        print("新增任务:", added)
    if removed:
        print("删除任务:", removed)

    save_state(new_seen)


if __name__ == "__main__":
    main()
