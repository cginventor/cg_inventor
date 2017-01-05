import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import os

import cg_inventor.sys.lib.qt.base as base
import cg_inventor.sys.utils.qt    as util_qt

#--------------------------------------------------------------------------------------------------#

class IconButton(qg.QPushButton, base.Base):
    _hover = False
    _draw  = True
       
    def __init__(self, image=None):
        qg.QPushButton.__init__(self)
        self.setFixedWidth(75)
        self.setFixedHeight(26)        
        
        self._icon_width    = 26
        self._icon_height   = 26       
        self._icon_offset_x = 0
        self._icon_offset_y = 0
        
        self.setImage(image)

    #-----------------------------------------------------------------------------------------#
    
    def setText(self, image):
        if image is None:
            self._pixmap_normal = None
            self._pixmap_bright = None
            return
            
        self._pixmap_normal = qg.QPixmap(image)
        self.setIcon(qg.QIcon(self._pixmap_normal))
        
        icon_size = self.icon().actualSize(qc.QSize(40,40))
        self._icon_width  = icon_size.width()
        self._icon_height = icon_size.height()
        
        button_size = self.size()
        button_width  = button_size.width()
        button_height = button_size.height()        
        
        self._icon_offset_x = (button_width - self._icon_width) / 2
        self._icon_offset_y = (button_height - self._icon_height) / 2
        
        image = self._pixmap_normal.toImage()
        image = util_qt.changeGamma(image, 120)
        image = util_qt.changeBrightness(image, 10)
        self._pixmap_bright = qg.QPixmap().fromImage(image)        
    
    #-----------------------------------------------------------------------------------------#        
        
    def enterEvent(self, event):
        self._hover = True
        qg.QPushButton.enterEvent(self, event)        


    def leaveEvent(self, event):
        self._hover = False
        qg.QPushButton.leaveEvent(self, event)
        
    #-----------------------------------------------------------------------------------------#
    
    def paintEvent(self, pEvent):        
        painter = qg.QStylePainter(self)
        option  = qg.QStyleOption()
        option.initFrom(self)
        
        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height()
        width  = option.rect.width()

        if not self.isEnabled():
            painter.setOpacity(0.3)
            
        if self.isDown() and self._hover:
            painter.fillRect(qc.QRectF(x+1,y+1,width-2,height-2),qg.QColor(89,89,89))
            painter.setPen(qg.QColor(51,51,51))
            painter.drawRoundedRect(qc.QRectF(x,y,width-1,height-1),2,2)
            painter.setPen(qg.QColor(41,41,41))
            painter.drawRoundedRect(qc.QRectF(x,y,width-1,height-1),3,3)
            painter.setPen(qg.QColor(93,93,93))
            painter.drawRoundedRect(qc.QRectF(x+1,y+1,width-3,height-3),2,2)
        
        if self._pixmap_normal:
            target = qc.QRectF(x + self._icon_offset_x, y + self._icon_offset_y, self._icon_width, self._icon_height)
            source = qc.QRectF(0, 0, self._icon_width, self._icon_height)
            
            if self._hover or self.isDown():
                painter.drawPixmap(target, self._pixmap_bright, source)
            else:
                painter.drawPixmap(target, self._pixmap_normal, source)
            

