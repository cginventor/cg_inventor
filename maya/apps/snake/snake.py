import random

import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

from collections import OrderedDict

from weakref import proxy

# ------------------------------------------------------------------------------------------------ #

BACKGROUND_COLOUR = (128, 175, 1)
MAIN_COLOUR = qg.QColor(18,30,0)
SHADOW_COLOUR = qg.QColor(18,30,0,150)

MAIN_BRUSHES = [qg.QPen(MAIN_COLOUR), qg.QBrush(MAIN_COLOUR)]        
SHADOW_BRUSHES = [qg.QPen(SHADOW_COLOUR), qg.QBrush(SHADOW_COLOUR)]

# ------------------------------------------------------------------------------------------------ #

class Snake2(qw.QDialog):
    ''' Main Game Window. Defines game panels and connections. '''
    TITLE = 'SNAKE II'
     
    def __init__(self):
        qw.QDialog.__init__(self)
        self.setWindowTitle('SNAKE II')
        qw.QDialog.setWindowFlags(self, qc.Qt.WindowStaysOnTopHint)
        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.setFixedWidth(452)
        self.setFixedHeight(324)
        
        self.setStyleSheet('background-color: rgb{};'.format(BACKGROUND_COLOUR))
        
        self.widget_stack = qw.QStackedWidget()
        self.layout().addWidget(self.widget_stack)
        
        self.title_panel = Title()
        self.main_menu_panel = Menu()
        self.level_menu_panel = Menu()
        self.game_panel = Game(100)
        
        self.title_panel.addLink(self.main_menu_panel)
        
        menu_items = OrderedDict([('New Game', self.game_panel), 
                                  ('Level', self.level_menu_panel),
                                  ('High Scores', None),
                                  ('Options', None)])
        
        self.main_menu_panel.initialize(menu_items)
        
        level_items = OrderedDict([('Slowest', self.main_menu_panel), 
                                   ('Slow'   , self.main_menu_panel),
                                   ('Normal' , self.main_menu_panel),
                                   ('Fast'   , self.main_menu_panel),
                                   ('Fastest', self.main_menu_panel)])
    
        self.level_menu_panel.initialize(level_items)        
        
        self.widget_stack.addWidget(self.title_panel)
        self.widget_stack.addWidget(self.main_menu_panel)
        self.widget_stack.addWidget(self.game_panel)
        self.widget_stack.addWidget(self.level_menu_panel)
        
        self.connect(self.title_panel, qc.SIGNAL('panelChanged(int)'), self.menuSwitchPanel)
        self.connect(self.main_menu_panel, qc.SIGNAL('panelChanged(int)'), self.menuSwitchPanel)
        
    
    def menuSwitchPanel(self, panel_index):
        current_widget = self.widget_stack.currentWidget()
        for index in range(self.widget_stack.count()):
            widget = self.widget_stack.widget(index)
            if panel_index != widget.panel_id:
                continue
            
            current_widget.end()            
            self.widget_stack.setCurrentWidget(widget)
            widget.start()
            break
        
    
    def keyPressEvent(self, event):
        current_widget = self.widget_stack.currentWidget()
        return current_widget.keyPressEvent(event)      
    
    
    def __del__(self):
        print 'deleting'                  
            
# ------------------------------------------------------------------------------------------------ #

class Panel(qw.QWidget):
    panel_id = 0
    
    def __init__(self):
        qw.QWidget.__init__(self)        
        self.width, self.height = 452, 324
        self.panel_id = Panel.panel_id
        Panel.panel_id += 1
        
        self.current_index = 0
        self.links = {}    
    
    
    @staticmethod
    def clear():
         Panel.panels = {}
        
    
    def addLink(self, widget):
        if widget:
            self.links[self.current_index] = proxy(widget)
        self.current_index += 1
        
        
    def start(self):
        pass
    
    
    def end(self):
        pass
        
        
    def emitPanelChange(self, index):
        next_panel = self.links.get(index, None)
        if not next_panel:
            return 
        
        self.emit(qc.SIGNAL('panelChanged(int)'), next_panel.panel_id)
        
    
    def __del__(self):
        print 'deleting panel'
        
# ------------------------------------------------------------------------------------------------ #
 
def new_uncompress(image_str, width):
    lines = []
    for line in image_str.split('-'):
        lines.append(int(line, 16))
    return lines

