import maya.cmds as mc
from math import cos, sin, radians, degrees
import maya.OpenMaya as om

import dimensions, category; reload(dimensions)

import piece; reload(piece)
from .piece import Piece, Construct, ConstructError

_plane_cache    = {}
_strut_cache    = {}
    
#--------------------------------------------------------------------------------------------------#
    
class Brick(Piece):
    HEIGHT_PLATE  = 'plate'  
        
    EDGE   = 'e'
    SMOOTH = 's'
    CORNER = 'c'
       
    def __init__(self, name='untitled'):
        Piece.__init__(self, name)
        self.category = category.BRICK
    
    #------------------------------------------------------------------------------------------#
    
    def createPlaneVertices(self, units_in_x, units_in_z, y, offset=0, smooth=True):
        vertices = []
        
        global _plane_cache
        try:
            vert_plane_template = _plane_cache[(units_in_x, units_in_z)]
        except KeyError:
            vert_plane_template = _plane_cache[(units_in_x, units_in_z)] = []

            unit           = dimensions.UNIT
            unit_offset    = dimensions.UNIT_OFFSET
            smooth_offset  = dimensions.SMOOTH_OFFSET
            
            x1 = z1 = unit_offset

            x2 = x1 + (unit * units_in_x) - unit_offset
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
                    vert_plane_template.append((x1, z1 + (index * panel_unit) - panel_unit_offset, self.EDGE))
                
            point_count = xrange(1, (units_in_x * 2) + 1)
            for index in point_count:            
                if index == point_count[-1]:
                    vert_plane_template.append((x2 - smooth_offset, z2, self.SMOOTH))                
                    vert_plane_template.append((x2, z2, self.CORNER))
                    vert_plane_template.append((x2, z2 - smooth_offset, self.SMOOTH))
                else:
                    vert_plane_template.append((x1 + (index * panel_unit) - panel_unit_offset, z2, self.EDGE))
                      
            point_count = xrange((units_in_z * 2) -1, -1, -1)
            for index in point_count:
                if index == point_count[-1]:
                    vert_plane_template.append((x2, z1 + smooth_offset, self.SMOOTH))
                    vert_plane_template.append((x2, z1, self.CORNER))
                    vert_plane_template.append((x2 - smooth_offset, z1, self.SMOOTH))
                else:
                    vert_plane_template.append((x2, z1 + (index * panel_unit) - panel_unit_offset, self.EDGE))
                       
            point_count = xrange((units_in_x * 2) - 1, 0, -1)
            for index in point_count:
                vert_plane_template.append((x1 + (index * panel_unit) - panel_unit_offset, z1, self.EDGE))
                if index == point_count[-1]:
                    vert_plane_template.append((x1 + smooth_offset, z1, self.SMOOTH))
        
        if offset == 0:
            for x, z, _ in vert_plane_template:
                vertices.append((x, y, z))
                                    
        else:
            corner_offset = {1:(1,1), 2:(1,-1), 3:(-1,-1), 4:(-1,1), 5:(1,1)}
            edge_offset   = {1:(1,0), 2:(0,-1), 3:(-1, 0), 4:( 0,1)}
            
            corner_counter = 0; previous_vertex_type = vert_plane_template[-1][2]
            for x, z, vertex_type in vert_plane_template:
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
                
                vertices.append((x, y, z))
                previous_vertex_type = vertex_type
                
        return self._construct.addVertex(vertices)    
    
    
    def createPlanePolygons(self, units_in_x, units_in_z, vert_planes):
        for vert_plane in vert_planes:
            vert_plane.append(vert_plane[0])
                        
        polygons = []
        for vert_plane_index in range(len(vert_planes) - 1):
            plane      = vert_planes[vert_plane_index]
            next_plane = vert_planes[vert_plane_index + 1]
            
            plane_len = len(plane); next_plane_len = len(next_plane) 

            if plane_len == next_plane_len:
                for vert_index in range(len(vert_planes[vert_plane_index]) - 1):
                    polygons.append((plane[vert_index],        plane[vert_index+1],
                                     next_plane[vert_index+1], next_plane[vert_index]))
            else:                
                if plane_len < next_plane_len:
                    small_plane = plane; large_plane = next_plane[:-1]
                    flip = True
                    current_num_polys = len(polygons)
                else:
                    small_plane = next_plane; large_plane = plane[:-1]
                    flip = False
                    
                small_index = 0
                a = (2 * units_in_z) + 2
                b = a + (2 * units_in_x) + 2
                c = b + a
                for large_index in range(len(large_plane) - 1):
                    if large_index in (0, a, b, c):
                        polygons.append((small_plane[small_index], large_plane[large_index-1],
                                         large_plane[large_index], large_plane[large_index+1]))                        
                        continue
                    elif large_index in (a-1, b-1, c-1): continue
                    else:
                        polygons.append((small_plane[small_index+1], small_plane[small_index],
                                         large_plane[large_index],   large_plane[large_index+1]))
                    small_index += 1
                
                if flip is True:
                    polygons[current_num_polys:] = [polygon[::-1] for polygon in polygons[current_num_polys:]]
                    
        
        return self._construct.addPolygon(polygons)
    
    #------------------------------------------------------------------------------------------#
        
    def buildRingFaces(self, rv, sv, flip=False):
        polygons = []; p_index = 0
        rv.append(rv[0]); sv.append(sv[0]);            
        for index in range(0, 16, 4):
            polygons.append((sv[p_index],   rv[index],   rv[index+1], sv[p_index+1]))
            polygons.append((sv[p_index+1], rv[index+1], rv[index+2]))
            polygons.append((sv[p_index+1], rv[index+2], rv[index+3]))
            polygons.append((sv[p_index+1], rv[index+3], rv[index+4], sv[p_index+2]))                        
            p_index += 2
            
        if flip:
            for index, polygon in enumerate(polygons):
                polygons[index] = polygon[::-1]                   

        return self._construct.addPolygon(polygons)
    
    
    def buildSquareFaces(self, sv, center, flip=False):
        sv.append(sv[0])
        polygons = []
        for index in range(0, 8, 2):
            polygons.append((center, sv[index+2], sv[index+1], sv[index]))
        
        if flip:
            for index, polygon in enumerate(polygons):
                polygons[index] = polygon[::-1]                   

        return self._construct.addPolygon(polygons)    
                
    #------------------------------------------------------------------------------------------#
    
    def buildStruts(self, units_in_x, units_in_z, height):
        if (units_in_x > 3 and units_in_z > 1) or (units_in_x > 1 and units_in_z > 3): pass
        else: return
        
        unit              = dimensions.UNIT
        unit_offset       = dimensions.UNIT_OFFSET
        wall_thickness    = dimensions.WALL_THICKNESS
        smooth_offset     = dimensions.SMOOTH_OFFSET
        panel_unit        = unit / 2.0
        panel_unit_offset = unit_offset / 2.0 
        
        strut_width         = dimensions.STRUT_WIDTH / 2.0
        strut_height_offset = dimensions.STRUT_HEIGHT_OFFSET
        
        radius = (dimensions.CYLINDER_OUTER_RADIUS + dimensions.CYLINDER_INNER_RADIUS) / 2.0
        mid_offset = (unit - (2 * radius)) / 2.0
        
        wall_offset = panel_unit - (wall_thickness / 2.0)
        
        try:
            strut_cache = _strut_cache[(units_in_x, units_in_z)]
        except KeyError:
            strut_cache = _strut_cache[(units_in_x, units_in_z)] = []
            
            def createStrutVerts(start, end, height, x=True):
                vertices = []
                if x is True:
                    for x, z in (start, end):
                        vertices.append((x, height, z + strut_width))
                        vertices.append((x, strut_height_offset + smooth_offset, z + strut_width))
                        vertices.append((x, strut_height_offset, z + strut_width))
                        vertices.append((x, strut_height_offset, z + strut_width - smooth_offset))
                        vertices.append((x, strut_height_offset, z - strut_width + smooth_offset))
                        vertices.append((x, strut_height_offset, z - strut_width))
                        vertices.append((x, strut_height_offset + smooth_offset, z - strut_width))
                        vertices.append((x, height, z - strut_width))
                        
                else:
                    for x, z in (start, end):
                        vertices.append((x - strut_width, height, z))
                        vertices.append((x - strut_width, strut_height_offset + smooth_offset, z))
                        vertices.append((x - strut_width, strut_height_offset, z))
                        vertices.append((x - strut_width + smooth_offset, strut_height_offset, z))
                        vertices.append((x + strut_width - smooth_offset, strut_height_offset, z))
                        vertices.append((x + strut_width, strut_height_offset, z))
                        vertices.append((x + strut_width, strut_height_offset + smooth_offset, z))
                        vertices.append((x + strut_width, height, z))
                
                strut_cache.append(vertices)
                
            # in z
            #
            for unit_in_x_index in range(1, units_in_x):
                if unit_in_x_index % 2: continue
                
                for unit_in_z_index in range(1, units_in_z * 2):
                    if not unit_in_z_index % 2: continue
                                     
                    mid_pos = (unit * unit_in_x_index + panel_unit_offset, panel_unit * unit_in_z_index + panel_unit_offset)
                    start = [mid_pos[0], mid_pos[1] - mid_offset]
                    end   = [mid_pos[0], mid_pos[1] + mid_offset]
                    if unit_in_z_index == 1:
                        start = [mid_pos[0], mid_pos[1] - wall_offset]                    
                    elif unit_in_z_index == ((units_in_z * 2) - 1):
                        end   = [mid_pos[0], mid_pos[1] + wall_offset]
    
                    createStrutVerts(start, end, height, False)
            
            # in x
            #
            for unit_in_x_index in range(1, units_in_x * 2):
                if not unit_in_x_index % 2: continue
                
                for unit_in_z_index in range(1, units_in_z):
                    if unit_in_z_index % 2: continue
                                     
                    mid_pos = (panel_unit * unit_in_x_index + panel_unit_offset, unit * unit_in_z_index + panel_unit_offset)
                    start = [mid_pos[0] - mid_offset, mid_pos[1]]
                    end   = [mid_pos[0] + mid_offset, mid_pos[1]]
                    if unit_in_x_index == 1:
                        start = [mid_pos[0] - wall_offset, mid_pos[1]]                    
                    elif unit_in_x_index == ((units_in_x * 2) - 1):
                        end   = [mid_pos[0] + wall_offset, mid_pos[1]]
                        
                    createStrutVerts(start, end, height, True)
                    
        polygons = []
        for vertices in strut_cache:
            vert_ids = self._construct.addVertex(vertices)
            start = vert_ids[0:8]; end = vert_ids[8:]
           
            for index in range(7):
                polygons.append((start[index], start[index+1], end[index+1], end[index]))
            
                
        return self._construct.addPolygon(polygons)
    
    #------------------------------------------------------------------------------------------#
    
    def create(self, units_in_x, units_in_z, height=1, hollow=False):
        self._construct = construct = Construct()
        
        unit           = dimensions.UNIT
        unit_offset    = dimensions.UNIT_OFFSET
        smooth_offset  = dimensions.SMOOTH_OFFSET
        wall_thickness = dimensions.WALL_THICKNESS
        
        x1 = z1 = unit_offset
        
        y1 = 0.0           
        y2 = dimensions.HEIGHT
        if height == Brick.HEIGHT_PLATE:
            y2 /= 3.0
        elif isinstance(height, int) and height > 0:
            y2 *= height
        y3 = y2 - wall_thickness
        
        panel_unit_offset = unit_offset / 2.0                

        # create box
        #
        apv = all_plane_vertices = []
        for y, offset, smooth in [(y3,                 wall_thickness + smooth_offset, False),
                                  (y3,                 wall_thickness,                 True),
                                  (y3 - smooth_offset, wall_thickness,                 True),
                                  (y1 + smooth_offset, wall_thickness,                 True),
                                  (y1,                 wall_thickness,                 True),
                                  (y1,                 wall_thickness - smooth_offset, True),
                                  (y1,                 smooth_offset,                  True),
                                  (y1,                 0,                              True),
                                  (y1 + smooth_offset, 0,                              True),
                                  (y2 - smooth_offset, 0,                              True),
                                  (y2,                 0,                              True),
                                  (y2,                 smooth_offset,                  False)]:
            apv.append(self.createPlaneVertices(units_in_x, units_in_z, y, offset, smooth))

        self.createPlanePolygons(units_in_x, units_in_z, all_plane_vertices)
        
        # add knobs
        #
        knob_edge_border   = dimensions.KNOB_EDGE_BORDER
        knob_radius        = dimensions.KNOB_RADIUS
        knob_height        = dimensions.KNOB_HEIGHT
        
        knob_hollow_radius = 0
        if hollow:
            knob_hollow_radius = dimensions.KNOB_HOLLOW_RADIUS
        
        under_knob_radius = dimensions.UNDER_KNOB_RADIUS
        under_knob_height = dimensions.UNDER_KNOB_HEIGHT
        
        inner_radius = dimensions.CYLINDER_INNER_RADIUS
        outer_radius = dimensions.CYLINDER_OUTER_RADIUS
        
        small_inner_radius = dimensions.SMALL_CYLINDER_INNER_RADIUS
        small_outer_radius = dimensions.SMALL_CYLINDER_OUTER_RADIUS
        
        round_vertex = lambda vert: (round(vert[0], 2), round(vert[1], 2), round(vert[2], 2))
        
        outer_top_vert_ids = all_plane_vertices[-1]
        inner_top_vert_ids = all_plane_vertices[0]
        outer_top_vertices = [round_vertex(vertex) for vertex in construct.getVertex(outer_top_vert_ids)]
        inner_top_vertices = [round_vertex(vertex) for vertex in construct.getVertex(inner_top_vert_ids)]
        
        outer_vert_id_lookup = dict(zip(outer_top_vertices, outer_top_vert_ids))
        inner_vert_id_lookup = dict(zip(inner_top_vertices, inner_top_vert_ids))        
        
        for unit_in_x_index in range(units_in_x):
            for unit_in_z_index in range(units_in_z):
                knob_center_x = x1 + knob_edge_border + knob_radius + (unit_in_x_index * unit) - panel_unit_offset             
                knob_center_z = z1 + knob_edge_border + knob_radius + (unit_in_z_index * unit) - panel_unit_offset 

                knob_vertex_ids = self.createKnob(knob_center_x, y2, knob_center_z, knob_height, knob_radius, knob_hollow_radius)              
                
                if unit_in_x_index == 0: xs1 = x1 + smooth_offset
                else:                    xs1 = x1 + (unit_in_x_index * unit) - panel_unit_offset
                 
                if unit_in_x_index == (units_in_x - 1): xs2 = x1 + (unit * units_in_x) - unit_offset - smooth_offset
                else:                                   xs2 = x1 + (unit * (unit_in_x_index + 1)) - panel_unit_offset
                 
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
                
                if unit_in_x_index == 0: 
                    xs1 = xs1 + wall_thickness
                if unit_in_x_index == (units_in_x - 1): 
                    xs2 = xs2 - wall_thickness
                if unit_in_z_index == 0:
                    zs1 = zs1 + wall_thickness
                if unit_in_z_index == (units_in_z - 1):    
                    zs2 = zs2 - wall_thickness
                                
                square = [(xs2, y3, knob_center_z), (xs2, y3, zs2),
                          (knob_center_x, y3, zs2), (xs1, y3, zs2),
                          (xs1, y3, knob_center_z), (xs1, y3, zs1),
                          (knob_center_x, y3, zs1), (xs2, y3, zs1)]
                
                square_vert_ids = []                
                for vertex in square:
                    rounded_vertex = round_vertex(vertex)
                    try:
                        vert_id = inner_vert_id_lookup[rounded_vertex]
                    except KeyError:
                        vert_id = construct.addVertex(vertex)
                        inner_vert_id_lookup[rounded_vertex] = vert_id
                    square_vert_ids.append(vert_id)
                
                if hollow is True:
                    center_id = construct.addVertex((knob_center_x, y3, knob_center_z))
                    self.buildSquareFaces(square_vert_ids, center_id, True)
                else:
                    y3 = y2 - wall_thickness
                    under_knob_bttm_ids = self.createKnob(knob_center_x, y3, knob_center_z, under_knob_height, under_knob_radius, flip=True)
                    
                    self.buildRingFaces(under_knob_bttm_ids, square_vert_ids, True)
            
                if hollow is True: continue
                
                if units_in_x == 1:
                    if unit_in_z_index == 0: continue
                    
                    cyl_x = x1 + (unit / 2.0)
                    cyl_z = z1 + (unit_in_z_index * unit) - panel_unit_offset
                    cylinder_base_verts = self.createCylinder(cyl_x, y1, y2 - wall_thickness, cyl_z, small_inner_radius, small_outer_radius)
                    
                elif units_in_z == 1:
                    if unit_in_x_index == 0: continue
                    
                    cyl_x = x1 + (unit_in_x_index * unit) - panel_unit_offset
                    cyl_z = z1 + (unit / 2.0) 
                    cylinder_base_verts = self.createCylinder(cyl_x, y1, y2 - wall_thickness, cyl_z, small_inner_radius, small_outer_radius)   
                    
                else:    
                    if unit_in_x_index == 0 or unit_in_z_index == 0: continue
                
                    cyl_x = x1 + (unit_in_x_index * unit) - panel_unit_offset
                    cyl_z = z1 + (unit_in_z_index * unit) - panel_unit_offset
                    cylinder_base_verts = self.createCylinder(cyl_x, y1, y2 - wall_thickness, cyl_z, inner_radius, outer_radius)

        self.buildStruts(units_in_x, units_in_z, y2 - (wall_thickness / 2.0))
        
        transform, mesh = construct.build(self.name)
        self._construct = None
                        
        mc.sets(transform, e=True, forceElement='initialShadingGroup')
        
