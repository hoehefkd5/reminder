import json

done=open("done.txt").read().splitlines()

stats={
"done":len(done)
}

with open("stats.json","w") as f:

    json.dump(stats,f)
