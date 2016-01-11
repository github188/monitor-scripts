#!/bin/env python
#-*- coding: utf-8 -*-
# 监控 api.snappea.com 在 loki 中的曲线

import requests


def main():
    url = "http://loki.hy01.internal.wandoujia.com/tsdb/api/query?type=domain&start=1h-ago&m=sum:10m-avg:url.responsetime{domain=api.snappea.com,path=*}"
    try:
        data = requests.get(url).json()
        if len(data["data"][0]["data"]) < 3:
            return "STATUS=1, api.snappea.com no data in opentsdb"
        else:
            return "STATUS=0, api.snappea.com is normal."
    except:
        return "STATUS=1, api.snappea.com no data in opentsdb"


if __name__ == "__main__":
    print main()
