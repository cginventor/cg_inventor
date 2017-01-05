import maya.cmds as mc
from math import cos, sin, radians, degrees
import maya.OpenMaya as om

import dimensions, category; reload(dimensions)

knob_subdivisions = dimensions.KNOB_SUBDIVISIONS
degree_step = 360.0 / knob_subdivisions
cosines = [cos(radians(degree_step * index)) for index in range(knob_subdivisions)]
sines   = [sin(radians(degree_step * index)) for index in range(knob_subdivisions)]
math_rotations = dict(zip(range(knob_subdivisions), zip(cosines, sines)))
del(knob_subdivisions, degree_step, cosines, sines)


_knob_cache     = {}
_cylinder_cache = {}


class Piece(object):
    def __init__(self, name='untitled'):
        self.name     = name        
        self.category = ''
        
        self._construct = None
        
    #------------------------------------------------------------------------------------------#
        
    def createKnob(self, x, y, z, height, radius, hollow_radius=0, flip=False):    
        if self._construct is None: return

        global _knob_cache
        try:
            cache_key = (radius, hollow_radius)
            knob_cache = _knob_cache[cache_key]            
        except KeyError:            
            knob_subdivisions = dimensions.KNOB_SUBDIVISIONS
            knob_smooth       = dimensions.SMOOTH_OFFSET
            knob_smooth_45    = dimensions.SMOOTH_45_OFFSET
                       
            knob_cache = _knob_cache[cache_key] = [None for _ in range(knob_subdivisions)]
            
            smooth_radius    = radius + knob_smooth
            smooth_45_radius = radius - knob_smooth_45
            
            if hollow_radius == 0:            
                for index in range(knob_subdivisions):
                    rx, rz = math_rotations[index]
                    vert_line = knob_cache[index] = [None for _ in range(5)]               
                    
                    knob_x, knob_z = rx * smooth_radius, rz * smooth_radius                
                    vert_line[0] = (knob_x, 0, knob_z, 0)
                    
                    knob_x, knob_z = rx * radius, rz * radius
                    vert_line[1] = (knob_x,               0, knob_z, 0)
                    vert_line[2] = (knob_x,     knob_smooth, knob_z, 0)
                    vert_line[3] = (knob_x, -knob_smooth_45, knob_z, 1)
                    
                    knob_x, knob_z = rx * smooth_45_radius, rz * smooth_45_radius
                    vert_line[4] = (knob_x, 0, knob_z, 1)
                    
            else:
                smooth_neg_radius        = (radius - knob_smooth)
                hollow_smooth_radius     = (hollow_radius + knob_smooth)
                hollow_smooth_neg_radius = (hollow_radius - knob_smooth)
                
                for index in range(knob_subdivisions):
                    rx, rz = math_rotations[index]
                    vert_line = knob_cache[index] = [None for _ in range(12)]

                    knob_x, knob_z = rx * smooth_radius, rz * smooth_radius                                        
                    vert_line[0] = (knob_x, 0, knob_z, 0)
                    
                    knob_x, knob_z = rx * radius, rz * radius
                    vert_line[1] = (knob_x,            0, knob_z, 0)
                    vert_line[2] = (knob_x,  knob_smooth, knob_z, 0)
                    vert_line[3] = (knob_x, -knob_smooth, knob_z, 1)
                    vert_line[4] = (knob_x,            0, knob_z, 1)
                    
                    knob_x, knob_z = rx * smooth_neg_radius, rz * smooth_neg_radius               
                    vert_line[5] = (knob_x, 0, knob_z, 1)
                    
                    knob_x, knob_z = rx * hollow_smooth_radius, rz * hollow_smooth_radius               
                    vert_line[6] = (knob_x, 0, knob_z, 1)
                    
                    knob_x, knob_z = rx * hollow_radius, rz * hollow_radius
                    vert_line[7]  = (knob_x,            0, knob_z, 1)
                    vert_line[8]  = (knob_x, -knob_smooth, knob_z, 1)
                    vert_line[9]  = (knob_x,  knob_smooth, knob_z, 0)
                    vert_line[10] = (knob_x,            0, knob_z, 0)
                    
                    knob_x, knob_z = rx * hollow_smooth_neg_radius, rz * hollow_smooth_neg_radius
                    vert_line[11] = (knob_x, 0, knob_z, 0)


        heights = {0:y, 1:y + height}
        all_vert_line_ids = []
        for line_index in range(len(knob_cache)):
            vert_line = []
            
            cache = knob_cache[line_index]
            for index in range(len(cache)):
                cx, cy, cz, h = cache[index]
                vert_line.append((x + cx, heights[h] + cy, z + cz))                    
            
            all_vert_line_ids.append(self._construct.addVertex(vert_line))
        all_vert_line_ids.append(all_vert_line_ids[0])


        polygons = []
        knob_center_id = self._construct.addVertex((x, heights[not(bool(hollow_radius))], z))
        for index in range(len(all_vert_line_ids)-1):
            a, b = all_vert_line_ids[index:index+2]

            edge_polygons = [(a[-1], knob_center_id, b[-1])]
            for index in range(len(a)-1):
                edge_polygons.append((a[index+1], b[index+1], b[index], a[index]))
            
            if flip:
                edge_polygons = [edge_polygon[::-1] for edge_polygon in edge_polygons]
                
            polygons.extend(edge_polygons)         
        polygon_ids = self._construct.addPolygon(polygons)        
        
        return [line[0] for line in all_vert_line_ids[:-1]]
    
    #------------------------------------------------------------------------------------------#
    
    def createCylinder(self, x, y1, y2, z, inner_radius, outer_radius):
        if self._construct is None: return
        
        global _cylinder_cache
        try:
            cache_key = (inner_radius, outer_radius)
            cylinder_cache = _cylinder_cache[cache_key]
        except KeyError:
            cyl_subdivisions = dimensions.KNOB_SUBDIVISIONS
            cyl_smooth       = dimensions.SMOOTH_OFFSET
            
            cylinder_cache = _cylinder_cache[cache_key] = [None for _ in range(cyl_subdivisions)]
            
            if inner_radius is not None:
                
                radius_diff = outer_radius - inner_radius
                adjusted_smooth = (radius_diff / 3.0) if ((radius_diff / 2.0) < cyl_smooth) else cyl_smooth
            
                for index in range(cyl_subdivisions):
                    rx, rz = math_rotations[index]
                    vert_line = cylinder_cache[index] = [None for _ in range(8)]
                    
                    cyl_x, cyl_z = rx * inner_radius, rz * inner_radius
                    vert_line[0] = (cyl_x,          0, cyl_z, 1) # inner top
                    vert_line[1] = (cyl_x, cyl_smooth, cyl_z, 0) # inner bttm side smooth
                    vert_line[2] = (cyl_x,          0, cyl_z, 0) # inner bttm                
                    
                    smooth_radius = inner_radius + adjusted_smooth
                    vert_line[3] = (rx * smooth_radius, 0, rz * smooth_radius, 0) # inner bttm smooth 
                    
                    smooth_radius = outer_radius - adjusted_smooth
                    vert_line[4] = (rx * smooth_radius, 0, rz * smooth_radius, 0) # outer bttm smooth
                    
                    cyl_x, cyl_z = rx * outer_radius, rz * outer_radius
                    vert_line[5] = (cyl_x,          0, cyl_z, 0) # outer bttm 
                    vert_line[6] = (cyl_x, cyl_smooth, cyl_z, 0) # outer bttm side smooth
                    vert_line[7] = (cyl_x,          0, cyl_z, 1) # outer top
                    
            else:
                adjusted_smooth = (outer_radius / 3.0) if ((outer_radius / 2.0) < cyl_smooth) else cyl_smooth
                
                for index in range(cyl_subdivisions):
                    rx, rz = math_rotations[index]
                    vert_line = cylinder_cache[index] = [None for _ in range(4)]
                    
                    smooth_radius = outer_radius - adjusted_smooth
                    vert_line[0] = (rx * smooth_radius, 0, rz * smooth_radius, 0) # outer bttm smooth
                    
                    cyl_x, cyl_z = rx * outer_radius, rz * outer_radius
                    vert_line[1] = (cyl_x,          0, cyl_z, 0) # outer bttm 
                    vert_line[2] = (cyl_x, cyl_smooth, cyl_z, 0) # outer bttm side smooth
                    vert_line[3] = (cyl_x,          0, cyl_z, 1) # outer top                    


        heights = {0:y1, 1:y2}
        all_vert_line_ids = []       
        for line_index in range(len(cylinder_cache)):
            vert_line = []
            
            cache = cylinder_cache[line_index]
            for index in range(len(cache)):
                cx, cy, cz, h = cache[index]
                vert_line.append((x + cx, heights[h] + cy, z + cz))
            
            all_vert_line_ids.append(self._construct.addVertex(vert_line))
        all_vert_line_ids.append(all_vert_line_ids[0])
        
        if inner_radius is None:
            center_vert_id = self._construct.addVertex((x, y1, z))

        polygons = []
        for index in range(len(all_vert_line_ids)-1):
            a, b = all_vert_line_ids[index:index+2]            
            
            for index in range(len(a)-1):
                polygons.append((a[index+1], b[index+1], b[index], a[index]))
            
            if inner_radius is None:
                polygons.append((a[0], b[0], center_vert_id))
                

        polygon_ids = self._construct.addPolygon(polygons)
        
        
        inner_vert_ids = [line[0]  for line in all_vert_line_ids[:-1]]
        outer_vert_ids = [line[-1] for line in all_vert_line_ids[:-1]]
        
        return inner_vert_ids, outer_vert_ids
    
