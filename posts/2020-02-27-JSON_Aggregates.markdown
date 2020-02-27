---
title: Django Aggregates Over JSONB
author: Quinlan Pfiffer
---

I wanted to park this here because it's useful. You can do aggregates over
nested JSONB fields in Django via a series of casts, which you can express using
only the ORM. Heres a simple examples. This is based on a real-world example
where I had to cast the float to an integer, which is a bonus little easter egg.

```Python
from django.db.models import Sum, IntegerField, FloatField, TextField
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import timedelta

class TicketReport:
    timestamp = models.DatetimeField()
    tickets = JSONField()

    def get_ticket_count_30_day(self):
        qs = obj.report_set\
                .filter(timestamp__gt=timezone.now() - timedelta(days=30))\
                .annotate(numeric_val=Cast(Cast(Cast('tickets', TextField()), FloatField()), IntegerField()))\
                .aggregate(Sum('numeric_val'))
        ds = qs['numeric_val__sum'] or 0
        return ds
```

Assume the JSON looks something like this, and you take part of that value and
extract it into the `tickets` field:

```JSON
{
  "tickets": 2516.0
}
```

You can directly cast the value into an Integer and then aggregate over it.
