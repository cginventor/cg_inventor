import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import re, inspect
from functools import partial

import cg_inventor.sys.lib.qt.base                        as base
import cg_inventor.sys.lib.qt.buttons.status_light_button as status_light_button
import cg_inventor.sys.lib.qt.buttons.icon_button         as icon_button
import cg_inventor.sys.lib.qt.misc.splitter               as splitter

import cg_inventor.maya.utils.generic as util_generic


force_stop = False

# ------------------------------------------------------------------------------------------------ #

class SceneCheckError(Exception):
    pass


class SceneCheckForceStop(Exception):
    pass

# ------------------------------------------------------------------------------------------------ #
#                                       SCENE CHECK LIGHT                                          #
# ------------------------------------------------------------------------------------------------ #

class SceneCheckLight(status_light_button.StatusLightButton):
    SUCCESS = 'SUCCESS'
    FAILED  = 'FAILED'
    IGNORE  = 'IGNORE'

    def __init__(self):
        status_light_button.StatusLightButton.__init__(self)
        
        self.addStatusColour(self.SUCCESS, (133, 230, 26))
        self.addStatusColour(self.FAILED,  (255,  38,  0))
        self.addStatusColour(self.IGNORE,  (255, 242,  0))
        
        self.setClickedStatus(self.IGNORE)


# ------------------------------------------------------------------------------------------------ #
#                                     SCENE CHECK MESSAGES                                         #
# ------------------------------------------------------------------------------------------------ #        
        
class SceneCheckMessages():
    title  = None
    single = None
    mult   = None


# ------------------------------------------------------------------------------------------------ #
#                                         SCENE CHECK                                              #
# ------------------------------------------------------------------------------------------------ #

