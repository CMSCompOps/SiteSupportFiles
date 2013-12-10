import datetime
from datetime import date

class TimeInfo:
    def __init__(self):
        self.todaydate             = date.today()
        self.today                 = datetime.datetime.utcnow()
        self.todaystamp            = self.today.strftime("%Y-%m-%d")
        self.todaystampfile        = self.today.strftime("%Y-%m-%d %H:%M:%S")
        self.todaystampfileSSB     = self.today.strftime("%Y-%m-%d 00:00:01")
        self.d                     = datetime.timedelta(1);
        self.yesterday             = self.today - self.d
        self.yesterdaystamp        = self.yesterday.strftime("%Y-%m-%d")
        self.yesterdaystampfileSSB = self.yesterday.strftime("%Y-%m-%d 00:00:01")
        self.timestamphtml         = self.today.strftime("%Y%m%d")

# return a generator for iterating from start date to stop date
def daterange(start, stop, step=datetime.timedelta(days=1)):
    if step.days > 0:
        while start < stop:
            yield start
            start = start + step
    elif step.days < 0:
        while start > stop:
            yield start
            start = start + step
