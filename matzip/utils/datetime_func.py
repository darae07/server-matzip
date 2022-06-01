from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta


def get_after_minutes(minutes, date=None):
    if date is None:
        now = datetime.datetime.now()
        result = now + relativedelta(minutes=minutes)
    else:
        result = date + relativedelta(minutes=minutes)
    return result


today = datetime.now().date()
today_min = datetime.combine(today, time())
today_max = datetime.combine((today + timedelta(1)), time())