class SceneCheck(qg.QWidget, base.Base):    
    FUNC_CHECK  = 'check'
    FUNC_SELECT = 'select'
    FUNC_FIX    = 'fix'
    
    NOT_CHECKED = 1
    CHECKED     = 2
    FIXED       = 3
    
    MODE_SEL    = 'MODE_SEL'
    MODE_ALL    = 'MODE_ALL'
    

    def __init__(self):
        qg.QWidget.__init__(self)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.setFixedHeight(26)
        
        self.setFocusPolicy(qc.Qt.StrongFocus)
        
        self.status_light = SceneCheckLight()        
        
        self.title_label = qg.QLabel('No Title')    
        self.fail_label  = qg.QLabel()
        self.fail_label.hide()
        self.fail_label.setObjectName('fail_label')
        self.fail_label.setStyleSheet('QLabel#fail_label{color: rgba(180,0,0,255);}')
        
        label_layout = qg.QVBoxLayout()
        label_layout.setContentsMargins(0,0,0,0)
        label_layout.setSpacing(0)
        label_layout.addWidget(self.title_label)
        label_layout.addWidget(self.fail_label)

        # setup check, select and fix functions
        #
        self._functions      = {self.FUNC_CHECK:None,  self.FUNC_SELECT:None,  self.FUNC_FIX:None}
        self._buttons        = {self.FUNC_CHECK:None,  self.FUNC_SELECT:None,  self.FUNC_FIX:None}
        self._button_spacers = {self.FUNC_CHECK:None,  self.FUNC_SELECT:None,  self.FUNC_FIX:None}
        self._func_callbacks = {self.FUNC_CHECK:False, self.FUNC_SELECT:False, self.FUNC_FIX:False}
        
        self._message   = SceneCheckMessages()
  
        # setup buttons
        #
        check_button = icon_button.IconButton()
        check_button.setImage(':gui/play.png')
        check_button.setVisible(False)
        self._buttons[self.FUNC_CHECK] = check_button

        select_button = icon_button.IconButton()
        select_button.setImage(':gui/select.png')
        select_button.setVisible(False)
        select_button.setEnabled(False)
        self._buttons[self.FUNC_SELECT] = select_button

        fix_button = icon_button.IconButton()
        fix_button.setImage(':gui/hammer.png')
        fix_button.setVisible(False)
        fix_button.setEnabled(False)
        self._buttons[self.FUNC_FIX] = fix_button
        
        button_layout = qg.QHBoxLayout()
        self.layout().addLayout(button_layout)
        
        check_spacer = qg.QSpacerItem(26, 26, qg.QSizePolicy.Fixed)
        self._button_spacers[self.FUNC_CHECK] = check_spacer
        
        select_spacer = qg.QSpacerItem(26, 26, qg.QSizePolicy.Fixed)
        self._button_spacers[self.FUNC_SELECT] = select_spacer
        
        fix_spacer = qg.QSpacerItem(26, 26, qg.QSizePolicy.Fixed)
        self._button_spacers[self.FUNC_FIX] = fix_spacer
        
        button_layout.addWidget(self.status_light)
        button_layout.addLayout(label_layout)
        button_layout.addWidget(check_button)
        button_layout.addSpacerItem(check_spacer)        
        button_layout.addWidget(select_button)
        button_layout.addSpacerItem(select_spacer)
        button_layout.addWidget(fix_button)
        button_layout.addSpacerItem(fix_spacer)
        
        self.status_light.clicked.connect(self.ignore)
        self._buttons[self.FUNC_CHECK ].clicked.connect(partial(self.run, self.FUNC_CHECK))
        self._buttons[self.FUNC_SELECT].clicked.connect(partial(self.run, self.FUNC_SELECT))
        self._buttons[self.FUNC_FIX   ].clicked.connect(partial(self.run, self.FUNC_FIX))
        
        self._check_status   = self.NOT_CHECKED
        self._selection_mode = self.MODE_ALL
        self._enabled        = True
        self._fixError       = ''
        self._returns        = None
        self._failed         = True   
        
    #-----------------------------------------------------------------------------------------#
    
    def ignore(self):
        value = self._enabled = not(self._enabled)
        self.title_label.setEnabled(value)
        self.fail_label.setEnabled(value)
        self.enableAllButtons(value)        
        
        if value is False:
            self.fail_label.setStyleSheet('QLabel#fail_label{color: rgba(100,20,20,255);}')            
        else:
            self.fail_label.setStyleSheet('QLabel#fail_label{color: rgba(180,0,0,255);}')
            
        qg.QApplication.processEvents()
        
    #-----------------------------------------------------------------------------------------#
    
    @property
    def selection_mode(self):
        return self._selection_mode
    
    
    @selection_mode.setter
    def selection_mode(self, selection_mode):
        if selection_mode not in [self.MODE_SEL, self.MODE_ALL]:
            raise SceneCheckError("Do not recognise selection type '%s'." %type)           
        
        self._selection_mode = selection_mode
        
    #-----------------------------------------------------------------------------------------#
    
    def loadFromLibrary(self, function_set):
        title, message, _ = SceneCheckLibrary.getSetup(function_set)
        
        self.title        = title
        self.message      = message
        self.function_set = function_set
        
    #-----------------------------------------------------------------------------------------#
   
    @property
    def title(self):
        return self._message.title
    
    
    @title.setter
    def title(self, title):
        self._message.title = title
        self.setLabel(title)
        
        
    def setLabel(self, text):
        self.title_label.setText(text)
        
    #-----------------------------------------------------------------------------------------#
    
    @property
    def message(self):
        return self._message
    

    @message.setter
    def message(self, msg):
        # find all multi tags
        #
        mult_tags = re.findall('\([a-zA-Z0-9_]+\)', msg)
        single_msg = msg = msg.replace('$NUM', '%s')

        # remove all multi tags from message
        #
        for tag in mult_tags:
            single_msg = single_msg.replace(tag, '')
        
        mult_msg = msg.replace('(', '').replace(')','')        
        
        self._message.single = single_msg
        self._message.mult   = mult_msg
        
    #-----------------------------------------------------------------------------------------#    

    @property
    def function_set(self):
        return self._functions
    
    
    @function_set.setter
    def function_set(self, function_set):
        check, select, fix = SceneCheckLibrary.getFunctions(function_set)
        for func, func_type in ((check , self.FUNC_CHECK),
                                (select, self.FUNC_SELECT),
                                (fix   , self.FUNC_FIX)):
            self._functions[func_type] = func
            if func is None: continue
            
            func_args = inspect.getargspec(func)[0]
            if 'callback' in func_args:
                self._func_callbacks[func_type] = True
            
            self._button_spacers[func_type].changeSize(0,0, qg.QSizePolicy.Fixed)
            self._buttons[func_type].setVisible(True)
    
    
    def hasFunction(self, func_type):
        return(bool(self._functions[func_type]))

    #-----------------------------------------------------------------------------------------#  

    def enableButton(self, button_type, value):
        if button_type not in self._buttons.keys():
            raise SceneCheckError("Do not recognise button type '%s'." %button_type)

        if button_type in [self.FUNC_SELECT, self.FUNC_FIX]:
            if self._returns and value:
                self._buttons[button_type].setEnabled(True)
            else:
                self._buttons[button_type].setEnabled(False)
        else:
            self._buttons[button_type].setEnabled(bool(value))


    def enableAllButtons(self, value):
        value = bool(value)
        self.enableButton(self.FUNC_CHECK,  value)
        self.enableButton(self.FUNC_SELECT, value)
        self.enableButton(self.FUNC_FIX,    value)

    #-----------------------------------------------------------------------------------------#  

    def _printError(self, message):
        self.setErrorMessage()
        print(util_generic.formatError(message))

    #-----------------------------------------------------------------------------------------#
    
    def run(self, func_type):
        global force_stop
        force_stop = False
        self._run(func_type)
    
    def _run(self, func_type):     
        # check function type
        #
        if func_type not in self._functions.keys():
            raise SceneCheckError("Do not recognise function type '%s'." %func_type)

        # if no function is assigned
        #
        if not self._functions[func_type]:
            raise SceneCheckError("Function '%s' not set." %func_type)

        # run selection
        #
        if func_type in [self.FUNC_SELECT, self.FUNC_FIX]:
            # already fixed so return
            #
            if self._check_status == self.FIXED:
                return
            
            # cannot run select or fix functions if check has not been run
            #
            if not self.return_nodes or self._check_status != self.CHECKED:
                raise SceneCheckError("Check function has not been run.")
            
        else:
            # turn off status light
            #
            self.status_light.setStatus(self.status_light.DEFAULT, mode=self.status_light.ANIM_LOCK)
            self._buttons[func_type].setEnabled(False)
            qg.QApplication.processEvents()

        # get return nodes or run select/fix
        #
        res = None        

        # enable relevant button
        #
        self._buttons[func_type].setEnabled(True)
        
        try:            
            if func_type == self.FUNC_CHECK:
                self.statusNormal("Checking For %s..." %self._message.title)
                kwargs = {}
                if self._func_callbacks[func_type] is True:
                    kwargs = {'callback' : self._callback}
                    
                res = self._functions[func_type](self._selection_mode, **kwargs)
                
                if res:
                    self.return_nodes = res
    
                    for func in [self.FUNC_SELECT, self.FUNC_FIX]:
                        if self._functions[func]:
                            self._buttons[func].setEnabled(True)
                            
                    self._check_status = self.CHECKED
                    self.status_light.setStatus(self.status_light.FAILED)
                    self.showMessage()
                    
                else:
                    self.setLabel(self._message.title)
                    self._buttons[self.FUNC_SELECT].setEnabled(False)
                    self._buttons[self.FUNC_FIX].setEnabled(False)
                    self._check_status = self.FIXED
                    self.status_light.setStatus(self.status_light.SUCCESS)
    
    
            elif func_type == self.FUNC_SELECT:
                self._functions[self.FUNC_SELECT](self.return_nodes)
    
    
            elif func_type == self.FUNC_FIX:
                self._functions[self.FUNC_FIX](self.return_nodes)
                
                # rerun check function after fixing
                #
                self._run(self.FUNC_CHECK)
                
        except SceneCheckError as e:
            self._printError(str(e))
            self.return_nodes = None
            
        except SceneCheckForceStop:
            self.statusError("%s Check Cancelled by User" %self.title.title())
            self.setStoppedMessage()
            
        except Exception:
            self._printError(util_generic.getTraceback())
            self.return_nodes = None
            
    #-----------------------------------------------------------------------------------------#  

    def showMessage(self):
        num_nodes = len(self.return_nodes)
        if num_nodes == 0: return
        
        if num_nodes > 1:
            if not self._message.mult:
                self.setLabel('%s - %s Nodes' %(self.title, num_nodes))
            else:
                self.setLabel(self._message.mult %num_nodes)
        else:
            if not self.message.single:
                self.setLabel('%s - %s Node' %(self.title, num_nodes))
            else:
                self.setLabel(self._message.single %num_nodes)    
    
    
    def reset(self):
        self.setLabel(self._message.title)
        self._check_status = self.NOT_CHECKED
        self.status_light.setStatus(self.status_light.DEFAULT)
        
    
    def setErrorMessage(self):
        self.setLabel('%s - <font color="red">Error</font>' %self._message.title)
        
        
    def setStoppedMessage(self):
        self.setLabel('%s - <font color="yellow">Cancelled</font>' %self._message.title)
        
    #-----------------------------------------------------------------------------------------#        

    def _callback(self, value):
        global force_stop
        if force_stop == True:
            raise SceneCheckForceStop
        qg.QApplication.processEvents()
        
        
    def keyPressEvent(self, event):
        if event.key() == qc.Qt.Key_Escape:
            global force_stop
            force_stop = True
        
        qg.QWidget.keyPressEvent(self, event)
        
        
        
        
