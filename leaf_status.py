#!/usr/bin/python

import sys
import json
import urllib2
import getopt


options,args = getopt.getopt(sys.argv[1:],'s:')
for opt, arg in options:
        if opt in ('-s'):
                srv_name = arg
                if srv_name == 'realtime_leaf':
                        port = '9867'
                elif srv_name == 'ssd_leaf':
                        port = '9877'
                elif srv_name == 'rewriter':
                        port = '9812'
                else:  
                        sys.exit(1)
        else:  
                sys.exit(0)

url = "http://localhost:" + port + "/status/list"
data = urllib2.urlopen(url).read()
if srv_name == 'realtime_leaf':
	res = json.loads(data)[1]
elif srv_name == 'ssd_leaf':
	res = json.loads(data)[0]
elif srv_name == 'rewriter':
	res = json.loads(data)[0]
else:
	sys.exit(1)

for tag in res['summary']['rpc_stat']:
        if srv_name == 'rewriter':
            if tag['key'] == 'common.QueryRewriter.RewriteV2':
                item = tag['data'][0]
                break
        else:
            if tag['key'] == 'common.GeneralSearch.Search':
                item  = tag['data'][0]
                break

for key in  ["request_qps","response_qps","latency_avg","latency_min","latency_max","latency_nq_avg"] :
    print "optsdb:%s.%s|%s" %(srv_name,key,item[key])
