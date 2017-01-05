import maya.cmds as mc



class BaseModuleError(Exception):
    pass



class BaseModule():
    exception = BaseModuleError
    
    def __init__(self, node):
        if not mc.objExists(node):
            raise self.exception("Node '%s' does not exist." %node)        
        self._node = node