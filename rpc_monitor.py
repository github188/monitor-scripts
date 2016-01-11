#!/usr/bin/python
# -*- coding:utf-8 -*-
# __author__ = 'hq'

import urllib2
import socket
import ujson as json
import sys
import logging
from kazoo.client import KazooClient

logging.basicConfig()
reload(sys)
sys.setdefaultencoding('utf8')


class Loki(object):
    def __init__(self):
        pass

    def get_node_instance(self, node_id):
        self.hosts = [] # store server list
        url = "http://loki.hy01.internal.wandoujia.com/server/api/servers?type=recursive&node_id=" + node_id
        data = urllib2.urlopen(url).read()
        for item in json.loads(data)['data']:
            self.hosts.append(''.join(map(lambda x: "%c" % ord(x), list(item['hostname']))))

        return self.hosts


class Zookeeper(object):
    def __init__(self, host):
        self.zk = KazooClient(hosts=host, connection_retry=True, read_only=True)
        self.zk.start()

    def stop(self):
        self.zk.stop()

    def get_path_instance(self, path):
        self.hosts = [] # store server list
        if self.zk.exists(path):
            if self.zk.get_children(path) > 0:
                for node in self.zk.get_children(path):
                    node_path = path + '/' + node
                    data, stat = self.zk.get(node_path)
                    host = data.split(':')[0]
                    self.hosts.append(host)
        else:
            raise Exception("path is not exsits")

        return self.hosts


def ipaddress(servers):

    ips = []
    for server in servers:
        ip = socket.gethostbyname(server)
        ips.append(ip)
    return ips

def compare(zk_hosts, info):

    zoo = Zookeeper(zk_hosts)
    loki = Loki()
    idc_list = []

    for p in info:
        name = p['name']
        path = p['zk_path']
        lid = p['loki_id']
        real_server = ipaddress(zoo.get_path_instance(path))
        theo_server = ipaddress(loki.get_node_instance(lid))
        for k in theo_server:
            if k not in real_server:
                detail = "shortage:%s:%s" % (name, k)
                idc_list.append(detail)
        for k in real_server:
            if k not in theo_server:
                detail = "extra:%s:%s" % (name, k)
                idc_list.append(detail)
    zoo.stop()
    return idc_list

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

if __name__ == '__main__':

    zk_addr = {
        "hy":"app272.hy01:2181, app273.hy01:2181, app274.hy01:2181,app275.hy01:2181, app277.hy01:2181",
        "hlg":"app272.hy01:2181, app273.hy01:2181, app274.hy01:2181,app275.hy01:2181, app277.hy01:2181",
        "db":"hda87.db01:2181,hda88.db01:2181,hda89.db01:2181"
    }

    ret = []
    config = loadcfg()
    for k,v in config.iteritems():
        zk_hosts = zk_addr[k]
        ret += compare(zk_hosts, v)

    if len(ret) > 0:
        s = ','.join(ret)
        print "STATUS=1,%s" % s
    else:
        print "STATUS=0"
