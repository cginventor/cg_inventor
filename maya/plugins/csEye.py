import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import math

#--------------------------------------------------------------------------------------------------#

def interp(start, end, value):
    return (value - start)/(end - start)



def getWeighting(point):
    # get weighting values
    #
    x1 = point[0] + 0.5
    x0 = 1.0 - x1
    y1 = point[1] + 0.5
    y0 = 1.0 - y1
    z1 = point[2] + 0.5
    z0 = 1.0 - z1
    
    # compute weight for each lattice point
    #
    weights = []; total = 0
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                w = x * y * z
                weights.append(w)
                total += w
    
    # normalize weight values
    #      
    scale = 1.0 / total
    return [w * scale for w in weights]



def warpPoint(point, weighting, vectors):
    offset = om.MVector(0,0,0)
    
    for weight, vector in zip(weighting, vectors):
        if vector is None or weight == 0:
            continue
        offset += vector * weight
        
    return point + offset 

#--------------------------------------------------------------------------------------------------#

def calculateCurve(in_angle, out_angle, divisions):   
    in_angle = math.radians(in_angle)
    out_angle = math.radians(out_angle)
    
    in_tangent =(math.cos(in_angle) * 0.5, math.sin(in_angle) * 0.5)
    out_tangent = (-math.cos(out_angle) * 0.5, math.sin(out_angle) * 0.5)
    
    p0 = om.MVector(0, 0, 0)
    p1 = om.MVector(in_tangent[0], 0, in_tangent[1])
    p2 = om.MVector(out_tangent[0] + 1, 0, out_tangent[1] + 1)
    p3 = om.MVector(1, 0, 1)
            
    vectors = []
    increment = 1.0 / divisions
    t_values = [index * increment for index in range(0, divisions+1)]
    t_values.insert(1, t_values[1] * 0.333333333)
    t_values.insert(-1, (1.0 - t_values[-2]) * 0.666666666 + t_values[-2])

    for t in t_values:            
        a = p0 * math.pow((1.0 - t), 3) 
        b = p1 * (3 * t * math.pow(1.0 - t, 2)) 
        c = p2 * (3 * math.pow(t, 2) * (1.0 - t))
        d = p3 * math.pow(t, 3)

        vectors.append((a + b + c + d))
    
    return vectors

#--------------------------------------------------------------------------------------------------#

