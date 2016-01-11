#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import time
import urllib2

def get_api_time(url):
    resp = urllib2.urlopen(url)
    val = resp.read().strip()
    return time.time() - float(val) / 1000

if __name__ == "__main__":
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        sys.exit(-1)

    url = "http://" + host + ":" + port + "/status?ws=1"
    diff = get_api_time(url)
    print "interval=%s" %(diff)
