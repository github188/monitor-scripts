#!/usr/bin/python
# -*- coding:utf-8 -*-
# __author__ = 'hq'

import urllib2
import socket
import json
import re
import sys
import gzip
import logging
from StringIO import StringIO

logging.basicConfig()
reload(sys)
sys.setdefaultencoding('utf8')

def loadcfg():
    cfg = {}
    if len(sys.argv) > 1:
        cfg = json.loads(sys.argv[1])
    else:
        usage()
    return cfg

def usage():
    print "python %s <json>" % sys.argv[0]
    sys.exit(0)

def parse_gzipd_http(url):
    try:
        response = urllib2.urlopen(url)
        code = response.getcode()
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
        else:
            content = response.read()

    except urllib2.HTTPError as e:
        code = e.code
        content = ""

    return {"url":url,"code":code,"content":content}

def check_alarm(src, obj):
    alarm_name = src['name']
    if str(src['code']) != str(obj['code']):
        msg = "{name} : {url} {real_code} != {main_code}".format(name=alarm_name, url=src['url'], real_code=src['code'], main_code=obj['code'])
        alarm_list.append(msg)
    else:
        if src['match'] != "":
            for match_key in re.split("\s+", src['match']):
                if re.search(match_key.decode("utf8"), str(obj['content']).decode("utf8")) == None:
                    msg = "{name} : {url} content dismatch {str}".format(name=alarm_name, url=src['url'], str=match_key)
                    alarm_list.append(msg)

        if src['dismatch'] != "":
            for dismatch_key in re.split("\s+", src['dismatch']):
                if re.search(dismatch_key.decode("utf8"), str(obj['content']).decode("utf8")) != None:
                    msg = "{name} : {url} content match {str}".format(name=alarm_name, url=src['url'], str=dismatch_key)
                    alarm_list.append(msg)

if __name__ == '__main__':

    alarm_list = []

    config = loadcfg()
    for item in config['data']:
        result = parse_gzipd_http(item['url'])
        check_alarm(item, result)

    if len(alarm_list) == 0:
        print "OK"
        sys.exit(0)
    else:
        print '\n'.join(alarm_list)
        sys.exit(1)


