import maya.OpenMayaMPx as omMPx
import maya.OpenMaya as om
import math
 
 
 
class CSEye(omMPx.MPxNode):
    plugin_node_id = om.MTypeId(0x00000001)  # needs to be updated
   
    
    def __init__(self, *args, **kwargs):
        omMPx.MPxNode.__init__(self, *args, **kwargs)
               
        self.surface_normal = om.MVector(0,0,0)
        self.world_matrix = om.MMatrix()     
        self.projection_matrix = None
        self.projection_vector = om.MVector(0,0,0)
        self.front_vector = om.MVector(0,0,0)
        
        self.eyeball_faces_key = None
        self.eyeball_faces = []
        
        self.iris_points = []
        
        self.iris_ring = []
        self.iris_vector_key = None
        self.iris_vectors = []
        self.iris_rotated_vectors = []
        self.iris_center = None
        self.iris_rotation = 0        
        self.iris_vertices_key = None
        self.iris_vertices = []
        self.iris_faces_key = None
        self.iris_faces = []
        self.iris_rotation_vectors = (om.MVector(1, 0, 0), om.MVector(0, 1, 0))
        self.iris_curve_angle = None
        self.iris_divisions = None
        self.iris_division_vectors = None
                
        self.pupil_rotation = 0        
        self.pupil_rotation_vectors = (om.MVector(1, 0, 0), om.MVector(0, 1, 0))        
        self.pupil_offset = (om.MVector(0, 0, 0), om.MVector(0, 0, 0))
        self.pupil_center = om.MVector(0, 0, 0)        
        self.pupil_vertices_key = None
        self.pupil_vertices = [om.MVector(*vertex) for vertex in PupilMesh.vertices]
        
        self.surface_points = []
        
        self.u_spans = 0
        self.u_angles = []
    
    
    
    def calculateCurve(self, in_angle, out_angle, divisions):   
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
    
    #------------------------------------------------------------------------------------------#
 
    def compute(self, plug, data):
        plug_name = plug.partialName()
        
        if plug_name == 'eyeball':
            data_handle = om.MDataHandle(data.inputValue(self.inputSurface))
            if data_handle.asNurbsSurface().isNull():
                return self.computeEyeballNoProjection(data)
            else:
                return self.computeEyeball(data)
        
        elif plug_name == 'iris':
            return self.computeIris(data)
         
        elif plug_name == 'pupil':
            return self.computerPupil(data)
        
        elif plug_name == 'irisMatrix':
            return self.computeIrisMatrix(data)

                
        
        
    def computerPupil(self, data):
        self.getPupilVertices(data)
        
        iris_size = data.inputValue(self.irisSize).asFloat()
        
        # get projection matrix
        #
        surface = om.MDataHandle(data.inputValue(self.inputSurface)).asNurbsSurface()
        if surface.isNull():
            data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
            projection_matrix = om.MMatrix(data_handle.asMatrix())
            
            eye_scale = data.inputValue(self.eyeScale).asFloat()
            
            if iris_size >= eye_scale:
                iris_size = eye_scale
        else:            
            projection_matrix = self.projection_matrix
                
        # calculate center of pupil geometry - slight negative offset from iris center
        #
        pupil_center = self.pupil_center - (self.surface_normal * 0.01 * iris_size)

        # create topology
        #
        pupil = Mesh()
        for pupil_vector in self.pupil_vertices:
            pupil.addVertex(om.MPoint((pupil_vector * projection_matrix) + pupil_center))
        
        # store pupil topology data
        #
        counter = 0
        for face in PupilMesh.faces:
            vertex_ids = PupilMesh.connections[counter:counter+face]
            counter += face
            pupil.addFace(vertex_ids)
        
        # set mesh data to output
        #
        data.outputValue(self.pupil).setMObject(pupil.getData())
        
        return True
        
    
    
    def getPupilVertices(self, data):
        # get settings
        #
        iris_size = data.inputValue(self.irisSize).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY).asFloat()
        
        pupil_size = data.inputValue(self.pupilSize).asFloat()
        pupil_scale_x = data.inputValue(self.pupilScaleX).asFloat()
        pupil_scale_y = data.inputValue(self.pupilScaleY).asFloat()
        pupil_depth = data.inputValue(self.pupilDepth).asFloat()
        pupil_depth *= iris_size
        
        pupil_translate_x = data.inputValue(self.pupilTranslateX).asFloat()
        pupil_translate_y = data.inputValue(self.pupilTranslateY).asFloat()
        
        # compare current settings to last time pupil was computed
        #
        pupil_vertices_key = [iris_size, pupil_size,
                   iris_scale_x, iris_scale_y,
                   pupil_scale_x, pupil_scale_y,
                   pupil_translate_x, pupil_translate_y]
        
        compute = pupil_vertices_key != self.pupil_vertices_key
        compute |= self.computeIrisRotation(data)
        compute |= self.computePupilRotation(data)
        
        # if settings haven't changed return precalculated vertices
        #
        if not compute:
            return False

        # recalculated pupil vertex positions
        #
        pupil_rotation_vectors = self.pupil_rotation_vectors
        iris_rotation_vectors = self.iris_rotation_vectors
        
        vertices = []
        for vertex in PupilMesh.vertices:
            pupil_vector = om.MVector(*vertex) * iris_size * pupil_size 
 
            pupil_vector_x_length = (pupil_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = pupil_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (pupil_rotation_vectors[1] * pupil_vector)
            pupil_vector_dot_y = pupil_rotation_vectors[1] * pupil_vector_y_length
               
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - pupil_scale_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - pupil_scale_y))
            
            pupil_vector_x_length = (iris_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = iris_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (iris_rotation_vectors[1] * pupil_vector)
            pupil_vector_dot_y = iris_rotation_vectors[1] * pupil_vector_y_length
      
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - iris_scale_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - iris_scale_y))
            
            pupil_vector = self.pupil_offset[0] + self.pupil_offset[1] + pupil_vector

            vertices.append(pupil_vector)
        
        self.pupil_vertices = vertices
        self.pupil_vertices_key = pupil_vertices_key
        
        return True
                    
                    
    
    def computeIris(self, data):
        self.computeIrisRing(data)
        self.computeIrisFaces(data)
        self.computeIrisVertices(data)
            
        # get input attributes
        #
        iris_size = data.inputValue(self.irisSize).asFloat()        
        pupil_depth = data.inputValue(self.pupilDepth).asFloat() * iris_size 

        # recreate projection matrix
        #
        surface = om.MDataHandle(data.inputValue(self.inputSurface)).asNurbsSurface()
        if surface.isNull():
            data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
            projection_matrix = om.MMatrix(data_handle.asMatrix())
            
            eye_scale = data.inputValue(self.eyeScale).asFloat()
            
            if iris_size >=eye_scale:
                iris_size=eye_scale
        else:            
            projection_matrix = self.projection_matrix

        pupil_center = self.iris_center - (self.surface_normal * pupil_depth)
        self.pupil_center = pupil_center

        # get iris divisions based on curvature
        #
        division_vectors = self.getIrisCurve(data)
        u_spans = len(division_vectors) + 3 
        
        # create mesh vertices
        #
        iris = Mesh()
        for iris_point, pupil_vector in zip(self.iris_ring, self.iris_vertices):
            pupil_point = pupil_center + pupil_vector * projection_matrix

            iris_pupil_vector = iris_point - pupil_point
            pupil_vector = (iris_pupil_vector * 0.95)
            
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
                    output = om.MPoint(pupil_point - (self.surface_normal * ((3-u_index) * 0.015) * iris_size))
                    if u_index < 2:
                        output += z_axis * ((2 - u_index) * 0.1)
                
                # u_index 3 is the edge of the pupil
                #
                elif u_index == 3:
                    output = om.MPoint(pupil_point)                    

                # the last u_index is the edge of the iris
                #
                elif u_index == u_spans - 1:
                    output = om.MPoint(iris_point)
                
                # all other u_indices and curved divisions between the pupil and the iris
                #
                else:
                    division_vector = division_vectors[u_index-2]
                    division_vector = z_axis * division_vector[0] + x_axis * division_vector[2]
                    division_point = om.MPoint(pupil_point + division_vector)
                    output = om.MPoint(division_point)
                    
                iris.addVertex(output)
        
        for face in self.iris_faces:
            iris.addFace(face)

        # set iris mesh data to output
        #
        data.outputValue(self.iris).setMObject(iris.getData())
        
    
    
    def computeIrisFaces(self, data):
        u_spans = len(self.getIrisCurve(data)) + 3
        v_spans = data.inputValue(self.vSpans).asInt()        
        
        new_key = (u_spans, v_spans)         

        if new_key == self.iris_faces_key:
            return False
        
        faces = []
        for v_index in range(v_spans):
            for u_index in range(u_spans-1):
                offset = u_index + (v_index * u_spans)
                if v_index == v_spans - 1:
                    end_offset = u_index
                else:
                    end_offset = offset + u_spans
                faces.append([offset, offset+1, end_offset+1, end_offset])
                
        self.iris_faces_key = new_key
        self.iris_faces = faces
        
        return True


    def getIrisCurve(self, data):
        iris_curve_angle = data.inputValue(self.irisCurveAngle).asFloat()
        iris_divisions = data.inputValue(self.irisDivisions).asInt() + 1
        
        if (iris_curve_angle, iris_divisions) == (self.iris_curve_angle, self.iris_divisions):
            return self.iris_division_vectors

        self.iris_division_vectors = self.calculateCurve(iris_curve_angle, 
                                                         iris_curve_angle-90, 
                                                         iris_divisions)
        self.iris_curve_angle, self.iris_divisions = iris_curve_angle, iris_divisions
        
        return self.iris_division_vectors
    
    
    
    def computeIrisVertices(self, data):
        self.computeIrisRotation(data)
        self.computePupilRotation(data)
        
        # get settings
        #
        iris_size = data.inputValue(self.irisSize).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY).asFloat()
         
        iris_curve_angle = data.inputValue(self.irisCurveAngle).asFloat()
        iris_divisions = data.inputValue(self.irisDivisions).asInt() + 1
 
        pupil_size = data.inputValue(self.pupilSize).asFloat()
        pupil_scale_x = data.inputValue(self.pupilScaleX).asFloat()
        pupil_scale_y = data.inputValue(self.pupilScaleY).asFloat()
         
        pupil_depth = data.inputValue(self.pupilDepth).asFloat()
         
        pupil_translate_x = data.inputValue(self.pupilTranslateX).asFloat()
        pupil_translate_y = data.inputValue(self.pupilTranslateY).asFloat()
        
        iris_rotation = data.inputValue(self.irisRotation).asFloat()
        pupil_rotation = data.inputValue(self.pupilRotation).asFloat()
        
        v_spans = data.inputValue(self.vSpans).asInt()
         
        new_key = (v_spans, iris_size, iris_scale_x, iris_scale_y, 
                   iris_curve_angle, iris_divisions, iris_rotation,  
                   pupil_size, pupil_scale_x, pupil_scale_y, 
                   pupil_depth, pupil_translate_x, pupil_translate_y,
                   pupil_rotation)
        
        compute = self.iris_vertices_key != new_key
        
        if not compute:
            return False
        
        pupil_rotation_vectors = self.pupil_rotation_vectors
        iris_rotation_vectors = self.iris_rotation_vectors 
        
        pupil_size_x = pupil_size * pupil_scale_x
        pupil_size_y = pupil_size * pupil_scale_y
        
        # calculate translation
        #
        scaled_iris_sizeX = iris_size * iris_scale_x
        scaled_iris_sizeY = iris_size * iris_scale_y
        
        pupil_translate_x *= scaled_iris_sizeX * 0.5
        pupil_translate_y *= scaled_iris_sizeY * 0.5
        
        pupil_offset_x = iris_rotation_vectors[0] * pupil_translate_x
        pupil_offset_y = iris_rotation_vectors[1] * pupil_translate_y
        self.pupil_offset = (pupil_offset_x, pupil_offset_y)
        
        vertices = []
        for iris_vector in self.iris_vectors:
            pupil_vector = om.MVector(iris_vector[0], iris_vector[1], 0.0)

            # rotate by iris rotation
            #
            pupil_vector_x_length = (pupil_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = pupil_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (pupil_rotation_vectors[1] * pupil_vector) 
            pupil_vector_dot_y = pupil_rotation_vectors[1] * pupil_vector_y_length
             
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - pupil_size_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - pupil_size_y))
            
            # rotate by pupil rotation
            #
            pupil_vector_x_length = (iris_rotation_vectors[0] * pupil_vector)
            pupil_vector_dot_x = iris_rotation_vectors[0] * pupil_vector_x_length
            pupil_vector_y_length = (iris_rotation_vectors[1] * pupil_vector)
            pupil_vector_dot_y = iris_rotation_vectors[1] * pupil_vector_y_length
 
            pupil_vector = pupil_vector - (pupil_vector_dot_x * (1 - iris_scale_x))
            pupil_vector = pupil_vector - (pupil_vector_dot_y * (1 - iris_scale_y))
            
            pupil_vector += pupil_offset_x + pupil_offset_y

            vertices.append(pupil_vector)
        
        self.iris_vertices = vertices
        self.iris_vertices_key = new_key
        
        return True
        


    def computeEyeballNoProjection(self, data):
        # get world matrix data
        #
        data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
        world_matrix = om.MMatrix(data_handle.asMatrix())
        translation = world_matrix[3]

        matrix_util = om.MScriptUtil()
        for index in range(3):
            matrix_util.setDoubleArray(translation, index, 0.0)

        # get settings
        #
        iris_size = data.inputValue(self.irisSize).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY).asFloat()
        eye_scale = data.inputValue(self.eyeScale).asFloat()

        iris_rotation = data.inputValue(self.irisRotation).asFloat()

        self.iris_y_rotation_vector = iris_y_rotation_vector = om.MVector(math.sin(math.radians(iris_rotation)),
                                          math.sin(math.radians(iris_rotation + 90)),0)
        self.iris_x_rotation_vector = iris_x_rotation_vector = om.MVector(math.cos(math.radians(iris_rotation)),
                                            math.cos(math.radians(iris_rotation + 90)), 0)

        u_spans = data.inputValue(self.uSpans).asInt()
        v_spans = data.inputValue(self.vSpans).asInt()

        eyeball = Mesh()
        self.iris_ring = []
        self.iris_vectors = []

        self.surface_normal = om.MVector(0,0,1) * world_matrix
        if iris_size > eye_scale:
            iris_size = eye_scale

        eyeball.addVertex(om.MPoint(om.MVector(0,0,-eye_scale)*world_matrix))

        u_angles = [a[0] for a in self.calculateCurve(80, 0, u_spans - 2)]

        for v in range(v_spans):
            vstep = (360.0 / v_spans) * v

            iris_x = math.cos(math.radians(vstep)) * iris_size
            iris_y = math.sin(math.radians(vstep)) * iris_size
            iris_vector_xy = (om.MVector(iris_x,iris_y,0))
            iris_circle_vector_dot_x = iris_x_rotation_vector * (iris_x_rotation_vector * iris_vector_xy)
            iris_circle_vector_dot_y = iris_y_rotation_vector * (iris_y_rotation_vector * iris_vector_xy)

            iris_vector_xy = iris_vector_xy - (iris_circle_vector_dot_x * (1 - iris_scale_x))
            iris_vector_xy = iris_vector_xy - (iris_circle_vector_dot_y * (1 - iris_scale_y))

            vector_length = iris_vector_xy.length()

            if vector_length > eye_scale:
                iris_vector_xy.normalize()
                iris_vector_xy = iris_vector_xy * eye_scale
                vector_length = round (iris_vector_xy.length(), 8)

            normalized_length = vector_length/eye_scale

            angle = math.degrees(math.asin(normalized_length))

            iris_z = math.sqrt(math.pow(eye_scale, 2) - math.pow(vector_length, 2))

            for u in range(1, u_spans + 1):
                if u == 1:
                    iris_vector=om.MVector(iris_vector_xy.x, iris_vector_xy.y, iris_z)

                    # adding the bevel
                    #
                    scaledVector = iris_vector - ( iris_vector_xy * 0.02) - (om.MVector(0,0,0.01) * iris_size)
                    eyeball.addVertex(om.MPoint(scaledVector)*world_matrix)
                    self.iris_ring.append(scaledVector*world_matrix)

                    self.iris_vectors.append(om.MVector(iris_x, iris_y, 0))

                    # adding the border
                    #
                    eyeball.addVertex(om.MPoint(iris_vector*world_matrix))

                else:
                    ustep =  (u_angles[u - 1] * (180.0 - angle)) + angle
                    z = math.cos(math.radians(ustep)) * eye_scale
                    radStep = math.sin(math.radians(ustep))

                    x = math.cos(math.radians(vstep)) * radStep * eye_scale
                    y = math.sin(math.radians(vstep)) * radStep * eye_scale

                    eyeball.addVertex(om.MPoint(om.MVector(x,y,z)*world_matrix))

        # store averaged iris center for creating the iris/pupil
        #
        iris_center = om.MVector(0,0,0)
        for iris_point in self.iris_ring:
            iris_center += iris_point
        self.iris_center = iris_center / len(self.iris_ring)

        vstep = 1
        u_spans += 1
        for v in range(v_spans):
            for u in range(u_spans):
                if v == v_spans - 1:
                    nextOffset = 1
                    offset = vstep  # 10
                else:
                    nextOffset = vstep + u_spans
                    offset = vstep


                if u == u_spans - 1:
                    eyeball.addFace([u + nextOffset, u + offset, 0])
                else:
                    eyeball.addFace([u + offset, u + offset + 1, 
                                     u + nextOffset + 1, u + nextOffset])
            vstep += u_spans

        data.outputValue(self.eyeball).setMObject(eyeball.getData())

        return True
    
    
    def computeProjection(self, data):
        # get nurbs surface data
        #   
        data_handle = om.MDataHandle(data.inputValue(self.inputSurface))
        surface = om.MFnNurbsSurface(data_handle.asNurbsSurface())

        # check if surface has changed
        #
        surface_points = om.MPointArray()
        surface.getCVs(surface_points)
        
        compute = True
        if self.surface_points:
            compute = False
            for index in range(surface_points.length()):
                compute = surface_points[index] != self.surface_points[index]
                if compute:
                    self.surface_points = surface_points
                    break
        else:
            self.surface_points = surface_points        
        
        # get world matrix
        #
        data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
        world_matrix = om.MMatrix(data_handle.asMatrix())
        
        data_handle = om.MDataHandle(data.inputValue(self.parentInverseMatrix))
        parent_inverse_matrix = om.MMatrix(data_handle.asMatrix())
        
        world_matrix = world_matrix * parent_inverse_matrix
        compute |= world_matrix != self.world_matrix

        # projection doesn't need to be recalculated
        #
        if not compute:
            return False
            
        # api pointers for u and v values
        #
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()
        
        center = om.MPoint(0, 0, 0) * world_matrix

        # project z axis onto surface
        # 
        front_vector = om.MVector(0.0, 0.0, 1.0) * world_matrix
        front_point = om.MPoint()        
        surface.intersect(center, front_vector, u_ptr, v_ptr, front_point)
        front_vector = om.MVector(front_point)
        self.front_vector = front_vector
        
        # get surface normal at intersection point
        #
        u, v = om.MScriptUtil.getDouble(u_ptr), om.MScriptUtil.getDouble(v_ptr)
        surface_normal = surface.normal(u, v)
        
        # can't project from front point, or it will find front again, so subtract a small vector
        # to place the start point inside the surface
        #
        close_front_point = om.MPoint(front_vector - (surface_normal * 0.1))

        # get back intersection point and store as vertex 0
        #
        back_point = om.MPoint()
        surface.intersect(close_front_point, (surface_normal*-1.0), u_ptr, v_ptr, back_point) 
        self.back_point = back_point  
        
        # get new center point
        #
        projection_center = om.MPoint((front_vector[0] + back_point[0]) / 2,
                                      (front_vector[1] + back_point[1]) / 2,
                                      (front_vector[2] + back_point[2]) / 2)
        self.projection_vector = om.MVector(projection_center)
        
        # calculate cross products
        #
        c = surface_normal
        b = om.MVector(0, 1, 0) * world_matrix
        a = b ^ c
        a.normalize()       

        b = c ^ a
        b.normalize()
        
        # create projection matrix object in memory
        #
        projection_matrix_util = om.MScriptUtil()
        projection_matrix = om.MMatrix()
        matrix_list = [a[0],a[1],a[2],0,b[0],b[1],b[2],0,c[0],c[1],c[2],0,0,0,0,1]
        projection_matrix_util.createMatrixFromList(matrix_list, projection_matrix)
        
        self.projection_matrix = projection_matrix
        self.surface_normal = surface_normal
        self.world_matrix = world_matrix
                
        return True 
        
        
    def computeIrisRing(self, data):
        compute = self.computeProjection(data)
        compute |= self.computeIrisVectors(data)
        
        if not compute:
            return False
        
        # get nurbs surface data
        #   
        data_handle = om.MDataHandle(data.inputValue(self.inputSurface))
        surface = om.MFnNurbsSurface(data_handle.asNurbsSurface())

        # get settings
        #
        iris_size = data.inputValue(self.irisSize).asFloat()
        
        self.iris_ring = []
    
        # api pointers for u and v values
        #
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()

        world_matrix = self.world_matrix
        surface_normal = self.surface_normal
        front_vector = self.front_vector
        projection_matrix = self.projection_matrix
        projection_vector = self.projection_vector
        
        center = om.MPoint(0,0,0) * world_matrix
        
        # get actual back point
        #
        back_point = om.MPoint()
        back_vector = om.MVector(0.0, 0.0, -1.0) * world_matrix
        surface.intersect(center, back_vector, u_ptr, v_ptr, back_point)
        self.back_point = back_point
         
        mid_center = om.MPoint((front_vector[0] + back_point[0]) / 2,
                               (front_vector[1] + back_point[1]) / 2,
                               (front_vector[2] + back_point[2]) / 2)
        mid_vector = om.MVector(mid_center)
        self.mid_point = mid_center
         
        rotation_vector = front_vector - mid_vector
                
        # bevel offsets
        #
        bevel_width = 0.02 * iris_size
        bevel_depth = 0.005 * iris_size
        
        self.offset_angles = []
        self.iris_angles = []
        self.iris_points = []
        
        rotation_matrix = om.MMatrix(world_matrix)
        translation = rotation_matrix[3]
        matrix_util = om.MScriptUtil()
        for index in range(3):
            matrix_util.setDoubleArray(translation, index, 0.0)
            
        ignore_iris_verts = set([])
        
        for _, iris_vector, reverse_matrix in self.iris_rotated_vectors:
            # store iris vector for iris/pupil creation
            #
            iris_vector = iris_vector * projection_matrix

            # translate iris edge by new center
            #
            iris_edge_projection = om.MPoint(iris_vector + projection_vector)
            
            # project iris edge onto surface along surface normal
            #
            ignore = False
            iris_vertex = om.MPoint()
            surface.intersect(iris_edge_projection, surface_normal, u_ptr, v_ptr, iris_vertex)
            if iris_vertex[0] == 0.0:
                iris_vertex = surface.closestPoint(iris_edge_projection)
                ignore = True
            self.iris_points.append(iris_vertex)
                               
            iris_vertex_vector = om.MVector(iris_vertex)            
            
            # subtract center from intersection point to get iris angle
            #  
            iris_edge_vector = iris_vertex_vector - mid_vector
            
            # get angle between surface normal and iris vector
            #                    
            iris_angle = math.degrees(rotation_vector.angle(iris_edge_vector))
            self.iris_angles.append(iris_angle)
            
            # calculate compensation for iris angle distortion
            #
            vector = (iris_vertex - front_vector) * rotation_matrix.inverse()
            vector = om.MVector(vector[0], vector[1], 0)
            vector = vector * reverse_matrix
            
            offset_angle = math.degrees(om.MVector(vector).angle(om.MVector(1,0,0)))
            if vector[1] < 0:
                offset_angle *= -1
            self.offset_angles.append(offset_angle)
                        
            # create beveled edge inside iris line
            #
            iris_plane_normal =(iris_vertex_vector - front_vector).normal()
            iris_plane = (iris_plane_normal ^ surface_normal) ^ surface_normal

            bevel_vector = iris_vertex_vector + (iris_plane * bevel_width) - (surface_normal * bevel_depth)              
            self.iris_ring.append(bevel_vector)
            if ignore:
                ignore_iris_verts.add(bevel_vector)
        
        # store averaged iris center for creating the iris/pupil
        #
        iris_center = om.MVector(0,0,0)
        for iris_point in self.iris_ring:
            if iris_point in ignore_iris_verts:
                continue
            iris_center += iris_point
            
        self.iris_center = iris_center / (len(self.iris_ring) - len(ignore_iris_verts))
        
