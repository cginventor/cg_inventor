import maya.cmds as mc
import maya.OpenMaya as om
import math

import cg_inventor.maya.utils.generic as util_generic

callbackSetup   = util_generic.callbackSetup
callbackCounter = util_generic.callbackCounter


TRIANGLES         = 'triangles'
NSIDED            = 'nsided'
NON_PLANAR        = 'nonPlanar'
HOLED             = 'holed'
CONCAVE           = 'concave'
ZERO_AREA_FACES   = 'zeroAreaFaces'
ZERO_LENGTH_EDGES = 'zeroLengthEdges'
LAMINA            = 'lamina'
NON_MANIFOLD      = 'nonManifold'


class MeshError(Exception):
    pass


def _checkMesh(mesh):
    if not mc.objExists(mesh):
        raise MeshError("'%s' does not exist." %mesh)
    
    if mc.nodeType(mesh) != 'mesh':
        raise MeshError("'%s' is not a mesh." %mesh)

#--------------------------------------------------------------------------------------------------#

def getAllMeshes(intermediates=False):
    return mc.ls(type='mesh', ni=not(intermediates))

#--------------------------------------------------------------------------------------------------#
    
def getAllIntermediateMeshes():
    return mc.ls(type='mesh', io=True)


def isIntermediateMesh(mesh):
    if len(mc.ls(mesh, io=True)):
        return True
    return False

#--------------------------------------------------------------------------------------------------#

def getTransformFromShape(shape):
    if not mc.nodeType(shape) == 'mesh':
        raise MeshError('Works for mesh type nodes only.')
    
    parent = mc.listRelatives(shape, p=True, pa=True)[0]
    
    if mc.nodeType(parent) != 'transform':
        raise MeshError("Failed to find transform for '%s'." %shape)
    
    return parent


def getTransformsFromShapes(shapes, filter=True):
    transforms = []
    for shape in shapes:
        try:
            transform = getTransformFromShape(shape)
        except MeshError as e:
            if filter: continue
            raise e
        
        transforms.append(transform)
    return transforms


def getShapesFromTransforms(transforms):
    return mc.listRelatives(transforms, ad=True, s=True)


def getMeshesFromSelection(selection):
    meshes = set([])
    
    for node in selection:
        node_type = mc.nodeType(node)
        
        if node_type == 'mesh':
            meshes.add(node)
            
        elif node_type == 'transform':
            shapes = getShapesFromTransforms(node)
            if shapes is None: continue
            
            for shape in shapes:
                if mc.nodeType(shape) == 'mesh':
                    meshes.add(shape)
                        
    return list(meshes)  

#--------------------------------------------------------------------------------------------------#    

def getUnconnectedIntermediates():
    intermediates = getAllIntermediateMeshes()
    ignore_nodes = set(['initialShadingGroup'])
    
    if len(intermediates) == 0: return []        

    unconnected = set(())
    for intermediate in intermediates:
        connections = mc.listConnections(intermediate)
        if connections is None: continue
        
        if not len(set(connections) - ignore_nodes):
            unconnected.add(intermediate)

    return list(unconnected)

#--------------------------------------------------------------------------------------------------#    

def getEmptyMeshes():
    meshes = getAllMeshes()
    
    empty_meshes = []
    for mesh in meshes:
        if _isMeshEmpty(mesh):
            empty_meshes.append(mesh)
    
    return list(empty_meshes)


def isMeshEmpty(mesh):
    node_type = mc.nodeType(mesh)
    if node_type == 'transform':
        shapes = mc.listRelatives(mesh, s=True)
        found_mesh = False
        for shape in shapes:
            if mc.nodeType(shape, 'mesh'):
                found_mesh = True
                break
        
        if found_mesh is False:
            raise MeshError("Failed to find a mesh shape")
        
    _checkMesh(mesh)
    
    return _isMeshEmpty(mesh)
    
    
def _isMeshEmpty(mesh):       
    try:
        mc.getAttr('%s.f[0]' %mesh)
    except Exception:
        return True
    return False    

#--------------------------------------------------------------------------------------------------#    

