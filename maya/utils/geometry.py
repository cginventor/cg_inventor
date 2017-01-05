import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as mc

class GeometryError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

def getSymmetry(center_edge, sets=True, sides=False, mirrors=False):
    util = om.MScriptUtil()
    
    sel = om.MSelectionList()
    sel.add(center_edge)
    dagPathSelShape = om.MDagPath()
    iter = om.MItSelectionList(sel)
    component = om.MObject()
    iter.getDagPath(dagPathSelShape, component)
    
    selected_edges = om.MItMeshEdge(dagPathSelShape, component)
    first_edge = selected_edges.index()
    
    # get mesh name
    #
    fnMesh = om.MFnMesh(dagPathSelShape) 
    
    edge_count = fnMesh.numEdges()
    vert_count = fnMesh.numVertices()
    poly_count = fnMesh.numPolygons()
    
    side_verts    = [-1] * vert_count    
    checked_verts = [-1] * vert_count
    checked_polys = [-1] * poly_count
    checked_edges = [-1] * edge_count
    
    l_edge_queue = om.MIntArray()
    r_edge_queue = om.MIntArray()
    
    # set up queue with initial edge
    #
    l_edge_queue.append(first_edge)
    r_edge_queue.append(first_edge)
    
    l_face_list = om.MIntArray()
    r_face_list = om.MIntArray()
    
    l_currentE = l_currentP = r_currentE = r_currentP = 0
    
    util.createFromInt(0)
    prev_index = util.asIntPtr()
    
    vertex_iter = om.MItMeshVertex(dagPathSelShape)
    poly_iter   = om.MItMeshPolygon(dagPathSelShape)
    edge_iter   = om.MItMeshEdge(dagPathSelShape)
    
    def compareChecked(lookup, left, right):
        def check(value): return lookup[value] == -1
            
        pairs = [(l, r) for l in left for r in right]
        
        for a, b in pairs:
            if check(a) and check(b):
                lookup[a] = b; lookup[b] = a    
        
    
    while len(l_edge_queue) > 0:        
        # set current edge
        #
        l_currentE = l_edge_queue[0]
        r_currentE = r_edge_queue[0]
        
        # remove current edge
        #
        l_edge_queue.remove(0)
        r_edge_queue.remove(0)
        
        if l_currentE == r_currentE and l_currentE != first_edge:
            continue
                
        # mark current edges as checked
        #
        checked_edges[l_currentE] = r_currentE
        checked_edges[r_currentE] = l_currentE
        
        # convert left edge to connected faces
        #
        edge_iter.setIndex(l_currentE, prev_index)
        edge_iter.getConnectedFaces(l_face_list)
        if l_face_list.length() != 2: continue
        f1, f2 = l_face_list   
        
        # get the face that hasnt been checked from the edge epansion
        #
        # if first face hasnt been checked and second has, set first
        if checked_polys[f1] == -1 and checked_polys[f2] != -1:
            l_currentP = f1
        # if first face has been checked and second hasnt, set second
        elif checked_polys[f1] != -1 and checked_polys[f2] == -1:
            l_currentP = f2
        # if neither face has been checked, store first and mark as reserved?
        elif checked_polys[f1] == -1 and checked_polys[f2] == -1:
            l_currentP = f1
            checked_polys[f1] = -2 # reserve it?
        
        
        # convert right edge to connected faces
        #
        edge_iter.setIndex(r_currentE, prev_index)
        edge_iter.getConnectedFaces(r_face_list)
        f1, f2 = r_face_list
    
        # get the face that hasnt been checked. Shouldnt be possible for neither
        # face to have been checked by this point, so throw error
        #
        # if first face hasnt been checked and second has, store first
        if checked_polys[f1] == -1 and checked_polys[f2] != -1:
            r_currentP = f1
        # if first face has been checked and second hasnt, store second
        elif checked_polys[f1] != -1 and checked_polys[f2] == -1:
            r_currentP = f2
        # if neither face has been checked, then its an error?
        elif checked_polys[f2] == -1 and checked_polys[f1] == -1:
            raise GeometryError('Topology is invalid.')
        # if both have been checked dont carry on
        else:
            continue
        
        # set polys to mirrored poly
        #
        checked_polys[r_currentP] = l_currentP
        checked_polys[l_currentP] = r_currentP
        
        # get verts from edge
        #
        util.createFromInt(0, 0)
        l_edge_verts = util.asInt2Ptr()
        util.createFromInt(0, 0)
        r_edge_verts = util.asInt2Ptr()
        
        # convert edges to verts
        #
        fnMesh.getEdgeVertices(l_currentE, l_edge_verts)
        lev1 = om.MScriptUtil.getInt2ArrayItem(l_edge_verts, 0, 0)
        lev2 = om.MScriptUtil.getInt2ArrayItem(l_edge_verts, 0, 1)
        
        fnMesh.getEdgeVertices(r_currentE, r_edge_verts)
        rev1 = om.MScriptUtil.getInt2ArrayItem(r_edge_verts, 0, 0)
        rev2 = om.MScriptUtil.getInt2ArrayItem(r_edge_verts, 0, 1)
        
        # if current edge is first edge set vert value to itself
        #
        if l_currentE == first_edge:
            checked_verts[lev1] = rev1
            checked_verts[lev2] = rev2
            checked_verts[rev1] = lev1
            checked_verts[rev2] = lev2
        
        l_face_edges = om.MIntArray()
        r_face_edges = om.MIntArray()
        
        poly_iter.setIndex(l_currentP, prev_index)
        poly_iter.getEdges(l_face_edges)
        poly_iter.setIndex(r_currentP, prev_index)
        poly_iter.getEdges(r_face_edges)
                   
        if l_face_edges.length() != r_face_edges.length():
            raise GeometryError('Geometry is not symmetrical.')
           
        util.createFromInt(0, 0)
        r_face_edge_verts = util.asInt2Ptr()
        util.createFromInt(0, 0)
        l_if_checked_verts = util.asInt2Ptr()  
        
        l_checked_vert = l_non_checked_vert = 0
        
        # loop over face edges    
        for l_face_edge_index in l_face_edges:            
            # if edge already been checked, continue
            if checked_edges[l_face_edge_index] != -1:
                continue
                
            edge_iter.setIndex(l_currentE, prev_index)
            
            # is it connected to the current edge or opposite, don't use opposite
            if not edge_iter.connectedToEdge(l_face_edge_index) or l_currentE == l_face_edge_index:
                continue
                
            # get edge verts
            fnMesh.getEdgeVertices(l_face_edge_index, l_if_checked_verts)
            lv1 = om.MScriptUtil.getInt2ArrayItem(l_if_checked_verts, 0, 0)
            lv2 = om.MScriptUtil.getInt2ArrayItem(l_if_checked_verts, 0, 1)
            
            # is first vert from source edge
            if lv1 in (lev1, lev2):
                # lv1 has been checked already 
                l_checked_vert = lv1
                l_non_checked_vert = lv2
            # is second vert from source edge
            elif lv2 in (lev1, lev2):
                # lv2 has been checked already
                l_checked_vert = lv2
                l_non_checked_vert = lv1
            else:
                continue
            
            l_checked_state = 0
            if checked_verts[lv1] != -1: l_checked_state += 1
            if checked_verts[lv2] != -1: l_checked_state += 1
                    
            for r_face_edge_index in r_face_edges:
                edge_iter.setIndex(r_currentE, prev_index)
                
                if not edge_iter.connectedToEdge(r_face_edge_index) or r_currentE == r_face_edge_index:
                    continue
    
                # get edge verts
                fnMesh.getEdgeVertices(r_face_edge_index, r_face_edge_verts)   
                rv1 = om.MScriptUtil.getInt2ArrayItem(r_face_edge_verts, 0, 0)
                rv2 = om.MScriptUtil.getInt2ArrayItem(r_face_edge_verts, 0, 1)

                
                l_checked_mirror     = checked_verts[l_checked_vert]
                
                if rv1 == l_checked_mirror or rv2 == l_checked_mirror:
                    r_checked_state = 0
                    if checked_verts[rv1] != -1: r_checked_state += 1
                    if checked_verts[rv2] != -1: r_checked_state += 1
                    if l_checked_state != r_checked_state:
                        raise GeometryError('Geometry is not symmetrical.')
                    
                    l_edge_queue.append(l_face_edge_index)
                    r_edge_queue.append(r_face_edge_index)
                
                # is it the mirror of the checked vert
                if rv1 == l_checked_mirror:
                    checked_verts[l_non_checked_vert] = rv2
                    checked_verts[rv2] = l_non_checked_vert
                    side_verts[l_non_checked_vert] = 2
                    side_verts[rv2] = 1
                    break
                    
                elif rv2 == l_checked_mirror:
                    checked_verts[l_non_checked_vert] = rv1
                    checked_verts[rv1] = l_non_checked_vert
                    side_verts[l_non_checked_vert] = 2
                    side_verts[rv1] = 1
                    break

    average_a = average_b = 0
    point_pos = om.MPoint()
    
    # work out which side is which
    #
    total_len_x = 0
    for index in range(vert_count):
        mirror_vert = checked_verts[index]
        if mirror_vert != index and mirror_vert != -1:
            fnMesh.getPoint(mirror_vert, point_pos)
            if side_verts[index] == 2:
                total_len_x += 1
                average_b += point_pos.x
            elif side_verts[index] == 1:
                average_a += point_pos.x
    
    if average_a < average_b: switch_side = True
    else:                     switch_side = False
    
    # create an array of which side each vert is on, and an array of each verts mirror
    #
    side_map = []; mirror_map = []
    for index in range(vert_count):
        mirror_map.append(checked_verts[index])
        if checked_verts[index] != index:
            if not switch_side:
                side_map.append(side_verts[index])
            else:
                if side_verts[index] == 1:
                    side_map.append(2)
                else:
                    side_map.append(1)
        else:
            side_map.append(0)

    # if side was requested
    #
    if sides is True:
        return side_map

    # if mirrors were requested
    #
    if mirrors is True:
        return mirror_map
    
    # return mirror sets instead
    #   
    left_verts   = []
    center_verts = []
    right_verts  = []
    
    mirror_dict = {}
    for index, (side, mirror) in enumerate(zip(side_map, mirror_map)):
        if side == 2: 
            continue
        if side == 0: 
            center_verts.append(index); 
            continue       
        mirror_dict[index] = mirror
        
    for key, value in mirror_dict.items():
        left_verts.append(value); right_verts.append(key)    
                        
    return left_verts, center_verts, right_verts

