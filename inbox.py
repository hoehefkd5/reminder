import os
import json
import requests
from datetime import datetime, timedelta
from ai_parser import parse

NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

INBOX_STATE = "inbox_state.json"
EVENTS = "events.txt"


def load_state():
    if not os.path.exists(INBOX_STATE):
        return []
    try:
        return json.load(open(INBOX_STATE, "r", encoding="utf-8"))
    except:
        return []


def save_state(data):
    try:
        json.dump(data[-100:], open(INBOX_STATE, "w", encoding="utf-8"))
    except Exception as e:
        print("保存 inbox_state 失败:", e)


def extract_time_and_event(text):
    """
    把 '20:46 叮我一下' 拆成：
    时间部分：20:46
    内容部分：叮我一下
    """
    parts = text.strip().split(" ", 1)

    if len(parts) == 1:
        return parts[0], ""

    return parts[0], parts[1]


def parse_text(text):
    text = text.strip()
    if not text:
        return None

    # 删除
    if text.startswith("del "):
        return {"action": "del", "content": text[4:].strip()}

    # add 前缀
    if text.startswith("add "):
        text = text[4:].strip()

    time_part, event = extract_time_and_event(text)

    t = parse(time_part)

    if not t:
        print("解析失败:", text)
        return None

    # 已过时间 → 自动+1天
    if t < datetime.now():
        t += timedelta(days=1)

    event_text = f"{t.year}-{t.month}-{t.day} {t.hour:02d}:{t.minute:02d} {event}"

    return {"action": "add", "content": event_text}


def main():
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
        try:
            events = open(EVENTS, encoding="utf-8").read().splitlines()
        except:
            events = []

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

    events = list(dict.fromkeys(events))

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
