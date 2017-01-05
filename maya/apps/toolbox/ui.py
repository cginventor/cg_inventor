import PyQt4.QtCore as qc
import PyQt4.QtGui  as qg

import os, gc
from functools import partial

import maya.cmds as mc

import cg_inventor.sys.lib.constants  as cnst
import cg_inventor.sys.lib.qt.signals as sig

import cg_inventor.maya.utils.qt             as util_qt
import cg_inventor.maya.apps.toolbox.library as lib

# window strings
#
UI_NAME     = "Toolbox"
UI_VERSION  = "1.3"
TAB_NAME    = '%s %s' %(cnst.BRAND_NAME, UI_NAME)
WINDOW_NAME = '%s v%s' %(TAB_NAME, UI_VERSION)
LOGO        = None

# default sizes
#
WINDOW_WIDTH  = 350
WINDOW_HEIGHT = 500

# status colours
#
STATUS_COLOUR = {sig.STATUS_NORMAL  : '#ffffff',
                 sig.STATUS_SUCCESS : '#00ff00',
                 sig.STATUS_ERROR   : '#ff0000'}

# ------------------------------------------------------------------------------------------------ #

class ToolboxError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#
#                                          MAIN GUI                                                #
#--------------------------------------------------------------------------------------------------#

class Toolbox(qg.QDialog):
    _dock_widget = None
    _docked      = False


    def __init__(self, *args, **kargs):
        qg.QDialog.__init__(self, *args, **kargs)
        qg.QDialog.setWindowFlags(self, qc.Qt.WindowStaysOnTopHint)

        # setup window attributes
        #
        self.setFocusPolicy(qc.Qt.NoFocus)
        self.setFixedWidth(WINDOW_WIDTH)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_NAME)
        self.setObjectName(UI_NAME)

        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 1)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setStyleSheet('QDialog#%s { background-color : rgba(30,30,30,255);}' %UI_NAME)

        # create ui title layout
        #
        title_font = qg.QFont()
        title_font.setBold(True)
        title_font.setPixelSize(14)
        brand_label = qg.QLabel('<font color="white">%s</font>' %cnst.BRAND_NAME)
        brand_label.setFont(title_font)
        brand_label.setFixedHeight(20)
        title_label = qg.QLabel('<font color="white">%s v%s</font>' %(UI_NAME, UI_VERSION))
        title_label.setFont(title_font)
        title_label.setFixedHeight(20)

        self.title_widget = qg.QWidget()
        title_layout = qg.QHBoxLayout()
        self.title_widget.setLayout(title_layout)
        title_layout.setContentsMargins(0,2,0,2)
        title_layout.addWidget(brand_label)
        title_layout.addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        title_layout.addWidget(title_label)
        self.layout().addWidget(self.title_widget)

        self.main_frame = qg.QFrame()
        self.main_frame.setParent(self.parent())
        self.main_frame.setObjectName('main_frame')
        self.main_frame.setStyleSheet('QFrame#main_frame {background-color : rgba(68,68,68,255);}')
        self.main_frame.setFrameStyle(qg.QFrame.Panel|qg.QFrame.Raised)
        self.main_frame.setSizePolicy(qg.QSizePolicy.Expanding, qg.QSizePolicy.Expanding)
        self.main_frame.setLayout(qg.QVBoxLayout())
        self.main_frame.layout().setContentsMargins(1,1,1,1)
        self.main_frame.layout().setSpacing(0)
        #self.main_frame.layout().setAlignment(qc.Qt.AlignTop)
        self.layout().addWidget(self.main_frame)

        self.graphics_scene = qg.QGraphicsScene()
        self.graphics_view = ToolboxGraphicsView(self.graphics_scene)
        self.graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        style = ['border-style: none;', 'background: transparent;']
        self.graphics_view.setStyleSheet("QGraphicsView {%s}"  %' '.join(style))
        self.graphics_view.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        self.main_frame.layout().addWidget(self.graphics_view)

        self._page_widget = qg.QWidget()
        self._page_widget.setLayout(qg.QVBoxLayout())
        self._page_widget.layout().setContentsMargins(0,0,0,0)
        self._page_widget.layout().setSpacing(0)
        self._page_widget_item = self.graphics_scene.addWidget(self._page_widget)
        self.graphics_view.main_widget = self._page_widget

        self.status_widget = qg.QWidget()
        self.status_widget.setLayout(qg.QHBoxLayout())
        self.status_widget.layout().setContentsMargins(0,0,0,0)
        self.status_widget.layout().setSpacing(0)
        self.status_label = qg.QLabel('Status: ')
        self.status_label.setFixedHeight(20)
        self.status_widget.layout().addWidget(self.status_label)
        self.status_widget.layout().addSpacerItem(qg.QSpacerItem(5, 5, qg.QSizePolicy.Expanding))
        self.layout().addWidget(self.status_widget)

        self.showTitle(False)

        self._main_menu        = None
        self._main_menu_lookup = {}
        self._current_page     = None
        self._page_anim        = None

        self._page_stack  = set([])
        self._dialogs     = {}

        # load pages into memory
        #
        lib.load()

        # create main menu
        #
        self._loadMainMenu()

    # --------------------------------------------------------------------------------------- #

    def _loadMainMenu(self):
        '''
            Load Main Menu page from 'main_menu.xml', and add to toolbox.
        '''

        self._main_menu = lib.Page('Menu')
        self._main_menu.title = 'Main Menu'
        self._main_menu.hideBackButton(True)
        self._main_menu.hideCloseButton(True)
        self._main_menu.setTearable(False)
        self._main_menu.buildFromXML('main_menu.xml')

        self._addPage(self._main_menu, show=True)
        self.connect(self._main_menu,
                     qc.SIGNAL(self._main_menu.MENU_ITEM_CLICKED),
                     self._loadMenuPage)

        self._main_menu_lookup = {}

        # disable menu items with erroneous page classes
        #
        for menu_group in self._main_menu.getAllMenuGroups():
            for menu_item in menu_group.getAllMenuItems():
                if not lib.exists(menu_item.data[0]):
                    menu_item.disable()


    def _loadMenuPage(self, menu_item_id, page_class):
        '''
            Runs when a menu item is clicked. Either shows existing page or creates it.

        args :
            menu_item_id : the id of the menu item. Assigned dynamically by the menu.
            page_class   : the page class to create.
        '''

        try:
            page = self._main_menu_lookup[menu_item_id]
            page_title = page.full_title
            try:
                # is page floating
                #
                self.setNormalStatus("%s is floating. Bringing dialog to front." %page_title)
                dialog = self._dialogs[page.id]
                dialog.raise_()
                dialog.activateWindow()
            except KeyError:
                # show page in toolbox
                #
                self.setNormalStatus("Displaying %s" %page_title)
                self._showPage(page)


        except KeyError:
            new_page = self._main_menu_lookup[menu_item_id] = lib.Page(page_class)
            new_page_title = new_page.full_title

            self.setNormalStatus("Loading %s..." %new_page_title)
            self._addPage(new_page, show=True)
            self.setSuccessStatus("Loaded %s" %new_page_title)

    # --------------------------------------------------------------------------------------- #

    def _addPage(self, page, show=True, add=True):
        '''
            When a new page is created it must first be connected to the toolbox, and added
            to its main layout. Once added, if show is True, it will display the given page.

        args :
            page : a page instance to add to the main layout.

        kwargs :
            show = True : if True, the page is displayed after adding.
        '''

        # add to main layout
        #
        if add is True:
            page.setVisible(False)
            #self.main_frame.layout().addWidget(page)
            self._page_widget.layout().addWidget(page)

        # connect page signals to toolbox
        #
        self.connect(page, qc.SIGNAL(page.BACK),    self._showPage)
        self.connect(page, qc.SIGNAL(page.CLOSE),   self._deletePage)
        self.connect(page, qc.SIGNAL(page.TEAR),    self._tearPage)
        self.connect(page, qc.SIGNAL(page.ATTACH),  self._attachPage)
        self.connect(page, qc.SIGNAL(page.REFRESH), self._refreshPage)
        self.connect(page, qc.SIGNAL(page.STATUS_NORMAL),  self.setNormalStatus)
        self.connect(page, qc.SIGNAL(page.STATUS_SUCCESS), self.setSuccessStatus)
        self.connect(page, qc.SIGNAL(page.STATUS_ERROR),   self.setErrorStatus)


        if show is True:
            self._showPage(page)
        else:
            page.hide()


    def _showPage(self, page, tear=False):
        '''
            Display the given page. Sets the new page 'previous page' to the current page,
            and then sets the new page as current. This allows the 'back' button to work.

        args:
            page : a page instance to display.
        '''

        # if requested page is already current, just show page
        #
        if self._current_page is page:
            self._page_stack.add(page)
            self._current_page.show()
            return

        # if there is no current page, set page
        #
        if self._current_page is None:
            page.previous_page = None

            self._page_stack.add(page)
            self._current_page = page
            self._current_page.show()
            return

        # if page in page stack already, jump to that page
        #
        if page in self._page_stack:
            #self._current_page.hide()

            current_page = self._current_page
            while current_page != page:
                previous_page = current_page.previous_page
                self._page_stack.remove(current_page)

                if previous_page == None or len(self._page_stack) == 0:
                    raise ToolboxError("Failed to show requested page.")

                current_page = previous_page

            self._animatedShowPage(self._current_page, page, tear=tear)
            self._current_page = page
            #self._current_page.show()

        else:
            page.previous_page = self._current_page
            self._page_stack.add(page)

            self._animatedShowPage(self._current_page, page, tear=tear)

            #self._current_page.hide()
            self._current_page = page
            #self._current_page.show()


    def _animatedShowPage(self, from_page, to_page, tear=False):
        opacity_fade_out = qc.QPropertyAnimation(self._page_widget_item, "opacity")
        opacity_fade_out.setStartValue(1.0); opacity_fade_out.setEndValue(0.0)
        opacity_fade_out.setDuration(200)

        opacity_fade_in = qc.QPropertyAnimation(self._page_widget_item, "opacity")
        opacity_fade_in.setStartValue(0.0); opacity_fade_in.setEndValue(1.0)
        opacity_fade_in.setDuration(200)

        self._page_anim = None
        self._page_anim = qc.QSequentialAnimationGroup()
        if tear is False:
            self._page_anim.addAnimation(opacity_fade_out)
            self._page_anim.addAnimation(opacity_fade_in)

            opacity_fade_out.finished.connect(from_page.hide)
            opacity_fade_out.finished.connect(to_page.show)
        else:
            self._page_anim.addAnimation(opacity_fade_in)
            to_page.show()

        self._page_anim.start()
        #self.connect(self._page_anim, qc.SIGNAL('finished'), self._page_anim.)



    def _removePage(self, page, tear=False):
        '''
            Remove the given page from the layout.

        args :
            page : the page instance to remove.
        '''

        # if page instance is the main menu, raise error
        #
        if page is self._main_menu:
            raise ToolboxError("Cannot remove Main Menu.")

        # if page instance is the current page, display previous
        #
        if page is self._current_page:
            self._showPage(page.previous_page, tear=tear)

        # else find the next page after page, and connect to previous
        #
        elif page in self._page_stack:
            current_page = self._current_page
            while current_page.previous_page is not page:
                current_page = current_page.previous_page

                if current_page is None:
                    raise ToolboxError("Could not remove request page.")

            current_page.previous_page = page.previous_page

        # remove page from main layout
        #
        #self.main_frame.layout().removeWidget(page)
        self._page_widget.layout().removeWidget(page)


    def _deletePage(self, page):
        self._removePage(page)
        menu_item_id = None
        for item_id, item_page in self._main_menu_lookup.items():
            if item_page is page:
                menu_item_id = item_id; break

        if menu_item_id is not None:
            del(self._main_menu_lookup[menu_item_id])

        page.deleteLater()


    # --------------------------------------------------------------------------------------- #

    def _tearPage(self, page):
        '''
            Remove the given instance from the toolbox and display in its own dialog.

        args :
            page : the instance to display.
        '''

        # is page already torn
        #
        try:
            page_id = page.id
            self._dialogs[page_id]
            raise ToolboxError("Failed to tear off page.")
        except KeyError:
            pass

        # remove page from main dialog
        #
        self._removePage(page, tear=True)

        # calculate dialog position
        #
        toolbox_pos = self.pos()

        if self._dock_widget:
            dock_pos = self._dock_widget.pos()
            if not self._dock_widget.isFloating():
                toolbox_pos.setX(dock_pos.x() + toolbox_pos.x())
                toolbox_pos.setY(dock_pos.y() + toolbox_pos.y() + 1)
            else:
                toolbox_pos.setX(dock_pos.x() + toolbox_pos.x() + 1)
                toolbox_pos.setY(dock_pos.y() + toolbox_pos.y() - 3)
        else:
            toolbox_pos.setX(toolbox_pos.x() + 3)
            toolbox_pos.setY(toolbox_pos.y() + 1)

        frame_size  = self.main_frame.geometry()
        frame_pos   = self.main_frame.pos()
        main_window = util_qt.getMayaWindow()
        main_pos    = main_window.pos()

        frame_pos.setX(frame_pos.x() + toolbox_pos.x() + main_pos.x())
        frame_pos.setY(frame_pos.y() + toolbox_pos.y() + main_pos.y())

        # create new dialog at position
        #
        new_dialog = ToolboxDialog(page, frame_size, frame_pos)
        self.connect(new_dialog, qc.SIGNAL(new_dialog.CLOSE), self._dialogClose)
        self._dialogs[page_id] = new_dialog
        new_dialog.show()

        new_dialog.raise_()
        new_dialog.activateWindow()


    def _attachPage(self, page, show=True):
        '''
            Reattach a floating page to the toolbox.

        args :
            page : the page instance to reattach.

        kwargs :
            show = True : if True the newly attached page will be displayed
        '''

        # is page already attached
        #
        try:
            page_id = page.id
            dialog = self._dialogs[page.id]
        except KeyError:
            raise ToolboxError("Failed to attach page.")

        # readd page to main window
        #
        #self.main_frame.layout().addWidget(page)
        self._page_widget.layout().addWidget(page)

        page.hide()
        if show is True:
            self._showPage(page)

        del(self._dialogs[page_id])
        dialog.blockSignals(True)
        dialog.close()
        dialog.blockSignals(False)


    def _dialogClose(self, dialog):
        '''
            If a dialog is closed rather than the 'attach' button clicked, reattach the page
            without displaying it.
        '''

        page = dialog.page
        if page is not None:
            self._attachPage(page, show=False)
            page.blockSignals(True)
            page.setFloating(False)
            page.blockSignals(False)

    # --------------------------------------------------------------------------------------- #

    def _refreshPage(self, page):
        # find page connections
        #
        floating  = False
        curr_page = False
        in_stack  = False
        next_page = None
        prev_page = None
        dialog    = None

        # is page in stack
        #
        if page in self._page_stack:
            in_stack = True
            prev_page = page.previous_page

            if page is not self._current_page:
                next_page = self._current_page
                while next_page.previous_page is not page:
                    next_page = check_page.previous_pages
                    if next_page is None:
                        raise ToolboxError("Error refresh page.")
            else:
                curr_page = True

        else:
            # else is page in a dialog
            #
            try:
                dialog = self._dialogs[page.id]
                floating = True
            except KeyError:
                pass

        page_menu_id = None
        for menu_id, menu_page in self._main_menu_lookup.items():
            if menu_page is page:
                page_menu_id = menu_id
                break

        # reload page class
        #
        page_name = page.__class__.__name__
        lib.reload(page_name)

        # delete current page
        #
        if in_stack is True:
            self._page_stack.remove(page)
        elif dialog is not None:
            dialog.layout().removeWidget(page)

        # create new page and hook up signals
        #
        new_page = lib.Page(page_name)
        new_page.previous_page = prev_page

        if in_stack is True:
            self._page_stack.add(new_page)
            self._addPage(new_page, show=False, add=True)

        elif floating is True:
            new_page.setFloating(True)
            self._addPage(new_page, show=False, add=False)

            dialog.setPage(new_page)
            del(self._dialogs[page.id])
            self._dialogs[new_page.id] = dialog

        if next_page:
            next_page.previous_page = new_page

        if curr_page is True:
            self._current_page = new_page
            new_page.show()

        if page_menu_id is not None:
            self._main_menu_lookup[page_menu_id] = new_page

        page.previous_page = None
        self._deletePage(page)

    # --------------------------------------------------------------------------------------- #

    def showTitle(self, value):
        if value is True:
            self.title_widget.setVisible(True)
        else:
            self.title_widget.setVisible(False)

    # --------------------------------------------------------------------------------------- #

    def showStatusBar(self, value):
        if value is True:
            self.status_widget.setVisible(True)
        else:
            self.status_widget.setVisible(False)


    def resetStatusBar(self):
        self.statusBar.setStyleSheet('color: #c8c8c8;')

    # --------------------------------------------------------------------------------------- #

    def clearStatus(self):
        for group in self.groups:
            group.clearGroupStatus()
            group.crossButton.setExpanded(False)


    def setStatus(self, text, mode=None):
        if not mode:
            mode = sig.STATUS_NORMAL

        elif mode not in sig.STATUSES:
            raise ToolboxError('Do not recognise status type.')

        if self._docked:
            self.statusBar.blockSignals(True)
            self.statusBar.setStyleSheet('color: %s;' %STATUS_COLOUR[mode])
            self.statusBar.showMessage(text, 5000)
            self.statusBar.blockSignals(False)
        else:
            self.status_label.setText("Status: <font color=%s>%s</font>"
                                      %(STATUS_COLOUR[mode], text))


    def setNormalStatus(self, text):
        self.setStatus(str(text), sig.STATUS_NORMAL)


    def setSuccessStatus(self, text):
        self.setStatus(str(text), sig.STATUS_SUCCESS)


    def setErrorStatus(self, text):
        self.setStatus(str(text), sig.STATUS_ERROR)

    # --------------------------------------------------------------------------------------- #

    def connectDockWidget(self, dock_name, dock_widget):
        dock_widget.topLevelChanged.connect(self.dockChanged)
        status_bar_name = 'MayaWindow|toolBar3|MainHelpLineLayout|helpLineFrame|formLayout16|helpLine1'
        self.statusBar = util_qt.getWidgetFromName(status_bar_name)
        self.statusBar.messageChanged.connect(self.resetStatusBar)
        self._dock_widget = dock_widget
        self._dock_name   = dock_name
        self.dockChanged(False)


    def dockChanged(self, floating):
        if floating:
            self._docked = False
            self.showStatusBar(True)
            self.showTitle(False)
            self.layout().setContentsMargins(5, 5, 5, 1)
        else:
            self._docked = True
            self.showStatusBar(False)
            self.showTitle(True)
            self.layout().setContentsMargins(5, 1, 5, 3)

    # --------------------------------------------------------------------------------------- #

    def close(self):
        lib.clear()
        self._current_page = None
        self._page_stack   = None

        if self._dock_widget:
            mc.deleteUI(self._dock_name)
        else:
            qg.QDialog.close(self)
        self._dock_widget = None
        self._dock_name = None


    def keyPressEvent(self, event):
        # block escape key closing
        #
        if event.key() != qc.Qt.Key_Escape:
            qg.QDialog.keyPressEvent(self, event)


    def __del__(self):
        print "Closing %s..." %UI_NAME


