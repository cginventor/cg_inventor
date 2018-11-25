import maya.cmds as mc


class Tracker(object):
    def __init__(self):
        self.attributes = {}
        self.key_range = 50
        
    
    def store(self):
        attributes = mc.channelBox('mainChannelBox', q=True, sma=True)
        if attributes:
            nodes = mc.ls(sl=True, dep=True)
            if nodes:
                self._storeAttributes(nodes, attributes)
        
        attributes = mc.channelBox('mainChannelBox', q=True, sha=True)
        if attributes:
            nodes = mc.channelBox('mainChannelBox', q=True, hol=True)
            if nodes:
                self._storeAttributes(nodes, attributes)

        attributes = mc.channelBox('mainChannelBox', q=True, soa=True)
        if attributes:
            nodes = mc.channelBox('mainChannelBox', q=True, ool=True)
            if nodes:
                self._storeAttributes(nodes, attributes)
        
    
    def _storeAttributes(self, nodes, attributes):
        for node in nodes:
            for attribute in attributes:                
                if not mc.attributeQuery(attribute, node=node, ex=True):
                    continue
                
                attr = '{}.{}'.format(node, attribute)
                if attr in self.attributes.keys():
                    continue
                
                self.attributes[attr] = TrackedAttribute(attr, self.key_range)
                
    
    def key(self, index):
        index = min(max(index, 0), self.key_range-1)
        for attribute in self.attributes.values():
            attribute.key(index)
            
    
    def set(self, index):
        index = min(max(index, 0), self.key_range-1)
        for attribute in self.attributes.values():
            attribute.set(index)
            
    
    def clear(self):
        for attribute in self.attributes.values():
            attribute.clear()

#--------------------------------------------------------------------------------------------------#

class TrackedAttribute(object):
    def __init__(self, attribute, key_range=50):
        self.attribute = attribute
        
        self.key_range = key_range       
        self.clear()
        
    
    def key(self, index):    
        self.values[index] = mc.getAttr(self.attribute)
        self.keys.append(index)
        self.keys.sort()
        
        self.update()
        
    
    def remove(self, index):
        if index in self.values.keys():
            return
        
        del(self.values[index])
        
        self.update()
        
    
    def clear(self):
        self.values = [0.0 for _ in range(self.key_range)]
        self.keys = []      
        
    
    def update(self):
        if len(self.keys) == 0:
            return
        
        if len(self.keys) == 1:
            value = self.values[self.keys[0]]
            self.values = [value for _ in range(self.key_range)]
            return
        
        lowest_key = self.keys[0]
        lowest_value = self.values[lowest_key]
        for index in range(lowest_key):
            self.values[index] = lowest_value
            
        for index, start_key_index in enumerate(self.keys[:-1]):            
            start_value = self.values[start_key_index]
            
            end_key_index = self.keys[index + 1]
            end_value = self.values[end_key_index]
            
            index_range = end_key_index - start_key_index
            value_range = end_value - start_value
            
            value_interval = value_range / index_range
            for index in range(index_range):
                self.values[index + start_key_index] = (value_interval * index) + start_value                      
        
        highest_key = self.keys[-1]
        highest_value = self.values[highest_key]
        for index in range(highest_key, self.key_range):
            self.values[index] = highest_value
            
    
    def set(self, index):
        mc.setAttr(self.attribute, self.values[index])
                
            
            
        