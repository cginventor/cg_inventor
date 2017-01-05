import maya.cmds as mc

#------------------------------------------------------------------------------#

def parent(parent, children):
    if not hasattr(children, '__iter__'):
        children = [children]

    for child in children:
        mc.setKeyframe(child, at=('t','r'), itt='linear', ott='linear')
        cnst_name = '__%s__%s_prnt' %(parent, child)
        mc.parentConstraint(parent, child, name=cnst_name, mo=True)

    current_time  = mc.currentTime(q=True)
    previous_time = current_time - 1

    mc.setKeyframe(child, t=current_time,  at='blendParent1', value=1)
    mc.setKeyframe(child, t=previous_time, at='blendParent1', value=0)


def bake(parent, child):
    current_time = mc.currentTime(q=True)
    previous_key = mc.findKeyframe(timeSlider=True, which='previous')

    mc.bakeResults(child, time=(previous_key, current_time),
                   sm=True, sb=1, dic=True, pok=True,
                   sac=False, ral=False, bol=False,
                   cp=False, s=True,
                   at=('tx','ty','tz','rx','ry','rz'))
    mc.delete('__%s__%s_prnt' %(parent, child))

#------------------------------------------------------------------------------#

def kk_dp():
    if mc.window('kk_dp', exists=True):
        mc.deleteUI('kk_dp', window=True)

    window = mc.window('kk_dp', title='kk_dp', rtf=1)
    mc.columnLayout(adjustableColumn=True)
    mc.frameLayout(label='parent   |   Child', borderStyle='etchedIn')

    parent = mc.textFieldButtonGrp('pt', adjustableColumn=1, columnAlign=(1, 'left'), buttonCommand='anim.getParent()', text='Parent', buttonLabel='<< ')
    child  = mc.textFieldButtonGrp('ct', adjustableColumn=1, columnAlign=(1, 'left'), buttonCommand='anim.getChild()',  text='Child',  buttonLabel='<< ')

    mc.rowLayout(numberOfColumns=2)

    mc.button(w=150, c='anim.kkparent()',   label='parent')
    mc.button(w=150, c='anim.kkunparent()', label='unparent')

    mc.showWindow('kk_dp')



def simulation():
    mc.window('kksimulation', title='simulation', w=150, h=50)
    mc.columnLayout(adjustableColumn=True)
    mc.button(c='anim.kkbake()', label='bake', h=50)
    mc.button(c='anim.kkdrop()', label='drop')

    mc.showWindow('kksimulation')



def getParent():
    sel = mc.ls(sl=True)[0]
    mc.textFieldButtonGrp('pt', e=True, text=sel)



def getChild():
    sel = mc.ls(sl=True)[0]
    mc.textFieldButtonGrp('ct', e=True, text=sel)



def kkparent():
    kpt = mc.textFieldButtonGrp('pt', q=True, text=True)
    kct = mc.textFieldButtonGrp('ct', q=True, text=True)

    mc.select(kct)
    mc.setKeyframe(attribute=('t','r'), inTangentType='linear', outTangentType='linear')
    mc.select(cl=True)

    mc.parentConstraint(kpt, kct, name='kk_____con_____parent', maintainOffset=True)

    ctime = mc.currentTime(q=True)
    calcu = ctime - 1
    bp = '%s.blendParent1' %kct
    mc.setKeyframe(bp)
    mc.currentTime(calcu)
    mc.setAttr(bp, 0)
    mc.setKeyframe(bp)
    mc.currentTime(ctime)



def kkunparent():
    kct = mc.textFieldButtonGrp('ct', q=True, text=True)
    mc.select(kct, r=True)
    simulation()



def kkbake():
    currentTime = mc.currentTime(q=True)
    previousKey = mc.findKeyframe(timeSlider=True, which='previous')
    simnumb = '%s:%s' %(previousKey, currentTime)
    print simnumb
    mc.bakeResults(time=(previousKey, currentTime), simulation=True, sampleBy=1,
        disableImplicitControl=True, preserveOutsideKeys=True,
        sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False, controlPoints=False, shape=True,
        at=('rx','ry','rz','tx','ty','tz'))
    mc.delete('kk_____con_____parent')
    delsimulation();



def kkdrop():
    mc.delete('kk_____con_____parent')
    delsimulation()



def delsimulation():
    mc.deleteUI('kksimulation', window=True)
