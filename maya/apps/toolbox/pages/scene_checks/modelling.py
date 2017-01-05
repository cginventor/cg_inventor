import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import maya.cmds as mc

import os
import xml.etree.ElementTree as ET

import cg_inventor.sys.lib.qt.base as base
import cg_inventor.sys.lib.qt.widgets.scene_check as scene_check

from cg_inventor.maya.apps.toolbox import page, settings

import cg_inventor.maya.utils.generic    as util_generic
import cg_inventor.maya.utils.transforms as util_transforms
import cg_inventor.maya.utils.history    as util_history
import cg_inventor.maya.utils.mesh       as util_mesh
import cg_inventor.maya.utils.texture    as util_texture


callbackPlus    = util_generic.callbackPlus
callbackSetup   = util_generic.callbackSetup
callbackCounter = util_generic.callbackCounter

setup  = scene_check.setup
check  = scene_check.check
select = scene_check.select
fix    = scene_check.fix

MODE_SEL = scene_check.SceneCheck.MODE_SEL
MODE_ALL = scene_check.SceneCheck.MODE_ALL

# ------------------------------------------------------------------------------------------------ #
#                                      MODELLING CHECKS                                            #
# ------------------------------------------------------------------------------------------------ #

TITLE    = 'Scene Checker'
SUBTITLE = 'Modelling' 

class ModellingChecks(page.Page):
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        self.subtitle = SUBTITLE
        
        self._all_sets    = []
        self._all_spacers = []
        
        self.settings_widget = ModellingChecksSettings
        
        self.loadXML("scene_checks_modelling.xml")
        
        
    def _addSceneCheckSet(self, title):
        new_set = scene_check.SceneCheckSet(title)
        self._all_sets.append(new_set)
        self.addElement(new_set)
        
        self.connect(new_set, qc.SIGNAL(base.Base.STATUS_NORMAL),  self.statusNormal)
        self.connect(new_set, qc.SIGNAL(base.Base.STATUS_SUCCESS), self.statusSuccess)
        self.connect(new_set, qc.SIGNAL(base.Base.STATUS_ERROR),   self.statusError)
        
        return new_set
    

    def clear(self):
        for check_set in self._all_sets:
            self.removeElement(check_set)
            check_set.deleteLater()
            
        for spacer in self._all_spacers:
            self.removeElement(spacer)
            
        self._all_sets    = []
        self._all_spacers = []
    
    
    def loadXML(self, xml_file):
        # get toolbox xml path
        #
        import cg_inventor.maya.apps.toolbox as toolbox
        xml_path = os.path.join(os.path.dirname(toolbox.__file__), 'xml', xml_file)
        
        # get the root element
        #
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for check_set in root:
            set_title = check_set.attrib['title']
            new_set = self._addSceneCheckSet(set_title)
            
            for check in check_set:
                function_set = str(check.text).strip()
                new_check = scene_check.SceneCheck()
                new_check.loadFromLibrary(function_set)
                
                new_set.addSceneCheck(new_check)
            
            spacer = qg.QSpacerItem(20,20,qg.QSizePolicy.Fixed)
            self.addElement(spacer)
            self._all_spacers.append(spacer)
    
    
# ------------------------------------------------------------------------------------------------ #
#                                      MODELLING CHECKS                                            #
# ------------------------------------------------------------------------------------------------ #

