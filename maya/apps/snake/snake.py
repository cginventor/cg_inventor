import random

import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

# ------------------------------------------------------------------------------------------------ #

MAIN_COLOUR = qg.QColor(18,30,0)
SHADOW_COLOUR = qg.QColor(18,30,0,150)

MAIN_BRUSHES = [qg.QPen(MAIN_COLOUR), qg.QBrush(MAIN_COLOUR)]        
SHADOW_BRUSHES = [qg.QPen(SHADOW_COLOUR), qg.QBrush(SHADOW_COLOUR)]

# ------------------------------------------------------------------------------------------------ #

class Game(qw.QDialog):
    '''Main Game Window. Has functions for adding and connection levels.'''

    TITLE = 'GAME'
    WIDTH = 452
    HEIGHT = 324

    def __init__(self):
        qw.QDialog.__init__(self)
        self.setWindowTitle(self.TITLE)
        qw.QDialog.setWindowFlags(self, qc.Qt.WindowStaysOnTopHint)

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


    def setBackgroundColor(self, r, g, b):
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



class GameData(object):
    def __init__(self):
        self.speed_level = 3



class Snake2(Game):
    TITLE = 'SNAKE II'
    WIDTH = 452
    HEIGHT = 324

    BACKGROUND_COLOUR = (128, 175, 1)

    MENU = 'menu'
    TITLE = 'title'
    ARENA = 'arena'
     
    def __init__(self):
        Game.__init__(self)
        
        self.setBackgroundColor(*self.BACKGROUND_COLOUR)

        self.registered_level_types = {}
        self.levels = {}

        # register level types
        #
        self.register(self.TITLE, Title)
        self.register(self.MENU, Menu)
        self.register(self.ARENA, Arena)

        # add levels
        #
        main_title = self.addLevel(self.TITLE)
        main_menu = self.addLevel(self.MENU)
        level_menu = self.addLevel(self.MENU)
        arena = self.addLevel(self.ARENA)

        # connect levels together
        #
        self.addConnection(main_title, 0, main_menu)

        self.addConnection(main_menu, 0, arena)
        self.addConnection(main_menu, 1, level_menu)

        self.addConnection(level_menu, 0, main_menu)

        # setup menus
        #
        menu_items = [('New Game', 0),
                      ('Level', 1),
                      ('High Scores', 1),
                      ('Options', 1)]
        main_menu.initialize(menu_items)

        menu_items = [('Slowest', 0),
                      ('Slow', 0),
                      ('Normal', 0),
                      ('Fast', 0),
                      ('Fastest', 0)]
        level_menu.initialize(menu_items)
            
# ------------------------------------------------------------------------------------------------ #

class Level(qw.QWidget):
    id = 0
    
    def __init__(self):
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
        self.emit(qc.SIGNAL('switchLevel(int, int)'), self.id,  index)
        
# ------------------------------------------------------------------------------------------------ #

def new_uncompress(image_str, width):
    lines = []
    for line in image_str.split('-'):
        lines.append(int(line, 16))
    return lines

TITLE_IMAGE = (95, 76, \
'700001800000000000001800-4f8003c00060100000003c00-40f803f080701c0780003f00-400fc7f9c07c3f07c0e03'\
'f80-40007ffbe07e3f87c0fc7fc0-78000ff7e07e3f87c0fc7fe0-7c60027bf0fc3fc7e1fc7ff0-c7c023df8fc3fc3e1'\
'fc3ff8-c7c060efce07fe3e3fc07f8-c4c7c0f7ee87be3e3fe03fc-c4c780f7fee79e3e3fe00fc-c4c408f3fdff9f3e7'\
'fe007e-c4c41ef1fdff1f3e7bc003e-c4c41fe0fdff0fbefb9f81f-c4c403e0fc7f8fbef3bff9f-7c4c401e1ff1fefbf'\
'f3bffff-4c4c471c3ff1fffbfe3bffff-403c479c7ff3fffdfc3bf07e-400c47fcfdf3e3fdfc3bf800-780073f8f9f3e'\
'07df83dfc00-7f000cf871e0407c383dfe00-fe0047821ef007f003eff80-1fc04100109c03f000f7fe0-3f8c0000786'\
'00800033ffc-7f8000fc73de000001ffc-f00018018630000007fc-20001001c8d0000001fc-3005a1b000000078-21e'\
'215afff000018-60b0cc7555e00000-4180001eaabc0000-61000003d5578000-1ffc007ffeaaaf000-f547f8800fd55'\
'5800-1aac04e00187eaac00-3556065807003d5600-ffebf034ffa00e7fa00-3803c181d0d200b7ae00-70e00070c0e0'\
'd400dd7700-8c80001c6060d8006b8b00-10707f8063030e000d715c0-21b0ebf031818b003ffaaf0-4320b59c18c0c8'\
'bffd7d558-87e1ab760c60642aaeaafac-8f21751b063030355555dd4-3086bebc58218183aaaaabec-51be5f5f6c30c'\
'0c1d5555554-519faffe261060617effabac-21c1ffe1621030312393ff54-23a80002c6179818a093feb8-63d600054'\
'c17cc086f57fd70-43ef807e9837e60d0827eb80-47d4ffc53067f304fb1fd700-47ea000260cff906faafac40-47d50'\
'004c19ff982f26359f8-47ec0009933ff182f7f6b3fe-4737c0f1167fc782f57d67ff-466a7f8b0c781c82f6facfff-2'\
'4b480120703f006f3f59fff-1f1a000a01fe000cf9f73fff-4007c0fb00000019fc603ffe-7ff07f81800000f3fcefff'\
'f8-fff003cf0000f87f9efffc0-fffffe1ffff83ffa5ffc00-0-0-0-0-1ddd5c3bbbb8000000-1449c4088aa8000000-'\
'1cc9cc3bbbb8000000-c4944220988000000-15c95c3bba88000000-0-0-0')

