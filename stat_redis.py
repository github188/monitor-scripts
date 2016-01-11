#!/usr/bin/env python
# -*- coding:utf8 -*-
# qinguoan@wandoujia.com
#
try:
    import os
    import sys
    import json
    import time
    import zlib
    import redis
    import subprocess 
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

def stats_redis(port=6379):
    redis = RedisClient(port=port)
    info = redis.info()
    ret = {}
    #ret['port'] = port
    for k,v in info.iteritems():
        if k in ['instantaneous_ops_per_sec','total_commands_processed','keyspace_misses','keyspace_hits','connected_clients','total_connections_received','used_memory','maxmemory','mem_fragmentation_ratio','keyspace']:
            ret[k] = v
    ret['maxmemory'] = redis.config_mem()['maxmemory']
    return ret

def main(argv):
    crc = zlib.crc32(argv, 0xffffffff)
    try:
        f = open('/tmp/_redis_stat.%s'%crc, 'r')
        last = json.loads(f.read())
        f.close()
    except:
        last = False

    if argv == 'auto':
        ports = []
        p1 = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "codis-server\|redis-server"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = subprocess.Popen(["grep", "-v", "grep"], stdin=p2.stdout, stdout=subprocess.PIPE)
        output = p3.communicate()[0]
        for line in output.strip().split("\n"):
            arr = line.strip().split(":")
            port = arr[len(arr)-1].strip()
            ports.append(port)
    else:
        ports = argv.split(',')

    this = {}
    this['ts'] = int(time.time())
    for  port in ports:
        rlt = stats_redis(port)
        this[port] = rlt
        for k,v in rlt.iteritems():
            if not last or port not in last.keys():
                print "optsdb:redis.%s|%s|port|%s"%(k,0,port)
            elif k in ['total_commands_processed','keyspace_misses','keyspace_hits','total_connections_received']:
                diff = round( (v - last[port][k]) / (time.time() - last['ts']), 2 )
                print "optsdb:redis.%s|%s|port|%s"%(k,diff,port)
            else:
                print "optsdb:redis.%s|%s|port|%s"%(k,v,port)

    f = open('/tmp/_redis_stat.%s'%crc, 'w')
    f.write(json.dumps(this))
    f.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print "No port(s) provided, auto check"
        main('auto')