class ModellingChecksSettings(settings.Settings):
    def __init__(self):
        settings.Settings.__init__(self)
        #self.setMinimumWidth(600)
        self.setFixedWidth(700)
        
        main_layout = qg.QHBoxLayout()
        main_layout.setContentsMargins(5,0,5,5)
        main_layout.setSpacing(5)
        self.addElement(main_layout)
        
        group_widget      = qg.QWidget()
        group_widget.setLayout(qg.QVBoxLayout())
        group_widget.layout().setContentsMargins(0,0,0,0)
        group_widget.layout().setSpacing(0)
        check_widget      = qg.QWidget()
        check_widget.setLayout(qg.QVBoxLayout())
        check_widget.layout().setContentsMargins(0,0,0,0)
        check_widget.layout().setSpacing(0)
        button_widget     = qg.QWidget()
        button_widget.setLayout(qg.QVBoxLayout())
        all_checks_widget = qg.QWidget()
        all_checks_widget.setLayout(qg.QVBoxLayout())
        all_checks_widget.layout().setContentsMargins(0,0,0,0)
        all_checks_widget.layout().setSpacing(0)
        description_widget = qg.QWidget()
        description_widget.setLayout(qg.QVBoxLayout())
        description_widget.layout().setContentsMargins(0,0,0,0)
        description_widget.layout().setSpacing(0)
        
        button_widget.setFixedWidth(30)
        
        main_layout.addWidget(group_widget)
        main_layout.addWidget(check_widget)
        main_layout.addWidget(button_widget)
        main_layout.addWidget(all_checks_widget)
        main_layout.addWidget(description_widget)
        
        title_font = qg.QFont()
        title_font.setBold(True)
        
        group_label        = qg.QLabel('GROUPS')
        group_layout       = qg.QHBoxLayout()
        checks_label       = qg.QLabel('CHECKS')
        checks_layout      = qg.QHBoxLayout()
        all_checks_label   = qg.QLabel('ALL CHECKS')
        all_checks_layout  = qg.QHBoxLayout()
        description_label  = qg.QLabel('DESCRIPTION')
        description_layout = qg.QHBoxLayout()
        
        group_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        group_layout.addWidget(group_label)
        group_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        
        checks_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        checks_layout.addWidget(checks_label)
        checks_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        
        all_checks_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        all_checks_layout.addWidget(all_checks_label)
        all_checks_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        
        description_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        description_layout.addWidget(description_label)
        description_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        
        group_label.setFont(title_font)
        checks_label.setFont(title_font)
        all_checks_label.setFont(title_font)
        description_label.setFont(title_font)
        
        group_label.setFixedHeight(18)
        checks_label.setFixedHeight(18)
        all_checks_label.setFixedHeight(18)
        description_label.setFixedHeight(18)
        
        self.group_list      = qg.QListWidget()
        self.check_list      = qg.QListWidget()
        self.all_checks_list = qg.QListWidget()
        self.description_te  = qg.QTextEdit()
        
        group_widget.layout().addLayout(group_layout)
        group_widget.layout().addWidget(self.group_list)
        check_widget.layout().addLayout(checks_layout)
        check_widget.layout().addWidget(self.check_list)
        all_checks_widget.layout().addLayout(all_checks_layout)
        all_checks_widget.layout().addWidget(self.all_checks_list)
        description_widget.layout().addLayout(description_layout)
        description_widget.layout().addWidget(self.description_te)
        
        self.all_checks_list.itemClicked.connect(self.showDescription)
        
        self._check_descriptions = {}
        
        self.populateAllChecks()
        
    
    def clearAllChecks(self):
        pass
        
    
    def populateAllChecks(self):
        self.clearAllChecks()
        
        all_names = []
        for check_name, setup_func in scene_check.SceneCheckLibrary.setup.items():
            title, _, description = setup_func()
            self._check_descriptions[title] = description
            all_names.append(title)
        
        for name in sorted(all_names):
            new_item = qg.QListWidgetItem()
            new_item.setText(name)
            self.all_checks_list.addItem(new_item)
            
            
        
    def showDescription(self, check_item):        
        description = self._check_descriptions[str(check_item.text())]
        
        self.description_te.setText(description)
                    
        
        
# ------------------------------------------------------------------------------------------------ #
#                                           CHECKS                                                 #
# ------------------------------------------------------------------------------------------------ #

@setup
def freezeTransforms():
    title       = 'Unfrozen Transforms'
    message     = 'Found $NUM Unfrozen Transform(s)'
    description = 'Finds all transforms with unfrozen values.' 
    return title, message, description


@check
def freezeTransforms(selection_mode, callback=None):    
    try:        
        if selection_mode == MODE_SEL:
            transforms = mc.ls(sl=True)
        else:
            transforms = util_transforms.getAllTransforms()
        
        if not len(transforms): return

        return util_transforms.getUnfrozenTransforms(transforms, callback=callback)
    
    except util_transforms.TransformError as e:
        raise scene_check.SceneCheckError(e)


@select
def freezeTransforms(unfrozen_transforms):
    mc.select(mc.ls(unfrozen_transforms, type='transform'), r=True)
    

