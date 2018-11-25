import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om
import math
   
 
class CSEye(omMPx.MPxNode):
    plugin_node_id = om.MTypeId(0x00000001)  # needs to be updated
     
    all_poses = [] 
 
    def compute(self, plug, data): 
        # get nurbs surface data
        #   
        data_handle = om.MDataHandle(data.inputValue(self.inputSurface))
        surface = data_handle.asNurbsSurface()
        
        if surface.isNull():
            return False
        
        surface = om.MFnNurbsSurface(data_handle.asNurbsSurface())
        
        # get world matrix data
        #
        data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
        world_matrix = om.MMatrix(data_handle.asMatrix())

        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()
        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()

        iris_width = data.inputValue(self.irisWidth).asFloat()
        u_spans = data.inputValue(self.uSpans).asInt()
        v_spans = data.inputValue(self.vSpans).asInt()
        
        center = om.MPoint(0,0,0)        
        
        num_spans = (u_spans-1)*v_spans
        
        connects = om.MIntArray((4*num_spans) + (v_spans * 3))
         
        counter = 0        
        for v_index in range(v_spans):            
            for u_index in range(u_spans):
                offset = u_index + (v_index * u_spans) + 1
                if u_index == u_spans - 1:
                    connects.set(offset, counter)
                    if v_index == v_spans - 1:
                        offset = u_index + 1
                    else:
                        offset = offset + u_spans
                    connects.set(offset, counter+1)
                    connects.set(0, counter+2)                    
                    counter += 3
                else:
                    connects.set(offset+1, counter)
                    connects.set(offset, counter+1)
                    if v_index == v_spans - 1:
                        offset = u_index + 1
                    else:
                        offset = offset + u_spans
                    connects.set(offset, counter+2)
                    connects.set(offset+1, counter+3)
                    counter += 4
            
        polygons = om.MIntArray(num_spans+v_spans) 
        counter = 0     
        for v_index in range(v_spans):
            for u_index in range(u_spans):
                if u_index == u_spans-1:
                    polygons.set(3, counter)
                else:
                    polygons.set(4, counter)
                counter += 1
         
        verts = om.MPointArray()
        verts.setLength(u_spans * v_spans + 1)
        
        front_vector = om.MVector(0.0, 0.0, 1.0) * world_matrix
        front_point = om.MPoint(0.0, 0.0, 0.0)
        surface.intersect(center, front_vector, u_ptr, v_ptr, front_point)
        u, v = om.MScriptUtil.getDouble(u_ptr), om.MScriptUtil.getDouble(v_ptr)
        surface_normal = surface.normal(u, v)
        invert_surface_normal = om.MVector(surface_normal[0] * -1, surface_normal[1] * -1, surface_normal[2] * -1)
        
        close_front_point = om.MPoint(front_point[0] + (invert_surface_normal[0] * 0.1),
                                      front_point[1] + (invert_surface_normal[1] * 0.1),
                                      front_point[2] + (invert_surface_normal[2] * 0.1))

        back_point = om.MPoint()
        surface.intersect(close_front_point, invert_surface_normal, u_ptr, v_ptr, back_point)
        verts.set(back_point, 0)        
                
        center = om.MPoint((front_point[0] + back_point[0]) / 2,
                           (front_point[1] + back_point[1]) / 2,
                           (front_point[2] + back_point[2]) / 2)
        
        v_angle_increment = 360 / v_spans
        
        c = surface_normal
        b = om.MVector(0, 1, 0) * world_matrix
        a = b ^ c
        a.normalize()       
        
        b = a ^ c
        b.normalize()
         
        matrix_util = om.MScriptUtil()
        
        new_matrix = om.MMatrix()
        matrix_list = [a[0],a[1],a[2],0,b[0],b[1],b[2],0,c[0],c[1],c[2],0,0,0,0,1]
        matrix_util.createMatrixFromList(matrix_list, new_matrix)
  
        iris_point = None
        counter = 0
        for v_index in range(v_spans):
            v_angle = v_angle_increment * v_index
            
            iris_angle = u_angle_increment = 0
            for u_index in range(u_spans):
                output = om.MPoint()
                
                if u_index == 0:
                    x = math.cos(math.radians(v_angle)) * iris_width
                    y = math.sin(math.radians(v_angle)) * iris_width
                    
                    iris_center = om.MVector(x,y,0) * new_matrix
                    
                    iris_center = om.MPoint(iris_center + om.MVector(center))
                    surface.intersect(iris_center, surface_normal, u_ptr, v_ptr, output)
                    
                    front_vector = om.MVector(output) - om.MVector(center)
                    iris_angle = math.degrees(surface_normal.angle(front_vector))
                    
                    u_angle_increment = (180.0 - iris_angle) / u_spans
                    
                    if v_index == 1:
                        iris_point = center
                        
                else:             
                    u_angle = (u_angle_increment * u_index) + iris_angle
                     
                    span = math.sin(math.radians(u_angle))
                      
                    x = math.cos(math.radians(v_angle)) * span
                    y = math.sin(math.radians(v_angle)) * span
                    z = math.cos(math.radians(u_angle))
                    ray_vector = om.MVector(x, y, z) * new_matrix

                    surface.intersect(center, ray_vector, u_ptr, v_ptr, output)
                          
                verts.set(output, counter+1)
                counter += 1

        mesh_data = om.MFnMeshData()
        mesh_data_obj = mesh_data.create()
        
        mesh = om.MFnMesh()
        
        mesh.create(verts.length(), polygons.length(), verts, polygons, connects, mesh_data_obj)
        
        data.outputValue(self.outputGeometry).setMObject(mesh_data_obj)
         
        data.setClean(plug)

