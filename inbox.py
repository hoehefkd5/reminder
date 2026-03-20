import os
import json
import requests
from datetime import datetime, timedelta
from ai_parser import parse  # 使用你现有的解析器

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


def parse_text(text):
    text = text.strip()
    if not text:
        return None

    # 删除任务
    if text.startswith("del "):
        return {"action": "del", "content": text[4:].strip()}

    # 添加任务前缀
    if text.startswith("add "):
        text = text[4:].strip()

    # 使用 ai_parser 解析时间
    t = parse(text)
    if t:
        # 如果时间已经过去 → 默认明天
        if t < datetime.now():
            t += timedelta(days=1)
        # 格式化为标准事件文本
        event_text = f"{t.year}-{t.month}-{t.day} {t.hour:02d}:{t.minute:02d} {text}"
        return {"action": "add", "content": event_text}

    return None


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
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(events))
        os.replace(tmp, EVENTS)
    except Exception as e:
        print("写入 events.txt 失败:", e)

    if added:
        print("新增任务:", added)
    if removed:
        print("删除任务:", removed)

    save_state(new_seen)


if __name__ == "__main__":
    main()