#         depth = 9999999999
#         for iris_point in self.iris_ring:
#             iris_vector = iris_point - self.iris_center
#             iris_depth = surface_normal * iris_vector
#             if iris_depth < depth:
#                 depth = iris_depth
#                 
#         self.iris_center += surface_normal * depth
        
        return True
    


    def computeEyeball(self, data):
        self.computeIrisRing(data)
        self.computeEyeballFaces(data)
        self.computeUAngles(data) 

        # get nurbs surface data
        #   
        data_handle = om.MDataHandle(data.inputValue(self.inputSurface))
        surface = om.MFnNurbsSurface(data_handle.asNurbsSurface())
                  
        eyeball = Mesh()
        eyeball.addVertex(self.back_point)

        # api pointers for u and v values
        #
        u_util = om.MScriptUtil()
        u_ptr = u_util.asDoublePtr()        
        v_util = om.MScriptUtil()
        v_ptr = v_util.asDoublePtr()
         
        u_angles = self.u_angles
        u_spans = len(u_angles)

        v_spans = data.inputValue(self.vSpans).asInt()
        world_matrix = self.world_matrix

        # calculate vertices
        #
        for v_index in range(v_spans):
            v_angle, _, _ = self.iris_rotated_vectors[v_index]
            offset_angle = self.offset_angles[v_index]
            iris_angle = self.iris_angles[v_index]
            iris_vertex = self.iris_points[v_index]
            
            bevel_vertex = om.MPoint(self.iris_ring[v_index])
            eyeball.addVertex(bevel_vertex)
            eye_angle = 180.0 - iris_angle

            # added eyeball vertices in the right order
            #
            for u_index in range(1, u_spans):                
                if u_index == 1: # iris edge
                    vertex = iris_vertex                    
                      
                else: # eyeball spans
                    vertex = om.MPoint()
                    
                    compensated_v_angle = math.radians(v_angle + (offset_angle / (2 * u_index)))
                        
                    # calculate angle for current span
                    #
                    u_angle = (u_angles[u_index] * eye_angle) + iris_angle       
                    scale = math.sin(math.radians(u_angle))
                    
                    # calculate projection vector as combination of u and v angles
                    # 
                    x = math.cos(compensated_v_angle) * scale
                    y = math.sin(compensated_v_angle) * scale
                    z = math.cos(math.radians(u_angle))
                    ray_vector = om.MVector(x, y, z) * world_matrix

                    # project new vector onto surface to get intersection
                    #
                    surface.intersect(self.mid_point, ray_vector, u_ptr, v_ptr, vertex)
                
                # store vertex position
                #
                eyeball.addVertex(vertex)
        
        # add faces
        #
        for face in self.eyeball_faces:
            eyeball.addFace(face)
        
        # set data block to eyeball attribute
        #
        data.outputValue(self.eyeball).setMObject(eyeball.getData())
        
        return True
    
    
    
    def computeIrisMatrix(self, data):
        self.computeIrisRing(data)
        
        data_handle = om.MDataHandle(data.inputValue(self.worldMatrix))
        world_matrix = om.MMatrix(data_handle.asMatrix())
        translation = world_matrix[3]
        
        projection_matrix = self.projection_matrix
        front_vector = self.front_vector

        proj_translation = projection_matrix[3]
        matrix_util = om.MScriptUtil()
        for index in range(3):
            offset = matrix_util.getDoubleArrayItem(translation, index)
            matrix_util.setDoubleArray(proj_translation, index, front_vector[index] + offset)  
        
        iris_matrix = data.outputValue(self.irisMatrix)
        iris_matrix.setMMatrix(projection_matrix)
        
        return True



    def computeIrisVectors(self, data):
        v_spans = data.inputValue(self.vSpans).asInt()
        iris_size = data.inputValue(self.irisSize).asFloat()
        iris_scale_x = data.inputValue(self.irisScaleX).asFloat()
        iris_scale_y = data.inputValue(self.irisScaleY).asFloat()
        
        iris_vector_key = (v_spans, iris_size, iris_scale_x, iris_scale_y)
        
        compute = iris_vector_key != self.iris_vector_key
        compute ^= self.computeIrisRotation(data)
        
        if not compute:
            return False
        
        matrix_util = om.MScriptUtil()  
        
        iris_rotation_vectors = self.iris_rotation_vectors
        
        v_angle_increment = 360.0 / v_spans
        
        vectors = []
        rotated_vectors = []
        for v_index in range(v_spans):
            v_angle = v_angle_increment * v_index
            v_radians = math.radians(v_angle)
            
            # get x, y values for iris edge point based on v_angle and iris width
            #
            x = math.cos(v_radians) * iris_size
            y = math.sin(v_radians) * iris_size

            iris_vector = om.MVector(x, y, 0)
            vectors.append(iris_vector)
            
            # project iris_vector onto rotation vector
            #
            iris_vector_x_length = (iris_rotation_vectors[0] * iris_vector)
            iris_vector_dot_x = iris_rotation_vectors[0] * iris_vector_x_length
            iris_vector_y_length = (iris_rotation_vectors[1] * iris_vector)
            iris_vector_dot_y = iris_rotation_vectors[1] * iris_vector_y_length

            iris_vector = iris_vector - (iris_vector_dot_x * (1 - iris_scale_x))
            iris_vector = iris_vector - (iris_vector_dot_y * (1 - iris_scale_y))
            
            # create reverse matrix
            #
            reverse_matrix = om.MMatrix()
            matrix_list = [math.cos(v_radians), -math.sin(v_radians), 0, 0,
                           math.sin(v_radians),  math.cos(v_radians), 0, 0,
                                             0,                    0, 1, 0,
                                             0,                    0, 0, 1]            
            matrix_util.createMatrixFromList(matrix_list, reverse_matrix)
    
            rotated_vectors.append((v_angle, iris_vector, reverse_matrix))
        
        self.iris_vectors = vectors
        self.iris_rotated_vectors = rotated_vectors
        self.iris_vector_key = iris_vector_key
        
        return True
    
        
    
    def computeEyeballFaces(self, data):
        u_spans = data.inputValue(self.uSpans).asInt() + 1
        v_spans = data.inputValue(self.vSpans).asInt()        
        
        eyeball_faces_key = (u_spans, v_spans)
        
        if eyeball_faces_key == self.eyeball_faces_key:
            return False
        
        faces = []
        for v_index in range(v_spans):
            num_spans = u_spans      
            for u_index in range(num_spans):
                offset = u_index + (v_index * num_spans) + 1
                
                # if u spans is at the end, create triangle with back vertex 0
                #
                if u_index == num_spans - 1:
                    if v_index == v_spans - 1:
                        end_offset = u_index + 1
                    else:
                        end_offset = offset + num_spans
                    faces.append([offset, 0, end_offset])
                
                # create quad with next row
                #
                else:
                    if v_index == v_spans - 1:
                        end_offset = u_index + 1
                    else:
                        end_offset = offset + num_spans
                    faces.append([offset, offset+1, end_offset+1, end_offset])
        
        self.eyeball_faces = faces
        self.eyeball_faces_key = eyeball_faces_key
        
        return True 
    
        
    
    def computeUAngles(self, data):
        u_spans = data.inputValue(self.uSpans).asInt()
        if u_spans == self.u_spans:
            return False
        
        self.u_angles = [a[0] for a in self.calculateCurve(80, 0, u_spans-2)]
        self.u_spans = u_spans
        
        return self.u_angles 
    
    
    
    def computeIrisRotation(self, data):
        iris_rotation = data.inputValue(self.irisRotation).asFloat()
        
        if iris_rotation == self.iris_rotation:
            return False 
        
        x_radians = math.radians(iris_rotation)
        y_radians = math.radians(iris_rotation + 90)
        x_rotation_vector = om.MVector(math.cos(x_radians), math.cos(y_radians), 0)
        y_rotation_vector = om.MVector(math.sin(x_radians), math.sin(y_radians), 0)
        
        # force recalculate of pupil rotation so they don't get out of sync
        #
        self.computePupilRotation(data)
        
        # store data
        #
        self.iris_rotation = iris_rotation        
        self.iris_rotation_vectors = (x_rotation_vector, y_rotation_vector)
        
        return True
    
    
    
    def computePupilRotation(self, data):
        iris_rotation = data.inputValue(self.irisRotation).asFloat()
        pupil_rotation = data.inputValue(self.pupilRotation).asFloat()
        
        if iris_rotation == self.iris_rotation and pupil_rotation == self.pupil_rotation:
            return False
        
        pupil_rotation += iris_rotation
        
        x_radians = math.radians(pupil_rotation)
        y_radians = math.radians(pupil_rotation + 90)
        x_rotation_vector = om.MVector(math.cos(x_radians), math.cos(y_radians), 0)
        y_rotation_vector = om.MVector(math.sin(x_radians), math.sin(y_radians),0)
        
        # store data
        #
        self.pupil_rotation = pupil_rotation
        self.pupil_rotation_vectors = (x_rotation_vector, y_rotation_vector)
        
        return True



