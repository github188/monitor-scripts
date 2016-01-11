#!/usr/bin/python
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
from datetime import datetime, timedelta
import json
import requests

ADMIN_IP = '10.0.12.231'
ADMIN_HOST = 'ipdp-hdr.cdn.wandoulabs.com'

PROVIDERS_APIKEYS = {
    'NC': 'ef7cb079e1',
    'CC': 'a53b12461a',
    'FW': '713d53c350',
    'DN': '1503b13b9b',
}


for provider, api_key in PROVIDERS_APIKEYS.items():
    data = {
        'user_name': provider,
        'api_key': api_key,
        'channel_name': ['medium'],
    }
    r = requests.post('http://%s/Api/Record/getList' %ADMIN_IP, data=json.dumps(data), headers={'host': ADMIN_HOST})

    records = json.loads(r.text)['records']
    #print records

    update_ts = sorted([str(record['update_ts']) for record in records['medium']])[0]
    update_dt = datetime.strptime(update_ts, '%Y-%m-%d %H:%M:%S')

    now = datetime.now()

    if now-update_dt > timedelta(minutes=10):
        print '%s的边缘节点已经很久未更新了, 最新更新时间%s' %(provider, update_ts)
        sys.exit(1)

print 'OK'
