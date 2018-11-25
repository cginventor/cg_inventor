import os, sys, types

from cg_inventor.sys.utils import version

python_version = version.getPythonVersion()
python2 = python_version[0] == 2
python3 = python_version[0] == 3

#--------------------------------------------------------------------------------------------------#

if python2:
    StringTypes = types.StringTypes
    UnicodeType = unicode
    BytesType   = str
    unicode     = unicode

    from ConfigParser import SafeConfigParser as ConfigParser
    from ConfigParser import Error as ConfigParserError

    from StringIO import StringIO
    
else:
    StringTypes = (str,)
    UnicodeType = str
    BytesType   = bytes
    unicode     = str

    from configparser import ConfigParser
    from configparser import Error as ConfigParserError

    from io import StringIO

#--------------------------------------------------------------------------------------------------#

def toByteString(n):
    if python2:
        return chr(n)
    else:
        return bytes((n,))


def byteiter(bites):
    assert(isinstance(bites, str if python2 else bytes))
    for b in bites:
        yield b if python2 else bytes((b,))

#--------------------------------------------------------------------------------------------------#

if python2 and python_version[1] < 7:
    from functools import total_ordering
    
else:
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
                              ('__lt__', lambda self, other: not self >= other)]
        }
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

    if python2:
        import imp
        mod = imp.load_source(mod_name, mod_file)
        
    else:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mod_name, mod_file)
        mod = loader.load_module()

    return mod