class Title(Level):
    title_image = new_uncompress(TITLE_IMAGE[2], TITLE_IMAGE[0])
    
    def __init__(self):
        Level.__init__(self)
        
        self.x_offset = (self.width - (TITLE_IMAGE[0] * 4)) / 2
        self.y_offset = (self.height - (TITLE_IMAGE[1] * 4)) / 2
    
    
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + self.x_offset
        y = option.rect.y() + self.y_offset
        
        for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])

            drawImage(painter, x, y, TITLE_IMAGE)


    def keyPressEvent(self, event):
        self.switch(0)
                    
# ------------------------------------------------------------------------------------------------ #  

class Menu(Level):
    menu_id = 0
    
    def __init__(self):
        Level.__init__(self)
        self.menu_id = Menu.menu_id
        Menu.menu_id += 1
        
        self.menu_item_width = 100
        self.menu_item_height = 16
                
        self.selected_index = 0
        
        self.menu_items = []
        self.menu_signals = []
        self.menu_item_grids = {}
                
    
    def initialize(self, menu_items):
        '''Setup the menu with given items and signal connections. Should be pairs of text:signal_id.'''

        self.menu_items = []
        self.menu_signals = []
        self.menu_item_grids = {}

        # add each menu item to menu as fancy text
        #
        for menu_item_name, signal_id in menu_items:
            self.menu_items.append(menu_item_name)
            self.menu_signals.append(signal_id)

            grids = [[0 for _ in range(self.menu_item_width)] for _ in range(16)]
            self.menu_item_grids[menu_item_name] = grids
             
            indent = [4, 3]
            for letter in menu_item_name:
                letter_grid = font[letter]
                grid_width = letter_grid[0]
                for i, row in enumerate(letter_grid):
                    grids[i + indent[1]][indent[0]:indent[0]+grid_width] = row
                indent[0] += grid_width + 1
                
                
    def keyPressEvent(self, event):
        key = event.key()   
        if key in (qc.Qt.Key_Up, qc.Qt.Key_Down):         
            if key == qc.Qt.Key_Up:
                self.selected_index -= 1
            elif key == qc.Qt.Key_Down:
                self.selected_index += 1
            
            num_items = len(self.menu_items)
            if self.selected_index < 0:
                self.selected_index = num_items - 1
            elif self.selected_index >= num_items:
                self.selected_index = 0
            
            self.repaint()
            
        elif key in (qc.Qt.Key_Return, qc.Qt.Key_Enter):
            self.switch(self.menu_signals[self.selected_index])
        
        
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + 24
        y = option.rect.y() + 24
        
        for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])            
            
            w_y = y
            for i, menu_item in enumerate(self.menu_items):
                menu_item_grid = self.menu_item_grids[menu_item]
                
                invert = False
                if i == self.selected_index:
                    invert = True
                    
                drawImage(painter, x, w_y, menu_item_grid, invert)
                
                w_y += 16 * 4
                    
