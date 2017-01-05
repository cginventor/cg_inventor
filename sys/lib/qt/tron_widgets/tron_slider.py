import PyQt4.QtCore as qc
import PyQt4.QtGui as qg



class TSlider(qg.QSlider):   
    def __init__(self, *args, **kwargs):
        qg.QSlider.__init__(self)
#         if isinstance(args[0], (str, unicode, qc.QString)):
#             self.setText(args[0])
#
        # setup paint gradients
        #        
        self._inner_gradient = {}
        self._outer_gradient = {}
        
        inner_gradient_down = qg.QLinearGradient()
        inner_gradient_down.setColorAt(0, qg.QColor(67, 68, 70))
        inner_gradient_down.setColorAt(1, qg.QColor(17, 18, 20))
        self._inner_gradient['up'] = inner_gradient_down        

        outer_gradient_down = qg.QLinearGradient()
        outer_gradient_down.setColorAt(0, qg.QColor(53, 57, 60))
        outer_gradient_down.setColorAt(1, qg.QColor(33, 34, 36))
        self._outer_gradient['up'] = outer_gradient_down
        
        # setup pens
        #
        self._pens = {}
        self._pens['default']     = qg.QPen(qg.QColor(202, 207, 210), 1, qc.Qt.SolidLine)
        self._pens['background']  = qg.QPen(qg.QColor(  6,  11,  14), 1, qc.Qt.SolidLine)
        self._pens['border']      = qg.QPen(qg.QColor(  9,  10,  12), 2, qc.Qt.SolidLine)
        
        self._pens['glow']  = qg.QPen(qg.QColor(150, 248, 248),      1, qc.Qt.SolidLine)        
        self._pens['clear'] = qg.QPen(qg.QColor(  0,   0,   0,   0), 1, qc.Qt.SolidLine)
        
        # setup brushes
        #
        self._brushes = {}
        self._brushes['clear']      = qg.QBrush(qg.QColor(0, 0, 0, 0))
        self._brushes['background'] = qg.QBrush(qg.QColor(6, 11, 14))         

        self._hover = False

        self._glow_value = 0
        self._follow_points = {}
        self._anim_timer = None
        self._anim_follow_timer = None
        
        self.setOrientation(qc.Qt.Horizontal)
        
        self.valueChanged.connect(self._trackChanges)
        
        
    def setOrientation(self, orientation):
        if orientation == qc.Qt.Horizontal:
            self.setFixedHeight(22)
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(50)
        else:
            self.setFixedWidth(22)
            self.setMaximumHeight(16777215)
            self.setMinimumHeight(50)
        qg.QSlider.setOrientation(self, orientation)
        
        
    #-----------------------------------------------------------------------------------------#
                
    def _animateGlow(self):
        if self._hover:
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

    def mouseMoveEvent(self, event):
        qg.QSlider.mouseMoveEvent(self, event)
        
        if not self._anim_follow_timer:
            self._anim_follow_timer = qc.QTimer()
            self._anim_follow_timer.timeout.connect(self._removeFollowPoints)        
            self._anim_follow_timer.start(30) 
        
        
    def enterEvent(self, event):
        self._hover = True
        qg.QSlider.enterEvent(self, event)
        
        if self._anim_timer:
            self._anim_timer.stop()
            self._anim_timer = None
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(15)


    def leaveEvent(self, event):
        self._hover = False
        qg.QSlider.leaveEvent(self, event)
        
        if self._anim_timer:
            self._anim_timer.stop()
            self._anim_timer = None
        
        self._anim_timer = qc.QTimer()
        self._anim_timer.timeout.connect(self._animateGlow)        
        self._anim_timer.start(30)

        
    def paintEvent(self, event):
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
     
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1
        
        value = self.value()
        orientation = self.orientation()
        
        painter.setRenderHint(qg.QPainter.Antialiasing, True)
        painter.setRenderHint(qg.QPainter.TextAntialiasing)
        painter.begin(self)
        
        painter.setPen(self._pens['background'])
        painter.setBrush(self._brushes['background'])        
        painter.drawRoundedRect(qc.QRect(x+1, y+1, width-1, height-1), 10, 10)
        
        if orientation == qc.Qt.Vertical:
            dark_pen = qg.QPen(qg.QColor( 0,  5,  9), 1, qc.Qt.SolidLine)
            painter.setPen(dark_pen)
            
            mid_width = (width / 2) + 1
            painter.drawLine(mid_width, 10, mid_width, height - 10)
            
            center = height - 10 - ((height - 20) / 100.0) * value            

            painter.setPen(self._pens['clear'])
            self._outer_gradient['up'].setStart(0, center - 3)
            self._outer_gradient['up'].setFinalStop(0, center + 3)
            painter.setBrush(qg.QBrush(self._outer_gradient['up']))        
            painter.drawEllipse(qc.QPoint(x + mid_width, center), 6, 6)
            
            self._inner_gradient['up'].setStart(0, center - 3)
            self._inner_gradient['up'].setFinalStop(0, center + 3)
            painter.setBrush(qg.QBrush(self._inner_gradient['up']))         
            painter.drawEllipse(qc.QPoint(x + mid_width, center), 5, 5)
            
            if self.isSliderDown():
                painter.setPen(self._pens['clear'])
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 10)))        
                painter.drawEllipse(qc.QPoint(x + mid_width, center), 10, 10)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 40)))        
                painter.drawEllipse(qc.QPoint(x + mid_width, center), 8, 8)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 100)))        
                painter.drawEllipse(qc.QPoint(x + mid_width, center), 7, 7)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248)))        
                painter.drawEllipse(qc.QPoint(x + mid_width, center), 6, 6)
            
        else:            
            mid_height = (height / 2) + 1
            dark_pen = qg.QPen(qg.QColor( 0,  5,  9), 1, qc.Qt.SolidLine)
            painter.setPen(dark_pen)
            painter.drawLine(10, mid_height, width - 8, mid_height)
            
            painter.setRenderHint(qg.QPainter.Antialiasing, False)
            light_pen = qg.QPen(qg.QColor(16, 17, 19), 1, qc.Qt.SolidLine)
            painter.setPen(light_pen)
            painter.drawLine(10, mid_height, width - 8, mid_height)           
            painter.setRenderHint(qg.QPainter.Antialiasing, True)
            
            painter.setPen(self._pens['clear'])        
        
            increment = ((width - 20) / 100.0)
            
            num_points = len(self._follow_points)
            if num_points > 0:
                for follow_value, time in self._follow_points.items():
                    center =  10 + (increment * follow_value)                  
                    painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 150 * time)))        
                    painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 6, 6)
                    
            center = 10 + (increment * value)
            
            if self._hover or self._glow_value > 0.0:
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 10 * self._glow_value)))        
                painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 10, 10)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 30 * self._glow_value)))        
                painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 9, 9)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 80 * self._glow_value)))        
                painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 8, 8)
                
                painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 255 * self._glow_value)))        
                painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 7, 7)
                

            self._outer_gradient['up'].setStart(0, mid_height - 3)
            self._outer_gradient['up'].setFinalStop(0, mid_height + 3)
            painter.setBrush(qg.QBrush(self._outer_gradient['up']))        
            painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 6, 6)
            
            self._inner_gradient['up'].setStart(0, mid_height - 3)
            self._inner_gradient['up'].setFinalStop(0, mid_height + 3)
            painter.setBrush(qg.QBrush(self._inner_gradient['up']))         
            painter.drawEllipse(qc.QPoint(x + center, y + mid_height), 5, 5)
            

                
            
