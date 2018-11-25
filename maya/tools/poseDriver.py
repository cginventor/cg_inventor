import maya.cmds as mc

drivers = ['pSphere1', 'pSphere2', 'pSphere3']
driven = 'pCube1'

driven_start = 2.0
driven_end = mc.getAttr('{}.ty'.format(driven))

bw = mc.createNode('blendWeighted', n='test_BW')

driver_weight = (driven_end - driven_start) / len(drivers)

for index, driver in enumerate(drivers):
    driver_value = mc.getAttr('{}.ty'.format(driver))
    mc.setAttr('{}.weight[{}]'.format(bw, index), driver_weight / driver_value)
    mc.connectAttr('{}.ty'.format(driver), '{}.input[{}]'.format(bw, index))
    
mc.setAttr('{}.weight[{}]'.format(bw, len(drivers)), driven_start)
mc.setAttr('{}.input[{}]'.format(bw, len(drivers)), 1.0)

mc.connectAttr('{}.output'.format(bw), '{}.ty'.format(driven))