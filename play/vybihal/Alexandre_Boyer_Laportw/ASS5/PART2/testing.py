#!/usr/bin/python

import dt
import datetime


tester1 = dt.dt(0,datetime.datetime(year=2001, month=1,day=1,hour=0,minute=0,second=0))  # should be true


datetime_string= '[09:00:00, 18:00:00]/[Saturday,Tuesday]'
date_string = '[04:01, 15:06]'
time_string = '[11:00:00]'
print 'call A: ', tester1.is_date(date_string)
print 'call B: ', tester1.is_time(time_string)
print 'call C: ', tester1.is_datetime(datetime_string)
