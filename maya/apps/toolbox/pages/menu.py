import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import os
from functools import partial
import xml.etree.ElementTree as ET

import cg_inventor.maya.apps.toolbox.page as page

import cg_inventor.sys.lib.qt.base                 as base
import cg_inventor.sys.lib.qt.buttons.cross_button as cross_button
import cg_inventor.sys.lib.qt.buttons.icon_button  as icon_button


#--------------------------------------------------------------------------------------------------#

class MenuError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#
#                                             Menu                                                 #
#--------------------------------------------------------------------------------------------------#

class Menu(page.Page):    
    # signals
    #
    MENU_ITEM_CLICKED = 'menu_item_clicked'
     
    def __init__(self):
        page.Page.__init__(self)
        self._groups = []
        
        
    def addMenuGroup(self):
        new_menu_widget = MenuGroup()
        self.connect(new_menu_widget, qc.SIGNAL(Menu.MENU_ITEM_CLICKED), self._menuItemClicked)
        self._groups.append(new_menu_widget)
        self.addElement(new_menu_widget)
        
        return new_menu_widget
    
    
    def getAllMenuGroups(self):
        return self._groups
        

    def buildFromXML(self, xml_file=None, root=None):
        # if no root element is supplied, load file
        #
        if not root:
            if not xml_file:
                raise MenuError("No Xml Data provided. Requires either a file, or a root element.")
            
            # get toolbox xml path
            #
            import cg_inventor.maya.apps.toolbox as toolbox
            xml_path = os.path.join(os.path.dirname(toolbox.__file__), 'xml', xml_file)
            
            # get the root element
            #
            tree = ET.parse(xml_path)
            root = tree.getroot()
        
        try:
            self.title = root.attrib['title'].strip()
        except KeyError:
            self.title = 'Untitled'

        for group in root:
            if group.tag != 'group':
                continue
            
            new_group = self.addMenuGroup()
            new_group.buildFromXML(root=group)
                    
    
    def _menuItemClicked(self, item_id, data):                  
        self.emit(qc.SIGNAL(Menu.MENU_ITEM_CLICKED), item_id, data)

        
#--------------------------------------------------------------------------------------------------#
#                                           Menu Group                                             #
#--------------------------------------------------------------------------------------------------#

class MenuFrame(qg.QFrame):
    def __init__(self):
        qg.QFrame.__init__(self)
        
        self.setObjectName('menu_frame')
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(3,6,3,6)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setMinimumHeight(0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        
        style = ['background:              rgba( 50, 50, 50,255);',
                 'border:0px     solid     rgba(  0,  0,  0,  0);',
                 'border-bottom: 1px solid rgba(78,78,78,255);',
                 'border-left:   1px solid rgba(30,30,30,255);',
                 'border-right:  1px solid rgba(78,78,78,255);']
        self.setStyleSheet('QFrame#menu_frame {%s}' %' '.join(style))
        
        
        
class MenuTitle(qg.QFrame):
    def __init__(self):
        qg.QFrame.__init__(self)
        
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,1)
        self.layout().setSpacing(2)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        self.setFixedHeight(22)
        
        self.setObjectName('menu_title')
        style = ['background:              rgba( 100, 100, 100,255);',
                 'border:0px     solid     rgba(  0,  0,  0,  0);',
                 'border-top:    1px solid rgba(150,150,150,255);',
                 'border-bottom: 1px solid rgba( 50, 50, 50,255);',
                 'border-left:   1px solid rgba(150,150,150,255);',
                 'border-right:  1px solid rgba( 50, 50, 50,255);']
        self.setStyleSheet('QWidget#menu_title {%s}' %' '.join(style))
        
        self.cross_bttn = cross_button.CrossButton()
        self.layout().addWidget(self.cross_bttn)
        self.layout().addSpacerItem(qg.QSpacerItem(3,5,qg.QSizePolicy.Fixed))

        self.title_label = qg.QLabel(self._title)
        self.title_label.setFixedHeight(20)
        self.title_label.setFixedWidth(200)
        self.layout().addWidget(self.title_label) 
        
            
        