@fix
def freezeTransforms(transforms, callback=None):
    try:
        util_transforms.freezeTransforms(transforms, filter=True, callback=callback)
    except util_transforms.TransformError as e:
        raise scene_check.SceneCheckError(str(e)) 
    
#--------------------------------------------------------------------------------------------------#

@setup
def nonDeletedHistory():
    title       = 'Non-Deleted History'
    message     = 'Found $NUM Node(s) with History'
    description = 'Find any nodes with history.'
    return title, message, description


@check
def nonDeletedHistory(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            transforms = mc.ls(sl=True)
        else:
            transforms = util_transforms.getAllTransforms()
            
        if not len(transforms): return
            
        return util_history.getNodesWithHistory(transforms, callback=callback)
    except util_history.HistoryError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def nonDeletedHistory(history_nodes):
    mc.select(mc.ls(history_nodes), r=True)
    
    
@fix
def nonDeletedHistory(history_nodes):
    try:
        util_history.deleteHistory(history_nodes)
    except util_history.HistoryError as e:
        raise scene_check.SceneCheckError(str(e))
    
#--------------------------------------------------------------------------------------------------#

@setup
def centeredPivots():
    title       = 'Non Centered Pivots'
    message     = 'Found $NUM Non Centered Pivot(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description

    
@check
def centeredPivots(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
    
        if not len(meshes): return
        
        if callback: counter, increment = callbackSetup(len(meshes), callback_range=30)
            
        transforms = set([])
        for mesh in meshes:
            if callback: callback(callbackCounter(counter, increment))
            
            if util_mesh._isMeshEmpty(mesh): continue
            transforms.add(util_mesh.getTransformFromShape(mesh))
            
        if callback: counter, increment = callbackSetup(len(transforms), callback_range=70)
        
        not_centred = []
        for transform in transforms:
            if callback: callback(30 + callbackCounter(counter, increment))
            
            if not util_transforms.isPivotCentered(transform):
                not_centred.append(transform)
        
        return not_centred
    
    except (util_transforms.TransformError, util_mesh.MeshError) as e:
        raise scene_check.SceneCheckError(str(e))


@select
def centeredPivots(transforms):
    mc.select(transforms, r=True)
    
    
@fix
def centeredPivots(transforms, callback=None):
    try:
        mc.xform(transforms, cp=True)
    except Exception as e:
        raise scene_check.SceneCheckError(str(e)) 

#--------------------------------------------------------------------------------------------------#

@setup
def unknownNodes():
    title       = "'Unknown' Nodes"
    message     = "Found $NUM 'Unknown' Node(s)"
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def unknownNodes(selection_mode):
    if selection_mode == MODE_SEL:
        return mc.ls(sl=True, type='unknown')
    else:
        return mc.ls(type='unknown')
    
    
@select
def unknownNodes(nodes):
    mc.select(mc.ls(nodes), r=True)

#--------------------------------------------------------------------------------------------------#

@setup
def triangles():
    title       = 'Triangles'
    message     = 'Found $NUM Triangle(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def triangles(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
    
        if not len(meshes): return
        
        return util_mesh.checkMesh(meshes, flags=util_mesh.TRIANGLES, callback=callback)
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e)) 


@select
def triangles(triangles):
    mc.select(triangles, r=True)
    
#--------------------------------------------------------------------------------------------------#

@setup
def nsided():
    title   = 'N-Sided Faces'
    message     = 'Found $NUM N-Sided Face(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def nsided(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        if not len(meshes): return
        
        return util_mesh.checkMesh(meshes, flags=util_mesh.NSIDED, callback=callback)
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e)) 


@select
def nsided(faces):
    mc.select(faces, r=True)
    
#--------------------------------------------------------------------------------------------------#

@setup
def holed():
    title       = 'Holes'
    message     = 'Found $NUM Hole(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def holed(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
    
        if not len(meshes): return
        
        if callback: counter, increment = callbackSetup(len(meshes), callback_range=30)
        
        holes = []
        for mesh in meshes:
            if callback: callback(callbackCounter(counter, increment))
            
            if util_mesh._isMeshEmpty(mesh): continue
            mesh_holes = util_mesh.getMeshHoles(mesh)
            holes.extend([(mesh, mesh_hole) for mesh_hole in mesh_holes])
        
        return holes

    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e)) 


