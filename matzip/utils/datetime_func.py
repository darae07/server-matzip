import datetime
import time
from django.utils import timezone
from dateutil.relativedelta import relativedelta


def get_after_minutes(minutes, date=None):
    if date is None:
        now = datetime.datetime.now()
        result = now + relativedelta(minutes=minutes)
    else:
        result = date + relativedelta(minutes=minutes)
    return result


today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
