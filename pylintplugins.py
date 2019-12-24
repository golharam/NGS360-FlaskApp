'''
This module is used to suppress the app.logger errors from pylint.   Its referenced in 'make test'
'''
# pylint: skip-file
from astroid import MANAGER, scoped_nodes, extract_node

def register(_linter):
    pass

def transform(f):
    if f.name == 'logger':
        for prop in ['debug', 'info', 'warning', 'error', 'addHandler']:
            f.instance_attrs[prop] = extract_node('def {name}(arg): return'.format(name=prop))

MANAGER.register_transform(scoped_nodes.FunctionDef, transform)
