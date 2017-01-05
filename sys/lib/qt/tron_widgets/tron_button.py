import PyQt4.QtCore as qc
import PyQt4.QtGui as qg



class TButton(qg.QPushButton):    
    HEIGHT = 27
    
    #-----------------------------------------------------------------------------------------#    
    
    def __init__(self, *args, **kwargs):
        qg.QPushButton.__init__(self)
        if args and isinstance(args[0], (str, unicode, qc.QString)):
            self.setText(args[0])
        
        self.setFixedHeight(self.HEIGHT)
        
        self._hover = False
        
        # setup paint gradients
        #        
        self._inner_gradient = {}
        self._outer_gradient = {}
        
        inner_gradient = qg.QLinearGradient(0, 3, 0, self.HEIGHT - 3)
        inner_gradient.setColorAt(0, qg.QColor(53, 57, 60))
        inner_gradient.setColorAt(1, qg.QColor(33, 34, 36))
        self._inner_gradient['up'] = qg.QBrush(inner_gradient)          

        outer_gradient = qg.QLinearGradient(0, 2, 0, self.HEIGHT - 2)
        outer_gradient.setColorAt(0, qg.QColor(67, 68, 70))
        outer_gradient.setColorAt(1, qg.QColor(17, 18, 20))
        self._outer_gradient['up'] = qg.QBrush(outer_gradient)
        
        inner_gradient_down = qg.QLinearGradient(0, 3, 0, self.HEIGHT - 3)
        inner_gradient_down.setColorAt(0, qg.QColor(20, 21, 23))
        inner_gradient_down.setColorAt(1, qg.QColor(48, 49, 51))
        self._inner_gradient['down'] = qg.QBrush(inner_gradient_down)
        
        outer_gradient_down = qg.QLinearGradient(0, 2, 0, self.HEIGHT - 2)
        outer_gradient_down.setColorAt(0, qg.QColor(36, 36, 40))
        outer_gradient_down.setColorAt(1, qg.QColor(30, 30, 34))
        self._outer_gradient['down'] = qg.QBrush(outer_gradient_down)
            
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
        
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1
        
        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)
     
        gradient_key = 'up'
        offset = 0
        if self.isDown(): 
            gradient_key = 'down'
            offset = 1
            
        painter.setPen(self._pens['clear'])
        
        painter.setBrush(self._outer_gradient[gradient_key])        
        painter.drawRoundedRect(qc.QRect(x+2, y+2, width-3, height-3), 5, 5)
        
        painter.setBrush(self._inner_gradient[gradient_key])
        painter.drawRoundedRect(qc.QRect(x+3, y+3, width-5, height-5), 4, 4)
        
        painter.setBrush(self._brushes['clear'])
        
        painter.setPen(self._pens['border'])
        painter.drawRoundedRect(qc.QRect(x+1, y+1, width-1, height-1), 5, 5)
 
        font = painter.font()
        font.setPointSize(8)
        font.setFamily("Calibri")
        painter.setFont(font)
         
        text = self.text()
         
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
        
        text_path = qg.QPainterPath()
        text_path.addText(((width+1)/2) - (text_width / 2), (height/2) + 3 + offset, font, text)
        
        painter.setPen(self._pens['shadow'])        
        painter.drawPath(text_path)    
                 
        if self._hover or self._glow_value > 0.0:
            glow_3 = qg.QPen(qg.QColor(150, 248, 248, 120 * self._glow_value), 1, qc.Qt.SolidLine)
            glow_2 = qg.QPen(qg.QColor(150, 248, 248,  50 * self._glow_value), 3, qc.Qt.SolidLine)
            glow_1 = qg.QPen(qg.QColor(150, 248, 248,  20 * self._glow_value), 5, qc.Qt.SolidLine)

            painter.setPen(glow_3)
            painter.drawPath(text_path)

            painter.setPen(glow_2)
            painter.drawPath(text_path)

            painter.setPen(glow_1)
            painter.drawPath(text_path)

            painter.setPen(self._pens['glow'])            
                               
        else:
            painter.setPen(self._pens['default'])
         
        painter.drawText(x, y+offset, width, height, (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter), text)

#--------------------------------------------------------------------------------------------------#