# ------------------------------------------------------------------------------------------------ #

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Arena(Level):
    GAME_OVER = 'GAME OVER'
    
    def __init__(self):
        Level.__init__(self)
        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(10,10,10,10)
        self.layout().setSpacing(0)
        
        self.setFocusPolicy(qc.Qt.StrongFocus)
        
        self.grid = Grid(self.width/16-2, self.height/16-4)
        
        self.snake_speed = 100
        
        self.score_board = ScoreBoard(self.width/16-2)
        self.layout().addWidget(self.score_board)
                
        self.ui = GameGrid(self.grid)
        self.layout().addWidget(self.ui)
        
        self.score_text = ['Game Over!', 'TOP SCORE:', 'SCORE:']

        self.reset()
    
    
    def reset(self):     
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.position = [8, 6]
        self.length = 5
        self.game_over_counter = 0       
        
        self.game_mode = True
        self.score_mode = False
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self.update)        
        self._anim_speed = self.snake_speed
        
        self.grid.reset()
        self.score_board.reset()
        
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == qc.Qt.Key_Left:
            self.moveLeft()            
        elif key == qc.Qt.Key_Right:
            self.moveRight()            
        elif key == qc.Qt.Key_Up:
            self.moveUp()            
        elif key == qc.Qt.Key_Down:
            self.moveDown()
        
    
    def start(self):
        self.grid.reset()
        self.addApple()
        
        x, y = self.position
        block = self.grid[x][y]
        block.state = Block.HEAD
        block.direction = self.direction
        block.counter = 5
        
        for index in range(1,self.length-1):
            block = self.grid[x-index][y]
            block.type = Block.TAIL if index == self.length - 2 else Block.BODY
            block.direction = self.direction
            block.counter = self.length - index
            
        self._anim_timer.start(self._anim_speed)
        
        
    def end(self):
        self._anim_timer.stop()
        
    
    def endGame(self):
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self.update)
        self._anim_timer.timeout.connect(self.gameOver)
        self._anim_timer.start(200)
        
    
    def gameOver(self):
        self.game_over_counter += 1
        self.ui.draw_snake = not self.game_over_counter % 2
        self.ui.repaint()
        
        if self.game_over_counter != 10:
            return
        
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self.gameOver)
        
        self.game_mode = False
        self.score_mode = True
        self.ui.hide()
        self.score_board.hide()
        
        self.repaint()
            
            
    def moveUp(self):
        if self.direction == DOWN:
            return
        self.next_direction = UP
        
    
    def moveDown(self):
        if self.direction == UP:
            return
        self.next_direction = DOWN
        
        
    def moveLeft(self):
        if self.direction == RIGHT:
            return
        self.next_direction = LEFT
        
    
    def moveRight(self):
        if self.direction == LEFT:
            return
        self.next_direction = RIGHT
        
    
    def nextPositions(self, x, y): 
        self.direction = self.next_direction
                       
        x += self.direction[0]
        y += self.direction[1]
        
        width = self.grid.width
        height = self.grid.height
        
        if x < 0:
            x += width
        elif x >= width:
            x -= width
            
        if y < 0:
            y += height
        elif y >= height:
            y -= height
        
        return x, y
    
    
    def update(self):
        x, y = self.position
        current_block = self.grid[x][y]
        
        x, y = self.nextPositions(x, y)        
        next_block = self.grid[x][y]
        
        x2, y2 = self.nextPositions(x, y) 
        future_block = self.grid[x2][y2]
        
        added_length = 0
        if next_block.type == Block.APPLE:
            added_length = 1
            self.score_board.score_counter += 8
            self.score_board.repaint()
            self.addApple()
        elif next_block.type not in (Block.FREE, Block.TAIL):
            self.endGame()            
            return
        
        next_block.counter = self.length + 1
        next_block.direction = self.direction
        next_block.type = Block.HEAD
        
        if future_block.type == Block.APPLE:
            next_block.open = True
        
        self.length += added_length
        
        if next_block.direction != current_block.direction:
            current_block.type = Block.CORNER
            d1, d2 = current_block.direction, next_block.direction
            if (d1, d2) in ((RIGHT, UP), (DOWN, LEFT)):
                current_block.corner_direction = RIGHT
            elif (d1, d2) in ((LEFT, UP), (DOWN, RIGHT)):
                current_block.corner_direction = LEFT
            elif (d1, d2) in ((LEFT, DOWN), (UP, RIGHT)):
                current_block.corner_direction = UP
            elif (d1, d2) in ((RIGHT, DOWN), (UP, LEFT)):
                current_block.corner_direction = DOWN
        else:        
            current_block.type = Block.BODY
        
        self.position = [x, y]
        
        self.grid.decrementCounter(added_length)
    
        self.ui.repaint()
        
    
    def addApple(self):
        free_blocks = self.grid.freeBlocks()
        random_index = random.randint(0, len(free_blocks)-1)
        x, y = free_blocks[random_index]
        block = self.grid[x][y]
        block.type = Block.APPLE
        block.food = True
        
    
    def paintEvent(self, event):
        if not self.score_mode:
            return
        
        painter = qw.QStylePainter(self)
        option  = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + 92
        y = option.rect.y() + 48
        
        for index, color in enumerate((MAIN_BRUSHES, SHADOW_BRUSHES)):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])            
            
            w_y = y
            for score_text in self.score_text[0:2]:
                text_grid = self.score_text_grids[score_text]               
                drawImage(painter, x, w_y, text_grid)                
                w_y += 16 * 4
                
            score_str = '{:04d}'.format(self.score_board.score_counter)
            
            sx = x
            for index in range(4):
                score_grid = font[score_str[index]]               
                drawImage(painter, sx, w_y, score_grid)
                sx += (len(score_grid[0]) + 1) * 4
        
    
    def __del__(self):
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self.update)
        print 'deleting game'
        
