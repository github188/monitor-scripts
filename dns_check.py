#!/usr/bin/python
# -*- encoding:utf-8 -*-
# zhouqiang@wandoujia.com
import subprocess

def get_dns_ip():
    ret = []
    ret.append("211.137.96.205")
    ret.append("183.221.253.100")
    return ret

def get_domain_and_expect_ip():
    ret = []
    ret.append({"domain":"account.wandoujia.com","expectips":["60.28.208.38"]})
    ret.append({"domain":"www.wandoujia.com","expectips":["211.152.118.11","60.28.208.18"]})
    return ret

def check_domain_by_dns(domain,dns_server,expectip):
    cmd = '''dig %s @%s +short +tries=1 +time=3''' % (domain,dns_server)
    code,stdout,stderr = shell(cmd)
    ip = stdout.strip()
    if not ip or ip not in expectip:
        return False
    return True

def get_detail(domain,dns_server):
    ret = []
    cmd = '''dig %s @%s +tries=1 +time=3''' % (domain,dns_server)
    code,stdout,stderr = shell(cmd)
    item = {"cmd":cmd,"code":code,"stdout":stdout,"stderr":stderr}
    ret.append(item)
    cmd = '''dig %s @%s +trace +tries=1 +time=3''' % (domain,dns_server)
    code,stdout,stderr = shell(cmd)
    item = {"cmd":cmd,"code":code,"stdout":stdout,"stderr":stderr}
    ret.append(item)
    return ret

def shell(cmd):
    process = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    std_out, std_err = process.communicate()
    return_code = process.poll()
    return return_code, std_out, std_err 

def main():
    dns_servers = get_dns_ip()
    domains = get_domain_and_expect_ip()
    ret = []
    for item in domains:
        for dns_server in dns_servers:
            domain = item["domain"]
            expectip = item["expectips"]
            if not check_domain_by_dns(domain,dns_server,expectip):
                ret.append(get_detail(domain,dns_server))
            else:
                pass
    if len(ret) > 0:
        print "status=FAIL, ",str(ret)
    else:
        print "status=OK"
if __name__ == "__main__":
    main()