class TButtonThin(qg.QPushButton):    
    HEIGHT = 22
    
    #-----------------------------------------------------------------------------------------#    
    
    def __init__(self, *args, **kwargs):
        qg.QPushButton.__init__(self)
        if isinstance(args[0], (str, unicode, qc.QString)):
            self.setText(args[0])
        
        self.setFixedHeight(self.HEIGHT)
        
        self._hover = False
        
        # setup paint gradients
        #        
        self._inner_gradient = {}
        self._outer_gradient = {}
        
        inner_gradient = qg.QLinearGradient(0, 3, 0, self.HEIGHT - 3)
        inner_gradient.setColorAt(0, qg.QColor(53, 57, 60))
        inner_gradient.setColorAt(1, qg.QColor(33, 34, 36))
        self._inner_gradient['up'] = qg.QBrush(inner_gradient)          

        outer_gradient = qg.QLinearGradient(0, 2, 0, self.HEIGHT - 2)
        outer_gradient.setColorAt(0, qg.QColor(67, 68, 70))
        outer_gradient.setColorAt(1, qg.QColor(17, 18, 20))
        self._outer_gradient['up'] = qg.QBrush(outer_gradient)
        
        inner_gradient_down = qg.QLinearGradient(0, 3, 0, self.HEIGHT - 3)
        inner_gradient_down.setColorAt(0, qg.QColor(20, 21, 23))
        inner_gradient_down.setColorAt(1, qg.QColor(48, 49, 51)) 
        self._inner_gradient['down'] = qg.QBrush(inner_gradient_down)
        
        outer_gradient_down = qg.QLinearGradient(0, 2, 0, self.HEIGHT - 2)
        outer_gradient_down.setColorAt(0, qg.QColor(36, 36, 40))
        outer_gradient_down.setColorAt(1, qg.QColor(35, 35, 37))
        self._outer_gradient['down'] = qg.QBrush(outer_gradient_down)
            
        # setup pens
        #
        self._pens = {}
        self._pens['default'] = qg.QPen(qg.QColor(202, 207, 210), 1, qc.Qt.SolidLine)
        self._pens['shadow']  = qg.QPen(qg.QColor(  6,  11,  14), 2, qc.Qt.SolidLine)
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
            self._anim_timer.stop()
            self._anim_timer = None
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(5)


    def leaveEvent(self, event):
        self._hover = False
        qg.QPushButton.leaveEvent(self, event)
        
        if self._anim_timer:
            self._anim_timer.stop()
            self._anim_timer = None
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(14)

    #-----------------------------------------------------------------------------------------#            
        
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1
        
        painter.setRenderHint(qg.QPainter.Antialiasing)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)
        
        gradient_key = 'up'
        offset = 0
        if self.isDown(): 
            gradient_key = 'down'
            offset = 1
            
        painter.setPen(self._pens['clear'])
        
        painter.setBrush(self._outer_gradient[gradient_key])
        painter.drawRoundedRect(qc.QRect(x+2, y+2, width-2, height-2), 10, 10)
        
        painter.setBrush(self._inner_gradient[gradient_key])
        painter.drawRoundedRect(qc.QRect(x+3, y+3, width-5, height-5), 9, 9)
        
        painter.setBrush(self._brushes['clear'])

        painter.setPen(self._pens['border'])
        painter.drawRoundedRect(qc.QRect(x+1, y+1, width-1, height-1), 10, 10)
 
        font = painter.font()
        font.setPointSize(8)
        font.setFamily("Calibri")
        painter.setFont(font)
         
        text = self.text()
         
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
        
        text_path = qg.QPainterPath()
        text_path.addText(((width+3)/2) - (text_width / 2) - 1, (height/2) + 4+offset, font, text)
        
        painter.setPen(self._pens['shadow'])        
        painter.drawPath(text_path)
                 
        if self._hover or self._glow_value > 0.0:
            glow_1 = qg.QPen(qg.QColor(150, 248, 248, 120 * self._glow_value), 1, qc.Qt.SolidLine)
            glow_2 = qg.QPen(qg.QColor(150, 248, 248,  50 * self._glow_value), 3, qc.Qt.SolidLine)
            glow_3 = qg.QPen(qg.QColor(150, 248, 248,  20 * self._glow_value), 5, qc.Qt.SolidLine)

            painter.setPen(glow_3)
            painter.drawPath(text_path)

            painter.setPen(glow_2)
            painter.drawPath(text_path)

            painter.setPen(glow_1)
            painter.drawPath(text_path)

            painter.setPen(self._pens['glow'])            
                               
        else:
            painter.setPen(self._pens['default'])
         
        painter.drawText(x, y+offset, width, height, (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter), text)
