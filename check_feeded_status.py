#!/bin/env python

import sys
import json
import requests
import datetime


def main():
    url="http://nginxlog.hy01.internal.wandoujia.com/feeded/account"
    ret = requests.get(url)
    data = json.loads(ret.content)["message"]
    last_one = data[-1]
    _time  = last_one["date"] + last_one["hourmin"]

    sub  = datetime.datetime.now() - datetime.datetime.strptime(_time, '%Y%m%d%H%M')
    sub = int(str(sub).split(":")[0])
    if sub > 3:
        print "feeded_status=Fail, last feeded:%s" % last_one 
    else:
        print "feeded_status=OK, last feeded:%s" % last_one 
    

if __name__ == "__main__":
    main()