#         data.outputValue(self.x).setFloat(iris_point[0])
#         data.outputValue(self.y).setFloat(iris_point[1])
#         data.outputValue(self.z).setFloat(iris_point[2])
 
        return True
 
 
def creator():
    return omMPx.asMPxPtr(CSEye())

 
def initialize():
    numeric_attr = om.MFnNumericAttribute()    
    typed_attr = om.MFnTypedAttribute()
    matrix_attr = om.MFnMatrixAttribute()

    setattr(CSEye, 'inputSurface', typed_attr.create('inputSurface', 'is', om.MFnNurbsSurfaceData.kNurbsSurface))
    typed_attr.setWritable(True)
    typed_attr.setStorable(True)
    
    surface_attr = getattr(CSEye, 'inputSurface')
    CSEye.addAttribute(surface_attr)    
    
    setattr(CSEye, 'worldMatrix', matrix_attr.create('worldMatrix', 'worldMatrix', om.MFnMatrixAttribute.kDouble))
    matrix_attr.setWritable(True)
    matrix_attr.setStorable(True)
    
    matrix_attr = getattr(CSEye, 'worldMatrix')
    CSEye.addAttribute(matrix_attr)
    
    setattr(CSEye, 'irisWidth', numeric_attr.create('irisWidth', 'irw', om.MFnNumericData.kFloat))
    numeric_attr.setWritable(True)
    numeric_attr.setStorable(True)
    numeric_attr.setDefault(0.5)
    numeric_attr.setMin(0.0)
    
    iris_attr = getattr(CSEye, 'irisWidth')
    CSEye.addAttribute(iris_attr) 
    
    setattr(CSEye, 'uSpans', numeric_attr.create('uSpans', 'us', om.MFnNumericData.kInt))
    numeric_attr.setWritable(True)
    numeric_attr.setStorable(True)
    numeric_attr.setDefault(8)
    numeric_attr.setMin(0)
    numeric_attr.setMax(20)
    
    u_attr = getattr(CSEye, 'uSpans')
    CSEye.addAttribute(u_attr) 
    
    setattr(CSEye, 'vSpans', numeric_attr.create('vSpans', 'vs', om.MFnNumericData.kInt))
    numeric_attr.setWritable(True)
    numeric_attr.setStorable(True)
    numeric_attr.setDefault(4)
    numeric_attr.setMin(0)
    numeric_attr.setMax(20)
    
    v_attr = getattr(CSEye, 'vSpans')
    CSEye.addAttribute(v_attr) 
 
    setattr(CSEye, 'outputGeometry', typed_attr.create('outputGeometry', 'outputGeometry', om.MFnMeshData.kMesh))
    typed_attr.setWritable(True)
    typed_attr.setStorable(True)
    
    mesh_attr = getattr(CSEye, 'outputGeometry')
    CSEye.addAttribute(mesh_attr)

    CSEye.attributeAffects(surface_attr, mesh_attr)
    CSEye.attributeAffects(matrix_attr, mesh_attr)
    CSEye.attributeAffects(iris_attr, mesh_attr)
    CSEye.attributeAffects(u_attr, mesh_attr)
    CSEye.attributeAffects(v_attr, mesh_attr)
    
    for axis in 'xyz':
        setattr(CSEye, axis, numeric_attr.create(axis, axis, om.MFnNumericData.kFloat))
        numeric_attr.setWritable(False)
        numeric_attr.setStorable(False)
        
        axis_attr = getattr(CSEye, axis)        
        CSEye.addAttribute(axis_attr) 
        
        CSEye.attributeAffects(surface_attr, axis_attr)
        CSEye.attributeAffects(matrix_attr, axis_attr)
        CSEye.attributeAffects(iris_attr, axis_attr)
        CSEye.attributeAffects(u_attr, axis_attr)
        CSEye.attributeAffects(v_attr, axis_attr)
    
 
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