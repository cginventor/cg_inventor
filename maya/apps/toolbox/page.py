import PyQt4.QtCore as qc
import PyQt4.QtGui  as qg
from functools import partial
from weakref import proxy

import cg_inventor.maya.apps.toolbox.settings as settings

import cg_inventor.sys.lib.qt.base                as base
import cg_inventor.sys.lib.qt.misc.splitter       as splitter
import cg_inventor.sys.lib.qt.buttons.icon_button as icon_button
import cg_inventor.maya.lib.images.icons_rc

# ------------------------------------------------------------------------------------------------ #

class PageError(Exception):
    pass

# ------------------------------------------------------------------------------------------------ #

class Page(qg.QWidget, base.Base):   
    _title    = 'Untitled'
    _subtitle = ''
    
    _docked = True
    
    _page_id = 0
    _prev_page_id = None
    
    _buttons = {}
    
    BACK    = 'back'
    TEAR    = 'tear'
    ATTACH  = 'attach'
    CLOSE   = 'close'
    REFRESH = 'refresh'
   
    def __init__(self):
        qg.QWidget.__init__(self)
    
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        # create title layout
        #
        title_layout = qg.QHBoxLayout()
        title_layout.setContentsMargins(0,0,0,0)
        title_layout.setSpacing(0)
        self.layout().addLayout(title_layout)
        self.layout().setAlignment(qc.Qt.AlignTop)
        
        # create left side buttons
        #
        left_bttn_layout = qg.QVBoxLayout()
        left_bttn_layout.layout().setAlignment(qc.Qt.AlignTop)
        left_bttn_layout.setContentsMargins(0,0,0,0)
        left_bttn_layout.setSpacing(0)
        
        left_bttns_widget = qg.QWidget()
        left_bttns_widget.setLayout(qg.QHBoxLayout())
        left_bttns_widget.layout().setContentsMargins(0,0,0,2)
        left_bttns_widget.layout().setSpacing(0)
        left_bttns_widget.layout().setAlignment(qc.Qt.AlignLeft)
        left_bttns_widget.setFixedWidth(78)
        left_bttns_widget.setFixedHeight(27)
        
        left_title_splitter = splitter.Splitter()
        left_title_splitter.setFixedHeight(2)
        
        left_bttn_layout.addWidget(left_bttns_widget)
        left_bttn_layout.addWidget(left_title_splitter)
        
        # create right side buttons
        #
        right_bttn_layout = qg.QVBoxLayout()
        right_bttn_layout.layout().setAlignment(qc.Qt.AlignTop)
        right_bttn_layout.setContentsMargins(0,0,0,0)
        right_bttn_layout.setSpacing(0)
        
        right_bttns_widget = qg.QWidget()
        right_bttns_widget.setLayout(qg.QHBoxLayout())
        right_bttns_widget.layout().setContentsMargins(0,0,0,2)
        right_bttns_widget.layout().setSpacing(0)
        right_bttns_widget.layout().setAlignment(qc.Qt.AlignRight|qc.Qt.AlignTop)
        right_bttns_widget.setFixedWidth(78)
        right_bttns_widget.setFixedHeight(27)
        
        right_title_splitter = splitter.Splitter()
        right_title_splitter.setFixedHeight(2)
        
        right_bttn_layout.addWidget(right_bttns_widget)
        right_bttn_layout.addWidget(right_title_splitter)
       
        # setup default left buttons
        #
        self._buttons['back']   = self.back_bttn   = icon_button.IconButton(':arrows/back.png')
        self._buttons['tear']   = self.tear_bttn   = icon_button.IconButton(':gui/docked.png')
        self._buttons['attach'] = self.attach_bttn = icon_button.IconButton(':gui/undocked.png')
        self.attach_bttn.setVisible(False)
        
        left_bttns_widget.layout().addWidget(self.back_bttn)
        left_bttns_widget.layout().addWidget(self.tear_bttn)
        left_bttns_widget.layout().addWidget(self.attach_bttn)
        
        self._buttons['refresh']  = self.refresh_bttn  = icon_button.IconButton(':gui/refresh.png')
        self._buttons['settings'] = self.settings_bttn = icon_button.IconButton(':gui/settings.png')
        self._buttons['close']    = self.close_bttn    = icon_button.IconButton(':gui/close.png')
        
        right_bttns_widget.layout().addWidget(self.refresh_bttn)
        right_bttns_widget.layout().addWidget(self.settings_bttn)
        right_bttns_widget.layout().addWidget(self.close_bttn)
        
        # setup title labels
        #
        title_font = qg.QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        sub_title_font = qg.QFont()
        sub_title_font.setPointSize(9)
        
        self.title_label = qg.QLabel()
        self.title_label.setText('Untitled')
        self.title_label.setFixedHeight(21)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(qc.Qt.AlignHCenter|qc.Qt.AlignBottom)
        self.subtitle_label = qg.QLabel()
        self.subtitle_label.setText('')
        self.subtitle_label.setFixedHeight(15)
        self.subtitle_label.setFont(sub_title_font)
        self.subtitle_label.setAlignment(qc.Qt.AlignHCenter)
        self.subtitle_label.setSizePolicy(qg.QSizePolicy.Maximum, qg.QSizePolicy.Maximum)
        
        title_label_layout = qg.QVBoxLayout()
        title_label_layout.setContentsMargins(0,0,0,0)
        title_label_layout.setSpacing(0)
        title_label_layout.setAlignment(qc.Qt.AlignTop)

        main_title_layout = qg.QHBoxLayout()
        main_title_layout.setContentsMargins(0,0,0,0)
        main_title_layout.setSpacing(0)
        main_title_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        main_title_layout.addWidget(self.title_label)
        main_title_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))

        left_subtitle_splitter = splitter.Splitter()
        left_subtitle_splitter.setFixedHeight(15)
        self.right_subtitle_splitter = splitter.Splitter()
        self.right_subtitle_splitter.setFixedHeight(15)

        subtitle_layout = qg.QHBoxLayout()
        subtitle_layout.setContentsMargins(0,0,0,0)
        subtitle_layout.setSpacing(5)
        subtitle_layout.setAlignment(qc.Qt.AlignBottom)
        subtitle_layout.addWidget(left_subtitle_splitter)
        subtitle_layout.addWidget(self.subtitle_label)
        subtitle_layout.addWidget(self.right_subtitle_splitter)

        title_label_layout.addLayout(main_title_layout)
        title_label_layout.addLayout(subtitle_layout)

        title_layout.addLayout(left_bttn_layout)
        title_layout.addLayout(title_label_layout)
        title_layout.addLayout(right_bttn_layout)

        # create main page widget
        #
        self.page_widget = qg.QWidget()
        self.page_widget.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Maximum)
        self.page_widget.setLayout(qg.QVBoxLayout())
        self.page_widget.layout().setSpacing(0)
        self.page_widget.layout().setContentsMargins(4,0,4,2)
        self.page_widget.layout().setAlignment(qc.Qt.AlignTop)
        
        self.page_scroll = qg.QScrollArea()
        self.page_scroll.setWidget(self.page_widget)
        self.page_scroll.setWidgetResizable(True)
        self.page_scroll.setFocusPolicy(qc.Qt.NoFocus)
        self.page_scroll.setStyleSheet("QScrollArea {border:0px solid rgba(0,0,0,0)};")
        self.layout().addWidget(self.page_scroll)

        self.subtitle_label.setVisible(False)
        self.right_subtitle_splitter.setVisible(False)
        
        self.back_bttn.clicked.connect(self._back)
        self.tear_bttn.clicked.connect(partial(self.setFloating, True))
        self.attach_bttn.clicked.connect(partial(self.setFloating, False))
        self.refresh_bttn.clicked.connect(self.refresh)
        self.close_bttn.clicked.connect(self._close)
        
        # increment page id
        #
        Page._page_id += 1
        self._page_id = Page._page_id
   
    # --------------------------------------------------------------------------------------- #
    
    def addElement(self, element):
        ''' 
        Adds any QWidget/QLayout/QSpacerItem to the main page widget.
            
        args :
            element : the Qt widget to add to the page
        '''        
        
        if isinstance(element, qg.QWidget):
            self.page_widget.layout().addWidget(element)
            
        elif isinstance(element, qg.QLayout):
            self.page_widget.layout().addLayout(element)
            
        elif isinstance(element, qg.QSpacerItem):
            self.page_widget.layout().addSpacerItem(element)
            
        else:
            text = ["Do not recognise Element Type. Must be QWidget, ",
                    "QLayout or QSpacerItem. Got type '%s." %type(element)]
            raise TypeError(''.join(text))
        
        
    def removeElement(self, element):
        '''
        Adds any QWidget/QLayout/QSpacerItem to the main page widget.
            
        args :
            element : the Qt widget to add to the page
        '''

        if isinstance(element, qg.QWidget):
            self.page_widget.layout().removeWidget(element)
            
        elif isinstance(element, qg.QLayout):
            self.page_widget.layout().removeLayout(element)
            
        elif isinstance(element, qg.QSpacerItem):
            self.page_widget.layout().removeItem(element)
            
        else:
            text = ["Do not recognise Element Type. Must be QWidget, ",
                    "QLayout or QSpacerItem. Got type '%s." %type(element)]
            raise TypeError(''.join(text))
        
    
    # --------------------------------------------------------------------------------------- #       
    
    @property
    def title(self):
        return self._title
    
    
    @title.setter
    def title(self, title):
        '''
            Property setter for page title.
        
        args :
            title : the name of the page
        '''        
        self._title = str(title).title()
        self.title_label.setText(self._title.upper())
    
    
    @property
    def subtitle(self):
        return self._subtitle
    
    
    @subtitle.setter
    def subtitle(self, subtitle):
        '''
            Property setter for page subtitle.
        
        args :
            subtitle : the name of the page
        '''
        if not subtitle:
            self.page_widget.layout().setContentsMargins(4,0,4,2)
            self._subtitle = ''
            self.subtitle_label.setText('')
            self.subtitle_label.setVisible(False)
            self.right_subtitle_splitter.setVisible(False)
            return
            
        self._subtitle = str(subtitle).title()
        self.subtitle_label.setText(self._subtitle)
        self.subtitle_label.setVisible(True)
        self.right_subtitle_splitter.setVisible(True)
        
        # adjust page margins
        #
        self.page_widget.layout().setContentsMargins(4,2,4,2)
        
        
    @property
    def full_title(self):
        '''
            Return full title of the Page.
        '''
        return '%s - %s' %(self._title, self._subtitle)
    
    # --------------------------------------------------------------------------------------- #  

    def setTearable(self, value):
        '''
            Toggle the visibility of the tear and attach buttons.
        '''
        if not isinstance(value, bool):
            return 
        
        self.tear_bttn.setVisible(value)
        self.attach_bttn.setVisible(value)       
        

    def setFloating(self, value):
        ''' 
            Toggle button layout for floating/not floating.
        '''
        self.back_bttn.setEnabled(not(value))
        self.tear_bttn.setVisible(not(value))
        self.attach_bttn.setVisible(value)
        
        if value:
            self.emit(qc.SIGNAL(Page.TEAR), self)
        else:
            self.emit(qc.SIGNAL(Page.ATTACH), self)
            
            
    def isDocked(self):
        '''
            Returns whether the page is currently docked or floating.
        '''
        return self.docked  
            
    # --------------------------------------------------------------------------------------- #   
           
    def show(self):
        self.setVisible(True)      
        

    def hide(self):
        self.setVisible(False)
        
        
    def hideBackButton(self, value):
        self.hideButton('back', not(value))
        
        
    def hideCloseButton(self, value):
        self.hideButton('close', not(value))
        
        
    def hideRefreshButton(self, value):
        self.hideButton('refresh', not(value))
        
        
    def hideSettingsButton(self, value):
        self.hideButton('settings', not(value))
        
        
    def hideButton(self, button_key, value):
        try:
            self._buttons[button_key].setVisible(bool(value))
        except KeyError:
            raise TypeError("Button '%s' does not exist." %button_key)
        
        
    def refresh(self):
        self.emit(qc.SIGNAL(self.REFRESH), self)
        
    # --------------------------------------------------------------------------------------- #
    
    @property
    def id(self):
        '''
            Property returning page ID. IDs are unique, and assigned dynamically on creation. 
        '''
        return self._page_id


    @property
    def previous_page(self):
        '''
            Returns the previous page, if it exists.
        '''
        if self._prev_page is None:
            return None
        return self._prev_page.getSelf()


    @previous_page.setter
    def previous_page(self, prev_page):
        '''
            Set the previous page.
        '''
        if prev_page is None:
            self._prev_page = None; return
        
        if not isinstance(prev_page, Page):
            raise Exception("Next Page must be a Page instance.")        
        self._prev_page = proxy(prev_page)
        
    # --------------------------------------------------------------------------------------- #
    
    @property
    def settings_widget(self):
        return self._settings_widget
    
    
    @settings_widget.setter
    def settings_widget(self, widget):        
        self._settings_widget = widget
        self.settings_bttn.clicked.connect(self._displaySettings)
        
    
    def _displaySettings(self):
        widget = self._settings_widget()
        answer = widget.exec_()
        print answer

    # --------------------------------------------------------------------------------------- #

    def _back(self):
        self.emit(qc.SIGNAL(Page.BACK), self.previous_page)
        
        
    def _close(self):
        self.emit(qc.SIGNAL(Page.CLOSE), self)
        
        
    def getSelf(self):
        return self
        
    # --------------------------------------------------------------------------------------- #

    def __del__(self):
        if self.subtitle is not '':
            print 'Closing %s - %s...' %(self._title, self.subtitle)
        else:
            print 'Closing %s...' %self._title
        
# ------------------------------------------------------------------------------------------------ 