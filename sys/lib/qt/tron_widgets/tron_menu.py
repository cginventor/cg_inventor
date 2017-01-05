import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

from functools import partial
from weakref import proxy


class TMenu(qg.QWidget):
    HEIGHT = 30
    
    def __init__(self):
        qg.QWidget.__init__(self)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(2,2,2,2)
        self.layout().setSpacing(0)
        
        self.setFixedHeight(self.HEIGHT)

        # setup pens
        #
        self._pens = {}
        self._pens['clear']  = qg.QPen(qg.QColor( 0,  0,  0), 1, qc.Qt.SolidLine)
        self._pens['border'] = qg.QPen(qg.QColor( 9, 10, 12), 2, qc.Qt.SolidLine)
        
        # setup brushes
        #
        self._brushes = {}
        self._brushes['clear']  = qg.QBrush(qg.QColor(0, 0, 0, 0))
        self._brushes['border'] = qg.QBrush(qg.QColor( 9, 10, 12))
        
        self._items = []
        self._current_item = None
        
        

    def addItem(self, item):
        previous_item = self._current_item
        self._current_item = item
        
        self._items.append(item)
        num_items = len(self._items)
        self.setFixedWidth((26 * num_items) + 8)
        
        self.layout().addWidget(item)
        
        for item in self._items:
            item._left_curve  = False
            item._right_curve = False  
            
        self._items[0]._left_curve  = True
        self._items[0]._right_curve = True

        if num_items > 1:
            self._items[0]._right_curve = False
            self._items[-1]._right_curve = True
            
            self._items[0].setFixedWidth(item.WIDTH + 1)
            self._items[-1].setFixedWidth(item.WIDTH + 1)
        
        item._next = None
        item._previous = None
        
        if previous_item:
            previous_item._next = proxy(item)
            item._previous = proxy(previous_item)
                
        
        
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1
        
        painter.setRenderHint(qg.QPainter.Antialiasing)
            
        painter.setBrush(self._brushes['border'])
        painter.setPen(self._pens['border'])
        painter.drawRoundedRect(qc.QRect(x+1, y+1, width-1, height-1), 2, 2)
        