# ------------------------------------------------------------------------------------------------ #

class GameGrid(qw.QWidget):
    def __init__(self, grid):
        qw.QWidget.__init__(self)
        self.grid = grid
        
        self.setFixedWidth(16 * self.grid.width + 16)
        self.setFixedHeight(16 * self.grid.height + 16)
        
        self.draw_snake = True
        
    
    def reset(self):
        self.grid.reset()
        
    
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 4
        width = option.rect.width() - 4
        
        for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
            painter.setPen(color[0])
            painter.setBrush(color[1])

            for i in range(width):
                px = x + (i * 4)
                painter.drawRect(px, y, 2, 2)
                painter.drawRect(px, y + height, 2, 2)
                        
            for i in range(height):                
                py = y + (i * 4)
                painter.drawRect(x, py, 2, 2)
                painter.drawRect(x + width, py, 2, 2)
            
            if not self.draw_snake:
                continue
            
            for i in range(self.grid.width):
                for j in range(self.grid.height):
                    block = self.grid[i][j]
                    if block.type == Block.FREE:
                        continue
                    
                    block_x = x + i * 16 + 7
                    block_y = y + j * 16 + 7
                    
                    block_value = block.draw()
                    
                    check = 1
                    for gi in range(4):
                        for gj in range(4):
                            if block_value & check:
                                gx, gy = block_x + (gj*3) + 1 + gj, block_y + (gi*3) + 1 + gi
                                painter.drawRect(gx, gy, 2, 2)
                            check = check << 1

            x += 1
            y += 1
                    
    
    def __del__(self):
        print 'deleting game grid'

# ------------------------------------------------------------------------------------------------ #
        
def drawImage(painter, x, y, image, invert=False):
    for line in image[1]:
        check = 1
        for i in range(image[0]):
            if line & check:
                gx, gy = x + (i * 3) + 1 + i, y + (i * 3) + 1 + i
                painter.drawRect(gx, gy, 2, 2)
            check <<= 1

# ------------------------------------------------------------------------------------------------ #

class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.columns = [Row(height) for _ in range(width)]
        
    
    def __len__(self):
        return len(self.columns)
    
    
    def __getitem__(self, index):
        return self.columns[index]
        
    
    def draw(self):
        symbols = {Block.FREE: '_',
                   Block.HEAD: '&',
                   Block.BODY: '#',
                   Block.TAIL: '^',
                   Block.CORNER: '%',
                   Block.APPLE: 'O'}
        for row_index in range(len(self.columns[0])):
            line = ''
            for column_index in range(len(self.columns)):
                block = self.columns[column_index][row_index]
                line += '{} '.format(symbols[block.type], block.counter) 
            
            
    def reset(self):
        for column in self.columns:
            for row in column.rows:
                row.reset()
                
                
    def decrementCounter(self, addition=0):
        body_parts = {}
        for column in self.columns:
            for row in column.rows:
                if row.counter == 0 or row.type == Block.APPLE:
                    continue  
                                  
                counter_value = row.counter = row.counter - 1 + addition
                if counter_value == 0:
                    row.reset()
                    continue
                
                body_parts[counter_value] = row
        
        keys = sorted(body_parts.keys())
        tail = body_parts[keys[0]]          
        tail.type = Block.TAIL
        tail.direction = body_parts[keys[1]].direction
                    
                    
    def freeBlocks(self):
        free_blocks = []
        for column_index, column in enumerate(self.columns):
            for row_index, block in enumerate(column.rows):
                if block.type == Block.FREE:
                     free_blocks.append((column_index, row_index))
        return free_blocks
    
    
    def __del__(self):
        print 'deleting grid'