#--------------------------------------------------------------------------------------------------#
        
class BrickCorner(Brick):
    INNER_CORNER = 'ic'
     
    def createPlaneVertices(self, units_in_x, units_in_z, y, offset=0, smooth=True):
        vertices = []
        
        global _plane_cache
        try:
            vert_plane_template = _plane_cache[(units_in_x, units_in_z, 'corner')]
        except KeyError:
            vert_plane_template = _plane_cache[(units_in_x, units_in_z, 'corner')] = []

            unit           = dimensions.UNIT
            unit_offset    = dimensions.UNIT_OFFSET
            smooth_offset  = dimensions.SMOOTH_OFFSET
            
            x1 = z1 = unit_offset
            
            x2 = x1 + unit - unit_offset
            z2 = z1 + unit - unit_offset

            x3 = x1 + (unit * units_in_x) - unit_offset
            z3 = z1 + (unit * units_in_z) - unit_offset
            
            panel_unit        = unit / 2.0
            panel_unit_offset = unit_offset / 2.0
            
            point_count = xrange((units_in_z * 2) + 1)
            for index in point_count:
                if index == point_count[0]:
                    vert_plane_template.append((x1, z1, self.CORNER))
                    vert_plane_template.append((x1, z1 + smooth_offset, self.SMOOTH))
                elif index == point_count[-1]:
                    vert_plane_template.append((x1, z3 - smooth_offset, self.SMOOTH)) 
                    vert_plane_template.append((x1, z3, self.CORNER))
                    vert_plane_template.append((x1 + smooth_offset, z3, self.SMOOTH))
                else:
                    vert_plane_template.append((x1, z1 + (index * panel_unit) - panel_unit_offset, self.EDGE))
                    
            vert_plane_template.append((x1 + panel_unit - panel_unit_offset, z3, self.EDGE))
                    
            point_count = xrange((units_in_z * 2) - 2, -1, -1)
            for index in point_count:
                print index
                if index == point_count[0]:
                    vert_plane_template.append((x2 - smooth_offset, z3, self.SMOOTH))                
                    vert_plane_template.append((x2, z3, self.CORNER))
                    vert_plane_template.append((x2, z3 - smooth_offset, self.SMOOTH)) 
                    print z3                   
                elif index == point_count[-1]:
                    vert_plane_template.append((x2, z2 + smooth_offset, self.INNER_CORNER))                
                    vert_plane_template.append((x2, z2, self.CORNER))
                    vert_plane_template.append((x2 + smooth_offset, z2, self.INNER_CORNER))
                    print z2
                else:
                    print z2 + (index * panel_unit) + panel_unit_offset
                    vert_plane_template.append((x2, z2 + (index * panel_unit) + panel_unit_offset, self.EDGE))
                  
            point_count = xrange(3, (units_in_x * 2) + 1)
            for index in point_count:            
                if index == point_count[-1]:
                    vert_plane_template.append((x3 - smooth_offset, z2, self.SMOOTH))                
                    vert_plane_template.append((x3, z2, self.CORNER))
                    vert_plane_template.append((x3, z2 - smooth_offset, self.SMOOTH))
                else:
                    vert_plane_template.append((x1 + (index * panel_unit) - panel_unit_offset, z2, self.EDGE))
                    
            vert_plane_template.append((x3, z1 + panel_unit - panel_unit_offset, self.EDGE))
                         
            point_count = xrange((units_in_x * 2), -1, -1)
            for index in point_count:
                if index == point_count[0]:
                    vert_plane_template.append((x3, z1 + smooth_offset, self.SMOOTH))
                    vert_plane_template.append((x3, z1, self.CORNER))
                    vert_plane_template.append((x3 - smooth_offset, z1, self.SMOOTH))
                elif index == point_count[-1]:
                    vert_plane_template.append((x1 + smooth_offset, z1, self.SMOOTH))
                else:
                    vert_plane_template.append((x1 + (index * panel_unit) - panel_unit_offset, z1, self.EDGE))

        
        if offset == 0:
            for x, z, _ in vert_plane_template:
                vertices.append((x, y, z))
                                    
        else:
            corner_offset = {1:(1,1), 2:(1,-1), 3:(-1,-1), 4:(-1,-1), 5:(-1,-1), 6:(-1,1), 7:(1,1)}
            edge_offset   = {1:(1,0), 2:(0,-1), 3:(-1, 0), 4:( 0,-1), 5:(-1, 0), 6:( 0,1)}
            
            corner_counter = 0; previous_vertex_type = vert_plane_template[-1][2]
            for x, z, vertex_type in vert_plane_template:
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
                elif vertex_type == self.INNER_CORNER:
                    x += corner_offset[corner_counter][0] * offset
                    z += corner_offset[corner_counter][1] * offset                    
                else:
                    x += edge_offset[corner_counter][0] * offset
                    z += edge_offset[corner_counter][1] * offset
                
                vertices.append((x, y, z))
                previous_vertex_type = vertex_type
                
        return self._construct.addVertex(vertices)
    
    
    def createPlanePolygons(self, units_in_x, units_in_z, vert_planes):
        for vert_plane in vert_planes:
            vert_plane.append(vert_plane[0])
                        
        polygons = []
        for vert_plane_index in range(len(vert_planes) - 1):
            plane      = vert_planes[vert_plane_index]
            next_plane = vert_planes[vert_plane_index + 1]
            
            plane_len = len(plane); next_plane_len = len(next_plane) 

            if plane_len == next_plane_len:
                for vert_index in range(len(vert_planes[vert_plane_index]) - 1):
                    polygons.append((plane[vert_index],        plane[vert_index+1],
                                     next_plane[vert_index+1], next_plane[vert_index]))
            else:                
                if plane_len < next_plane_len:
                    small_plane = plane; large_plane = next_plane[:-1]
                    flip = True
                    current_num_polys = len(polygons)
                else:
                    small_plane = next_plane; large_plane = plane[:-1]
                    flip = False
                    
                small_index = 0
                a = (2 * units_in_z) + 2
                b = a + 4
                c = b + (2 * (units_in_z - 1)) + (2 * (units_in_x - 1)) + 4
                d = c + 4
                e = d + (2 * units_in_x) + 2
                for large_index in range(len(large_plane) - 1):
                    if large_index in (0, a, b, c, d, e):
                        polygons.append((small_plane[small_index], large_plane[large_index-1],
                                         large_plane[large_index], large_plane[large_index+1]))                        
                        continue
                    elif large_index in (a-1, b-1, c-1, d-1, e-1): continue
                    else:
                        polygons.append((small_plane[small_index+1], small_plane[small_index],
                                         large_plane[large_index],   large_plane[large_index+1]))
                    small_index += 1
                
                if flip is True:
                    polygons[current_num_polys:] = [polygon[::-1] for polygon in polygons[current_num_polys:]]
                    
        
        return self._construct.addPolygon(polygons)
    
    
    def buildStruts(self, units_in_x, units_in_z, height):        
        unit           = dimensions.UNIT
        unit_offset    = dimensions.UNIT_OFFSET
        wall_thickness = dimensions.WALL_THICKNESS
        smooth_offset  = dimensions.SMOOTH_OFFSET
        panel_unit     = unit / 2.0
        
        strut_width         = dimensions.STRUT_WIDTH / 2.0
        strut_height_offset = dimensions.STRUT_HEIGHT_OFFSET
        
        radius = (dimensions.SMALL_CYLINDER_OUTER_RADIUS + dimensions.SMALL_CYLINDER_INNER_RADIUS) / 2.0
        mid_offset = panel_unit - radius
        
        wall_offset = wall_thickness / 2.0
        
        try:
            strut_cache = _strut_cache[(units_in_x, units_in_z)]
        except KeyError:
            strut_cache = _strut_cache[(units_in_x, units_in_z)] = []
            
            def createStrutVerts(start, end, height, x=True):
                vertices = []
                if x is True:
                    for x, z in (start, end):
                        vertices.append((x, height, z + strut_width))
                        vertices.append((x, strut_height_offset + smooth_offset, z + strut_width))
                        vertices.append((x, strut_height_offset, z + strut_width))
                        vertices.append((x, strut_height_offset, z + strut_width - smooth_offset))
                        vertices.append((x, strut_height_offset, z - strut_width + smooth_offset))
                        vertices.append((x, strut_height_offset, z - strut_width))
                        vertices.append((x, strut_height_offset + smooth_offset, z - strut_width))
                        vertices.append((x, height, z - strut_width))
                        
                else:
                    for x, z in (start, end):
                        vertices.append((x - strut_width, height, z))
                        vertices.append((x - strut_width, strut_height_offset + smooth_offset, z))
                        vertices.append((x - strut_width, strut_height_offset, z))
                        vertices.append((x - strut_width + smooth_offset, strut_height_offset, z))
                        vertices.append((x + strut_width - smooth_offset, strut_height_offset, z))
                        vertices.append((x + strut_width, strut_height_offset, z))
                        vertices.append((x + strut_width, strut_height_offset + smooth_offset, z))
                        vertices.append((x + strut_width, height, z))
                
                strut_cache.append(vertices)
                
            # in z
            #
            for unit_in_x_index in range(1, units_in_x):
                start = [unit * unit_in_x_index, wall_offset]
                end   = [unit * unit_in_x_index, mid_offset]
                createStrutVerts(start, end, height, False)
                start = [unit * unit_in_x_index, unit - mid_offset]
                end   = [unit * unit_in_x_index, unit - wall_offset]
                createStrutVerts(start, end, height, False)
                
            for unit_in_z_index in range(1, units_in_z):
                start = [wall_offset, unit * unit_in_z_index]
                end   = [mid_offset,  unit * unit_in_z_index]
                createStrutVerts(start, end, height, True)
                start = [unit - mid_offset,  unit * unit_in_z_index]
                end   = [unit - wall_offset, unit * unit_in_z_index]
                createStrutVerts(start, end, height, True)      
                    
        polygons = []
        for vertices in strut_cache:
            vert_ids = self._construct.addVertex(vertices)
            start = vert_ids[0:8]; end = vert_ids[8:]
           
            for index in range(7):
                polygons.append((start[index], start[index+1], end[index+1], end[index]))
            
                
        return self._construct.addPolygon(polygons)
    
    
    def buildRingFaces(self, rv, sv, flip=False, inner_corner=False):
        polygons = []; p_index = 0
        rv.append(rv[0]); sv.append(sv[0]);
        if inner_corner is False:
            for index in [0, 4, 8, 12]:
                polygons.append((sv[p_index],   rv[index],   rv[index+1], sv[p_index+1]))
                polygons.append((sv[p_index+1], rv[index+1], rv[index+2]))
                polygons.append((sv[p_index+1], rv[index+2], rv[index+3]))
                polygons.append((sv[p_index+1], rv[index+3], rv[index+4], sv[p_index+2]))                        
                p_index += 2
        else:
            for index in [0, 4, 8, 12]:
                if index == 0:
                    polygons.append((sv[p_index],   rv[index],   rv[index+1], sv[p_index+1]))
                    polygons.append((sv[p_index+1], rv[index+1], rv[index+2], sv[p_index+2]))
                    polygons.append((sv[p_index+2], rv[index+2], rv[index+3], sv[p_index+3]))
                    polygons.append((sv[p_index+3], rv[index+3], rv[index+4], sv[p_index+4]))
                    p_index += 4 
                else:
                    polygons.append((sv[p_index],   rv[index],   rv[index+1], sv[p_index+1]))
                    polygons.append((sv[p_index+1], rv[index+1], rv[index+2]))
                    polygons.append((sv[p_index+1], rv[index+2], rv[index+3]))
                    polygons.append((sv[p_index+1], rv[index+3], rv[index+4], sv[p_index+2]))                        
                    p_index += 2     
            
        if flip:
            for index, polygon in enumerate(polygons):
                polygons[index] = polygon[::-1]                   

        return self._construct.addPolygon(polygons)
    
    
    def create(self, units_in_x, units_in_z, height=1):
        self._construct = construct = Construct()
        
        unit           = dimensions.UNIT
        unit_offset    = dimensions.UNIT_OFFSET
        smooth_offset  = dimensions.SMOOTH_OFFSET
        wall_thickness = dimensions.WALL_THICKNESS
        
        x1 = z1 = unit_offset
        
        y1 = 0.0           
        y2 = dimensions.HEIGHT
        if height == Brick.HEIGHT_PLATE:
            y2 /= 3.0
        elif isinstance(height, int) and height > 0:
            y2 *= height
        y3 = y2 - wall_thickness
        
        panel_unit_offset = unit_offset / 2.0                

        # create box
        #
        apv = all_plane_vertices = []
        for y, offset, smooth in [(y3,                 wall_thickness + smooth_offset, False),
                                  (y3,                 wall_thickness,                 True),
                                  (y3 - smooth_offset, wall_thickness,                 True),
                                  (y1 + smooth_offset, wall_thickness,                 True),
                                  (y1,                 wall_thickness,                 True),
                                  (y1,                 wall_thickness - smooth_offset, True),
                                  (y1,                 smooth_offset,                  True),
                                  (y1,                 0,                              True),
                                  (y1 + smooth_offset, 0,                              True),
                                  (y2 - smooth_offset, 0,                              True),
                                  (y2,                 0,                              True),
                                  (y2,                 smooth_offset,                  False)]:
            apv.append(self.createPlaneVertices(units_in_x, units_in_z, y, offset, smooth))

        self.createPlanePolygons(units_in_x, units_in_z, all_plane_vertices)
        
        # add knobs
        #
        knob_edge_border   = dimensions.KNOB_EDGE_BORDER
        knob_radius        = dimensions.KNOB_RADIUS
        knob_height        = dimensions.KNOB_HEIGHT
        
        under_knob_radius = dimensions.UNDER_KNOB_RADIUS
        under_knob_height = dimensions.UNDER_KNOB_HEIGHT
        
        inner_radius = dimensions.CYLINDER_INNER_RADIUS
        outer_radius = dimensions.CYLINDER_OUTER_RADIUS
        
        small_inner_radius = dimensions.SMALL_CYLINDER_INNER_RADIUS
        small_outer_radius = dimensions.SMALL_CYLINDER_OUTER_RADIUS
        
        knobs = [[[[],[]] for _ in range(units_in_z)] for _ in range(units_in_x)]
        
        round_vertex = lambda vert: (round(vert[0], 2), round(vert[1], 2), round(vert[2], 2))
        
        outer_top_vert_ids = all_plane_vertices[-1]
        inner_top_vert_ids = all_plane_vertices[0]
        outer_top_vertices = [round_vertex(vertex) for vertex in construct.getVertex(outer_top_vert_ids)]
        inner_top_vertices = [round_vertex(vertex) for vertex in construct.getVertex(inner_top_vert_ids)]
        
        outer_vert_id_lookup = dict(zip(outer_top_vertices, outer_top_vert_ids))
        inner_vert_id_lookup = dict(zip(inner_top_vertices, inner_top_vert_ids))
        
        
        for unit_in_x_index in range(units_in_x):
            for unit_in_z_index in range(units_in_z):
                if unit_in_x_index > 0 and unit_in_z_index > 0: continue
                
                knob_center_x = x1 + knob_edge_border + knob_radius + (unit_in_x_index * unit) - panel_unit_offset             
                knob_center_z = z1 + knob_edge_border + knob_radius + (unit_in_z_index * unit) - panel_unit_offset 

                knob_vertex_ids = self.createKnob(knob_center_x, y2, knob_center_z, knob_height, knob_radius)
                
                if unit_in_x_index == 0: xs1 = x1 + smooth_offset
                else:                    xs1 = x1 + (unit_in_x_index * unit) - panel_unit_offset
                 
                if unit_in_x_index == 0 and unit_in_z_index > 0:
                    xs2 = x1 + unit - unit_offset - smooth_offset
                elif unit_in_x_index == (units_in_x - 1): 
                    xs2 = x1 + (unit * units_in_x) - unit_offset - smooth_offset
                else:                                   
                    xs2 = x1 + (unit * (unit_in_x_index + 1)) - panel_unit_offset
                 
                if unit_in_z_index == 0: zs1 = z1 + smooth_offset
                else:                    zs1 = z1 + (unit_in_z_index * unit) - panel_unit_offset
                 
                if unit_in_z_index == 0 and unit_in_x_index > 0:
                    zs2 = z1 + unit - unit_offset - smooth_offset
                elif unit_in_z_index == (units_in_z - 1): 
                    zs2 = z1 + (unit * units_in_z) - unit_offset - smooth_offset
                else:                                   
                    zs2 = z1 + (unit * (unit_in_z_index + 1)) - panel_unit_offset
                
                inner_corner = False
                square = [(xs2, y2, knob_center_z), [xs2, y2, zs2],
                          (knob_center_x, y2, zs2), [xs1, y2, zs2],
                          (xs1, y2, knob_center_z), [xs1, y2, zs1],
                          (knob_center_x, y2, zs1), [xs2, y2, zs1]]
                if unit_in_x_index == 0 and unit_in_z_index == 0:
                    square[1][0] -= smooth_offset + panel_unit_offset 
                    square[1][2] -= smooth_offset + panel_unit_offset
                    square.insert(1, [xs2 - panel_unit_offset, y2, zs2 - smooth_offset - panel_unit_offset])
                    square.insert(3, [xs2 - smooth_offset - panel_unit_offset, y2, zs2 - panel_unit_offset])
                    inner_corner = True
                elif unit_in_x_index == 0 and unit_in_z_index == 1:
                    square[7][2] -= panel_unit_offset
                elif unit_in_x_index == 1 and unit_in_z_index == 0:
                    square[3][0] -= panel_unit_offset                     
                
                square_vert_ids = [] 
                for vertex in square:
                    rounded_vertex = round_vertex(vertex)
                    try:
                        vert_id = outer_vert_id_lookup[rounded_vertex]
                    except KeyError:
                        vert_id = construct.addVertex(vertex)
                        outer_vert_id_lookup[rounded_vertex] = vert_id                    
                    square_vert_ids.append(vert_id)
                
                self.buildRingFaces(knob_vertex_ids, square_vert_ids, False, inner_corner)
                
                y3 = y2 - wall_thickness
                under_knob_bttm_ids = self.createKnob(knob_center_x, y3, knob_center_z, under_knob_height, under_knob_radius, flip=True)
                
                if unit_in_x_index == 0: 
                    xs1 = xs1 + wall_thickness
                if unit_in_x_index == (units_in_x - 1) or (unit_in_x_index == 0 and unit_in_z_index > 0): 
                    xs2 = xs2 - wall_thickness
                if unit_in_z_index == 0:
                    zs1 = zs1 + wall_thickness
                if unit_in_z_index == (units_in_z - 1) or (unit_in_z_index == 0 and unit_in_x_index > 0):    
                    zs2 = zs2 - wall_thickness                
                
                square = [(xs2, y3, knob_center_z), [xs2, y3, zs2],
                          (knob_center_x, y3, zs2), [xs1, y3, zs2],
                          (xs1, y3, knob_center_z), [xs1, y3, zs1],
                          (knob_center_x, y3, zs1), [xs2, y3, zs1]]
                
                if unit_in_x_index == 0 and unit_in_z_index == 0:
                    square[1][0] -= wall_thickness + smooth_offset + panel_unit_offset 
                    square[1][2] -= wall_thickness + smooth_offset + panel_unit_offset
                    offset = wall_thickness + panel_unit_offset
                    offset2 = offset + smooth_offset
                    square.insert(1, [xs2 - offset, y3, zs2 - offset2])
                    square.insert(3, [xs2 - offset2, y3, zs2 - offset])
                    
                elif unit_in_x_index == 0 and unit_in_z_index == 1:
                    square[7][2] -= wall_thickness + panel_unit_offset
                    
                elif unit_in_x_index == 1 and unit_in_z_index == 0:
                    square[3][0] -= wall_thickness + panel_unit_offset                
                
                square_vert_ids = []                
                for vertex in square:
                    rounded_vertex = round_vertex(vertex)
                    try:
                        vert_id = inner_vert_id_lookup[rounded_vertex]
                    except KeyError:
                        vert_id = construct.addVertex(vertex)
                        inner_vert_id_lookup[rounded_vertex] = vert_id
                    square_vert_ids.append(vert_id)
                
                self.buildRingFaces(under_knob_bttm_ids, square_vert_ids, True, inner_corner)
            
                if unit_in_x_index == 0 and unit_in_z_index > 0:       
                    cyl_x = x1 + (unit / 2.0)
                    cyl_z = z1 + (unit_in_z_index * unit) - panel_unit_offset
                    cylinder_base_verts = self.createCylinder(cyl_x, y1, y2 - wall_thickness, cyl_z, small_inner_radius, small_outer_radius)
                    
                elif unit_in_z_index == 0 and unit_in_x_index > 0:                    
                    cyl_x = x1 + (unit_in_x_index * unit) - panel_unit_offset
                    cyl_z = z1 + (unit / 2.0) 
                    cylinder_base_verts = self.createCylinder(cyl_x, y1, y2 - wall_thickness, cyl_z, small_inner_radius, small_outer_radius)   

        self.buildStruts(units_in_x, units_in_z, y2 - (wall_thickness / 2.0))
        
        transform, mesh = construct.build(self.name)
        self._construct = None
                        
        mc.sets(transform, e=True, forceElement='initialShadingGroup')
    
      
