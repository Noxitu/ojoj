import xml.etree.ElementTree
from collections import defaultdict, Counter

def _default_handler(elem):
    return ''.join(elem.itertext())
    
class Data:
    def __init__(self, data):
        self.data = {k:v for k,v in data.items()}
        
    def __getitem__(self, tag):
        return self.data[tag][-1]
    
    def get(self, tag, value=None):
        return self.data.get(tag, [value])[-1]
        
    def get_list(self, tag):
        return self.data.get(tag, [])
        
    def __repr__(self): return self.data.__repr__()
    
    def __setitem__(self, tag, value):
        if tag in self.data:
            self.data[tag].append(value)
        else:
            self.data[tag] = [value]
        


def load_xml(root_tag, path, handlers={}):
    e = xml.etree.ElementTree.parse(path).getroot()
    
    if e.tag != root_tag:
        raise Exception('Invalid root element file: {} (expected {})'.format(e.tag, root_tag))
        
    data = defaultdict(list)
    
    def _parse_recursive(tag, elem):
        if len(elem) == 0:
            value = handlers.get(tag, _default_handler)(elem)
            data[tag].append(value)
            
        else:    
            for child in elem:
                _parse_recursive('{}.{}'.format(tag, child.tag), child)
        
    for child in e:
        _parse_recursive(child.tag, child)
        
    return Data(data)

    