#             if self.isSliderDown() or self._glow_value > 0.0:
#                 painter.setPen(self._pens['clear'])
#                 painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 10 * self._glow_value)))        
#                 painter.drawEllipse(qc.QPoint(center, y + 1 + (height/2)), 10, 10)
#                 
#                 painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 40 * self._glow_value)))        
#                 painter.drawEllipse(qc.QPoint(center, y + 1 + (height/2)), 8, 8)
#                 
#                 painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 100 * self._glow_value)))        
#                 painter.drawEllipse(qc.QPoint(center, y + 1 + (height/2)), 7, 7)
#                 
#                 painter.setBrush(qg.QBrush(qg.QColor(150, 248, 248, 255 * self._glow_value)))        
#                 painter.drawEllipse(qc.QPoint(center, y + 1 + (height/2)), 6, 6)
            
        
    def _trackChanges(self, value):
        self._follow_points[value] = 1.0
        
        
    def _removeFollowPoints(self):
        if not self.isSliderDown() and not len(self._follow_points):
            self._anim_follow_timer.stop()
            self._anim_follow_timer = None
        
        for value, time in self._follow_points.items():
            self._follow_points[value] -= 0.1
            if self._follow_points[value] <= 0.0:
                del(self._follow_points[value])
                
        self.update()
        qg.QApplication.processEvents()
        
            
            
        
        

        
        
        
        