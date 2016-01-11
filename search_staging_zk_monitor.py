#!/usr/bin/python
# -*- coding:utf-8 -*-
# heqiang@wandoujia.com
# 2014-09-30
import re
import os
import sys
import pykeeper
import redis
import socket
import getopt

pykeeper.install_log_stream()

def usage():
	print "python %s usage:" % sys.argv[0]
	print "-h , --help:print help message."
	print "-i idc_name,--idc idc_name: idc to monitor."
	sys.exit(0)

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
        #pool = redis.ConnectionPool(host = 'localhost',port = 6379,db = 0,max_connections= 1)
        pool = redis.ConnectionPool(host = '10.0.1.12',port = 6379,db = 0,max_connections= 1)
        redis.StrictRedis.__init__(self, connection_pool = pool)
        self.connected = True if self.ping() else False



def ipaddress(*servers):
	ips = dict()
	for server in servers:
		ip = socket.gethostbyname(server)
		ips[ip] = server
	return ips

def check(host,idc_name):
	# configuration
	paths = {
		'db':{
			'rewriter_nodes' :'/com/wandoujia/orion/staging/server/rewriter',
			'realtime_nodes': '/com/wandoujia/orion/staging/leaf/realtime',
			'dataservice_nodes':'/com/wandoujia/orion/staging/dataservice/0',
			'ssd_nodes':'/com/wandoujia/orion/staging/leaf/ssd',
			'ssd_apps_nodes':'/com/wandoujia/mmsapps/staging/search/leaf/ssd',
			'realtime_apps_nodes':'/com/wandoujia/mmsapps/staging/search/leaf/realtime',
			},
	}

	zkh = zookeeper_client(host[idc_name])
	#rkh = redis_client()

	#rewriter_nodes = list()
	#realtime_nodes = list()
	#dataservice_nodes = list()
	#ssd_nodes = list()
	#ssd_apps_nodes = list()
	#realtime_apps_nodes = list()
	#segment_nodes = list()
	#if rkh.connected:
	#	if idc_name == "hy":
	#		rewriter_nodes = [ i for i in rkh.smembers('server:hy:search:rewriter') ]
	#		realtime_nodes = [ i for i in  rkh.smembers('server:hy:search:realtime_leaf') ]
	#		dataservice_nodes = [ i for i in  rkh.smembers('server:hy:search:data_services') ]
	#		ssd_nodes = [ i for i in  rkh.smembers('server:hy:search:ssd_leaf') ]
	#		ssd_apps_nodes = [ i for i in rkh.smembers('server:hy:search:ssd_leaf_apps')]
	#		realtime_apps_nodes = [ i for i in rkh.smembers('server:hy:search:realtime_leaf_apps')]
	#	elif idc_name == "db":
	#		segment_nodes = [ i for i in rkh.smembers('server:db:search:segmenter')]
	#else:
	rewriter_nodes = [ "index1.db01" ]
	realtime_nodes = [ "index1.db01" ]
	dataservice_nodes = [ "index1.db01" ]
	ssd_nodes = [ "index1.db01" ]
	ssd_apps_nodes = [ "index2.db01" ]
	realtime_apps_nodes = [ "index2.db01" ]

	if idc_name == "db":
		rewriter_nodes = ipaddress(*rewriter_nodes)
		realtime_nodes =  ipaddress(*realtime_nodes)
		dataservice_nodes = ipaddress(*dataservice_nodes)
		ssd_nodes = ipaddress(*ssd_nodes)
		ssd_apps_nodes = ipaddress(*ssd_apps_nodes)
		realtime_apps_nodes = ipaddress(*realtime_apps_nodes)

	error_rewriter = list()
	error_realtime = list()
	error_dataservice = list()
	error_ssd = list()
	error_ssd_apps = list()
	error_realtime_apps = list()
	error_segment = list()
	if zkh.connected:
		for path in paths[idc_name]:
			znodes = zkh.execute('list', paths[idc_name][path])
			if not znodes:
				continue
			else:
				for node in znodes:
					tmp = paths[idc_name][path] + '/' + node
					ip = zkh.execute('get',tmp).split(':')[0]
					if not ip or not re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ip):
						continue
					else:
						if path == 'rewriter_nodes':
							if ip in rewriter_nodes:
								del rewriter_nodes[ip]
							else:
								error_rewriter.append(ip)
						elif path == 'realtime_nodes':
							if ip in realtime_nodes:
								del realtime_nodes[ip]
							else:
								error_realtime.append(ip)
						elif path == 'dataservice_nodes':
							if ip in dataservice_nodes:
								del dataservice_nodes[ip]
							else:
								error_dataservice.append(ip)
						elif path == 'ssd_nodes':
							if ip in ssd_nodes:
								del ssd_nodes[ip]
							else:
								error_ssd.append(ip)
						elif path == 'ssd_apps_nodes':
							if ip in ssd_apps_nodes:
								del ssd_apps_nodes[ip]
							else:
								error_ssd_apps.append(ip)
						elif path == 'realtime_apps_nodes':
							if ip in realtime_apps_nodes:
								del realtime_apps_nodes[ip]
							else:
								error_realtime_apps.append(ip)
						elif path == 'segment_nodes':
							if ip in segment_nodes:
								del segment_nodes[ip]
							else:
								error_segment.append(ip)
	
	else:
		print "STATUS=1,zookeeper connect failed"
		exit(1)
	if rewriter_nodes:
		print "STATUS=2,rewriter_nodes:%s isn't connected" % (','.join(rewriter_nodes.values()))
	if realtime_nodes:
		print "STATUS=3,realtime_nodes:%s isn't connected" % (','.join(realtime_nodes.values()))
	if dataservice_nodes:
		print "STATUS=4,dataservice_nodes:%s isn't connected" % (','.join(dataservice_nodes.values()))
	if ssd_nodes:
		print "STATUS=5,ssd_nodes:%s isn't connected" % (','.join(ssd_nodes.values()))
	if ssd_apps_nodes:
		print "STATUS=6,ssd_apps_nodes:%s isn't connected" % (','.join(ssd_apps_nodes.values()))
	if realtime_apps_nodes:
		print "STATUS=7,realtime_apps_nodes:%s isn't connected" % (','.join(realtime_apps_nodes.values()))
	if error_rewriter:
		print "STATUS=8,rewriter_nodes:%s wrong ip connected" % (','.join(error_rewriter))
	if error_realtime:
		print "STATUS=9,realtime_nodes:%s wrong ip connected" % (','.join(error_realtime))
	if error_dataservice:
		print "STATUS=10,dataservice_nodes:%s wrong ip connected" % (','.join(error_dataservice))
	if error_ssd:
		print "STATUS=11,ssd_nodes:%s wrong ip connected" % (','.join(error_ssd))
	if error_ssd_apps:
		print "STATUS=12,ssd_apps_nodes:%s wrong ip connected" % (','.join(error_ssd_apps))
	if error_realtime_apps:
		print "STATUS=13,realtime_apps_nodes:%s wrong ip connected" % (','.join(error_realtime_apps))
	if not rewriter_nodes and not realtime_nodes and not error_rewriter and not error_realtime and not dataservice_nodes and not ssd_nodes and not error_dataservice and not error_ssd and not error_ssd_apps and not error_realtime_apps and not ssd_apps_nodes and not realtime_apps_nodes :
		print "STATUS=0,data service znodes ok"

if __name__ == "__main__":
	try:
		opts,args = getopt.getopt(sys.argv[1:],"i:",["idc="])
	except getopt.GetoptError:
		usage()
		sys.exit(1)

	host = {
		"db":"stg1.hy01:2181, stg2.hy01:2181, stg3.hy01:2181",
	}
	
	for opt,arg in opts:
		if opt in ("-i","--idc"):
			idc_name = arg
			if idc_name == 'db':
				pass
			else:
				print "Invalid IDC Name!"
				sys.exit(1)
		elif opt in ("-h","--help"):
			usage()
			sys.exit(1)
	
	check(host,idc_name)
