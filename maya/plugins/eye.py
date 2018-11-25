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