class TMenuItem(qg.QPushButton):
    HEIGHT = 26
    WIDTH  = 26
        
    POS_LEFT   = 1
    POS_CENTRE = 2
    POS_RIGHT  = 3
       
    def __init__(self, *args, **kwargs):
        qg.QPushButton.__init__(self)
        if args and isinstance(args[0], (str, unicode, qc.QString)):
            self.setText(args[0])
        
        self.setFixedHeight(self.HEIGHT)
        self.setFixedWidth(self.WIDTH)
        
        self._hover = False
        
        # setup paint gradients
        #        
        self._inner_gradient = {}
        self._outer_gradient = {}
        
        inner_gradient = qg.QLinearGradient(0, 1, 0, self.HEIGHT - 1)
        inner_gradient.setColorAt(0, qg.QColor(51, 55, 58))
        inner_gradient.setColorAt(1, qg.QColor(31, 32, 34))
        self._inner_gradient['up'] = qg.QBrush(inner_gradient)          
        
        inner_gradient_down = qg.QLinearGradient(0, 1, 0, self.HEIGHT - 1)
        inner_gradient_down.setColorAt(0, qg.QColor(11, 13, 12))
        inner_gradient_down.setColorAt(1, qg.QColor(35, 36, 38)) 
        self._inner_gradient['down'] = qg.QBrush(inner_gradient_down)
            
        # setup pens
        #
        self._pens = {}
        self._pens['default'] = qg.QPen(qg.QColor(202, 207, 210), 1, qc.Qt.SolidLine)
        self._pens['shadow']  = qg.QPen(qg.QColor(  6,  11,  14), 1, qc.Qt.SolidLine)
        self._pens['border']  = qg.QPen(qg.QColor(  9,  10,  12), 2, qc.Qt.SolidLine)
        
        self._pens['glow']    = qg.QPen(qg.QColor(150, 248, 248),      1, qc.Qt.SolidLine)        
        self._pens['clear']   = qg.QPen(qg.QColor(  0,   0,   0,   0), 1, qc.Qt.SolidLine)
        
        # setup brushes
        #
        self._brushes = {}
        self._brushes['clear'] = qg.QBrush(qg.QColor(0, 0, 0, 0))

        # setup animation
        #
        self._glow_value = 0
        self._anim_timer = None
        
        self._left_curve  = False
        self._right_curve = False
        self._left_down   = False
        self._right_down  = False
        
        self._next     = None
        self._previous = None
        
    #-----------------------------------------------------------------------------------------#
    
    def setText(self, text):
        qg.QPushButton.setText(self, text)
        
        font = self.font()
        font.setPointSize(8)
        font.setFamily("Calibri")
        
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
        
        self.setMinimumWidth(text_width + 30)
        
    #-----------------------------------------------------------------------------------------#
        
    def _animateGlow(self):
        if self._hover is True:
            if self._glow_value < 0.9:
                self._glow_value += 0.1
            else:
                self._glow_value = 1.0
                self._anim_timer.stop()
                self._anim_timer = None
            
        else:
            if self._glow_value > 0.1:
                self._glow_value -= 0.1
            else:
                self._glow_value = 0.0
                self._anim_timer.stop()
                self._anim_timer = None
           
        self.update()
        qg.QApplication.processEvents()
        
    #-----------------------------------------------------------------------------------------#
        
    def enterEvent(self, event):
        self._hover = True
        qg.QPushButton.enterEvent(self, event)
        
        if self._anim_timer:
            return
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(5)


    def leaveEvent(self, event):
        self._hover = False
        qg.QPushButton.leaveEvent(self, event)
        
        if self._anim_timer:
            return
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(14)

    #-----------------------------------------------------------------------------------------#
    
    def mousePressEvent(self, event):
        if self._previous:
            self._previous._right_down = True
            self._previous.update()
        if self._next:
            self._next._left_down = True
            self._next.update()
            
        qg.QPushButton.mousePressEvent(self, event)
        
        
    def mouseReleaseEvent(self, event):
        if self._previous:
            self._previous._right_down = False
            self._previous.update()
        if self._next:
            self._next._left_down = False
            self._next.update()
            
        qg.QPushButton.mouseReleaseEvent(self, event)

    #-----------------------------------------------------------------------------------------#
    
    
    def getSymbolPath(self):
        return None
    
            
        
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1 
        width  = option.rect.width() - 1
        
        painter.setRenderHint(qg.QPainter.Antialiasing)
        
        gradient_key = 'up'
        if self.isDown(): 
            gradient_key = 'down'
        
        painter.setPen(self._pens['clear'])
        painter.setBrush(self._inner_gradient[gradient_key])
        painter.drawRect(qc.QRect(x+1, y+2, width-1, height-2))
        
        painter.setRenderHint(qg.QPainter.Antialiasing, False)

        if self.isDown():
            if self._left_curve is True:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(22, 23, 25))) 
                painter.drawLine(x+2, y, x+15, y)                # dark top line
                painter.drawLine(x+1, y+1, x+15, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(11, 11, 11))) # top line
                painter.drawLine(x+2, y+2, x+15, y+2)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+2, y+height, x+15, y+height)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(11, 11, 11))
                gradient.setColorAt(1, qg.QColor(35, 36, 38))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+1, y+2, 1, 22)
            
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(22, 23, 25))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x, y+2, 1, 22)
                
            else:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(22, 23, 25))) 
                painter.drawLine(x, y, x+15, y)                # dark top line
                painter.drawLine(x, y+1, x+15, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(11, 11, 11))) # top line
                painter.drawLine(x, y+2, x+15, y+2)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x, y+height, x+15, y+height)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(11, 11, 11))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x, y+3, 1, 22)
                
            if self._right_curve is True:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(22, 23, 25))) 
                painter.drawLine(x+15, y, x+width-2, y)       # dark top line
                painter.drawLine(x+15, y+1, x+width-1, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(11, 11, 11))) # top line
                painter.drawLine(x+15, y+2, x+width, y+2)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+15, y+height, x+width-2, y+height)
                painter.drawPoint(x+width-1, y+height-1)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(11, 11, 11))
                gradient.setColorAt(1, qg.QColor(35, 36, 38))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width-1, y+2, 1, 22)
            
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(22, 23, 25))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width, y+2, 1, 22)
                
            else:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(22, 23, 25))) 
                painter.drawLine(x+15, y, x+width, y)                # dark top line
                painter.drawLine(x+15, y+1, x+width, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(11, 11, 11))) # top line
                painter.drawLine(x+15, y+2, x+width, y+2)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+15, y+height, x+width, y+height)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, 3, 0, height-1)
                gradient.setColorAt(0, qg.QColor(11, 11, 11))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width, y+3, 1, 22)
                
        else:
            # LEFT
            #
            if self._left_curve is True:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(38, 39, 41))) # top left
                painter.drawPoint(x+1, y+1)
                painter.drawLine(x+2, y, x+15, y)              # dark top line
                
                painter.setPen(qg.QPen(qg.QColor(64, 68, 71))) # top line
                painter.drawLine(x+2, y+1, x+15, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+2, y+height, x+15, y+height)
                painter.drawPoint(x+1, y+height-1)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, 2, 0, height-2)
                gradient.setColorAt(0, qg.QColor(64, 68, 71))
                gradient.setColorAt(1, qg.QColor(38, 39, 41))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+1, y+2, 1, 22)
                
                gradient = qg.QLinearGradient(0, 2, 0, height-2)
                gradient.setColorAt(0, qg.QColor(38, 39, 41))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x, y+2, 1, 22)
            
            else:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(74, 75, 79))) # top left
                painter.drawPoint(x, y+1)
                painter.setPen(qg.QPen(qg.QColor(30, 31, 33))) # bottom left
                painter.drawPoint(x, y+height)
                 
                painter.setPen(qg.QPen(qg.QColor(38, 39, 41))) # dark top line
                painter.drawLine(x, y, x+15, y)
                
                painter.setPen(qg.QPen(qg.QColor(64, 68, 71))) # top line
                painter.drawLine(x+1, y+1, x+15, y+1)
                
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+1, y+height, x+15, y+height)
                
                painter.setPen(self._pens['clear'])
                if self._left_down:
                    gradient = qg.QLinearGradient(0, 0, 0, self.HEIGHT)
                    gradient.setColorAt(0, qg.QColor(43, 44, 46))
                    gradient.setColorAt(1, qg.QColor(29, 30, 32))
                    painter.setBrush(qg.QBrush(gradient))
                else:
                    gradient = qg.QLinearGradient(0, 0, 0, self.HEIGHT)
                    gradient.setColorAt(0, qg.QColor(62, 63, 67))
                    gradient.setColorAt(1, qg.QColor(38, 39, 41))
                    painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x, y+2, 1, 23)
            
            # RIGHT
            #
            if self._right_curve is True:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(38, 39, 41))) # top right
                painter.drawPoint(x+width-1, y+1)
                painter.drawLine(x+15, y, x+width-2, y)        # dark top line
                 
                painter.setPen(qg.QPen(qg.QColor(64, 68, 71))) # top line
                painter.drawLine(x+15, y+1, x+width-2, y+1)
                 
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+15, y+height, x+width-2, y+height)
                painter.drawPoint(x+width-1, y+height-1)
                
                painter.setPen(self._pens['clear'])             
                gradient = qg.QLinearGradient(0, +2, 0, height-2)
                gradient.setColorAt(0, qg.QColor(64, 68, 71))
                gradient.setColorAt(1, qg.QColor(38, 39, 41))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width-1, y+2, 1, 22)
                
                gradient = qg.QLinearGradient(0, 2, 0, height-2)
                gradient.setColorAt(0, qg.QColor(38, 39, 41))
                gradient.setColorAt(1, qg.QColor(28, 29, 31))
                painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width, y+2, 1, 22)
                 
            else:
                # draw corner points
                #
                painter.setPen(qg.QPen(qg.QColor(59, 60, 64))) # top right
                painter.drawPoint(x+width, y+1)
                painter.setPen(qg.QPen(qg.QColor(26, 27, 29))) # bottom right
                painter.drawPoint(x+width, y+height)
                 
                painter.setPen(qg.QPen(qg.QColor(38, 39, 41))) # dark top line
                painter.drawLine(x+15, y, x+width, y)
                 
                painter.setPen(qg.QPen(qg.QColor(64, 68, 71))) # top line
                painter.drawLine(x+15, y+1, x+width-1, y+1)
                 
                painter.setPen(qg.QPen(qg.QColor(28, 29, 31))) # bottom line
                painter.drawLine(x+15, y+height, x+width-1, y+height)
    
                painter.setPen(self._pens['clear'])
                if self._left_down:
                    gradient = qg.QLinearGradient(0, 2, 0, height-1)
                    gradient.setColorAt(0, qg.QColor(50, 51, 53))
                    gradient.setColorAt(1, qg.QColor(31, 32, 34))
                    painter.setBrush(qg.QBrush(gradient))
                else:
                    gradient = qg.QLinearGradient(0, 2, 0, height-1)
                    gradient.setColorAt(0, qg.QColor(45, 46, 50))
                    gradient.setColorAt(1, qg.QColor(29, 30, 32))
                    painter.setBrush(qg.QBrush(gradient))
                painter.drawRect(x+width, y+2, 1, 23)


        
        symbol_path = self.getSymbolPath()
        if not isinstance(symbol_path, qg.QPainterPath):
            return
        
        painter.setRenderHint(qg.QPainter.Antialiasing, True)
        
        painter.setBrush(self._brushes['clear'])        
        painter.setPen(self._pens['shadow'])        
        
        #painter.setPen(qg.QPen(qg.QColor(3, 7, 10), 2))
        painter.drawPath(symbol_path)

        #painter.setRenderHint(qg.QPainter.Antialiasing, False)
        painter.setPen(qg.QPen(qg.QColor(131, 140, 145), 1))
        painter.drawPath(symbol_path)
        
        painter.setBrush(self._brushes['clear'])
         
