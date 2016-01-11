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


args = sys.argv[1]

#analyze data  
QueueData = Popen('export JAVA_HOME=/usr/local/java6 &&'+ActiveMQAdmin+' \
            query -QTopic='+args+' --view PendingQueueSize,ConnectionId,Name,ConsumerCount',\
            shell=True,stderr=PIPE, stdout=PIPE, )
out, err = QueueData.communicate()

out = re.split('Connecting.*jmxrmi\n',out)[1].strip()
if out.find('ERROR') >=0:
    print "STATUS=1,ActiveMQ connect failed"
    exit(1)
elif not out:
    print "STATUS=2,no queue in ActiveMQ"
else:
    print "STATUS=0,ActiveMQ connect success"
out = [ i for i in out.split('\n\n') if i ]

pendingNumber = -1
pendingHost = ''

for item in out:
    tmp = dict()
    data = [ re.sub('\s+','',i).split("=") for i in item.split('\n') if re.search('=',i) ]
    #print data
    for x in data:
        tmp[x[0]] = x[1]
    if not tmp:
        continue
    else:
        if 'ConnectionId' in tmp and tmp['PendingQueueSize'] >= pendingNumber:
                pendingNumber =  tmp['PendingQueueSize']
                pendingHost = re.search('ID:(.*?\..*?)[\.-].*',tmp['ConnectionId']).groups(0)[0]
        elif 'Name' in tmp:
                print "[%s][ConsumerCount]=%s" % (tmp['Name'],tmp['ConsumerCount'])
print "[%s][PendingMessage]=%s,%s" % (args, pendingNumber, pendingHost)
