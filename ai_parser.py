from datetime import datetime,timedelta
import re

WEEKMAP={"一":0,"二":1,"三":2,"四":3,"五":4,"六":5,"日":6,"天":6}

def parse(text):

    now=datetime.now()

    if "今天" in text:
        t=re.findall(r'\d+点',text)
        if t:
            h=int(t[0].replace("点",""))
            return now.replace(hour=h,minute=0)

    if "明天" in text:
        t=re.findall(r'\d+点',text)
        if t:
            h=int(t[0].replace("点",""))
            dt=now+timedelta(days=1)
            return dt.replace(hour=h,minute=0)

    if "后天" in text:
        t=re.findall(r'\d+点',text)
        if t:
            h=int(t[0].replace("点",""))
            dt=now+timedelta(days=2)
            return dt.replace(hour=h,minute=0)

    if text.startswith("每天"):
        t=re.findall(r'\d+点',text)
        if t:
            return ("daily",int(t[0].replace("点","")))

    if text.startswith("每周"):
        day=text[2]
        t=re.findall(r'\d+点',text)
        if t:
            return ("weekly",day,int(t[0].replace("点","")))

    if text.startswith("每月"):
        d=re.findall(r'\d+',text)[0]
        t=re.findall(r'\d+点',text)[0]
        return ("monthly",int(d),int(t.replace("点","")))

    return None
