#!/usr/bin/python

import json
import urllib2
import time

url = "http://localhost:9867/status/data?name=RpcServer"
qps = 0
data = urllib2.urlopen(url).read()
for tag in json.loads(data)['rpc_stat']:
    if tag['key'] == 'common.GeneralIndex.Index':
        for q in tag['data']:
            qps += q['response_qps']


qps_zero_duration = 0
ts_path = '/tmp/.qps_zero_last_ts.txt'
if qps == 0:
    current_ts = int(time.time())
    try:
        with open(ts_path, 'r') as f:
            last_ts = int(f.read())
        qps_zero_duration = current_ts - last_ts
    except:
        pass
    with open(ts_path, 'w') as f:
        f.write(str(current_ts))
else:
    open(ts_path, 'w').close()

print "qps=%s,qps_zero_duration=%s" % (qps, qps_zero_duration)
