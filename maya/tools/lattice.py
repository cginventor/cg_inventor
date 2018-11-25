import maya.cmds as mc
from pymel.core.datatypes import Vector


base = mc.createNode('lattice', n='baseShape')
deformed = mc.createNode('lattice', n='deformedShape')

eye = mc.createNode('csEye')

mc.connectAttr()


for lat in (base, deformed):
    for div in 'uts':
        mc.setAttr('{}.{}Divisions'.format(lat, div), 2)

for s in range(2):
    for t in range(2):
        for u in range(2):
            point = '{}.pt[{}][{}][{}]'.format(deformed, s, t, u)
            vector = Vector(mc.xform(point, q=True, t=True, ws=True))
            vector *= 2
            mc.xform(point, t=(vector.x, vector.y, vector.z), ws=True)
            break
        break
    break
            
sphere = mc.polySphere(r=0.5, sx=20, sy=20, ax=(0,1,0), cuv=2, ch=0)[0]

base_points = [[None, None],[None, None]],[[None, None],[None, None]]
for s in range(2):
    for t in range(2):
        for u in range(2):
            pos = mc.xform('{}.pt[{}][{}][{}]'.format(base, s, t, u), q=True, t=True, ws=True)
            base_points[s][t][u] = Vector(pos)

length = base_points[1][1][1] - base_points[0][0][0]


def smoothstep(start, end, value):
    #return min(max((value - start)/(end - start), 0.0), 1.0)
    return (value - start)/(end - start)


all_verts = []
for index in range(mc.polyEvaluate(sphere, v=True)):
    pos = Vector(mc.xform('{}.vtx[{}]'.format(sphere, index), q=True, t=True, ws=True))
    all_verts.append(pos)
    
s = base_points[0][0][0][0], base_points[1][0][0][0]
t = base_points[0][0][0][1], base_points[0][1][0][1]
u = base_points[0][0][0][2], base_points[0][0][1][2]

weighting = {}
for vert_index, vertex in enumerate(all_verts):
    x1 = smoothstep(s[0], s[1], vertex[0])
    x0 = 1.0 - x1
    y1 = smoothstep(t[0], t[1], vertex[1])
    y0 = 1.0 - y1
    z1 = smoothstep(u[0], u[1], vertex[2])
    z0 = 1.0 - z1
    
    weights = []; total = 0
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                w = x * y * z
                weights.append(w)
                total += w
    
    scale = 1.0 / total
    weighting[vert_index] = [w * scale for w in weights]

all_vectors = []
for x in range(2):
    for y in range(2):
        for z in range(2):
            deform_pos = Vector(mc.xform('{}.pt[{}][{}][{}]'.format(deformed, x, y, z), q=True, t=True, ws=True))
            base_pos = base_points[x][y][z]
            if deform_pos == base_pos:
                all_vectors.append(None)
                continue
                
            all_vectors.append(deform_pos - base_pos)
            
for vert_index, vertex in enumerate(all_verts):
    deform_vector = Vector(0,0,0)
    weights = weighting[vert_index]
    
    if vert_index == 276:
        print weights
    
    for vector_index, vector in enumerate(all_vectors):
        if vector is None:
            continue
        
        deform_vector += weights[vector_index] * vector
    
    if deform_vector.length() == 0.0:
        continue
    
    new_vector = vertex + deform_vector
    
    mc.xform('{}.vtx[{}]'.format(sphere, vert_index), ws=True, t=(new_vector[0], new_vector[1], new_vector[2]))
            
import maya.cmds as mc

mc.loadPlugin( 'C:\\Users\\Mike\\Documents\\maya\\scripts\\cg_inventor\\maya\\plugins\\csEye.py' )

eye = mc.createNode('csEye')

lattice = mc.createNode('lattice')
for axis in 'stu':
    mc.setAttr('{}.{}Divisions'.format(lattice, axis), 2)
mc.connectAttr('{}.latticeOutput'.format(lattice), '{}.lattice'.format(eye))
mc.connectAttr('{}.worldMatrix'.format(lattice), '{}.latticeMatrix'.format(eye))

off = mc.createNode('joint', n='off')
jnt = mc.createNode('joint', n='aim', p=off)

mc.connectAttr('{}.worldMatrix'.format(jnt), '{}.aimMatrix'.format(eye))
    
#surface = mc.createNode('nurbsSurface')
#mc.connectAttr('{}.surface'.format(eye), '{}.create'.format(surface))

eyeball = mc.createNode('transform', n='eyeball')
eyeball_shape = mc.createNode('mesh', n='eyeballShape', p=eyeball)
mc.sets(eyeball_shape, e=True, forceElement='initialShadingGroup')
mc.connectAttr('{}.eyeball'.format(eye), '{}.inMesh'.format(eyeball_shape))

iris = mc.createNode('transform', n='iris')
iris_shape = mc.createNode('mesh', n='irisShape', p=iris)
mc.connectAttr('{}.iris'.format(eye), '{}.inMesh'.format(iris_shape))

pupil = mc.createNode('transform', n='pupil')
pupil_shape = mc.createNode('mesh', n='pupilShape', p=pupil)
mc.connectAttr('{}.pupil'.format(eye), '{}.inMesh'.format(pupil_shape))