def checkMesh(meshes, flags='all', area=None, length=None, callback=None):  
    component_flags = [TRIANGLES, NSIDED, NON_PLANAR, HOLED, CONCAVE,
                      ZERO_AREA_FACES, ZERO_LENGTH_EDGES, LAMINA]
    geometry_flags  = [NON_MANIFOLD]

    if area:        
        if not isinstance(area, (tuple, list)):
            raise MeshError('Area must be a list or tuple of floats, (min, max).')
        if not isinstance(area[0], (int, float)) or not isinstance(area[1], (int, float)):
            raise MeshError('Area must be a list or tuple of floats, (min, max).')
    else:
        area = (0.0, 0.00001)

    if length:         
        if not isinstance(area, (tuple, list)):
            raise MeshError('Length must be a list or tuple of floats, (min, max).')
        if not isinstance(area[0], (int, float)) or not isinstance(area[1], (int, float)):
            raise MeshError('Length must be a list or tuple of floats, (min, max).')
    else:
        length = (0.0, 0.00001)

    if flags == 'all':
        flags = list(component_flags)
        flags.extend(geometry_flags)
        
    elif isinstance(flags, str):
        flags = [flags]
        
    elif not isinstance(flags, (list, tuple)):
        raise MeshError("Invalid input type, '%s'." %flags)

    components = []
    currentSelection = mc.ls(sl=True)
    
    if callback:
        callback_counter, callback_increment = callbackSetup(len(flags))        
    
    for flag in flags:
        
        if callback:
            callback(callbackCounter(callback_counter, callback_increment))
        
        if flag in component_flags:
            mc.select(meshes, r=True)
            mc.polySelectConstraint(disable=True)
            
            if flag == component_flags[0]:                                   # triangles
                mc.polySelectConstraint(m=3, t=0x0008, sz=1)
                
            elif flag == component_flags[1]:                                 # nsided
                mc.polySelectConstraint(m=3, t=0x0008, sz=3)
                
            elif flag == component_flags[2]:                                 # nonPlanar
                mc.polySelectConstraint(m=3, t=0x0008, p=1)
                
            elif flag == component_flags[3]:                                  # holed
                mc.polySelectConstraint(m=3, t=0x0008, h=1)
                
            elif flag == component_flags[4]:                                 # concave
                mc.polySelectConstraint(m=3, t=0x0008, c=1)
                
            elif flag == component_flags[5]:                                 # zeroAreaFaces
                mc.polySelectConstraint(m=3, t=0x0008, ga=True, gab=area)
                
            elif flag == component_flags[6]:                                 # zeroLengthEdges
                mc.polySelectConstraint(m=3, t=0x8000, l=True, lb=length)
                
            elif flag == component_flags[7]:                                 # lamina
                mc.polySelectConstraint(m=3, t=0x0008, tp=2)   
                 
            components.extend(mc.ls(sl=True, fl=True))
            mc.polySelectConstraint(disable=True)
        
        elif flag in geometry_flags:
            if flag == geometry_flags[0]:                                    # nonManifold
                for item in meshes:
                    nm_verts = set(())
                    nm_verts.update(mc.ls(mc.polyInfo(item, nmv=True), fl=True))

                    edges = mc.polyInfo(item, nme=True)
                    if edges:
                        nm_verts.update(mc.ls(mc.polyListComponentConversion(edges, 
                                                                             fe=True, 
                                                                             tv=True), fl=True))

                    components.extend(mc.ls(list(nm_verts), fl=True))

        mc.select(cl=True)

    if currentSelection:
        mc.select(currentSelection, r=True)
           
    return components

#--------------------------------------------------------------------------------------------------#    

def getVertexCount(mesh):
    return mc.polyEvaluate(mesh, v=True)


def getEdgeCount(mesh):
    return mc.polyEvaluate(mesh, e=True)


def getFaceCount(mesh):
    return mc.polyEvaluate(mesh, f=True)
    
#--------------------------------------------------------------------------------------------------#    

def _getMObject(mesh):
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    mObject = om.MObject()
    sel_list.getDependNode(0, mObject)
    return mObject


def _getMDagPath(mesh):
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    mDagPath = om.MDagPath()
    sel_list.getDagPath(0, mDagPath)
    return mDagPath


def _getVertIndexFromString(vertex):
    return _getIndexFromString(vertex, 'vtx')