@select
def holed(holes):
    edges = []
    for mesh, edge_indices in holes:
        edges.extend(['%s.e[%s]' %(mesh, edge_index) for edge_index in edge_indices])
    mc.select(mc.ls(edges), r=True)
    
#--------------------------------------------------------------------------------------------------#

@setup
def zeroLengthEdges():
    title       = 'Zero Length Edges'
    message     = 'Found $NUM Zero Length Edge(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def zeroLengthEdges(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        if not len(meshes): return
        
        return util_mesh.checkMesh(meshes, flags=util_mesh.ZERO_LENGTH_EDGES, callback=callback)
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e))

@select
def zeroLengthEdges(edges):
    mc.select(mc.ls(edges), r=True)

#--------------------------------------------------------------------------------------------------#

@setup
def zeroAreaFaces():    
    title       = 'Zero Area Faces'
    message     = 'Found $NUM Zero Area Face(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def zeroAreaFaces(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        if not len(meshes): return
        
        return util_mesh.checkMesh(meshes, flags=util_mesh.ZERO_AREA_FACES, callback=callback)
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def zeroAreaFaces(faces):
    mc.select(mc.ls(faces), r=True)
    
#--------------------------------------------------------------------------------------------------#

@setup
def lockedNormals():
    title       = 'Locked Normals'
    message     = 'Found $NUM Locked Normal(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def lockedNormals(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
            
        num_meshes = len(meshes)
        if not num_meshes: return
        
        if callback: counter, increment = callbackSetup(num_meshes, callback_range=100)
        
        locked_normals = []
        for mesh in meshes:            
            if callback: callback(callbackCounter(counter, increment))
            
            if util_mesh._isMeshEmpty(mesh): continue
            indices = util_mesh.getLockedVertexNormals(mesh)
            vertices = ['%s.vtx[%s]' %(mesh, index) for index in indices]
            locked_normals.extend(vertices)
        
        return locked_normals

    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def lockedNormals(normals):
    mc.select(mc.ls(normals), r=True)
 
    
@fix
def lockedNormals(normals):
    try:
        mc.polyNormalPerVertex(normals, ufn=True)
    except Exception as e:
        raise scene_check.SceneCheckError(str(e))
       
#--------------------------------------------------------------------------------------------------#

@setup
def hardEdges():
    title       = 'Hard Edges'
    message     = 'Found $NUM Hard Edge(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def hardEdges(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        num_meshes = len(meshes)
        if not num_meshes: return
        
        if callback: counter, increment = callbackSetup(num_meshes, callback_range=100)
        
        hard_edges = []
        for mesh in meshes:
            if callback: callback(callbackCounter(counter, increment))
            
            if util_mesh._isMeshEmpty(mesh): continue
            hard_edges.extend([(mesh, edge) for edge in util_mesh.getHardEdges(mesh)])
        
        return hard_edges
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def hardEdges(edges):
    edge_strings = []
    for mesh, edge in edges:
        edge_strings.append('%s.e[%s]' %(mesh, edge))
    mc.select(edge_strings, r=True)
    
    
@fix
def hardEdges(edges, callback=None):
    try:
        all_hard_edges = {}
        
        if callback: 
            counter, increment = callbackSetup(len(edges), callback_range=20)
        
        for mesh, edge in edges:
            if callback: callback(callbackCounter(counter, increment))
                        
            try:
                hard_edges = all_hard_edges[mesh]
            except KeyError:
                hard_edges = all_hard_edges[mesh] = []
            hard_edges.append('%s.e[%s]' %(mesh, edge))
            
        if callback: 
            counter, increment = callbackSetup(len(all_hard_edges.keys()), callback_range=80)
        
        for mesh, hard_edges in all_hard_edges.items():
            if callback: callback(20 + callbackCounter(counter, increment))
            
            history = bool(mc.listHistory(mesh, il=2, pdo=True))
            mc.polySoftEdge(*hard_edges, a=180, ch=history)
            
    except Exception as e:
        raise scene_check.SceneCheckError(str(e))

#--------------------------------------------------------------------------------------------------#

@setup
def unconnectedIntermediates():
    title       = 'Unconnected Intermediates'
    message     = 'Found $NUM Unconnected Intermediate(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description
    

@check
def unconnectedIntermediates(selection_mode):
    return util_mesh.getUnconnectedIntermediates()


