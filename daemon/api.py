
from custom_http import http
import re

submission_result = lambda code : {'AC': 0, 'WA': 1, 'TLE': 2, 'RE': 4, 'CE': 5, 'NZEC':7}.get( code[0], 6 )


class Submission:
    pass

class Api:
    def __init__(self, config):
        self.config = config
        self.url = config['web.url']
        
        print('Connecting to web api...')
        http(self.url+'logout')
        data = http(self.url+'login')
        token = re.search('<input name="authenticity_token" type="hidden" value="([^"]+)" />', data ).group(1)
        http(self.url+'login', [ ('commit', 'Login'), ('name', config['web.login']), ('password', config['web.password']), ('authenticity_token', token) ] )
        print('Connected.')
        
        
    def get(self):
        data = http(self.config['web.url']+'tester_api_get').split('\n', 2)
        if data[0] == '-1':
            return None
        
        sub = Submission()
        sub.id = int(data[0])
        sub.task = data[1]
        sub.src = data[2]
        sub.lang = 'c++'
        return sub
        
    def set(self, sub, result, resources=None):
        result = submission_result(result)
        url = self.url+'tester_api_set/{}/{}'.format(sub.id, result)
        
        if resources:
            cpu, mem = resources
            url += '/{}/{}'.format(cpu, mem)

        http(url)

    def clear(self, sub):
        http(self.url+'subs/clear/{}'.format(sub.id))