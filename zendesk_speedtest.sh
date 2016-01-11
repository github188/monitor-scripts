#!/bin/bash
url='https://androidfeedback.zendesk.com/api/v2/ticket_fields/23722073.json'
domain='androidfeedback.zendesk.com'
curl_timeout=20

output=$(curl -Ss -m "$curl_timeout" -w"optsdb:custom.http.time.namelookup|%{time_namelookup}|domain|$domain
optsdb:custom.http.time.connect|%{time_connect}|domain|$domain
optsdb:custom.http.time.appconnect|%{time_appconnect}|domain|$domain
optsdb:custom.http.time.total|%{time_total}|domain|$domain
" -o /dev/null -H 'Authorization: Basic cDNmZWVkYmFja0B3YW5kb3VqaWEuY29tOnAzZmVlZGJhY2s=' "$url")

# success 0
# timeout 35
ec=$?
if [ $ec = 0 ]; then
    echo "$output"
else
    echo "optsdb:custom.http.time.total|$curl_timeout|domain|$domain"
    echo "optsdb:custom.http.timeout|1|domain|$domain"
fi
