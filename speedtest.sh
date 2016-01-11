#!/bin/bash
url="$1"
domain=$(echo $1 | cut -d/ -f3)
curl_timeout=20

output=$(curl -Ss -m "$curl_timeout" -w"optsdb:custom.http.time.namelookup|%{time_namelookup}|domain|$domain
optsdb:custom.http.time.connect|%{time_connect}|domain|$domain
optsdb:custom.http.time.appconnect|%{time_appconnect}|domain|$domain
optsdb:custom.http.time.total|%{time_total}|domain|$domain
" -o /dev/null "$url")

# success 0
# timeout 35
ec=$?
if [ $ec = 0 ]; then
    echo "$output"
else
    echo "optsdb:custom.http.time.total|$curl_timeout|domain|$domain"
    echo "optsdb:custom.http.timeout|1|domain|$domain"
fi
