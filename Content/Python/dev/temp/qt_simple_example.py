"""
PySide6 간단한 예제 - Unreal Engine에서 Qt 대화상자 표시

Requirements:
- PySide6 설치 필요
  실행: exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_pyside2.py').read())

Usage:
  Unreal Python 콘솔에서:
  exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_simple_example.py').read())
"""

import unreal
import sys
from PySide6 import QtCore, QtWidgets


def show_simple_dialog():
    """간단한 정보 대화상자"""
    # QApplication 확인/생성
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # 메시지 박스
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Unreal Python")
    msg.setText("Hello from PySide6!")
    msg.setInformativeText("PySide6가 정상적으로 설치되었습니다.")
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    # Unreal Slate에 부모 지정
    unreal.parent_external_window_to_slate(msg.winId())
    
    result = msg.exec()
    unreal.log(f"Dialog closed with result: {result}")


def show_input_dialog():
    """사용자 입력 받기"""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    text, ok = QtWidgets.QInputDialog.getText(
        None,
        "Input Dialog",
        "Enter your name:"
    )
    
    if ok and text:
        unreal.log(f"User entered: {text}")
        
        # 결과 표시
        msg = QtWidgets.QMessageBox()
        msg.setText(f"Hello, {text}!")
        msg.exec()
    else:
        unreal.log("User cancelled input")


def show_custom_window():
    """커스텀 윈도우 생성"""
    
    class SimpleWindow(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.setup_ui()
        
        def setup_ui(self):
            # 윈도우 설정
            self.setWindowTitle("Simple Unreal Tool")
            self.setMinimumSize(400, 200)
            
            # 레이아웃
            layout = QtWidgets.QVBoxLayout(self)
            
            # 제목
            title = QtWidgets.QLabel("🎮 Unreal Engine Tool")
            title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
            title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # 버튼들
            btn_layout = QtWidgets.QHBoxLayout()
            
            btn_log = QtWidgets.QPushButton("Log Message")
            btn_log.clicked.connect(self.on_log_clicked)
            btn_layout.addWidget(btn_log)
            
            btn_assets = QtWidgets.QPushButton("Get Selected Assets")
            btn_assets.clicked.connect(self.on_assets_clicked)
            btn_layout.addWidget(btn_assets)
            
            layout.addLayout(btn_layout)
            
            # 닫기 버튼
            btn_close = QtWidgets.QPushButton("Close")
            btn_close.clicked.connect(self.close)
            layout.addWidget(btn_close)
            
            layout.addStretch()
        
        def on_log_clicked(self):
            unreal.log("Button clicked from PySide6 window!")
            QtWidgets.QMessageBox.information(self, "Info", "Message logged to Unreal console")
        
        def on_assets_clicked(self):
            # 선택된 에셋 가져오기
            selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
            
            if selected_assets:
                asset_names = [asset.get_name() for asset in selected_assets]
                message = f"Selected {len(asset_names)} asset(s):\n" + "\n".join(asset_names)
                unreal.log(message)
                QtWidgets.QMessageBox.information(self, "Selected Assets", message)
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "No assets selected")
    
    # QApplication 확인/생성
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # 기존 윈도우 닫기
    for win in QtWidgets.QApplication.allWindows():
        if win.objectName() == 'SimpleUnrealWindow':
            win.close()
    
    # 새 윈도우 생성
    window = SimpleWindow()
    window.setObjectName('SimpleUnrealWindow')
    window.show()
    
    # Unreal Slate에 부모 지정
    unreal.parent_external_window_to_slate(window.winId())
    
    unreal.log("Simple window opened")
    
    return window


# 메인 실행
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PySide6 Examples for Unreal Engine")
    print("="*60)
    print("\n사용 가능한 함수들:")
    print("  1. show_simple_dialog()    - 간단한 메시지 박스")
    print("  2. show_input_dialog()     - 사용자 입력 받기")
    print("  3. show_custom_window()    - 커스텀 윈도우")
    print("\n예제:")
    print("  >>> show_custom_window()")
    print("="*60 + "\n")
    
    # 기본으로 커스텀 윈도우 표시
    window = show_custom_window()
