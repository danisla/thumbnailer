#!/usr/bin/env python

'''
Python script to test thumbnail generation service using requests module.

Usage:
	pip install requests
	python service_test.py <src file> <dest thumbnail>

'''

import requests
import sys
import os

if len(sys.argv) != 3:
	print "USAGE: %s <input file> <output thumbnail>" % __file__
	sys.exit(-1)

src_path = sys.argv[1]
dest_path = sys.argv[2]

url = "http://localhost:8001/"
files = {'file': open(src_path, 'rb')}
r = requests.post(url, files=files, data={"thumbnail": "yes", "thumbnail_size": "500x500", "save_orig": "no"})

print "Response code: %d, content length: %d" % (r.status_code,len(r.content))
with open(dest_path,'wb') as f:
	f.write(r.content)

print "Saved %s" % dest_path