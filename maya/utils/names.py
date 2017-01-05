import maya.cmds as mc

import cg_inventor.maya.utils.generic as util_gen

# undo decorator
#
undo = util_gen.undo


#--------------------------------------------------------------------------------------------------#

def intToAlpha(integer, capital=False, base=26):
    '''
        Turn an integer into letter. a-z then doubles, aa-zz etc.
        
    args:
        integer : a int value for convert
    
    kwargs:
        captial = False : if True returns uppercase letters.
        base    = 26    : the base number for looping over. Maximum is 26.
    '''
    
    if 1 > base > 26:
        raise ValueError("Base [%s] invalid. Must be an int value of 1-26." %base)
    
    return _intToAlpha(integer, capital, base)


def _intToAlpha(integer, capital=False, base=26):
    # calculate base
    #
    base_power = 0
    base_start = 0
    base_end = 0
    while integer >= base_end:
        base_power += 1
        base_start = base_end
        base_end += pow(base, base_power)
    base_index = integer - base_start
    
    # determine alpha
    #
    alphas = [chr(97)] * base_power; index = 0
    while True:
        letter_index = base_index % base
        alphas[index] = chr(97 + letter_index)
        base_index /= base
        index += 1
        if not base_index: break
    
    if capital:
        return ''.join(alphas[::-1]).upper()
    return ''.join(alphas[::-1])
            
#--------------------------------------------------------------------------------------------------#

def getRepeatedNames():
    nodes = mc.ls()

    repeated_names = set(())
    for node in nodes:
        if '|' in node:
            repeated_names.add(node)
            
    return list(repeated_names)

#--------------------------------------------------------------------------------------------------#

def getNodesInNamespace():
    return mc.ls('*:*')


def removeAllNamespaces():        
    namespaces = getAllNamespaces()

    for namespace in namespaces:
        mc.namespace(f=True, mv=(namespace, ':'))
        mc.namespace(rm=namespace)


def removeNamespace(namespace):
    mc.namespace(f=True, mv=(namespace, ':'))
    mc.namespace(rm=namespace)
    
    
def getAllNamespaces():
    namespaces = mc.namespaceInfo(lon=True)
    namespaces.remove('UI')
    namespaces.remove('shared')
    
    return namespaces


def getEmptyNamespace():
    empty_namespaces = set(())
    namespaces = getAllNamespaces()
    
    for namespace in namespaces:
        if not len(mc.ls('%s:*' %namespace)):
            empty_namespaces.add(namespace)

    return list(empty_namespaces)


def removeEmptyNamespaces():
    empty_namespaces = getEmptyNamespace()

    for empty_namespace in empty_namespaces:
        mc.namespace(rm=empty_namespace)    
        
#--------------------------------------------------------------------------------------------------#

@undo
def rename(nodes, text, prefix=None, suffix=None, padding=0, letters=False, capital=False):    
    if prefix: text = '%s_%s' %(prefix, text)
    
    if len(nodes) == 1:
        if suffix:
            new_name = '%s_%s' %(text, suffix)
        else:
            new_name = text
        
        if not mc.objExists(new_name):
            nodes[0] = mc.rename(nodes[0], '__tmp__')
            mc.rename(nodes[0], new_name)
            return new_name    
    
    new_node_names = []; index = 1    
    for node in nodes:
        new_node_names.append(mc.rename(node, '__tmp__'))
    
    new_nodes = []
    for node_name in new_node_names:
        new_name = _findAvaliableName(text, suffix, index, padding, letters, capital)
        new_nodes.append(mc.rename(node_name, new_name))        
    
    return new_nodes
        


def _findAvaliableName(name, suffix, index, padding, letters=False, capital=False):
    test_name = name
    if index > 0:
        if letters:
            letter = intToAlpha(index-1, capital=capital)
            test_name = '%s_%s' %(name, letter)
        else:
            test_name = '%s_%s' %(name, str(index).zfill(padding))
        
    if suffix:
        test_name = '%s_%s' %(test_name, suffix)
        
    if mc.objExists(test_name):
        return _findAvaliableName(name, suffix, (index+1), padding, letters, capital)
    else:
        return test_name

#--------------------------------------------------------------------------------------------------#

@undo
def replace(nodes, from_text, to_text):
    shapes = mc.ls(nodes, s=True)
        
    new_nodes_names = []
    for node in nodes:
        if not from_text in node: continue
        if node in shapes: continue
        try:
            new_nodes_names.append((node, mc.rename(node, '__tmp__')))
        except Exception:
            pass
    
    for shape in shapes:
        if not from_text in shape: continue
        try:
            new_nodes_names.append((shape, mc.rename(shape, shape.replace(from_text, '__tmp__'))))
        except Exception:
            pass

    new_names = []
    for name, new_node in new_nodes_names:
        name = name.replace(from_text, to_text)
        new_name = _findAvaliableName(name, None, 0, 0)
        new_names.append(mc.rename(new_node, new_name))
    
    return new_names