#!/use/bin/env python
# coding:utf-8

import pycurl
import smtplib
import multiprocessing
import re
import subprocess
import os
import time

def get_curl_result(c):
    data = dict()
    data["total_time"] = c.getinfo(pycurl.TOTAL_TIME)
    data["connect_time"] = c.getinfo(pycurl.CONNECT_TIME)
    data["namelookup_time"] = c.getinfo(pycurl.NAMELOOKUP_TIME)
    data["pre_transfer_time"] = c.getinfo(pycurl.PRETRANSFER_TIME)
    data["start_transfer_time"] = c.getinfo(pycurl.STARTTRANSFER_TIME)
    data["speed_download"] = c.getinfo(pycurl.SPEED_DOWNLOAD)
    data["download_size"] = c.getinfo(pycurl.SIZE_DOWNLOAD)    
    data["http_code"] = c.getinfo(pycurl.HTTP_CODE)    
    return data  


def main(url, out_queue):
    data = dict()
    t = CurlTest()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.FOLLOWLOCATION, True)
    c.setopt(c.WRITEFUNCTION, t.callback)
    c.setopt(c.TIMEOUT, 30)
    #c.setopt(pycurl.USERAGENT, "guoan_12131349")
    try:
        c.perform()
    except Exception as e:
        print "%s=ERROR, curl failed" % url
    else:
        data = get_curl_result(c)
        #print url, " ".join(["%s=%s" % (k, v) for k, v in data.items()])
        code = data["http_code"]
        ret = list()
        if code != 200:
            ret = ["ERROR", url]
        else:
            ret = ["OK", url]
        out_queue.put(ret)
    c.close()


class CurlTest(object):
    def __init__(self):
        self.contents = ""

    def callback(self, buf):
        self.contents += buf

if __name__ == "__main__":
    # CELLS = ["15901553737","18611088383","13811416649","13911870720","15652718887"]
    CELLS = [ 15652718887]
    process = list()
    CONCURRENCY = 20
    REQUEST_NUM = 50
    out_queue = multiprocessing.Queue()
    URL = ["http://www.google.com", "http://www.youtube.com", "https://www.google.com", "https://www.youtube.com"] 
    for i in URL:
        p = multiprocessing.Process(target=main, args=(i, out_queue))
        p.start()
        process.append(p)
    for p in process:
        p.join()
    result = dict()
    for i in xrange(4):
        tmp = out_queue.get()
        if tmp[0] not in result:
            result[tmp[0]] = list()
        result[tmp[0]].append(tmp[1])
    current = time.strftime("%T", time.localtime())
    if "OK" in result:
        warn = "专线异常,%s 无法正常访问 [%s]" % (",".join(result["OK"]), current)
        for cell in CELLS:
            cmd = "./wdsms -user %s -pass %s %d \"%s\"" % ("sre", "MYNqvSOEfsrbPChJ", cell, warn)
            subprocess.Popen(cmd, shell=True)
        subprocess.Popen("touch failed", shell=True)
    else:
        if os.path.isfile("failed"):
            os.unlink("failed")
            warn = "专线恢复正常,%s 可以正常访问 [%s]" % (",".join(result["OK"]), current)
            for cell in CELLS:
                cmd = "./wdsms -user %s -pass %s %d \"%s\"" % ("sre", "MYNqvSOEfsrbPChJ", cell, warn)
                subprocess.Popen(cmd, shell=True)