#--------------------------------------------------------------------------------------------------#   

class ConstructError(Exception):
    pass
   

class Construct(object):
    def __init__(self):        
        self.vertices = []
        self.polygons = []
        self.mesh_fn = None

    #------------------------------------------------------------------------------------------#    

    def addVertex(self, vertex):
        if not hasattr(vertex, '__iter__'):
            raise ConstructError("Vertex must be a list or tuple of three floats. Got type '%s'." %type(vertex))
        
        if not hasattr(vertex[0], '__iter__'):
            if len(vertex) != 3:
                raise ConstructError("Vertex must be three floats. Got '%s'." %vertex)
            
            self.vertices.append(vertex)
            return len(self.vertices) - 1
        
        vertices = vertex
            
        vertex_ids = []
        for vertex in vertices:
            vertex_ids.append(len(self.vertices))
            self.vertices.append(vertex)
            
        return vertex_ids
    
    
    def getVertex(self, id):
        if isinstance(id, int):
            return self.vertices[id]
    
        elif hasattr(id, '__iter__'):
            vertices = []
            ids = id
            for id in ids:
                vertices.append(self.vertices[id])
            return vertices       
        
        raise ConstructError("Vertex ID must be a integer or list/tuple. Got type '%s'." %type(vertex))
        
    #------------------------------------------------------------------------------------------#        
    
    def addPolygon(self, polygon):
        if not hasattr(polygon, '__iter__'):
            raise ConstructError("Polygon must be a list or tuple of vertex ids. Got type '%s'." %type(polygon))
        
        if not hasattr(polygon[0], '__iter__'):
            if len(polygon) < 3:
                raise ConstructError("Polygons must be defined by at least 3 vertices.")
            
            self.polygons.append(polygon)
            return len(self.polygons) - 1
        
        polygons = polygon
        
        polygon_ids = []
        for polygon in polygons:
            polygon_ids.append(len(self.polygons))
            self.polygons.append(polygon)            
            
        return polygon_ids


    def getPolygon(self, polygon_id):
        try:
            return self.polygons[polygon_id]
        except IndexError:
            raise ConstructError("Polygon Id %s out of range." %polygon_id)
        
    #------------------------------------------------------------------------------------------#
    
    def build(self, name='untitled'):
        num_vertices = len(self.vertices)
        num_polygons = len(self.polygons)

        vertex_array = om.MFloatPointArray()
        vertex_array.setLength(num_vertices)
        
        scale_mult = dimensions.SCALE_MULT
        
        for index in range(num_vertices):
            x, y, z = self.vertices[index]
            x *= scale_mult; y *= scale_mult; z *= scale_mult
            vertex_array.set(om.MFloatPoint(x, y, z), index)
        
        polygon_counts = om.MIntArray()
        polygon_counts.setLength(num_polygons)
        polygon_connects = om.MIntArray()
        polygon_connects.setLength(sum([len(polygon) for polygon in self.polygons]))
        
        total_polygon_ids = 0
        for index in range(num_polygons):
            polygon_indices = self.polygons[index]
            num_polygon_verts = len(polygon_indices)
            
            polygon_counts.set(num_polygon_verts, index)
            
            for vertex_index in range(num_polygon_verts):
                polygon_connects.set(polygon_indices[vertex_index], total_polygon_ids + vertex_index)
                
            total_polygon_ids += num_polygon_verts
            
        transform_fn = om.MFnTransform()
        transform = transform_fn.create()
        
        transform_node = om.MFnDependencyNode(transform)
        transform_name = transform_node.setName(name)
                
        self.mesh_fn   = om.MFnMesh()
        mesh = self.mesh_fn.create(num_vertices, 
                                   num_polygons, 
                                   vertex_array, 
                                   polygon_counts, 
                                   polygon_connects,
                                   transform)
        
        mesh_node = om.MFnDependencyNode(mesh)
        mesh_name = mesh_node.setName('%sShape' %transform_name)
       
        return transform_name, mesh_name
    
    
    def getContainedEdges(self, vertex_indices):
        if self.mesh_fn == None:
            raise ConstructError("Construct has not been built.")
        
        util = om.MScriptUtil(0)
        prev_index = util.asIntPtr()
        
        connected_edges = om.MIntArray()        
        lookup = {}
                     
        mesh_vertex_fn = om.MItMeshVertex(self.mesh_fn.object())
        for vertex_index in vertex_indices:
            mesh_vertex_fn.setIndex(vertex_index, prev_index)
            mesh_vertex_fn.getConnectedEdges(connected_edges)
            for index in range(connected_edges.length()):
                try:
                    edges = lookup[connected_edges[index]]
                except KeyError:
                    edges = lookup[connected_edges[index]] = []
                edges.append(vertex_index)
        
        contained_edges = []
        for edge_index, vertices in lookup.items():
            if len(vertices) > 1:
                contained_edges.append(edge_index)
                
        return contained_edges