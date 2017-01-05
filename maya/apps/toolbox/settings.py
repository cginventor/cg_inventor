import PyQt4.QtCore as qc
import PyQt4.QtGui  as qg

from functools import partial

import cg_inventor.sys.lib.qt.base                as base
import cg_inventor.sys.lib.qt.misc.splitter       as splitter
import cg_inventor.sys.lib.qt.buttons.icon_button as icon_button
import cg_inventor.maya.lib.images.icons_rc

DEFAULT_WINDOW_WIDTH  = 500
DEFAULT_WINDOW_HEIGHT = 300

WINDOW_NAME = 'Settings and Preferences'

# ------------------------------------------------------------------------------------------------ #

class SettingsError(Exception):
    pass

# ------------------------------------------------------------------------------------------------ #

class Settings(qg.QDialog, base.Base):
  
          
    def __init__(self):
        qg.QDialog.__init__(self)
        self.setMinimumHeight(DEFAULT_WINDOW_HEIGHT)
        self.setMinimumWidth(DEFAULT_WINDOW_WIDTH)
        self.setWindowTitle(WINDOW_NAME)
        self.setObjectName('Settings')
        self.setStyleSheet('QDialog#Settings { background-color : rgba(30,30,30,255);}')
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
     
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        
        self.main_frame = qg.QFrame()
        self.main_frame.setParent(self.parent())
        self.main_frame.setObjectName('main_frame')
        self.main_frame.setStyleSheet('QFrame#main_frame {background-color : rgba(68,68,68,255);}')
        self.main_frame.setFrameStyle(qg.QFrame.Panel|qg.QFrame.Raised)
        self.main_frame.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)
        self.main_frame.setLayout(qg.QVBoxLayout())
        self.main_frame.layout().setContentsMargins(1,1,1,1)
        self.main_frame.layout().setSpacing(0)
        self.main_frame.layout().setAlignment(qc.Qt.AlignTop)
        self.layout().addWidget(self.main_frame)
        
        button_layout = qg.QHBoxLayout()
        button_layout.setContentsMargins(0,3,0,0)
        button_layout.setSpacing(3)
        self.layout().addLayout(button_layout)
        
        save_bttn   = qg.QPushButton('Save')
        cancel_bttn = qg.QPushButton('Cancel')
        
        button_layout.addWidget(save_bttn)
        button_layout.addWidget(cancel_bttn)
        
        save_bttn.clicked.connect(partial(self.returnCode, 1))
        cancel_bttn.clicked.connect(partial(self.returnCode, 0)) 
        
        self._changes = False
        
    
    #-----------------------------------------------------------------------------------------#
     
    @property
    def title(self):
        return self._title
    
    
    @title.setter
    def title(self, title):
        self._title = str(title).title()
        self.setWindowTitle('%s - Settings and Preferences' %self._title)
        
    #-----------------------------------------------------------------------------------------#
    
    def addElement(self, element):
        ''' 
            Adds any QWidget/QLayout/QSpacerItem to the main page widget.
            
        args :
            element : the Qt widget to add to the page
        '''
        
        if isinstance(element, qg.QWidget):
            self.main_frame.layout().addWidget(element)
            
        elif isinstance(element, qg.QLayout):
            self.main_frame.layout().addLayout(element)
            
        elif isinstance(element, qg.QSpacerItem):
            self.main_frame.layout().addSpacerItem(element)
            
        else:
            text = ["Do not recognise Element Type. Must be QWidget, ",
                    "QLayout or QSpacerItem. Got type '%s." %type(element)]
            raise TypeError(''.join(text))
        
    #-----------------------------------------------------------------------------------------#

    def returnCode(self, code):
        if code == 1 and self._changes is True:
            self.done(2)
        self.done(code)
            
    