#--------------------------------------------------------------------------------------------------#      
      
class Brick1x1(Brick):
    def create(self):
        Brick.create(self, 1, 1)
        
        
class Brick1x2(Brick):
    def create(self):
        Brick.create(self, 1, 2)
        
        
class Brick1x1x3(Brick):
    def create(self):
        Brick.create(self, 1, 1, 3)
        
        
class Brick1x3(Brick):
 def create(self):
     Brick.create(self, 1, 3)
     
     
class Brick1x2x2(Brick):
    def create(self):
        Brick.create(self, 1, 2, 2)
        
        
class Brick2x2(Brick):
    def create(self):
        Brick.create(self, 2, 2)
        
        
class Brick1x4(Brick):
 def create(self):
     Brick.create(self, 1, 4)
     
     
class Brick1x1x5(Brick):
 def create(self):
     Brick.create(self, 1, 1, 5)
     

class Brick2x3(Brick):
    def create(self):
        Brick.create(self, 2, 3)
        

class Brick1x6(Brick):
 def create(self):
     Brick.create(self, 1, 6)
     

class Brick2x4(Brick):
    def create(self):
        Brick.create(self, 2, 4)
        
        
class Brick1x8(Brick):
 def create(self):
     Brick.create(self, 1, 8)
     
     
