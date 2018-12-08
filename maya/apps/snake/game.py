import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

#--------------------------------------------------------------------------------------------------#

class Game(qw.QDialog):
    '''Main Game Window. Has functions for adding and connection levels.'''

    TITLE = 'GAME'
    WIDTH = 500
    HEIGHT = 500

    BACKGROUND_COLOUR = (100, 100, 100)

    data = dict()

    def __init__(self):
        super(Game, self).__init__()

        self.setWindowTitle(self.TITLE)
        self.setWindowFlags(qc.Qt.WindowStaysOnTopHint)

        self.setBackgroundColor(*self.BACKGROUND_COLOUR)

        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.HEIGHT)

        self.widget_stack = qw.QStackedWidget()
        self.layout().addWidget(self.widget_stack)

        # level information
        #
        self._levels = {}
        self._types = {}
        self._connections = {}

        # setup default game data
        #
        self.data['width'] = self.WIDTH
        self.data['height'] = self.HEIGHT


    def setBackgroundColor(self, r, g, b):
        '''Set background color to give rgb value.'''
        self.setStyleSheet('background-color: rgb({}, {}, {});'.format(r, g, b))


    def register(self, type_name, level_class):
        '''Register a new level type.'''

        self._types[type_name] = level_class


    def addLevel(self, level_type):
        '''Add a new level to the game. Creates the level based on type, add and connects.'''

        # get level class from registered level types
        #
        level_class = self._types.get(level_type, None)
        new_level = level_class()
        new_level.data = Game.data
        self.widget_stack.addWidget(new_level)
        self.connect(new_level, qc.SIGNAL('switchLevel(int, int)'), self._switch)

        # store new level against level id for reference
        #
        self._levels[new_level.id] = new_level

        return new_level


    def addConnection(self, src_level, signal_id, dst_level):
        '''Define connections between levels.'''
        # get level connections. Create dictionary if first connection
        #
        level_connections = self._connections.get(src_level.id, None)
        if level_connections is None:
            level_connections = self._connections[src_level.id] = {}

        # store the connection to the level
        #
        level_connections[signal_id] = dst_level.id


    def _switch(self, current_level_id, signal_id):
        '''Switch to another level based on predefined connections.'''

        # end current level
        #
        current_level = self._levels[current_level_id]
        current_level.end()

        # get next level from connections
        #
        next_level_id = self._connections[current_level_id][signal_id]

        # display next level and start
        #
        next_level = self._levels[next_level_id]
        self.widget_stack.setCurrentWidget(next_level)
        next_level.start()


    def keyPressEvent(self, event):
        '''Feed key press events to current widget. Otherwise signal goes to main window and is lost.'''

        current_widget = self.widget_stack.currentWidget()
        return current_widget.keyPressEvent(event)

# ------------------------------------------------------------------------------------------------ #

class Level(qw.QWidget):
    id = 0

    data = None

    def __init__(self,):
        qw.QWidget.__init__(self)
        self.width, self.height = 452, 324
        self.id = Level.id
        Level.id += 1

    def reset(self):
        pass

    def start(self):
        pass

    def end(self):
        pass

    def switch(self, index):
        self.emit(qc.SIGNAL('switchLevel(int, int)'), self.id, index)