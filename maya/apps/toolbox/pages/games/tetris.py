import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import cg_inventor.maya.apps.toolbox.page as page

import random



TITLE    = 'Games'
SUBTITLE = 'Tetris'

class Tetris(page.Page):
    def __init__(self):
        page.Page.__init__(self)
        self.title    = TITLE
        self.subtitle = SUBTITLE
        
        game_layout = qg.QHBoxLayout()
        game_layout.setContentsMargins(0,0,0,0)
        game_layout.setSpacing(6)
        self.addElement(game_layout)
        
        self.setFocusPolicy(qc.Qt.StrongFocus) 
        
        self.play_area = PlayArea()
        game_layout.addWidget(self.play_area)
        
        self.next_piece = NextPiece()
        
        button_layout = qg.QVBoxLayout()
        button_layout.setAlignment(qc.Qt.AlignTop)
        game_layout.addLayout(button_layout)
        
        self.score_label = qg.QLabel('Score: 0')
        self.score = 0
        
        start_button = qg.QPushButton('Start')
        end_button   = qg.QPushButton('End')
        reset_button = qg.QPushButton('Reset')
        button_layout.addWidget(self.next_piece)
        button_layout.addWidget(self.score_label)
        button_layout.addWidget(start_button)
        button_layout.addWidget(end_button)
        button_layout.addWidget(reset_button)
        
        start_button.clicked.connect(self.play_area.startGame)
        end_button.clicked.connect(self.play_area.stopGame)
        reset_button.clicked.connect(self.play_area.reset)
        
        self.connect(self.play_area, qc.SIGNAL('nextPiece'), self.next_piece.setPiece)
        self.connect(self.play_area, qc.SIGNAL('score'), self.updateScore)

        
    def keyPressEvent(self, event):
        key = event.key()
        if key == qc.Qt.Key_Left:
            self.play_area.moveLeft()
            
        elif key == qc.Qt.Key_Right:
            self.play_area.moveRight()
            
        elif key == qc.Qt.Key_Up:
            self.play_area.rotate()
            
        elif key == qc.Qt.Key_Down:
            self.play_area.moveDown()
        
        
    def focusOutEvent(self, event):
        self.play_area.stopGame()
        page.Page.focusOutEvent(self, event)
        
        
    def focusInEvent(self, event):
        page.Page.focusInEvent(self, event)
        
        
    def updateScore(self, value):
        self.score += value
        self.score_label.setText('Score: %s' %self.score)
        
        