#--------------------------------------------------------------------------------------------------#
#                                         TOOL DIALOG                                              #
#--------------------------------------------------------------------------------------------------#

class ToolboxDialog(qg.QDialog):
    _page = None

    CLOSE = 'close'

    def __init__(self, page=None, size=None, position=None):
        #main_window = util_qt.getMayaWindow()
        #qg.QDialog.__init__(self, parent=parent)
        qg.QDialog.__init__(self)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Untitled')

        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(2,1,3,1)
        self.layout().setSpacing(0)

        if page is not None:
            self.setPage(page, size, position)

    # --------------------------------------------------------------------------------------- #

    def setPage(self, page, size=None, position=None):
        if size is not None:
            self.setFixedWidth(size.width())
            self.resize(size.width(), size.height())

        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)

        self._page = page
        self.layout().addWidget(page)

        if position is not None:
            self.move(position.x(), position.y())

        self.setWindowTitle(page.full_title)
        self.connect(page, qc.SIGNAL(page.CLOSE), self.close)
        page.show()


    @property
    def page(self):
        return self._page

    # --------------------------------------------------------------------------------------- #

    def closeEvent(self, event):
        self.emit(qc.SIGNAL(ToolboxDialog.CLOSE), self)
        self.deleteLater()
        qg.QDialog.closeEvent(self, event)

