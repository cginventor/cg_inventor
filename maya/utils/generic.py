import maya.cmds as mc

from cg_inventor.sys.utils.generic import *

#--------------------------------------------------------------------------------------------------#

def formatError(error):
    '''
        Format and string in the maya error style.
    '''
    if not isinstance(error, str):
        return

    error = error.lstrip('\n').rstrip('\n')
    error = error.replace('\n','\n# ')
    error = '\n# %s\n' %error
    return error

#--------------------------------------------------------------------------------------------------#

def undo(func):
    def wrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            mc.undoInfo(closeChunk=True)
        return ret
    return wrapper

#--------------------------------------------------------------------------------------------------#
