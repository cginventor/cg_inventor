class Vector3D():
    def __init__(self, *args):
        num_args = len(args)
        
        if num_args == 1:
            self.x = args[0].x
            self.y = args[0].y
            self.z = args[0].z
                
        elif num_args >= 3:        
            self.x = float(args[0])
            self.y = float(args[1])
            self.z = float(args[2])
            
        else:
            self.x = 0.0   
            self.y = 0.0
            self.z = 0.0
            
        
    def __getitem__(self, index):
        if index == 0: return self.x
        if index == 1: return self.y
        if index == 2: return self.z
        raise IndexError('Index out of range. Vec3(x, y, z)')
        
        
    def __setitem__(self, index, value):
        if index == 0: self.x = float(value); return
        if index == 1: self.y = float(value); return
        if index == 2: self.z = float(value); return
    
        
    def __add__(self, vector):
        return Vector3D(self.x + vector.x, self.y + vector.y, self.z + vector.z)
    
    
    def __sub__(self, vector):
        return Vector3D(self.x - vector.x, self.y - vector.y, self.z - vector.z)
    
    
    def __str__(self):
        return 'Vec3(%s, %s, %s)' %(self.x, self.y, self.z)    
    
    __repr__ = __str__
    
        
        
class Vector4D(Vector3D):
    def __init__(self, *args):
        Vector3D.__init__(self, *args)
        
        num_args = len(args)
        
        self.w = 1.0
        if num_args == 1:
            if isinstance(args[0], Vector4D):     
                self.w = args[0].w
        elif num_args == 4:
            self.w = float(args[3])        
    
        
    def __getitem__(self, index):
        if index == 0: return self.x
        if index == 1: return self.y
        if index == 2: return self.z
        if index == 3: return self.w
        raise IndexError('Index out of range. Vec4(x, y, z, w)')
        
        
        
    def __setitem__(self, index, value):
        if index == 0: self.x = float(value); return
        if index == 1: self.y = float(value); return
        if index == 2: self.z = float(value); return
        if index == 3: self.w = float(value); return
    
        
    def __add__(self, vector):
        if not isinstance(vector, Vector4D):
            return Vector3D.__add__(self, vector)
        
        return Vector4D(self.x + vector.x, 
                        self.y + vector.y, 
                        self.z + vector.z,
                        self.w + vector.w)
    
    
    def __sub__(self, vector):
        if not isinstance(vector, Vector4D):
            return Vector3D.__sub__(self, vector)
        
        return Vector4D(self.x - vector.x, 
                        self.y - vector.y, 
                        self.z - vector.z,
                        self.w - vector.w)
    
    
    def __str__(self):
        return 'Vec4(%s, %s, %s, %s)' %(self.x, self.y, self.z, self.w)    
    
    __repr__ = __str__



class Matrix3D():
    def __init__(self, *args):
        num_args = len(args)
        
        if num_args == 1:
            self._values = list(args[0]._values)
            
        if num_args == 9:
            self._row1 = Vector3D(args[0], args[1], args[2])
            self._row2 = Vector3D(args[3], args[4], args[5])
            self._row3 = Vector3D(args[6], args[7], args[8])
            
        else:
            self._row1 = Vector3D(1.0, 0.0, 0.0)
            self._row2 = Vector3D(0.0, 1.0, 0.0)
            self._row3 = Vector3D(0.0, 0.0, 1.0)
            
            
    def __getitem__(self, index):     
        if index == 0: return self._row1
        if index == 1: return self._row2
        if index == 2: return self._row3
        
    
    def __str__(self):
        return 'Mat3((%s, %s, %s), (%s, %s, %s), (%s, %s, %s))' %(self._row1.x, self._row1.y, 
                                                                  self._row1.z, self._row2.x,
                                                                  self._row2.y, self._row2.z,
                                                                  self._row3.x, self._row3.y,
                                                                  self._row3.z)
        
    __repr__ = __str__
    