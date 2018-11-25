import maya.cmds as mc

driver_sphere = mc.sphere(p=(0,0,0), ax=(0,1,0), ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=8, nsp=4, ch=False)[0]
driver_sphere = mc.rename(driver_sphere, 'driver_sphere')

plane_grp = mc.createNode('transform', n='plane_GRP')
crv_grp = mc.createNode('transform', n='curve_GRP')

for index in range(9):    
    plane = mc.nurbsPlane(p=(0,0,0), ax=(0,1,0), w=10, lr=1, d=3, u=1, v=1, ch=False)
    plane = mc.rename(plane, 'plane_{}'.format(index))
    mc.parent(plane, plane_grp)
    mc.setAttr('{}.rz'.format(plane), 20*index)
    
    crv = mc.curve(d=1, p=((0,1,0), (0,-1,0)), k=(0,1))
    crv = mc.rename(crv, 'curve_{}'.format(index))
    mc.parent(crv, crv_grp)
    
    intersect = mc.createNode('intersectSurface', n='eye_{}_INT'.format(index))
    
    mc.connectAttr('{}.worldSpace[0]'.format(driver_sphere), '{}.inputSurface1'.format(intersect))
    mc.connectAttr('{}.worldSpace[0]'.format(plane), '{}.inputSurface2'.format(intersect))
    
    mc.connectAttr('{}.output3dCurve[0]'.format(intersect), 'curve_Shape{}.create'.format(index))