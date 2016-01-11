#!/usr/bin/python
# -*- encoding:utf-8 -*-
# zhouqiang@wandoujia.com
import kazoo
from kazoo.client import KazooClient
from tornado import httpclient
import json
import sqlite3
import os
ZOO_ADDR = (
    'app272.hy01:2181,'
    'app273.hy01:2181,'
    'app274.hy01:2181,'
    'app275.hy01:2181,'
    'app277.hy01:2181'
)
INSTALL_SERVER_LIST = [
    'apps-applist-rpc1-cnc0.hlg01',
]
class ZKClient(KazooClient):
    def __init__(self,hosts=ZOO_ADDR):
        KazooClient.__init__(self, hosts=hosts)
        self.start()

class Process():
    def __init__(self):
        self.zk = ZKClient()
    def get_host(self,path):
        nodes = self.zk.get_children(path)
        ret = []
        for node in nodes:
            ret.append(self.zk.get(path + '/' + node)[0])
        return ret

def get_applist_return(host,port):
    http_client = httpclient.HTTPClient()
    url = 'http://localhost:8080/applist/installCount?packageName=com.tencent.mm&host=' + host + '&port=' + port
    try:
        response = http_client.fetch(url)
        return response.body
    except httpclient.HTTPError as e:
        raise e

def get_db_cursor():
    db = "package.db"
    if not os.path.isfile(db):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute('''create table package (packageName text not null,count int);''')
        conn.commit()
        conn.close()
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    return conn,cursor

def _writeback_pacakge_count(conn,cursor,packageName,count):
    #cursor.execute('''INSERT INTO package VALUES("%s",%d)''' % (packageName,count))
    oc = _get_origin_count(conn,cursor,packageName)
    if oc < 1:
        cursor.execute('''INSERT INTO package VALUES("%s",%d)''' % (packageName,count))
    try:
        cursor.execute('''UPDATE package set count=%d where packagename="%s"''' % (count,packageName))
    except Exception as e:
        pass
    conn.commit()
def _get_origin_count(conn,cursor,packageName):
    cursor.execute('SELECT count FROM package WHERE packagename=?',[packageName])
    item = cursor.fetchone()
    try:
        return item[0]
    except:
        return 0

def check_incr(count,packageName):
    conn,cursor = get_db_cursor()
    origin_count = _get_origin_count(conn,cursor,packageName)
    if count <= origin_count - 50000:
        return False,origin_count
    else:
        _writeback_pacakge_count(conn,cursor,packageName,count)
    return True,origin_count


def parser_result(a):
    try:
        a = json.loads(a)
    except:
        pass
    packageName = a.keys()[0]
    count = a[a.keys()[0]]
    return check_incr(count,packageName)

def get_count_packagename(a):
    try:
        a = json.loads(a)
    except:
        pass
    return a[a.keys()[0]],a.keys()[0]

def Monitor():
    #p = Process()
    #rpcs = p.get_host("/com/wandoujia/applist/rpc")
    status = []
    port = '5009'
    for host in INSTALL_SERVER_LIST:
        try:
            response = get_applist_return(host,port)
            ret = json.loads(response)
            if len(ret) < 1:
                status.append(host+":"+port)
            b,origin_count = parser_result(response)
            if not b:
                count,packageName = get_count_packagename(response)
                status.append(str(host)+":"+str(port)+"; 数据量减少,现在是"+ str(count) + ";之前是" +str(origin_count))
        except Exception as e:
            status.append(host+":"+port)
    if len(status) > 0:
        print "status=FAIL, "," ".join(status)
    else:
        print "status=OK"

if __name__ == "__main__":
    Monitor()
