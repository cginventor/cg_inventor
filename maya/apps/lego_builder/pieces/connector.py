import maya.cmds as mc
from math import cos, sin, radians, degrees
import maya.OpenMaya as om

import dimensions, category; reload(dimensions)

import piece; reload(piece)
from .piece import Piece, Construct, ConstructError, xLine, yLine, zLine

knob_subdivisions = dimensions.KNOB_SUBDIVISIONS
degree_step = 360.0 / knob_subdivisions
cosines = [cos(radians(degree_step * index)) for index in range(knob_subdivisions)]
sines   = [sin(radians(degree_step * index)) for index in range(knob_subdivisions)]
math_rotations = dict(zip(range(knob_subdivisions), zip(cosines, sines)))
del(knob_subdivisions, degree_step, cosines, sines)

# global caches
#
_knob_cache     = {}
_cylinder_cache = {}
_plane_cache    = {}
_ridge_cache    = {}
    
#--------------------------------------------------------------------------------------------------#
    
class Connector(Piece):       
    def __init__(self, *args, **kwargs):
        Piece.__init__(self, *args, **kwargs)
        self.category = category.TECHNIC_CONNECTOR
        
        self._construct = None
        
        
    def createEndRing(self, x, y, radius, split=None):    
        if self._construct is None: return

        global _end_ring_cache
        try:
            cache_key = radius
            end_ring_cache = _end_ring_cache[cache_key]            
        except KeyError:            
            ring_subdivisions = dimensions.KNOB_SUBDIVISIONS
                       
            end_ring_cache = _end_ring_cache[cache_key] = [None for _ in range(ring_subdivisions)]
               
            for index in range(knob_subdivisions):
                rx, rz = math_rotations[index]
                vert_line = knob_cache[index] = [None for _ in range(12)]
    
                knob_x, knob_z = rx * smooth_radius, rz * smo3oth_radius                                        
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
        
        
    def create(self, height=1):
        self._construct = construct = Construct()

        AXIS_RADIUS = dimensions.AXEL_RADIUS
        
        for sin, cosine in (sin, cosines):
            
            