import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import maya.cmds as mc

import pymel.core as pm


class ItemList(qg.QListWidget):

    TRANSFORM   = 'Transform'
    JOINT       = 'Joint'
    OBJECT_SET  = 'ObjectSet'
        
    # shapes
    #
    CAMERA      = 'Camera'
    LOCATOR     = 'Locator'
    
    # geometry
    #
    MESH          = 'Mesh'
    MESH_VERTEX   = 'MeshVertex'
    MESH_FACE     = 'MeshFace'
    MESH_EDGE     = 'MeshEdge'    
    NURBS_CURVE   = 'NurbsCurve'
    NURBS_SURFACE = 'NurbsSurface'

    # joints
    #
    IK_HANDLE   = 'IkHandle'
    IK_EFFECTOR = 'IkEffector'    
    
    # deformers
    #
    LATTICE     = 'Lattice'
    CLUSTER     = 'ClusterHandle'
    
    # utility nodes
    #
    PLUS_MINUS  = 'PlusMinusAverage'
    MULT_DIVIDE = 'MultiplyDivide'
    
    # lights
    #
    AMBIENT_LIGHT     = 'AmbientLight'
    DIRECTIONAL_LIGHT = 'DirectionalLight'
    POINT_LIGHT       = 'PointLight'
    SPOT_LIGHT        = 'SpotLight'
    AREA_LIGHT        = 'AreaLight'
    VOLUME_LIGHT      = 'VolumeLight'
    
    
    ICONS = {TRANSFORM     : ':nodes/small_transform.png',
             JOINT         : ':nodes/small_joint.png',
             OBJECT_SET    : ':nodes/small_object_set.png',
             
             CAMERA        : ':nodes/small_camera.png',
             LOCATOR       : ':nodes/small_locator.png',
             
             MESH          : ':nodes/small_mesh.png',
             MESH_VERTEX   : ':nodes/small_mesh_vertex.png',
             MESH_FACE     : ':nodes/small_mesh_face.png',
             MESH_EDGE     : ':nodes/small_mesh_edge.png',
             NURBS_CURVE   : ':nodes/small_nurbs_curve.png',             
             NURBS_SURFACE : ':nodes/small_nurbs_surface.png',
             
             IK_HANDLE     : ':nodes/small_ik_handle.png',
             IK_EFFECTOR   : ':nodes/small_ik_effector.png',
             
             LATTICE       : ':nodes/small_lattice.png',
             CLUSTER       : ':nodes/small_cluster.png',
             
             PLUS_MINUS    : ':nodes/small_plus_minus.png',
             MULT_DIVIDE   : ':nodes/small_mult_divide.png',
             
             AMBIENT_LIGHT     : ':nodes/small_light.png',
             DIRECTIONAL_LIGHT : ':nodes/small_light.png',
             POINT_LIGHT       : ':nodes/small_light.png',
             SPOT_LIGHT        : ':nodes/small_light.png',
             AREA_LIGHT        : ':nodes/small_light.png',
             VOLUME_LIGHT      : ':nodes/small_light.png'}
    
    
    
    def __init__(self):
        qg.QListWidget.__init__(self)
        
        self._all_nodes = {}
    
    #------------------------------------------------------------------------------------------#
    
    def _removeItems(self):
        for _ in range(self.count()):
            self.takeItem(0)        
        
    #------------------------------------------------------------------------------------------#    
    
    def loadNodes(self, nodes):
        self.clear()
        self._all_nodes = {}
        
        nodes = pm.ls(nodes)
        for node in nodes:
            node_type = type(node).__name__
            
            new_item = qg.QListWidgetItem()
            new_item.setText(node.name())

            new_icon = qg.QIcon(self.ICONS.get(node_type, ':nodes/small_blank.png'))
            new_item.setIcon(new_icon)
            
            try:
                node_dict = self._all_nodes[node_type]
            except KeyError:
                node_dict = self._all_nodes[node_type] = {}
            
            node_dict[node.name()] = new_item
            
            self.addItem(new_item)
            
    #------------------------------------------------------------------------------------------#
            
    def sortByType(self):
        self._removeItems()
        
        for node_type in self._all_nodes.keys():
            node_dict = self._all_nodes[node_type]
            for node_name in sorted(node_dict.keys()):
                self.addItem(node_dict[node_name])
                
                                
    def sortByName(self):
        self._removeItems()
        
        name_order = {}        
        for node_type in self._all_nodes.keys():
            node_dict = self._all_nodes[node_type]
            for node_name, node_item in node_dict.items():
                name_order[node_name] = node_item            
        
        for node_name in sorted(name_order.keys()):
            self.addItem(name_order[node_name])        

    #------------------------------------------------------------------------------------------#    