---
title: A Random Python Timezone Bug
author: Quinlan Pfiffer
---

So this one is another interesting Python Timezone thing. It feels like every
time I do something with timezones in Python, I think I've got them figured out
and I clearly don't. Theres always another thing. This one was interesting
though and took a while to figure out. The issue turned out to be not as
straight-forward as I thought it would have been.

Imagine something like this:

```Python
from datetime import datetime, timezone
import pytz

TIMEZONE = "US/Eastern"
tz = pytz.timezone(TIMEZONE)

def utc_now():
    return datetime.now(timezone.utc)

def tz_now():
    return convert_to_local(get_utc_now())

def convert_to_local(any_time):
    return any_time.astimezone(tz)

def convert_to_utc(any_time):
    return any_time.astimezone(pytz.utc)
```

With me so far? Simple stuff, and this is all the correct way to do timezones in
Python: No [naive timestamps](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects),
no [replace](http://pytz.sourceforge.net/#localized-times-and-date-arithmetic), use
UTC for computation and localtime for display, etc. Good, let's keep going:

```Python
# Get the first of the month, in the local time:
local_first_of_month = tz_now().replace(day=1, hour=0, minute=0,
        second=0, microsecond=0)
# datetime.datetime(2020, 3, 1, 0, 0,
#    tzinfo=<DstTzInfo 'US/Eastern' EDT-1 day, 20:00:00 DST>)

# Convert it to utc:
utc_first_of_month = convert_to_utc(local_first_of_month)
# datetime.datetime(2020, 3, 1, 4, 0,
#    tzinfo=datetime.timezone.utc)

# Convert it back and ???
convert_to_local(utc_first_of_month)
# datetime.datetime(2020, 2, 29, 23, 0,
#    tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)

```

Whoa, wait a minute, what happened there? Why aren't they the same? Should going
between UTC and your local timezone be idempotent? Well, you'd be correct,
except that things go a little haywire when you call `replace()`. `replace()`
will probably work just fine in the vast majority of cases, *except* when you
cross a daylight savings-time boundary. You'll notice here that the two
timestamps have the same timezone name, but differ in Daylight-ness: `DST` vs.
`STD`.

The reason it isn't "idempotent" here is because that doesn't really make any
sense, since you're crossing a datetime boundary: Though timezones are
technically the same, the hour delta between UTC changes because of daylight
savings time. This only happens when you do a `replace()`, because you're just
modifying values on  an existing timezone. Fascinating, but REAL annoying.
Heres the correct implementation: instead of doing a replace, build the
datetime from the ground up:

```Python
# Get the first of the month, in the local time:
local_first_of_month = datetime(year=this.year, month=this.month, day=1,
        hour=0, minute=0, second=0, microsecond=0)
local_first_of_month = tz.localize(local_first_of_month)
```

This works as you'd expect, and works regardless of when you run the code since
you're not doing a replace on `datetime.now()`. Good luck out there, soldier.
