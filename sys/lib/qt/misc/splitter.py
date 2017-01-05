import PyQt4.QtCore as qc
import PyQt4.QtGui as qg

from ..base import Base



class SplitterError(Exception):
    pass



class Splitter(qg.QWidget, Base):
    def __init__(self):
        qg.QWidget.__init__(self)
               
        self.setMinimumHeight(2)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)
        
        self.main_line = qg.QFrame()
        self.main_line.setFrameStyle(qg.QFrame.HLine)
        self.layout().addWidget(self.main_line)
        
        self.second_line = None
        self.widget      = None
        
        self._main_rgb   = (150, 150, 150)
        self._shadow_rgb = (45, 45, 45)
        self._shadow     = True
        
        self._setStyleSheet()
        
        

    def _setStyleSheet(self):
        background    = 'rgba(%s,%s,%s,255)' %self._main_rgb
        shadow        = 'rgba(%s,%s,%s,255)' %self._shadow_rgb
        if self._shadow is True:
            bottom_border = 'border-bottom:1px solid %s;' %shadow
            self.setMinimumHeight(2)
        else:
            bottom_border = ''
            self.setMinimumHeight(1)
        
        style_sheet = "border:0px solid rgba(0,0,0,0); \
                       background-color:%s; \
                       max-height:1px; \
                       %s;" %(background, bottom_border)
        
        self.main_line.setStyleSheet(style_sheet)
        
        if not self.second_line: return
        
        self.second_line.setStyleSheet(style_sheet)



    def addText(self, text, bold=True):
        font = qg.QFont()
        font.setBold(bold)
        text_width = qg.QFontMetrics(font)
        width  = text_width.width(text) + 6
        
        label = qg.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setAlignment(qc.Qt.AlignHCenter)
        label.setMaximumWidth(width)     

        self.addWidget(label)



    def addWidget(self, widget):
        if not isinstance(widget, qg.QWidget):
            raise SplitterError('Non Widget argument received.')

        width  = widget.minimumSizeHint().width()
        widget.setMaximumWidth(width + 10)

        self.main_line.setMaximumWidth(5)

        if self.second_line:
            del(self.second_line); self.second_line = None

        self.widget = widget
        self.layout().addWidget(widget)

        self.second_line = qg.QFrame()
        self.second_line.setFrameStyle(qg.QFrame.HLine)
        self.layout().addWidget(self.second_line)
        
        self._setStyleSheet()
        
    
    
    def refresh(self):
        if not self.second_line: return
        
        width = self.widget.minimumSizeHint().width()
        self.widget.setMaximumWidth(width + 10)
        
        
    
    def setMainColour(self, r, g, b):
        self._main_rgb = (r, g, b)
        self._setStyleSheet()
        
        
    def setShadowColour(self, r, g, b):
        self._shadow_rgb = (r, g, b)
        self._setStyleSheet()  
        
    
    def showShadow(self, value):
        self._shadow = bool(value)
        self._setStyleSheet()
        