class MenuGroup(qg.QWidget, base.Base):
    ANIM_OPACITY_SPEED  = 200
    ANIM_GEOMETRY_SPEED = 100
    
    _title    = 'Untitled'
    _subtitle = None
    _icon     = None
    _items    = []
    
    def __init__(self, title=None, subtitle=None):
        qg.QWidget.__init__(self)
        
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        
        # create title bar
        #
        title_widget = qg.QFrame()       
        title_widget.setLayout(qg.QHBoxLayout())
        title_widget.layout().setContentsMargins(0,0,0,1)
        title_widget.layout().setSpacing(2)
        title_widget.layout().setAlignment(qc.Qt.AlignVCenter)
        title_widget.setFixedHeight(22)
        
        title_widget.setObjectName('menu_title')
        style = ['background:              rgba( 100, 100, 100,255);',
                 'border:0px     solid     rgba(  0,  0,  0,  0);',
                 'border-top:    1px solid rgba(150,150,150,255);',
                 'border-bottom: 1px solid rgba( 50, 50, 50,255);',
                 'border-left:   1px solid rgba(150,150,150,255);',
                 'border-right:  1px solid rgba( 50, 50, 50,255);']
        title_widget.setStyleSheet('QWidget#menu_title {%s}' %' '.join(style))
        self.layout().addWidget(title_widget)
        title_widget.layout().addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Fixed))

        self.cross_bttn = cross_button.CrossButton()
        title_widget.layout().addWidget(self.cross_bttn)
        title_widget.layout().addSpacerItem(qg.QSpacerItem(3,5,qg.QSizePolicy.Fixed))

        self.title_label = qg.QLabel(self._title)
        self.title_label.setFixedHeight(20)
        self.title_label.setFixedWidth(200)
        title_widget.layout().addWidget(self.title_label)

        # create frame
        #        
        self.row_widget = qg.QWidget()
        self.row_widget.setStyleSheet("background: transparent;")
        self.row_widget.setLayout(qg.QVBoxLayout())
        self.row_widget.layout().setContentsMargins(0,0,0,0)
        self.row_widget.layout().setSpacing(6)
        self.row_widget.layout().setAlignment(qc.Qt.AlignTop)
        
        self.empty_menu_label = qg.QLabel("<font color='#999999'>No Available Tools</font>")
        self.row_widget.layout().addWidget(self.empty_menu_label)
        
        self.graphics_scene = qg.QGraphicsScene()        
        self.graphics_view  = qg.QGraphicsView(self.graphics_scene)
        self.graphics_view.setFocusPolicy(qc.Qt.NoFocus)
        self.graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        style = ['border-style: none;', 'background: transparent;']
        self.graphics_view.setStyleSheet("QGraphicsView {%s}"  %' '.join(style))
        self.graphics_view.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        
        self.row_graphic_item = self.graphics_scene.addWidget(self.row_widget)
        
        self.menu_frame = MenuFrame()        
        self.menu_frame.layout().addWidget(self.graphics_view)
        self.layout().addWidget(self.menu_frame)
        
        self._row_count          = 0
        self._current_row        = None
        self._current_count      = 0
        self._current_row_height = 0
        
        self._menu_anim   = None
        self._menu_height = 0
                
        # setup expanding and collapsing
        #
        self.connect(self.cross_bttn, qc.SIGNAL(cross_button.EXPAND  ), partial(self.setExpanded, True))
        self.connect(self.cross_bttn, qc.SIGNAL(cross_button.COLLAPSE), partial(self.setExpanded, False))
        #self.connect(self.menu_frame, qc.SIGNAL('resize'), self._test)
        
        # setup title and icon
        #
        self.title = title, subtitle
        
    #-----------------------------------------------------------------------------------------#
    
    def setExpanded(self, expanded):
        self._animateExpansion(expanded)
        
            
    def _animateExpansion(self, open):        
        # opacity animation
        #
        opacity_anim = qc.QPropertyAnimation(self.row_graphic_item, "opacity")
      
        opacity_anim.setStartValue(not(open)); 
        opacity_anim.setEndValue(open)        
        opacity_anim.setDuration(MenuGroup.ANIM_OPACITY_SPEED)        
        opacity_anim_curve = qc.QEasingCurve()
        if open is True:
            opacity_anim_curve.setType(qc.QEasingCurve.InQuad)
        else:
            opacity_anim_curve.setType(qc.QEasingCurve.OutQuad)
        opacity_anim.setEasingCurve(opacity_anim_curve)
        
        # size animation
        #
        size_anim = qc.QPropertyAnimation(self.menu_frame, "geometry")
        
        menu_geo = self.menu_frame.geometry()
        menu_width = menu_geo.width()
        menu_x = menu_geo.x() 
        menu_y = menu_geo.y()
        
        size_start = qc.QRect(menu_x, menu_y, menu_width, int(not(open)) * self._menu_height)
        size_end   = qc.QRect(menu_x, menu_y, menu_width, open * self._menu_height)
        
        size_anim.setStartValue(size_start)
        size_anim.setEndValue(size_end)
        size_anim.setDuration((self._menu_height/50.0) * MenuGroup.ANIM_GEOMETRY_SPEED)
        size_anim_curve = qc.QEasingCurve()
        if open is True:
            size_anim_curve.setType(qc.QEasingCurve.InQuad)
        else:
            size_anim_curve.setType(qc.QEasingCurve.OutQuad)
        size_anim.setEasingCurve(size_anim_curve)
        
        # create animation sequence
        #
        self.menu_anim = qc.QSequentialAnimationGroup()
        
        if open:
            self.menu_anim.addAnimation(size_anim)
            self.menu_anim.addAnimation(opacity_anim)
        else:
            self.menu_anim.addAnimation(opacity_anim)
            self.menu_anim.addAnimation(size_anim)            

        size_anim.valueChanged.connect(self._test)
        self.menu_anim.start()
        

    def _test(self):        
        anim = self.menu_anim.currentAnimation()
        current_height = anim.currentValue().toRect().height()
        self.menu_frame.setFixedHeight(current_height)
            
    #-----------------------------------------------------------------------------------------#
    
    @property
    def title(self):
        return self._title
    
    
    @title.setter
    def title(self, title):
        try:
            title, subtitle = title
        except ValueError:
            subtitle = None

        if title is None:
            self._title = 'Untitled'
        else:
            self._title = str(title).title()
            
        if subtitle is not None:
            self.subtitle = subtitle
        else:
            self._setFullTitle()
        
        
    @property
    def subtitle(self):
        return self._subtitles
    
    
    @subtitle.setter
    def subtitle(self, subtitle):
        if subtitle is None:
            self._subtitle = None
            return
        
        self._subtitle = str(subtitle).title()
        self._setFullTitle()
    
    
    def _setFullTitle(self):
        if self._subtitle is not None:
            self.title_label.setText('<b>%s</b> - %s' %(self._title.upper(), self._subtitle))
        else:
            self.title_label.setText('<b>%s</b>' %self._title.upper())     
            
    #-----------------------------------------------------------------------------------------#
    
    def buildFromXML(self, xml_file=None, root=None):
        # reset menu height
        #
        self._menu_height = 0
        
        # if no root element is supplied, load file
        #
        if not root:
            if not xml_file:
                raise MenuError("No Xml Data provided. Requires either a file, or a root element.")
            
            # get toolbox xml path
            #
            import cg_inventor.maya.apps.toolbox as toolbox
            xml_path = os.path.join(os.path.dirname(toolbox.__file__), 'xml', xml_file)        
            
            # get the root element
            #
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
        try:
            self.title = root.attrib['title'].strip()
        except KeyError:
            self.title = 'UNTITLED'
            
        try:
            self.subtitle = root.attrib['subtitle'].strip()
        except KeyError:
            self.subtitle = None
        
        for item in root: 
            if item.tag != 'item':
                continue
            
            menu_item = self.addMenuItem()
            menu_item.buildFromXML(root=item)
            
            item_height = menu_item.sizeHint().height()
            if item_height > self._current_row_height:
                self._current_row_height = item_height
                print self._row_count, self._current_row_height, item_height
                
        self._menu_height += self._current_row_height + (self._row_count * 6)
        self.graphics_view.setFixedHeight(self._menu_height)
        self._menu_height += 12
        
        
    
    def addMenuItem(self):
        if self._current_row is None or self._current_count >= 4:
            self.empty_menu_label.setVisible(False)
            self._addMenuRow()
            self._current_count = 0
        
        new_menu_item = MenuItem()
        self._items.append(new_menu_item)
        
        self.connect(new_menu_item, qc.SIGNAL(Menu.MENU_ITEM_CLICKED), self._menuItemClicked)
        self._current_row.addWidget(new_menu_item)
        self._current_count += 1

        return new_menu_item
    
    
    
    def _addMenuRow(self):
        self._current_row = qg.QHBoxLayout()
        self._current_row.setContentsMargins(0,0,0,0)
        self._current_row.setSpacing(5)
        self._current_row.setAlignment(qc.Qt.AlignTop)
        self.row_widget.layout().addLayout(self._current_row)
        
        self._row_count += 1
        
        self._menu_height += self._current_row_height
        self._current_row_height = 0       
   
        
    
    def getAllMenuItems(self):
        return self._items
        
    #-----------------------------------------------------------------------------------------#
    
    def _menuItemClicked(self, item_id, data):
        self.emit(qc.SIGNAL(Menu.MENU_ITEM_CLICKED), item_id, data)