class NurbsSphere(object):
    cvs = [(0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0, -0.5, 0),
           (0.05095834807853684, -0.5, -0.05095834807853698),
           (0.07206598696879582, -0.5, 0),
           (0.05095834807853691, -0.5, 0.05095834807853684),
           (0, -0.5, 0.07206598696879579),
           (-0.05095834807853685, -0.5, 0.05095834807853689),
           (-0.07206598696879583, -0.5, 0),
           (-0.050958348078536914, -0.5, -0.050958348078536865),
           (0, -0.5, -0.07206598696879585),
           (0.05095834807853684, -0.5, -0.05095834807853698),
           (0.07206598696879582, -0.5, 0),
           (0.05095834807853691, -0.5, 0.05095834807853684),
           (0.15399058328790757, -0.4739659357910228, -0.15399058328790782),
           (0.2177755713635027, -0.4739659357910228, 0),
           (0.15399058328790766, -0.4739659357910228, 0.15399058328790763),
           (0, -0.4739659357910228, 0.21777557136350267),
           (-0.1539905832879076, -0.4739659357910228, 0.15399058328790766),
           (-0.21777557136350276, -0.4739659357910228, 0),
           (-0.15399058328790766, -0.4739659357910228, -0.1539905832879076),
           (0, -0.4739659357910228, -0.21777557136350273),
           (0.15399058328790757, -0.4739659357910228, -0.15399058328790782),
           (0.2177755713635027, -0.4739659357910228, 0),
           (0.15399058328790766, -0.4739659357910228, 0.15399058328790763),
           (0.28422099513819493, -0.36275782226528064, -0.2842209951381954),
           (0.4019491860356131, -0.36275782226528064, 0),
           (0.2842209951381951, -0.36275782226528064, 0.2842209951381951),
           (0, -0.36275782226528064, 0.4019491860356131),
           (-0.28422099513819504, -0.36275782226528064, 0.2842209951381952),
           (-0.4019491860356132, -0.36275782226528064, 0),
           (-0.28422099513819515, -0.36275782226528064, -0.28422099513819493),
           (0, -0.36275782226528064, -0.4019491860356131),
           (0.28422099513819493, -0.36275782226528064, -0.2842209951381954),
           (0.4019491860356131, -0.36275782226528064, 0),
           (0.2842209951381951, -0.36275782226528064, 0.2842209951381951),
           (0.3714167174908939, -0.19632311870749702, -0.37141671749089433),
           (0.5252625591677188, -0.19632311870749705, 0),
           (0.37141671749089394, -0.19632311870749708, 0.37141671749089405),
           (0, -0.19632311870749708, 0.5252625591677188),
           (-0.371416717490894, -0.19632311870749708, 0.37141671749089405),
           (-0.5252625591677189, -0.19632311870749705, 0),
           (-0.371416717490894, -0.19632311870749702, -0.3714167174908939),
           (0, -0.19632311870749702, -0.5252625591677188),
           (0.3714167174908939, -0.19632311870749702, -0.37141671749089433),
           (0.5252625591677188, -0.19632311870749705, 0),
           (0.37141671749089394, -0.19632311870749708, 0.37141671749089405),
           (0.40200035992297106, 0, -0.40200035992297156),
           (0.5685143610819317, 0, 0),
           (0.4020003599229712, 0, 0.4020003599229713),
           (0, 0, 0.5685143610819317),
           (-0.4020003599229712, 0, 0.4020003599229713),
           (-0.5685143610819318, 0, 0),
           (-0.40200035992297123, 0, -0.40200035992297106),
           (0, 0, -0.5685143610819317),
           (0.40200035992297106, 0, -0.40200035992297156),
           (0.5685143610819317, 0, 0),
           (0.4020003599229712, 0, 0.4020003599229713),
           (0.3714167174908938, 0.19632311870749733, -0.3714167174908943),
           (0.5252625591677187, 0.1963231187074973, 0),
           (0.3714167174908939, 0.19632311870749727, 0.371416717490894),
           (0, 0.19632311870749727, 0.5252625591677187),
           (-0.3714167174908939, 0.19632311870749727, 0.371416717490894),
           (-0.5252625591677187, 0.1963231187074973, 0),
           (-0.37141671749089394, 0.19632311870749733, -0.3714167174908938),
           (0, 0.19632311870749733, -0.5252625591677187),
           (0.3714167174908938, 0.19632311870749733, -0.3714167174908943),
           (0.5252625591677187, 0.1963231187074973, 0),
           (0.3714167174908939, 0.19632311870749727, 0.371416717490894),
           (0.2842209951381948, 0.36275782226528075, -0.28422099513819515),
           (0.40194918603561286, 0.36275782226528075, 0),
           (0.2842209951381949, 0.36275782226528075, 0.284220995138195),
           (0, 0.36275782226528075, 0.40194918603561286),
           (-0.28422099513819493, 0.36275782226528075, 0.284220995138195),
           (-0.4019491860356129, 0.36275782226528075, 0),
           (-0.28422099513819493, 0.36275782226528075, -0.2842209951381948),
           (0, 0.36275782226528075, -0.40194918603561286),
           (0.2842209951381948, 0.36275782226528075, -0.28422099513819515),
           (0.40194918603561286, 0.36275782226528075, 0),
           (0.2842209951381949, 0.36275782226528075, 0.284220995138195),
           (0.15399058328790738, 0.4739659357910228, -0.15399058328790755),
           (0.21777557136350242, 0.4739659357910228, 0),
           (0.15399058328790743, 0.4739659357910228, 0.15399058328790752),
           (0, 0.4739659357910228, 0.21777557136350245),
           (-0.15399058328790743, 0.4739659357910228, 0.1539905832879075),
           (-0.21777557136350248, 0.4739659357910228, 0),
           (-0.15399058328790743, 0.4739659357910228, -0.15399058328790735),
           (0, 0.4739659357910228, -0.2177755713635024),
           (0.15399058328790738, 0.4739659357910228, -0.15399058328790755),
           (0.21777557136350242, 0.4739659357910228, 0),
           (0.15399058328790743, 0.4739659357910228, 0.15399058328790752),
           (0.05095834807853668, 0.5, -0.05095834807853668),
           (0.07206598696879553, 0.5, 0),
           (0.05095834807853665, 0.5, 0.05095834807853673),
           (0, 0.5, 0.07206598696879556),
           (-0.05095834807853669, 0.5, 0.05095834807853669),
           (-0.07206598696879554, 0.5, 0),
           (-0.05095834807853666, 0.5, -0.05095834807853665),
           (0, 0.5, -0.0720659869687955),
           (0.05095834807853668, 0.5, -0.05095834807853668),
           (0.07206598696879553, 0.5, 0),
           (0.05095834807853665, 0.5, 0.05095834807853673),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0),
           (0, 0.5, 0)]
    
    points = om.MPointArray()
    for cv in cvs:
        points.append(om.MPoint(*cv))
   
    knotsU = om.MDoubleArray()
    for knot in [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0]:
        knotsU.append(knot)        
        
    knotsV = om.MDoubleArray()
    for knot in [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
        knotsV.append(knot)
    
    degreeU = 3
    degreeV = 3
    
    formU = 1
    formV = 3
   
    @staticmethod
    def create(cvs):
        data = om.MFnNurbsSurfaceData()
        surface_data = data.create()
        
        knotsU = NurbsSphere.knotsU            
        knotsV = NurbsSphere.knotsV
            
        degreeU = NurbsSphere.degreeU
        degreeV = NurbsSphere.degreeV
        
        formU = NurbsSphere.formU
        formV = NurbsSphere.formV

        surface = om.MFnNurbsSurface()
        surface.create(cvs, knotsU, knotsV, degreeU, degreeV, formU, formV, True, surface_data)
        
        return surface, surface_data
    
#--------------------------------------------------------------------------------------------------#
 
class CSEye(omMPx.MPxNode):
    plugin_node_id = om.MTypeId(0x00000001)
    
    
    def __init__(self, *args, **kwargs):
        omMPx.MPxNode.__init__(self, *args, **kwargs)
        
        self.lattice_points = []
        
        self.u_spans = None
        self.v_spans = None
        
        self.front_vector = om.MVector(0, 0, 0.5)
        self.center_vector = om.MVector(0, 0, 0)
        self.back_vector = om.MVector(0, 0, -0.5)
        self.projection_vector = self.front_vector
        self.surface_normal = om.MVector(0, 0, 1)        
        self.offset_angles = []
        
        self.projection_matrix = om.MMatrix()
        self.aim_matrix = om.MMatrix()
        self.lattice_matrix = om.MMatrix()
        self.iris_matrix = om.MMatrix()
        
        self.iris_size = None
        self.iris_rotate_x = None
        self.iris_scale_x = None
        self.iris_scale_y = None
        self.iris_ring = []
        self.iris_dirty = False
        self.iris_divisions = None
        self.iris_curve_angle = None
        self.iris_curve_values = None        
        self.iris_vertices = om.MVectorArray()        
        self.iris_faces = om.MIntArray()        
        self.iris_connections = om.MIntArray()
        
        self.pupil_size = None
        self.pupil_translate_x = None
        self.pupil_translate_y = None
        self.pupil_rotate_x = None
        self.pupil_scale_x = None
        self.pupil_scale_y = None
        self.pupil_ring = []
        self.pupil_dirty = False
                
        self.eyeball_key = []
        self.eyeball_dirty = False
        self.eyeball_vertices = om.MVectorArray()
        self.eyeball_faces = om.MIntArray()        
        self.eyeball_connections = om.MIntArray()        

               
 
    def compute(self, plug, data):
        plug_name = plug.partialName()
        print plug_name
        
        if plug_name == 'eyeball':
            self.createEyeball(plug, data)
        
        if plug_name == 'iris':
            self.createIris(plug, data)
        
        data.setClean(plug)
        
        
        
    def createIris(self, plug, data):
        self.computeIrisVertices(plug, data)
        data_handle = om.MDataHandle(data.inputValue(self.latticeMatrix_attr)) 
        lattice_matrix = data_handle.asMatrix()

        translate_vector = om.MTransformationMatrix(lattice_matrix).getTranslation(om.MSpace.kWorld) 
        print 'RECALCULATING IRIS'
        # convert vectors to points
        #
        iris_points = om.MPointArray()
        for vert_index in range(self.iris_vertices.length()):
            vertex = (self.iris_vertices[vert_index] * lattice_matrix) + translate_vector
            iris_points.append(om.MPoint(vertex))

#         verts = [iris_points[index] for index in range(iris_points.length())]
#         print 'V = {}'.format([(v.x, v.y, v.z) for v in verts])
#         print 'F = {}'.format([self.iris_faces[index] for index in range(self.iris_faces.length())])
#         print 'C = {}'.format([self.iris_connections[index] for index in range(self.iris_connections.length())])
#         return
        # create mesh output
        #
        mesh_data = om.MFnMeshData()
        mesh_data_obj = mesh_data.create()

        mesh = om.MFnMesh()        
        mesh.create(iris_points.length(), 
                    self.iris_faces.length(), 
                    iris_points, 
                    self.iris_faces, 
                    self.iris_connections, 
                    mesh_data_obj)
        
        data.outputValue(self.iris_attr).setMObject(mesh_data_obj)
        
        
            
    def computeIrisFaces(self, plug, data):
        u_spans = data.inputValue(self.uSpans_attr).asInt()
        
        compute = u_spans != self.u_spans
        compute |= self.computeIrisCurve(plug, data)         

        if not compute:
            return False
        print 'RECALCULATING IRIS FACES'
        self.iris_faces = om.MIntArray()
        self.iris_connections = om.MIntArray()
        
        faces = []
        v_spans = len(self.iris_curve_values) + 3
        spans = v_spans
        for u_index in range(u_spans):
            start = (u_index * spans)
            end = ((u_index + 1) * spans) + 1 if u_index < (u_spans - 1) else 1
            for v_index in range(v_spans-1):
                a = start + v_index
                b = a + 1
                c = end + v_index
                d = c - 1
                 
                for face_index in (a,d,c,b):
                    self.iris_connections.append(face_index)
                self.iris_faces.append(4)
        
        return True



    def computeIrisCurve(self, plug, data):
        iris_curve_angle = data.inputValue(self.irisCurveAngle_attr).asFloat()
        iris_divisions = data.inputValue(self.irisDivisions_attr).asInt()       
        
        if iris_curve_angle == self.iris_curve_angle and iris_divisions == self.iris_divisions:
            return False
        
        print 'RECALCULATING IRIS CURVE'
        self.iris_curve_angle = iris_curve_angle
        self.iris_divisions = iris_divisions

        self.iris_curve_values = calculateCurve(iris_curve_angle, 
                                                iris_curve_angle-90, 
                                                iris_divisions)        
        return True
    
    
    
    def computeIrisVertices(self, plug, data):
        compute = self.computeIrisRing(plug, data)
        compute |= self.computeIrisFaces(plug, data)
        compute |= self.computeIrisCurve(plug, data)
        compute |= self.computePupilRing(plug, data)
        compute |= self.iris_dirty
        
        if not compute:
            return False
        print 'CALCULATING IRIS VERTICES'
        # get input attributes
        #
        u_spans = len(self.iris_curve_values) + 3
        iris_size = data.inputValue(self.irisSize_attr).asFloat()        
        pupil_depth = data.inputValue(self.pupilDepth_attr).asFloat() * iris_size

        pupil_center = self.iris_center - (self.surface_normal * pupil_depth)
        self.pupil_center = pupil_center
        
        self.iris_vertices = om.MVectorArray() 
        
        # create mesh vertices
        #
        for iris_vector, pupil_vector in zip(self.iris_ring, self.pupil_ring):
            pupil_vector = pupil_center + pupil_vector * self.iris_matrix
            iris_pupil_vector = iris_vector - pupil_vector           
            
            # get x and z axis for curved division vectors
            #                                        
            rotation_vector = self.surface_normal ^ (iris_pupil_vector.normal() ^ self.surface_normal)
            rotation_vector.normalize()
            
            x_axis = self.surface_normal * (iris_pupil_vector * self.surface_normal)
            z_axis = rotation_vector * (rotation_vector * iris_pupil_vector)  
    
            for u_index in range(u_spans):
                # u_index less than 3 is the inner back iris spans
                #
                if u_index < 3:
                    output = om.MVector(pupil_vector - (self.surface_normal * ((3 - u_index) * 0.015) * iris_size))
                    if u_index < 2:
                        output += z_axis * ((2 - u_index) * 0.1)
                
                # u_index 3 is the edge of the pupil
                #
                elif u_index == 3:
                    output = pupil_vector                    

                # the last u_index is the edge of the iris
                #
                elif u_index == u_spans - 1:
                    output = iris_vector
                
                # all other u_indices and curved divisions between the pupil and the iris
                #
                else:
                    division_vector = self.iris_curve_values[u_index-2]
                    division_vector = z_axis * division_vector[0] + x_axis * division_vector[2]
                    output = om.MVector(pupil_vector + division_vector)
                
                self.iris_vertices.append(output)
        
        self.iris_dirty = False

        return True
        
    
    
    def computePupilRing(self, plug, data):
        compute = self.computePupilRotation(plug, data)
        compute |= self.computeIrisRing(plug, data)
 
        pupil_size = data.inputValue(self.pupilSize_attr).asFloat()        
        pupil_translate_x = data.inputValue(self.pupilTranslateX_attr).asFloat()
        pupil_translate_y = data.inputValue(self.pupilTranslateY_attr).asFloat()
        pupil_scale_x = data.inputValue(self.pupilScaleX_attr).asFloat()
        pupil_scale_y = data.inputValue(self.pupilScaleY_attr).asFloat()        

        compute |= pupil_size != self.pupil_size
        compute |= pupil_translate_x != self.pupil_translate_x
        compute |= pupil_translate_y != self.pupil_translate_y
        compute |= pupil_scale_x != self.pupil_scale_x
        compute |= pupil_scale_y != self.pupil_scale_y
        
        if not compute:
            return False
        print 'RECALCUTING PUPIL RING'
        self.pupil_size = pupil_size
        self.pupil_translate_x = pupil_translate_x
        self.pupil_translate_y = pupil_translate_y
        self.pupil_scale_x = pupil_scale_x
        self.pupil_scale_y = pupil_scale_y
        
        iris_size = data.inputValue(self.irisSize_attr).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX_attr).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY_attr).asFloat()
        
        pupil_size_x = pupil_size * pupil_scale_x * iris_size
        pupil_size_y = pupil_size * pupil_scale_y * iris_size
        
        pupil_translate_x *= iris_size * iris_scale_x * 0.5
        pupil_translate_y *= iris_size * iris_scale_y * 0.5
        
        pupil_offset_x = self.iris_rotation_vectors[0] * pupil_translate_x
        pupil_offset_y = self.iris_rotation_vectors[1] * pupil_translate_y
        
        self.pupil_ring = []
        for pupil_vector in self.iris_vectors:
            # rotate by iris rotation
            #
            pupil_vector_x_length = (self.pupil_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = self.pupil_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (self.pupil_rotation_vectors[1] * pupil_vector) 
            pupil_vector_dot_y = self.pupil_rotation_vectors[1] * pupil_vector_y_length
             
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - pupil_size_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - pupil_size_y))
            
            # rotate by pupil rotation
            #
            pupil_vector_x_length = (self.iris_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = self.iris_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (self.iris_rotation_vectors[1] * pupil_vector)
            pupil_vector_dot_y = self.iris_rotation_vectors[1] * pupil_vector_y_length
 
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - iris_scale_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - iris_scale_y))
            
            pupil_vector += (pupil_offset_x + pupil_offset_y)
            pupil_vector *= 0.5
            self.pupil_ring.append(pupil_vector)
        
        return True
                    
        
        
    def computePupilRotation(self, plug, data):    
        iris_rotate_x = data.inputValue(self.irisRotateX_attr).asFloat()
        pupil_rotate_x = data.inputValue(self.pupilRotateX_attr).asFloat()
        
        if iris_rotate_x == self.iris_rotate_x and pupil_rotate_x == self.pupil_rotate_x:
            return False
        print 'RECALCUTING PUPIL ROTATION'
        pupil_rotation = iris_rotate_x + pupil_rotate_x
        
        x_radians = math.radians(pupil_rotation)
        y_radians = math.radians(pupil_rotation + 90)
        x_rotation_vector = om.MVector(math.cos(x_radians), math.cos(y_radians), 0)
        y_rotation_vector = om.MVector(math.sin(x_radians), math.sin(y_radians), 0)
        
        self.pupil_rotate_x = pupil_rotate_x
        self.pupil_rotation_vectors = (x_rotation_vector, y_rotation_vector)
        
        return True
        
    
    
    def createEyeball(self, plug, data):
        self.computeEyeballVertices(plug, data)
        
        data_handle = om.MDataHandle(data.inputValue(self.latticeMatrix_attr)) 
        lattice_matrix = data_handle.asMatrix()
        
        self.lattice_matrix = lattice_matrix
        translate_vector = om.MTransformationMatrix(lattice_matrix).getTranslation(om.MSpace.kWorld) 
        print 'RECALCULATING EYEBALL'
        # convert vectors to points
        #
        eyeball_points = om.MPointArray()
        for vert_index in range(self.eyeball_vertices.length()):
            vertex = self.eyeball_vertices[vert_index] * lattice_matrix + translate_vector
            eyeball_points.append(om.MPoint(vertex))
