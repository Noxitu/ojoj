#!/usr/bin/python

import os, subprocess
import events

class Paths:
    user_app = '{tmp_dir}/ojoj-user-app'
    compiler_output = '{tmp_dir}/ojoj-compiler-output.txt'
    judge_app = '{tester_dir}/ojoj_judge'
    judge_output = '{tmp_dir}/ojoj-judge-output.txt'
    user_output = '{tmp_dir}/ojoj-user-output.txt'

class OjojCodes:
    AC = ('AC', 'Accepted')
    WA = ('WA', 'Wrong Answer')
    TLE = ('TLE', 'Time Limit Exceeded')
    RE = ('RE', 'Runtime Error')
    NZEC = ('NZEC', 'Non-zero Exit Code')
    CE = ('CE', 'Compilation Error')
    UnknownJudgeStatus = ('?', 'Unknown Judge Status')
    
    short = lambda code : code[0]
    long = lambda code : code[1]
    
    
JudgeCodes = {1: OjojCodes.TLE, 3: OjojCodes.RE, 4: OjojCodes.NZEC}

tester_dir, _ = os.path.split(os.path.abspath(__file__))

class Language:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)[:-5]
        self.ext = ''
        for line in open(path):
            if line.startswith('#ext: '):
                self.ext = line.split()[-1]
                break

languages = os.listdir(os.path.join(tester_dir, 'languages'))
languages = [ Language(os.path.join(tester_dir, 'languages', filename)) for filename in languages if filename.endswith('.lang') ]
languages = { lang.name: lang for lang in languages if lang }

print('Found languages: {}'.format(', '.join(languages.keys())))

def parse_cpu(cpu):
    if cpu[-2:] == 'ms': return float(cpu[:-2])/1000
    if cpu[-1:] == 's': return float(cpu[:-1])
    raise Exception('Invalid CPU limit')
    
def parse_mem(cpu):
    if cpu[-1:] == 'K': return int(float((cpu[:-1])))
    if cpu[-1:] == 'M': return int(1024*float((cpu[:-1])))
    if cpu[-1:] == 'G': return int(1024*1024*float((cpu[:-1])))
    raise Exception('Invalid MEM limit')
   
def flow(compiler, source_path, task, config):
    vars = {
        'tester_dir': tester_dir,
        'task_dir': task.task_dir,
    }
    vars.update(config)

    if not os.path.isdir(vars['tmp_dir']):
        raise Exception('Invalid temporary directory: {}'.format(vars['tmp_dir']))

    yield events.Compiling()
    
    app = Paths.user_app.format(**vars)
    with open(Paths.compiler_output.format(**vars), 'w') as output:
        cmd = [compiler.path, source_path, app]
        compiled = subprocess.call(cmd, stdout=output, stderr=subprocess.DEVNULL)
    
    if compiled != 0:
            yield events.Failure(OjojCodes.CE)
            return

    yield events.Compiled()
    
    vars['out'] = Paths.user_output.format(**vars)
    for test in task.tests:
        test_vars = dict(vars)
        test_vars.update({
            'id': test['id']
        })
        
        cpu_limit = parse_cpu(test['cpu'])
        mem_limit = parse_mem(test['memory'])
        yield events.TestRunning(id=test['id'], cpu_limit=cpu_limit, mem_limit=mem_limit)
        
        judge_output_path = Paths.judge_output.format(**test_vars)
        with open(judge_output_path, 'w') as judge_output:
            cmd = [
                Paths.judge_app.format(**test_vars),
                Paths.user_app.format(**test_vars),
                str(cpu_limit),
                str(mem_limit),
                test['input'].format(**test_vars),
                Paths.user_output.format(**test_vars) ]
            status = subprocess.call( cmd, stdout=judge_output, stderr=subprocess.DEVNULL )
            
        if status != 0:
            code = JudgeCodes.get(status, OjojCodes.UnknownJudgeStatus)
            yield events.TestFailure(code)
            yield events.Failure(code)
            return
            
        cpu, mem = open(judge_output_path).read().split()
        cpu = float(cpu)
        mem = int(mem)
        yield events.TestResources(cpu=cpu, mem=mem)

        
        cmd = [ arg.format(**test_vars) for arg in test['verify'] ]
        status = subprocess.call( cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        if status != 0:
            yield events.TestFailure(OjojCodes.WA)
            yield events.Failure(OjojCodes.WA)
            return
        
        yield events.TestOk()
        
    yield events.Accepted()

if __name__ == '__main__':
    import main
    main.main()