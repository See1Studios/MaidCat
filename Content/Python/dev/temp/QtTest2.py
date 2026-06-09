import sys
import unreal
from PySide6.QtWidgets import *

class MyWindow(QWidget):
     def __init__(self):
        super().__init__()
        self.setGeometry(500, 500, 200, 100)

        #라벨
        label = QLabel(unreal.SystemLibrary.get_engine_version())

        #버튼
        button0 = QPushButton()
        button0.setText("Button 0")
        button1 = QPushButton()
        button1.setText("Button 1")
        button2 = QPushButton()
        button2.setText("Button 2")
        button0.clicked.connect(lambda:unreal.log(unreal.SystemLibrary.get_engine_version()))
        button1.clicked.connect(lambda:unreal.log(unreal.SystemLibrary.get_project_content_directory()))
        button2.clicked.connect(lambda:unreal.log(unreal.SystemLibrary.get_rendering_material_quality_level()))

        #레이아웃
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(button0)
        layout.addWidget(button1)
        layout.addWidget(button2)
        self.setLayout(layout)

if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    window = MyWindow()
    window.show()
    unreal.parent_external_window_to_slate(window.winId())