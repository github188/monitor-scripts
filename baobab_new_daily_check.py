#!/usr/bin/python
# -*- coding: utf-8 -*-
# lihao@wandoujia.com
# 2015-05-12

import urllib2
import pytz
import time
from datetime import datetime

url = "http://baobab.wandoujia.com/api/v1/feed"
# print url

try:
    response = urllib2.urlopen(url)
    json = response.read()
    # print json

    now = datetime.now(pytz.timezone('Asia/Chongqing'))
    # print now
    today = datetime(now.year, now.month, now.day)
    # print today

    timestamp = int(time.mktime(today.timetuple()))*1000
    # print timestamp

    date_str = "\"date\":" + str(timestamp)
    # print date_str

    if date_str in json:
        print "ret=success"
    else:
        print "ret=failed"
except BaseException as e:
    print str(e)
    print "ret=failed"