#         
#         print 'V = {}'.format([(v.x, v.y, v.z) for v in verts])
#         print 'F = {}'.format([self.iris_faces[index] for index in range(self.iris_faces.length())])
#         print 'C = {}'.format([self.iris_connections[index] for index in range(self.iris_connections.length())])
#         return
        
        # create mesh output
        #
        mesh_data = om.MFnMeshData()
        mesh_data_obj = mesh_data.create()
        
        mesh = om.MFnMesh()        
        mesh.create(eyeball_points.length(), 
                    self.eyeball_faces.length(), 
                    eyeball_points, 
                    self.eyeball_faces, 
                    self.eyeball_connections, 
                    mesh_data_obj)
        
        data.outputValue(self.eyeball_attr).setMObject(mesh_data_obj)


        
    def computeEyeballVertices(self, plug, data):
        compute = self.computeIrisRing(plug, data)        
        compute |= self.computeEyeballFaces(plug, data)
        compute |= self.eyeball_dirty
        
        if not compute:
            return False
        
        data_handle = om.MDataHandle(data.inputValue(self.aimMatrix_attr))
        aim_matrix = om.MTransformationMatrix(data_handle.asMatrix()).asRotateMatrix()
        
        print 'RECALCUTING EYEBALL VERTICES'
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()
        
        self.eyeball_vertices = om.MVectorArray()
        self.eyeball_vertices.append(self.back_vector)

        for iris_index in range(len(self.iris_ring)):            
            iris_point = self.iris_ring[iris_index]
            iris_vector = self.iris_vectors[iris_index]
            iris_angle = self.iris_angles[iris_index]
