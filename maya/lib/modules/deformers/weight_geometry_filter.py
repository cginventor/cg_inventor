import maya.OpenMaya as om

from .. import base_module


class WeightGeometryFilterError(Exception):
    pass    


class WeightGeometryFilter(base_module.BaseModule):
    exception = WeightGeometryFilterError

    def __init__(self, node):
        base_module.BaseModule.__init__(self, *args, **kwargs)
    
    #------------------------------------------------------------------------------------------#
    
    def getWeights(self):
        pass    
    
    
    def setWeights(self):
        pass    
    
    #------------------------------------------------------------------------------------------#    
    
    def saveWeights(self):
        pass    
    
    
    def loadWeights(self):
        pass

    #------------------------------------------------------------------------------------------#
    
    def copyWeights(self):
        pass
    
    
    def mirrorWeights(self):
        pass
    
    
    def flipWeights(self):
        pass
    
    #------------------------------------------------------------------------------------------#