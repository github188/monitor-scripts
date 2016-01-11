#!/usr/bin/python2.6
import requests
def get_result(packageName):
    url = 'http://localhost:9583/cache/query?n=blockapp&k=' + packageName +'%23-2'
    try:
        response = requests.get(url,timeout=1)
        return response.text
    except Exception as e:
        raise e
def match_response(responseBody):
    if responseBody != '-2':
        return False
    return True
def get_package_names():
    f = open('/home/op/pandora-client/script/blockapps.txt','r')
    result = list()
    for line in f.readlines():
        line = line.strip()
        if not len(line):
            continue
        result.append(line)
    return result

def get_failed_packageNames():
    packagenames = get_package_names()
    fail_packages = []
    for packagename in packagenames:
        try:
            result = get_result(packagename)
            if not match_response(result):
                fail_packages.append(packagename)
        except Exception as e:
            fail_packages.append(packagename)
    return fail_packages
def main():
    fail_packages = get_failed_packageNames()
    if fail_packages:
        print "status=FAIL,packages:%s" % ",".join(fail_packages)
    else:
        print "status=OK"
if __name__ == "__main__":
    main()