#             offset_angle = self.offset_angles[iris_index]
            
            self.eyeball_vertices.append(om.MVector(iris_point)) 
         
            eyeball_angle = 180.0 - iris_angle
            
            u_angle = self.u_angles[iris_index]

            for v_index in range(1, self.v_spans + 1):
                v_degrees = (self.v_angles[v_index] * eyeball_angle)
                v_angle = math.radians(v_degrees + iris_angle)
                scale = math.sin(v_angle) * 0.5
                    
                u_radians = math.radians(u_angle)
                x = math.sin(u_radians) * scale
                y = math.cos(u_radians) * scale
                z = math.cos(v_angle) * 0.5
                v_vector = om.MVector(x, y, z) * self.projection_matrix
#                 v_vector = om.MVector(x, y, z) * aim_matrix
                
                weighting = getWeighting(v_vector)
                v_point = warpPoint(v_vector, weighting, self.lattice_vectors)
                
                self.eyeball_vertices.append(v_point)
                
        self.eyeball_dirty = False
                
        return True
    
    
    
    def computeEyeballFaces(self, plug, data):
        u_spans = data.inputValue(self.uSpans_attr).asInt()
        v_spans = data.inputValue(self.vSpans_attr).asInt()
        
        if u_spans == self.u_spans and v_spans == self.v_spans:
            return False
        print 'RECALCUTING EYEBALL FACES'
        self.v_angles = [a[0] for a in calculateCurve(45, 0, v_spans-2)]
        self.v_spans = v_spans
        
        self.eyeball_faces = om.MIntArray()
        self.eyeball_connections = om.MIntArray()
        
        spans = self.v_spans + 1
        for u_index in range(u_spans):
            start = (u_index * spans) + 1
            end = ((u_index + 1) * spans) + 2 if u_index < (u_spans - 1) else 2
            for v_index in range(self.v_spans):
                a = start + v_index
                b = a + 1
                c = end + v_index
                d = c - 1
                
                for face_index in (a,d,c,b):
                    self.eyeball_connections.append(face_index)
                self.eyeball_faces.append(4)
                
            for face_index in (b, c, 0):
                self.eyeball_connections.append(face_index)
            self.eyeball_faces.append(3)         
        
        return True
    
    
    
    def computeIrisRotation(self, plug, data):
        iris_rotate_x = data.inputValue(self.irisRotateX_attr).asFloat()
        
        if iris_rotate_x == self.iris_rotate_x:
            return False 
        print 'RECALCUTING IRIS ROTATION'
        x_radians = math.radians(iris_rotate_x)
        y_radians = math.radians(iris_rotate_x + 90)
        x_rotate_vector = om.MVector(math.cos(x_radians), math.cos(y_radians), 0)
        y_rotate_vector = om.MVector(math.sin(x_radians), math.sin(y_radians), 0)
        
        # force recalculate of pupil rotation so they don't get out of sync
        #
        self.computePupilRotation(plug, data)
        
        # store data
        #
        self.iris_rotate_x = iris_rotate_x        
        self.iris_rotation_vectors = (x_rotate_vector, y_rotate_vector)
        
        return True
        
        
        
    def computeIrisRing(self, plug, data):
        u_spans = data.inputValue(self.uSpans_attr).asInt()
        iris_size = data.inputValue(self.irisSize_attr).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX_attr).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY_attr).asFloat()
               
        iris_ring_key = (u_spans, iris_size, iris_scale_x, iris_scale_y)
        old_iris_ring_key = (self.u_spans, self.iris_size, self.iris_scale_x, self.iris_scale_y)
        
        compute = iris_ring_key != old_iris_ring_key 
        compute |= self.computeIrisProjection(plug, data)
        compute |= self.computeEyeballProjection(plug, data)
        compute |= self.computeIrisRotation(plug, data)
        
        if not compute:
            return False
        print 'RECALCULATING IRIS RING'
        self.u_spans = u_spans
        
        self.iris_size = iris_size
        self.iris_scale_x = iris_scale_x
        self.iris_scale_y = iris_scale_y
        self.iris_ring_key = iris_ring_key
        
        aim_inverse = self.aim_matrix.inverse()
        
        self.iris_vectors = []
        self.iris_ring = []
        self.iris_angles = []
        self.offset_angles = []
        self.u_angles = []
        self.compensated_u_angles = []
        
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()
        
        u_angle_increment = 360.0 / self.u_spans 
        
        iris_radius = self.iris_size / 2.0
        
        matrix_util = om.MScriptUtil()
        
        up_vector = om.MVector(0,1,0)
        
        center = self.unwarped_front_vector * aim_inverse
        center = om.MVector(center.x, center.y, 0.0)

        for u_index in range(self.u_spans):
            u_angle = math.radians(u_angle_increment * u_index)
            
            iris_vector = om.MVector(math.sin(u_angle), math.cos(u_angle), 0)
            self.iris_vectors.append(iris_vector)
            
            # get uniform iris point
            #
            uniform_iris_vector = iris_vector * iris_radius
            uniform_iris_vector = uniform_iris_vector * self.iris_matrix
            uniform_iris_vector = uniform_iris_vector + self.front_vector
                          
            uniform_iris_point = om.MPoint(uniform_iris_vector + self.surface_normal)
            hit = self.surface.intersect(uniform_iris_point, -self.surface_normal, u_ptr, v_ptr, uniform_iris_point)
            if not hit:
                uniform_iris_point = self.surface.closestPoint(om.MPoint(uniform_iris_vector))
                self.surface.getParamAtPoint(uniform_iris_point, u_ptr, v_ptr)
                 
            # convert uniform iris point on undeformed surface
            #
            u, v = om.MScriptUtil.getDouble(u_ptr), om.MScriptUtil.getDouble(v_ptr)
            unwarped_uniform_iris_point = om.MPoint()
            self.default_surface.getPointAtParam(u, v, unwarped_uniform_iris_point)
            unwarped_uniform_iris_vector = om.MVector(unwarped_uniform_iris_point)            
             
            # invert aim matrix to calculate compensated u_angle
            #
            a = unwarped_uniform_iris_vector * aim_inverse
            a = om.MVector(a.x, a.y, 0) - center
            compensated_u_angle = up_vector.angle(a)
            if a.x < 0:
                compensated_u_angle *= -1
                 
            self.u_angles.append(math.degrees(compensated_u_angle))   
            
            # get rotated/scaled iris point
            #
            iris_vector_x_length = (self.iris_rotation_vectors[0] * iris_vector)
            iris_vector_dot_x = self.iris_rotation_vectors[0] * iris_vector_x_length
            iris_vector_y_length = (self.iris_rotation_vectors[1] * iris_vector)
            iris_vector_dot_y = self.iris_rotation_vectors[1] * iris_vector_y_length
  
            iris_vector = iris_vector - (iris_vector_dot_x * (1 - iris_scale_x))
            iris_vector = iris_vector - (iris_vector_dot_y * (1 - iris_scale_y))
            
            iris_vector = iris_vector * self.iris_matrix * iris_radius
            iris_vector = iris_vector + self.front_vector
                         
            iris_point = om.MPoint(iris_vector + self.surface_normal)
            hit = self.surface.intersect(iris_point, -self.surface_normal, u_ptr, v_ptr, iris_point)
            if not hit:
                iris_point = self.surface.closestPoint(om.MPoint(iris_vector))
                self.surface.getParamAtPoint(iris_point, u_ptr, v_ptr)
                
            self.iris_ring.append(om.MVector(iris_point))
            
            u, v = om.MScriptUtil.getDouble(u_ptr), om.MScriptUtil.getDouble(v_ptr)
            unwarped_iris_point = om.MPoint()
            self.default_surface.getPointAtParam(u, v, unwarped_iris_point)
            unwarped_iris_vector = om.MVector(unwarped_iris_point)
             
            angle = self.unwarped_front_vector.angle(unwarped_iris_vector)
            self.iris_angles.append(math.degrees(angle))
             
