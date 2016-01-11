#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# qinguoan@wandoujia.com
# 2014-03-12
try:
    import os
    import re
    import sys
    import pprint
    from subprocess import Popen, PIPE
except ImportError, e:
    print os.path.abspath(__file__), str(e)
    exit(1)

#configuration
ActiveMQAdmin = '/home/work/activemq/bin/activemq-admin'




#analyze data  
QueueData = Popen('export JAVA_HOME=/usr/local/java6 &&'+ActiveMQAdmin+' \
            query -QQueue = *',shell=True,stderr=PIPE, stdout=PIPE, )
out, err = QueueData.communicate()

out = re.split('Connecting.*jmxrmi\n',out)[1].strip()

if out.find('ERROR') >=0:
    print "STATUS=1,ActiveMQ connect failed"
    exit(1)
elif not out:
    print "STATUS=2,no queue in ActiveMQ"
    out = ''
else:
    print "STATUS=0,ActiveMQ connect success"
out = [ i for i in out.split('\n\n') if i ]
result = dict()
for item in out:
    tmp = dict()
    data = [ re.sub('\s+','',i).split("=") for i in item.split('\n') if re.search('=',i) ]
    for x in data:
        tmp[x[0]] = x[1]
    if not tmp:continue
    QueueName = tmp['Name']
    result['['+QueueName+'][PendingMessage]'] = tmp['QueueSize']
    result['['+QueueName+'][ConsumerCount]'] = tmp['ConsumerCount']
    result['['+QueueName+'][MemoryPercentUsage]'] = tmp['MemoryPercentUsage']

for k,v in result.items():
    print "%s=%s" % (k,v)