# ------------------------------------------------------------------------------------------------ #
#                                      SCENE CHECK SET                                             #
# ------------------------------------------------------------------------------------------------ #
        
class SceneCheckSet(qg.QWidget, base.Base):
    FUNC_CHECK  = 'check'
    FUNC_SELECT = 'select'
    FUNC_FIX    = 'fix'
    
    MODE_SEL    = 'MODE_SEL'
    MODE_ALL    = 'MODE_ALL'
    
    def __init__(self, title='Untitled'):
        qg.QWidget.__init__(self)
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        
        self.setFocusPolicy(qc.Qt.StrongFocus)
        
        title_bar =  qg.QWidget()
        title_bar.setFixedHeight(12)
        title_bar.setLayout(qg.QHBoxLayout())
        title_bar.layout().setContentsMargins(5,0,5,0)
        title_bar.layout().setSpacing(0)
        self.layout().addWidget(title_bar)

        self.title_label = qg.QLabel()
        self.title_label.setFixedHeight(12)
        title_font = qg.QFont()
        title_font.setBold(True)
        self.title_width = qg.QFontMetrics(title_font)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(qc.Qt.AlignHCenter)
        
        title_splitter = splitter.Splitter()
        title_splitter.setMainColour(100, 100, 100)
        title_splitter.addWidget(self.title_label)
        title_bar.layout().addWidget(title_splitter)
                
        self.check_widget = qg.QWidget()
        self.check_widget.setLayout(qg.QVBoxLayout())
        self.check_widget.layout().setContentsMargins(0,0,0,0)
        self.check_widget.layout().setSpacing(0)
        self.setObjectName('check_widget')
        
        self.layout().addWidget(self.check_widget)
        
        # setup buttons
        #
        self._buttons = {self.FUNC_CHECK:None, self.FUNC_SELECT:None, self.FUNC_FIX:None}

        all_label = qg.QLabel('Run All')
        
        check_button = icon_button.IconButton()
        check_button.setImage(':gui/play_all.png')
        self._buttons[self.FUNC_CHECK] = check_button

        select_spacer = qg.QSpacerItem(26, 26, qg.QSizePolicy.Fixed)

        fix_button = icon_button.IconButton()
        fix_button.setImage(':gui/hammer_all.png')
        self._buttons[self.FUNC_FIX] = fix_button
        
        foot_splitter = splitter.Splitter()
        foot_splitter.setMainColour(60,60,60)
        foot_splitter.showShadow(False)
        foot_splitter.setFixedHeight(1)
        foot_splitter_layout = qg.QHBoxLayout()
        foot_splitter_layout.setContentsMargins(5,0,5,0)
        foot_splitter_layout.addWidget(foot_splitter)
        
        self.layout().addLayout(foot_splitter_layout)
        
        self.button_widget = qg.QWidget()
        self.button_widget.setLayout(qg.QHBoxLayout())
        self.button_widget.layout().setSpacing(0)
        self.button_widget.layout().setContentsMargins(0,0,0,0)
        self.button_widget.layout().addSpacerItem(qg.QSpacerItem(26,20,qg.QSizePolicy.Fixed))
        self.button_widget.layout().addWidget(all_label)
        self.button_widget.layout().addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Expanding))
        self.button_widget.layout().addWidget(check_button)
        self.button_widget.layout().addSpacerItem(select_spacer)
        self.button_widget.layout().addWidget(fix_button)
        self.layout().addWidget(self.button_widget)
        
        self._buttons[self.FUNC_CHECK].clicked.connect(self._checkAll)
        self._buttons[self.FUNC_FIX  ].clicked.connect(self._fixAll)        
        
        if title:
            self.setTitle(title)
            
        self._checks = []
        self._selection_mode = self.MODE_ALL
    
    #------------------------------------------------------------------------------------------#    
    
    def setTitle(self, title):
        width = self.title_width.width(title.upper()) + 6
        self.title_label.setMaximumWidth(width)
        self.title_label.setText(title.upper())

    #------------------------------------------------------------------------------------------#        
    
    def addSceneCheck(self, scene_check):
        self.check_widget.layout().addWidget(scene_check)
        self._checks.append(scene_check)
        self.connect(scene_check, qc.SIGNAL(base.Base.STATUS_NORMAL),  self.statusNormal)
        self.connect(scene_check, qc.SIGNAL(base.Base.STATUS_SUCCESS), self.statusSuccess)
        self.connect(scene_check, qc.SIGNAL(base.Base.STATUS_ERROR),   self.statusError)
    
    #------------------------------------------------------------------------------------------#
    
    def setSelectionMode(self, mode):
        if mode not in [self.MODE_SEL, self.MODE_ALL]:
            raise("Do not recognise Selection Type '%s'." %mode)
        
        self._selection_mode = mode
        
        for check in self.checks:
            check.selection_mode = mode
            
    #------------------------------------------------------------------------------------------#

    def _checkAll(self):
        global force_stop
        force_stop = False
        
        for check in self._checks:
            if not check._enabled: continue
            
            check._run(self.FUNC_CHECK)
            qg.QApplication.processEvents()
            
            if force_stop is True: break
            
        title = str(self.title_label.text()).title()
        
        if force_stop is True:
            self.statusNormal("%s Checks Cancelled by User" %title)
            force_stop = False
            return 
        
        self.statusSuccess('%s Checks Complete' %title)
        
    
    def _fixAll(self):
        global force_stop
        force_stop = False
        
        for check in self._checks:
            if check._check_status != check.CHECKED: continue
            if not check.hasFunction(self.FUNC_FIX): continue
            
            check._run(self.FUNC_FIX)
            qg.QApplication.processEvents()
            
            if force_stop is True: break
                    
        title = str(self.title_label.text()).title()
        
        if force_stop is True:
            self.statusNormal("%s Fixes Stopped by User" %title)
            force_stop = False
            return 
        
        self.statusSuccess('%s Fixes Complete' %title)
        

    #------------------------------------------------------------------------------------------#
        
    def keyPressEvent(self, event):
        if event.key() == qc.Qt.Key_Escape:
            global force_stop
            force_stop = True
        
        qg.QWidget.keyPressEvent(self, event)


