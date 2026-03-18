import os
import json
from datetime import datetime

DONE_FILE = "done.txt"
STATS_FILE = "stats.json"

done_list = []

# 读取已完成任务
if os.path.exists(DONE_FILE):
    with open(DONE_FILE, encoding="utf-8") as f:
        done_list = [l.strip() for l in f if l.strip()]

done_count = len(done_list)

# 今日完成（简单版）
today = datetime.now().strftime("%Y-%m-%d")

stats = {
    "done": done_count,
    "last_update": today
}

with open(STATS_FILE, "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print("统计完成：", stats)
