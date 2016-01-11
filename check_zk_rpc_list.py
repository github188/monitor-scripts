#!/bin/env python
# -*- coding:utf8 -*-
# jiangchangchun@wandoujia.com
'''
检查zk节点注册的列表
参数示例:
'{"zk":"HY","path":"/com/wandoujia/plutus/ads/rpcServer","hosts":["monetization-plutus0-bgp0.hy01"]}'
'''

import pykeeper
import sys
import json
import socket


class Checker():
    zk_list = {'HY':'app273.hy01:2181,app274.hy01:2181,app275.hy01:2181,app277.hy01:2181,app272.hy01:2181'}
    def __init__(self, zkhost='HY'):
        pykeeper.install_log_stream()
        self.zk = pykeeper.ZooKeeper(self.zk_list[zkhost])
        self.zk.connect()
    
    def compare(self, path, expect_hosts):
        try:
            znodes = self.zk.get_children(path)
        except Exception:
            print "Error at get host list from zookeeper"
            exit(1)

        current_hosts = []
        for node in znodes:
            host = self.zk.get(path+'/'+node)[0]
            host = host.split(":")[0]
            current_hosts.append(host)

        current_hosts = list(set(current_hosts))
        expect_hosts = list(set(expect_hosts))
        for i, host in enumerate(set(expect_hosts)):
            ip = socket.gethostbyname(host)
            if ip in current_hosts:
                current_hosts.remove(ip)
                expect_hosts.remove(host)

        if len(expect_hosts)==0 and len(current_hosts)==0:
            print "result=OK"
        elif len(expect_hosts)>0:
            print "result=Expect_host:%s. "%(','.join(expect_hosts))
        elif len(current_hosts)>0:
            print "result=NOT_Expect_host:%s. "%(','.join(current_hosts))


if __name__ == '__main__':
    checker = Checker()
    args = sys.argv[1]
    args = json.loads(args)
    checker.compare(path=args['path'],expect_hosts=args['hosts'])
