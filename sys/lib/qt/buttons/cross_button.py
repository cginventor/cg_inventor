import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import cg_inventor.sys.lib.qt.base as base


EXPAND   = 'expand'
COLLAPSE = 'collapse'


class CrossButton(qg.QPushButton, base.Base):
    _draw   = True
    _toggle = True
      
    def __init__(self):
        qg.QPushButton.__init__(self)
        
        font = qg.QFont()
        font.setBold(True)
        self.setFont(font)
        self.setMinimumHeight(11)
        self.setFixedWidth(12)
        self.setSizePolicy(qg.QSizePolicy.Fixed, qg.QSizePolicy.Expanding) 
    
    #-----------------------------------------------------------------------------------------#
    
    def setExpanded(self, expanded):
        expanded = bool(expanded)
        
        self._toggle = expanded
        if self._toggle is True:
            self.emit(qc.SIGNAL(EXPAND))
        else:
            self.emit(qc.SIGNAL(COLLAPSE))
        self.repaint()
    
    #-----------------------------------------------------------------------------------------#    
    
    def setDraw(self, draw):
        draw = bool(draw)
        
        if draw:
            self._draw = True
        else:
            self._draw = False
        self.repaint()
    
    
    def paintEvent(self, pEvent):
        if not self._draw:
            return
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)
        self._drawButton(option, painter)  

        
    def _drawButton(self, option, painter):       
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width()  - 1
    
        oldPen = painter.pen()
        painter.setPen(option.palette.text().color())
        
        off_x = 1
        off_y = ((height - 11) / 2) + 2
        size  = 10

        painter.setPen(option.palette.mid().color())
        painter.drawLine(x       , y + off_y       , x + size, y + off_y)
        painter.drawLine(x + size, y + off_y       , x + size, y + off_y + size)
        painter.drawLine(x + size, y + off_y + size, x       , y + off_y + size)
        painter.drawLine(x       , y + off_y + size, x       , y + off_y)

        painter.drawLine(x + 2, y + off_y + (size/2), x + size - 2, y + off_y + (size/2))
        if not self._toggle:
            painter.drawLine(x + (size/2), y + off_y + 2, x + (size/2), y + off_y + size - 2)

        off_x = 0
        off_y -= 1
        painter.setPen(option.palette.text().color())
        painter.drawLine(x + off_x, y + off_y, x + off_x + size, y + off_y)
        painter.drawLine(x + off_x + size, y + off_y, x + off_x + size, y + off_y + size)
        painter.drawLine(x + off_x + size, y + off_y + size, x + off_x, y + off_y + size)
        painter.drawLine(x + off_x, y + off_y + size, x + off_x, y + off_y)

        painter.drawLine(x + off_x + 2, y + off_y + (size/2), x + off_x + size - 2, y + off_y + (size/2))
        if not self._toggle:
            painter.drawLine(x + off_x + (size/2), y + off_y + 2, x + off_x + (size/2), y + off_y + size - 2)
    
        painter.setPen(oldPen)

    #-----------------------------------------------------------------------------------------#
    
    def mouseReleaseEvent(self, event):
        if event.button() == qc.Qt.LeftButton:
            qg.QPushButton.mouseReleaseEvent(self, event)
            if self._toggle is True:
                self.setExpanded(False)
            else:
                self.setExpanded(True) 
