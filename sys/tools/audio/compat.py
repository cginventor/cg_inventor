import os, sys, types
from configparser import ConfigParser
from configparser import Error as ConfigParserError

#--------------------------------------------------------------------------------------------------#

def total_ordering(cls):
    convert = {'__lt__': [('__gt__', lambda self, other: other < self),
                          ('__le__', lambda self, other: not other < self),
                          ('__ge__', lambda self, other: not self < other)],
               '__le__': [('__ge__', lambda self, other: other <= self),
                          ('__lt__', lambda self, other: not other <= self),
                          ('__gt__', lambda self, other: not self <= other)],
               '__gt__': [('__lt__', lambda self, other: other > self),
                          ('__ge__', lambda self, other: not other > self),
                          ('__le__', lambda self, other: not self > other)],
               '__ge__': [('__le__', lambda self, other: other >= self),
                          ('__gt__', lambda self, other: not other >= self),
                          ('__lt__', lambda self, other: not self >= other)]}
    
    roots = set(dir(cls)) & set(convert)
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    
    root = max(roots)
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
            
    return cls

#--------------------------------------------------------------------------------------------------#

def importmod(mod_file):
    mod_name = os.path.splitext(os.path.basename(mod_file))[0]

    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader(mod_name, mod_file)
    mod = loader.load_module()

    return mod
