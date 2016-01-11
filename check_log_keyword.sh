#!/bin/bash

if [ $# -ne 3 ];then
    echo "STATUS=1, wrong parm"
    exit 1
fi

FILE=$1
KEY=$2
ALERT=$3

cnt=`grep "$KEY" $FILE -c`
if [ $cnt -ge $ALERT ];then
    echo "STATUS=2, $KEY more than $ALERT"
else
    echo "STATUS=0"
fi
