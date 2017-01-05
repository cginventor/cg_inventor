import maya.cmds as mc
from math import cos, sin, radians, degrees
import maya.OpenMaya as om

import dimensions, category; reload(dimensions)

import brick; reload(brick)
from .piece import Construct, ConstructError, math_rotations


_plane_cache      = {}
_hole_cache       = {}
_hole_outer_cache = {}
    
#--------------------------------------------------------------------------------------------------#
    
class TechnicBrick(brick.Brick):               
    def __init__(self, name='untitled'):
        brick.Brick.__init__(self, name)
        self.category = category.TECHNIC   

    #------------------------------------------------------------------------------------------#
    
    def createPlaneVertices(self, units_in_z, 
                                  y, 
                                  offset=0, 
                                  smooth=True,
                                  skip_set=set([])):
        vertices = []
        
        global _plane_cache
        try:
            vert_plane_template = _plane_cache[units_in_z]
        except KeyError:
            vert_plane_template = _plane_cache[units_in_z] = []

            unit           = dimensions.UNIT
            unit_offset    = dimensions.UNIT_OFFSET
            smooth_offset  = dimensions.SMOOTH_OFFSET
            
            x1 = z1 = unit_offset

            x2 = x1 + unit - unit_offset
            z2 = z1 + (unit * units_in_z) - unit_offset
            
            panel_unit        = unit / 2.0
            panel_unit_offset = unit_offset / 2.0
            
            point_count = xrange((units_in_z * 2) + 1)
            for index in point_count:
                if index == point_count[0]:
                    vert_plane_template.append((x1, z1, self.CORNER))
                    vert_plane_template.append((x1, z1 + smooth_offset, self.SMOOTH))
                elif index == point_count[-1]:
                    vert_plane_template.append((x1, z2 - smooth_offset, self.SMOOTH)) 
                    vert_plane_template.append((x1, z2, self.CORNER))
                    vert_plane_template.append((x1 + smooth_offset, z2, self.SMOOTH))
                else:
                    z = z1 + (index * panel_unit) - panel_unit_offset
                    vert_plane_template.append((x1, z, self.EDGE))
                
            point_count = xrange(1, 3)
            for index in point_count:            
                if index == point_count[-1]:
                    vert_plane_template.append((x2 - smooth_offset, z2, self.SMOOTH))                
                    vert_plane_template.append((x2, z2, self.CORNER))
                    vert_plane_template.append((x2, z2 - smooth_offset, self.SMOOTH))
                else:
                    x = x1 + panel_unit - panel_unit_offset
                    vert_plane_template.append((x, z2, self.EDGE))
                      
            point_count = xrange((units_in_z * 2) -1, -1, -1)
            for index in point_count:
                if index == point_count[-1]:
                    vert_plane_template.append((x2, z1 + smooth_offset, self.SMOOTH))
                    vert_plane_template.append((x2, z1, self.CORNER))
                    vert_plane_template.append((x2 - smooth_offset, z1, self.SMOOTH))
                else:
                    z = z1 + (index * panel_unit) - panel_unit_offset
                    vert_plane_template.append((x2, z, self.EDGE))
                       
            point_count = xrange(1, 0, -1)
            for index in point_count:
                x = x1 + (index * panel_unit) - panel_unit_offset
                vert_plane_template.append((x, z1, self.EDGE))
                if index == point_count[-1]:
                    vert_plane_template.append((x1 + smooth_offset, z1, self.SMOOTH))
        
        vert_order = []
        if offset == 0:
            for index, template in enumerate(vert_plane_template):
                if index in skip_set:
                    vert_order.append(None) 
                    continue
                
                x, z, _ = template
                vert_order.append(len(vertices))
                vertices.append((x, y, z))                
                                    
        else:
            corner_offset = {1:(1,1), 2:(1,-1), 3:(-1,-1), 4:(-1,1), 5:(1,1)}
            edge_offset   = {1:(1,0), 2:(0,-1), 3:(-1, 0), 4:( 0,1)}
            
            corner_counter = 0; previous_vertex_type = vert_plane_template[-1][2]
            for index, template in enumerate(vert_plane_template):
                x, z, vertex_type = template
                if index in skip_set:
                    if vertex_type == self.CORNER:                        
                        corner_counter += 1
                    vert_order.append(None)
                    continue
                
                if vertex_type == self.CORNER: 
                    corner_counter += 1
                    x += corner_offset[corner_counter][0] * offset
                    z += corner_offset[corner_counter][1] * offset                                    
                elif vertex_type == self.SMOOTH:
                    if smooth == False: continue
                    
                    if previous_vertex_type == self.CORNER:
                        x += corner_offset[corner_counter][0] * offset
                        z += corner_offset[corner_counter][1] * offset
                    else:
                        x += corner_offset[corner_counter+1][0] * offset
                        z += corner_offset[corner_counter+1][1] * offset   
                else:
                    x += edge_offset[corner_counter][0] * offset
                    z += edge_offset[corner_counter][1] * offset
                
                vert_order.append(len(vertices))
                vertices.append((x, y, z))
                previous_vertex_type = vertex_type
        
        vert_ids = self._construct.addVertex(vertices)
        
        all_vert_ids = []
        for index in vert_order:
            if index is not None:
                all_vert_ids.append(vert_ids[index])
            else:
                all_vert_ids.append(None)
        
        return all_vert_ids
    
    
    
    def createPlanePolygons(self, units_in_z, vert_planes):
        for vert_plane in vert_planes:
            vert_plane.append(vert_plane[0])

        polygons = []
        for vert_plane_index in range(len(vert_planes) - 1):
            plane      = vert_planes[vert_plane_index]
            next_plane = vert_planes[vert_plane_index + 1]
            
            plane_len = len(plane); next_plane_len = len(next_plane) 
                
            if plane_len == next_plane_len:
                for vert_index in range(len(vert_planes[vert_plane_index]) - 1):
                    p1, p2, n1, n2 = plane[vert_index], plane[vert_index+1], \
                                     next_plane[vert_index+1], next_plane[vert_index]
                    if None in (p1, p2, n1, n2): continue
                    polygons.append((p1, p2, n1, n2))
                
            else:                
                if plane_len < next_plane_len:
                    small_plane = plane; large_plane = next_plane[:-1]
                    flip = True
                    num_polygons = len(polygons)
                else:
                    small_plane = next_plane; large_plane = plane[:-1]
                    flip = False
                    
                small_index = 0
                a = (2 * units_in_z) + 2
                b = a + (2) + 2
                c = b + a
                for large_index in range(len(large_plane) - 1):        
                    # add square corners
                    #
                    if large_index in (0, a, b, c):
                        s1, l1, l2, l3 = small_plane[small_index], large_plane[large_index-1], \
                                         large_plane[large_index], large_plane[large_index+1]
                        if None in (s1, l1, l2, l3): continue
                        polygons.append((s1, l1, l2, l3))                        
                        continue
                    
                    # skip the next vert row after square corner
                    #
                    elif large_index in (a-1, b-1, c-1): continue
                    
                    # connect vert rows
                    #
                    else:
                        s1, s2, l1, l2 = small_plane[small_index+1], small_plane[small_index], \
                                         large_plane[large_index],   large_plane[large_index+1]
                        if None not in (s1, s2, l1, l2):
                            polygons.append((s1, s2, l1, l2))
                        
                    small_index += 1
                
                if flip is True:
                    polygons[num_polygons:] = [polygon[::-1] for polygon in polygons[num_polygons:]]
                    
        
        return self._construct.addPolygon(polygons)
    
    
    def createHole(self, x1, x2, y, z, hole_radius, hole_border_radius):
        if self._construct is None: return

        global _hole_cache
        try:
            cache_key = (hole_radius, hole_border_radius)
            hole_cache = _hole_cache[cache_key]            
        except KeyError:            
            hole_subdivisions = dimensions.KNOB_SUBDIVISIONS
            hole_smooth       = dimensions.SMOOTH_OFFSET

            hole_border_depth  = dimensions.HOLE_BORDER_DEPTH
            hr, hbr = hole_radius, hole_border_radius 
            
            radius_diff = hole_border_radius - hole_radius            
            new_smooth, min_smooth = (radius_diff / 3.0), (radius_diff / 2.0)
            adjusted_radius_smooth = new_smooth if (min_smooth < hole_smooth) else hole_smooth
            new_smooth, min_smooth = (hole_border_depth / 3.0), (hole_border_depth / 2.0)            
            adjusted_side_smooth   = new_smooth if (min_smooth < hole_smooth) else hole_smooth
                                   
            hole_cache = _hole_cache[cache_key] = [None for _ in range(hole_subdivisions)]
           
            for index in range(hole_subdivisions):
                ry, rz = math_rotations[index]
                vert_line = hole_cache[index] = [None for _ in range(9)]
                
                knob_y, knob_z = ry * (hbr + hole_smooth), rz * (hbr + hole_smooth)
                vert_line[0] = (0, knob_y, knob_z)
                
                knob_y, knob_z = ry * hbr, rz * hbr
                vert_line[1] = (0, knob_y, knob_z)
                vert_line[2] = (adjusted_side_smooth, knob_y, knob_z)
                vert_line[3] = (hole_border_depth - adjusted_side_smooth, knob_y, knob_z)
                vert_line[4] = (hole_border_depth, knob_y, knob_z)
                
                knob_y, knob_z = ry * (hbr - adjusted_radius_smooth), rz * (hbr - adjusted_radius_smooth)
                vert_line[5] = (hole_border_depth, knob_y, knob_z)
                
                knob_y, knob_z = ry * (hr + adjusted_radius_smooth), rz * (hr + adjusted_radius_smooth)
                vert_line[6] = (hole_border_depth, knob_y, knob_z)
                
                knob_y, knob_z = ry * hr, rz * hr
                vert_line[7] = (hole_border_depth, knob_y, knob_z)
                vert_line[8] = (hole_border_depth + hole_smooth, knob_y, knob_z)
        
        all_vert_line_ids = []       
        for line_index in range(len(hole_cache)):            
            cache = hole_cache[line_index]
            vert_line = [None for _ in range(len(cache) * 2)]
            
            for index in range(len(cache)):
                cx, cy, cz = cache[index]
                vert_line[index]        = (x1 + cx, y + cy, z + cz)
                vert_line[-(index + 1)] = (x2 - cx, y + cy, z + cz)
                            
            all_vert_line_ids.append(self._construct.addVertex(vert_line))
        all_vert_line_ids.append(all_vert_line_ids[0])
        
        polygons = []
        for index in range(len(all_vert_line_ids)-1):
            a, b = all_vert_line_ids[index:index+2]            
            
            for index in range(len(a)-1):
                polygons.append((a[index+1], b[index+1], b[index], a[index]))

        polygon_ids = self._construct.addPolygon(polygons)        
        
        lf_vert_ids = [line[0]  for line in all_vert_line_ids[:-1]]
        rt_vert_ids = [line[-1] for line in all_vert_line_ids[:-1]]
        
        return lf_vert_ids, rt_vert_ids
    
    
    
    def createOuterHole(self, x1, x2, y, z, hole_radius, highest_point):
        if self._construct is None: return

        global _hole_outer_cache
        try:
            cache_key = (hole_radius)
            hole_cache = _hole_outer_cache[cache_key]            
        except KeyError:            
            hole_subdivisions = dimensions.KNOB_SUBDIVISIONS
            hole_smooth       = dimensions.SMOOTH_OFFSET
                                   
            hole_cache = _hole_cache[cache_key] = [None for _ in range(hole_subdivisions)]

            for index in range(hole_subdivisions):
                ry, rz = math_rotations[index]
                vert_line = hole_cache[index] = [None for _ in range(3)]
                
                knob_y, knob_z = ry * (hole_radius + hole_smooth), rz * (hole_radius + hole_smooth)
                vert_line[0] = (0, knob_y, knob_z)
                
                knob_y, knob_z = ry * hole_radius, rz * hole_radius
                vert_line[1] = (0, knob_y, knob_z)
                vert_line[2] = (hole_smooth, knob_y, knob_z)
        
        start_index = len(hole_cache); end_index = 0
        for line_index in range(len(hole_cache)):            
            if (y + hole_cache[line_index][1][1]) < highest_point:
                start_index = line_index if line_index < start_index else start_index
                end_index   = line_index if line_index > end_index   else end_index
        
        mid_width = (x1 + x2) / 2.0
        all_vert_line_ids = []; end_verts = []
        for line_index in range(len(hole_cache)):            
            cache = hole_cache[line_index]
            if line_index < start_index or line_index > end_index:
                continue
            
            vert_line = [None for _ in range(len(cache) * 2 + 1)]
            
            for index in range(len(cache)):
                cx, cy, cz = cache[index]
                cy = highest_point if line_index in (start_index, end_index) else y + cy 
                vert_line[index]        = (x1 + cx, cy, z + cz)
                vert_line[-(index + 1)] = (x2 - cx, cy, z + cz)

            vert_line[len(cache)] = (mid_width, cy, z + cz)
                            
            all_vert_line_ids.append(self._construct.addVertex(vert_line))
        
        polygons = []
        for index in range(0, end_index-start_index):
            a, b = all_vert_line_ids[index:index+2]            
            
            for index in range(len(a)-1):
                polygons.append((a[index], b[index], b[index+1], a[index+1]))

        self._construct.addPolygon(polygons)
        
        all_extra_verts = []
        for cache_index, line_index in ((start_index, 0), (end_index, -1)):
            cache_line = hole_cache[cache_index]
            cz = z + cache_line[0][2]
            extra_vertices = [(x1 + cache_line[2][0], highest_point, cz),
                              (mid_width,             highest_point, cz),
                              (x2 - cache_line[2][0], highest_point, cz)]

            extra_vert_ids = self._construct.addVertex(extra_vertices)
            all_extra_verts.append(extra_vert_ids)
         
            line_vert_ids  = all_vert_line_ids[line_index]
            extra_vert_ids = [line_vert_ids[0]] + extra_vert_ids + [line_vert_ids[-1]]
            line_vert_ids  = line_vert_ids[1:-1]  
                
            extra_polygons = []
            for index in range(len(line_vert_ids) - 1):
                extra_polygons.append((line_vert_ids[index],    line_vert_ids[index+1], 
                                       extra_vert_ids[index+1], extra_vert_ids[index]))
                if line_index: extra_polygons[index] = extra_polygons[index][::-1]
            self._construct.addPolygon(extra_polygons)       
        
        x1_vert_ids = [line[0]  for line in all_vert_line_ids]
        x2_vert_ids = [line[-1] for line in all_vert_line_ids][::-1]
        
        return x1_vert_ids + all_extra_verts[1] + x2_vert_ids + all_extra_verts[0][::-1]
    
    
    
    def createOuterSquare(self, cylinder_verts, square_verts):
        if self._construct is None: return
        
        a, b = cylinder_verts, square_verts
        polygons = [(b[0],  b[1],  a[1],  a[0]),  (b[1],  b[2],  a[2],  a[1]),
                    (b[2],  b[3],  a[3],  a[2]),  (b[3],  a[4],  a[3]),
                    (b[3],  a[5],  a[4]),         (b[3],  b[4],  a[6],  a[5]),
                    (b[4],  b[5],  a[7],  a[6]),  (b[5],  a[8],  a[7]),
                    (b[5],  a[9],  a[8]),         (b[5],  b[6],  a[10], a[9]),
                    (b[6],  b[7],  a[11], a[10]), (b[7],  b[8],  a[12], a[11]),
                    (b[8],  b[9],  a[13], a[12]), (b[9],  b[10], a[14], a[13]),
                    (b[10], b[11], a[15], a[14]), (b[11], b[12], a[16], a[15]),
                    (b[12], b[13], a[17], a[16]), (b[13], b[14], a[18], a[17]),
                    (b[14], b[15], a[19], a[18]), (b[15], a[20], a[19]),
                    (b[15], a[21], a[20]),        (b[15], b[16], a[22], a[21]),
                    (b[16], b[17], a[23], a[22]), (b[17], a[24], a[23]),
                    (b[17], a[25], a[24]),        (b[17], b[18], a[26], a[25]),
                    (b[18], b[19], a[27], a[26]), (b[19], b[20], a[28], a[27]),
                    (b[20], b[21], a[29], a[28]), (b[21], b[22], a[30], a[29]),
                    (b[22], b[23], a[31], a[30]), (b[23], b[0],  a[0],  a[31])]
        
        self._construct.addPolygon(polygons) 
        
    #------------------------------------------------------------------------------------------#
    
    def create(self, units_in_z):
        self._construct = construct = Construct()
        
        unit           = dimensions.UNIT
        unit_offset    = dimensions.UNIT_OFFSET
        smooth_offset  = so = dimensions.SMOOTH_OFFSET
        wall_thickness = wt = dimensions.WALL_THICKNESS
        
        x1 = z1 = unit_offset
        x2 = x1 + unit - unit_offset
        
        y1 = 0.0           
        y2 = dimensions.HEIGHT        
        y3 = y2 - wall_thickness
        
        panel_unit        = unit / 2.0
        panel_unit_offset = unit_offset / 2.0
        
        knob_edge_border   = dimensions.KNOB_EDGE_BORDER
        knob_radius        = dimensions.KNOB_RADIUS
        knob_height        = dimensions.KNOB_HEIGHT
        knob_hollow_radius = dimensions.KNOB_HOLLOW_RADIUS
         
        small_outer_radius = dimensions.SMALL_CYLINDER_OUTER_RADIUS
        
        hole_radius        = dimensions.HOLE_RADIUS
        hole_border_radius = dimensions.HOLE_BORDER_RADIUS
        hole_thickness     = dimensions.HOLE_THICKNESS
        
        hole_height = hh = dimensions.HOLE_HEIGHT_OFFSET

        # create box
        #
        apv = all_plane_vertices = []
        skip_set = set(range(3,(units_in_z * 2)) + range((units_in_z * 2) + 9,(units_in_z * 4) + 6))
        for y, offset, smooth, skip in [(y3,      wt + so, False,  True),
                                        (y3,           wt,  True,  True),
                                        (y3 - so,      wt,  True,  True),
                                        (y1 + hh,      wt,  True,  True),
                                        (y1 + so,      wt,  True, False),
                                        (y1,           wt,  True, False),
                                        (y1,      wt - so,  True, False),
                                        (y1,           so,  True, False),
                                        (y1,            0,  True, False),
                                        (y1 + so,       0,  True, False),
                                        (y1 + hh,       0,  True,  True),
                                        (y2 - so,       0,  True, False),
                                        (y2,            0,  True, False),
                                        (y2,           so, False, False)]:
            if skip:
                vertex_ids = self.createPlaneVertices(units_in_z, y, offset, smooth, skip_set)
            else:            
                vertex_ids = self.createPlaneVertices(units_in_z, y, offset, smooth)
            all_plane_vertices.append(vertex_ids)
   
        self.createPlanePolygons(units_in_z, all_plane_vertices)
          
        round_vertex = lambda vert: (round(vert[0], 2), round(vert[1], 2), round(vert[2], 2))
               
        outer_top_vert_ids = all_plane_vertices[-1]
        outer_top_vertices = [round_vertex(vertex) for vertex in construct.getVertex(outer_top_vert_ids)]
        outer_vert_id_lookup = dict(zip(outer_top_vertices, outer_top_vert_ids))
        
        lf_side_vert_ids = apv[9][2:(units_in_z*2)+1] + apv[11][2:(units_in_z*2)+1] + [apv[10][2], apv[10][(units_in_z*2)]]
        lf_side_vertices = [round_vertex(vertex) for vertex in construct.getVertex(lf_side_vert_ids)]
        lf_side_vert_id_lookup = dict(zip(lf_side_vertices, lf_side_vert_ids))
        
        rt_side_vert_ids = apv[9][(units_in_z*2)+8:(units_in_z*4)+7] + apv[11][(units_in_z*2)+8:(units_in_z*4)+7] + [apv[10][(units_in_z*2)+8], apv[10][(units_in_z*4)+6]]
        rt_side_vertices = [round_vertex(vertex) for vertex in construct.getVertex(rt_side_vert_ids)]
        rt_side_vert_id_lookup = dict(zip(rt_side_vertices, rt_side_vert_ids))
                
        # create top inner end faces
        #
        end_mid_verts = (((x1 + x2) / 2.0, y3, z1 + panel_unit - panel_unit_offset),
                         ((x1 + x2) / 2.0, y3, z1 + (unit * units_in_z) - panel_unit - panel_unit_offset))
        end_mid_ids = self._construct.addVertex(end_mid_verts)
        
        top_plane_ids = all_plane_vertices[0][:-1]
        
        end_plane_ids = (top_plane_ids[-3:] + top_plane_ids[:2]), \
                        (top_plane_ids[(units_in_z * 2)-1:(units_in_z * 2)+4])
        for mid_id, plane_ids in zip(end_mid_ids, end_plane_ids):
            polygons = [(mid_id, plane_ids[2], plane_ids[1], plane_ids[0]),
                        (mid_id, plane_ids[4], plane_ids[3], plane_ids[2])]
            self._construct.addPolygon(polygons)
        
        inner_vert_ids = end_plane_ids[0][0::4] + end_plane_ids[1][0::4] + end_mid_ids
        for index in range(1,4):
            plane_ids = apv[index]
            inner_vert_ids.extend([plane_ids[-7], plane_ids[2], plane_ids[(units_in_z * 2)], plane_ids[(units_in_z * 2) + 8]]) 
        inner_vert_ids.extend(apv[4][(units_in_z * 2) + 8:-6] + apv[4][2:(units_in_z * 2)+1])

        inner_vertices = [round_vertex(vertex) for vertex in construct.getVertex(inner_vert_ids)]
        inner_vert_id_lookup = dict(zip(inner_vertices, inner_vert_ids))
  
        for unit_in_z_index in range(units_in_z):
            knob_center_x = x1 + knob_edge_border + knob_radius - panel_unit_offset             
            knob_center_z = z1 + knob_edge_border + knob_radius + (unit_in_z_index * unit) - panel_unit_offset 
         
            knob_vertex_ids = self.createKnob(knob_center_x, y2, knob_center_z, knob_height, knob_radius, knob_hollow_radius)
              
            xs1 = x1 + smooth_offset             
            xs2 = x1 + unit - unit_offset - smooth_offset
              
            if unit_in_z_index == 0: zs1 = z1 + smooth_offset
            else:                    zs1 = z1 + (unit_in_z_index * unit) - panel_unit_offset
              
            if unit_in_z_index == (units_in_z - 1): zs2 = z1 + (unit * units_in_z) - unit_offset - smooth_offset
            else:                                   zs2 = z1 + (unit * (unit_in_z_index + 1)) - panel_unit_offset
              
            square = [(xs2, y2, knob_center_z), (xs2, y2, zs2),
                      (knob_center_x, y2, zs2), (xs1, y2, zs2),
                      (xs1, y2, knob_center_z), (xs1, y2, zs1),
                      (knob_center_x, y2, zs1), (xs2, y2, zs1)]
             
            square_vert_ids = [] 
            for vertex in square:
                rounded_vertex = round_vertex(vertex)
                try:
                    vert_id = outer_vert_id_lookup[rounded_vertex]
                except KeyError:
                    vert_id = construct.addVertex(vertex)
                    outer_vert_id_lookup[rounded_vertex] = vert_id                    
                square_vert_ids.append(vert_id)
                 
            self.buildRingFaces(knob_vertex_ids, square_vert_ids)
             
            if unit_in_z_index == 0: continue
            
            hole_center_z = (unit_in_z_index * unit) + panel_unit_offset
            
            lf_ring_ids, rt_ring_ids = self.createHole(x1, x2, 
                                                       hole_height, 
                                                       hole_center_z, 
                                                       hole_radius, 
                                                       hole_border_radius)
            outer_vert_ids = self.createOuterHole(x1 + wall_thickness, 
                                                  x2 - wall_thickness, 
                                                  hole_height, 
                                                  (unit_in_z_index * unit) + panel_unit_offset, 
                                                  hole_radius + hole_thickness,
                                                  y3)
            
            
            xs1, xs3 = x1 + wall_thickness, x2 - wall_thickness
            xs2 = (xs1 + xs3) / 2.0
            zs1 = z1 + (unit_in_z_index - 1) * unit + panel_unit - panel_unit_offset
            zs2 = zs1 + panel_unit
            zs3 = z1 + unit_in_z_index * unit + panel_unit - panel_unit_offset
            
            square_verts = [(xs1, y3, zs3), (xs1, y3 - smooth_offset, zs3), 
                            (xs1, hole_height, zs3), (xs1, smooth_offset, zs3),
                            (xs1, smooth_offset, zs2), (xs1, smooth_offset, zs1), 
                            (xs1, hole_height, zs1), (xs1, y3 - smooth_offset, zs1),
                            (xs1, y3, zs1), (xs1 + smooth_offset, y3, zs1),
                            (xs2, y3, zs1), (xs3 - smooth_offset, y3, zs1),
                            (xs3, y3, zs1), (xs3, y3 - smooth_offset, zs1),
                            (xs3, hole_height, zs1), (xs3, smooth_offset, zs1),
                            (xs3, smooth_offset, zs2), (xs3, smooth_offset, zs3),
                            (xs3, hole_height, zs3), (xs3, y3 - smooth_offset, zs3), 
                            (xs3, y3, zs3), (xs3 - smooth_offset, y3, zs3), 
                            (xs2, y3, zs3), (xs1 + smooth_offset, y3, zs3)]

            square_vert_ids = []                
            for vertex in square_verts:
                rounded_vertex = round_vertex(vertex)
                try:
                    vert_id = inner_vert_id_lookup[rounded_vertex]
                except KeyError:
                    vert_id = construct.addVertex(vertex)
                    inner_vert_id_lookup[rounded_vertex] = vert_id
                square_vert_ids.append(vert_id)
                
            self.createOuterSquare(outer_vert_ids, square_vert_ids)                

            for x_value, lookup, ring_ids, flip in [(x1, lf_side_vert_id_lookup, lf_ring_ids, False), 
                                                    (x2, rt_side_vert_id_lookup, rt_ring_ids,  True)]:            
                ys1 = y1 + smooth_offset
                ys2 = y2 - smooth_offset
                              
                if unit_in_z_index == 0: zs1 = z1 + panel_unit - panel_unit_offset
                else:                    zs1 = z1 + (unit_in_z_index * unit) - panel_unit_offset - panel_unit
                  
                if unit_in_z_index == (units_in_z - 1): zs2 = z1 + (unit * units_in_z) - panel_unit - panel_unit_offset
                else:                                   zs2 = z1 + (unit * (unit_in_z_index + 1)) - panel_unit - panel_unit_offset
                  
                square = [(x_value, ys2, hole_center_z), 
                          (x_value, ys2, zs2), (x_value, hole_height, zs2), 
                          (x_value, ys1, zs2), (x_value, ys1, hole_center_z),
                          (x_value, ys1, zs1), (x_value, hole_height, zs1), (x_value, ys2, zs1)]
                
                square_vert_ids = []                
                for vertex in square:
                    rounded_vertex = round_vertex(vertex)
                    try:
                        vert_id = lookup[rounded_vertex]
                    except KeyError:
                        vert_id = construct.addVertex(vertex)
                        lookup[rounded_vertex] = vert_id
                    square_vert_ids.append(vert_id)
                
                self.buildRingFaces(ring_ids, square_vert_ids, flip)

                  
                cyl_x = x1 + (unit / 2.0)
                cyl_y = hole_height - hole_radius - (hole_thickness / 4.0)
                cyl_z = z1 + (unit_in_z_index * unit) - panel_unit_offset
                cylinder_base_verts = self.createCylinder(cyl_x, y1, cyl_y, cyl_z, None, small_outer_radius)

        
        transform, mesh = construct.build(self.name)
        self._construct = None
                        
        mc.sets(transform, e=True, forceElement='initialShadingGroup')
      