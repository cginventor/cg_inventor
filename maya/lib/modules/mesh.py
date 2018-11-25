import maya.cmds as mc
import maya.OpenMaya as om
import math

from .module import Module, ModuleError 

from cs_rigging.utils.constants import LEFT, CENTER, RIGHT


class MeshError(ModuleError):
    pass


class Mesh(Module):    
    def __init__(self, name=None):
        Module.__init__(self)
        self._mObject = None
        self._mDagPath = None

        self._mirror_sets = {LEFT:None, RIGHT:None, CENTER:None}
        
        self.node = name  
    
    
    def create(self, name, vertices=None, face_vert_list=None, uvs=None):
        self.node = name

        if vertices and face_vert_list:
            self._create(name, vertices, face_vert_list, uvs)
        else:
            raise MeshError("Not Enough information provided."
                            "Requires vertices and face lists.")        
            

    def _create(self, name, vertices, face_vert_list, uvs=None):
        num_faces = len(face_vert_list)
        num_verts = len(vertices)

        face_vert_count =  om.MIntArray()
        face_connects = om.MIntArray()

        for face_vert in face_vert_list:
            face_vert_count.append(len(face_vert))
            for vert in face_vert:
                face_connects.append(vert)

        points = om.MFloatPointArray()

        for vert in vertices:
            p = om.MFloatPoint(vert[0], vert[1], vert[2])
            points.append(p)

        transform_fn = om.MFnTransform()
        output_mesh = transform_fn.create()
        transform_fn.setName(name)

        if uvs:
            u = om.MFloatArray()
            v = om.MFloatArray()
            uv_id = om.MIntArray()
            uv_count = om.MIntArray()

            uv_count = face_vert_count
            uv_id = face_connects

            for uv in uvs:
                u.append(uv[0])
                v.append(uv[1])

            mesh_fn = om.MFnMesh()
            mesh_fn.create(num_verts, num_faces, points, face_vert_count, face_connects, u, v, output_mesh)

            mesh_fn.updateSurface()
            mesh_fn.assignUVs(uv_count, uv_id)

        else:
            mesh_fn = om.MFnMesh()
            mesh_fn.create(num_verts, num_faces, points, face_vert_count, face_connects, output_mesh)
            mesh_fn.updateSurface()

        mesh_fn.setName('{}Shape'.format(name))

    #-----------------------------------------------------------------------------------------#
    
    @staticmethod
    def _getSymmetry(center_edge, sets=True, sides=False, mirrors=False):
        sel_list = om.MSelectionList()
        sel_list.add(center_edge)
        sel_shape = om.MDagPath()
        sel_iter = om.MItSelectionList(sel_list)
        
        component = om.MObject()
        sel_iter.getDagPath(sel_shape, component)
    
        sel_edges = om.MItMeshEdge(sel_shape, component)
        first_edge = sel_edges.index()
        fn_mesh = om.MFnMesh(sel_shape)
    
        vert_count = fn_mesh.numVertices()
        side_verts = [-1] * vert_count
        checked_verts = [-1] * vert_count
        checked_polygons = [-1] * fn_mesh.numPolygons()
        checked_edges = [-1] * fn_mesh.numEdges()
    
        poly_iter = om.MItMeshPolygon(sel_shape)
        edge_iter = om.MItMeshEdge(sel_shape)
    
        lf_edge_queue = om.MIntArray()
        rt_edge_queue = om.MIntArray()
    
        lf_edge_queue.append(first_edge)
        rt_edge_queue.append(first_edge)
    
        lf_face_list = om.MIntArray()
        rt_face_list = om.MIntArray()
    
        lf_curr_edge = lf_curr_poly = rt_curr_edge = rt_curr_poly = 0
    
        util = om.MScriptUtil()
        util.createFromInt(0)
        prev_index = util.asIntPtr()
    
        lf_edge_verts_util = om.MScriptUtil()
        rt_edge_verts_util = om.MScriptUtil()
        rt_face_edge_verts_util = om.MScriptUtil()
        lf_if_checked_verts_util = om.MScriptUtil()
    
        while len(lf_edge_queue) > 0:
            lf_curr_edge = lf_edge_queue[0]
            rt_curr_edge = rt_edge_queue[0]
    
            lf_edge_queue.remove(0)
            rt_edge_queue.remove(0)
    
            if lf_curr_edge == rt_curr_edge and lf_curr_edge != first_edge:
                continue
    
            checked_edges[lf_curr_edge] = rt_curr_edge
            checked_edges[rt_curr_edge] = lf_curr_edge
    
            edge_iter.setIndex(lf_curr_edge, prev_index)
            edge_iter.getConnectedFaces(lf_face_list)
            if lf_face_list.length() != 2:
                continue
            f1, f2 = lf_face_list
    
            if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
                lf_curr_poly = f1
            elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
                lf_curr_poly = f2
            elif checked_polygons[f1] == -1 and checked_polygons[f2] == -1:
                lf_curr_poly = f1
                checked_polygons[f1] = -2
    
            edge_iter.setIndex(rt_curr_edge, prev_index)
            edge_iter.getConnectedFaces(rt_face_list)
            f1, f2 = rt_face_list
    
            if checked_polygons[f1] == -1 and checked_polygons[f2] != -1:
                rt_curr_poly = f1
            elif checked_polygons[f1] != -1 and checked_polygons[f2] == -1:
                rt_curr_poly = f2
            elif checked_polygons[f2] == -1 and checked_polygons[f1] == -1:
                raise MeshError('Topology is invalid.')
            else:
                continue
    
            checked_polygons[rt_curr_poly] = lf_curr_poly
            checked_polygons[lf_curr_poly] = rt_curr_poly
    
    
            lf_edge_verts_util.createFromInt(0, 0)
            lf_edge_verts = lf_edge_verts_util.asInt2Ptr()
            rt_edge_verts_util.createFromInt(0, 0)
            rt_edge_verts = rt_edge_verts_util.asInt2Ptr()
    
            fn_mesh.getEdgeVertices(lf_curr_edge, lf_edge_verts)
            lf_edge_vert_1 = om.MScriptUtil.getInt2ArrayItem(lf_edge_verts, 0, 0)
            lf_edge_vert_2 = om.MScriptUtil.getInt2ArrayItem(lf_edge_verts, 0, 1)
    
            fn_mesh.getEdgeVertices(rt_curr_edge, rt_edge_verts)
            rt_edge_vert_1 = om.MScriptUtil.getInt2ArrayItem(rt_edge_verts, 0, 0)
            rt_edge_vert_2 = om.MScriptUtil.getInt2ArrayItem(rt_edge_verts, 0, 1)
    
            if lf_curr_edge == first_edge:
                checked_verts[lf_edge_vert_1] = rt_edge_vert_1
                checked_verts[lf_edge_vert_2] = rt_edge_vert_2
                checked_verts[rt_edge_vert_1] = lf_edge_vert_1
                checked_verts[rt_edge_vert_2] = lf_edge_vert_2
    
            lf_face_edges = om.MIntArray()
            rt_face_edges = om.MIntArray()
    
            poly_iter.setIndex(lf_curr_poly, prev_index)
            poly_iter.getEdges(lf_face_edges)
            poly_iter.setIndex(rt_curr_poly, prev_index)
            poly_iter.getEdges(rt_face_edges)
    
            if lf_face_edges.length() != rt_face_edges.length():
                raise MeshError('Mesh is not symmetrical.')
    
            rt_face_edge_verts_util.createFromInt(0, 0)
            rt_face_edge_verts = rt_face_edge_verts_util.asInt2Ptr()
            lf_if_checked_verts_util.createFromInt(0, 0)
            lf_if_checked_verts = lf_if_checked_verts_util.asInt2Ptr()
    
            lf_checked_vert = lf_non_checked_vert = 0
    
            for lf_face_edge_index in lf_face_edges:
                if checked_edges[lf_face_edge_index] != -1:
                    continue
    
                edge_iter.setIndex(lf_curr_edge, prev_index)
    
                connected = edge_iter.connectedToEdge(lf_face_edge_index)
                if not connected or lf_curr_edge == lf_face_edge_index:
                    continue
    
                fn_mesh.getEdgeVertices(lf_face_edge_index, lf_if_checked_verts)
                lf_vert_1 = om.MScriptUtil.getInt2ArrayItem(lf_if_checked_verts, 0, 0)
                lf_vert_2 = om.MScriptUtil.getInt2ArrayItem(lf_if_checked_verts, 0, 1)
    
                if lf_vert_1 in (lf_edge_vert_1, lf_edge_vert_2):
                    lf_checked_vert     = lf_vert_1
                    lf_non_checked_vert = lf_vert_2
                elif lf_vert_2 in (lf_edge_vert_1, lf_edge_vert_2):
                    lf_checked_vert     = lf_vert_2
                    lf_non_checked_vert = lf_vert_1
                else:
                    continue
    
                lf_checked_state = 0
                if checked_verts[lf_vert_1] != -1: lf_checked_state += 1
                if checked_verts[lf_vert_2] != -1: lf_checked_state += 1
    
                for rt_face_edge_index in rt_face_edges:
                    edge_iter.setIndex(rt_curr_edge, prev_index)
    
                    connected = edge_iter.connectedToEdge(rt_face_edge_index)
                    if not connected or rt_curr_edge == rt_face_edge_index:
                        continue
    
                    fn_mesh.getEdgeVertices(rt_face_edge_index, rt_face_edge_verts)
                    rt_vert_1 = om.MScriptUtil.getInt2ArrayItem(rt_face_edge_verts, 0, 0)
                    rt_vert_2 = om.MScriptUtil.getInt2ArrayItem(rt_face_edge_verts, 0, 1)
    
                    lf_checked_mirror = checked_verts[lf_checked_vert]
                    if rt_vert_1 == lf_checked_mirror or rt_vert_2 == lf_checked_mirror:
                        rt_checked_state = 0
                        if checked_verts[rt_vert_1] != -1: rt_checked_state += 1
                        if checked_verts[rt_vert_2] != -1: rt_checked_state += 1
                        if lf_checked_state != rt_checked_state:
                            raise MeshError('Mesh is not symmetrical.')
    
                        lf_edge_queue.append(lf_face_edge_index)
                        rt_edge_queue.append(rt_face_edge_index)
    
                    if rt_vert_1 == lf_checked_mirror:
                        checked_verts[lf_non_checked_vert] = rt_vert_2
                        checked_verts[rt_vert_2] = lf_non_checked_vert
                        side_verts[lf_non_checked_vert] = 2
                        side_verts[rt_vert_2] = 1
                        break
    
                    elif rt_vert_2 == lf_checked_mirror:
                        checked_verts[lf_non_checked_vert] = rt_vert_1
                        checked_verts[rt_vert_1] = lf_non_checked_vert
                        side_verts[lf_non_checked_vert] = 2
                        side_verts[rt_vert_1] = 1
                        break
    
        average_a = average_b = 0
        point_pos = om.MPoint()
    
        total_len_x = 0
        for index in range(vert_count):
            mirror_vert = checked_verts[index]
            if mirror_vert != index and mirror_vert != -1:
                fn_mesh.getPoint(mirror_vert, point_pos)
                if side_verts[index] == 2:
                    total_len_x += 1
                    average_b += point_pos.x
                elif side_verts[index] == 1:
                    average_a += point_pos.x
    
        if average_a < average_b:
            switch_side = True
        else:
            switch_side = False
    
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
    
        if sides is True:
            return side_map
    
        if mirrors is True:
            return mirror_map
    
        lf_verts = []
        cn_verts = []
        rt_verts = []
    
        mirror_dict = {}
        for index, (side, mirror) in enumerate(zip(side_map, mirror_map)):
            if side == 0:
                cn_verts.append(index);
                continue
            if side == 2:
                continue
            mirror_dict[index] = mirror
    
        for rt_vert, lf_vert in mirror_dict.items():
            lf_verts.append(lf_vert)
            rt_verts.append(rt_vert)
    
        return lf_verts, cn_verts, rt_verts  
    
    
    def createMirrorSets(self, center_edge):
        self._isSet()
        
        if isinstance(center_edge, int):
            center_edge = '{}.e[{}]'.format(self.node, center_edge)
            
        self._createMirrorSets(center_edge)
    
    
    def _createMirrorSets(self, center_edge):
        lf, cn, rt = self._getSymmetry(center_edge)
        self._mirror_sets[LEFT] = lf
        self._mirror_sets[CENTER] = cn
        self._mirror_sets[RIGHT] = rt
        
    
    def getMirrorSets(self):
        self._isSet()
        if self._mirror_sets.values() == [None, None, None]:
            raise MeshError("No Symmetry Sets Stored.")
        return self._mirror_sets


    def mirrorLeftToRight(self, vert_index):
        return self._getOpposite(vert_index, LEFT, RIGHT)        


    def mirrorRightToLeft(self, vert_index):
        return self._getOpposite(vert_index, RIGHT, LEFT)
    
    
    def mirror(self, vert_index):
        side = self.getSide(vert_index)
        if side == CENTER: return vert_index
        
        if side == LEFT:
            return self.mirrorLeftToRight(vert_index)
        elif side == RIGHT:
            return self.mirrorRightToLeft(vert_index)

    
    def _getOpposite(self, vert_index, from_side, to_side):
        mirror_sets = self.getMirrorSets()
        try:
            index = mirror_sets[from_side].index(vert_index)
        except KeyError:
            raise MeshError("Do not recognize side '{}'.".format(from_side))
        except ValueError:
            raise MeshError("Vertex Index is not on '{}' side.".format(from_side))
        
        return mirror_sets[to_side][index]
        
    #-----------------------------------------------------------------------------------------#

    def isVertexLeft(self, vert_index):
        return self._testVertexSide(vert_index, LEFT)    
    

    def isVertexRight(self, vert_index):
        return self._testVertexSide(vert_index, RIGHT)    

    
    def isVertexCenter(self, vert_index):
        return self._testVertexSide(vert_index, CENTER)
    

    def _testVertexSide(self, vert_index, side):
        if vert_index in set(self.getMirrorSets()[side]):
            return True
        return False    
    
    
    def getVertexSide(self, vert_index):
        if self.isVertexLeft(vert_index):
            return LEFT
        if self.isVertexRight(vert_index):
            return RIGHT
        if self.isVertexCenter(vert_index):
            return CENTER
        
    #-----------------------------------------------------------------------------------------#        
        
    def getVertCount(self):
        self._isSet()
        return mc.polyEvaluate(self.node, v=True)
    
    
    def getEdgeCount(self):
        self._isSet()
        return mc.polyEvaluate(self.node, e=True)
    
    
    def getFaceCount(self):
        self._isSet()
        return mc.polyEvaluate(self.node, f=True)
    
    #-----------------------------------------------------------------------------------------#
    
    def _getMObject(self):
        if not self._mObject:
            selection_list = om.MSelectionList()
            selection_list.add(self.node)
            self._mObject = om.MObject()
            selection_list.getDependNode(0, self._mObject)
        return self._mObject


    def _getMDagPath(self):
        if not self._mDagPath:
            selection_list = om.MSelectionList()
            selection_list.add(self.node)
            self._mDagPath = om.MDagPath()
            selection_list.getDagPath(0,self._mDagPath)
        return self._mDagPath
    
    #-----------------------------------------------------------------------------------------#    
    
    def getVertexPosition(self, vertex_index, os=True, ws=False):
        self._isSet()
    
        vertex_iter = om.MItMeshVertex(self._getMDagPath())
        
        if vertex_index < 0 or vertex_index > (vertex_iter.count() - 1):
            raise MeshError("Vertx index '{}' is out of range.".format(vertex_index))
        
        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        prev_index = util.asIntPtr()         
        
        vertex_iter.setIndex(vertex_index, prev_index)        
        point = vertex_iter.position(om.MSpace.kWorld)

        return (point[0], point[1], point[2])
    
    
    def setVertexPosition(self, vert_index, position):
        self._isSet()

        vertex_iter = om.MItMeshVertex(self._getMDagPath())
        
        if vertex_index < 0 or vertex_index > (vertex_iter.count() - 1):
            raise MeshError("Vertx index '{}' is out of range.".format(vertex_index))

        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        prev_index = util.asIntPtr()
        
        vertex_iter.setIndex(vertex_index, prev_index)
        
        if isinstance(position, (tuple, list)):
            position = om.MPoint(position[0], position[1], position[2], 1.0)

        vertex_iter.setPosition(position, om.MSpace.kWorld)
    
    
    def getAllVertexPositions(self, asMPoint=False):
        self._isSet()
        
        vertex_iter = om.MItMeshVertex(self._getMDagPath())
        
        point_positions = {}
        while not vertex_iter.isDone():
            index = vertex_iter.index()
            point_positions[index] = vertex_iter.position(om.MSpace.kWorld)
            vertex_iter.next()
        
        if asMPoint:
            return point_positions
        
        vert_positions = {}
        for vert_index, point in point_positions.items():
            vert_positions[vert_index] = (point[0], point[1], point[2])
            
        return vert_positions
        
    
    def setVertexPosition(self, vertex_index, position):
        self._isSet()
        
        vertex_iter = om.MItMeshVertex(self._getMDagPath())

        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        prev_index = util.asIntPtr()
        
        vertex_iter.setIndex(vertex_index, prev_index)
        
        if isinstance(position, (tuple, list)):
            position = om.MPoint(position[0], position[1], position[2], 1.0)

        vertex_iter.setPosition(position, om.MSpace.kWorld)
    
    
    def getVertexNormal(self, vertex_index, asMVector=False):
        self._isSet()
        
        vertex_iter = om.MItMeshVertex(self._getMDagPath())
        
        if vertex_index < 0 or vertex_index > (vertex_iter.count() - 1):
            raise MeshError("Vertex index '{}' is out of range.".format(vertex_index))
        
        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        pInt = util.asIntPtr()
        
        normal = om.MVector()
        vertex_iter.setIndex(vertex_index, pInt)
        vertex_iter.getNormal(normal, om.MSpace.kWorld)
        
        if asMVector:
            return normal
        
        return (normal[0], normal[1], normal[2])
    
    
    def getOrientationAtVertex(self, vertex_index, up_vector=(0,1,0)):        
        normal = self.getVertexNormal(vertex_index, asMVector=True)
        up = om.MVector(up_vector[0], up_vector[1], up_vector[2])
        up.normalize()
        
        tangent = up ^ normal
        up = normal ^ tangent
        
        normal.normalize()
        up.normalize()
        tangent.normalize()
        
        atan2 = math.atan2
        power = math.pow
        degrees = math.degrees
        sqrt = math.sqrt
        
        rot_x = degrees(atan2(up[2], normal[2]))
        rot_y = degrees(atan2(-tangent[2], sqrt(power(up[2], 2) + power(normal[2], 2))))
        rot_z = degrees(atan2(tangent[1], tangent[0]))
        
        return (rot_x, rot_y, rot_z)
    
    #-----------------------------------------------------------------------------------------#

    def getShapes(self):
        self._isSet()
        
        return mc.listRelatives(self.node, s=True)    
    
    #-----------------------------------------------------------------------------------------#

    def vertexToFaces(self, vertex_index):
        self._isSet()

        vertex_iter = om.MItMeshVertex(self._getMObject())
        
        if vertex_index < 0 or vertex_index > (vertex_iter.count() - 1):
            raise MeshError("Edge index '{}' out of range.".format(vertex_index))

        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        prev_index = util.asIntPtr()
        
        vertex_iter.setIndex(vert_index, prev_index)
        
        faces = om.MIntArray()
        vertex_iter.getConnectedFaces(faces)
        return list(faces)    
    
    
    def vertexToEdges(self, vertex_index):
        self._isSet()
        
        vertex_iter = om.MItMeshVertex(self._getMObject())
        
        if vertex_index < 0 or vertex_index > (vertex_iter.count() - 1):
            raise MeshError("Edge index '{}' out of range.".format(vertex_index))

        util = om.MScriptUtil()
        util.createFromInt(vertex_iter.index())
        prev_index = util.asIntPtr()
        
        vertex_iter.setIndex(vertex_index, prev_index)
        
        edges = om.MIntArray()
        vertex_iter.getConnectedEdges(edges)
        return list(edges)
    
    
    def edgeToFaces(self, edge_index):
        self._isSet()
        
        edge_iter = om.MItMeshEdge(self._getMObject())
        
        if edge_index < 0 or edge_index > (edge_iter.count() - 1):
            raise MeshError("Edge index '{}' out of range.".format(edge_index))
        
        util = om.MScriptUtil()
        util.createFromInt(edge_iter.index())
        prev_index = util.asIntPtr()
        
        edge_iter.setIndex(edgeIndex, prev_index)
        
        faces = om.MIntArray()
        edge_iter.getConnectedFaces(faces)
        return list(faces)
    
    
    def edgeToVerts(self, edge_index):
        self._isSet()
        
        edge_iter = om.MItMeshEdge(self._getMObject())
        
        if edge_index < 0 or edge_index > (edge_iter.count() - 1):
            raise MeshError("Edge index '{}' out of range.".format(edge_index))
        
        util = om.MScriptUtil()
        util.createFromInt(edge_iter.index())
        prev_index = util.asIntPtr()
        
        edge_iter.setIndex(edge_index, prev_index)
        
        return [edge_iter.index(0), edge_iter.index(1)]
    
    
    def getConnectedEdges(self, edge_index):
        self._isSet()
        
        edge_iter = om.MItMeshEdge(self._getMObject())
        
        if edge_index < 0 or edge_index > (edge_iter.count() - 1):
            raise MeshError("Edge index '{}' out of range.".format(edge_index))
        
        util = om.MScriptUtil()
        util.createFromInt(edge_iter.index())

        edge_iter.setIndex(edge_index, util.asIntPtr())
        
        edges = om.MIntArray()
        edge_iter.getConnectedEdges(edges)
        return list(edges)
    
    
    def faceToEdges(self, face_index):
        self._isSet()
        
        face_iter = om.MItMeshPolygon(self._getMObject())
        
        if face_index < 0 or face_index > (face_iter.count() - 1):
            raise MeshError("Face index '{}' out of range.".format(face_index))
        
        util = om.MScriptUtil()
        util.createFromInt(face_iter.index())
        prev_index = util.asIntPtr()
        
        face_iter.setIndex(face_index, prev_index)
        
        edges = om.MIntArray()
        face_iter.getConnectedEdges(edges)
        return list(edges)
        
    
    def faceToVertices(self, face_index):
        self._isSet()
        
        polygon_iter = om.MItMeshPolygon(self._getMObject())
        
        if face_index < 0 or face_index > (face_index.count() - 1):
            raise MeshError("Face index '{}' out of range.".format(face_index))

        util = om.MScriptUtil()
        util.createFromInt(polygon_iter.index())
        prev_index = util.asIntPtr()
        
        polygon_iter.setIndex(face_index, prev_index)
        
        verts = om.MIntArray()
        polygon_iter.getVertices(verts)
        return list(verts)
    
    #------------------------------------------------------------------------------------------#
    
    def getBorderVerts(self):
        self._isSet()
        
        vertex_iter = om.MItMeshVertex(self._getMObject())

        border_verts = []
        while not vertex_iter.isDone():
            if vertex_iter.onBoundary():
                border_verts.append(vertex_iter.index())
            vertex_iter.next()

        return border_verts


    def getBorderFaces(self):
        self._isSet()
        
        mesh_iter = om.MItMeshPolygon(self._getMObject())

        border_faces = []
        while not mesh_iter.isDone():
            if mesh_iter.onBoundary():
                border_faces.append(mesh_iter.index())
            mesh_iter.next()

        return border_faces


    def getHardEdges(self):
        self._isSet()
        
        edge_iter = om.MItMeshEdge(self._getMObject())

        hard_edges = []
        while not edge_iter.isDone():
            if not edge_iter.isSmooth():
                hard_edges.append(edge_iter.index())
            edge_iter.next()

        return hard_edges


    def getLockedVertNormals(self):
        self._isSet()
        
        mesh_fn = om.MFnMesh(self._getMDagPath())
        normal_ids = om.MIntArray()

        mesh_fn.getNormalIds(om.MIntArray(), normal_ids)

        locked_vertices = []
        for normal_id in normal_ids:
            if mesh_fn.isNormalLocked(normal_id):
                locked_vertices.append(normal_id)

        return locked_vertices
    
    