#--------------------------------------------------------------------------------------------------#

def getAllVertexPositions(geometry, world_space=True):
    if geometry and not mc.objExists(geometry):
        raise RuntimeError("Object '%s' does not exist." %geometry)
    
    return _getAllVertexPositions(geometry, world_space)


def _getAllVertexPositions(geometry, world_space=True):
    # Get points to generate weights from
    #
    vert_list = om.MPointArray()
    
    sel_list = om.MSelectionList()
    sel_list.add(geometry)
    mesh = om.MObject()
    sel_list.getDependNode(0, mesh)

    vert_positions = []
    vertex_iter = om.MItMeshVertex(mesh)
    if world_space:
        space = om.MSpace.kWorld
    else:
        space = om.MSpace.kObject
        
    while not vertex_iter.isDone():
        point = vertex_iter.position(space)
        vert_positions.append([point[0], point[1], point[2]])
        vertex_iter.next()
    
    return vert_positions

#--------------------------------------------------------------------------------------------------#    

def mirrorGeometry(center_edge, mirror='lf'):
    lf_verts, cn_verts, rt_verts = getSymmetry(center_edge)
    geometry = center_edge.split('.')[0]
    
    vert_positions = getAllVertexPositions(center_edge.split('.')[0], world_space=False)
    if mirror == 'lf':
        src = lf_verts; dst = rt_verts
    else:
        src = rt_verts; dst = lf_verts
    
    for src_vert, dst_vert in zip(src, dst):
        src_pos = vert_positions[src_vert]        
        mc.move(src_pos[0] * -1, src_pos[1], src_pos[2], 
                '%s.vtx[%s]' %(geometry, dst_vert), a=True, os=True)
        
    for cn_vert in cn_verts:
        cn_pos = vert_positions[cn_vert]
        mc.move(0, cn_pos[1], cn_pos[2], 
                '%s.vtx[%s]' %(geometry, cn_vert), a=True, os=True)


def mirrorGeometryLeftToRight(center_edge):
    mirrorGeometry(center_edge, mirror='lf')

    
def mirrorGeometryRightToLeft(center_edge):
    mirrorGeometry(center_edge, mirror='rt')
    
#--------------------------------------------------------------------------------------------------#