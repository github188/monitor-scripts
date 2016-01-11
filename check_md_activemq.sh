#!/bin/bash

export JAVA_HOME=/usr/local/java6

queueName=(adnetworkClickQueue adnetworkImpressionQueue asyncTask callBack clickQueue impressionQueue)

for i in ${queueName[@]}
do
        queueSize=`/home/work/apache-activemq-*/bin/activemq-admin query -QQueue=$i | grep 'QueueSize' | awk -F' = ' '{print $2}'`
        echo $i=$queueSize
done
