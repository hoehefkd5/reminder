import os
import json
import base64
import urllib.request
from datetime import datetime, timedelta
import re

# ✅ 北京时间
def now_time():
    return datetime.utcnow() + timedelta(hours=8)

NTFY_SERVER = os.environ.get("NTFY_SERVER")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")

STATE_FILE = "state.json"
EVENTS = "events.txt"

REPEAT_INTERVAL = 5   # 分钟重复提醒
EXPIRE_HOURS = 24     # 24小时删除
TRIGGER_WINDOW = 10   # 🔥 关键：允许延迟10分钟内触发


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
    if not NTFY_SERVER or not NTFY_TOPIC:
        print("NTFY 未配置")
        return

    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"

    req = urllib.request.Request(
        url,
        data=msg.encode("utf-8"),
        method="POST"
    )

    title_b64 = base64.b64encode(title.encode("utf-8")).decode()
    req.add_header("Title", f"=?UTF-8?B?{title_b64}?=")

    try:
        urllib.request.urlopen(req, timeout=10)
        print("✅ 发送成功:", msg)
    except Exception as e:
        print("❌ 发送失败:", e)


def parse_time(line):
    now = now_time()

    # YYYY-MM-DD HH:MM
    m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2}) (.+)', line)
    if m:
        y, mo, d, h, mi, event = m.groups()
        return datetime(int(y), int(mo), int(d), int(h), int(mi)), event

    # 明天
    m = re.match(r'明天 (\d{1,2}):(\d{2}) (.+)', line)
    if m:
        h, mi, event = m.groups()
        base = now + timedelta(days=1)
        return datetime(base.year, base.month, base.day, int(h), int(mi)), event

    # 今天 HH:MM
    m = re.match(r'(\d{1,2}):(\d{2}) (.+)', line)
    if m:
        h, mi, event = m.groups()
        t = datetime(now.year, now.month, now.day, int(h), int(mi))

        # 已过 → 还是今天（🔥关键，不自动+1天）
        return t, event

    return None, line


def main():
    state = load()
    now = now_time()

    print("当前时间:", now)

    if not os.path.exists(EVENTS):
        open(EVENTS, "w").close()

    events = open(EVENTS, encoding="utf-8").read().splitlines()
    new_events = []

    for line in events:
        line = line.strip()
        if not line:
            continue

        t, event = parse_time(line)

        if not t:
            print("⚠️ 解析失败:", line)
            new_events.append(line)
            continue

        diff = (now - t).total_seconds() / 60

        print(f"🕒 {line} | 时间差: {diff:.2f} 分钟")

        key = line
        last = state.get(key)

        # 🔥 核心逻辑：允许延迟触发
        if -1 <= diff <= TRIGGER_WINDOW:
            if not last or (now - datetime.fromisoformat(last)).total_seconds() >= REPEAT_INTERVAL * 60:
                print("🚀 触发提醒:", line)
                send("提醒", event)
                state[key] = now.isoformat()

        # ⏰ 24小时后删除
        if diff <= EXPIRE_HOURS * 60:
            new_events.append(line)

    # 写回（不会乱删）
    tmp = EVENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(new_events))
    os.replace(tmp, EVENTS)

    save(state)
    print("✅ 完成")


if __name__ == "__main__":
    main()