#             # get compensation angle
#             #
#             b = unwarped_iris_vector * aim_inverse
#             b = om.MVector(b.x, b.y, 0) - center
#             correction_u_angle = up_vector.angle(b)
#             if b.x < 0:
#                 correction_u_angle *= -1
#             
#             self.compensated_u_angles.append(math.degrees(correction_u_angle))
#             
#             correction_angle = math.degrees(a.angle(b))
#             if (a ^ b).z > 0.0:
#                 correction_angle *= -1
#             
#             self.offset_angles.append(correction_angle)
            
#             iris_plane_normal = (iris_vertex_vector - front_vector).normal()
#             iris_plane = (iris_plane_normal ^ surface_normal) ^ surface_normal
            
        #print self.offset_angles
            
        # calculate averaged iris center
        #
        iris_center = om.MVector(0,0,0)
        for iris_point in self.iris_ring:
            iris_center += iris_point
        self.iris_center = iris_center / len(self.iris_ring)
        
        self.eyeball_dirty = self.iris_dirty = True
        
        return True
    
    
    
    def computeEyeballProjection(self, plug, data):
        compute = self.computeSurface(plug, data)
        
        # only recompute if one of these vectors has changed
        #
        key = (self.front_vector, self.center_vector, self.back_vector, self.aim_matrix)        
        compute |= self.eyeball_key != key
        
        if not compute:
            return False
        
        self.eyeball_key = key
        
        # create new matrix for iris projection
        #
        c = self.unwarped_front_vector
        c.normalize()
        b = om.MVector(0,1,0) * self.aim_matrix
        a = b ^ c
        a.normalize()        
        b = c ^ a
        b.normalize()
         
        matrix_util = om.MScriptUtil()        
        self.projection_matrix = om.MMatrix()
        matrix_list = [a[0],a[1],a[2],0,b[0],b[1],b[2],0,c[0],c[1],c[2],0,0,0,0,1]
        matrix_util.createMatrixFromList(matrix_list, self.projection_matrix)
        
        return True
                    
            
            
    def computeIrisProjection(self, plug, data):
        data_handle = om.MDataHandle(data.inputValue(self.aimMatrix_attr))
        aim_matrix = om.MTransformationMatrix(data_handle.asMatrix()).asRotateMatrix()
        
        compute = aim_matrix != self.aim_matrix
        compute |= self.computeSurface(plug, data)
        
        # if nothing has changed do not compute
        #
        if not compute:
            return False
        print 'RECALCULATING IRIS PROJECTION'
        self.aim_matrix = aim_matrix
        
        # uv pointers
        #
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()
        
        # calculate projection points
        #        
        self.center_vector = warpPoint(om.MVector(0,0,0), self.weighting[-1], self.lattice_vectors)
        
        self.unwarped_front_vector = om.MVector(0, 0, 0.5) * aim_matrix       
        front_weighting = getWeighting(self.unwarped_front_vector)
        self.front_vector = warpPoint(self.unwarped_front_vector, front_weighting, self.lattice_vectors)
        
        self.unwarped_back_vector = om.MVector(0, 0, -0.5) * aim_matrix  
        back_weighting = getWeighting(self.unwarped_back_vector)
        self.back_vector = warpPoint(self.unwarped_back_vector, back_weighting, self.lattice_vectors)
        
        # warped front point doesn't always perfectly match surface
        # so get surface intersection of front vector for UV coordinates
        #
        projection_vector = self.front_vector - self.center_vector
        center_point = om.MPoint(self.center_vector)
        front_point = om.MPoint(self.front_vector)
        self.surface.intersect(center_point, projection_vector, u_ptr, v_ptr, front_point)
        u, v = om.MScriptUtil.getDouble(u_ptr), om.MScriptUtil.getDouble(v_ptr)
        
        # get surface normal
        #        
        self.surface_normal = self.surface.normal(u, v)
        
        # create new matrix for iris projection
        #
        c = self.surface_normal
        b = om.MVector(0,1,0) * aim_matrix
        a = b ^ c
        a.normalize()        
        b = c ^ a
        b.normalize()
         
        matrix_util = om.MScriptUtil()        
        self.iris_matrix = om.MMatrix()
        matrix_list = [a[0],a[1],a[2],0,b[0],b[1],b[2],0,c[0],c[1],c[2],0,0,0,0,1]
        matrix_util.createMatrixFromList(matrix_list, self.iris_matrix)
        
        return True
                       
                            
        
    def computeSurface(self, plug, data):
        data_handle = om.MDataHandle(data.inputValue(self.lattice_attr))
        lattice_data = om.MFnLatticeData(data_handle.data())
        lattice = oma.MFnLattice(lattice_data.lattice())
        
        lattice_points = [[[None, None],[None, None]],[[None, None],[None, None]]]
        for s in range(2):
            for t in range(2):
                for u in range(2):
                    lattice_points[s][t][u] = om.MVector(lattice.point(s, t, u))
                    
        if self.lattice_points == lattice_points:
            return False
        print 'RECALCUTING SURFACE'
        # store warped lattice vectors
        #
        self.lattice_vectors = []
        for s in range(2):
            for t in range(2):
                for u in range(2):
                    vector = lattice_points[s][t][u] - self.base_points[s][t][u]
                    self.lattice_vectors.append(vector if vector.length() else None)
        
        self.lattice_points = lattice_points
        
        # warp sphere surface by lattice
        #
        deformed_points = om.MPointArray()        
        for point_index in range(NurbsSphere.points.length()):
            point = NurbsSphere.points[point_index]
            weighting = self.weighting[point_index]
            deformed_points.append(warpPoint(point, weighting, self.lattice_vectors)) 
                
        self.surface, self.surface_data = NurbsSphere.create(deformed_points)
        
        return True
 
