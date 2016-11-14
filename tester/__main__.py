
import argparse
from sys import stdout
import os.path

from task import Task, _make_test
import tester, events
from tester import OjojCodes

#diff = '~/diff {{out}} {}.out'
diff = 'python3 ~/decimal_diff.py -v {{out}} {}.out'

def create_test(arg):
    path = arg.split(':')[0]
    id = os.path.basename(path).split('.')[0]
    ret = {
        'id': id,
        'verify': diff.format(path[:-3]),
        'memory': '512M',
        'cpu': '10s',
        'input': path
    }
    
    _make_test(ret)
    return ret

def create_task(args):
    if len(args.tests) == 1:
        path = args.tests[0]
        if os.path.basename(path) == 'task.xml':
            print('Loading xml task...')
            return Task.from_xml(path)
        if os.path.basename(path) == 'info':
            print('Loading legacy "info" task...')
            return Task.from_info(path)
    
    task = Task()
    task.id = task.name = 'unknown'
    task.task_dir = args.tmp
    task.tests = [create_test(t) for t in args.tests]
    return task
            
event_handlers = {}
def event(type):
    def decorator(handler):
        event_handlers[type] = handler
        return handler
    return decorator
    
def cpu_to_str(cpu):
    return str(cpu)[:4]+'s'
    
def mem_to_str(mem):
    return '{}M'.format(mem//1024)

colors = {'red': '\033[31m', 'green': '\033[32m', 'none': '\033[0m'}
    
               
parser = argparse.ArgumentParser(description='Compile, run and verify code.')
parser.add_argument('source', metavar='source-path', help='source code to compile')
parser.add_argument('--lang', metavar='language', default="c++", help='compiler name [default c++]')
parser.add_argument('--verify', metavar='verify-path', default="./diff", help='application verifying output [default ./diff]')
parser.add_argument('--tmp', metavar='tmp-path', default="/tmp", help='temporary directory [default /tmp]')
parser.add_argument('--all', dest='all', action='store_true')
parser.set_defaults(feature=True)
parser.add_argument('tests', metavar='test-path', nargs='*', help='Each test should have format: <test input .in file>[:cpu limit(s)[:(mem limit(MB)]]. You can also provide single "task.xml" or "info" file.')
args = parser.parse_args()

task = create_task(args)

state = None

@event(events.Compiling)
def compiling_handler(event):
    stdout.write('+-------------+--------+\n')
    stdout.write('| Compilation |        |')
    stdout.flush()
    state = 'compiling'
    
@event(events.Compiled)
def compiled_handler(event):
    stdout.write(9*'\b'+'   {green}OK{none}   |\n'.format(**colors))
    stdout.write('+----------------------+-----------------+-----------------+--------+\n')
    state = None
    
@event(events.TestRunning)
def test_running_handler(event):
    global state
    id = event.id[:20]
    state = (cpu_to_str(event.cpu_limit), mem_to_str(event.mem_limit), '    -', '    -')
    stdout.write('| {:20s} |        / {:5s}  |        / {:5s}  |        |'.format(id, state[0], state[1]))
    stdout.flush()
    
@event(events.TestFailure)
def test_failure_handler(event):
    stdout.write('\b'*45 + '  {3:5s} / {1:5s}  |  {4:5s} / {2:5s}  |  {red}{0:4s}{none}  |\n'.format(OjojCodes.short(event.code), *state, **colors))
    stdout.write('+----------------------+-----------------+-----------------+--------+\n')
    
@event(events.TestResources)
def test_failure_handler(event):
    global state
    cpu_limit, mem_limit, _, _ = state
    state = (cpu_limit, mem_limit, cpu_to_str(event.cpu), mem_to_str(event.mem))
    stdout.write('\b'*45 + '  {2:5s} / {0:5s}  |  {3:5s} / {1:5s}  |        |'.format(*state))
    
@event(events.Failure)
def failure_handler(event):
    if state == 'compiling':
        stdout.write(9*'\b'+' {red}Failed{none} |\n')
        stdout.write('+-------------+--------+\n')
    else:
        stdout.write('|   Overall   |  {red}{:4s}{none}  |\n'.format(OjojCodes.short(event.code), **colors))
        stdout.write('+-------------+--------+\n')

@event(events.TestOk)
def test_ok_handler(event):
    stdout.write('\b'*9 + '   {green}{:2s}{none}   |\n'.format(OjojCodes.short(OjojCodes.AC), **colors))
    stdout.write('+----------------------+-----------------+-----------------+--------+\n')
        
@event(events.Accepted)
def accepted_handler(event):
    stdout.write('|   Overall   |   {green}{:2s}{none}   |\n'.format(OjojCodes.short(OjojCodes.AC), **colors))
    stdout.write('+-------------+--------+\n')
    
def default_handler(event):
    print(event)

compiler = tester.languages[args.lang]
for event in tester.flow(compiler, args.source, task, {'tmp_dir': args.tmp, 'test_all': args.all}):
    handler = event_handlers.get(event.__class__, default_handler)
    handler(event)
     

"""
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
            
        if event.event == 'failure' and event.type == 'CE':

        if event.event == 'compilation-ok':
            
        if event.event == 'test-running':
            
        if event.event == 'test-failure':

        if event.event == 'test-res':
            ucpu = '%.1fs' % event.cpu if event.cpu < 5 else str(int(event.cpu))+'s'
            umem = '%dK' % event.mem if kcpu else '%dM' % int(event.mem/1024)
            stdout.write('\b'*45 + '  %5s / %5s  |  %5s / %5s  |        |' % (ucpu, cpu, umem, mem))
            stdout.flush()
        if event.event == 'test-ok':

        if event.event == 'ok':

        if event.event == 'failure':


except MissingFile as e:
    print '\033[31m'+e.message+'\033[0m'"""