@select
def unconnectedIntermediates(intermediates):
    mc.select(mc.ls(intermediates), r=True)

 
@fix
def unconnectedIntermediates(intermediates):
    intermediates = mc.ls(intermediates)
    if not intermediates: return
    
    mc.delete(intermediates)
    
#--------------------------------------------------------------------------------------------------#   

@setup
def emptyMeshes():
    title       = 'Empty Meshes'
    message     = 'Found $NUM Empty Mesh(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def emptyMeshes(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getEmptyMeshes()
        
        num_meshes = len(meshes)
        if not num_meshes: return
        
        if callback: counter, increment = callbackSetup(num_meshes, callback_range=100)
        
        empty_meshes = []
        for mesh in meshes:
            if callback: callback(callbackCounter(counter, increment))
                
            if util_mesh._isMeshEmpty(mesh):
                empty_meshes.append(mesh)
                
        return meshes
    
    except util_mesh.MeshError as e:
        raise scene_check.SceneCheckError(str(e))
    
    
@select    
def emptyMeshes(meshes):    
    mc.select(mc.ls(meshes), r=True)
 
 
@fix
def emptyMeshes(meshes):
    meshes = mc.ls(meshes)
    if not meshes: return
    
    try:
        mc.delete(meshes)
    except Exception as e:
        raise scene_check.SceneCheckError(str(e))
                       
#--------------------------------------------------------------------------------------------------#

@setup
def unusedShaders():
    title       = 'Unused Shaders'
    message     = 'Found $NUM Unused Shader(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def unusedShaders(selection_mode):
    try:
        if selection_mode == MODE_SEL:
            materials = mc.ls(sl=True, mat=True)
            
            unused_materials = []
            for material in materials:                
                if util_texture._getMaterialMembers(material) is None:
                    unused_materials.append(material)
                    
        else:
            unused_materials = util_texture.getAllUnusedMaterials()
            
        return unused_materials
    
    except util_texture.TextureError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def unusedShaders(materials):
    mc.select(materials, r=True)
    
    
@fix
def unusedShaders(materials, callback=None):
    try:
        if callback: counter, increment = callbackSetup(len(materials), callback_range=100)
        
        for material in materials:
            if callback: callback(callbackCounter(counter, increment))
            
            util_texture.deleteMaterial(material)
            
    except util_texture.TextureError as e:
        raise scene_check.SceneCheckError(str(e))
        
#--------------------------------------------------------------------------------------------------#

@setup
def uvsOutOfBounds():
    title       = 'UVs Out of Bounds'
    message     = 'Found $NUM UV(s) Out of Bounds'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def uvsOutOfBounds(selection_mode, callback=None):
    try:        
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        num_meshes = len(meshes)
        if not num_meshes: return 
        
        if callback: counter, increment = callbackSetup(num_meshes, callback_range=100)
    
        all_uvs_oob = []
        for mesh in meshes:
            if callback: callback(callbackCounter(counter, increment))
            
            uvs_oob = util_texture.getAllUVsOutOfBounds(mesh)
            for uv_index in uvs_oob:
                all_uvs_oob.append('%s.map[%s]' %(mesh, uv_index))
        
        return all_uvs_oob
    
    except util_texture.TextureError as e:
        raise scene_check.SceneCheckError(str(e))


@select
def uvsOutOfBounds(uvs):
    mc.select(uvs, r=True)
    
#--------------------------------------------------------------------------------------------------#

@setup
def fivePointers():
    title       = 'Five+ Pointers'
    message     = 'Found $NUM Five+ Pointer(s)'
    description = 'Find any geometry with uncentered pivots.'
    return title, message, description


@check
def fivePointers(selection_mode, callback=None):
    try:
        if selection_mode == MODE_SEL:
            meshes = util_mesh.getMeshesFromSelection(mc.ls(sl=True))
        else:
            meshes = util_mesh.getAllMeshes()
        
        five_pointers = []
        for mesh in meshes:
            vertices = util_mesh.getFiveEdgeVerts(mesh)
            for vertex_index in vertices:
                five_pointers.append('%s.vtx[%s]' %(mesh, vertex_index))
        
        return five_pointers
            
    except Exception as e:
        raise scene_check.SceneCheckError(str(e))
    
    
@select
def fivePointers(verts):
    mc.select(verts, r=True)