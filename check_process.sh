#!/bin/bash

stdout=""
stderr=""
for process in $@
do
    ps aux | grep "$process\>" | egrep -v "grep|$0.*$process"  &>/dev/null
    ret=$?
    if [ $ret -eq 0 ];then
        echo "$process=OK,$process is running"
    else
        echo "$process=Fail,$process is not running"
    fi
done
