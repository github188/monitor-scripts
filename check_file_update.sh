#!/bin/bash

FILE=$1


if [ ! -f $FILE ];then
    echo "STATUS=2, $FILE not exist!"
    exit 1
fi

modify=`date -r $FILE +%s`
current=`date +%s`

pass_time=`expr $current - $modify`

if [ $pass_time -ge 600 ];then
    echo "STATUS=1, $FILE 600 秒未更新"
else
    echo "STATUS=0"
fi
