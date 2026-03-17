import re
from datetime import datetime,timedelta

WEEK_MAP={
"一":0,"二":1,"三":2,"四":3,"五":4,"六":5,"日":6,"天":6
}

def parse_advance(text):

    if "|" not in text:
        return text,0

    base,adv=text.split("|",1)

    minutes=0

    d=re.search(r'(\d+)d',adv)
    h=re.search(r'(\d+)h',adv)
    m=re.search(r'(\d+)',adv)

    if d:
        minutes+=int(d.group(1))*1440

    if h:
        minutes+=int(h.group(1))*60

    if not d and not h and m:
        minutes+=int(m.group(1))

    return base,minutes


def parse(text):

    text=text.strip()

    now=datetime.now()

    text,advance=parse_advance(text)

    t=None

    m=re.match(r'(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2})',text)
    if m:
        y,mn,d,h,mi=map(int,m.groups())
        t=datetime(y,mn,d,h,mi)

    m=re.match(r'(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{2})',text)
    if not t and m:
        mn,d,h,mi=map(int,m.groups())
        t=datetime(now.year,mn,d,h,mi)

    m=re.match(r'(\d{1,2}):(\d{2})$',text)
    if not t and m:
        h,mi=map(int,m.groups())
        t=datetime(now.year,now.month,now.day,h,mi)

    m=re.match(r'明天 ?(\d{1,2}):(\d{2})',text)
    if not t and m:
        h,mi=map(int,m.groups())
        base=now+timedelta(days=1)
        t=datetime(base.year,base.month,base.day,h,mi)

    m=re.match(r'后天 ?(\d{1,2}):(\d{2})',text)
    if not t and m:
        h,mi=map(int,m.groups())
        base=now+timedelta(days=2)
        t=datetime(base.year,base.month,base.day,h,mi)

    m=re.match(r'(\d+)天后 ?(\d{1,2}):(\d{2})',text)
    if not t and m:
        d,h,mi=map(int,m.groups())
        base=now+timedelta(days=d)
        t=datetime(base.year,base.month,base.day,h,mi)

    m=re.match(r'周([一二三四五六日天]) ?(\d{1,2}):(\d{2})',text)
    if not t and m:

        w=WEEK_MAP[m.group(1)]
        h=int(m.group(2))
        mi=int(m.group(3))

        today=now.weekday()

        delta=(w-today)%7

        base=now+timedelta(days=delta)

        t=datetime(base.year,base.month,base.day,h,mi)

    if t and advance:
        t=t-timedelta(minutes=advance)

    return t
