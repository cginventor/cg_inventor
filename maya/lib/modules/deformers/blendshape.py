import pymel.core as pm
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import math

import xml.etree.ElementTree as ET

from .module import Module, ModuleError 
import rpd_rig.modules.deformers.skinCluster as skcls

from cs_rigging.utils.constants import LEFT, CENTER, RIGHT

import util_dataFile
import util_xml
   
#--------------------------------------------------------------------------------------------------#

class BlendShapeError(ModuleError):
    pass


class BlendShape(Module):    
    def __init__(self):
        Module.__init__(self)
        
        self.base     = None
        self.targets  = set(())
        
    #-----------------------------------------------------------------------------------------#

    def create(self, name, base_shape):
        self.node = mc.deformer(base_shape, n=name, type='blendShape')[0]        
        self.base = base_shape
            

    def createFromData(self, name=None, root=None):
        if root == None:
            try:
                xmlTree = util_xml.read(name, 'blendshapes', inherit=True)
            except util_dataFile.util_dataFileError:
                return False
            root = xmlTree.getroot()
        
        blend_name = eval(root.attrib['name'])
        
        base_shape = None
        matching_geo = False
        base_element = None
        for base in root:
            if base.tag != 'base': continue
            
            base_element = base
            base_shape = eval(base.attrib['name'])
            vert_count = eval(base.attrib['count'])
            
            if not mc.objExists(base_shape):
                raise BlendShapeError("Base Shape '{}' does not exist.".format(base_shape))
            
            if mc.polyEvaluate(base_shape, v=True) == vert_count:
                matching_geo = True
                
        if base_shape is None:
            raise BlendShapeError("No Base Shape provided.")
            
        self.build(blend_name, base_shape)
        
        for target_element in base_element:
            index  = eval(target_element.attrib['index'])
            name   = eval(target_element.attrib['name'])
            target = eval(target_element.attrib['target'])
            normal = eval(target_element.attrib['normal'])
        
            self.addTarget(target, [name], normal, False)

        if matching_geo is True:
            self.loadData()
            
    #-----------------------------------------------------------------------------------------# 
        
    def addTarget(self, target, attributes=None, normal_id=None, next_normal_id=False):
        self._isSet()
        
        base = self.getBaseShape()
        base_index = getGeometryIndex(self.node, base)

        if next_normal_id is True:
            norm_grp_ids = self.getNormGroups()
            normal_id = norm_grp_ids[-1] + 1            
        
        if attributes is None:
            attributes = [target]
        elif isinstance(attributes, (str, unicode)):
            attributes = [attributes]
        
        orig_name = target
        for attribute in attributes:
            next_index = self.getNextIndex()
            
            shapes = mc.listRelatives(target, s=True)
            if not shapes:
                target = mc.rename(target, orig_name)
                err_str = "Failed to add target '{}' to blendshape '{}'.".format(target, self.node)
                raise BlendShapeError(err_str)

            attrName = 'worldMesh[0]'
            if mc.nodeType(shapes[0]) in ('nurbsSurface','nurbsCurve'):
                attrName = 'worldSpace[0]'
            
            mc.blendShape(self.node, e=True, t=(base, next_index, target, 1))
            if normal_id is not None:                
                mc.setAttr('{}.it[{}].itg[{}].nid'.format(self.node, base_index, next_index), normal_id)
            
            mc.aliasAttr(attribute, '{}.weight[{}]'.format(self.node, next_index)) 
        
        if len(attributes) > 1:
            self._floodWeights([attributes[0]], 1.0)
            self._floodWeights(attributes[1:], 0.0)

        self.targets.add(target)


    def addBlankTarget(self, target_name, attributes=None, normal_id=None, next_normal_id=False):
        orig_shape = self.getOrigShape()

        base_shape = self.getBaseShape()
        base_geo = mc.listRelatives(base_shape, p=True)[0]

        target = cleanDuplicate(base_geo, target_name)
        target_shape = getFirstShape(new_target)
        mc.connectAttr('{}.worldMesh[0]'.format(orig_shape), '{}.inMesh'.format(target_shape))
        mc.disconnectAttr('{}.worldMesh[0]'.format(orig_shape), '{}.inMesh'.format(target_shape))

        self.addTarget(target, attributes, normal_id, next_normal_id)

        return dict(zip(self.getTargetAliases(), self.getAllTargetIndices()))
    
    #-----------------------------------------------------------------------------------------#
    
    def getBaseShape(self):
        if self.base is None:
            self.base = mc.blendShape(self.node, q=True, g=True)[0]
        return self.base
        
    #-----------------------------------------------------------------------------------------#

    def getOrigShape(self):
        base_geom = mc.listRelatives(self.getBaseShape(), p=True)
        orig_shp = getOrigShape(base_geom)
        return orig_shp

    #-----------------------------------------------------------------------------------------#

    def getTargetAliases(self):
        num_indices = mc.getAttr('{}.{}'.format(self.node, 'weight'), mi=True)
        aliases = []
        for index in num_indices:
            aliases.append(mc.aliasAttr('{}.weight[{}]'.format(self.node, index), q=True))
        return aliases

    #-----------------------------------------------------------------------------------------#
    
    def getNormGroups(self):
        self._isSet()

        base = self.getBaseShape()
        base_index = getGeometryIndex(self.node, base)
        
        norm_grp_ids    = set(())
        latestNormGrp = 0
        
        norm_grp_indices = mc.getAttr('{}.it[{}].itg'.format(self.node, base_index), mi=True)
        if norm_grp_indices:
            for norm_grp_index in norm_grp_indices:
                norm_grp_id = '{}.it[{}].itg[{}].nid'.format(self.node, base_index, norm_grp_index)
                norm_grp_ids.add(mc.getAttr(norm_grp_id))
        else:
            norm_grp_ids.add(0)
        
        return list(norm_grp_ids)
    
    
    def getTargetNormaliseGroup(self, index):
        self._isSet()
        
        base_index = getGeometryIndex(self.node, self.base)
        return mc.getAttr('{}.it[%{}].itg[{}].nid'.format(self.node, base_index, index))
    
    
    def setTargetNormaliseGroup(self, index, normal_index):
        self._isSet()
        
        base_index = getGeometryIndex(self.node, self.base)
        mc.setAttr('{}.it[{}].itg[%{}].nid'.format(self.node, base_index, index), normal_index)
    
    #-----------------------------------------------------------------------------------------#
    
    def getNextIndex(self):
        if not self.node: raise BlendShapeError(self.ERR_NSET)
        
        indicies = mc.getAttr('{}.weight'.format(self.node), mi=True)
        if not indicies:
            return 0
        return (indicies[-1] + 1)
    
    #-----------------------------------------------------------------------------------------#
    
    def load(self, node):
        self.node = node
        geometry = mc.deformer(self.node, q=True, g=True)
        if not geometry:
            raise BlendShapeError("Failed to load '{}' base geometry." .format(self.node))
        self.base = geometry[0]
        
    #-----------------------------------------------------------------------------------------#
    
    def getTargets(self):
        self._isSet()
        
        if not self.targets:
            input_target = '{}.inputTarget[0]'.format(self.node)
            num_targets = mc.getAttr('{}.inputTargetGroup'.format(input_target), mi=True)
            if num_targets is None: 
                num_targets = []
            
            for index in num_targets:
                input_target_grp = '{}.inputTargetGroup[{}]'.format(input_target, index)
                targets = mc.listConnections('{}.inputTargetItem[6000].inputGeomTarget'.format(input_target_grp))
                
                if not targets: continue                
                self.targets.add(targets[0])
        
        order_dict = {}
        for target in list(self.targets):
            for index in self.getTargetIndices(target):
                order_dict[index] = target
                break
                
        target_order = []
        for target_index in sorted(order_dict.keys()):
            target_order.append(order_dict[target_index])
                
        return target_order
    
    
    def getTargetIndices(self, target):
        self._isSet()
        
        input_target = '{}.inputTarget[0]'.format(self.node)
        num_targets = mc.getAttr('{}.inputTargetGroup'.format(input_target), mi=True)
        
        target_indices = []
        for index in num_targets:
            input_target_grp = '{}.inputTargetGroup[%s]'.format(input_target, index)
            targets = mc.listConnections('{}.inputTargetItem[6000].inputGeomTarget'.format(input_target_grp))
            
            if not targets:
                continue
            
            if target in targets:
                target_indices.append(index)
                
        return target_indices


    def getAllTargetIndices(self):
        self._isSet()

        input_target = '{}.inputTarget[0]'.format(self.node)
        num_targets = mc.getAttr('{}.inputTargetGroup'.format(input_target), mi=True)

        target_indices = []
        for index in num_targets:
            input_target_grp = '{}.inputTargetGroup[{}]'.format(input_target, index)
            targets = mc.listConnections('{}.inputTargetItem[6000].inputGeomTarget'.format(input_target_grp))

            if not targets: 
                continue

            target_indices.append(index)

        return target_indices


    def getAllSplitTargets(self):
        split_blend_dict = {}
        for index in self.getAllTargetIndices():
            geom = self.getTargetMeshAtIndex(index)
            if geom in split_blend_dict:
                split_blend_dict[geom].append(index)
            else:
                split_blend_dict[geom] = [index]

        return_dict = {}
        for target_geo, index_list in split_blend_dict.items():
            if len(index_list) > 1:
                return_dict[target_geo] = index_list

        return return_dict


    def isAliasSplit(self, alias):
        target_index =self.getTargetIndexFromAlias(alias)
        return self.isIndexSplit(self.getAllTargetIndices())


    def isIndexSplit(self, index):
        target_mesh = self.getTargetMeshAtIndex(index)
        return self.isTargetSplit(target_mesh)


    def isTargetSplit(self, target):
        indicies = self.getTargetIndices(target)
        if len(indicies) > 1:
            return True
        else:
            return False


    def getTargetMeshAtIndex(self, index):
        self._isSet()
        
        input_target_grp = '{}.inputTarget[0].inputTargetGroup[{}]'.format(self.node, index)
        connections = mc.listConnections('{}.inputTargetItem[6000].inputGeomTarget'.format(input_target_grp))
        if connections is None:
            return None
        
        return connections[0]
    
    
    def getTargetWeightAlias(self, index):
        self._isSet()
        
        return mc.aliasAttr('{}.weight[{}]'.format(self.node, index), q=True)
    
    
    def getTargetIndexFromAlias(self, alias):
        self._isSet()

        for index in self.getAllTargetIndices():
            if mc.aliasAttr('{}.weight[{}]'.format(self.node, index), q=True) == alias:
                return index
        
        raise BlendShapeError("No target weight matches alias '{}'.".format(alias))
    
    #-----------------------------------------------------------------------------------------#
    
    def setEnvelope(self, value):
        self._isSet()

        mc.setAttr('{}.envelope'.format(self.node), value)
    
    #-----------------------------------------------------------------------------------------#
    
    def copyWeights(self, source_attr, target_attr, mirror=False, mirror_attrs=[]):
        self._isSet()
        
        if isinstance(source_attr, (str, unicode)):
            source_index = self.getTargetIndexFromAlias(source_attr)
        elif isinstance(source_attr, int):
            source_index = source_attr

        if isinstance(target_attr, (str, unicode)):
            target_index = self.getTargetIndexFromAlias(target_attr)
        elif isinstance(target_attr, int):
            target_index = target_attr
            
        # get source weights from source_index
        #
        source_weights = self._getWeightsFromIndex(source_index)
        
        if mirror is True:
            if len(mirror_attrs) == 0:
                mirror_attrs = self._getMirrorAttrsFromBaseShape() 
            else:
                for index in range(3):
                    if isinstance(mirror_attrs[index], (str, unicode)):
                        mirror_attrs[index] = mc.getAttr(mirror_attrs[index])
                    
            lf_attr = mirror_attrs[0]
            rt_attr = mirror_attrs[2]
            
            mirrored_weights = {}
            for source_vert, source_weight in source_weights.items():
                try:
                    mirror_index = lf_attr.index(source_vert)
                    mirrored_weights[rt_attr[mirror_index]] = source_weight  
                except ValueError:
                    try:
                        mirror_index = rt_attr.index(source_vert)
                        mirrored_weights[lf_attr[mirror_index]] = source_weight
                    except ValueError:
                        mirrored_weights[source_vert] = source_weight
            
            source_weights = mirrored_weights
            
        # set weights at target_index
        #
        self._setWeightsAtIndex(target_index, source_weights)        

    #-----------------------------------------------------------------------------------------#
    
    def flipWeights(self, source_attr, target_attr, mirror_attrs=[]):        
        self.copyWeights(source_attr, target_attr, True, mirror_attrs)
        
    
    def mirrorWeights(self, weight_attr, source_side=LEFT, mirror_attrs=[]):
        self._isSet()
        
        if source_side not in [LEFT, RIGHT]:
            raise BlendShapeError("Do not recognise side type '{}'.".format(source_side))
        
        # get weight_index from weight_attr
        #
        if isinstance(weight_attr, (str, unicode)):
            weight_index = self.getTargetIndexFromAlias(weight_attr)
        elif isinstance(source_attr, int):
            weight_index = weight_attr
        
        # get mirror attributes
        #
        if len(mirror_attrs) == 0:
            mirror_attrs = self._getMirrorAttrsFromBaseShape()
        else:
            for index in range(3):
                if isinstance(mirror_attrs[index], (str, unicode)):
                    mirror_attrs[index] = mc.getAttr(mirror_attrs[index])
        
        lf_attr = mirror_attrs[0]
        cn_attr = mirror_attrs[1]
        rt_attr = mirror_attrs[2]
        
        # get source weights from source_index
        #
        curr_weights = self._getWeightsFromIndex(weight_index)
        flipped_weights = {}
        
        
        if source_side == LEFT:
            source_attr, target_attr = lf_attr, rt_attr
        else:     
            source_attr, target_attr = rt_attr, lf_attr
            
        for vert_index, weight in curr_weights.items():
            try:
                # is a vert of the source side
                #
                mirror_index = source_attr.index(vert_index)
                flipped_weights[vert_index] = weight
                flipped_weights[target_attr[mirror_index]] = weight
            except ValueError:
                try:
                    # is a vert on the target side so ignore
                    #
                    mirror_index = target_attr.index(vert_index)
                    continue
                except ValueError:
                    # must be a center vert
                    #
                    flipped_weights[vert_index] = weight
                    
        # set weights at target_index
        #
        self._setWeightsAtIndex(weight_index, flipped_weights)
    
    
    def _getMirrorAttrsFromBaseShape(self):
        base_shape = self.getBaseShape()
        base_transform = mc.listRelatives(base_shape, p=True)[0]

        if not mc.objExists('%s.lfVrts' %base_transform):
            raise BlendShapeError("Unable to mirror weights. Failed to find mirror attributes.")
        
        mirror_attrs = []
        
        for attr in ['lfVrts', 'cnVrts', 'rtVrts']:
            mirror_attrs.append(mc.getAttr('%s.%s' %(base_transform, attr)))
        
        return mirror_attrs
    
    #-----------------------------------------------------------------------------------------#
    
    def copyWeightsFromBlendshape(self, source_bs, source_attr, target_attr):
        self._isSet()
        
        if isinstance(source_attr, (str, unicode)):
            source_index = source_bs.getTargetIndexFromAlias(source_attr)
        elif isinstance(source_attr, int):
            source_index = source_attr

        if isinstance(target_attr, (str, unicode)):
            target_index = self.getTargetIndexFromAlias(target_attr)
        elif isinstance(target_attr, int):
            target_index = target_attr
            
        source_shape = source_bs.getBaseShape()
        base_shape = self.getBaseShape()
        
        source_count = mc.polyEvaluate(source_shape, v=True)
        base_count = mc.polyEvaluate(base_shape, v=True)
        
        if source_count != base_count:
            raise BlendShapeError("Source base shape has a different vert count.")
        
        source_weights = source_bs._getWeightsFromIndex(source_index)           
        self._setWeightsAtIndex(target_index, source_weights)
    
    
    def copyAllWeightsFromBlendshape(self, source_bs):
        source_bs_name = source_bs.name()
        source_aliases = set([])
        for index in range(mc.getAttr('{}.weight'.format(source_bs_name), s=True)):
            source_aliases.add(mc.aliasAttr('{}.weight[{}]'.format(source_bs_name, index), q=True))
            
        target_aliases = set([])
        for index in range(mc.getAttr('{}.weight'.format(self.node), s=True)):
            target_aliases.add(mc.aliasAttr('{}.weight[{}]'.format(self.node, index), q=True))
        
        for alias in list(source_aliases & target_aliases):
            self.copyWeightFromBlendshape(source_bs, alias, alias)
        
    
    def copyWeightsFromBlendshapeByLookup(self, source_bs, source_attr, target_attr, lookup=None):
        self._isSet()
               
        if isinstance(source_attr, (str, unicode)):
            source_index = source_bs.getTargetIndexFromAlias(source_attr)
        elif isinstance(source_attr, int):
            source_index = source_attr

        if isinstance(target_attr, (str, unicode)):
            target_index = self.getTargetIndexFromAlias(target_attr)
        elif isinstance(target_attr, int):
            target_index = target_attr
            
        if lookup is None:
            base_shape = self.getBaseShape()
            lookup = '{}.vertLookup'.format(base_shape)
            if not mc.objExists('{}.vertLookup'.format(base_shape)):
                raise BlendShapeError("Unable to copy weights. Failed to find lookup table.")
        
        if isinstance(lookup, (str, unicode)):
            lookup_table = eval(mc.getAttr(lookup))
        elif not isinstance(lookup, dict):
            raise BlendShapeError("Lookup table must be a dictionary. Got '{}'.".format(type(lookup)))
        
        new_weights = {}
        
        source_weights = source_bs._getWeightsFromIndex(source_index)
        for source_vert_index, weight in source_weights.items():
            try:
                target_vert_index = lookup_table[source_vert_index]
                new_weights[target_vert_index] = weight
            except KeyError:
                continue
            
        self._setWeightsAtIndex(target_index, new_weights)                


    def copyWeightsFromBlendshapeBySpace(self, source_bs, source_attr, target_attr=None, sample_method='UV', sample_space='world'):
        self._isSet()

        if isinstance(source_attr, (str, unicode)):
            source_index = source_bs.getTargetIndexFromAlias(source_attr)
        elif isinstance(source_attr, int):
            source_index = source_attr
            source_attr = source_bs.getTargetWeightAlias(source_attr)

        if isinstance(target_attr, (str, unicode)):
            target_index = self.getTargetIndexFromAlias(target_attr)
        elif isinstance(target_attr, int):
            target_index = target_attr
        elif target_attr is None:
            try:
                target_index = self.getTargetIndexFromAlias(source_attr)
            except :
                raise BlendShapeError("Source Attribute/Index: {} does not exist in Blendshape Node {}".format(source_attr, self.node))

        # create temp geom
        #
        src_shape = source_bs.getBaseShape()
        src_xform = mc.listRelatives(src_shape, p=True)[0]
        src_geom = mc.duplicate(src_xform, name='{}_SKCLS_TEMP_SRC_GEO' .format(src_xform))[0]

        dst_shape = self.getBaseShape()
        dst_xform = mc.listRelatives(dst_shape, p=True)[0]
        dst_geom = mc.duplicate(dst_xform, name='{}_SKCLS_TEMP_DEST_GEO'.format(dest_xform))[0]

        # get weights in skincluster format
        #
        try:
            weight_list, infs = source_bs._getWeightsFromIndicies([int(target_index)], sparse=False)
        except:
            print 'failed to get weights'

        # build joints
        #
        joints = []

        mc.select(cl=True)
        joints.append(mc.joint(name=infs.values()[0]))
        
        # build temp skinclusters
        #
        src_skin= skcls.SkinCluster()
        src_skin.build('{}_TEMP_SRC_SKCLS'.format(source_bs.node), src_geom, joints, normalize=0)
        src_skin._setWeights(weight_list)

        dst_skin= skcls.SkinCluster()
        dst_skin.build('{}_TEMP_DEST_SKCLS'.format(self.node), dst_geom, joints, normalize=0)

        # transfer weight
        #
        spa = 0
        if sample_space is 'object':
            spa = 1           

        if sample_method == 'UV':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestPoint', ia='oneToOne', uv = ['map1', 'map1'], spa=spa)
        elif sample_method == 'closestPoint':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestPoint', ia='oneToOne', spa=spa)
        elif sample_method == 'closestComponent':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestComponent', ia='oneToOne', spa=spa)
        elif sample_method == 'rayCast':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='rayCast', ia='oneToOne', spa=spa)

        for index, inf in infs.items():
            weights = dst_skin._getInfluenceWeights([inf], sparse=False)
            self._setWeightsAtIndex(target_index, weights, sparse=False)

        mc.delete(dst_geom, src_geom, joints)


    def copyWeightsFromBlendshapeTargetBySpace(self, source_bs, source_targ, dest_targ, sample_method='UV', sample_space='world'):
        self._isSet()

        # get source/dest indices
        #
        src_indicies = source_bs.getTargetIndices(source_targ)
        dest_indicies = {}
        for index in src_indicies:
            dest_indicies[source_bs.getTargetWeightAlias(index)] = (self.getTargetIndexFromAlias(source_bs.getTargetWeightAlias(index)))

        # create temp geom
        #
        src_shape = source_bs.getBaseShape()
        src_xform = mc.listRelatives(src_shape, p=True)[0]
        src_geom = mc.duplicate(src_xform, name='{}_SKCLS_TEMP_SRC_GEO'.format(src_xform))[0]

        dst_shape = self.getBaseShape()
        dst_xform = mc.listRelatives(dst_shape, p=True)[0]
        dst_geom = mc.duplicate(dst_xform, name='{}_SKCLS_TEMP_DEST_GEO'.format(dst_xform))[0]

        # get weights in skincluster format
        #
        weight_list, infs = source_bs._getWeightsFromIndicies(src_indicies, sparse=False)

        # build joints
        #
        joints = []

        mc.select(cl=True)
        for index in sorted(src_indicies):
            mc.select(cl=True)
            joints.append(mc.joint(name=infs[index]))

        # build temp skinclusters
        #
        src_skin = skcls.SkinCluster()
        src_skin.build('{}_TEMP_SRC_SKCLS'.format(source_bs.node), src_geom, joints, normalize=0)
        src_skin._setWeights(weight_list)

        dst_skin = skcls.SkinCluster()
        dst_skin.build('{}_TEMP_DEST_SKCLS'.format(self.node), dest_geom, joints, normalize=0)

        # transfer weight
        #
        spa = 0
        if sample_space is 'object': 
            spa = 1                      

        if sample_method == 'UV':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestPoint', ia='oneToOne', uv = ['map1', 'map1'], spa=spa)
        elif sample_method == 'closestPoint':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestPoint', ia='oneToOne', spa=spa)
        elif sample_method == 'closestComponent':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='closestComponent', ia='oneToOne', spa=spa)
        elif sample_method == 'rayCast':
            mc.copySkinWeights(ss=src_skin.node, ds=dest_skin.node, noMirror=True, sa='rayCast', ia='oneToOne', spa=spa)

        for index, inf in infs.items():
            wght = dest_skin._getInfluenceWeights([inf], sparse=False)
            dest_ind =  dest_indicies[inf]
            self._setWeightsAtIndex(dest_ind, wght, sparse=False)

        mc.delete(dest_geom, src_geom, joints)
        
    #-----------------------------------------------------------------------------------------#
    
    def saveData(self, parent=None):
        self._isSet()

        root = ET.Element('blendShape', attrib={'name':repr(self.node)})
        if parent == None:
            xmlTree = ET.ElementTree(root)
        else:
            parent.append(root)
            
        weightData = self._getWeights()
        
        for base in weightData.keys():
            count = weightData[base]['count']
            base_shape = ET.Element('base', attrib={'name':repr(base), 'count':repr(count)})
            root.append(base_shape)
    
            targets = weightData[base]['targets']
            
            target_indices = {}; indices_lists = {}
            for target in targets.keys():
                index = targets[target]['index']
                try:
                    indices_list = indices_lists[target]
                except KeyError:
                    indices_list = indices_lists[target] = []
                      
                indices_list.append(index)                
                target_indices[index] = target            
            
            # get order based on lowest index number
            #
            order_dict = {}
            for target, indices_list in indices_lists.items():
                order_dict[min(indices_list)] = target
            
            # create index order
            #
            index_order = []
            for index_min in sorted(order_dict.keys()):
                target = order_dict[index_min]
                indices_list = indices_lists[target]
                index_order.extend(indices_list)
                
            for target_index in index_order:
                target = target_indices[target_index]

                index = targets[target]['index']
                target_shape = self.getTargetMeshAtIndex(targets[target]['index'])   
                
                normalise_id = self.getTargetNormaliseGroup(target_index)
                
                target_data = ET.Element('target')
                target_data.attrib['name']   = repr(target)
                target_data.attrib['index']  = repr(index)
                target_data.attrib['target'] = repr(target_shape)
                target_data.attrib['normal'] = repr(normalise_id)
                
                base_shape.append(target_data)

                target_shape = self.getTargetMeshAtIndex(targets[target]['index'])
                
                weights = targets[target]['weights']
                
                all_one = True
                weight_values = weights.values()
                if len(weight_values) == count:
                    for value in weight_values:
                        if value != 1: all_one = False
                else:
                    all_one = False
                
                if all_one is True:
                    target_data.attrib['all'] = repr(True)
                    continue
                
                for vert_index in weights.keys():
                    value = repr(weights[vert_index])
                    
                    weight = ET.Element('weight', attrib={'vertIndex':repr(vert_index), 'value':value})
                    target_data.append(weight)

        if parent is None:
            util_xml.write(xmlTree, self.node, 'blendshapes')        
        
    
    def _getWeights(self, format=None):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)
        
        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects)        
        
        data = {}

        if format == 'skinCluster':
            inf_dict = dict(zip(self.getAllTargetIndices(), self.getTargetAliases()))
            for baseIndex in range(base_objects.length()):
                dag_path = om.MDagPath.getAPathTo(base_objects[baseIndex])
                base = dag_path.partialPathName().split('|')[-1]
                geometry = om.MItGeometry(base_objects[baseIndex])
                vertex_count = geometry.count()

                index_list = om.MIntArray()
                blendshape_fn.weightIndexList(index_list)

                for vertex_index in range(vertex_count):
                    data[vertex_index] = {}

                    plug_weight = blendshape_fn.findPlug('weight')
                    for plug_index in range(index_list.length()):
                        plug_current_weight = plug_weight.elementByLogicalIndex(index_list[plug_index])

                        plug_input_target = blendshape_fn.findPlug('inputTarget')
                        plug_input_target = plug_input_target.elementByLogicalIndex(baseIndex)
                        plug_input_target_group = plug_input_target.child(0)
                        plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[plug_index])

                        plug_weights = plug_input_target_group.child(1)
                        vertex_weight = plug_weights.elementByLogicalIndex(vertex_index)
                        weight = vertex_weight.asFloat()
                        #if weight != 0.0:
                        inf = inf_dict[int(index_list[plug_index])]
                        data[vertex_index][inf] = weight

            data = (data, inf_dict)

        elif format is None:
            for baseIndex in range(base_objects.length()):
                dag_path = om.MDagPath.getAPathTo(base_objects[baseIndex])
                base = dag_path.partialPathName().split('|')[-1]
                geometry = om.MItGeometry(base_objects[baseIndex])
                vertex_count = geometry.count()

                data[base] = {}
                data[base]['count']   = vertex_count
                data[base]['targets'] = {}
                targets = data[base]['targets']

                index_list = om.MIntArray()
                blendshape_fn.weightIndexList(index_list)

                plug_weight = blendshape_fn.findPlug('weight')
                for plug_index in range(index_list.length()):
                    plug_current_weight = plug_weight.elementByLogicalIndex(index_list[plug_index])
                    alias_of_plug = blendshape_fn.plugsAlias(plug_current_weight)
                    targets[alias_of_plug] = {}
                    targets[alias_of_plug]['index'] = index_list[plug_index]

                    plug_input_target = blendshape_fn.findPlug('inputTarget')
                    plug_input_target = plug_input_target.elementByLogicalIndex(baseIndex)
                    plug_input_target_group = plug_input_target.child(0)
                    plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[plug_index])

                    plug_weights = plug_input_target_group.child(1)
                    targets[alias_of_plug]['weights'] = {}
                    for vertex_index in range(vertex_count):
                        vertex_weight = plug_weights.elementByLogicalIndex(vertex_index)
                        weight = vertex_weight.asFloat()
                        if weight != 0.0:
                            targets[alias_of_plug]['weights'][vertex_index] = weight
        
        return data
    
    
    def _getWeightsFromIndex(self, index, base_index=0, sparse=True):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)
        
        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects)
        
        weights = {}        

        geometry = om.MItGeometry(base_objects[base_index])
        vert_count = geometry.count()
        
        index_list = om.MIntArray()
        blendshape_fn.weightIndexList(index_list)
        
        if index > index_list.length(): 
            raise BlendShapeError("Index out of range.")
        
        plug_weight = blendshape_fn.findPlug('weight')

        plug_current_weight = plug_weight.elementByLogicalIndex(index_list[index])
        
        plug_input_target = blendshape_fn.findPlug('inputTarget')
        plug_input_target = plug_input_target.elementByLogicalIndex(base_index)
        plug_input_target_group = plug_input_target.child(0)
        plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[index])
        
        plug_weights = plug_input_target_group.child(1)
        for vert_index in range(vert_count):
            vert_weight = plug_weights.elementByLogicalIndex(vert_index)
            weight = vert_weight.asFloat()
            if sparse is False:
                weights[vert_index] = weight
            elif weight != 0.0:
                weights[vert_index] = weight
        
        return weights

    def _getWeightsFromIndicies(self, indicies, base_index=0, sparse=True):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)

        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects)

        weights = {}

        geometry = om.MItGeometry(base_objects[base_index])
        vert_count = geometry.count()

        index_list = om.MIntArray()
        blendshape_fn.weightIndexList(index_list)
        data ={}
        inf_dict = {}
        for vert_index in range(vert_count):
            data[vert_index]={}
            for index in indicies:
                influence = self.getTargetWeightAlias(index)
                inf_dict[index] = influence
                if index > index_list.length():
                    raise BlendShapeError("Index out of range.")

                plug_weight = blendshape_fn.findPlug('weight')

                plug_current_weight = plug_weight.elementByLogicalIndex(index_list[index])

                plug_input_target = blendshape_fn.findPlug('inputTarget')
                plug_input_target = plug_input_target.elementByLogicalIndex(base_index)
                plug_input_target_group = plug_input_target.child(0)
                plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[index])

                plug_weights = plug_input_target_group.child(1)

                vert_weight = plug_weights.elementByLogicalIndex(vert_index)
                weight = vert_weight.asFloat()
                if sparse is False:
                    data[vert_index][influence] = weight
                elif weight != 0.0:
                    data[vert_index][influence] = weight

        data = (data, inf_dict)
        return data

    #-----------------------------------------------------------------------------------------#
    
    def loadData(self, root=None):
        self._isSet()
        
        if root == None:
            try:
                xmlTree = util_xml.read(self.node, 'blendshapes', inherit=True)
            except util_dataFile.util_dataFileError:
                return False
            root = xmlTree.getroot()
        
        data = {}
        for base in root:
            if base.tag != 'base': continue
            base_name = eval(base.attrib['name'])
            vert_count = eval(base.attrib['count'])
            data[base_name] = {}
            data[base_name]['count'] = vert_count
            data[base_name]['targets'] = {}
            targets = data[base_name]['targets']
            
            for target in base:
                if target.tag != 'target': continue
                targetName = eval(target.attrib['name'])
                targetIndex = eval(target.attrib['index'])
                targets[targetName] = {}
                targets[targetName]['index'] = targetIndex
                targets[targetName]['weights'] = {}
                weights = targets[targetName]['weights'] 
                
                if len(target) == 0:
                    try:
                        # if all weights should be set to 1.0
                        #
                        target.attrib['all']
                        for index in range(eval(base.attrib['count'])):
                            weights[index] = 1.0
                    except KeyError:
                        # all weights set to 0
                        #
                        pass                        
                else:                
                    for weight in target:
                        if weight.tag != 'weight': continue
                        vertex_index = eval(weight.attrib['vertIndex'])
                        value     = eval(weight.attrib['value'])
                        weights[vertex_index] = value
        
        self._setWeights(data)

        return True
    


    def _setWeights(self, data):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)
        
        # get number of weights lists
        #
        index_list = om.MIntArray()
        blendshape_fn.weightIndexList(index_list)
        
        # get all base objects
        #
        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects)
        
        # get all base shapes data
        #
        bases = {}
        for baseIndex in range(base_objects.length()):
            dag_path = om.MDagPath.getAPathTo(base_objects[baseIndex])
            base_shape = dag_path.partialPathName().split('|')[-1]
            geometry = om.MItGeometry(base_objects[baseIndex])
            vertex_count = geometry.count()
            bases[base_shape] = {}
            bases[base_shape]['index'] = baseIndex
            bases[base_shape]['count'] = vertex_count
        
        # compare base shape vert count to data vert count
        #
        base_shapes = []
        for base_shape in list(set(data.keys()).intersection(set(bases.keys()))):
            if bases[base_shape]['count'] != data[base_shape]['count']:
                printError("Base Shape '{}' vert count does not match.".format(base_shape))
                continue
            index = bases[base_shape]['index']
            count = bases[base_shape]['count']
            base_shapes.append((index, base_shape, count))

        # loop over bases
        #
        for baseIndex, base_shape, baseCount in base_shapes:          
            geometry = om.MItGeometry(base_objects[baseIndex])
            vertex_count = geometry.count()
            
            targets = data[base_shape]['targets']                       
            plug_weight = blendshape_fn.findPlug('weight')            
      
            # get target alias and store with weight plug
            # 
            plug_weights_alias = {}
            for plug_index in range(index_list.length()):
                plug_current_weight = plug_weight.elementByLogicalIndex(index_list[plug_index])
                alias_of_plug = blendshape_fn.plugsAlias(plug_current_weight)
                  
                plug_input_target = blendshape_fn.findPlug('inputTarget')
                plug_input_target = plug_input_target.elementByLogicalIndex(0)
                plug_input_target_group = plug_input_target.child(0)
                plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[plug_index])
                  
                plug_weights = plug_input_target_group.child(1)
                plug_weights_alias[alias_of_plug] = plug_weights

            for target in targets.keys():
                # get target weights by alias
                #
                try:
                    plug_weights = plug_weights_alias[target]
                except Exception:
                    continue
                
                # if vertex index is in weights, set weight value, otherwise 0.0
                #
                weights = targets[target]['weights']
                weightVerts = set(weights.keys())
                for vertex_index in range(vertex_count):
                    vertex_weight = plug_weights.elementByLogicalIndex(vertex_index)
                    if vertex_index in weightVerts:
                        vertex_weight.setFloat(weights[vertex_index])
                    else:
                        vertex_weight.setFloat(0.0)


    def _setWeightsAtIndex(self, index, weights, base_index=0, sparse=True):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)
        
        # get number of weights lists
        #
        index_list = om.MIntArray()
        blendshape_fn.weightIndexList(index_list)
        
        # get all base objects
        #
        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects)
        
        # get base shape vert_count
        #
        geometry = om.MItGeometry(base_objects[base_index])
        vert_count = geometry.count()

        # loop over bases
        #       
        plug_weight = blendshape_fn.findPlug('weight')
  
        # get target index weight plug
        #
        plug_current_weight = plug_weight.elementByLogicalIndex(index_list[index])
          
        plug_input_target = blendshape_fn.findPlug('inputTarget')
        plug_input_target = plug_input_target.elementByLogicalIndex(0)
        plug_input_target_group = plug_input_target.child(0)
        plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[index])
          
        plug_weights = plug_input_target_group.child(1)
            
        # if vertex index is in weights, set weight value, otherwise if sparse set to 0.0
        #
        weight_verts = set(weights.keys())
        for vert_index in range(vert_count):
            vert_weight = plug_weights.elementByLogicalIndex(vert_index)
            if vert_index in weight_verts:
                vert_weight.setFloat(weights[vert_index])
            elif sparse is True:
                vert_weight.setFloat(0.0)


    def _floodWeights(self, targets, value=1.0, base_index=0):
        selection_list = om.MSelectionList()
        selection_list.add(self.node)
        blendshape = om.MObject()
        selection_list.getDependNode(0, blendshape)
        blendshape_fn = oma.MFnBlendShapeDeformer(blendshape)
        
        index_list = om.MIntArray()
        blendshape_fn.weightIndexList(index_list)
        
        base_objects = om.MObjectArray()
        blendshape_fn.getBaseObjects(base_objects) 
         
        geometry = om.MItGeometry(base_objects[base_index])
        vert_count = geometry.count()
                      
        plug_weight = blendshape_fn.findPlug('weight')            
  
        plug_weights_alias = {}
        for plug_index in range(index_list.length()):
            plug_current_weight = plug_weight.elementByLogicalIndex(index_list[plug_index])
            alias_of_plug = blendshape_fn.plugsAlias(plug_current_weight)
              
            plug_input_target = blendshape_fn.findPlug('inputTarget')
            plug_input_target = plug_input_target.elementByLogicalIndex(0)
            plug_input_target_group = plug_input_target.child(0)
            plug_input_target_group = plug_input_target_group.elementByLogicalIndex(index_list[plug_index])
              
            plug_weights = plug_input_target_group.child(1)
            plug_weights_alias[alias_of_plug] = plug_weights
            
        for target in targets:
            try:
                plug_weights = plug_weights_alias[target]
            except Exception:
                continue
            
            for vert_index in range(vert_count):
                vert_weight = plug_weights.elementByLogicalIndex(vert_index)
                vert_weight.setFloat(value)
                 
             