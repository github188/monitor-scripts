#!/usr/bin/env python
# -*- coding:utf8 -*-
# zhouqiang@wandoujia.com
import requests
import json
import re
url = 'http://startpage.wandoujia.com/api/v1/fetch?vc=8000&launchedCount=11'
def get_response(url):
    ret = requests.get(url)
    data = json.loads(ret.content)
    return ret.content
def count_ad(data):
    count = len(re.findall('"ad":true',data))
    return count
    
if __name__ == "__main__":
    data = get_response(url)
    count = count_ad(data)
    if count <1 :
        print "check=FAIL,count:%d" % count
    else:
        print "check=OK"
