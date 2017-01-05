import PyQt4.QtCore as qc
import PyQt4.QtGui as qg



class TLabel(qg.QLabel):
    DEFAULT_COLOUR = (203, 244, 248)
    
    def __init__(self, *args, **kwargs):
        qg.QLabel.__init__(self, *args, **kwargs)
        
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
        
        self._glow_value = 0
        
    
    
    def setGlowValue(self, value):        
        self._glow_value = min(max(value / 100.0, 0), 1)
        self.update()
        
        
        
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
        painter.begin(self)
         
        font = painter.font()
        font.setPointSize(8)
        font.setFamily("Calibri")
        painter.setFont(font)
         
        text = self.text()
        if text == '':
            painter.end()
            return
         
        font_metrics = qg.QFontMetrics(font)
        text_width = font_metrics.width(text)
         
        painter.setPen(self._pens['shadow'])        
        painter.drawText(x, y, width, height, (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter), text)
        
        painter.setPen(self._pens['default'])          
        painter.drawText(x, y, width, height, (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter), text)
                  
        if self._glow_value > 0.0:            
            text_path = qg.QPainterPath()
            text_path.addText(((width+3)/2) - (text_width / 2) - 1, (height/2) + 4, font, text)
            
            glow   = qg.QPen(qg.QColor(150, 248, 248, 255 * self._glow_value), 1, qc.Qt.SolidLine)      
            glow_1 = qg.QPen(qg.QColor(150, 248, 248, 120 * self._glow_value), 1, qc.Qt.SolidLine)
            glow_2 = qg.QPen(qg.QColor(150, 248, 248,  50 * self._glow_value), 3, qc.Qt.SolidLine)
            glow_3 = qg.QPen(qg.QColor(150, 248, 248,  20 * self._glow_value), 5, qc.Qt.SolidLine)            
  
            painter.setPen(glow_3)
            painter.drawPath(text_path)
  
            painter.setPen(glow_2)
            painter.drawPath(text_path)
  
            painter.setPen(glow_1)
            painter.drawPath(text_path)
  
            painter.setPen(glow)
            painter.drawText(x, y, width, height, (qc.Qt.AlignHCenter | qc.Qt.AlignVCenter), text)            
                 
        painter.end()