# TITLE_IMAGE = (95, 76, \
# 'c00000000000000c00007-1e00000004030001e000f9-7e0000f01c070087e00f81-fe0381f07e1f01cff1f801-1ff1f'\
# '81f0fe3f03efff0001-3ff1f81f0fe3f03f7f8000f-7ff1fc3f1fe1f87ef20031f-ffe1fc3e1fe1f8fde201f18-ff01f'\
# 'e3e3ff039fb8301f18-1fe03fe3e3ef0bbf781f1918-1f803fe3e3cf3bff780f1918-3f003ff3e7cffdfe78811918-3e'\
# '001ef3e7c7fdfc7bc11918-7c0fcefbef87fdf83fc11918-7cffee7bef8ff1f83e011918-7fffee7fefbfc7fc3c01191'\
# 'f-7fffee3fefffc7fe1c711919-3f07ee1fdfffe7ff1cf11e01-fee1fdfe3e7df9ff11801-1fde0fdf03e7cf8fe7000f'\
# '-3fde0e1f0103c70f98007f-ffbe007f007bc20f1003f8-3ff78007e01c84004101fc0-1ffe600008030f000018fe00-'\
# '1ffc000003de71f8000ff000-1ff000000630c00c00078000-1fc000000589c00400020000-f00000006c2d006000000'\
# '00-c00007ffad423c200000000-3d55719868300000000-1eaabc0000c100000000-f555e000004300000000-7aaabff'\
# 'f001ffc0000000-d555f8008ff1578000000-1aabf0c003901aac000000-355e00700d303556000000-2ff3802ff9607'\
# 'ebff80000-3af6802585c0c1e00e0000-775d801583818700038700-68eb000d83031c00009880-1d47580038606300f'\
# 'f07040-7aaffe0068c0c607eb86c20-d55f5ffe89818c1cd682610-1afaabaaa130318376ac3f08-15dd555560606306'\
# 'c5742788-1beaaaaae0c0c20d1ebeb086-15555555c181861b7d7d3ec5-1aeaffbf430304323ffafcc5-157fe4e24606'\
# '042343ffc1c2-ebfe4828c0cf431a0000ae2-75ff57b0819f419500035e3-ebf2085833f60cbf00fbe1-75fc6f9067f3'\
# '0651ff95f1-11afaafb04ff98320002bf1-fcd6327a0cffcc1900055f1-3fe6b7f7a0c7fe64c8001bf1-7ff35f57a0f1'\
# 'ff344781f671-7ff9afb7a09c0f1868ff2b31-7ffcd7e7b007e07024009692-7ffe77cf98003fc028002c7c-3ffe031f'\
# 'cc0000006f81f001-ffffb9fe7800000c0ff07ff-1fffbcff0f800079e007ff8-1ffd2ffe0ffffc3fffff80-0-0-0-0-'\
# 'eeeee1d5ddc000000-aa88811c914000000-eeeee19c99c000000-8c822114918000000-8aeee1d49d4000000-0-0-0')

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

class Title(Panel):
    title_image = new_uncompress(TITLE_IMAGE[2], TITLE_IMAGE[0])
    
    def __init__(self):
        Panel.__init__(self)
        
        self.x_offset = (self.width - (TITLE_IMAGE[0] * 4)) / 2
        self.y_offset = (self.height - (TITLE_IMAGE[1] * 4)) / 2
    
    
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option  = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + self.x_offset
        y = option.rect.y() + self.y_offset
        
        for index, color in enumerate((MAIN_BRUSHES, SHADOW_BRUSHES)):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])
            
            for i in range(TITLE_IMAGE[1]):
                check = 1
                line = Title.title_image[i]
                for j in range(TITLE_IMAGE[0]):
                    if line & check:
                        gx, gy = x + (j*3) + 1 + j, y + (i*3) + 1 + i
                        painter.drawRect(gx, gy, 2, 2)
                    check <<= 1
            #drawGrid(painter, x, y, title)
            

    def keyPressEvent(self, event):
        self.emitPanelChange(0)
    
    
    def __del__(self):
        print 'deleting title'
                    
# ------------------------------------------------------------------------------------------------ #  