# ------------------------------------------------------------------------------------------------ #

class ScoreBoard(qw.QWidget):
    DRAW = {'0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            '1': [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[0,1,0]],
            '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
            '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
            '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
            '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
            '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
            '7': [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
            '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
            '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]]}
    
    def __init__(self, width):
        qw.QWidget.__init__(self)
        
        self.setFixedHeight(32)
        self.setFixedWidth(16 * width + 16)
        
        self.score_counter = 0
        
        
    def reset(self):
        self.score_counter = 0
        
    
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 8
        width = option.rect.width() - 4
        
        for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
            painter.setPen(color[0])
            painter.setBrush(color[1])
            
            for i in range(width):
                painter.drawRect(x + (i * 4), y + height, 2, 2)
                
            score_str = '{:04d}'.format(self.score_counter)
            
            for index in range(4):
                sx = x + (index * 16) + 4
                grid = ScoreBoard.DRAW[score_str[index]]
                for i in range(3):
                    for j in range(5):
                        if not grid[j][i]:
                            continue
                        gx, gy = sx + (i*4), y + (j*4)
                        painter.drawRect(gx, gy, 2, 2)

            x += 1
            y += 1
                        
    def __del__(self):
        print 'deleting scoreboard'
                        
# ------------------------------------------------------------------------------------------------ #
        
class Row(object):
    def __init__(self, width):
        self.rows = [Block() for _ in range(width)]
        
        
    def __len__(self):
        return len(self.rows)
    
    
    def __getitem__(self, index):
        return self.rows[index]
        
# ------------------------------------------------------------------------------------------------ #

class Block(object):
    FREE = 0 
    BODY = 1
    HEAD = 2
    HEAD_OPEN = 3
    TAIL = 4
    CORNER = 5
    
    FOOD = 0x6bd6 
    APPLE = 0x252
    BONUS_A_1 = 0xcfac
    BONUS_A_2 = 0x3750
    BONUS_B_1 = 0xed90
    BONUS_B_2 = 0xf753
    BONUS_C_1 = 0xaf10    
    BONUS_C_2 = 0xaf00
    BONUS_D_1 = 0x5dfc
    BONUS_D_2 = 0xabf3

    DRAW = {BODY: {LEFT: 0xbd0, RIGHT: 0xdb0, UP: 0x6246, DOWN: 0x6426},
            HEAD: {LEFT: 0xe68, RIGHT: 0x761, UP: 0xa660, DOWN: 0x66a},
            HEAD_OPEN: {LEFT: 0x2c4a, RIGHT: 0x4325, UP: 0x5690, DOWN: 0x965},
            TAIL: {LEFT: 0xf30, RIGHT: 0xfc0, UP: 0x4466, DOWN: 0x6644},
            CORNER: {LEFT: 0xca6, RIGHT: 0x356, UP: 0x6ac0, DOWN: 0x6530}}
    
    def __init__(self):
        self.reset()
              
        
    def reset(self):
        self.type = Block.FREE
        self.direction = LEFT
        self.corner_direction = LEFT
        self.counter = 0
        self.food = False
        self.open = False
        
        
    def draw(self):
        if self.type == Block.APPLE:
            return Block.APPLE
        
        if self.food and self.type not in (Block.HEAD, Block.TAIL):
            return Block.FOOD
        
        direction = self.corner_direction if self.type == Block.CORNER else self.direction        
        if self.type == Block.HEAD and self.open:
            return Block.DRAW[Block.HEAD_OPEN][direction]        

        return Block.DRAW[self.type][direction]
    
# ------------------------------------------------------------------------------------------------ #

def compress(image_str):
    lookup = {'0':'!', '1':'-'}
    output = []
    previous_letter = image_str[0]
    letter_count = 1
    image_str += '|'
    for letter in image_str[1:]:
        if letter == previous_letter:
            letter_count += 1
            continue
        
        if letter_count == 1:
            output.append(lookup[previous_letter])
        else:
            output.append(lookup[previous_letter])
            output.append(str(letter_count))
            
        previous_letter = letter
        letter_count = 1
    
    return ''.join(output)


def uncompress(image_str):
    lookup = {'!':'0', '-':'1','&':'2'}
    current_number = ''
    counter_str = '1'
    image_str += '&'
    
    output = []
    for letter in image_str:
        number = lookup.get(letter, None)
        if number is None:
            counter_str += letter
        else:
            output.append(current_number * int(counter_str if counter_str != '' else '1'))
            
            current_number = number            
            counter_str = ''
            
    return ''.join(output)


def splitLetters(keys, font_str, font_width):    
    font_str = uncompress(font_str)
    font = []
    for i in range(len(font_str) / font_width):
        line = font_str[i*font_width:(i+1)*font_width]
        font.append([int(num) for num in line])
        
    break_points = [0]
    for i in range(len(font[0])):
        break_line = True
        for j in range(len(font)):
            if font[j][i] != 0:
                break_line = False
    
        if break_line:    
            break_points.append(i)        
    break_points.append(-1)
    
    all_grids = {}
    for index, key in enumerate(keys):
        all_grids[key] = grid = []
        for i in range(len(font)):
            j, k = break_points[index], break_points[index+1]
            j = j if j == 0 else (j + 1)
            grid.append(font[i][j:k])
     
    return all_grids

# ------------------------------------------------------------------------------------------------ #    

title_width, title_height = 95, 77

font_lower_width, font_lower_height = 166, 11
font_lower = \
'!7-2!16-2!10-2!8-2!5-2!2-2!-2!5-2!51-2!50-2!16-2!9-2!9-2!12-2!5-2!51-2!44-4!2-5!3-4!3-5!2-4!2-4!'\
'2-4!2-5!2-2!2-2!-2!2-2!-2!-7!2-5!3-4!2-5!3-4!2-2!-2!2-4!-4!-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!-5'\
'!4-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!-2!2-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2'\
'-2!-2!2-2!-5!-2!5-2!2-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!3-2!2-5!-2!2-2!-2!5-2!2-2!-2!2-2!2-2!2-2'\
'!2-2!-2!2-2!-2!2-2!-4!3-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!5-2!2-2!2-2!-2!2-2!-2!3-2!'\
'-2!2-2!-2!2-2!3-2!-2!2-2!-2!2-2!-2!5-2!2-2!-6!2-2!2-2!2-2!-2!2-2!-2!2-2!-3!4-2!-2!-2!-2!-2!2-2!-'\
'2!2-2!-2!2-2!-2!2-2!-2!5-3!3-2!2-2!2-2!-2!2-2!-2!-!-2!2-4!2-2!2-2!2-2!2-2!2-2!-2!2-2!-2!5-2!2-2!'\
'-2!6-2!2-2!2-2!-2!2-2!-2!2-2!-4!3-2!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!2-2!2-2!2-2!2-!2'\
'-!2-2!-!-2!-6!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!2-2!2-2!2-2!-2!2-2!-2!2-2!-2!-2!2-2'\
'!-2!-2!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!2-2!2-2!2-2!2-4!3-5!2-2!2-2!-2!2-2!-2!4-5!-5!3-4!3-'\
'5!2-4!3-2!3-5!-2!2-2!-2!-2!2-2!2-2!-2!-2!-2!-2!-2!2-2!2-4!2-5!3-5!-2!4-4!4-2!2-5!3-2!4-2!-2!2-2!'\
'2-2!2-5!-5!44-2!48-2!9-2!51-2!47-4!49-2!9-2!48-4!7'

font_upper_width, font_upper_height = 174, 11
font_upper = \
'!-4!2-5!3-4!2-5!2-5!-5!2-4!2-2!2-2!-2!3-2!-2!2-2!-2!3-!5-!-!4-2!2-4!2-5!3-4!2-5!3-4!2-6!-2!2-2!-'\
'2!2-2!-2!3-2!-2!2-2!-2!2-2!-8!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-'\
'2!3-2!-2!3-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!3-2!3-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!2-2!4-2!-2!2'\
'-2!-2!2-2!-2!5-2!2-2!-2!4-2!4-2!5-2!2-2!-2!3-2!-2!2-2!-2!3-3!-3!-3!2-2!-2!2-2!-2!2-2!-2!2-2!-2!2'\
'-2!-2!7-2!3-2!2-2!-2!2-2!-2!3-2!2-4!2-2!2-2!4-2!-2!2-2!-2!2-2!-2!5-2!2-2!-4!2-4!2-2!5-2!2-2!-2!3'\
'-2!-2!2-2!-2!3-7!-4!-2!-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!7-2!3-2!2-2!-2!2-2!-2!-!-2!2-4!2-2!2-2!3-2'\
'!2-6!-5!2-2!5-2!2-2!-2!4-2!4-2!5-6!-2!3-2!-5!2-2!3-2!-!-2!-7!-2!2-2!-5!2-2!2-2!-5!3-4!4-2!3-2!2-'\
'2!-2!2-2!-2!-!-2!3-2!4-4!4-2!2-2!2-2!-2!2-2!-2!5-2!2-2!-2!4-2!4-2!-3!-2!2-2!-2!3-2!-2!2-2!-2!3-2'\
'!3-2!-2!-4!-2!2-2!-2!5-2!2-2!-2!2-2!5-2!3-2!3-2!2-2!-2!2-2!-7!2-4!4-2!4-2!3-2!2-2!-2!2-2!-2!5-2!'\
'2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-2!3-2!-2!2-3!-2!2-2!-2!5-2!2-2!-2!2-2!5-2!3-2!3-2!2'\
'-2!2-4!3-5!3-4!4-2!4-2!3-2!2-2!-2!2-2!-2!2-2!-2!2-2!-2!4-2!4-2!2-2!-2!2-2!-2!3-2!-2!2-2!-2!3-2!3'\
'-2!-2!3-2!-2!2-2!-2!5-2!-3!-2!2-2!-2!2-2!3-2!3-2!2-2!2-4!3-5!2-2!2-2!3-2!3-2!4-2!2-2!-5!3-4!2-5!'\
'2-5!-2!5-4!2-2!2-2!-2!-3!2-2!2-2!-4!-2!3-2!-2!4-!2-4!2-2!6-4!2-2!2-2!2-4!4-2!4-4!4-2!4-2!-2!2-2!'\
'2-2!3-2!3-6!108-2!238'

font_numbers_width, font_number_height = 70, 11
font_numbers = \
'!-4!3-2!3-4!3-4!6-2!2-6!2-4!2-6!2-4!3-4!3-2!2-2!-3!2-2!2-2!-2!2-2!4-3!2-2!5-2!2-2!-2!2-2!-2!2-2'\
'!-2!2-2!2-2!2-2!2-2!2-2!2-2!-2!2-2!3-4!2-2!5-2!9-2!-2!2-2!-2!2-2!2-2!2-2!2-2!2-2!2-2!5-2!2-2!-2'\
'!2-5!2-5!6-2!-2!2-2!-2!2-2!2-2!2-2!2-2!5-3!3-3!3-!2-2!6-2!-2!2-2!4-2!3-4!2-2!2-2!2-2!2-2!2-2!4-'\
'3!6-2!-2!2-2!6-2!-2!2-2!3-3!2-2!2-2!2-5!2-2!2-2!2-2!3-3!3-2!2-2!-2!2-2!2-2!2-2!-2!2-2!3-2!3-2!2'\
'-2!5-2!2-2!2-2!2-2!2-3!4-2!2-2!-7!-2!2-2!-2!2-2!3-2!3-2!2-2!-2!2-2!3-4!2-4!-6!2-4!6-2!3-4!3-4!4'\
'-2!4-4!3-4!143'

font_symbols_width, font_symbols_height = 49, 11
font_symbols = \
'!6-2!2-4!5-2!-2!10-2!-2!2-3!-3!7-2!-2!2-2!4-2!-2!10-2!-2!-2!5-4!-2!-2!-2!2-2!4-2!-2!10-2!2-!-2!'\
'5-4!-2!-2!5-2!3-2!3-2!9-2!4-2!5-2!6-2!3-3!4-2!3-2!9-2!4-2!5-2!6-2!3-2!4-2!5-2!8-2!4-2!5-4!-2!12'\
'-2!5-2!8-2!4-2!5-4!-2!-2!3-2!3-2!7-2!-2!-2!-2!4-2!5-2!4-!-2!3-2!3-2!7-2!-2!-2!-2!5-3!-3!30-!68'
symbols = ':',';','!','?','/','\\','.',',','|','\'','(',')'

font = splitLetters([chr(index + 97) for index in range(26)], font_lower, font_lower_width)
font.update(splitLetters([chr(index + 65) for index in range(26)], font_upper, font_upper_width))
font.update(splitLetters([str(index) for index in range(10)], font_numbers, font_numbers_width))
font.update(splitLetters(symbols, font_symbols, font_symbols_width))
font[' '] = [[0 for _ in range(4)] for _ in range(11)]
font['"'] = font['\'']
font['{'] = font['['] = font['(']
font['}'] = font[']'] = font['('] 

# ------------------------------------------------------------------------------------------------ #

ui = None

def create():
    global ui
    
    if not ui:
        ui = Snake2()
    
    ui.show()
    


def delete():
    global ui
    
    if ui:
        del(ui)
    
    ui = None


# font_lower_width, font_lower_height = 166, 11
# font_lower = \
# test = '!6-2!2-4!5-2!-2!10-2!-2!2-3!-3!7-2!-2!2-2!4-2!-2!10-2!-2!-2!5-4!-2!-2!-2!2-2!4-2!-2!10-2!2-!-2!'\
# '5-4!-2!-2!5-2!3-2!3-2!9-2!4-2!5-2!6-2!3-3!4-2!3-2!9-2!4-2!5-2!6-2!3-2!4-2!5-2!8-2!4-2!5-4!-2!12'\
# '-2!5-2!8-2!4-2!5-4!-2!-2!3-2!3-2!7-2!-2!-2!-2!4-2!5-2!4-!-2!3-2!3-2!7-2!-2!-2!-2!5-3!-3!30-!68'
#
# uncompressed_image = uncompress(test)
#
# prev = 0
# new_image = []
# for i in range(font_lower_width, len(uncompressed_image), font_lower_width):
#     new_image.append(hex(int(uncompressed_image[prev:i], 2))[2:-1])
#     prev = i
# print '-'.join(new_image)

font_lower_width = 166
font_lower = '600018018060cd83000000000000180000000000-6000180300600183000000000000180000000000-1e7c7' \
             '8f9e79e7ccd9b7f3e3cf8f367bd9b36366cdf-366cd9b333366cdb36db366cd9bec199b36366cc6-1f66c19' \
             'b333366cde36db366cd9b0c199b36366cc6-3366c19bf33366cdc36db366cd9b07199b36b3cccc-3366c19b' \
             '033366cde36db366cd9b01999926b7eccc-3366cd9b333366cdb36db366cd9b019999e3e66cd8-1f7c78f9e' \
             '31f66d99b6db33cf8fb0f0cf8c36667df-3000000000000c018000000000000c0'

font_upper_width = 174
font_upper = '1e7c79f3ef9e66c6cd8828679f1e7c79fb366c6cd9bf-3366cd9b0c3366c6cd8c6c6cd9b366cc63366c6cd9' \
             '86-3366c19b0c3066c6cd8eee6cd9b366c063366c679986-3366c19bcf3066c6cd8fef6cd9b366c063366d6' \
             '7998c-3f7cc19b0c307ec6f98d6fecdf337c7863366d630f0c-3366c19b0c3766c6cd8c6decd833660c6336' \
             '6fe78618-3366c19b0c3366c6cd8c6cecd833660c6333c7c78618-3366cd9b0c3366c6cd8c6c6cd83766cc6' \
             '333c7ccc630-337c79f3ec1e66dccdec6c27981e667861e186ccc63f-30000000000000000'

font_numbers_width = 70
font_numbers = '1e31e3c0cfcf3f3c78cdccd9873066cd9b33333366-f30600d9b333333066cf9f0366ccccc1c71303661-' \
               '23cccccc381b303663999f3331c66cccd98c660ccc-33866fecd98c66cc79efcf031e3c30f1e000000000'

font_symbols_width = 49
font_symbols = 'cf06c00d9dc06cc36006d83db661b0032c1ed831-23006183031c318030c1818c30601860f60018300c-c' \
               '1ed8c6036d860c2c6301b6c1dc00000008000000'



def uncompress_image(image_str, width):
    lines = []
    for line in image_str.split('-'):
        lines.append(int(line, 16))
    return width, lines


def split(image):
    split_images = []
    binary_lines = [bin(line)[2:].zfill(image[0]) for line in image[1]]

    check = 1
    counter = image[0] - 1
    prev_counter = image[0]
    for i in range(image[0]):
        split_line = True
        for line in image[1]:
            if line & check:
                split_line = False
        check <<= 1

        if split_line is True or i == image[0] - 1:
            width = prev_counter - counter - (0 if i == image[0] - 1 else 1)
            split_images.append([width, [int(binary_line[counter:prev_counter], 2) for binary_line in binary_lines]])
            prev_counter = counter
        counter -= 1

    return split_images[::-1]


def draw(image, x, y, painter, invert=False):
    for line in image[1]:
        check = 1
        line_str = []
        for _ in range(image[0]):
            if line & check:
                line_str.append('H')
            else:
                line_str.append('-')
            check <<= 1

        print ''.join(line_str[::-1])

# font_upper_image = uncompress_image(font_upper, font_upper_height)
# display(font_upper_image)
# split_images = split(image)
# for split_image in split_images:
#     display(split_image)

#font = dict(zip([chr(index + 97) for index in range(26)], split(uncompress_image(font_lower, font_lower_width))))
#font.update(dict(zip([chr(index + 65) for index in range(26)], split(uncompress_image(font_upper, font_upper_width)))))

print font