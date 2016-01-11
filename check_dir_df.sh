#!/bin/bash

dir=$@

disk=`du -sk $dir 2>/dev/null | awk '{print $1}'`

if [ -z "$disk" ];then
    echo "$dir=0"
else
    echo "$dir=$disk"     
fi