#--------------------------------------------------------------------------------------------------#
#                                  TOOL GRAPHICS VIEW                                              #
#--------------------------------------------------------------------------------------------------#

class ToolboxGraphicsView(qg.QGraphicsView):
    main_widget = None

    def resizeEvent(self, event):
        qg.QGraphicsView.resizeEvent(self, event)
        if not self.main_widget: return

        view_geometry = self.geometry()
        self.main_widget.setGeometry(0, 0, view_geometry.width() - 1, view_geometry.height())
        self.setSceneRect(0, 0, view_geometry.width(), view_geometry.height())


#--------------------------------------------------------------------------------------------------#
#                                     CREATE/DELETE TOOLBOX                                        #
#--------------------------------------------------------------------------------------------------#

toolbox = None

def create(docked=True):
    '''
        Create the toolbox UI and setup the dock widget.
    '''
    global toolbox

    if toolbox is None:
        toolbox = Toolbox()

    if docked is True:
        mainWindow = util_qt.getMayaWindow()

        toolbox.setParent(mainWindow)
        size = toolbox.size()

        name = util_qt.getFullName(toolbox)
        print name
        dock = mc.dockControl(
            allowedArea=['right', 'left'],
            area='right',
            floating=False,
            content=name,
            width=size.width(),
            height=size.height(),
            label=WINDOW_NAME)

        dock_widget = util_qt.getWidgetFromName(dock)
        toolbox.connectDockWidget(dock, dock_widget)

    else:
        toolbox.show()

#--------------------------------------------------------------------------------------------------#

def delete():
    '''
        Delete the toolbox UI.
    '''
    global toolbox
    if toolbox:
        toolbox.close()
        toolbox = None

#--------------------------------------------------------------------------------------------------#
