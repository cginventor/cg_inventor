import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import cg_inventor.sys.lib.qt.misc.status_light as status_light
import time

# ------------------------------------------------------------------------------------------------ #

class LightButtonError(Exception):
    pass

# ------------------------------------------------------------------------------------------------ #
#                                       LIGHT BUTTON                                               #
# ------------------------------------------------------------------------------------------------ #

class StatusLightButton(qg.QPushButton, status_light.StatusLight):
    DEFAULT = 'default'    
    
    def __init__(self, radius=5):
        qg.QPushButton.__init__(self)
        self._default_width  = 26
        self._default_height = 26
        self.setFixedWidth(self._default_width)
        self.setFixedHeight(self._default_height)
               
        self._colour       = qg.QColor()
        self._hover_colour = qg.QColor()
        self._base_colour = qg.QColor()
        
        self._hover          = False
        self._animate        = False
        self._status         = None
        self._clicked_status = None 
        
        self._radius = radius
        self._circ   = radius * 2
        
        self._clicked_status = None
        self._preclicked_status = self.DEFAULT
        
        self._status_colours = {}
        self._status_colours[self.DEFAULT] = (180, 180, 180)
        self.setStatus(self.DEFAULT)
        
        # turn animation on by default
        #
        self._animate = True
        
        self.clicked.connect(self._clickedStatus)
        
    # ---------------------------------------------------------------------------------------- #
    
    def setClickedStatus(self, status=None):
        '''
            Sets and emits the desired status when button is clicked.
        '''
        if status is None:
            self._clicked_status = None 
        
        if status not in self._status_colours.keys():
            raise LightButtonError("Status type '%s' not recognised." %status)
        
        self._clicked_status = status
        
    
    def _clickedStatus(self):
        if self._clicked_status is None: return
        
        if self._status == self._clicked_status:
            self.setStatus(self._preclicked_status)
        else:
            self._preclicked_status = self._status
            self.setStatus(self._clicked_status)
            self.emit(qc.SIGNAL(self._clicked_status))

    
    # ---------------------------------------------------------------------------------------- #

#    def setStatus(self, status=None):
#        if status is None:
#            status = self.DEFAULT
#            
#        if status not in self._status_colours.keys():
#            raise LightButtonError("Status type '%s' not recognised." %status)
#
#        status_colour = self._status_colours[status]
#
#        self._colour.setRgb(*status_colour)
#        self._hover_colour.setRgb(min((status_colour[0] + 30), 255),
#                                  min((status_colour[1] + 30), 255),
#                                  min((status_colour[2] + 30), 255))

#        if status == self.IGNORE:
#            self.color.setRgb(255,255,0)
#            self.hover_color.setRgb(255,255,40)
#            self.ignore = True
#        else:
#            if status == self.OFF:
#                self.color.setRgb(180,180,180)
#                self.hover_color.setRgb(220,220,220)
#            elif status == self.SUCCESS:
#                self.color.setRgb(0,255,0)
#                self.hover_color.setRgb(40,255,40)
#            elif status == self.FAILURE:
#                self.color.setRgb(255,0,0)
#                self.hover_color.setRgb(255,40,40)
#            self.ignore = False
        
#        self._status = status
#        self.emit(qc.SIGNAL(self._status))
        
    # ---------------------------------------------------------------------------------------- #
        
    def enterEvent(self, event):
        self._hover = True
        qg.QPushButton.enterEvent(self, event)        


    def leaveEvent(self, event):
        self._hover = False
        qg.QPushButton.leaveEvent(self, event)

    # ---------------------------------------------------------------------------------------- #
    
    def paintEvent(self, pEvent):
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        x = option.rect.x()
        y = option.rect.y()
        height = option.rect.height() - 1
        width  = option.rect.width() - 1
        
        offset = 0
        if self.isDown():
            offset = 1
            
        old_pen = painter.pen()
                
        if not self.isEnabled():
            painter.setOpacity(0.3)
            
        if self.isDown() and self._hover:
            painter.fillRect(qc.QRectF(x+1, y+1, width-2, height-2),qg.QColor(89, 89, 89))
            painter.setPen(qg.QColor(51, 51, 51))
            painter.drawRoundedRect(qc.QRectF(x, y ,width-1, height-1), 2, 2)
            painter.setPen(qg.QColor(41, 41, 41))
            painter.drawRoundedRect(qc.QRectF(x, y, width-1, height-1), 3, 3)
            painter.setPen(qg.QColor(93, 93, 93))
            painter.drawRoundedRect(qc.QRectF(x+1, y+1, width-3, height-3), 2, 2)

        colour = self._colour
        base_colour = self._base_colour
        if self._hover:
            colour = qg.QColor(min((colour.red() + 30), 255),
                                min((colour.green() + 30), 255),
                                min((colour.blue() + 30), 255))
            base_colour = qg.QColor(min((base_colour.red() + 30), 255),
                                     min((base_colour.green() + 30), 255),
                                     min((base_colour.blue() + 30), 255))
            
        # calculate light size
        #
        radius = self._radius
        circ   = self._circ
        half_height = (height / 2)
        half_width  = (width / 2)
        x_offset = half_height - radius
        y_offset = half_width  - radius
                    
        # draw shadow
        #
        shadow_colour = qg.QColor(0, 0, 0, 100)
        brush = qg.QBrush(shadow_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(shadow_colour)
        painter.drawEllipse(x_offset+1, y_offset+1, circ, circ)
        
        # draw base colour
        #
        brush = qg.QBrush(base_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(base_colour)
        painter.drawEllipse(x_offset, y_offset, circ, circ)
        
        # draw main colour
        #
        main_radius = radius - 2
        main_circ   = main_radius * 2
        main_x_offset = half_height - main_radius - 1
        main_y_offset = half_width  - main_radius - 1
        brush = qg.QBrush(qg.QBrush(colour, qc.Qt.SolidPattern))
        painter.setBrush(brush)
        painter.setPen(colour)
        painter.drawEllipse(main_x_offset, main_y_offset, main_circ, main_circ)
         
        # draw hilight
        #
        hi_radius = 1
        hi_circ   = hi_radius * 2
        hi_x_offset = half_height - hi_radius - (radius / 3)
        hi_y_offset = half_width  - hi_radius - (radius / 3)
        hi_colour = qg.QColor(255,255,255)
        brush = qg.QBrush(hi_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(hi_colour)
        painter.drawEllipse(hi_x_offset, hi_y_offset, hi_circ, hi_circ)
        
        # draw outline
        #
        brush = qg.QBrush(qg.QColor(0,0,0,0), qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(qg.QColor(0,0,0))
        painter.drawEllipse(x_offset, y_offset, circ, circ)
    
        # reset pen
        painter.setPen(old_pen)           
    
        # reset pen
        painter.setPen(old_pen)