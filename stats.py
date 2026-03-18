done=0

if os.path.exists("done.txt"):
    done=len(open("done.txt").read().splitlines())

print("已完成任务:",done)