class Menu(Panel):
    menu_id = 0
    
    def __init__(self):
        Panel.__init__(self)
        self.menu_id = Menu.menu_id
        Menu.menu_id += 1
        
        self.menu_item_width = 100
        self.menu_item_height = 16
                
        self.selected_index = 0
        
        self.menu_items = []
        self.menu_item_grids = {}
                
    
    def initialize(self, menu_items):
        self.menu_items = menu_items.keys()
        self.menu_item_grids = {}
        for menu_item_name, panel in menu_items.items():
            self.addLink(panel)
             
            grids = [[0 for _ in range(self.menu_item_width)] for _ in range(16)]
            self.menu_item_grids[menu_item_name] = grids
             
            indent = [4, 3]
            for letter in menu_item_name:
                letter_grid = font[letter]
                grid_width = len(letter_grid[0])
                for index, row in enumerate(letter_grid):
                    grids[index+indent[1]][indent[0]:indent[0]+grid_width] = row
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
            self.emitPanelChange(self.selected_index)           
        
        
    def paintEvent(self, event):
        painter = qw.QStylePainter(self)
        option  = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x() + 24
        y = option.rect.y() + 24
        
        for index, color in enumerate((MAIN_BRUSHES, SHADOW_BRUSHES)):
            x += 1
            y += 1
            
            painter.setPen(color[0])
            painter.setBrush(color[1])            
            
            w_y = y
            for menu_item in self.menu_items:
                menu_item_grid = self.menu_item_grids[menu_item]
                
                invert = False
                if self.menu_items.index(menu_item) == self.selected_index:
                    invert = True
                    
                drawGrid(painter, x, w_y, menu_item_grid, invert)
                
                w_y += 16 * 4
                
                
    def __del__(self):
        print 'deleting menu'
                    
# ------------------------------------------------------------------------------------------------ #

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Game(Panel):
    GAME_OVER = 'GAME OVER'
    
    def __init__(self, snake_speed):
        Panel.__init__(self)
        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(10,10,10,10)
        self.layout().setSpacing(0)
        
        self.setFocusPolicy(qc.Qt.StrongFocus)
        
        self.grid = Grid(self.width/16-2, self.height/16-4)
        
        self.snake_speed = snake_speed
        
        self.score_board = ScoreBoard(self.width/16-2)
        self.layout().addWidget(self.score_board)
                
        self.ui = GameGrid(self.grid)
        self.layout().addWidget(self.ui)
        
        self.score_text = ['Game Over!', 'TOP SCORE:', 'SCORE:']        
        self.score_text_grids = {}
        
        for text_item in self.score_text:
            grids = [[0 for _ in range(100)] for _ in range(16)]
            self.score_text_grids[text_item] = grids
            
            indent = [0, 0]
            for letter in text_item:
                letter_grid = font.get(letter, None)
                if letter_grid is None:
                    continue
                
                grid_width = len(letter_grid[0])
                for index, row in enumerate(letter_grid):
                    grids[index+indent[1]][indent[0]:indent[0]+grid_width] = row
                    
                indent[0] += grid_width + 1
        
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
                drawGrid(painter, x, w_y, text_grid)                
                w_y += 16 * 4
                
            score_str = '{:04d}'.format(self.score_board.score_counter)
            
            sx = x
            for index in range(4):
                score_grid = font[score_str[index]]               
                drawGrid(painter, sx, w_y, score_grid)
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
        option  = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 4
        width  = option.rect.width() - 4
        
        for index, color in enumerate((MAIN_BRUSHES, SHADOW_BRUSHES)):
            painter.setPen(color[0])
            painter.setBrush(color[1])
            
            x += index
            y += index
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
                            if block_value & check:#(1 << (gj * 4 + gi)):
                                gx, gy = block_x + (gj*3) + 1 + gj, block_y + (gi*3) + 1 + gi
                                painter.drawRect(gx, gy, 2, 2)
                            check = check << 1
                    
                    #drawGrid(painter, block_x, block_y, block.draw())
                    #drawGrid(painter, block_x, block_y, block_draw)
                    
    
    def __del__(self):
        print 'deleting game grid'

# ------------------------------------------------------------------------------------------------ #
        
