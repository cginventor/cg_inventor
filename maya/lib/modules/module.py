import maya.cmds as mc

    
def undo(func):
    def wrapper(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            mc.undoInfo(closeChunk=True)
        return ret
    return wrapper


class ModuleError(Exception):
    pass


class Module(object):    
    ATTR_AT_SET = set(['bool', 'long', 'short', 'byte', 'char', 'float', 'double'])
    ATTR_DT_SET = set(['string', 'stringArray', 'matrix', 'Int32Array'])
    
    
    def __init__(self):
        self.node = None


    def name(self):
        if self.node:
            return self.node
        return ''    
    
    
    def build(self):
        pass    
    
    
    def buildFromData(self):
        pass 
    
    
    def load(self, node):
        self.node = node        
    
    
    def _isSet(self):
        if not self.node: raise ModuleError('Module is not set.')    
    
    
    def rename(self, new_name):
        pass    
    
    
    def delete(self):
        pass    
    
    #------------------------------------------------------------------------------------------#
    
    def addAttr(self, data, attr, type, k=False, h=False):
        self._isSet()
        
        attr_name = '%s.%s'%(self.node, attr)
        
        mode = 'dt'
        if type in Module.ATTR_AT_SET: 
            mode = 'at'
                    
        if not mc.objExists(attr_name):
            if mode == 'at': 
                mc.addAttr(self.node, ln=attr, at=type, k=k, h=h)
            else:            
                mc.addAttr(self.node, ln=attr, dt=type, k=k, h=h)
        
        if mode == 'at':
            mc.setAttr(attr_name, data)
        else:
            mc.setAttr(attr_name, data, type=type)


    def getAttr(self, attr):
        self._isSet()
        
        attr_name = '{}.{}'.format(self.node, attr)
        
        if not mc.objExists(attr_name):
            return None
        
        return mc.getAttr(attr_name)
    
    
    def setAttr(self, attr, value):
        self._isSet()
        
        attr_name = '{}.{}'.format(self.node, attr)
        
        if not mc.objExists(attr_name):
            return None
        
        return mc.setAttr(attr_name, value)

    #------------------------------------------------------------------------------------------#
    
    def getSelf(self):
        return self
    
    
    def asPyNode(self):
        self._isSet()
        
        import pymel.core as pm
        
        try:
            return pm.PyNode(self.node)
        except pm.MayaNodeError:
            raise ModuleError("Node '%s' does not exist." %self.node)
    
    #------------------------------------------------------------------------------------------#
    
    def __str__(self):
        return "<%s '%s'>" %(self.__class__.__name__, self.node)    
    
    
    __repr__ = __str__
    
    
    