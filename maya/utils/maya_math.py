import maya.cmds as mc

class UtilityNode(object):
    NODE_LOOKUP = {}
    
    PLUS_MINUS_AVERAGE = 'plusMinusAverage'
    NODE_LOOKUP['sum'] = (PLUS_MINUS_AVERAGE, 1)
    NODE_LOOKUP['subtract'] = (PLUS_MINUS_AVERAGE, 2)
    NODE_LOOKUP['average'] = (PLUS_MINUS_AVERAGE, 3)
    
    MULTIPLY_DIVIDE = 'multiplyDivide'
    NODE_LOOKUP['multiply'] = (MULTIPLY_DIVIDE, 1)
    NODE_LOOKUP['divide'] = (MULTIPLY_DIVIDE, 2)
    NODE_LOOKUP['power'] = (MULTIPLY_DIVIDE, 3)
    
    
    def __init__(self, operation_type=None, data=None):
        node_type, operation_value = UtilityNode.NODE_LOOKUP.get(operation_type, (None, None))
        
        self.node_type = node_type
        self.node = mc.createNode(node_type)
        mc.setAttr('{}.operation'.format(self.node), operation_value)


# ------------------------------------------------------------------------------------------------ #

class UtilityNode(object):
    NODE_LOOKUP = {}
    
    PLUS_MINUS_AVERAGE = 'plusMinusAverage'
    NODE_LOOKUP['sum'] = (PLUS_MINUS_AVERAGE, 1)
    NODE_LOOKUP['subtract'] = (PLUS_MINUS_AVERAGE, 2)
    NODE_LOOKUP['average'] = (PLUS_MINUS_AVERAGE, 3)
    
    MULTIPLY_DIVIDE = 'multiplyDivide'
    NODE_LOOKUP['multiply'] = (MULTIPLY_DIVIDE, 1)
    NODE_LOOKUP['divide'] = (MULTIPLY_DIVIDE, 2)
    NODE_LOOKUP['power'] = (MULTIPLY_DIVIDE, 3)    
    
    
    def __init__(self, operation_type=None, data=None):
        node_type, operation_value = UtilityNode.NODE_LOOKUP.get(operation_type, (None, None))
        
        self.node_type = node_type
        self.node = mc.createNode(node_type)
        mc.setAttr('{}.operation'.format(self.node), operation_value)
        
        if isinstance(data, (str, unicode)):
            self._attributeConnect(data)
         
        elif isinstance(data, UtilityNode):
            self._nodeConnect(data)
            
        elif hasattr(data, '__iter__') or isinstance(data, (int, float)):
            self._set(data)
        
        else:
            raise RuntimeError("Do not recognize data type.")
            
    
    def _attributeConnect(self, data):`
        if mc.attributeQuery(data, multi=True):
            self.data_range = mc.getAttr(data, s=True)
            for data_axis, axis in zip('XYZ', 'xyz'):
                data_attr = '{}{}'.format(data, data_axis)
                if self.node_type == UtilityNode.PLUS_MINUS_AVERAGE:                    
                    node_attr = '{}.input3D[0].input3D{}'.format(self.node, axis)
                elif self.node_type == UtilityNode.MULTIPLY_DIVIDE:
                    node_attr = '{}.input1{}'.format(self.node, data_axis) 
                mc.connectAttr(data_attr, node_attr)
                    
            return

        self.data_range = 1
        if self.node_type == UtilityNode.PLUS_MINUS_AVERAGE:
            mc.connectAttr(data, '{}.input1D[0]'.format(self.node))
        elif self.node_type == UtilityNode.MULTIPLY_DIVIDE:
            mc.connectAttr(data, '{}.input1X'.format(self.node))
    
    
    def _nodeConnect(self, data):
        self.data_range = data.data_range
    
    
    def _set(self, data):
        if isinstance(data, (int, float)):
           data = [data]
                
        self.data_range = len(data)
        
        if self.node_type == UtilityNode.PLUS_MINUS_AVERAGE:
            if self.data_range == 1:
                mc.setAttr('{}.input1D[0]'.format(self.node), data[0])
                return
            
            attr = '{0}.input{1}D[0].input{1}D{2}'.format(self.node, self.data_range, axis)                            
            for index, axis in zip(range(self.data_range), 'xyz'):
                mc.setAttr(attr, data[index])
                
        elif self.node_type == UtilityNode.MULTIPLY_DIVIDE:
            for index, axis in zip(range(self.data_range), 'XYZ'):
                mc.setAttr('{}.input1{}'.format(self.node, axis), data[index])
        
        
    def __add__(self, arg):
        print 'sum', arg
        new_node = UtilityNode('sum', arg)
        
        if isinstance(arg, (int, float)):
            if self.data_range == 1:
                mc.setAttr('{}.input1D[1]'.format(new_node), arg)
            
        elif isinstance(arg, UtilityNode):
            if arg.node_type == UtilityNode.PLUS_MINUS_AVERAGE:
                mc.connectAttr('{}.output1D'.format(arg), '{}.input1D[1]'.format(new_node))
            
        return new_node
    

    def __sub__(self, arg):
        if isinstance(arg, (int, float)):
            new_node = UtilityNode('subtract')
            mc.connectAttr(self.attr, '{}.input1D[0]'.format(new_node))
            mc.setAttr('{}.input1D[1]'.format(new_node), arg)
            
        return new_node
    
    
    @property
    def inputs_ports(self):
        if self.node_type == UtilityNode.PLUS_MINUS_AVERAGE:
            if self.data_range == 1:
                return '{}.input1D[0]'.format(node)

            size = self.data_range
            attr = '{0}.input{1}D[0]'
            return ['{}.input{1}D{2}'.format(attr, size, axis) for axis in 'xyz'[:size]]
    
        if self.node_type == UtilityNode.MULTIPLY_DIVIDE:
            return ['{}.input1X{}'.format(self.node, axis) for axis in 'XYZ'[:size]]
        
            
    def __str__(self):
        return self.node
        
a = UtilityNode('sum', 5)
print a.inputs()