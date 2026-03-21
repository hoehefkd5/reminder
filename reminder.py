import os
import time
import json
import base64
import urllib.request
from datetime import datetime, timedelta
from ai_parser import parse  # 使用你写的 ai_parser

# 自动适配本地时区，默认 +8小时（北京时间）
from datetime import timezone

os.environ['TZ'] = 'Asia/Shanghai'  # 不再硬编码时区，适配不同地区

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

    try:
        urllib.request.urlopen(req, timeout=10)
        print("发送成功:", msg)
    except Exception as e:
        print("发送失败:", e)


def split_event(line):
    """
    提取时间和事件内容
    示例:
    - "10:25 叮我一下"
    - "明天 10:25 吃饭"
    """
    parts = line.split(" ", 2)

    if len(parts) < 2:
        return None, None

    time_part = parts[0] + " " + parts[1]  # 时间部分
    event = parts[2] if len(parts) > 2 else ""  # 事件内容部分

    return time_part, event


def parse_time(line):
    """
    时间解析支持格式：
    - 10:30 叮我一下
    - 明天 10:30 吃饭
    - 2027-5-8 12:00 生日
    """
    now = datetime.now()

    # 解析“YYYY-MM-DD HH:MM”
    m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2})', line)
    if m:
        y, mo, d, h, mi = map(int, m.groups())
        return datetime(y, mo, d, h, mi), line.split(" ", 2)[-1]

    # 解析“明天 HH:MM”
    m = re.match(r'明天 (\d{1,2}):(\d{2})', line)
    if m:
        h, mi = map(int, m.groups())
        base = now + timedelta(days=1)
        return datetime(base.year, base.month, base.day, h, mi), line.split(" ", 2)[-1]

    # 解析“HH:MM”
    m = re.match(r'(\d{1,2}):(\d{2})', line)
    if m:
        h, mi = map(int, m.groups())
        t = datetime(now.year, now.month, now.day, h, mi)

        # 已过 → 明天
        if t < now:
            t += timedelta(days=1)

        return t, line.split(" ", 1)[-1]

    return None, None


def main():
    state = load()
    now = datetime.now()

    if not os.path.exists(EVENTS):
        return

    events = open(EVENTS, encoding="utf-8").read().splitlines()
    new_events = []

    for line in events:

        t, event = parse_time(line)

        # 解析失败 → 永远保留（不会再清空）
        if not t:
            print("解析失败(保留):", line)
            new_events.append(line)
            continue

        diff = (now - t).total_seconds() / 60

        # 默认保留
        new_events.append(line)

        # 24小时后删除
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

    # 写回文件
    tmp = EVENTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(new_events))
    os.replace(tmp, EVENTS)

    save(state)
    print("完成")


if __name__ == "__main__":
    main()