#         painter.setPen(self._pens['shadow'])        
#         painter.drawPath(symbol_path)
#         
#         painter.setRenderHint(qg.QPainter.Antialiasing, False)
#         painter.setPen(self._pens['default'])
#         painter.drawPath(symbol_path)
                  
        if self._hover or self._glow_value > 0.0:
            painter.setRenderHint(qg.QPainter.Antialiasing, True)
            
            glow_1 = qg.QPen(qg.QColor(150, 248, 248, 120 * self._glow_value), 1, qc.Qt.SolidLine)
            glow_2 = qg.QPen(qg.QColor(150, 248, 248,  50 * self._glow_value), 3, qc.Qt.SolidLine)
            glow_3 = qg.QPen(qg.QColor(150, 248, 248,  20 * self._glow_value), 5, qc.Qt.SolidLine)
 
            painter.setPen(glow_3)
            painter.drawPath(symbol_path)
 
            painter.setPen(glow_2)
            painter.drawPath(symbol_path)
 
            painter.setPen(glow_1)
            painter.drawPath(symbol_path)

            painter.setRenderHint(qg.QPainter.Antialiasing, False)
            painter.setPen(self._pens['glow'])
            painter.drawPath(symbol_path)           
            
            

class TSaveMenuItem(TMenuItem):
    def getSymbolPath(self):
        path = qg.QPainterPath()

        offset = 0
        if self.isDown():
            offset = 1

        path.moveTo( 6,  7 + offset)
        path.lineTo( 6, 18 + offset)
        path.lineTo( 8, 20 + offset)
        path.lineTo(19, 20 + offset)
        path.lineTo(20, 19 + offset)
        path.lineTo(20,  7 + offset)
        path.lineTo(19,  6 + offset)
        path.lineTo( 7,  6 + offset)
        
        path.moveTo( 8,  6 + offset)
        path.lineTo( 8, 12 + offset)
        path.moveTo( 9, 13 + offset)
        path.lineTo(17, 13 + offset)
        path.moveTo(18, 12 + offset)
        path.lineTo(18,  6 + offset)
        
        path.moveTo(10, 20 + offset)
        path.lineTo(10, 17 + offset)
        path.moveTo(11, 16 + offset)
        path.lineTo(15, 16 + offset)
        path.moveTo(16, 17 + offset)
        path.lineTo(16, 20 + offset)
        
        return path