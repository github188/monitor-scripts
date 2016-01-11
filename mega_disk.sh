#!/bin/bash

#0:第10块盘:Other_Error=0

/home/op/pandora-client/script/mega_disk | while read i;do
echo $i;
echo $i | awk -F ':' '{print "optsdb:system.disk_"$3"|Adapter|"$1"|disk|"$2}' | sed 's/=/|/g,s/[第块盘]//g' | tr [A-Z] [a-z]
done
