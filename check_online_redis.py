#!/usr/bin/env python
# -*- coding:utf8 -*-
# qinguoan@wandoujia.com
#
try:
    import os
    import sys
    import redis
except ImportError as e:
    print str(e)
    exit(1)


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions as e:
            return None
    return wrapper

class RedisClient(redis.StrictRedis):
    def __init__(self, host='localhost', port=6379, dbid=0):
        pool = redis.ConnectionPool(host=host, port=port, db=dbid, max_connections=1)
        redis.StrictRedis.__init__(self, connection_pool=pool)

    @catch_exception
    def check_alive(self):
        return self.ping()
    
    @catch_exception
    def list_len(self, name):
        return self.llen(name)
    
    @catch_exception
    def info_mem(self):
        return self.info(section='Memory')

    @catch_exception
    def config_mem(self):
        return self.config_get(pattern='maxmemory')

def check_redis_status(*args):
    for port in args:
        rs = RedisClient(port=port)
        if rs.check_alive():
            print 'Redis:%s=OK' % port
            mem_used = rs.info_mem()['used_memory']
            mem_max = rs.config_mem()['maxmemory']
            print 'Mem_pct:%s=%d' % (port, mem_used*100/float(mem_max))
        else:
            print 'Redis:%s=ERROR' % port
   
def check_list_len(*args):
    for name in args:
        length = RedisClient(port=22122).list_len(name)
        print 'Queue:%s=%s' % (name, length)

@catch_exception
def main(argv=None):
    args = dict()
    if len(sys.argv) == 2:
        argv = sys.argv[1]
    if not argv:
        print 'script parm is empty'
        exit(1)
    for item in (x.strip() for x in argv.split(',')):
        k, v = [x.strip() for x in item.split(':')]
        if k not in args:args[k] = list()
        args[k].append(v)
    if 'redis' in args:check_redis_status(*args['redis'])
    if 'queue' in args:check_list_len(*args['queue'])
    if 'twemproxy' in args:check_proxy_alive(*args['twemproxy'])

if __name__ == "__main__":
    argv = '\
           redis:6378,\
           redis:6379,\
	   redis:6380,\
	   redis:6381,\
	   redis:6382,\
	   redis:6383,\
	   redis:6384,\
	   redis:6385,\
	   redis:6386,\
	   redis:6479,\
	   redis:6480,\
	   redis:6481,\
           redis:6482,\
           redis:6483,\
           redis:6484,\
           redis:6485,\
	   redis:6486'
    main(argv)