class Mesh(object):
    def __init__(self):
        self.polygons = om.MIntArray()
        self.connections = om.MIntArray()
        self.vertices = om.MPointArray()
        
        
    def addVertex(self, point):
        self.vertices.append(point)
        return self.vertices.length() - 1
    

    def addFace(self, vertex_ids):
        self.polygons.append(len(vertex_ids))
        for vertex_id in vertex_ids:
            self.connections.append(vertex_id)
    
    
    def getData(self):
        mesh_data = om.MFnMeshData()
        mesh_data_obj = mesh_data.create()

        mesh = om.MFnMesh()
        mesh.create(self.vertices.length(), 
                    self.polygons.length(), 
                    self.vertices, 
                    self.polygons, 
                    self.connections, 
                    mesh_data_obj)
        
        return mesh_data_obj
    


class PupilMesh(object):
    # dump of pupil topology. Always the same so no need to recalculate each time
    #
    vertices = [(0.551634, 0.551645, 0.0), (0.314172, 0.627605, 0.0), (0.382049, 0.922303, 0.0), 
                (0.707107, 0.707105, 0.0), (0.0, 0.673187, 0.0), (-1e-06, 1.0, 0.0), 
                (-0.314172, 0.627605, 0.0), (-0.38205, 0.922303, 0.0), (-0.551634, 0.551645, 0.0), 
                (-0.707109, 0.707039, 0.0), (-0.627649, 0.314196, 0.0), (-0.922352, 0.382029, 0.0), 
                (-0.673143, 6.5e-05, 0.0), (-0.999999, 0.0, 0.0), (-0.627649, -0.314064, 0.0), 
                (-0.922352, -0.381964, 0.0), (-0.551634, -0.551514, 0.0), (-0.707109, -0.706974, 0.0), 
                (-0.314173, -0.627573, 0.0), (-0.38205, -0.92227, 0.0), (0.0, -0.67309, 0.0), 
                (-1e-06, -0.999868, 0.0), (0.314172, -0.627573, 0.0), (0.382049, -0.92227, 0.0), 
                (0.551634, -0.551514, 0.0), (0.707106, -0.706974, 0.0), (0.627649, -0.314064, 0.0), 
                (0.92235, -0.381964, 0.0), (0.673141, 0.0, 0.0), (1.0, 0.0, 0.0), 
                (0.627649, 0.314196, 0.0), (0.922351, 0.382029, 0.0), (-0.333469, 0.333464, 0.0), 
                (0.0, 0.356108, 0.0), (0.0, 0.0, 0.0), (-0.35605, 0.0, 0.0), 
                (-0.333469, -0.333399, 0.0), (0.0, -0.355978, 0.0), (0.333465, -0.333399, 0.0), 
                (0.356051, 0.0, 0.0), (0.333465, 0.333498, 0.0), (-0.34079, 0.774413, 0.0), 
                (-0.451395, 0.58638, 0.0), (-0.555268, 0.830417, 0.0), (-0.618047, 0.618069, 0.0), 
                (-0.586384, 0.451403, 0.0), (-0.830453, 0.55525, 0.0), (-0.774395, 0.340805, 0.0), 
                (-0.659541, 0.161097, 0.0), (-0.979851, 0.19462, 0.0), (-0.83518, 0.0, 0.0), 
                (-0.659541, -0.16103, 0.0), (-0.979851, -0.194553, 0.0), (-0.774395, -0.34074, 0.0), 
                (-0.586387, -0.451303, 0.0), (-0.830453, -0.555151, 0.0), (-0.618047, -0.617905, 0.0), 
                (-0.451395, -0.58625, 0.0), (-0.555268, -0.830318, 0.0), (-0.34079, -0.774282, 0.0), 
                (-0.16106, -0.659458, 0.0), (-0.194587, -0.979748, 0.0), (-1e-06, -0.835102, 0.0), 
                (0.161056, -0.659458, 0.0), (0.194585, -0.979748, 0.0), (0.340786, -0.774282, 0.0), 
                (0.451393, -0.58625, 0.0), (0.555263, -0.830318, 0.0), (0.618048, -0.617905, 0.0), 
                (0.586384, -0.451303, 0.0), (0.830452, -0.555151, 0.0), (0.774392, -0.34074, 0.0), 
                (0.659539, -0.16103, 0.0), (0.979852, -0.194553, 0.0), (0.835175, 0.0, 0.0), 
                (0.659539, 0.161097, 0.0), (0.979847, 0.19462, 0.0), (0.774392, 0.340773, 0.0), 
                (0.586384, 0.451403, 0.0), (0.830451, 0.55525, 0.0), (-0.483327, 0.316818, 0.0), 
                (-0.316834, 0.48332, 0.0), (-0.170108, 0.348768, 0.0), (0.0, 0.51668, 0.0), 
                (-0.348747, 0.170107, 0.0), (-0.181505, 0.0, 0.0), (-1e-06, 0.181479, 0.0), 
                (-0.516681, 0.0, 0.0), (-0.316838, -0.483189, 0.0), (-0.483327, -0.316784, 0.0), 
                (-0.348747, -0.170042, 0.0), (-0.170108, -0.348669, 0.0), (0.0, -0.181479, 0.0), 
                (0.0, -0.516615, 0.0), (0.483327, -0.316784, 0.0), (0.316834, -0.483189, 0.0), 
                (0.170108, -0.348669, 0.0), (0.348747, -0.170042, 0.0), (0.181503, 0.0, 0.0), 
                (0.516682, 0.0, 0.0), (0.316834, 0.48332, 0.0), (0.483326, 0.316818, 0.0), 
                (0.348747, 0.170139, 0.0), (0.170108, 0.348801, 0.0), (0.618048, 0.618069, 0.0), 
                (0.451392, 0.58638, 0.0), (0.555263, 0.830417, 0.0), (0.340786, 0.774413, 0.0), 
                (0.161056, 0.659523, 0.0), (0.194585, 0.979847, 0.0), (-1e-06, 0.835103, 0.0), 
                (-0.16106, 0.659523, 0.0), (-0.194587, 0.979847, 0.0), (0.49186, 0.709923, 0.0), 
                (0.174258, 0.818325, 0.0), (-0.174259, 0.818325, 0.0), (-0.491861, 0.709923, 0.0), 
                (-0.709927, 0.491873, 0.0), (-0.818337, 0.174269, 0.0), (-0.818338, -0.174236, 0.0), 
                (-0.709927, -0.491741, 0.0), (-0.491861, -0.709858, 0.0), (-0.174259, -0.818325, 0.0),  
                (0.174259, -0.81826, 0.0), (0.491856, -0.709791, 0.0), (0.709926, -0.491776, 0.0), 
                (0.818337, -0.174236, 0.0), (0.818338, 0.174269, 0.0), (0.709926, 0.491873, 0.0), 
                (-0.45681, 0.45681, 0.0), (-0.162107, 0.506226, 0.0), (-0.177765, 0.177742, 0.0), 
                (-0.506176, 0.162144, 0.0), (-0.456809, -0.456743, 0.0), (-0.506176, -0.162046, 0.0), 
                (-0.177765, -0.177742, 0.0), (-0.162107, -0.506096, 0.0), (0.456807, -0.456678, 0.0), 
                (0.162107, -0.506096, 0.0), (0.177765, -0.177742, 0.0), (0.506174, -0.162046, 0.0), 
                (0.456807, 0.45681, 0.0), (0.506174, 0.162144, 0.0), (0.177762, 0.177776, 0.0), 
                (0.162107, 0.506226, 0.0)]

        
    faces = [4 for _ in range(128)]
    
    connections = [0, 104, 113, 105, 104, 3, 106, 113, 113, 106, 2, 107, 105, 113, 107, 1, 1, 107,
                   114, 108, 107, 2, 109, 114, 114, 109, 5, 110, 108, 114, 110, 4, 4, 110, 115,
                   111, 110, 5, 112, 115, 115, 112, 7, 41, 111, 115, 41, 6, 6, 41, 116, 42, 41, 7,
                   43, 116, 116, 43, 9, 44, 42, 116, 44, 8, 8, 44, 117, 45, 44, 9, 46, 117, 117,
                   46, 11, 47, 45, 117, 47, 10, 10, 47, 118, 48, 47, 11, 49, 118, 118, 49, 13, 50,
                   48, 118, 50, 12, 12, 50, 119, 51, 50, 13, 52, 119, 119, 52, 15, 53, 51, 119,
                   53, 14, 14, 53, 120, 54, 53, 15, 55, 120, 120, 55, 17, 56, 54, 120, 56, 16, 16,
                   56, 121, 57, 56, 17, 58, 121, 121, 58, 19, 59, 57, 121, 59, 18, 18, 59, 122,
                   60, 59, 19, 61, 122, 122, 61, 21, 62, 60, 122, 62, 20, 20, 62, 123, 63, 62, 21,
                   64, 123, 123, 64, 23, 65, 63, 123, 65, 22, 22, 65, 124, 66, 65, 23, 67, 124,
                   124, 67, 25, 68, 66, 124, 68, 24, 24, 68, 125, 69, 68, 25, 70, 125, 125, 70,
                   27, 71, 69, 125, 71, 26, 26, 71, 126, 72, 71, 27, 73, 126, 126, 73, 29, 74, 72,
                   126, 74, 28, 28, 74, 127, 75, 74, 29, 76, 127, 127, 76, 31, 77, 75, 127, 77, 30,
                   30, 77, 128, 78, 77, 31, 79, 128, 128, 79, 3, 104, 78, 128, 104, 0, 8, 45, 129,
                   42, 45, 10, 80, 129, 129, 80, 32, 81, 42, 129, 81, 6, 6, 81, 130, 111, 81, 32,
                   82, 130, 130, 82, 33, 83, 111, 130, 83, 4, 32, 84, 131, 82, 84, 35, 85, 131,
                   131, 85, 34, 86, 82, 131, 86, 33, 10, 48, 132, 80, 48, 12, 87, 132, 132, 87,
                   35, 84, 80, 132, 84, 32, 16, 57, 133, 54, 57, 18, 88, 133, 133, 88, 36, 89, 54,
                   133, 89, 14, 14, 89, 134, 51, 89, 36, 90, 134, 134, 90, 35, 87, 51, 134, 87, 12,
                   36, 91, 135, 90, 91, 37, 92, 135, 135, 92, 34, 85, 90, 135, 85, 35, 18, 60, 136,
                   88, 60, 20, 93, 136, 136, 93, 37, 91, 88, 136, 91, 36, 24, 69, 137, 66, 69, 26,
                   94, 137, 137, 94, 38, 95, 66, 137, 95, 22, 22, 95, 138, 63, 95, 38, 96, 138,
                   138, 96, 37, 93, 63, 138, 93, 20, 38, 97, 139, 96, 97, 39, 98, 139, 139, 98, 34,
                   92, 96, 139, 92, 37, 26, 72, 140, 94, 72, 28, 99, 140, 140, 99, 39, 97, 94, 140,
                   97, 38, 0, 105, 141, 78, 105, 1, 100, 141, 141, 100, 40, 101, 78, 141, 101, 30,
                   30, 101, 142, 75, 101, 40, 102, 142, 142, 102, 39, 99, 75, 142, 99, 28, 40, 103,
                   143, 102, 103, 33, 86, 143, 143, 86, 34, 98, 102, 143, 98, 39, 1, 108, 144, 100,
                   108, 4, 83, 144, 144, 83, 33, 103, 100, 144, 103, 40]

 
 
