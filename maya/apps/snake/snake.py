import random

import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

from cg_inventor.maya.apps.snake import game; reload(game)
from cg_inventor.maya.apps.snake import images
from cg_inventor.maya.apps.snake import font; reload(font)

# ------------------------------------------------------------------------------------------------ #

MAIN_COLOUR = qg.QColor(18, 30, 0)
SHADOW_COLOUR = qg.QColor(18, 30, 0, 150)

MAIN_BRUSHES = [qg.QPen(MAIN_COLOUR), qg.QBrush(MAIN_COLOUR)]        
SHADOW_BRUSHES = [qg.QPen(SHADOW_COLOUR), qg.QBrush(SHADOW_COLOUR)]

# ------------------------------------------------------------------------------------------------ #

class Snake2(game.Game):
    TITLE = 'SNAKE II'

    PIXEL = 2

    SCREEN_WIDTH = 101
    SCREEN_HEIGHT = 82

    WIDTH = (PIXEL + 1) * SCREEN_WIDTH
    HEIGHT = (PIXEL + 1) * SCREEN_HEIGHT

    BACKGROUND_COLOUR = (128, 175, 1)

    SPLASH = 'splash'
    MENU = 'menu'
    ARENA = 'arena'
     
    def __init__(self):
        super(Snake2, self).__init__()

        # setup game data
        #
        self.data['pixel_width'] = self.PIXEL + 1
        self.data['speed_level'] = 5
        self.data['game_mode'] = 0

        # register level types
        #
        self.register(self.SPLASH, Splash)
        self.register(self.MENU, Menu)
        self.register(self.ARENA, Arena)

        # add levels
        #
        start_screen = self.addLevel(self.SPLASH)
        main_menu = self.addLevel(self.MENU)
        level_menu = self.addLevel(self.MENU)
        arena = self.addLevel(self.ARENA)

        # connect levels together
        #
        self.addConnection(start_screen, 0, main_menu)

        self.addConnection(main_menu, 0, arena)
        self.addConnection(main_menu, 1, level_menu)

        self.addConnection(level_menu, 0, main_menu)

        # setup splash screen
        #
        start_screen.initialize(images.title)

        # setup menus
        #
        menu_items = [('New Game', 0),
                      ('Level', 1),
                      ('High Scores', 1),
                      ('Options', 1),
                      ('Options', 1),
                      ('Options', 1),
                      ('Options', 1),
                      ('Options', 1)]
        main_menu.initialize(menu_items)

        menu_items = [('Slowest', 0),
                      ('Slow', 0),
                      ('Normal', 0),
                      ('Fast', 0),
                      ('Fastest', 0)]
        level_menu.initialize(menu_items)
        
# ------------------------------------------------------------------------------------------------ #

class SnakeLevel(game.Level):
    def paintPixels(self, image, painter, x, y, invert=False):
        '''Generic paint function for any grid.'''

        pixel = self.data['pixel_width']

        x *= pixel
        y *= pixel

        for i in range(image.height):
            line = image.lines[i]
            check = 1 << (image.width - 1)
            for j in range(image.width):
                paint = bool(line & check)
                if invert:
                    paint = not paint

                if paint:
                    gx = x + (j * pixel) + 1 + j
                    gy = y + (i * pixel) + 1 + i
                    painter.drawRect(gx, gy, pixel-1, pixel-1)
                check >>= 1


class Splash(SnakeLevel):
    def __init__(self):
        super(Splash, self).__init__()
        self.image = None
        self.offset = (0, 0)


    def initialize(self, image):
        self.image = image

        pixel_width = self.data['pixel_width'] + 1

        x_offset = (self.data['width'] - (self.image.width * pixel_width)) / 2
        y_offset = (self.data['height'] - (self.image.height * pixel_width)) / 2
        self.offset = (x_offset, y_offset)

        print self.data['width'], (self.image.width * pixel_width)
        print self.data['height'], (self.image.height * pixel_width)

    
    def paintEvent(self, _):
        if self.image is None:
            return

        painter = qw.QStylePainter(self)
        option = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + self.offset[0]
        y = option.rect.y() + self.offset[1]
        
        for color in (MAIN_BRUSHES, SHADOW_BRUSHES):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])

            self.paintPixels(self.image, painter, x, y)


    def keyPressEvent(self, _):
        self.switch(0)
                    
# ------------------------------------------------------------------------------------------------ #  

class Menu(SnakeLevel):
    menu_id = 0
    
    def __init__(self):
        super(Menu, self).__init__()

        self.menu_id = Menu.menu_id
        Menu.menu_id += 1
        
        self.menu_item_width = 103
        self.menu_item_height = 17
                
        self.selected_index = 0
        
        self.menu_items = []
        self.menu_signals = []
        self.menu_item_grids = {}
                
    
    def initialize(self, menu_items):
        '''
        Setup the menu with given items and signal connections. Should be pairs of
        text:signal_id.
        '''

        self.menu_items = []
        self.menu_signals = []
        self.menu_item_grids = {}

        # add each menu item to menu as fancy text
        #
        for menu_item_name, signal_id in menu_items:
            self.menu_items.append(menu_item_name)
            self.menu_signals.append(signal_id)
            menu_item_image = font.main_font.getImage(menu_item_name,
                                                      width=self.menu_item_width,
                                                      height=self.menu_item_height)
            self.menu_item_grids[menu_item_name] = menu_item_image
                
                
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
                    
                self.paintPixels(menu_item_grid, painter, x, w_y, invert)

                w_y += 16 * 4
                    
# ------------------------------------------------------------------------------------------------ #

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Arena(SnakeLevel):
    GAME_OVER = 'GAME OVER'
    
    def __init__(self):
        super(Arena, self).__init__()

        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(10,10,10,10)
        self.layout().setSpacing(0)
        
        self.setFocusPolicy(qc.Qt.StrongFocus)
        
        self.grid = Grid(self.width/16-2, self.height/16-4)
        
        self.snake_speed = 40
        
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
                paint(painter, x, w_y, text_grid)
                w_y += 16 * 4
                
            score_str = '{:04d}'.format(self.score_board.score_counter)
            
            sx = x
            for index in range(4):
                score_grid = font[score_str[index]]               
                paint(painter, sx, w_y, score_grid)
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


def draw(image):
    image_str = []
    for line in image.lines:
        check = 1
        line_str = []
        for _ in range(image.width):
            if line & check:
                line_str.append('#')
            else:
                line_str.append(' ')
            check = check << 1
        image_str.append(''.join(line_str)[::-1])
    print '\n'.join(image_str)