def drawGrid(painter, x, y, grid, invert=False):
    for i in range(len(grid[0])):
        for j in range(len(grid)):
            draw = grid[j][i]
            if not (draw if not invert else not draw):
                continue
            gx, gy = x + (i*3) + 1 + i, y + (j*3) + 1 + j
            painter.drawRect(gx, gy, 2, 2)

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
        symbols = {Block.FREE:'_', 
                   Block.HEAD:'&', 
                   Block.BODY:'#',
                   Block.TAIL:'^',
                   Block.CORNER:'%',
                   Block.APPLE:'O'}
                
        rows = []
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
        option  = qw.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 8
        width  = option.rect.width() - 4
        
        for index, color in enumerate((MAIN_BRUSHES, SHADOW_BRUSHES)):
            painter.setPen(color[0])
            painter.setBrush(color[1])
            
            x += index
            y += index
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

    DRAW = {BODY: {LEFT:0xbd0, RIGHT:0xdb0, UP:0x6246, DOWN:0x6426},
    #DRAW = {BODY: {LEFT:0xdb0, RIGHT:0xbd0, UP:0x6426, DOWN:0x6246},
            HEAD: {LEFT:0xe68, RIGHT:0x761, UP:0xa660, DOWN:0x66a},
            HEAD_OPEN: {LEFT:0x2c4a, RIGHT:0x4325, UP:0x5690, DOWN:0x965},
            TAIL: {LEFT:0xf30, RIGHT:0xfc0, UP:0x4466, DOWN:0x6644},
            CORNER: {LEFT:0xca6, RIGHT:0x356, UP:0x6ac0, DOWN:0x6530}}
    
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
# title = \
# '!11-2!58-2!19-3!10-4!30-!8-2!15-4!13-5!2-!8-6!17-4!7-3!7-3!8-!4-6!9-5!6-!7-7!7-3!6-5!5-6!4-5!7-3'\
# '!2-8!3-6!10-!6-9!3-6!6-5!4-7!3-6!6-5!-12!15-!5-10!3-6!6-5!4-7!3-6!6-6!-8!15-4!4-11!3-7!4-6!3-8!4'\
# '-6!4-6!-4!2-!11-2!3-5!3-11!4-7!4-5!4-8!4-6!3-6!-4!3-!8-5!3-2!6-8!7-8!3-5!3-10!6-3!2-6!-3!5-2!7-5'\
# '!3-2!5-8!7-9!3-5!3-5!-4!4-!-3!-6!-4!6-5!3-2!2-!3-2!5-6!9-9!3-5!3-4!2-4!2-3!-10!-4!7-4!3-2!2-!3-2'\
# '!4-6!10-10!2-5!2-5!2-10!-8!2-4!3-!6-!3-2!2-!3-2!4-5!12-4!-4!2-5!2-5!3-9!-7!3-4!-4!5-!3-2!2-!3-2!'\
# '3-5!6-6!2-3!-5!-5!-5!4-9!-6!5-8!5-!3-2!2-!3-2!3-5!2-11!-3!2-4!-5!-5!3-8!3-6!5-5!8-!3-2!2-!3-2!3-'\
# '18!-3!2-10!-5!-8!3-9!4-4!9-!3-2!2-!3-23!-3!3-9!-14!3-10!4-3!3-3!3-!3-2!2-!3-2!2-!-6!5-6!-3!4-7!-'\
# '16!2-11!3-3!2-4!3-!3-4!8-!11-7!-3!4-7!-8!3-5!2-5!-6!2-9!3-!3-2!10-!10-7!-4!5-6!-5!6-5!2-5!2-5!3-'\
# '7!2-3!12-4!9-8!-4!5-3!4-5!7-!6-4!3-3!4-5!2-2!12-7!7-9!-5!10-7!9-4!-4!4-!5-4!3-!10-7!8-10!-4!12-6'\
# '!8-3!2-!4-!11-!5-!7-7!8-12!2-2!17-!9-2!4-4!19-2!3-7!11-11!24-4!-4!2-3!3-6!15-8!14-9!25-2!3-2!4-2'\
# '!10-2!15-4!17-7!27-!-2!3-!2-3!11-!16-!20-4!29-2!-2!4-!-2!-!9-2!36-2!19-12!-!-2!-!-!4-!3-4!4-!54-'\
# '4!-!-!-!-!-!-3!3-2!2-2!4-2!-!5-2!50-4!-!-!-!-!-!-4!18-2!5-!47-4!-!-!-!-!-!-4!22-!4-2!44-4!-!-!-!'\
# '-!-!-!-14!11-11!41-2!-!-!-!-!-!-!-6!11-!3-8!3-!-!-!-4!37-2!-!-!-!-!-6!4-2!12-3!2-!7-2!-!-!-!-2!3'\
# '5-2!-!-!-!-4!10-3!8-2!-!2-2!6-2!-!-!-!-!-2!34-!-8!2-3!9-!-9!2-!-2!6-6!-!-11!28-3!-!-4!-2!-!9-!2-'\
# '!-2!4-!-3!6-2!5-4!9-3!25-3!-3!-!-3!-2!10-!-!-2!5-3!6-2!4-3!14-3!4-3!16-2!-!3-3!-!-2!12-2!-2!5-2!'\
# '6-2!3-3!18-!2-2!3-!13-3!-!-!3-3!-!-2!13-3!4-2!6-2!3-2!8-8!5-3!5-!10-4!-!-!-!-11!10-2!-!3-2!6-2!3'\
# '-2!6-6!-!-3!4-2!-2!4-!8-2!-!-!-!-!-5!-!-12!-!3-!2-2!6-2!3-2!5-3!2-2!-!-2!-!5-!2-2!4-!6-2!-!-5!-!'\
# '-!-!-!-3!-!-!-!-!-!4-!2-2!6-2!3-2!5-2!-3!-2!-!-!-2!4-6!4-!5-!-!-3!-3!-!-!-!-!-!-!-!-!-!-2!6-2!6-'\
# '2!3-2!5-2!-2!3-!-!-3!-!4-!2-4!3-!5-2!-5!-!-!-!-!-!-!-!-!-!-!-3!5-2!6-2!4-!5-2!-!3-4!-!-5!-!-2!4-'\
# '!4-2!3-!-!-!-!-!-!-!-!-!-!-!-!-!-!-3!5-2!6-2!4-2!4-2!-2!-5!-!-5!-!2-5!-2!3-!-!2-2!-!-3!-!-!-9!-6'\
# '!-!4-2!6-2!5-!4-2!2-!3-11!-!-6!2-2!3-!-!2-!-!-!-10!2-!2-3!3-!2-!3-2!6-2!6-!4-!3-2!-!4-12!5-3!4-!'\
# '4-3!-!-9!2-!2-!5-!-!3-2!6-2!2-4!-!4-2!3-2!-!17-!-!-3!3-!5-3!-!-9!-!-!-4!-2!4-!6-2!2-5!-!5-2!2-!-'\
# '!-!14-2!-!-4!3-2!7-3!-!-6!2-!5-!4-!-2!5-2!2-6!-2!5-2!2-!-6!8-5!-5!4-!8-3!-!-7!3-2!-5!2-!5-2!2-7!'\
# '2-2!5-2!2-!-!3-10!2-!-!-5!3-!6-!3-2!-!-5!-!-!-!-5!-2!5-!2-9!2-2!5-2!2-!15-!-!-6!3-!3-6!2-2!-!-2!'\
# '3-2!2-!2-4!-!5-2!2-10!2-2!5-2!2-!13-!-!-!-5!3-!-9!2-2!-!-2!-7!-4!-!5-2!3-10!2-2!2-!2-2!2-!14-2!-'\
# '6!3-12!2-2!-!-5!-!-!-4!-!5-4!3-9!2-2!-!3-!3-4!6-5!-2!2-3!3-13!2-2!-!-5!-2!-4!-!5-!2-3!6-4!3-2!4-'\
# '2!-!3-8!2-!-!-2!2-2!3-14!2-2!-!-6!2-4!-2!9-6!6-3!6-!2-!10-!2-!-2!-!2-!2-!-14!2-3!-5!2-5!2-2!13-8'\
# '!8-!-!13-!-2!3-5!3-13!7-2!3-7!2-2!27-2!-5!6-5!11-!3-17!-3!2-8!2-4!23-2!6-8!5-11!6-14!-4!2-8!4-5!'\
# '16-4!2-4!10-12!13-11!-!2-!-11!5-18!4-23!414-3!-3!-3!-3!-3!4-3!-!-!-3!-3!-3!53-!-!-!-!-!3-!3-!6-!'\
# '3-3!2-!2-!3-!-!53-3!-3!-3!-3!-3!4-2!2-3!2-!2-2!2-3!53-!3-2!2-!5-!3-!4-!3-!-!2-!2-!3-2!54-!3-!-!-'\
# '3!-3!-3!4-3!-!-!2-!2-3!-!-!406'






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
        ui = Snake()
    
    ui.show()
    


def delete():
    global ui
    
    if ui:
        del(ui)
    
    ui = None