#--------------------------------------------------------------------------------------------------#

class Mesh(object):
    def __init__(self):
        self.vertices = om.MPointArray()
        self.faces = om.MIntArray()
        self.connections = om.MIntArray()
        self.world_matrix = om.MMatrix()
        
    
    def setWorldMatrix(self, matrix):
        self.world_matrix = om.MTransformationMatrix(matrix)
        
        
    def addVertex(self, point):
        if self.world_matrix:
            if isinstance(point, om.MPoint):
                point = om.MVector(point)
            point = point * self.world_matrix.asMatrix()
            point += self.world_matrix.getTranslation(om.MSpace.kWorld)
            
        if isinstance(point, om.MVector):
            point = om.MPoint(point)
        self.vertices.append(point)
        
        
    def addFace(self, vert_ids):
        self.faces.append(len(vert_ids))
        for vert_id in vert_ids:
            self.connections.append(vert_id)
            
    
    def create(self):
        mesh_data = om.MFnMeshData()
        mesh_data_obj = mesh_data.create()
        
#         verts = [self.vertices[index] for index in range(self.vertices.length())]
#         print 'V = {}'.format([(v.x, v.y, v.z) for v in verts])
#         print 'F = {}'.format([self.faces[index] for index in range(self.faces.length())])
#         print 'C = {}'.format([self.connections[index] for index in range(self.connections.length())])
        
        mesh = om.MFnMesh()        
        mesh.create(self.vertices.length(), 
                    self.faces.length(), 
                    self.vertices, 
                    self.faces, 
                    self.connections, 
                    mesh_data_obj)
        
        return mesh_data_obj
 
 #--------------------------------------------------------------------------------------------------#
 
