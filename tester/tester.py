#!/usr/bin/python

import os.path, subprocess

BASEDIR, filename = os.path.split(os.path.abspath(__file__))

class MissingFile(Exception):
	pass

JUDGE_CODES = {1: 'TLE', 3: 'RE', 4: 'NZEC'}

class AttributeDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def Test(args):
	if isinstance(args, dict):
		args = AttributeDict(args)
		
	if args.verify[0] == '.':
		args.verify = BASEDIR+args.verify[1:]

	with open('/dev/null', 'w') as nullfd:
		if not os.path.isdir(args.tmp):
			raise MissingFile('Invalid temporary directory: '+args.tmp)

		yield { 'event': 'compilation' }


		compiler = BASEDIR+'/languages/'+args.lang+'.lang'
		if not os.path.isfile(compiler):
			raise MissingFile('Compiler file is missing: ' + compiler)

		if not os.path.isfile(args.source):
			raise MissingFile('Source file is missing: ' + args.source)
	
		with open(args.tmp+'/tester-compiler-output', 'w') as output:
			compiled = subprocess.call( [ compiler, args.source, args.tmp+'/tester-user-app' ], stdout = output, stderr = output )
		
		if compiled != 0:
			yield { 'event': 'failure', 'type': 'CE' }
			return

		yield { 'event': 'compilation-ok' }

		for path, cpu, mem in args.tests:
			if path[-3:] == '.in':
				path = path[:-3]

			yield { 'event': 'test-running', 'name': path.split('/')[-1], 'cpu':cpu, 'mem':mem }

			if not os.path.isfile(path+'.in'):
				raise MissingFile('Test file is missing: ' + path)

			with open(args.tmp+'/tester-judge-output', 'w') as output:
				app = [ BASEDIR+'/ojoj_judge', args.tmp+'/tester-user-app', str(cpu), str(mem), path+'.in', args.tmp+'/tester-user-output' ]
				status = subprocess.call( app, stdout = output, stderr = nullfd )

			if status != 0:
				yield { 'event': 'test-failure', 'type': JUDGE_CODES.get(status, 'ERROR') }
				yield { 'event': 'failure', 'type': JUDGE_CODES.get(status, 'ERROR') }
				return
	
			cpu, mem = open(args.tmp+'/tester-judge-output').read().split()
			cpu = float(cpu)
			mem = int(mem)
			yield { 'event': 'test-res', 'cpu':cpu, 'mem': mem }

		
			status = subprocess.call( [args.verify, args.tmp+'/tester-user-output', path], stdout = nullfd, stderr = nullfd )
			if status != 0:
				yield { 'event': 'test-failure', 'type': 'WA' }
				yield { 'event': 'failure', 'type': 'WA' }
				return
			yield { 'event': 'test-ok'}

		yield { 'event': 'ok' }
	

if __name__ == '__main__':
	import argparse
	from sys import stdout

	parser = argparse.ArgumentParser(description='Compile, run and verify code.')
	parser.add_argument('source', metavar='source-path', help='source code to compile')
	parser.add_argument('--lang', metavar='language', default="c++", help='compiler name [default c++]')
	parser.add_argument('--verify', metavar='verify-path', default="./diff", help='application verifying output [default ./diff]')
	parser.add_argument('--tmp', metavar='tmp-path', default="/tmp", help='temporary directory [default /tmp]')
	parser.add_argument('tests', metavar='test-path', nargs='*', help='(test input .in file):(cpu limit[s]):(mem limit[MB])')
	args = parser.parse_args()
	args.tests = map(lambda x : x.split(':'), args.tests)
	args.tests = map(lambda x : (x[0], x[1] if len(x) > 1 else 15, x[2] if len(x) > 2 else 256), args.tests)
	args.tests = map(lambda (path,cpu,mem) : (path,float(cpu), int(round(float(mem)*1024))), args.tests)

#	print args
	try:
#		0.1s / 5s
#		print '+-------------+
		for event in Test(args):
			event = AttributeDict(event)
			if event.event == 'compilation':
				stdout.write('+-------------+--------+\n')
				stdout.write('| Compilation |        |')
				stdout.flush()
			if event.event == 'failure' and event.type == 'CE':
				stdout.write('\b\b\b\b\b\b\b\b\b\033[31m Failed \033[0m|\n')
				stdout.write('+-------------+--------+\n')
				os.system('cat '+args.tmp+'/tester-compiler-output')
			if event.event == 'compilation-ok':
				stdout.write('\b\b\b\b\b\b\b\b\b\033[32m   OK   \033[0m|\n')
				stdout.write('+----------------------+-----------------+-----------------+--------+\n')
			if event.event == 'test-running':
				name = event.name[:15]
				kcpu = event.mem < 10000
				cpu = '%.1fs' % event.cpu if event.cpu < 5 else str(int(event.cpu))+'s'
				mem = '%dK' % event.mem if kcpu else '%dM' % int(event.mem/1024)
				if len(name) < 15: name += ' '*(15-len(name))
				if len(cpu) < 5: cpu += ' '*(5-len(cpu))
				if len(mem) < 5: mem += ' '*(5-len(mem))
				stdout.write('| Test %15s |        / %5s  |        / %5s  |        |' % (name, cpu, mem))
				stdout.flush()
			if event.event == 'test-failure':
				stdout.write('\b'*45 + '      - / %5s  |      - / %5s  |  \033[31m%4s\033[0m  |\n' % (cpu, mem, event.type))
				stdout.write('+----------------------+-----------------+-----------------+--------+\n')
			if event.event == 'test-res':
				ucpu = '%.1fs' % event.cpu if event.cpu < 5 else str(int(event.cpu))+'s'
				umem = '%dK' % event.mem if kcpu else '%dM' % int(event.mem/1024)
				stdout.write('\b'*45 + '  %5s / %5s  |  %5s / %5s  |        |' % (ucpu, cpu, umem, mem))
				stdout.flush()
			if event.event == 'test-ok':
				stdout.write('\b'*9 + '  \033[32mOK\033[0m    |\n')
				stdout.write('+----------------------+-----------------+-----------------+--------+\n')
			if event.event == 'ok':
				stdout.write('|   Overall   |   \033[32mOK\033[0m   |\n')
				stdout.write('+-------------+--------+\n')
			if event.event == 'failure':
				stdout.write('|   Overall   |  \033[31m%4s\033[0m  |\n' % event.type)
				stdout.write('+-------------+--------+\n')

	except MissingFile as e:
		print '\033[31m'+e.message+'\033[0m'
	