class NextPiece(qg.QWidget):
    def __init__(self):
        qg.QWidget.__init__(self)
        
        self.setFixedHeight(80)
        self.setFixedWidth(120)       
        
        # colours
        #
        self.background_colour = qg.QColor(50, 50, 50)
        #self.hilight_colour    = qg.QColor(78, 78, 78)
        #self.shadow_colour     = qg.QColor(30, 30, 30)
        self.black_colour      = qg.QColor(0,0,0)
        
        self._piece = None
        
    
    def setPiece(self, piece_index):
        self._piece = Piece(piece_index)
        if piece_index == SQUARE:
            self._piece.position[0] = 2
            self._piece.position[1] = 1.25
        elif piece_index in (L_SHAPE, L_SHAPE_REV):
            self._piece.position[0] = 2.5
            self._piece.position[1] = 2.25
        elif piece_index == STRAIGHT:
            self._piece.position[0] = 2
            self._piece.position[1] = 1.75
        elif piece_index == WEDGE:
            self._piece.position[0] = 2.5
            self._piece.position[1] = 2.25
        elif piece_index in (ZIGZAG, ZIGZAG_REV):
            self._piece.position[0] = 2.5
            self._piece.position[1] = 1.25
        self.update()

        
    def paintEvent(self, pEvent):
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        height = option.rect.height() - 1
        width  = option.rect.width() - 1

        # draw play area
        #
        background_colour = self.background_colour
        #hilight_colour    = self.hilight_colour
        #shadow_colour     = self.shadow_colour
        black_colour      = self.black_colour

        brush = qg.QBrush(background_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(black_colour)
        painter.drawRect(0, 0, width, height)
        
#         painter.setPen(hilight_colour)
#         painter.drawLine(width, 0, width, height)
#         painter.drawLine(0, height, width, height)
        
        painter.setPen(qg.QColor(240, 240, 240))
        painter.drawText(qc.QPoint(5,15), 'NEXT PIECE')
        
        if not self._piece: return
        

         
        def drawBlock(block, x, y):            
            main, hi, lo, mid = block.colours
             
            main_brush  = qg.QBrush(main,  qc.Qt.SolidPattern)
            hi_brush    = qg.QBrush(hi,    qc.Qt.SolidPattern)
            lo_brush    = qg.QBrush(lo,    qc.Qt.SolidPattern)
            mid_brush   = qg.QBrush(mid,   qc.Qt.SolidPattern)
                         
            size = 20
 
            painter.setPen(main)
            painter.fillRect(x, y, size, size, main_brush)
             
            a = qc.QPoint(x , y) 
            b = qc.QPoint(x + size, y)                        
            c = qc.QPoint(x + size, y + size)
            d = qc.QPoint(x, y + size)
             
            ao = qc.QPoint(a.x() + 3, a.y() + 3)
            bo = qc.QPoint(b.x() - 3, b.y() + 3)
            co = qc.QPoint(c.x() - 3, c.y() - 3)
            do = qc.QPoint(d.x() + 3, d.y() - 3)
  
            # hilite
            #
            painter.setBrush(hi_brush); painter.setPen(hi)
            painter.drawPolygon(qg.QPolygon([a, b, bo, ao]))
            painter.setBrush(mid_brush); painter.setPen(mid)
            painter.drawPolygon(qg.QPolygon([a, ao, do, d]))
            painter.drawPolygon(qg.QPolygon([b, c, co, bo]))
            painter.setBrush(lo_brush); painter.setPen(lo)                       
            painter.drawPolygon(qg.QPolygon([d, do, co, c]))
             
            # black outline
            #
            painter.setPen(black_colour)
            painter.drawLine(a, b)
            painter.drawLine(b, c)
            painter.drawLine(c, d)
            painter.drawLine(d, a)
        
        # draw piece
        # 
        piece = self._piece
        x_offset, y_offset = piece.position
        for row in piece._blocks:
            for block in row:
                if block is None: continue
                 
                x, y = block.position
                x += x_offset; y += y_offset
                x *= 20; y *= 20
                 
                drawBlock(block, x, y)
        

        


class PlayArea(qg.QWidget):
    BACKGROUND = 'background'
    HEIGHT = 20
    WIDTH  = 10
    
    GAME_OVER = 'GAME OVER'
    
    
    def __init__(self):
        qg.QWidget.__init__(self)
        
        self.setFixedHeight(self.HEIGHT * 20)
        self.setFixedWidth(self.WIDTH * 20)
        
        self._board = []
        for _ in range(self.HEIGHT):
            self._board.append([])
            for _ in range(self.WIDTH):
                self._board[-1].append(None) 
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animate)
        
        self._anim_speed = 300
        self._pause = False
        self._game_over = False
        
        self.background_colour = qg.QColor(50, 50, 50)
        #self.hilight_colour    = qg.QColor(78, 78, 78)
        #self.shadow_colour     = qg.QColor(30, 30, 30)
        self.black_colour      = qg.QColor(0,0,0)
        
        self._completed_rows = []
        self._removing_anim_counter = 0
        self._next_piece_index = random.randint(1,7)        
        
        self.connect(self, qc.SIGNAL(self.GAME_OVER), self.gameOver)
        
        self.addPiece()
                
        
    def addPiece(self):
        self._current_piece = new_piece = Piece(self._next_piece_index)
        new_piece.position = [4, - new_piece.height]
        self._next_piece_index = random.randint(1,7)
        self.emit(qc.SIGNAL('nextPiece'), self._next_piece_index)
        
        
    def startGame(self):
        self._anim_timer.start(self._anim_speed)
        self._pause = False
        
        
    def stopGame(self):
        self._anim_timer.stop()
        self._pause = True        
        self.update()
        
    
    def gameOver(self):
        self._anim_timer.stop()
        self._game_over = True
        self.update()
        
    
    def reset(self):
        self.pieces = {}
        self.piece_count = 0        
    
    
    def moveLeft(self):
        if self._pause or self._game_over: return
        
        if not self._current_piece: return
        
        position = self._current_piece.position
        
        for row in self._current_piece._blocks:
            for block in row:
                if block is None: continue
                
                block_position = block.position 
                
                if position[0] + block_position[0] == 0:
                    return
                
                x = position[0] + block_position[0] - 1
                y = position[1] + block_position[1]
                if self._board[y][x] is not None:
                    return
        
        position[0] -= 1      

        self.update()

        
    
    def moveRight(self):
        if self._pause or self._game_over: return
        
        if not self._current_piece: return
        
        position = self._current_piece.position
        
        for row in self._current_piece._blocks:
            for block in row[::-1]:
                if block is None: continue
                
                block_position = block.position 
                
                if position[0] + block_position[0] == 9:
                    return
                              
                x = position[0] + block_position[0] + 1
                y = position[1] + block_position[1]
                if self._board[y][x] is not None:
                    return
        
        position[0] += 1 

        self.update()
        
        
        
    def moveDown(self):
        if self._pause or self._game_over: return
        
        if not self._current_piece: return
        
        self._current_piece.position[1] += 1

        if self._pieceCollideDown():
            if self._storePiece() is False:
                self.addPiece()
            else:
                return
            
        self.update()
    
    
    
    def rotate(self):
        if self._pause or self._game_over: return
        
        if not self._current_piece: return
        
        position = self._current_piece.position
        center   = self._current_piece._center
        style    = self._current_piece._style
        if position[0] in (0, 9): return
        
        if (position[0] + center[0]) == 0: return
        
        if self._board[position[1]][position[0]-1] is not None:
            return
        if self._board[position[1]][position[0]+1] is not None:
            return
        
        if style == STRAIGHT:
            if position[0] == 8: return
            if self._board[position[1]][position[0]-1] is not None:
                return
            if self._board[position[1]][position[0]+2] is not None:
                return        
        
        for block in self._current_piece._blocks[-1]:
            if block is None: continue
            
            block_position = block.position
            x = position[0] + block_position[0]
            y = position[1] + block_position[1]
            
            if (y == 19) or (style == STRAIGHT and y == 18): return
             
            if self._board[y + 1][x] is not None:
                return
            
            if (style == STRAIGHT) and self._board[y + 2][x] is not None:
                return

        self._current_piece.rotate()
        self.update()
        

    def _animate(self):
        self.moveDown()
        
    
    def _animateRemovingRows(self):
        if self._removing_anim_counter == 14:
            self._removingRowsEnd()
            return

        self.update()
        self._removing_anim_counter += 1
        
    
    def _pieceCollideDown(self):
        if not self._current_piece: return False
        
        position = self._current_piece.position

        for row in self._current_piece._blocks[::-1]:
            for block in row:
                if block is None: continue
                
                block_position = block.position
                if (position[1] + block_position[1]) == 20:
                    return True
                
                x = position[0] + block_position[0]
                y = position[1] + block_position[1]
                if y < 0: continue
                
                if self._board[y][x] is not None:
                    return True       
        
        return False
    
    
    def _storePiece(self):
        position = self._current_piece.position
        
        for row in self._current_piece._blocks:
            for block in row:
                if block is None: continue
                block_position = block.position
                x = position[0] + block_position[0]
                y = position[1] + block_position[1] - 1
                
                if y < 0:
                    self.emit(qc.SIGNAL(self.GAME_OVER))
                    return             

                self._board[y][x] = block
                
        
        self._current_piece = None
        
        return self._removingRowsStart()
            
    
    def _removingRowsStart(self):
        completed_rows = self._completed_rows = []
        for index, row in enumerate(self._board):
            complete = True
            for block in row:
                if block is None:
                    complete = False
                    break
            if complete is True:
                completed_rows.append(index)
                
        if len(completed_rows) == 0: return False
        
        self._removing_anim_counter = 0
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self._animate)
        self._anim_timer.timeout.connect(self._animateRemovingRows)
        self._anim_timer.start(20)
        
        self.emit(qc.SIGNAL('score'), 40 * len(completed_rows))
        
        return True
        
        
    def _removingRowsEnd(self):
        self._anim_timer.stop()
        self._anim_timer.timeout.disconnect(self._animateRemovingRows)
        
        for row_index in self._completed_rows:
            tmp_board = list(self._board)
            for index in range(row_index - 1, -1, -1):
                self._board[index + 1] = tmp_board[index]
            
            new_row = []
            for _ in range(self.WIDTH):
                new_row.append(None)
            self._board[0] = new_row
            
        self._completed_rows = []        
        self._removing_anim_counter = 0

        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(self._anim_speed)
        
        self.addPiece()
        self.update()
                
        
        
    def paintEvent(self, pEvent):
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        height = option.rect.height() - 1
        width  = option.rect.width() - 1
        
        # draw play area
        #
        background_colour = self.background_colour
        #hilight_colour    = hilight_colour
        #shadow_colour     = shadow_colour
        black_colour      = self.black_colour
        
        brush = qg.QBrush(background_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        #painter.setPen(black_colour)
        painter.drawRect(0, 0, width, height)
        
        grid_colour = qg.QColor(52,52,52)
        painter.setPen(grid_colour)
        for index in range(1,self.HEIGHT):
            painter.drawLine(1, index * 20, width - 1, index * 20)
        for index in range(1,self.WIDTH):
            painter.drawLine(index * 20, 1, index * 20, height - 1)
        
#         painter.setPen(hilight_colour)
#         painter.drawLine(width, 0, width, height)
#         painter.drawLine(0, height, width, height)
        

        black_brush = qg.QBrush(black_colour, qc.Qt.SolidPattern)
        
        if self._game_over: painter.setOpacity(0.3)            
         
        def drawBlock(block, x, y, offset=0):            
            main, hi, lo, mid = block.colours
             
            main_brush  = qg.QBrush(main,  qc.Qt.SolidPattern)
            hi_brush    = qg.QBrush(hi,    qc.Qt.SolidPattern)
            lo_brush    = qg.QBrush(lo,    qc.Qt.SolidPattern)
            mid_brush   = qg.QBrush(mid,   qc.Qt.SolidPattern)
                         
            size = 20
 
            painter.setPen(main)
            painter.fillRect(x + offset, y + offset, size - offset - offset, size - offset - offset, main_brush)
             
            a = qc.QPoint(x + offset, y + offset) 
            b = qc.QPoint(x + size - offset, y + offset)                        
            c = qc.QPoint(x + size - offset, y + size - offset)
            d = qc.QPoint(x + offset, y + size - offset)
             
            if   offset < 3: rim_size = 3
            elif offset < 6: rim_size = 2
            else:            rim_size = 1
            ao = qc.QPoint(a.x() + rim_size, a.y() + rim_size)
            bo = qc.QPoint(b.x() - rim_size, b.y() + rim_size)
            co = qc.QPoint(c.x() - rim_size, c.y() - rim_size)
            do = qc.QPoint(d.x() + rim_size, d.y() - rim_size)
  
            # hilite
            #
            if offset < 9:
                painter.setBrush(hi_brush); painter.setPen(hi)
                painter.drawPolygon(qg.QPolygon([a, b, bo, ao]))
                painter.setBrush(mid_brush); painter.setPen(mid)
                painter.drawPolygon(qg.QPolygon([a, ao, do, d]))
                painter.drawPolygon(qg.QPolygon([b, c, co, bo]))
                painter.setBrush(lo_brush); painter.setPen(lo)                       
                painter.drawPolygon(qg.QPolygon([d, do, co, c]))
             
            # black outline
            #
            painter.setPen(black_colour)
            painter.drawLine(a, b)
            painter.drawLine(b, c)
            painter.drawLine(c, d)
            painter.drawLine(d, a)
             
        # draw board
        #
        completed_rows = self._completed_rows
        removing_counter = self._removing_anim_counter
        for row_index, row in enumerate(self._board):
            for column_index, block in enumerate(row):
                if block is None: continue
                if row_index in completed_rows:
                    if removing_counter == 14:
                        continue
                    offset = 0
                    if removing_counter < 3:
                        offset = -removing_counter
                    else: 
                        offset = removing_counter - 4

                    drawBlock(block, column_index * 20, row_index * 20, offset)
                        
                    continue
                drawBlock(block, column_index * 20, row_index * 20)
                
        # draw piece
        # 
        if self._current_piece:
            piece = self._current_piece
            x_offset, y_offset = piece.position
            for row in piece._blocks:
                for block in row:
                    if block is None: continue
                     
                    x, y = block.position
                    x += x_offset; y += y_offset
                    x *= 20; y *= 20
                     
                    drawBlock(block, x, y)
                    
        painter.setPen(black_colour)
        painter.drawLine(width, 0, width, height)
        painter.drawLine(0, height, width, height)
        painter.drawLine(0, 0, width, 0)
        painter.drawLine(0, 0, 0, height)
        
        
        if self._pause:
            painter.setOpacity(1.0)
            font = qg.QFont(painter.font())
            font.setPointSize(12)
            painter.setPen(qg.QColor(240, 240, 240))
            painter.setFont(font)
            painter.drawText(qc.QPoint(self.WIDTH * 7.2, self.HEIGHT * 10), 'PAUSE')
        
        
        if self._game_over:
            painter.setOpacity(1.0)
            font = qg.QFont(painter.font())
            font.setBold(True)
            font.setPointSize(20)
            painter.setPen(qg.QColor(240, 240, 240))
            painter.setFont(font)
            painter.drawText(qc.QPoint(self.WIDTH * 1.8, self.HEIGHT * 10), 'GAME OVER')

                
# Piece types
#
SQUARE       = 1
L_SHAPE      = 2
L_SHAPE_REV  = 3
STRAIGHT     = 4
WEDGE        = 5
ZIGZAG       = 6
ZIGZAG_REV   = 7

# Piece Colours
#
MAIN = 1
HI   = 2
LO   = 3
MID  = 4

COLOURS = {}
COLOURS[SQUARE] = {MAIN : (240, 240,   0), # YELLOW
                   HI   : (242, 242, 166),
                   LO   : (112, 112,  45),
                   MID  : (189, 189,   0)}

COLOURS[L_SHAPE] = {MAIN : (240, 160,   0), # ORANGE
                    HI   : (242, 217, 166),
                    LO   : (112,  90,  45),
                    MID  : (189, 126,   0)}

COLOURS[L_SHAPE_REV] = {MAIN : (  0,   0, 240), # BLUE
                        HI   : (166, 166, 242),
                        LO   : ( 45, 45,  112),
                        MID  : (  0,   0, 189)}

COLOURS[STRAIGHT] = {MAIN : (  0, 240, 240), # LIGHT BLUE
                     HI   : (166, 242, 242),
                     LO   : ( 45, 112, 112),
                     MID  : (  0, 189, 189)}

COLOURS[WEDGE] = {MAIN : (160,   0, 240), # PURPLE
                  HI   : (217, 166, 242),
                  LO   : (90,   45, 112),
                  MID  : (126,   0, 189)}

COLOURS[ZIGZAG] = {MAIN : (  0, 240,   0), # GREEN
                   HI   : (166, 242, 166),
                   LO   : ( 42, 112,  45),
                   MID  : (  0, 189,   0)}

COLOURS[ZIGZAG_REV] = {MAIN : (240,  0,    0), # RED
                       HI   : (242, 166, 166),
                       LO   : (112,  45,  45),
                       MID  : (189,  0,    0)}
        
class Piece(object):
    MAIN = 1
    HI   = 2
    LO   = 3
    MID  = 4
    
    def __init__(self, style):
        self._style    = style
        self._reverse  = None
        self._rotation = 0
        self._center = (0,0)
        
        self.position = [0,0]
        
        self._all_blocks = [Block(style),Block(style),Block(style),Block(style)]
        self.rotate()
        
        
        
    def rotate(self):        
        blocks = self._all_blocks
        rotation = self._rotation
        
        rev = False
        if self._style in [L_SHAPE_REV, ZIGZAG_REV]:
            rev = True
            
        if self._style == SQUARE:               
            self._blocks = [[blocks[0], blocks[1]],
                            [blocks[2], blocks[3]]]
            self._center = (0, 0)
        
        if self._style in [L_SHAPE, L_SHAPE_REV]:            
            if rotation == 0:                
                self._blocks = [[None,      None,      blocks[0]],
                                [blocks[1], blocks[2], blocks[3]]]
                
                self._center = (1, 1)
                
                
            elif rotation == 1:
                self._blocks = [[blocks[0], blocks[1]],
                                [None,      blocks[2]], 
                                [None,      blocks[3]]]
                if not rev: self._center = (1, 1)
                else:       self._center = (1, 0)
                
            elif rotation == 2:
                self._blocks = [[blocks[1], blocks[2], blocks[3]],
                                [blocks[0], None,      None     ]]
                self._center = (0, 1)
                
            elif rotation == 3:
                self._blocks = [[blocks[1], None     ],
                                [blocks[2], None     ], 
                                [blocks[0], blocks[3]]]
                if not rev: self._center = (1, 0)
                else:       self._center = (1, 1)
                
                self._rotation = -1
            self._rotation += 1
        
        elif self._style == STRAIGHT:
            if rotation == 0:
                self._blocks = [[blocks[0], blocks[1], blocks[2], blocks[3]]]
                self._center = (0, 1)
                
            elif rotation == 1:
                self._blocks = [[blocks[0]], 
                                [blocks[1]], 
                                [blocks[2]], 
                                [blocks[3]]]
                self._center = (1, 0)
                
                self._rotation = -1
            self._rotation += 1
            
        elif self._style == WEDGE:                
            if rotation == 0:
                self._blocks = [[None,      blocks[0], None     ],
                                [blocks[1], blocks[2], blocks[3]]]
                self._center = (1, 1)
                
            elif rotation == 1:
                self._blocks = [[None,      blocks[0]],
                                [blocks[1], blocks[2]],
                                [None,      blocks[3]]]
                self._center = (1, 1)
                
            elif rotation == 2:
                self._blocks = [[blocks[0], blocks[1], blocks[2]],
                                [None,      blocks[3], None     ]]
                self._center = (0, 1)
                
            elif rotation == 3:
                self._blocks = [[blocks[0], None     ],
                                [blocks[1], blocks[2]],
                                [blocks[3], None     ]]
                self._center = (1, 0)
                
                self._rotation = -1
            self._rotation += 1
            
        elif self._style in [ZIGZAG, ZIGZAG_REV]:
            if self._rotation == 0:
                self._blocks = [[None,      blocks[0], blocks[3]],
                                [blocks[1], blocks[2], None     ]]
                self._center = (0, 1)
                
            elif rotation == 1:
                self._blocks = [[blocks[0], None     ],
                                [blocks[1], blocks[2]],
                                [None,      blocks[3]]]
                if not rev: self._center = (1, 0)
                else:       self._center = (1, 1)
                
                self._rotation = -1
            self._rotation += 1
        
        
        if rev is False:
            for row_index, row in enumerate(self._blocks):
                for column_index, block in enumerate(row):
                    if block is None: continue                
                    block.position = [column_index - self._center[1], row_index - self._center[0]]
        
        else:
            for row_index, row in enumerate(self._blocks):
                for column_index, block in enumerate(row[::-1]):
                    if block is None: continue                
                    block.position = [column_index - self._center[1], row_index - self._center[0]]
        
        
        self.height = len(self._blocks) - self._center[0]
        #self.width  = len(self._blocks[0]) - self._center[1]
        
        
class Block():
    def __init__(self, style):        
        self.position = [0,0]

        style_colours = COLOURS[style]
        self.colours = [qg.QColor(*style_colours[MAIN]),
                        qg.QColor(*style_colours[HI]),
                        qg.QColor(*style_colours[LO]),
                        qg.QColor(*style_colours[MID])]