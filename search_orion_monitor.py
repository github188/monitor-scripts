#!/usr/bin/env python
#-*-coding:UTF-8-*-
# Author: yourname@wandoujia.com
# Created Time: 05/29/14 13:20:26
# about:

import urllib2
import json
import sys
def catch_exception(func):
    def __wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print "STATUS=1"
            sys.exit(1)
    return __wrapper

class Monitor(object):
    def query(self, url):
        response = urllib2.urlopen(url).read()
        result_json = json.loads(response)
        return result_json

    def get_value_by_key_value(self, alist, key, key1, value1):
        #import pdb;pdb.set_trace()
        for one in alist: 
            if one[key1] == value1:
                return one[key]


    @catch_exception
    def check(self, url, rpc_method="__ALL_OP_SIGNATURE__"):
        result_json = self.query(url)
        rpc_summary = self.get_value_by_key_value(result_json, "summary", "name", "RpcServer") 
        rpc_stat = rpc_summary["rpc_stat"]
        search_stat = self.get_value_by_key_value(rpc_stat, "data", "key", rpc_method) 
        #print search_stat[0]
        for k in search_stat[0].keys():
            print "%s=%s" %(k,search_stat[0][k])
        print "STATUS=0"

def main():
    m = Monitor()
    if len(sys.argv) != 2:
        print "STATUS=2"
        sys.exit(1)
    #m.check("http://127.0.0.1:9877/status/list", "common.GeneralSearch.Search")
    #m.check("http://127.0.0.1:9812/status/list", "common.QueryRewriter.Rewrite")
    m.check(sys.argv[1])

if __name__ == "__main__":
    main() 


