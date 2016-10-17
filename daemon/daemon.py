#!/usr/bin/python

import re, os, time, sys
from collections import Counter
from api import Api

BASEDIR, filename = os.path.split(os.path.abspath(__file__))
TESTER_PATH = os.path.abspath(BASEDIR+'/../tester')
sys.path.append(TESTER_PATH)

class Paths:
    user_source = '{tmp_dir}/ojoj-user-source{ext}'

import tester, data, events
from task import Task

config = data.load_xml('ojoj.daemon.config', sys.argv[1])

if config.get('web.password') is None:
    import getpass
    config['web.password'] = getpass.getpass()
    
tasks = []


for tasks_directory in config.get_list('tasks'):
    for directory, _, files in os.walk(tasks_directory):
        if 'task.xml' in files:
            tasks.append((Task.from_xml, os.path.join(directory, 'task.xml')))
        if 'info' in files:
            tasks.append((Task.from_info, os.path.join(directory, 'info')))
            
print('Collected {} tasks. Loading...'.format(len(tasks)))
            
for i, task_pair in enumerate(tasks):
    loader, task = task_pair
    task = loader(task)
    tasks[i] = task
    print('Loaded "{}" [id: {}].'.format(task.name, task.id))
    
print('Loaded all.'.format(task.name, task.id))
    
counter = Counter(t.id for t in tasks)
counter -= Counter(id for id in counter)
if counter:
    raise Exception('Following tasks have colliding id: "{}"'.format('", "'.join(id for id in counter)))

tasks = {task.id: task for task in tasks}


api = Api(config)
report_waiting = True

class C: pass
c = C()
c.id = 170
api.clear(c)

while True:
    sub = api.get()
    if sub is None:
        if report_waiting:
            report_waiting = False
            print('No more submissions. Waiting...')
        time.sleep(float(config['web.interval']))
        continue
        
    report_waiting = True
    task = tasks.get(sub.task, None)
    lang = tester.languages.get(sub.lang, None)
    print('Recived submission {} of task "{}" in language {}.'.format(sub.id, task.name if task is not None else sub.task, sub.lang))
    
    if task is None:
        print('Unknown task: {}.'.format(sub.task))
        continue
        
    if lang is None:
        print('Unknown language: {}.'.format(sub.lang))
        continue
    
    user_src = Paths.user_source.format(tmp_dir=config['tmp'], ext=lang.ext)
    with open(user_src, 'w') as f:
        f.write(sub.src)
        
    result = tester.OjojCodes.UnknownJudgeStatus
    cpu = []
    mem = []
    
    for event in tester.flow(lang, user_src, task, {'tmp_dir': config['tmp']}):
        if isinstance(event, events.Accepted):
            result = tester.OjojCodes.AC
        elif isinstance(event, events.Failure):
            result = event.code
        elif isinstance(event, events.TestResources):
            cpu.append(event.cpu)
            mem.append(event.mem)
    
    print('Finished testing solution. Result: {1} ({0})'.format(*result))
    if result is tester.OjojCodes.AC and cpu and mem:
        print('Submission cpu: {}'.format(str(cpu)))
        print('Submission mem: {}'.format(str(mem)))
        res = (int(1000*max(cpu)), max(mem))
        api.set(sub, result, res)
    else:
        api.set(sub, result)

"""
    
http(config['web.url']+'logout')
data = http(config['web.url']+'login')
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

        
    
    
    
    """