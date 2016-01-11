#!/usr/bin/python
# -*- coding:utf-8 -*-
# qinguoan@wandoujia.com
# 2014-03-10
import re
import os
import sys
import pykeeper
import redis
import socket

pykeeper.install_log_stream()

class zookeeper_client(object):
	def __init__(self,host):
		self.zkh = pykeeper.ZooKeeper(host, reconnect = True)
		self.zkh.connect()
		self.zkh.wait_until_connected(timeout=1)
		self.connected = True if self.zkh.state_name == 'connected' else False

	def execute(self, action, path, value=None):
		try:
			func = getattr(zookeeper_client, action)
		except Exception:
			pass
		else:
			return func(self,path)

	def list(self, path):
		try:
			return self.zkh.get_children(path)
		except Exception:
			return []
	
	def get(self, path):
		try:
			return self.zkh.get(path)[0]
		except Exception:
			return ''



class redis_client(redis.StrictRedis):
    def __init__(self):
        pool = redis.ConnectionPool(host = 'localhost',port = 6379,db = 0,max_connections= 1)
        redis.StrictRedis.__init__(self, connection_pool = pool)
        self.connected = True if self.ping() else False



def ipaddress(*servers):
	ips = dict()
	for server in servers:
		ip = socket.gethostbyname(server)
		ips[ip] = server
	return ips

def check(host):
	# configuration
	paths = {
		'read_nodes' :'/com/wandoujia/mms/dataservice/rpc', 
		'write_nodes': '/com/wandoujia/mms/dataservice_write/rpc',
		}


	zkh = zookeeper_client(host)
	rkh = redis_client()
	if rkh.connected:
		read_nodes = [ i for i in rkh.smembers('server:hy:app-kernel:mms-dataservice-read') ]
		write_nodes = [ i for i in  rkh.smembers('server:hy:app-kernel:mms-dataservice-write') ]
	else:
		read_nodes = [ "app315.hy01", "app316.hy01", "app317.hy01", "cache1.hy01" ]
		write_nodes = ["app314.hy01", "cache0.hy01"]

	read_nodes = ipaddress(*read_nodes)

	write_nodes =  ipaddress(*write_nodes)

	error_read = list()
	error_write = list()
	if zkh.connected:
		for path in paths:
			znodes = zkh.execute('list', paths[path])
			if not znodes:
				continue
			else:
				for node in znodes:
					tmp = paths[path] + '/' + node
					name = zkh.execute('list', tmp)
					tmp += '/' + name[0]
					ip = zkh.execute('get',tmp).split(':')[0]
					if not ip or not re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip):
						continue
					else:
						if path == 'read_nodes':
							if ip in read_nodes:
								del read_nodes[ip]
							else:
								error_read.append(ip)
						elif path == 'write_nodes':
							if ip in write_nodes:
								del write_nodes[ip]
							else:
								error_write.append(ip)
	else:
		print "STATUS=1,zookeeper connect failed"
		exit(1)
	if read_nodes:
		print "STATUS=2,read_nodes:%s isn't connected" % (','.join(read_nodes.values()))
	if write_nodes:
		print "STATUS=3,write_nodes:%s isn't connected" % (','.join(write_nodes.values()))
	if error_read:
		print "STATUS=4,read_nodes:%s wrong ip connected" % (','.join(error_read))
	if error_write:
		print "STATUS=5,write_nodes:%s wrong ip connected" % (','.join(error_write))
	if not read_nodes and not write_nodes and not error_read and not error_write:
		print "STATUS=0,data service znodes ok"

if __name__ == "__main__":
	host = 'app272.hy01:2181, app273.hy01:2181, app274.hy01:2181,app275.hy01:2181, app277.hy01:2181'
	check(host)