def _getFaceIndexFromString(face):
    return _getIndexFromString(face, 'f')

    
def _getEdgeIndexFromString(edge):
    return _getIndexFromString(edge, 'e')


def _getIndexFromString(component, cmp_string):
    mesh, index = component.split('.%s[' %cmp_string)
    index = int(index.split(']')[0])
    return mesh, index


def _itMeshVertex(mesh, index):
    mesh       = _getMObject(mesh)
    it_vertex  = om.MItMeshVertex(mesh)

    util = om.MScriptUtil(0)
    prev_index = util.asIntPtr()
    
    it_vertex.setIndex(index, prev_index)
    return it_vertex


def _itMeshEdge(mesh, index):
    mesh       = _getMObject(mesh)
    it_edge    = om.MItMeshEdge(mesh)
    
    util = om.MScriptUtil(0)
    prev_index = util.asIntPtr()
    
    it_edge.setIndex(index, prev_index)
    return it_edge


def _itMeshPolygon(mesh, index):
    mesh       = _getMObject()
    it_polygon = om.MItMeshPolygon(mesh)

    util = om.MScriptUtil(0)
    prev_index = util.asIntPtr()
  
    it_polygon.setIndex(index, prev_index)
    return it_polygon

#--------------------------------------------------------------------------------------------------#

def getVertexPosition(vertex=None, mesh=None, index=None, os=True, ws=False):
    if vertex:
        mesh, index = _getVertIndexFromString(vertex)
    it_vertex = _itMeshVertex(mesh, index)
       
    if ws is True:    os = False
    elif os is False: ws = True
    
    if os:
        point = it_vertex.position(om.MSpace.kObject)
    else:      
        point = it_vertex.position(om.MSpace.kWorld)

    return (point[0], point[1], point[2])


def getAllVertexPositions(mesh, asMPoint=False, os=True, ws=False):
    mesh = _getMDagPath(mesh)
    it_vertex = om.MItMeshVertex(mesh)
    
    if ws is True:    os = False
    elif os is False: ws = True
    
    point_positions = {}
    while not it_vertex.isDone():
        index = it_vertex.index()
        if os:
            point_positions[index] = it_vertex.position(om.MSpace.kObject)
        else:
            point_positions[index] = it_vertex.position(om.MSpace.kWorld)
        it_vertex.next()
    
    if asMPoint:
        return point_positions
    
    vert_positions = {}
    for vert_index, point in point_positions.items():
        vert_positions[vert_index] = (point[0], point[1], point[2])
        
    return vert_positions


def setVertexPosition(position, vertex=None, mesh=None, index=None, os=True, ws=True):
    if vertex:
        mesh, index = _getVertIndexFromString(vertex)
    it_vertex = _itMeshVertex(mesh, index)

    if isinstance(position, (tuple, list)):
        position = om.MPoint(position[0], position[1], position[2], 1.0)
        
    if ws is True:    os = False
    elif os is False: ws = True

    if os:
        it_vertex.setPosition(position, om.MSpace.kObject)
    else:
        it_vertex.setPosition(position, om.MSpace.kWorld)
    
#--------------------------------------------------------------------------------------------------#
    
def getVertexNormal(vertex=None, mesh=None, index=None, asMVector=False):
    if vertex:
        mesh, index = _getVertIndexFromString(vertex)
    it_vertex = _itMeshVertex(mesh, index)
    
    normal = om.MVector()
    it_vertex.getNormal(normal, om.MSpace.kWorld)
    
    if asMVector:
        return normal    
    return (normal[0], normal[1], normal[2])


def getOrientationAtVertex(vertex, up_vector=(0,1,0)):
    normal = getVertexNormal(vertex, asMVector=True)
    
    up     = om.MVector(up_vector[0], up_vector[1], up_vector[2])
    up.normalize()
    
    tangent = up ^ normal
    up      = normal ^ tangent
    
    normal.normalize()
    up.normalize()
    tangent.normalize()
    
    atan2   = math.atan2
    power   = math.pow
    degrees = math.degrees
    sqrt    = math.sqrt
    
    rot_x = degrees(atan2(up[2], normal[2]))
    rot_y = degrees(atan2(-tangent[2], sqrt(power(up[2], 2) + power(normal[2], 2))))
    rot_z = degrees(atan2(tangent[1], tangent[0]))
    
    return (rot_x, rot_y, rot_z)

