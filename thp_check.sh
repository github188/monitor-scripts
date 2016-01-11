#!/bin/bash

if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
   cat /sys/kernel/mm/transparent_hugepage/enabled | grep '\[never\]'
   if [ $? ! -eq 0 ];then
       exit 1
   fi
fi
if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
   cat /sys/kernel/mm/transparent_hugepage/defrag | grep '\[never\]'
   if [ $? ! -eq 0 ];then
       exit 1
   fi
fi