#--------------------------------------------------------------------------------------------------#
#                                           Menu Item                                              #
#--------------------------------------------------------------------------------------------------#

class MenuItem(qg.QFrame, base.Base):
    _title        = 'Untitled'
    _icon         = None
    data          = None
    _item_id      = 0
    
    def __init__(self, title=None, icon=None, data=None):
        qg.QWidget.__init__(self)
        
        self.setFixedWidth(76)
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Minimum)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)
               
        self.icon_bttn = icon_button.IconButton()
        self.icon_bttn.setFixedHeight(42)
        self.icon_bttn.setFixedWidth(42)

        button_layout = qg.QHBoxLayout()
        button_layout.addSpacerItem(qg.QSpacerItem(0,0,qg.QSizePolicy.Expanding))
        button_layout.addWidget(self.icon_bttn)
        button_layout.addSpacerItem(qg.QSpacerItem(0,0,qg.QSizePolicy.Expanding))
        self.layout().addLayout(button_layout)
        
        self.title_label = qg.QLabel('Untitled')
        self.title_label.setFixedWidth(76)
        self.title_label.setFixedHeight(14)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(qc.Qt.AlignHCenter|qc.Qt.AlignTop)
        self.layout().addWidget(self.title_label)
        
        MenuItem._item_id += 1
        self._item_id = MenuItem._item_id
        
        if title: self.title = title
        if icon:  self.icon  = icon
        if data:  self.data  = data
        
        self.icon_bttn.clicked.connect(self._emitMenuID)

    # ---------------------------------------------------------------------------------------- #
    
    def buildFromXML(self, xml_file=None, root=None):
        # if no root element is supplied, load file
        #
        if not root:
            if not xml_file:
                raise MenuError("No Xml Data provided. Requires either a file, or a root element.")
            
            # get toolbox xml path
            #
            import cg_inventor.maya.apps.toolbox as toolbox
            xml_path = os.path.join(os.path.dirname(toolbox.__file__), 'xml', xml_file)        
            
            # get the root element
            #
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
        # get page information
        #
        try:
            self.title = root.attrib['title'].strip().capitalize()
        except KeyError:
            self.title = 'Untitled'
        
        self.data = []
        self.icon = None 
        
        for element in root:
            if element.tag == 'icon':
                self.icon = element.text.strip()
                
            elif element.tag == 'data':
                data = element.text.strip()
                try:
                    data = eval(data)
                except (NameError, SyntaxError):
                    pass
                
                self.data.append(data)
                
        if self.icon == None:
            self.icon = ':logos/maya_default.png' 
        
    # ---------------------------------------------------------------------------------------- #

        
    @property
    def title(self):
        return self._title
    
    
    @title.setter
    def title(self, title):
        # format as title string
        #
        title = title.title()
        
        # if word is longer that 11 charactes, add '-'
        #
        parts = title.split(' ')
        first_word = parts[0] 
        if len(first_word) >= 11:
            parts[0] = '%s-%s' %(first_word[0:11], first_word[11:])
        
        # adjust menu item for wrapped text
        #
        self._title = title
        self.title_label.setText(' '.join(parts))
        if len(title) > 13:
            self.title_label.setFixedHeight(28)
        else:
            self.title_label.setFixedHeight(14)

    # ---------------------------------------------------------------------------------------- #    
    
    @property
    def icon(self):
        return self._icon
    
    @icon.setter
    def icon(self, icon):
        self._icon = icon      
        self.icon_bttn.setImage(icon)
    
    # ---------------------------------------------------------------------------------------- #
    
    def disable(self, value=True):
        self.title_label.setEnabled(not(value))
        self.icon_bttn.setEnabled(not(value))

    # ---------------------------------------------------------------------------------------- #   
    
    def _emitMenuID(self):
        if len(self.data) == 0:   data = None
        elif len(self.data) == 1: data = self.data[0]
        else: data =              self.data
        
        self.emit(qc.SIGNAL(Menu.MENU_ITEM_CLICKED), self._item_id, 
                  data)  
        
        