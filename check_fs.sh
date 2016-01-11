#!/bin/bash

FS_CHECK_FILE=fs_check.$$

checkHang(){
    HANG=`ps aux | grep '/bin/ls' | wc -l`
    if [ ${HANG} -gt 1 ];then
        echo "system.disk_fs:ls=HANG"
    fi

    HANG=`ps aux | grep '/bin/touch' | wc -l`
    if [ ${HANG} -gt 1 ];then
        echo "system.disk_fs:touch=HANG"
    fi
}

checkHang

cat /proc/mounts |egrep -v "boot|rootfs|proc|sysfs|devtmpfs|devpts|tmpfs|root" |grep /dev/ |awk '{print $2}' | while read PATH; do
    /bin/ls ${PATH} >/dev/null 2>&1 || echo "system.fs_error:ls="${PATH} || break
done

cat /proc/mounts |egrep -v "boot|rootfs|proc|sysfs|devtmpfs|devpts|tmpfs|root" |grep /dev/ |awk '{print $2}' | while read PATH; do
     /bin/touch ${PATH}/${FS_CHECK_FILE} >/dev/null 2>&1 || echo "system.fs_error:touch="${PATH} || break
done

cat /proc/mounts |egrep -v "boot|rootfs|proc|sysfs|devtmpfs|devpts|tmpfs|root" |grep /dev/ |awk '{print $2}' | while read PATH; do
    /bin/rm -f ${PATH}/${FS_CHECK_FILE} >/dev/null 2>&1
done
