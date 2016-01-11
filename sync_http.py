#!/usr/bin/env python

import sys
import json
import urllib
import urllib2

POLICY_URL = "http://m.wandoulabs.com/rambo_admin/policy/http?collector="
POLICY_UPDATE_URL = "http://m.wandoulabs.com/rambo_admin/policy/http/"
COLLECTOR_URL = "http://m.wandoulabs.com/rambo_admin/collector/http"
COLLECTOR_UPDATE_URL = "http://m.wandoulabs.com/rambo_admin/collector/http/"
#PTREE_URL     = "http://loki.hy01.internal.wandoujia.com/server/api/servers?type=node&node_id="
PTREE_URL = "http://loki.hy01.internal.wandoujia.com/server/api/servers?type=path&path="
X_SUPERTOKEN = "OnAD2ImiTiC1nXrJXNaa3eCEbqXrGEANlVEm+C/rUEU="


def getCollectors():
    request = urllib2.Request(COLLECTOR_URL,
                              headers={"X-Supertoken": X_SUPERTOKEN})
    contents = urllib2.urlopen(request).read()
    collectors = json.loads(contents)
    return collectors


def loadConfig():
    if len(sys.argv) > 1:
        #configFile=sys.argv[1]
        cfg = json.loads(sys.argv[1])
    else:
        configFile = "config.json"
        with open(configFile, "r") as fd:
            data = fd.read()
            cfg = json.loads(data)
    return cfg


cfg = loadConfig()
collectors = getCollectors()


def updateCollector(collector):
    collector["id"] = collector["name"]
    data = json.dumps(collector)
    name = urllib.quote(collector["name"].encode('utf-8'))
    request = urllib2.Request(COLLECTOR_UPDATE_URL + name,
                              data=data,
                              headers={"X-Supertoken": X_SUPERTOKEN})
    print urllib2.urlopen(request).read()


def mergeCollector(collector):
    hosts = []
    for path in cfg[collector]["path"]:
        hosts = hosts + getHosts(path)
    hosts.sort()
    t1 = collectors[collector]["target"]
    t2 = ",".join(hosts)
    if t1 != t2:
        collectors[collector]["target"] = t2
        updateCollector(collectors[collector])


def updatePolicy(policy):
    policy["id"] = policy["name"]
    data = json.dumps(policy)
    name = urllib.quote(policy["name"].encode('utf-8'))
    request = urllib2.Request(POLICY_UPDATE_URL + name,
                              data=data,
                              headers={"X-Supertoken": X_SUPERTOKEN})
    print urllib2.urlopen(request).read()


def mergePolicy(collector):
    hosts = []
    for path in cfg[collector]["path"]:
        hosts = hosts + getHosts(path)
    hosts.sort()

    request = urllib2.Request(POLICY_URL + collector,
                              headers={"X-Supertoken": X_SUPERTOKEN})
    contents = urllib2.urlopen(request).read()
    policys = json.loads(contents)
    for policy in policys:
        try:
            if policy["name"] not in cfg[collector]["policy_black_list"]:
                t1 = policy["target"]
                t2 = ",".join(hosts)
                if t1 != t2:
                    policy["target"] = t2
                    updatePolicy(policy)
        except Exception, err:
            print err


def getHosts(path):
    hosts = []
    path = urllib.quote(path.encode('utf-8'))
    url = PTREE_URL + path
    data = urllib2.urlopen(url).read()
    j = json.loads(data)
    for h in j["data"]:
        hosts.append(h["hostname"])
    return hosts


if __name__ == '__main__':
    for collector in collectors:
        if collector in cfg:
            mergeCollector(collector)
            mergePolicy(collector)
