#!/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import string
import shutil
import urllib
import urllib2
import json
import subprocess

import requests


GIT_BASE_DIR = "/tmp/" + os.path.basename(sys.argv[0])
GIT_CLONE_CMD = "git clone --depth=1 ssh://liningning@git.wandoujia.com:29418/nginx_cfg_level2.git"
GIT_PROJECT_DIR = "nginx_cfg_level2" 

ACCESS_HOST = "access.hy01.wandoujia.com"

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='%(message)s')


class HTTPRequestClass(object):
    def __init__(self, host_url=ACCESS_HOST):
        self.host_url = host_url

    def post_wrapper(self, url, data_dict):
        data = urllib.urlencode(data_dict)
        visit_url = r"http://" + self.host_url + r"/" + url

        request = urllib2.Request(visit_url, data)
        login_response = urllib2.urlopen(request)
        response = login_response.read()
        ret_dict = json.loads(response)

        return ret_dict

    def get_wrapper(self, url, data_dict):
        data = urllib.urlencode(data_dict)
        visit_url = r"http://" + self.host_url + r"/" + url

        request = urllib2.Request(visit_url + "?" + data)
        login_response = urllib2.urlopen(request)
        response = login_response.read()
        ret_dict = json.loads(response)

        return ret_dict

    def put_wrapper(self, url, data_dict):
        data = urllib.urlencode(data_dict)
        visit_url = r"http://" + self.host_url + r"/" + url

        request = urllib2.Request(visit_url, data)
        request.get_method = lambda: 'PUT'
        login_response = urllib2.urlopen(request)
        response = login_response.read()
        ret_dict = json.loads(response)

        return ret_dict

    def delete_wrapper(self, url, data_dict):
        data = urllib.urlencode(data_dict)
        visit_url = r"http://" + self.host_url + r"/" + url

        request = urllib2.Request(visit_url + "?" + data)
        request.get_method = lambda: 'DELETE'
        login_response = urllib2.urlopen(request)
        response = login_response.read()
        ret_dict = json.loads(response)

        return ret_dict

    def patch_wrapper(self, url, data_dict):
        data = urllib.urlencode(data_dict)
        visit_url = r"http://" + self.host_url + r"/" + url

        request = urllib2.Request(visit_url + "?" + data)
        request.get_method = lambda: 'PATCH'
        login_response = urllib2.urlopen(request)
        response = login_response.read()
        ret_dict = json.loads(response)

        return ret_dict


def delete(name):
    request_oj = HTTPRequestClass()
    uri = "api/v1/nginx/upstreams/%s" % name
    ret = request_oj.delete_wrapper(uri, {})
    return ret


def shell(cmd):
    process = subprocess.Popen(args=cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
    std_out, std_err = process.communicate()
    return_code = process.poll()
    return return_code, std_out, std_err


def _shell(cmd, _exit=1):
    rc , so, se = shell(cmd)
    if rc == 0:
        message = "cmd:%s" % cmd
        logging.info(message)
        return so.strip()
    else:
        message = "cmd:%s, stdout:%s, error:%s" % (cmd, so, se)
        logging.error(message)
        if _exit == 1:
            sys.exit(1)
        else:
            return False


###

import email
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.header import Header

SMTP_HOST = 'mx.hy01.wandoujia.com'
SMTP_PORT = 25
CONT_MAIL_LIST = [
    'liningning@wandoujia.com',
    'sre-team@wandoujia.com',
    'ep-robots@wandoujia.com'
]

def sanitize_subject(subject):
    try:
        subject.decode('ascii')
    except UnicodeEncodeError:
        pass
    except UnicodeDecodeError:
        subject = Header(subject, 'utf-8')
    return subject

# Assuming send_mail() is intended for scripting usage, only Subject is sanitzed here.
# Also, the sanitzation procedure for other Headers is far too complicated.

def mail(mailto, subject, content):
    mail_from = 'noreply@wandoujia.com'
    mail_cc = None
    mail_body_type = 'html'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = sanitize_subject(subject)
    msg['From'] = mail_from
    # assert(isinstance(mailto, list))

    if isinstance(mailto, list):
        mailto.extend(CONT_MAIL_LIST)
        msg['To'] = ', '.join(mailto)
    elif mailto is None or mailto == "None":
        mailto = CONT_MAIL_LIST
        msg['To'] = ", ".join(CONT_MAIL_LIST)
    elif isinstance(mailto, str) or isinstance(mailto, unicode):
        msg['To'] = ", ".join(CONT_MAIL_LIST) + ", " + mailto
    else:
        mailto = CONT_MAIL_LIST
        msg['To'] = ", ".join(CONT_MAIL_LIST)

    if mail_cc is not None:
        assert(isinstance(mail_cc, list))
        msg['Cc'] = ', '.join(mail_cc)
    body = MIMEText(content, mail_body_type, 'utf-8')
    msg.attach(body)
    smtp = smtplib.SMTP()
    smtp.connect(SMTP_HOST, SMTP_PORT)
    smtp.sendmail(mail_from, mailto, msg.as_string())


def main():
    deleted = []

    url = "http://access.hy01.wandoujia.com/api/v1/nginx/upstreams"
    ret = requests.get(url).json()
    
    offlines = [i["name"] for i in ret if i["online"] == 0]
    logging.info("offline upstream nodes:%s" % offlines)
    for u in offlines:
        delete(u)
        logging.info("%s deleted" % u)
    deleted.extend(offlines)

    _dir = os.path.join(GIT_BASE_DIR, GIT_PROJECT_DIR)
    shutil.rmtree(_dir)
    if not os.path.isdir(GIT_BASE_DIR):
        os.makedirs(GIT_BASE_DIR)
    cmd = "cd {0} && {1}".format(GIT_BASE_DIR, GIT_CLONE_CMD)
    _shell(cmd)

    onlines = [i["name"] for i in ret if i["online"] == 1]
    for o in onlines:
        cmd = "cd {0} && egrep -ri 'http://{1}|https://{2}' * ".format(_dir, o, o)
        if not  _shell(cmd, _exit=0):
            delete(o)
            logging.info("%s deleted" % o) 
            deleted.append(o)
    logging.info("%s deleted" % deleted)
   
    if deleted == []:
        return

    subject = "[SRE]有不在使用的 upstream node 被删除"
    content = u"""如下 upstream node 未在使用, 已从 Nginx upstream node 数据库中删除 .<br/><br/>
    """
    for d in deleted:
        content += u"""%s <br/><br/>""" % d
 
    mail(None, subject, content)
    logging.info("mail sended")


if __name__ == "__main__":
    main()
