#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: qinguoan@wandoujia.com 
# 2014-06-18


try:
    import os
    import sys
    import json
    from time import strftime, localtime
except ImportError as e:
    exit(1)


def deal_data(args):
    file, interval = args[0], args[1]
    if os.path.isfile(file) or os.path.islink(file):
        mtime = os.stat(file)[-2]
        cur_time = strftime('%s', localtime())
        if int(cur_time) - int(mtime) < int(interval):
            fh = open(file, 'r')
            json_obj = json.load(fh)
            for item, value in json_obj.items():
                for k, v in value.items():
                    key = '%s:%s' % (item, k)
                    print "%s=%s" % (key, v)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(0)
    else:
        deal_data(sys.argv[1:])
