#!/usr/bin/python

import re, os, time, sys

URL = 'http://localhost:3000/'
LOGIN = 'Tester'
PASSWORD = ''
TIMEOUT = 15

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Connect to Ojoj and test submissions.')
	parser.add_argument('url', metavar='url', default=URL, help='Ojoj root url')
	parser.add_argument('-l', '--login', metavar='login', default=LOGIN, help='Ojoj username allowed to test submissions')
	parser.add_argument('-p', '--password', metavar='password', default=PASSWORD, help='Ojoj user password')
	parser.add_argument('-t', '--timeout', metavar='timeout', default=TIMEOUT, help='Time to wait between requests', type=float)
	args = parser.parse_args()
	URL = args.url+('/' if not args.url.endswith('/') else '')
	LOGIN = args.login
	PASSWORD = args.password
	TIMEOUT = max( args.timeout, 0.0 )
	
BASEDIR, filename = os.path.split(os.path.abspath(__file__))

DATA_PATH = os.path.abspath(BASEDIR+'/../tasks')
TESTER_PATH = os.path.abspath(BASEDIR+'/../tester')
sys.path.append(TESTER_PATH)

from http import http
from tester import Test, AttributeDict


	
http(URL+'logout')
data = http(URL+'login')
token = re.search('<input name="authenticity_token" type="hidden" value="([^"]+)" />', data ).group(1)

http(URL+'login', [ ('commit', 'Login'), ('name', LOGIN), ('password', PASSWORD), ('authenticity_token', token) ] )

# test if everything is ok:
print 'Running. Asking for submissions...'


while True:
	data = http(URL+'tester_api_get').split('\n', 2)
	if data[0] == '-1':
		time.sleep(TIMEOUT)
		continue
		
	id = int(data[0])
	task_id = int(data[1])
	src = data[2]
	print 'Testing submission id %d' % id
	
	tests = []
	with open(DATA_PATH+'/%d/info' % task_id, 'r') as f:
		cpu, mem = map(int, f.readline().strip().split() )
		mem *= 1024
		test_names = f.readline().strip().split()
		for name in test_names:
			tests.append( (DATA_PATH+'/%d/%s.in' % (task_id, name), cpu, mem) )
	
	with open('/tmp/user-source.cpp', 'w') as f:
		f.write(src)
		
	params = {
		'tests': tests,
		'source': '/tmp/user-source.cpp',
		'lang': 'c++',
		'verify': './diff',
		'tmp': '/tmp'
	}
		
	print params 
	
	result = 6
	cpu = []
	mem = []
	
	for event in Test(params):
		event = AttributeDict(event)
		if event.event == 'ok':
			result = 0
		elif event.event == 'failure':
			result = {'WA': 1, 'TLE': 2, 'RE': 4, 'CE': 5, 'NZEC':7}.get( event.type, 6 )
		elif event.event == 'test-res':
			cpu.append( event.cpu )
			mem.append( event.mem )

	print 'Finished. Result = %d' % result
	if result != 0 or len(cpu) == 0 or len(mem) == 0:
		http(URL+'tester_api_set/%d/%d' % (id, result))
	else:
		cpu = int(1000*max(cpu))
		mem = max(mem)
		http(URL+'tester_api_set/%d/%d/%d/%d' % (id, result, cpu, mem) )

		
	
	
	
	