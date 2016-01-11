#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import subprocess

class Memory(object):

    def __init__(self, process_name):
        self.pid = ""
        self.rss = ""
        self.get_pid_cmd = "ps -ef|grep %s|grep java|grep -v grep|awk \'{print $2}\'" %(process_name)

    def __getprocessPid(self):
        p = subprocess.Popen(self.get_pid_cmd, stdout=subprocess.PIPE, shell=True)
        (self.pid, err) = p.communicate()
        self.pid = self.pid.strip()
        self.get_rss_cmd = "ps axo pid,rss|grep %s|grep -v grep|awk \'{print $2}\'" %(self.pid)

    def __getprocessRss(self):
        p = subprocess.Popen(self.get_rss_cmd, stdout=subprocess.PIPE, shell=True)
        (self.rss, err) = p.communicate()
        self.rss = self.rss.strip()

    def get_process_memory(self):
        self.__getprocessPid()
        self.__getprocessRss()

        return self.rss

    def print_optsdb_format(self):
        print "optsdb:%s.rss|%s" %(process_name, self.rss)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit(1)

    process_name = sys.argv[1].strip()
    m = Memory(process_name)
    print "rss=",m.get_process_memory()
    m.print_optsdb_format()
