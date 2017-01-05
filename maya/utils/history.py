import maya.cmds as mc

import cg_inventor.maya.utils.generic as util_generic

callbackSetup   = util_generic.callbackSetup
callbackCounter = util_generic.callbackCounter


class HistoryError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

def getNodesWithHistory(nodes, callback=None):
    skip_nodes    = set(['initialShadingGroup'])
    history_nodes = set(())
    
    if callback: counter, increment = callbackSetup(len(nodes))
    
    for node in nodes:
        history = mc.listHistory(node, il=2, pdo=True)
        
        if callback:
            callback(callbackCounter(counter, increment))

        if not history:
            continue
            
        if len(history) == 1 and history[0] in skip_nodes:
            continue

        history_nodes.add(node)

    return list(history_nodes)


def deleteHistory(nodes):
    nodes = mc.ls(nodes)
    _deleteHistory(nodes)
        

def _deleteHistory(nodes):
    try:
        mc.delete(nodes, ch=True)
    except Exception as e:
        raise HistoryError(str(e))
                

#--------------------------------------------------------------------------------------------------#
