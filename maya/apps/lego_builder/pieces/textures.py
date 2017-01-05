import maya.cmds as mc

import colors

rgb_convert = lambda r, g, b: (r / 255.0, g / 255.0, b / 255.0)



class TextureError(Exception):
    pass



class Texture():
    DIFFUSE           = 0.5
    SPECULAR_ROLL_OFF = 0.3
    REFLECTIVITY      = 0.0
    ECCENTRICITY      = 0.3
    
    def __init__(self):
        self.shader = None
        self._rgb = (0.0, 0.0, 0.0)        
        
    
    def setColor(self, color):
        self._setColor(self, color)
        
    
    def _setColor(self, r, g, b):
        r, g, b = rgb_convert(r, g, b)
        mc.setAttr('%s.color' %self.shader, r, g, b, type='double3')
    
    
    def create(self, color):
        try:
            color_name = colors.ALL_COLOR_NAMES[color]
        except KeyError:
            raise colors.ColorError("Failed to find color.")
        
        color_name = '%s%s_Lego' %(color_name[0].lower(), color_name[1:].replace(' ','_'))
        if mc.objExists(color_name):
            raise TextureError("Texture '%s' already exists." %color_name)
        
        color_name = mc.shadingNode('blinn', n=color_name, asShader=True)
        
        color_sg = mc.sets(renderable=True, noSurfaceShader=True, name='%sSG' %color_name, empty=True)
        mc.connectAttr('%s.outColor' %color_name, '%s.surfaceShader' %color_sg, f=True)
                
        mc.setAttr('%s.color' %color_name, *rgb_convert(*color), type='double3')
        mc.setAttr('%s.specularColor' %color_name, *rgb_convert(*color), type='double3')
        mc.setAttr("%s.diffuse" %color_name, self.DIFFUSE)
        mc.setAttr("%s.reflectivity" %color_name, self.REFLECTIVITY)
        mc.setAttr("%s.specularRollOff" %color_name, self.SPECULAR_ROLL_OFF)
        mc.setAttr("%s.eccentricity" %color_name, self.ECCENTRICITY)
        