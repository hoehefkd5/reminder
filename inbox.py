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
    json.dump(data, open(INBOX_STATE, "w"))


def parse_text(text):
    text = text.strip()

    # 支持 add 前缀
    if text.startswith("add "):
        text = text[4:]

    # 支持 del 指令
    if text.startswith("del "):
        return {"action": "del", "content": text[4:].strip()}

    # 明天
    if text.startswith("明天"):
        rest = text.replace("明天", "").strip()
        parts = rest.split(" ", 1)
        time_part = parts[0]
        event = parts[1] if len(parts) > 1 else "提醒"
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y-%m-%d")
        return {"action": "add", "content": f"{date} {time_part} {event}"}

    # 今天/当日 HH:MM
    m = re.match(r"(\d{1,2}:\d{2})(.*)", text)
    if m:
        time_part = m.group(1)
        event = m.group(2).strip() or "提醒"
        today = datetime.now().strftime("%Y-%m-%d")
        return {"action": "add", "content": f"{today} {time_part} {event}"}

    # 其他无法识别的格式直接忽略
    return None


def main():
    url = f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1"
    data = requests.get(url).json()

    seen = load_state()
    new_seen = seen[:]

    events = []
    if os.path.exists(EVENTS):
        events = open(EVENTS, encoding="utf-8").read().splitlines()

    added = []
    removed = []

    for msg in data:
        msg_id = msg.get("id")
        text = msg.get("message", "")

        if msg_id in seen:
            continue

        parsed = parse_text(text)

        if parsed is None:
            new_seen.append(msg_id)
            continue

        action = parsed.get("action")
        content = parsed.get("content")

        if action == "add" and content not in events:
            events.append(content)
            added.append(content)
        elif action == "del":
            before = len(events)
            events = [e for e in events if content not in e]
            removed.append(f"{content} ({before-len(events)} removed)")

        new_seen.append(msg_id)

    if added or removed:
        with open(EVENTS, "w", encoding="utf-8") as f:
            f.write("\n".join(events))

    if added:
        print("新增任务:", added)
    if removed:
        print("删除任务:", removed)

    save_state(new_seen)


if __name__ == "__main__":
    main()
