import PyQt4.QtCore as qc
import PyQt4.QtGui as qg



class TLabel(qg.QLabel):
    def __init__(self):
        qg.QLabel.__init__(self)
        
        
    def paintEvent(self, event):
        qg.QLabel.paintEvent(self, event)