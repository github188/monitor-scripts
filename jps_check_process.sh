#!/bin/bash

stdout=""
stderr=""
for process in $@
do
    jps  | grep "$process\>"  &>/dev/null
    ret=$?
    if [ $ret -eq 0 ];then
        echo "$process=OK,$process is running"
    else
        echo "$process=Fail,$process is not running"
    fi
done
