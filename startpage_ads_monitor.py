#!/usr/bin/python env
#-*- coding:utf-8 -*-

import sys
import re
import json
import urllib2

def getPatchPackageName(patch):

	sub_pn = []
	for sub_item in patch['sub_entity']:
		s = getPackageName(sub_item)
		sub_pn.append(s)
	return sub_pn


def getPackageName(patch):

	packageName = patch['detail']['app_detail']['package_name']
	return packageName


def checkAdsPackageName(patch, num):

	if len(patch) < num:
		print "STATUS=2,startpage广告位展现不足%s个" % num
		sys.exit(0)

	dupkey = []
	fullPatch = patch
	for key in fullPatch:
		if fullPatch.count(key) > 1:
			dupkey.append(key)

	if len(dupkey) > 1:
		print "STATUS=3,startpage广告位有重复展现"
		sys.exit(0)


def main():

	URL = [ ("http://startpage.wandoujia.com/five/v1/startpages?monitor=true&start=0&max=20&netStatus=WIFI&isIntroductio\
nShow=false&closedFeeds=&v=5.3.1&source=wandoujia_pc_wandoujia2_hom\
epage&launchedCount=5&entry=other&capacity=3&sectionItemNum=3&vc=8908&ch=wandoujia_pc_wandoujia2_homepage&sdk=17&\
channel=wandoujia_pc_wandoujia2_homepage&rippleSupported=true",6), ("http://startpage.wandoujia.com/five/v3/tabs/apps?\
v=10000&vc=5.4.1",3), ("http://startpage.wandoujia.com/five/v3/tabs/games?\
v=10000&vc=5.4.1&start=5",3) ]

	for key in URL:
		try:
			url = key[0]
			adsNum = key[1]
			f = urllib2.urlopen(url).read()
			data = json.loads(f)
		except Exception, e:
			print "STATUS=1,startpage广告接口访问失败"
			raise

		pn = []
		ps = []

		for item in data['entity']:
			#if item['title'] == u'这里是推广':
			try:
				if re.search(r'Ads', item['id_string'], re.IGNORECASE):
					ps = getPatchPackageName(item)
					pn += ps
			except:
				continue

		checkAdsPackageName(pn, adsNum)
	print "STATUS=0"

if __name__ == '__main__':
	main()
