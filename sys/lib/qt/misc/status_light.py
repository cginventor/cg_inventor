import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

import math, time

import cg_inventor.sys.lib.qt.base as base

# ------------------------------------------------------------------------------------------------ #

class StatusLightError(Exception):
    pass

# ------------------------------------------------------------------------------------------------ #
#                                        STATUS LIGHT                                              #
# ------------------------------------------------------------------------------------------------ #

class StatusLight(qg.QWidget, base.Base):
    DEFAULT = 'default'
    
    ANIM_TIMER = 'timer'
    ANIM_LOCK  = 'lock'
    
    def __init__(self):
        qg.QWidget.__init__(self)
        self._default_width  = 26
        self._default_height = 26
        self.setFixedWidth(self._default_width)
        self.setFixedHeight(self._default_height)
               
        self._colour      = qg.QColor()
        self._base_colour = qg.QColor()
        self._status  = None
        self._radius  = 5
        self._animate = False
        
        self._clicked_status = None
        
        self._status_colours = {}
        self._status_colours[self.DEFAULT] = (180, 180, 180)
        self.setStatus(self.DEFAULT)
        
        self._animate = True
        self._anim_timer = None
        self._anim_increment = 0
        self._anim_colours      = []
        self._anim_base_colours = []
        
    # ---------------------------------------------------------------------------------------- #

    def setRadius(self, radius):
        max_radius = min(self._default_height, self._default_width)
        max_radius = (max_radius - 5) / 2
        
        if radius > max_radius: radius = max_radius        
            
        self._radius = radius
        self._circ   = radius * 2
        
    # ---------------------------------------------------------------------------------------- #
    
    def setDefaultStatusColour(self, default_colour):
        self.addColour(self.DEFAULT, default_colour)
        
    
    def addStatusColour(self, colour_name, colour):
        colour_err = "Colours must be a list or tuple or 3 rgb integers (0-255)."
        if not isinstance(colour, (list, tuple)) or len(colour) != 3:
            raise StatusLightError(colour_err) 
        
        colour = list(colour)       
        
        # check colour values are valid
        #
        for index, value in enumerate(colour):
            if not isinstance(value, (float, int)):
                value_err = "Received Non numeric value '%s'." %value
                raise StatusLightError('%s%s' %(colour_err, value_err))
            
            colour[index] = int(max(min(value, 255), 0))
        
        # store new colour
        #
        self._status_colours[colour_name] = tuple(colour)
    
    # ---------------------------------------------------------------------------------------- #

    def setStatus(self, status=None, mode=None):
        if status is None:
            status = self.DEFAULT
            
        if status not in self._status_colours.keys():
            raise StatusLightError("Status type '%s' not recognised." %status)
        
        status_colour  = self._status_colours[status]
        current_colour = self._colour.getRgb()
        
        # get base colour from colour
        #
        def getBaseColour(colour):            
            base_colour = list(colour)
            for index, value in enumerate(colour):
                base_colour[index] = max((value - 30), 0)
            return base_colour
        
        # if animation is on, calculate colours and start timer
        #
        if self._animate is True:            
            r_inc = (status_colour[0] - current_colour[0]) / 20.0
            g_inc = (status_colour[1] - current_colour[1]) / 20.0
            b_inc = (status_colour[2] - current_colour[2]) / 20.0
            colours = self._anim_colours = [((current_colour[0] + (index * r_inc)),
                                             (current_colour[1] + (index * g_inc)),
                                             (current_colour[2] + (index * b_inc))) 
                                            for index in range(1,21)]
            
            self._anim_base_colours = [getBaseColour(colour) for colour in colours]
            self._anim_increment = 0
            
            if mode == None or mode == self.ANIM_TIMER:
                self._anim_timer = qc.QTimer()
                self._anim_timer.timeout.connect(self._animateLight)        
                self._anim_timer.start(5)
                          
            else:                
                while self._anim_increment < 20:
                    self._colour.setRgb(*self._anim_colours[self._anim_increment])
                    self._base_colour.setRgb(*self._anim_base_colours[self._anim_increment])
                    self._anim_increment += 1
                    
                    self.update()
                    qg.QApplication.processEvents()
                    time.sleep(0.005)
                       
        else:                
            self._colour.setRgb(*status_colour)
            self._base_colour.setRgb(*getBaseColour(status_colour))          
            self.update()
            
        self._status = status
        qg.QApplication.processEvents()
        
    
    def _animateLight(self):        
        counter = self._anim_increment
        self._colour.setRgb(*self._anim_colours[counter])
        
        self._base_colour.setRgb(*self._anim_base_colours[counter])

        self._anim_increment += 1
        
        if self._anim_increment == 20:
            self._anim_increment = 0
            self._anim_timer.stop()
            self._anim_timer = None
           
        self.update()
        qg.QApplication.processEvents()
        
    # ---------------------------------------------------------------------------------------- #
    
    def paintEvent(self, pEvent):
        painter = qg.QStylePainter(self)
        option = qg.QStyleOption()
        option.initFrom(self)

        height = option.rect.height() - 1
        width  = option.rect.width() - 1
            
        old_pen = painter.pen()
                
        if not self.isEnabled():
            painter.setOpacity(0.3)

        # calculate light size
        #
        radius = self._radius
        circ   = radius * 2
        half_height = (height / 2) - 1
        half_width  = (width / 2) - 1
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
        brush = qg.QBrush(self._base_colour, qc.Qt.SolidPattern)
        painter.setBrush(brush)
        painter.setPen(self._base_colour)
        painter.drawEllipse(x_offset, y_offset, circ, circ)
        
        # draw main colour
        #
        main_radius = radius - 2
        main_circ   = main_radius * 2
        main_x_offset = half_height - main_radius - 1
        main_y_offset = half_width  - main_radius - 1
        brush = qg.QBrush(qg.QBrush(self._colour, qc.Qt.SolidPattern))
        painter.setBrush(brush)
        painter.setPen(self._colour)
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