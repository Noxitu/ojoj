
class Failure:
    def __init__(self, code): self.code = code
    
class Compiling: pass
class Compiled: pass

class TestRunning:
    def __init__(self, *a, id, cpu_limit, mem_limit, **kw):
        self.id = id
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        
class TestResources:
    def __init__(self, *a, cpu, mem, **kw):
        self.cpu = cpu
        self.mem = mem

class TestFailure:
    def __init__(self, code): self.code = code
    
class TestOk: pass
class Accepted: pass