#-----------------------------------------------------------------------------------------#

def vertexToFaces(vertex=None, mesh=None, index=None):
    if vertex:
        mesh, index = _getVertIndexFromString(vertex)
    it_vertex = _itMeshVertex(mesh, index)

    faces = om.MIntArray()
    it_vertex.getConnectedFaces(faces)
    return list(faces)


def vertexToEdges(vertex=None, mesh=None, index=None):
    if vertex:
        mesh, index = _getVertIndexFromString(vertex)
    it_vertex = _itMeshVertex(mesh, index)
        
    edges = om.MIntArray()
    it_vertex.getConnectedEdges(edges)
    return list(edges)


def edgeToFaces(edge=None, mesh=None, index=None):
    if edge:
        mesh, index = _getEdgeIndexFromString(edge)
    it_edge = _itMeshEdge(mesh, index)
    
    faces = om.MIntArray()
    it_edge.getConnectedFaces(faces)
    return list(faces)


def edgeToVertices(edge=None, mesh=None, index=None):
    if edge:
        mesh, index = _getEdgeIndexFromString(edge)
    it_edge = _itMeshEdge(mesh, index)
    
    return [it_edge.index(0), it_edge.index(1)]


def getConnectedEdges(edge=None, mesh=None, index=None):
    if edge:
        mesh, index = _getEdgeIndexFromString(edge)
    it_edge = _itMeshEdge(mesh, index)
    
    edges = om.MIntArray()
    it_edge.getConnectedEdges(edges)
    return list(edges)


def faceToVertices(face=None, mesh=None, index=None):
    if face:
        mesh, index = _getFaceIndexFromString(face)
    it_polygon = _itMeshPolygon(mesh, index)
        
    verts = om.MIntArray()
    it_polygon.getVertices(verts)
    return list(verts)


def faceToEdges(face=None, mesh=None, index=None):
    if face:
        mesh, index = _getFaceIndexFromString(face)
    it_polygon = _itMeshPolygon(mesh, index)
     
    edges = om.MIntArray()
    it_polygon.getConnectedEdges(edges)
    return list(edges)

#--------------------------------------------------------------------------------------------------#

def getBorderVerts(mesh):
    mesh = _getMObject(mesh)
    it_vertex = om.MItMeshVertex(mesh)

    border_verts = []
    while not it_vertex.isDone():
        if it_vertex.onBoundary():
            border_verts.append(it_vertex.index())
        it_vertex.next()

    return border_verts


def getBorderEdges(mesh):
    mesh = _getMObject(mesh)
    it_edge = om.MItMeshEdge(mesh)

    border_edges = []
    while not it_edge.isDone():
        if it_edge.onBoundary():
            border_edges.append(it_edge.index())
        it_edge.next()

    return border_edges


def getBorderFaces(mesh):
    mesh = _getMObject(mesh)
    it_polygon = om.MItMeshPolygon(mesh)

    border_faces = []
    while not it_polygon.isDone():
        if it_polygon.onBoundary():
            border_faces.append(it_polygon.index())
        it_polygon.next()

    return border_faces

#--------------------------------------------------------------------------------------------------#

def getHardEdges(mesh, border=False):
    mesh = _getMObject(mesh)
    it_edge = om.MItMeshEdge(mesh)

    hard_edges = []
    while not it_edge.isDone():
        if not it_edge.isSmooth() and not (not(border) and it_edge.onBoundary()):
            hard_edges.append(it_edge.index())
        it_edge.next()

    return hard_edges


def getSoftEdges(mesh):
    mesh = _getMObject(mesh)
    it_edge = om.MItMeshEdge(mesh)

    soft_edges = []
    while not it_edge.isDone():
        if it_edge.isSmooth():
            soft_edges.append(it_edge.index())
        it_edge.next()

    return soft_edges

#--------------------------------------------------------------------------------------------------#

