import os
import json
import requests
from datetime import datetime, timedelta

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

    # 明天
    if text.startswith("明天"):
        rest = text.replace("明天", "").strip()

        parts = rest.split(" ", 1)
        time_part = parts[0]
        event = parts[1] if len(parts) > 1 else ""

        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime("%Y-%m-%d")

        return f"{date} {time_part} {event}"

    # 今天（默认）
    if ":" in text:
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{today} {text}"

    return None


def main():
    url = f"https://ntfy.sh/{NTFY_TOPIC}/json?poll=1"

    data = requests.get(url).json()

    seen = load_state()
    new_seen = seen[:]

    events = []
    if os.path.exists(EVENTS):
        events = open(EVENTS).read().splitlines()

    added = []

    for msg in data:
        msg_id = msg.get("id")
        text = msg.get("message", "")

        if msg_id in seen:
            continue

        parsed = parse_text(text)

        if parsed and parsed not in events:
            events.append(parsed)
            added.append(parsed)

        new_seen.append(msg_id)

    if added:
        with open(EVENTS, "w", encoding="utf-8") as f:
            f.write("\n".join(events))

        print("新增任务:", added)

    save_state(new_seen)


if __name__ == "__main__":
    main()