# ------------------------------------------------------------------------------------------------ #
#                                   SCENE CHECK CATEGORY                                           #
# ------------------------------------------------------------------------------------------------ #

class SceneCheckCategory(qg.QWidget):
    def __init__(self, title='Untitled'):
        qg.QWidget.__init__(self)
        self.setFixedHeight(14)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        
        self.category_label = qg.QLabel()
        self.category_label.setFixedHeight(12)
        category_font = qg.QFont()
        category_font.setBold(True)
        self.category_label.setFont(category_font)
        
        self.layout().addSpacerItem(qg.QSpacerItem(8,5,qg.QSizePolicy.Fixed))
        self.layout().addWidget(self.category_label)
        self.layout().addSpacerItem(qg.QSpacerItem(5,5,qg.QSizePolicy.Expanding))
        
        if title:
            self.setTitle(title)
        
    
    def setTitle(self, title):
        self.category_label.setText(title.upper())


# ------------------------------------------------------------------------------------------------ #
#                                     FUNCTION LIBRARY                                             #
# ------------------------------------------------------------------------------------------------ #

class SceneCheckLibrary():
    setup   = {}
    checks  = {}
    selects = {}
    fixes   = {}
    
    @staticmethod
    def clear():
        SceneCheckLibrary.setup   = {}
        SceneCheckLibrary.checks  = {}
        SceneCheckLibrary.selects = {}
        SceneCheckLibrary.fixes   = {}


    @staticmethod
    def getFunctions(function_set):
        try:
            check_func = SceneCheckLibrary.checks[function_set]
        except KeyError:
            check_func = None
            
        try:
            select_func = SceneCheckLibrary.selects[function_set]
        except KeyError:
            select_func = None
            
        try:
            fix_func = SceneCheckLibrary.fixes[function_set]
        except KeyError:
            fix_func = None
            
        return check_func, select_func, fix_func
    
    
    @staticmethod
    def getSetup(function_set):         
        try:
            title, message, description = SceneCheckLibrary.setup[function_set]()
        except KeyError:
            title       = 'Untitled'
            message     = "Found $NUM Item(s)"
            description = "No Description"
        
        return title, message, description
        
#--------------------------------------------------------------------------------------------------#

def setup(func):
    SceneCheckLibrary.setup[func.__name__] = func
    return func
 

def check(func): 
    SceneCheckLibrary.checks[func.__name__] = func
    return func


def select(func):
    SceneCheckLibrary.selects[func.__name__] = func
    return func


def fix(func):
    SceneCheckLibrary.fixes[func.__name__ ] = func
    return func
    