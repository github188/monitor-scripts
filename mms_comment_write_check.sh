#!/bin/bash
#
# qinguoan@wandoujia.com
# 2013-03-18
#
#
#

function help
{
    echo $0 -f "lofgile" -m "partern"
}


if [ $# -lt 1 ];then
    echo "STATUS=1,need args to run"
    exit 1
fi


if [ -z $freq ];then
    freq=1
fi

if [ -z $logfile ];then
    logfile="/home/work/tomcat/logs/mms-web.log"
fi

if [ -z $info ];then
    info="日志中有评论提交错误"
fi

past=`date -d "1 mins ago" +"%m\/%d %H:%M"`
current=`date +"%m\/%d %H:%M"`

if [ ! -f "$logfile" ];then
    echo "STATUS=2,log file isn't exist"
    exit 1
else
    regex=$@
    awk "/$past/,/$current/" $logfile 2>/dev/null | egrep -m 1 "$regex" &>/dev/null
    if [ $? -eq 0 ];then
        echo "STATUS=4,$info"
    else
        echo "STATUS=0,catalina.out content ok"
    fi
fi
