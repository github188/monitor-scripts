#!/bin/bash
# qinguoan@wandoujia.com
# 2014-05-29
CUR_PATH=$(cd `dirname $0`; pwd)
LOG_DIR="/home/work/logs"
DEBUG=1
LOG="$CUR_PATH/compress.log"

function print
{
    local info=$1
    local level=$2
    if [ -z "$level" ];then
        level="INFO"
    elif [ $level -eq 1 ];then
        level="ERROR"
    elif [ $level -eq 0 ];then
        level="INFO"
    fi
    current=$(date +'%Y-%m-%d %H:%M:%S')
    [ ! -f $LOG ] && [ -n "`touch $LOG >/dev/null`" ] && exit 1
    [ $DEBUG -eq 1 ] && echo -e "$current * $level * $info"
    echo -e "$current * $level * $info" >> $LOG || exit 1

}

LOG_FILE=$(find $LOG_DIR -maxdepth 1 -mmin +600 -type f -name "*.log*" | grep -v '\.gz$' | xargs)
print "totalfile: $LOG_FILE"
for file in $LOG_FILE
do
    for((i=0;i<3;i++))
    do
        nice -19 gzip $file &>/dev/null
        if [ $? -eq 0 ];then
            print "$file gzip success"
            break
        elif [ $? -eq 2 ];then
            print "$file gzip failed"  1
        else
            sleep 60
        fi
    done
done

sleep 1 && sync

print "finish gzip all files."

print "start to delete old files"

OLD_LOG=$(find $LOG_DIR -maxdepth 1 -mtime +15 -type f -name "*.log*" | xargs)
for file in $OLD_LOG
do
    nice -19 rm -f $file &>/dev/null
    sleep 1
done
