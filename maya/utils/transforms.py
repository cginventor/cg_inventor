import maya.cmds as mc

import cg_inventor.maya.utils.generic as util_generic

callbackSetup   = util_generic.callbackSetup
callbackCounter = util_generic.callbackCounter


class TransformError(Exception):
    pass


# ------------------------------------------------------------------------------------------------ #

def getAllTransforms(cameras=False):
    ignore_list = set([])
    if cameras is False:        
        for camera in mc.ls(type='camera'):
            ignore_list.add(mc.listRelatives(camera, p=True)[0])
            
    return list(set(mc.ls(type='transform')) - ignore_list)
    
    
def _getAllTransforms():
    return mc.ls(type='transform')


def isTransform(transform):
    if mc.nodeType(transform) == 'transform': return True
    return False

# ------------------------------------------------------------------------------------------------ #

def freezeTransforms(transforms, t=True, r=True, s=True, filter=True, callback=None):
    # convert to list
    #
    if not isinstance(transforms, (list, tuple)):
        transforms = [transforms]
    
    # filter out non transforms
    #
    if filter is True:
        filtered_transforms = []
        for transform in transforms:
            if mc.nodeType(transform) == 'transform':
                filtered_transforms.append(transform)
                
        transforms = filtered_transforms
    
    # fail if non transforms are found
    #   
    else:
        failed_transforms = []
        for transform in transforms:
            if mc.nodeType(transform) != 'transform':
                failed_transforms.append(transform)
                
        if len(failed_transforms):
            raise TransformError("One or more non transforms found. %s." %failed_transforms)
    
    _freezeTransforms(transforms)


def freezeAllTransforms():
    freezeTransforms(getAllTransforms())
    

def _freezeTransforms(transforms, translate=True, rotate=True, scale=True, callback=None):
    errors = set([])
    
    if callback: counter, increment = callbackSetup(len(transforms))
    
    mc.undoInfo(openChunk=True)
    mc.scriptEditorInfo(e=True, sw=True)
    try:
        for transform in transforms:
            # store mesh opposite values for resetting
            #
            all_meshes = mc.listRelatives(transform, ad=True, type='mesh', f=True)
            
            mesh_opposites = {}
            for mesh in all_meshes:
                mesh_opposites[mesh] = mc.getAttr('%s.opposite' %mesh)

            try:
                mc.makeIdentity(transform, apply=True, t=translate, r=rotate, s=scale)                                        

            except RuntimeError as e:
                errors.add(str(e))
                                
            finally:
                if callback: callback(callbackCounter(counter, increment))
            
            # reset opposite flag
            #   
            for mesh in all_meshes:
                mc.setAttr('%s.opposite' %mesh, mesh_opposites[mesh])
                
    finally:
        mc.undoInfo(closeChunk=True)
        mc.scriptEditorInfo(e=True, sw=False)

    if len(errors):
        raise TransformError('\n'.join(errors))
    
    if callback: callback(100)     
    
# ------------------------------------------------------------------------------------------------ #

def isFrozen(transform):
    trs = ('t',0), ('r',0), ('s',1)    
    xyz = 'xyz'    
    
    for i, value in trs:
        for j in xyz:
            if mc.getAttr("%s.%s%s" %(transform, i, j)) != value:
                return False
             
    return True


def getUnfrozenTransforms(transforms, callback=None):
    transforms = mc.ls(transforms, type='transform')
    return _getUnfrozenTransforms(transforms, callback=callback)
        
    
def _getUnfrozenTransforms(transforms, callback=None):
    unfrozen_transforms = []
        
    if callback: counter, increment = callbackSetup(len(transforms))
    
    for transform in transforms:
        if callback: callback(callbackCounter(counter, increment))
             
        if isFrozen(transform):
            continue
        
        unfrozen_transforms.append(transform)
    
    return unfrozen_transforms

# ------------------------------------------------------------------------------------------------ #

def isLocked(transform):
    '''
        Test if transform channels are locked.
    
    args : 
        transform : the name of the transform to check
        
    returns :
        returns the locked values for each channel [tx, ty, tz, rx, ry, rz, sx, sy, sz]
    '''
    
    trs = 'trs'; xyz = 'xyz'
    
    locked = []
    for i in trs:
        for j in xyz:
            locked.append(mc.getAttr("%s.%s%s" %(transform, i, j), l=True))

    return locked
    
# ------------------------------------------------------------------------------------------------ #
    
def isPivotCentered(transform):
    current_centre = mc.xform(transform, q=True, ws=True, rp=True)
    mc.xform(transform, cp=True)
    new_centre = mc.xform(transform, q=True, ws=True, rp=True)
    mc.xform(transform, rp=current_centre, ws=True)

    return current_centre == new_centre
    
# ------------------------------------------------------------------------------------------------ #

def mirrorTransformAcrossAxis(transform, x=False, y=False, z=False, ws=False, os=False):
    # get axis choice
    #
    index = 0
    for index, attr in enumerate([x, y, z]):
        if attr is True:
            index = index
            break

    # get object space
    #
    if ws is False and os is False:
        ws = True
       
    if os is True:
        attr = ['x','y','z'][index]
        
        value = mc.getAttr('%s.t%s' %(transform, attr))
        mc.setAttr('%s.t%s' %(transform, attr), value * -1)
        
    else:
        position = mc.xform(transform, q=True, ws=True, t=True)
        position[index] *= -1
        mc.xform(transform, ws=True, t=position)
        
        
        
        
    
    



    
    
    
    