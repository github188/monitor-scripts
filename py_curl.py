#!/use/bin/env python
# coding:utf-8

import pycurl
import multiprocessing

def get_curl_result(c):
    data = dict()
    data["total"] = c.getinfo(pycurl.TOTAL_TIME)
    data["connect"] = c.getinfo(pycurl.CONNECT_TIME)
    data["nslookup"] = c.getinfo(pycurl.NAMELOOKUP_TIME)
    data["pre_transfer"] = c.getinfo(pycurl.PRETRANSFER_TIME)
    data["start_transfer"] = c.getinfo(pycurl.STARTTRANSFER_TIME)
    data["speed_download"] = c.getinfo(pycurl.SPEED_DOWNLOAD)
    data["download_size"] = c.getinfo(pycurl.SIZE_DOWNLOAD)
    data["redirect"] = c.getinfo(pycurl.REDIRECT_TIME)
    return data  


def main(num, urls):
    for url in urls:
        print "===URL:%s===" % url
        for i in xrange(num):
            data = dict()
            t = CurlTest()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEFUNCTION, t.callback)
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.TIMEOUT, 30)
            c.setopt(pycurl.USERAGENT, "chrome")
            try:
                c.perform()
            except Exception as e:
                print str(e)
            else:
                data = get_curl_result(c)
                print " ".join(["%s=%s" % (k, v) for k, v in data.items()])
            c.close()


class CurlTest(object):
    def __init__(self):
        self.contents = ""

    def callback(self, buf):
        self.contents += buf

if __name__ == "__main__":
    process = list()
    CONCURRENCY = 1
    REQUEST_NUM = 5
    URL = ["http://snaplock.wandoujia.com/api/v1/promotion?timestamp=0&f=roshan&v=4.1.0&vc=276&u=37ee921e660e44d9a13a43c429d7ad0a690ec7c5&ch=suoping_wdj_market"]
    #URL = "http://wdj.im/1n"
    for i in xrange(CONCURRENCY):
        p = multiprocessing.Process(target=main, args=(REQUEST_NUM, URL))
        p.start()
        process.append(p)
    for p in process:
        p.join()
