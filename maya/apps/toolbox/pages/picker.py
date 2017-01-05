import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import pymel.core as pm

import cg_inventor.maya.apps.toolbox.page as page
import cg_inventor.maya.utils.mesh as util_mesh

TITLE    = 'Animation Picker'

class Picker(page.Page):
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        
        self.picker = picker()
        self.addElement(self.picker)
        
        

class picker(qg.QWidget):
    def __init__(self):
        qg.QWidget.__init__(self)
        
        self.setFixedHeight(600)
        self.setFixedWidth(300)
        
        self.points = []
        
        self.head = pm.PyNode('pSphere1')
        self.camera = pm.PyNode('camera1')
        
        matrix = self.camera.worldInverseMatrix.get()
        
        vert_positions = util_mesh.getAllVertexPositions('pSphereShape1', ws=True)
        
        x_most_index = None; x_most_value = 0
        vec = pm.dt.VectorN(pos[0], pos[1], pos[2], 1.0)
        new_vec = vec * matrix
        
        z_depth = -1.0 / new_vec[2] * 1000
        plane_vec = (int(new_vec[0] * z_depth + 150), int(300 - new_vec[1] * z_depth))

        self.points.append(plane_vec)
        
        if x_most_index == None or plane_vec[0] > x_most_value:
            x_most_index = index
            x_most_value = plane_vec[0]

        
        
    
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        height = option.rect.height() - 1
        width  = option.rect.width() - 1
        
        for point in self.points:
            painter.drawPoint(point[0], point[1])