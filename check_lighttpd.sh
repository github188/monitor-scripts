#!/bin/bash


status=`curl -o /dev/null -w %{http_code} http://127.0.0.1:1023/`

if [ $status -eq 200 ];then
    echo "lighttpd=OK, curl return code is $status"
else
    echo "lighttpd=Fail, curl return code is $status"
fi

