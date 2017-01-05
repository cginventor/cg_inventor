import PyQt4.QtCore as qc
import PyQt4.QtGui  as qg

from cg_inventor.sys.lib.qt.tron_widgets import tron_label


WINDOW_NAME = 'Interpolation UI'
UI_NAME     = 'main_ui'
UI_VERSION  = 2.0


class InterpolationUI(qg.QDialog):    
    def __init__(self):
        qg.QDialog.__init__(self)
        self.setLayout(qg.QVBoxLayout())
        
        self.main_widget = qg.QWidget()
        self.main_widget.setLayout(qg.QHBoxLayout())
        self.layout().addWidget(self.main_widget)
        
        self.graphics_scene = qg.QGraphicsScene()
        self.graphics_view = InterpolationGraphicsView(self.graphics_scene)
        self.graphics_view.setHorizontalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(qc.Qt.ScrollBarAlwaysOff)
        style = ['border-style: none;', 'background: transparent;']
        self.graphics_view.setStyleSheet("QGraphicsView {%s}"  %' '.join(style))
        self.graphics_view.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Minimum)
        self.layout().addWidget(self.graphics_view)
        self.graphics_view.main_widget = self.main_widget
        
        label = qg.QLabel('cgInventor')
        dse = qg.QGraphicsDropShadowEffect()
        dse.setBlurRadius(10)
        label.setGraphicsEffect(dse)
        
        self.layout().addWidget(label)
        
        
        
        
class InterpolationGraphicsView(qg.QGraphicsView):
    main_widget = None
    
    def resizeEvent(self, event):
        qg.QGraphicsView.resizeEvent(self, event)
        if not self.main_widget: return
        
        view_geometry = self.geometry()
        self.main_widget.setGeometry(0, 0, view_geometry.width() - 1, view_geometry.height())
        self.setSceneRect(0, 0, view_geometry.width(), view_geometry.height())