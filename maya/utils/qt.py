import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import maya.OpenMayaUI as mui
import sip

#--------------------------------------------------------------------------------------------------#

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    window = sip.wrapinstance(long(ptr), qc.QObject)
    return window

#--------------------------------------------------------------------------------------------------#

def getFocusWidget():
    return qg.qApp.focusWidget()


def getWidgetAtMouse():
    currentPos = qg.QCursor().pos()
    return qg.qApp.widgetAt(currentPos)

#--------------------------------------------------------------------------------------------------#

def getFullName(widget):
    if not isinstance(widget, qc.QObject):
        raise TypeError('Non QObject received.')

    return mui.MQtUtil.fullName(long(sip.unwrapinstance(widget)))


def getWidgetFromName(name):
    widget = mui.MQtUtil.findControl(name)
    return sip.wrapinstance(long(widget), qc.QObject)

#--------------------------------------------------------------------------------------------------#