def getLockedVertexNormals(mesh):
    _checkMesh(mesh)
    
    mesh    = _getMObject(mesh)
    fn_mesh = om.MFnMesh(mesh)
    it_face = om.MItMeshPolygon(mesh)
    
    util       = om.MScriptUtil(0)
    prev_index = util.asIntPtr()  
    
    poly_verts = om.MIntArray()
    normal_ids = om.MIntArray()
    verts      = om.MIntArray()

    fn_mesh.getNormalIds(poly_verts, normal_ids)
    if not len(normal_ids): return []
    
    locked_verts = set([]); count = 0
    for face_index, num_verts in enumerate(poly_verts):
        it_face.setIndex(face_index, prev_index)

        it_face.getVertices(verts)
        normals = normal_ids[count:count+num_verts]
        
        for norm_id, vert_index in zip(normals, verts):
            if fn_mesh.isNormalLocked(norm_id):
                locked_verts.add(vert_index)
        count += num_verts

    return locked_verts

#--------------------------------------------------------------------------------------------------#   

def getMeshHoles(mesh, as_verts=False, as_edges=False, as_faces=False, callback=None):        
    _checkMesh(mesh)

    border_edges = getBorderEdges(mesh)

    hole_sets = []
    edge_lookup = {}
    
    if callback:
        counter, increment = callbackSetup(len(border_edges), 10)
    
    # sort border edges by shared verts
    #
    for border_edge in border_edges:
        vertices = edgeToVertices(mesh=mesh, index=border_edge)
        hole_sets.append(set(vertices))
        
        try:
            lookup = edge_lookup[vertices[0]]
        except KeyError:
            lookup = edge_lookup[vertices[0]] = []
        lookup.append(border_edge)
        
        try:
            lookup = edge_lookup[vertices[1]]
        except KeyError:
            lookup = edge_lookup[vertices[1]] = []
        lookup.append(border_edge)
        
        if callback: callback(callbackCounter(counter, increment))
        

    # find all joined edges
    #
    def _sortHoleEdges():
        num_hole_sets = len(hole_sets)
        if num_hole_sets <= 1:
            return False, hole_sets
        
        new_hole_sets = []
        matched       = False
        matched_sets  = set([])        
        
        for offset in range(num_hole_sets - 1):
            if offset in matched_sets: continue
            a = hole_sets[offset]            
            for index in range(num_hole_sets - offset - 1):
                set_index = index + offset + 1 
                b = hole_sets[set_index]
            
                ab = a | b
                if len(ab) < (len(a) + len(b)):
                    matched = True
                    matched_sets.add(set_index)
                    a = ab
                    
            new_hole_sets.append(a)
        
        if (num_hole_sets - 1) not in matched_sets:
            new_hole_sets.append(hole_sets[-1])            
            
        return matched, new_hole_sets
    
    # condense hole sets
    #    
    matching = True
    while matching is True:
        matching, hole_sets = _sortHoleEdges()
        if callback: callback(60)
         
    if as_verts is not True and as_edges is not True and as_faces is not True:
        as_edges = True
    
    if as_verts is True:
        if callback: callback(100)   
        return [list(hole_set) for hole_set in hole_sets]
    
    if as_edges is True or as_faces is True:
        edge_sets = []
        for hole_set in hole_sets:
            edge_set = set([])
            for vert in hole_set:
                edge_set.update(edge_lookup[vert])
            edge_sets.append(list(edge_set))
            
        if as_faces is False:
            if callback: callback(100)
            return edge_sets
        
        if callback:
            counter, increment = callbackSetup(len(edge_sets), 40)
    
        face_sets = []
        for edge_set in edge_sets:
            face_set = set([])
            for edge in edge_set:
                face_set.update(edgeToFaces(mesh=mesh, index=edge))
            face_sets.append(list(face_set))
            
            if callback: callback(60 + callbackCounter(counter, increment))
            
        return face_sets
    
#--------------------------------------------------------------------------------------------------#   

def getFiveEdgeVerts(mesh):
    mesh = _getMObject(mesh)
    it_vertex = om.MItMeshVertex(mesh)
    
    util = om.MScriptUtil(0)
    edge_count = util.asIntPtr()
    
    five_edge_verts = []
    while not it_vertex.isDone():
        it_vertex.numConnectedEdges(edge_count)
        if util.getInt(edge_count) > 4:
            five_edge_verts.append(it_vertex.index())
        it_vertex.next()

    return five_edge_verts