class Brick1x10(Brick):
 def create(self):
     Brick.create(self, 1, 10)
     

class Brick2x2x3(Brick):
    def create(self):
        Brick.create(self, 2, 2, 3)
        
     
class Brick1x12(Brick):
 def create(self):
     Brick.create(self, 1, 12)
     
     
class Brick2x6(Brick):
    def create(self):
        Brick.create(self, 2, 6)


class Brick1x12(Brick):
 def create(self):
     Brick.create(self, 1, 16)
     
     
class Brick2x8(Brick):
    def create(self):
        Brick.create(self, 2, 8)
        
        
class Brick2x10(Brick):
    def create(self):
        Brick.create(self, 2, 10)
        

class Brick2x4x3(Brick):
    def create(self):
        Brick.create(self, 2, 4, 3)
        
        
class Brick4x6(Brick):
    def create(self):
        Brick.create(self, 4, 6)
        
        
class Brick2x6x3(Brick):
    def create(self):
        Brick.create(self, 2, 6, 3)


class Brick1x1x5(Brick):
    def create(self):
        Brick.create(self, 1, 1, 5, hollow=True)


class Brick1x3x5(Brick):
    def create(self):
        Brick.create(self, 1, 3, 5, hollow=True)


class Brick1x6x5(Brick):
    def create(self):
        Brick.create(self, 1, 6, 5, hollow=True)
        
        
class Brick4x10(Brick):
    def create(self):
        Brick.create(self, 4, 10)
        

class Brick4x12(Brick):
    def create(self):
        Brick.create(self, 4, 12)
        
        
class Brick8x8(Brick):
    def create(self):
        Brick.create(self, 8, 8)


class Brick4x18(Brick):
    def create(self):
        Brick.create(self, 4, 18)
        
        
class Brick8x16(Brick):
    def create(self):
        Brick.create(self, 8, 16)
        
        
class Brick12x24(Brick):
    def create(self):
        Brick.create(self, 12, 24)
        
        
class BrickCorner1x2x2(BrickCorner):
    def create(self):
        BrickCorner.create(self, 2, 2)