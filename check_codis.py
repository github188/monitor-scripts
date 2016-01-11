#!/usr/bin/env python
# -*- coding:utf-8 -*-
# jiangchuangchun@wandoujia.com


import sys
import ast
import time
import redis
import pykeeper


class CheckResult():
    def __init__(self):
        self._isOK = True
        self._msgErr = ''
        self._msgOK = ''

    def isOK(self, ok=True):
        self._isOK = self._isOK and ok
        return self._isOK

    def msgOK(self, msg=''):
        self._msgOK += ' %s'%msg
        return self._msgOK

    def msgErr(self, msg=''):
        self._msgErr += ' %s'%msg
        return self._msgErr


class CodisCheck():
    zk_list = {'HY':'app273.hy01:2181,app274.hy01:2181,app275.hy01:2181,app277.hy01:2181,app272.hy01:2181',
        'HLG':'10.19.29.52:2181,10.19.29.52:2181,10.19.30.4:2181'}

    def __init__(self, zkhost):
        pykeeper.install_log_stream()
        self.zk = pykeeper.ZooKeeper(self.zk_list[zkhost])
        self.zk.connect()

    def checkProxy(self, host, port):
        try:
            r = redis.StrictRedis(host=host, port=port, db=0)
            for i in range(5):
                r.set('SRE_MONITOR_KEY',0)
                time.sleep(0.1)
        except Exception as e:
            return "Except: %s"%str(e)
        else:
            return "OK"

    def checkRedis(self, host, port, mem, type):
        try:
            r = redis.StrictRedis(host=host, port=port, db=0)
            r.ping()
            if (type == 'master'):
                r.set('SRE_MONITOR_KEY',0)
            mem_curr = r.info(section="Memory")['used_memory']
            mem_max = r.config_get(pattern="maxmemory")['maxmemory']
        except Exception as e:
            return "Except: %s"%str(e)
        else:
            if int(mem_max) == 0:
                mem_pct = 100
            else:
                mem_pct = 100*int(mem_curr)/int(mem_max)
    
            if mem_pct >= mem:
                return "Mem_pct:%s"%mem_pct
            else:
                return "OK"

    def check(self, codis_name='ALL', codis_mem=85, proxy=['proxy_1']):
        codis_root='/zk/codis'
        checkResult = CheckResult()

        try:
            # Get full list of codises
            codis_list = self.zk.get_children(codis_root)

            if codis_name == 'ALL':
                pass    # Check all codises
            elif 'db_'+codis_name in codis_list:
                codis_list = ['db_'+codis_name]
            else:   # No such codis name
                print 'No codis named "%s". Full list: %s'%(codis_name, str(codis_list))
                return False
        except:
            print "Fail at get all codis list"
            return False


        # All backend redis list
        all_redis = {}

        for codis in codis_list:
            all_redis[codis] = []

            # Get proxy list
            proxy_addrs = []
            try:
                proxy_list = self.zk.get_children('%s/%s/proxy'%(codis_root, codis))
            except Exception as e:
                checkResult.msgErr(str(e))
                checkResult.isOK(False)
            else:
                for p in proxy:
                    if not p in proxy_list:
                        checkResult.msgErr('%s not configed. '%p)
                        checkResult.isOK(False)
                    else:
                        addr = self.zk.get('%s/%s/proxy/%s'%(codis_root, codis, p))[0]
                        addr = ast.literal_eval(addr)['addr']
                        proxy_addrs.append(addr)
            
            # Check proxy status
            for proxy_addr in proxy_addrs:
                host_port = proxy_addr.split(":")
                p_rlt = self.checkProxy(host_port[0],host_port[1])
                if p_rlt == 'OK':
                    checkResult.msgOK("%s:%s"%(proxy_addr, 'OK'))
                else:
                    checkResult.msgErr("%s:%s"%(proxy_addr, p_rlt))
                    checkResult.isOK(False)


            # Get group ids containing live redis
            group_ids = []  # All groups in use
            for slot in self.zk.get_children('%s/%s/slots'%(codis_root, codis)):
                slot_data = self.zk.get('%s/%s/slots/%s'%(codis_root, codis, slot))[0]
                slot_data = ast.literal_eval(slot_data)
                if slot_data['group_id'] not in group_ids:
                    group_ids.append(slot_data['group_id'])

            # Get all redis instances
            for groupid in group_ids:
                group_redis_list = self.zk.get_children('%s/%s/servers/%s'%(codis_root, codis, 'group_'+str(groupid)))
                # One group may contain one master and more slaves
                for group_redis in group_redis_list:
                    a_redis = self.zk.get('%s/%s/servers/%s/%s'%(codis_root, codis, 'group_'+str(groupid), group_redis))[0]
                    a_redis = ast.literal_eval(a_redis)
                    addr = a_redis['addr'].split(':')
                    all_redis[codis].append({'groupid':groupid, 'type':a_redis['type'], 'host':addr[0], 'port':int(addr[1])})

        # Check redis status
        for a_redis_k, a_redis_v in all_redis.iteritems():
            for a_redis_v_e in a_redis_v:
                a_rlt = self.checkRedis(host=a_redis_v_e['host'], port=a_redis_v_e['port'], mem=codis_mem, type=a_redis_v_e['type'])
                a_rlt_str = ',[%s,%s,%s:%s]:%s'%(a_redis_v_e['groupid'], a_redis_v_e['type'], a_redis_v_e['host'], a_redis_v_e['port'], a_rlt)
                if a_rlt == 'OK':
                    checkResult.msgOK(a_rlt_str)
                else:
                    checkResult.msgErr(a_rlt_str)
                    checkResult.isOK(False)

        if checkResult.isOK():
            print "Check=OK,Name:%s%s"%(str(codis_list), checkResult.msgOK())
        else:
            print "Check=Fail,Name:%s%s"%(str(codis_list), checkResult.msgErr())
        

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for kv_str in sys.argv[1].split(","):
            kv_arr = kv_str.split(":")
            if kv_arr[0] == "name":
                db_name = kv_arr[1]
            elif kv_arr[0] == "mem":
                mem_pct = kv_arr[1]
            elif kv_arr[0] == "zk":
                zk_host = kv_arr[1]
            elif kv_arr[0] == "proxy":
                proxy = kv_arr[1:]
    if not 'db_name' in locals():
        db_name = 'ALL'
    if not 'mem_pct' in locals():
        mem_pct = 85
    if not 'zk_host' in locals():
        zk_host = 'HY'
    if not 'proxy' in locals():
        proxy = ['proxy_1']

    codisCheck = CodisCheck(zk_host)
    codisCheck.check(codis_name = db_name, codis_mem = int(mem_pct), proxy=proxy)
