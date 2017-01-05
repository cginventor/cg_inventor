import maya.cmds as mc
import maya.OpenMaya as om

import cg_inventor.maya.utils.mesh as util_mesh

class TextureError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

def _checkMaterial(material):
    if not mc.objExists(material):
        raise TextureError("Material '%s' does not exist." %material)
    
    if mc.nodeType(material) not in mc.listNodeTypes('shader'):
        raise TextureError("'%s' is not a recognised material." %material)

#--------------------------------------------------------------------------------------------------#

def getAllMaterials(persistent_nodes=False):
    if persistent_nodes:
        return mc.ls(mat=True)
    return list(set(mc.ls(mat=True)) - set(['lambert1', 'particleCloud1']))

#--------------------------------------------------------------------------------------------------#

def getMaterialMembers(material):
    _checkMaterial(material)    
    return _getMaterialMembers(material)
    
    
def _getMaterialMembers(material):
    shader_engine = _getMaterialShaderEngine(material)
    return mc.listConnections('%s.dagSetMembers' %shader_engine)


def assignMaterial(material, nodes):
    _checkMaterial(material)    
    _assignMaterial(material, nodes)


def _assignMaterial(material, nodes):
    nodes = mc.ls(nodes, type='transform')
    shader_engine = _getMaterialShaderEngine(material)  
    
    mc.sets(nodes, e=True, forceElement=shader_engine)

#--------------------------------------------------------------------------------------------------#

def getMaterialShaderEngine(material):
    _checkMaterial(material)   
    return _getMaterialShaderEngine(material)


def _getMaterialShaderEngine(material):
    shader_engines = mc.listConnections('%s.outColor' %material)
    num_se = len(shader_engines)
    if num_se == 0:
        raise TextureError("Failed to find shader engine for '%s'." %material)
    elif num_se == 1:
        return shader_engines[0]
    else:
        for shader_engine in shader_engines:
            if mc.listConnections('%s.volumeShader' %shader_engine):
                continue
            return shader_engine
    raise TextureError("Failed to find shader engine for '%s'." %material) 

#--------------------------------------------------------------------------------------------------#


def getAllUnusedMaterials(persistent_nodes=False):
    all_materials = getAllMaterials(persistent_nodes=persistent_nodes)
    
    unused_materials = []
    for material in all_materials:
        members = getMaterialMembers(material)
        if members is None:
            unused_materials.append(material)
    
    return unused_materials

#--------------------------------------------------------------------------------------------------#

def deleteMaterial(material, reassign='lambert1'):
    _checkMaterial(material)

    return _deleteMaterial(material, reassign)

    
def _deleteMaterial(material, reassign='lambert1'):
    members       = _getMaterialMembers(material)
    shader_engine = _getMaterialShaderEngine(material)
    
    try:
        mc.delete(material, shader_engine)
    except RuntimeError:
        raise TextureError("Failed to delete material '%s'." %material)
    
    if not members: return
    
    _assignMaterial(reassign, members)
    
#--------------------------------------------------------------------------------------------------#

def getAllUVs(mesh):
    util_mesh._checkMesh(mesh)
    return _getAllUVs(mesh)


def _getAllUVs(mesh):
    uv_sets = _getUVSetNames(mesh)
    
    mesh       = util_mesh._getMDagPath(mesh)
    it_polygon = om.MItMeshPolygon(mesh)
    
    index_util = om.MScriptUtil()
    u_util = om.MScriptUtil()
    v_util = om.MScriptUtil()
    
    uv_index_ptr = index_util.asIntPtr()
    u_ptr        = u_util.asFloatPtr()    
    v_ptr        = v_util.asFloatPtr()
    
    uv_positions = {}
    while not it_polygon.isDone():        
        face_index = it_polygon.index()
        
        for vert_index in range(it_polygon.polygonVertexCount()):
            try:
                vert_uv = it_polygon.getUVIndex(vert_index, uv_index_ptr, u_ptr, v_ptr)
            except RuntimeError:
                continue
            
            uv = u_util.getFloat(u_ptr), v_util.getFloat(v_ptr)
            uv_positions[index_util.getInt(uv_index_ptr)] = uv

        it_polygon.next()
    
    return uv_positions

#--------------------------------------------------------------------------------------------------#

def getAllUVsOutOfBounds(mesh, u_max=1, u_min=0, v_max=1, v_min=0):
    all_uvs = getAllUVs(mesh)
    
    uvs_oob = []
    for uv_index, uv in all_uvs.items():
        u = round(uv[0], 6); v = round(uv[1], 6)
        if u < u_min or u > u_max or v < v_min or v > v_max:
            uvs_oob.append(uv_index)
            
    return uvs_oob

#--------------------------------------------------------------------------------------------------#

def getUVSetNames(mesh):
    util_mesh._checkMesh(mesh)
    return _getUVSetNames(mesh)
    
    
def _getUVSetNames(mesh):
    mesh       = util_mesh._getMDagPath(mesh)
    it_polygon = om.MItMeshPolygon(mesh)
    
    set_names = []
    it_polygon.getUVSetNames(set_names)   
        
    return set_names
    
#--------------------------------------------------------------------------------------------------#

def zeroAreaUVFaces(mesh):
    mesh       = util_mesh._getMDagPath(mesh)
    it_polygon = om.MItMeshPolygon(mesh)
    
    set_names = []
    it_polygon.getUVSetNames(set_names)
    
    index_util = om.MScriptUtil()
    u_util = om.MScriptUtil()
    v_util = om.MScriptUtil()
    
    uv_index_ptr = index_util.asIntPtr()
    u_ptr        = u_util.asFloatPtr()    
    v_ptr        = v_util.asFloatPtr()
    
    uv_set_positions = {}
    while not it_polygon.isDone():        
        face_index = it_polygon.index()
        
        for set_name in set_names:
            for vert_index in range(it_polygon.polygonVertexCount()):
                try:
                    vert_uv = it_polygon.getUVIndex(vert_index, uv_index_ptr, u_ptr, v_ptr, set_name)
                except RuntimeError:
                    continue
                
                try:
                    uv_positions = uv_set_positions[set_name]
                except KeyError:
                    uv_positions = uv_set_positions[set_name] = {}
                
                uv = u_util.getFloat(u_ptr), v_util.getFloat(v_ptr)
                uv_positions[index_util.getInt(uv_index_ptr)] = uv

        it_polygon.next()
    
    return uv_set_positions
    