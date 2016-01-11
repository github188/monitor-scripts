#!/usr/bin/python 
import os
import re
import sys
import subprocess
import fcntl
import json

def ListFile( dir ):
	if not os.path.isdir( dir ):
		return []
	files = list()
	for file in os.listdir( dir ):
		file = dir + '/' + file
		if os.path.isfile( file ) or os.path.islink( file ):
			files.append( file )
	return files

def AnalyzeFile( file ):
	for line in open( file, 'r' ):
		m = re.match( '\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line )
		if m:
			return m.group(1)


class GetFlow( object ):
	def __init__( self, **info ):
		self.info = info
		self.data = dict()
	def calculate( self, out, port ):
		out = out.split( "\n" )
		data = list()
		for line in out:
			col = line.split()
			if len(col) != 7 or not re.search( '\d+',col[-1] ):
				continue
			( ip, rx, tx ) = ( col[1].split(':')[0], col[-2], col[-1] )
			if ip not in self.data:
				self.data[ip] = dict()
			print "%s:%s:in=%s" % ( ip, port, rx )
			print "%s:%s:out=%s" % ( ip, port, tx )
			if col[0] == 'TCP':
				break 


	def run( self, port ):
		for file in self.info:
			ip = self.info[file]
			worker = subprocess.Popen('/sbin/ipvsadm -L -t '+ip+':'+port+' --rate', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			out, err = worker.communicate()
			self.calculate( out, port )
		return self

def main():
	info = dict()
	confDir,port = sys.argv[1:]
	files = ListFile( confDir )
	for file in files:
		vip = AnalyzeFile( file )
		info[file] = vip
	gf = GetFlow( **info )
	gf.run(port)


if __name__ == "__main__":
	main()
