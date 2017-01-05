import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import cg_inventor.maya.apps.toolbox.page as page
import cg_inventor.maya.lib.qt.item_list  as item_list

import cg_inventor.sys.lib.qt.misc.splitter       as splitter
import cg_inventor.sys.lib.qt.buttons.icon_button as icon_button

import cg_inventor.maya.utils.names as util_names
import maya.cmds as mc


#--------------------------------------------------------------------------------------------------#


TITLE = 'Symmetry'

class Symmetry(page.Page):    
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        
        # TRANSFORM Widget
        #
        transform_widget = qg.QWidget()
        transform_widget.setLayout(qg.QVBoxLayout())
        transform_widget.layout().setContentsMargins(0,0,0,0)
        transform_widget.layout().setSpacing(2)
        transform_widget.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.addElement(transform_widget)
        
        self.transform_label = qg.QLabel('TRANSFORM')
        self.transform_label.setFixedHeight(12)
        title_font = qg.QFont()
        title_font.setBold(True)
        self.transform_label.setFont(title_font)
        self.transform_label.setAlignment(qc.Qt.AlignHCenter)
     
        transform_splitter = splitter.Splitter()
        transform_splitter.setMainColour(100, 100, 100)
        transform_splitter.addWidget(self.transform_label)
        transform_widget.layout().addWidget(transform_splitter)
    
        transform_text_layout = qg.QHBoxLayout()
        transform_text_layout.setContentsMargins(4,0,4,0)  
        transform_text_layout.setSpacing(2)
        transform_widget.layout().addLayout(transform_text_layout)
        
        