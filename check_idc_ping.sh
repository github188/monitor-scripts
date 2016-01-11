#!/bin/bash
for dst in $@ 
do
    lost=`$(which ping) -f -c 2000 $dst|grep "transmitted"\
        |awk -F "," '{print $3}'|sed s#^[[:space:]]##`
    if [ "X$lost" != "X0% packet loss" ];then
        echo "status=FAIL, fping $dst $lost"
    else
        echo "status=OK, fping $dst $lost"
    fi
done
