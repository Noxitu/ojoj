import os.path
from data import load_xml


def _attrs_to_dict(elem):
    return dict(elem.items())
    
def _convert_special_directories(path):
    if path[:2] == './':
        return '{task_dir}/'+path[2:]
    if path[:2] == '~/':
        return '{tester_dir}/'+path[2:]
    return path
    
_required_params = {'id', 'verify', 'memory', 'cpu', 'input'}

def _make_test(test):
    missing_params = _required_params - test.keys()
    if missing_params:
        raise Exception('Missing test parameters: {}'.format(', '.join(missing_params)))
        
    test['verify'] = [ _convert_special_directories(arg) for arg in test['verify'].split(' ') ]
    test['input'] = _convert_special_directories(test['input'])

class Task:  
    @staticmethod
    def from_xml(path):
        task_dir = os.path.dirname(path)
        self = Task()
        data = load_xml('ojoj.task', path, handlers={'default': _attrs_to_dict, 'test': _attrs_to_dict})
        self.id = data['id']
        self.name = data.get('name', self.id)
        self.task_dir = data.get('task_dir', task_dir)
        self.tests = []
        
        default = data.get('default', {})
        for test in data.get_list('test'):
            tmp = {}
            tmp.update(default)
            tmp.update(test)
            _make_test(tmp)            
            self.tests.append(tmp)
            
        return self
        
    @staticmethod
    def from_info(path):
        """Legacy task format"""
        task_dir = os.path.dirname(path)
        self = Task()
        self.id = os.path.basename(task_dir) or 'unknown_task'
        self.name = self.id
        self.task_dir = task_dir
        self.tests = []
        
        with open(path) as file:
            data = file.read().split('\n')
            cpu, mem = map(float, data[0].split())
            cpu = '{:.0f}s'.format(cpu) if cpu%1 == 0 else '{:.0f}ms'.format(1000*cpu)
            mem = '{:.0f}M'.format(mem)
            
            for test in data[1].split():
                tmp = {
                    'id': test,
                    'verify': '~/diff {out} ./{id}.out',
                    'memory': mem,
                    'cpu': cpu,
                    'input': './{id}.in'
                }
                _make_test(tmp)
                self.tests.append(tmp)
            
        return self
        