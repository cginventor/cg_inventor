import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import cg_inventor.maya.apps.toolbox.page as page
import cg_inventor.maya.lib.qt.item_list  as item_list

import cg_inventor.sys.lib.qt.misc.splitter       as splitter
import cg_inventor.sys.lib.qt.buttons.icon_button as icon_button

import cg_inventor.maya.utils.names as util_names
import maya.cmds as mc


#--------------------------------------------------------------------------------------------------#


TITLE    = 'Naming Tools'

class NamingTools(page.Page):
    SORT_TYPE = 'type'
    SORT_NAME = 'name'
    
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        
        # RENAME Widget
        #
        rename_widget = qg.QWidget()
        rename_widget.setLayout(qg.QVBoxLayout())
        rename_widget.layout().setContentsMargins(0,0,0,0)
        rename_widget.layout().setSpacing(2)
        rename_widget.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.addElement(rename_widget)
        
        self.rename_label = qg.QLabel('RENAME')
        self.rename_label.setFixedHeight(12)
        title_font = qg.QFont()
        title_font.setBold(True)
        self.rename_label.setFont(title_font)
        self.rename_label.setAlignment(qc.Qt.AlignHCenter)
     
        rename_splitter = splitter.Splitter()
        rename_splitter.setMainColour(100, 100, 100)
        rename_splitter.addWidget(self.rename_label)
        rename_widget.layout().addWidget(rename_splitter)
    
        rename_text_layout = qg.QHBoxLayout()
        rename_text_layout.setContentsMargins(4,0,4,0)  
        rename_text_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_text_layout)
   
        rename_text_label = qg.QLabel('New Name:')
        self.rename_line = qg.QLineEdit()
        text_validator = qg.QRegExpValidator(qc.QRegExp("[^_][a-zA-Z_]+"), self.rename_line)
        self.rename_line.setValidator(text_validator)
        rename_text_layout.addWidget(rename_text_label)
        rename_text_layout.addWidget(self.rename_line)
         
        name_splitter = NamingSplitter()
        rename_widget.layout().addLayout(name_splitter)
  
        rename_mult_layout = qg.QHBoxLayout()
        rename_mult_layout.setContentsMargins(4,0,4,0)
        rename_mult_layout.setSpacing(2)
        rename_widget.layout().addLayout(rename_mult_layout)
          
        rename_mult_method_label = qg.QLabel('Multiples Naming Method:')
        self.rename_mult_method_combo = qg.QComboBox()
        self.rename_mult_method_combo.addItem('Numbers (0-9)')
        self.rename_mult_method_combo.addItem('Letters (a-z)')
        self.rename_mult_method_combo.setFixedWidth(100)
          
        rename_mult_layout.addWidget(rename_mult_method_label)
        rename_mult_layout.addWidget(self.rename_mult_method_combo)
          
        mult_options_layout = qg.QHBoxLayout()
        mult_options_layout.setContentsMargins(4,0,4,0)
        mult_options_layout.setSpacing(2)
        rename_widget.layout().addLayout(mult_options_layout)
          
        self.frame_pad_label = qg.QLabel('No. Padding:')
        self.frame_pad_spin = qg.QSpinBox()
        self.frame_pad_spin.setFixedWidth(40)
        self.frame_pad_spin.setMinimum(0)
        self.frame_pad_spin.setMaximum(10)
          
        self.lower_radio = qg.QRadioButton('Lowercase')
        self.upper_radio = qg.QRadioButton('Uppercase')
        self.lower_radio.setVisible(False)
        self.upper_radio.setVisible(False)
        self.lower_radio.setFixedHeight(19)
        self.upper_radio.setFixedHeight(19)
        self.lower_radio.setChecked(True)
          
        mult_splitter = NamingSplitter()
        rename_widget.layout().addLayout(mult_splitter)
          
        mult_options_layout.addWidget(self.frame_pad_label)
        mult_options_layout.addWidget(self.lower_radio)
        mult_options_layout.addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Expanding))
        mult_options_layout.addWidget(self.frame_pad_spin)        
        mult_options_layout.addWidget(self.upper_radio)
  
        fix_layout = qg.QHBoxLayout()
        fix_layout.setContentsMargins(4,0,4,0)
        fix_layout.setSpacing(2)
        rename_widget.layout().addLayout(fix_layout)
           
        self.prefix_check = qg.QCheckBox('Prefix:')
        self.prefix_line  = qg.QLineEdit()
        self.prefix_line.setValidator(text_validator)
        self.prefix_line.setEnabled(False)
        self.prefix_line.setFixedWidth(85)
           
        self.suffix_check = qg.QCheckBox('Suffix:')
        self.suffix_line  = qg.QLineEdit()
        self.suffix_line.setValidator(text_validator)
        self.suffix_line.setEnabled(False)
        self.suffix_line.setFixedWidth(85)
           
        fix_layout.addWidget(self.prefix_check)
        fix_layout.addWidget(self.prefix_line)
        fix_layout.addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Expanding))
        fix_layout.addWidget(self.suffix_check)
        fix_layout.addWidget(self.suffix_line)
          
        fix_splitter = NamingSplitter()
        rename_widget.layout().addLayout(fix_splitter)
          
        self.rename_label = qg.QLabel()        
        self.rename_button = qg.QPushButton('Rename')
        self.rename_button.setFixedHeight(20)
        self.rename_button.setFixedWidth(55)
        rename_button_layout = qg.QHBoxLayout()
        rename_button_layout.setContentsMargins(4,0,4,0)
        rename_button_layout.setSpacing(0)
        rename_button_layout.addWidget(self.rename_label)
        rename_button_layout.addWidget(self.rename_button)
        rename_widget.layout().addLayout(rename_button_layout)       
  
        spacer_1 = qg.QSpacerItem(20, 20, qg.QSizePolicy.Fixed)
        self.addElement(spacer_1)
 
        # REPLACE Widget
        #
        replace_widget = qg.QWidget()
        replace_widget.setLayout(qg.QVBoxLayout())
        replace_widget.layout().setContentsMargins(0,0,0,0)
        replace_widget.layout().setSpacing(2)
        replace_widget.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.addElement(replace_widget)
          
        self.replace_label = qg.QLabel('REPLACE')
        self.replace_label.setFixedHeight(12)
        self.replace_label.setFont(title_font)
        self.replace_label.setAlignment(qc.Qt.AlignHCenter)
          
        replace_splitter = splitter.Splitter()
        replace_splitter.setMainColour(100, 100, 100)
        replace_splitter.addWidget(self.replace_label)
        replace_widget.layout().addWidget(replace_splitter)
          
        replace_label     = qg.QLabel('Replace:')        
        self.replace_line = qg.QLineEdit()
        self.replace_line.setValidator(text_validator)
        with_label        = qg.QLabel('With:')        
        self.with_line    = qg.QLineEdit()
        self.with_line.setValidator(text_validator)
          
        replace_label.setFixedWidth(55)
        with_label.setFixedWidth(55)
          
        replace_layout = qg.QHBoxLayout()
        replace_layout.setContentsMargins(4,0,4,0)
        replace_layout.setSpacing(2)
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_line)
        replace_widget.layout().addLayout(replace_layout)
          
        with_layout = qg.QHBoxLayout()
        with_layout.setContentsMargins(4,0,4,0)
        with_layout.setSpacing(2)
        with_layout.addWidget(with_label)
        with_layout.addWidget(self.with_line)
        replace_widget.layout().addLayout(with_layout)
          
        with_splitter = NamingSplitter()
        replace_widget.layout().addLayout(with_splitter)
          
        selection_mode_label = qg.QLabel('Selection Mode:')
        self.all_radio = qg.QRadioButton('All')
        self.all_radio.setFixedHeight(19)
        self.all_radio.setChecked(True)
        self.selected_radio = qg.QRadioButton('Selected')
        self.selected_radio.setFixedHeight(19)        
          
        selection_layout = qg.QHBoxLayout()
        selection_layout.setContentsMargins(4,0,4,0)
        selection_layout.setSpacing(2)
        selection_layout.addWidget(selection_mode_label)
        selection_layout.addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Expanding))
        selection_layout.addWidget(self.all_radio)
        selection_layout.addWidget(self.selected_radio)
        replace_widget.layout().addLayout(selection_layout)
          
        selection_splitter = NamingSplitter()
        replace_widget.layout().addLayout(selection_splitter)
          
        self.replace_button = qg.QPushButton('Replace')
        self.replace_button.setFixedHeight(20)
        self.replace_button.setFixedWidth(55)
        replace_button_layout = qg.QHBoxLayout()
        replace_button_layout.setContentsMargins(4,0,4,0)
        replace_button_layout.setSpacing(0)
        replace_button_layout.setAlignment(qc.Qt.AlignRight)
        replace_button_layout.addWidget(self.replace_button)
        replace_widget.layout().addLayout(replace_button_layout)
          
        spacer_2 = qg.QSpacerItem(20, 20, qg.QSizePolicy.Fixed)
        self.addElement(spacer_2)
         
        # NAMESPACE Widget
        #
        namespace_widget = qg.QWidget()
        namespace_widget.setLayout(qg.QVBoxLayout())
        namespace_widget.layout().setContentsMargins(0,0,0,0)
        namespace_widget.layout().setSpacing(2)
        namespace_widget.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.addElement(namespace_widget)
           
        self.namespace_label = qg.QLabel('NAMESPACE')
        self.namespace_label.setFixedHeight(12)
        self.namespace_label.setFont(title_font)
        self.namespace_label.setAlignment(qc.Qt.AlignHCenter)
           
        namespace_splitter = splitter.Splitter()
        namespace_splitter.setMainColour(100, 100, 100)
        namespace_splitter.addWidget(self.namespace_label)
        namespace_widget.layout().addWidget(namespace_splitter)
  
        namespace_tree_layout = qg.QHBoxLayout()
        namespace_tree_layout.setContentsMargins(0,0,0,0)
        namespace_tree_layout.setSpacing(2)
        namespace_tree_layout.setStretch(0, 60)
        namespace_tree_layout.setStretch(1, 40)
        namespace_widget.layout().addLayout(namespace_tree_layout)
          
        self.namespace_tree = qg.QTreeWidget()
        self.namespace_tree.setFixedWidth(200)
          
        button_layout = qg.QVBoxLayout() 
  
        namespace_tree_layout.addWidget(self.namespace_tree)
        namespace_tree_layout.addLayout(button_layout)
 
        # connect modifiers
        #
        self.rename_mult_method_combo.currentIndexChanged.connect(self._toggleMultNamingMethod)
          
        self.lower_radio.clicked.connect(self._updateExampleRename)
        self.upper_radio.clicked.connect(self._updateExampleRename)
        self.frame_pad_spin.valueChanged.connect(self._updateExampleRename)
          
        self.prefix_check.stateChanged.connect(self._prefixToggle)
        self.suffix_check.stateChanged.connect(self._suffixToggle)
          
        self.rename_line.textChanged.connect(self._updateExampleRename)
        self.prefix_line.textChanged.connect(self._updateExampleRename)
        self.suffix_line.textChanged.connect(self._updateExampleRename)
         
        self.rename_button.clicked.connect(self.rename)
        self.replace_button.clicked.connect(self.replace)
         
        #self.sort_method_button.clicked.connect(self.toggleSort)
         
        self._updateExampleRename()
        
        #self.items_list.loadNodes(mc.ls(sl=True))
    
    #-----------------------------------------------------------------------------------------#

    def _toggleMultNamingMethod(self, index):
        value = bool(index)
        self.lower_radio.setVisible(value)
        self.upper_radio.setVisible(value)
        self.frame_pad_label.setVisible(not(value))
        self.frame_pad_spin.setVisible(not(value))
        
        self._updateExampleRename()
    
    #-----------------------------------------------------------------------------------------#
    
    def _prefixToggle(self, value):
        self.prefix_line.setEnabled(value)
        
        
    def _suffixToggle(self, value):
        self.suffix_line.setEnabled(value)
        
    #-----------------------------------------------------------------------------------------#
    
    def _updateExampleRename(self):
        example_text = ''
        
        text, prefix, suffix, padding, naming_method, upper = self._getRenameSettings()
        if not text:
            self.rename_label.setText('<font color=#646464>e.g.</font>')
            return
            
        if prefix: example_text += '%s_' %prefix
        
        if text:   example_text += '%s_' %text

        if naming_method:
            if upper: example_text += 'A'
            else:     example_text += 'a'                        
        else:
            example_text += (padding * '0') + '1'
            
        if suffix:
            example_text += '_%s' %suffix
        
        self.rename_label.setText('<font color=#646464>e.g. \'%s\'</font>' %example_text)
    
    #-----------------------------------------------------------------------------------------#
    
    def rename(self):
        text, prefix, suffix, padding, naming_method, upper = self._getRenameSettings()
        util_names.rename(mc.ls(sl=True), text, prefix, suffix, padding, naming_method, upper)
        

    def _getRenameSettings(self):
        text = str(self.rename_line.text()).strip()
        
        naming_method = bool(self.rename_mult_method_combo.currentIndex())
        padding = 0; upper = True
        if naming_method == 0:
            padding = self.frame_pad_spin.value()
        else:
            upper   = self.upper_radio.isChecked()
        
        prefix = ''; suffix = ''
        if self.prefix_check.isChecked():
            prefix = self.prefix_line.text()
        if self.suffix_check.isChecked():
            suffix = self.suffix_line.text()
        
        return text, prefix, suffix, padding, naming_method, upper
    
    #-----------------------------------------------------------------------------------------#

    def replace(self):
        replace_text = str(self.replace_line.text())
        with_text    = str(self.with_line.text())
        
        if self.all_radio.isChecked():
            nodes = mc.ls()
        else:
            nodes = mc.ls(sl=True)
    
        util_names.replace(nodes, replace_text, with_text)

    #-----------------------------------------------------------------------------------------#

    def toggleSort(self):
        if self.sort_method == self.SORT_TYPE:
            self.sort_method = self.SORT_NAME
            self.sort_method_button.setImage(':gui/sort_name.png')
            self.items_list.sortByName()
            
        else:
            self.sort_method = self.SORT_TYPE
            self.sort_method_button.setImage(':gui/sort_type.png')
            self.items_list.sortByType()

#--------------------------------------------------------------------------------------------------#

class NamingSplitter(qg.QHBoxLayout):
    def __init__(self):
        qg.QHBoxLayout.__init__(self)
        self.setContentsMargins(40,2,40,2)

        splitter_line = splitter.Splitter()
        splitter_line.setMainColour(60,60,60)
        splitter_line.showShadow(False)
        splitter_line.setFixedHeight(1)
        
        self.addWidget(splitter_line)
        
        