def creator():
    return omMPx.asMPxPtr(CSEye())


 
def initialize():
    numeric_attr = om.MFnNumericAttribute()    
    typed_attr = om.MFnTypedAttribute()
    matrix_attr = om.MFnMatrixAttribute()

    # inputs
    #
    setattr(CSEye, 'inputSurface', typed_attr.create('inputSurface', 'is', om.MFnNurbsSurfaceData.kNurbsSurface))
    typed_attr.setWritable(True)
    typed_attr.setStorable(False)    
    typed_attr.setCached(False)
        
    surface_attr = getattr(CSEye, 'inputSurface')
    CSEye.addAttribute(surface_attr)
    
    # matrix inputs
    #
    all_matrix_attrs = []
    for matrix in ('worldMatrix', 'parentInverseMatrix'):
        setattr(CSEye, matrix, matrix_attr.create(matrix, matrix, om.MFnMatrixAttribute.kDouble))
        matrix_attr.setWritable(True)
        matrix_attr.setStorable(True)
    
        world_matrix_attr = getattr(CSEye, matrix)
        CSEye.addAttribute(world_matrix_attr)
        all_matrix_attrs.append(world_matrix_attr)
    
    # sphere attributes
    #
    for direction in 'uv':
        long_name = '{}Spans'.format(direction)
        short_name = '{}s'.format(direction)
        setattr(CSEye, long_name, numeric_attr.create(long_name, short_name, om.MFnNumericData.kInt))
        numeric_attr.setWritable(True)
        numeric_attr.setStorable(True)
        numeric_attr.setDefault(8)
        numeric_attr.setMin(4)
        numeric_attr.setMax(50)
        numeric_attr.setChannelBox(True)
        CSEye.addAttribute(getattr(CSEye, long_name)) 

    # iris attributes
    #
    for iris_attr_data in (('eyeScale', 'es', 1.0, 0.1, 50.0, om.MFnNumericData.kFloat),
                           ('irisSize', 'irs', 0.5, 0.0, 10.0, om.MFnNumericData.kFloat), 
                           ('irisScaleX', 'irsx', 1.0, 0.0, 2.0, om.MFnNumericData.kFloat), 
                           ('irisScaleY', 'irsy', 1.0, 0.0, 2.0, om.MFnNumericData.kFloat),
                           ('irisCurveAngle', 'irca', 30.0, 0.0, 90, om.MFnNumericData.kFloat),
                           ('irisDivisions', 'irdv', 6, 1, 20, om.MFnNumericData.kInt),
                           ('irisBevel', 'irbv', 2, 0, 5, om.MFnNumericData.kInt),
                           ('irisRotation', 'irr', 0.0, -720.0, 720.0, om.MFnNumericData.kFloat)):
        name, short_name, default, min_value, max_value, data_type = iris_attr_data
        setattr(CSEye, name, numeric_attr.create(name, short_name, data_type))
        numeric_attr.setWritable(True)
        numeric_attr.setStorable(True)
        numeric_attr.setDefault(default)
        numeric_attr.setMin(min_value)
        numeric_attr.setMax(max_value)
        numeric_attr.setChannelBox(True)

        iris_attr = getattr(CSEye, name)
        CSEye.addAttribute(iris_attr)
        
    # pupil attributes
    #
    for pupil_attr_data in (('pupilSize', 'ps', 0.5, 0.0, 1.0, om.MFnNumericData.kFloat),
                            ('pupilRotation', 'pr', 0.0, -360.0, 360.0, om.MFnNumericData.kFloat),
                            ('pupilScaleX', 'psx', 1.0, 0.0, 2.0, om.MFnNumericData.kFloat), 
                            ('pupilScaleY', 'psy', 1.0, 0.0, 2.0, om.MFnNumericData.kFloat),
                            ('pupilTranslateX', 'ptx', 0.0, - 1.0, 1.0, om.MFnNumericData.kFloat),
                            ('pupilTranslateY', 'pty', 0.0, - 1.0, 1.0, om.MFnNumericData.kFloat),
                            ('pupilDepth', 'psd', 0.15, 0.0, 1.0, om.MFnNumericData.kFloat)):
        name, short_name, default, min_value, max_value, data_type = pupil_attr_data
        setattr(CSEye, name, numeric_attr.create(name, short_name, data_type))
        numeric_attr.setWritable(True)
        numeric_attr.setStorable(True)
        numeric_attr.setDefault(default)
        numeric_attr.setMin(min_value)
        numeric_attr.setMax(max_value)
        numeric_attr.setChannelBox(True)

        pupil_attr = getattr(CSEye, name)
        CSEye.addAttribute(pupil_attr)
 
    # geometry outputs
    #    
    affected_by = {'eyeball':['uSpans', 'vSpans', 'irisSize', 'irisScaleX', 
                              'irisScaleY','eyeScale','irisRotation'],
                   
                   'iris':['vSpans', 'irisSize', 'irisScaleX', 'irisScaleY', 'irisCurveAngle', 
                           'irisDivisions', 'irisBevel','pupilSize', 'pupilScaleX', 
                           'pupilScaleY','pupilDepth','eyeScale','irisRotation', 
                           'pupilTranslateX', 'pupilTranslateY','pupilRotation'],
                   
                   'pupil':['irisSize', 'irisScaleX', 'irisScaleY', 'pupilSize', 
                            'pupilScaleX', 'pupilScaleY','pupilDepth','eyeScale','irisRotation', 
                            'pupilTranslateX', 'pupilTranslateY','pupilRotation']}
    
    # create mesh outputs and connect to driver attributes
    #
    for geo_name in ['eyeball', 'iris', 'pupil']:        
        setattr(CSEye, geo_name, typed_attr.create(geo_name, geo_name, om.MFnMeshData.kMesh))
        typed_attr.setWritable(True)
        typed_attr.setStorable(True)        
        mesh_attr = getattr(CSEye, geo_name)
        CSEye.addAttribute(mesh_attr)
    
        CSEye.attributeAffects(surface_attr, mesh_attr)
        for world_matrix_attr in all_matrix_attrs:
            CSEye.attributeAffects(world_matrix_attr, mesh_attr) 
        
        for affected_attr_name in affected_by[geo_name]:
            affected_attr = getattr(CSEye, affected_attr_name)
            CSEye.attributeAffects(affected_attr, mesh_attr)
            
            
    setattr(CSEye, 'irisMatrix', matrix_attr.create('irisMatrix', 'irisMatrix', om.MFnMatrixAttribute.kDouble))
    matrix_attr.setReadable(True)
    matrix_attr.setStorable(False)
    matrix_attr.setWritable(False)
    matrix_attr.setKeyable(False)
    
    iris_matrix_attr = getattr(CSEye, 'irisMatrix')
    CSEye.addAttribute(iris_matrix_attr)  
    
    CSEye.attributeAffects(surface_attr, iris_matrix_attr)
    for world_matrix_attr in all_matrix_attrs:
        CSEye.attributeAffects(world_matrix_attr, iris_matrix_attr) 
    
 
 
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



