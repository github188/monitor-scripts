#!/bin/bash
#
# for start page to check errors in log
# qinguoan@wandoujia.com 2014-05-29
# 

log_prefix="/home/work/install-star-server/logs/star-request.log"
log_suffix=$(date +'%Y_%m_%d')
log_file="${log_prefix}.${log_suffix}"
curtime=$(date -d '1 mins ago' +%d/%B/%Y:%H:%M) 

grep $curtime $log_file | awk '{print $9}'|sort -n |awk \
'BEGIN{HTTP_CODE_500=0}{if($1==500)HTTP_CODE_500 += 1}END{print "HTTP_CODE_500="HTTP_CODE_500}' 
