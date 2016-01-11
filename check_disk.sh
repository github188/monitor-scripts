#!/bin/bash
# Author: liningning@wandoujia.com
# Created Time:09/12/13 13:29:14

data=`date`
part=`cat /proc/mounts |egrep -v "rootfs|proc|sysfs|devtmpfs|devpts|tmpfs|root" |grep /dev/ |awk '{print $2}'`


for i in $part
do
    if ! echo $date > $i/.fsro
    then
        echo "[文件系统只读检测] $i 分区写入失败."
        exit 3
    fi
done

echo "[文件系统只读检测] 所有分区均能写入."
exit 0
