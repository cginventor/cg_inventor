import PySide.QtCore as qc
import PySide.QtGui as qg

import tracker


class InterpolateIt(qg.QDialog):
    pass



class InterpolateSet(qg.QWidget):
    def __init__(self):
        self.tracker = tracker.Tracker()
        
        qg.QWidget.__init__(self)
        
        self.setFixedWidth(250)
        
        self.setLayout(qg.QVBoxLayout())
        self.layout().setContentsMargins(5,5,5,5)
        self.layout().setSpacing(2)
        
        bold_font = qg.QFont()
        bold_font.setBold(True)
        
        attribute_layout = qg.QHBoxLayout()
        attribute_layout.setSpacing(2)
        attribute_layout.setContentsMargins(0,0,0,0)
        self.layout().addLayout(attribute_layout)
        attribute_label = qg.QLabel('Attributes:')   
        attribute_label.setFont(bold_font)
        self.track_button = qg.QPushButton('Track')
        self.track_button.setFixedWidth(50)
        self.clear_button = qg.QPushButton('Clear')
        self.clear_button.setFixedWidth(50)
        attribute_layout.addWidget(attribute_label)
        attribute_layout.addWidget(self.track_button)
        attribute_layout.addWidget(self.clear_button)
        
        key_layout = qg.QHBoxLayout()        
        key_layout.setSpacing(2)
        key_layout.setContentsMargins(0,0,0,0)     
        self.layout().addLayout(key_layout)
        keys_label = qg.QLabel('Keys:')        
        keys_label.setFont(bold_font)
        self.add_button = qg.QPushButton('Add')        
        self.add_button.setFixedWidth(50)
        self.remove_button = qg.QPushButton('Remove')        
        self.remove_button.setFixedWidth(50)
        key_layout.addWidget(keys_label)
        key_layout.addWidget(self.add_button)
        key_layout.addWidget(self.remove_button)        
        
        slider_layout = qg.QHBoxLayout()
        slider_layout.setSpacing(5)
        slider_layout.setContentsMargins(0,5,0,0)
        self.layout().addLayout(slider_layout)        
        self.start_label = qg.QLabel('Start')               
        self.start_label.setFont(bold_font)
        self.slider = qg.QSlider()
        self.slider.setRange(0, 49)
        self.slider.setOrientation(qc.Qt.Horizontal)
        self.slider.setFixedHeight(22)
        self.end_label = qg.QLabel('End')
        self.end_label.setFont(bold_font)
        slider_layout.addWidget(self.start_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.end_label)
        
        self.track_button.clicked.connect(self.tracker.store)
        self.clear_button.clicked.connect(self.tracker.clear)
        self.add_button.clicked.connect(self.key)
        
        self.slider.valueChanged.connect(self.tracker.set)
        
        
    def key(self):
        self.tracker.key(self.slider.value())
        
        
        
        