def creator():
    return omMPx.asMPxPtr(CSEye())

#--------------------------------------------------------------------------------------------------#
 
def initialize():
    typed_attr = om.MFnTypedAttribute()
    matrix_attr = om.MFnMatrixAttribute()
    numeric_attr = om.MFnNumericAttribute()
    
    kInt = om.MFnNumericData.kInt
    kFloat = om.MFnNumericData.kFloat
    
    # INPUTS
    #
    lattice_attr = typed_attr.create('lattice', 'lattice', om.MFnData.kLattice)
    CSEye.lattice_attr = lattice_attr
    typed_attr.setWritable(True)
    typed_attr.setStorable(True)
    CSEye.addAttribute(lattice_attr)

    latticeMatrix_attr = matrix_attr.create('latticeMatrix', 'lMat', om.MFnMatrixAttribute.kDouble)
    CSEye.latticeMatrix_attr = latticeMatrix_attr
    matrix_attr.setWritable(True)
    matrix_attr.setStorable(True)
    CSEye.addAttribute(latticeMatrix_attr)
    
    aimMatrix_attr = matrix_attr.create('aimMatrix', 'aMat', om.MFnMatrixAttribute.kDouble)
    CSEye.aimMatrix_attr = aimMatrix_attr
    matrix_attr.setWritable(True)
    matrix_attr.setStorable(True)
    CSEye.addAttribute(aimMatrix_attr)
    
    attributes = (('uSpans', 'us', 8, 0, 20, kInt),
                  ('vSpans', 'vs', 8, 0, 20, kInt),
                  
                  ('irisSize', 'irs', 0.5, 0.0, 10.0, kFloat),
                  ('irisRotateX', 'irrx', 0.0, -360.0, 360.0, kFloat),
                  ('irisScaleX', 'irsx', 1.0, 0.0, 2.0, kFloat),
                  ('irisScaleY', 'irsy', 1.0, 0.0, 2.0, kFloat),
                  ('irisCurveAngle', 'irca', 30.0, 0.0, 90.0, kFloat),
                  ('irisDivisions', 'ird', 6, 1, 20, kInt),
                  
                  ('pupilSize', 'ps', 0.5, 0.0, 1.0, kFloat),
                  ('pupilTranslateX', 'ptx', 0.0, -1.0, 1.0, kFloat),
                  ('pupilTranslateY', 'pty', 0.0, -1.0, 1.0, kFloat),
                  ('pupilRotateX', 'prx', 0.0, -360.0, 360, kFloat),
                  ('pupilScaleX', 'psx', 1.0, 0.0, 2.0, kFloat),
                  ('pupilScaleY', 'psy', 1.0, 0.0, 2.0, kFloat),
                  ('pupilDepth', 'psd', 0.15, 0.0, 1.0, kFloat))

    for attribute_data in attributes:
        attr_name, short_name, default, min_value, max_value, attribute_type = attribute_data
        
        attr = numeric_attr.create(attr_name, short_name, attribute_type)
        setattr(CSEye, '{}_attr'.format(attr_name), attr)
        
        numeric_attr.setWritable(True)
        numeric_attr.setStorable(True)
        numeric_attr.setDefault(default)
        numeric_attr.setMin(min_value)
        numeric_attr.setMax(max_value)
        numeric_attr.setChannelBox(True)
        
        CSEye.addAttribute(attr)
    
    # OUTPUTS
    #
    mesh_attributes = {'eyeball' : ('lattice', 'latticeMatrix', 'aimMatrix', 'uSpans', 'vSpans', 
                                    'irisSize', 'irisRotateX', 'irisScaleX', 'irisScaleY'),
                       'iris' : ('lattice', 'latticeMatrix', 'aimMatrix', 'uSpans', 'irisSize',
                                 'irisRotateX', 'irisScaleX', 'irisScaleY', 'irisCurveAngle',
                                 'irisDivisions', 'pupilSize', 'pupilTranslateX', 
                                 'pupilTranslateY', 'pupilRotateX', 'pupilScaleX',
                                 'pupilScaleY', 'pupilDepth'),
                       'pupil' : ('lattice', 'latticeMatrix', 'aimMatrix', 'irisSize', 
                                  'irisRotateX', 'irisScaleX', 'irisScaleY', 'pupilSize',
                                  'pupilTranslateX', 'pupilTranslateY', 'pupilRotateX',
                                  'pupilScaleX', 'pupilScaleY', 'pupilDepth')}

    for mesh_name, input_attributes in mesh_attributes.items():
        mesh_attr = typed_attr.create(mesh_name, mesh_name, om.MFnMeshData.kMesh)
        setattr(CSEye, '{}_attr'.format(mesh_name), mesh_attr)
        
        typed_attr.setWritable(True)
        typed_attr.setStorable(True)
        
        CSEye.addAttribute(mesh_attr)
        
        for input_attribute in input_attributes:
            input_attribute = getattr(CSEye, '{}_attr'.format(input_attribute))
            CSEye.attributeAffects(input_attribute, mesh_attr)
    
    # create default lattice points
    #
    CSEye.base_points = [[[om.MVector(-0.5, -0.5, -0.5), om.MVector(-0.5, -0.5, 0.5)], 
                          [om.MVector(-0.5,  0.5, -0.5), om.MVector(-0.5,  0.5, 0.5)]], 
                         [[om.MVector( 0.5, -0.5, -0.5), om.MVector( 0.5, -0.5, 0.5)], 
                          [om.MVector( 0.5,  0.5, -0.5), om.MVector( 0.5,  0.5, 0.5)]]]
    
    # calculate and store lattice weighting
    #   
    CSEye.weighting = {}
    for cv_index, cv in enumerate(NurbsSphere.cvs):
        CSEye.weighting[cv_index] = getWeighting(cv)
    CSEye.weighting[-1] = getWeighting(om.MPoint(0,0,0))
    
    # create internal nurbs surface
    #
    CSEye.surface, CSEye.surface_data = NurbsSphere.create(NurbsSphere.points)
    CSEye.default_surface, CSEye.default_surface_data = NurbsSphere.create(NurbsSphere.points)
    

#--------------------------------------------------------------------------------------------------#  
 
def initializePlugin(obj):
    plugin = omMPx.MFnPlugin(obj, 'cinesite', '1.0', 'Any')
    try:
        plugin.registerNode('csEye', CSEye.plugin_node_id, creator, initialize)
    except RuntimeError:
        raise RuntimeError, 'Failed to register node'
 
 
 
def uninitializePlugin(obj):
    plugin = omMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(CSEye.plugin_node_id)
    except RuntimeError:
        raise RuntimeError, 'Failed to register node'
    
    
creator()