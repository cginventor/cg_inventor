import PyQt4.QtCore as qc
import PyQt4.QtGui as qg



class TDialog(qg.QDialog):
    def __init__(self):
        qg.QDialog.__init__(self)
        
        
    def paintEvent(self, event):
        qg.QDialog.paintEvent(self, event)