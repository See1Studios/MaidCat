"""
Unreal Engine Qt UI Loader
.ui 파일을 로드하여 Unreal Engine에서 실행하는 유틸리티

Features:
- .ui 파일 자동 검색 (프로젝트 내 여러 경로)
- 에러 처리 및 Fallback UI
- Unreal 통합 기능들
- 재사용 가능한 클래스 구조

Usage:
    exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())
"""

import sys
import unreal
from pathlib import Path
from PySide6.QtCore import Qt, QFile, QIODevice
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QGroupBox, QMessageBox, QFileDialog
)
from PySide6.QtUiTools import QUiLoader


class UnrealQtWindow(QWidget):
    """
    Unreal Engine Qt Window
    .ui 파일을 로드하거나 Fallback UI를 표시
    """
    # 클래스 변수로 윈도우 참조 유지 (가비지 컬렉션 방지)
    _instance = None
    
    def __init__(self, ui_file_path=None):
        super().__init__()
        
        # 기존 인스턴스 정리
        if UnrealQtWindow._instance:
            try:
                UnrealQtWindow._instance.close()
                UnrealQtWindow._instance.deleteLater()
            except:
                pass
        
        UnrealQtWindow._instance = self
        
        # UI 파일 경로 찾기
        self.ui_file_path = self.find_ui_file(ui_file_path)
        
        # UI 로드 시도
        if self.ui_file_path and self.ui_file_path.exists():
            if not self.load_ui_file(self.ui_file_path):
                unreal.log_warning("Failed to load .ui file, creating fallback UI")
                self.create_fallback_ui()
        else:
            unreal.log_warning("No .ui file found, creating fallback UI")
            self.create_fallback_ui()
        
        # 윈도우 설정
        self.setWindowTitle("Unreal Qt Tool")
        self.setMinimumSize(500, 400)
    
    def find_ui_file(self, ui_file_path=None):
        """
        .ui 파일 검색
        1. 지정된 경로
        2. 같은 폴더의 QtTest.ui
        3. 프로젝트 내 여러 경로
        """
        if ui_file_path:
            path = Path(ui_file_path)
            if path.exists():
                unreal.log(f"Found UI file: {path}")
                return path
        
        # 스크립트와 같은 폴더
        script_dir = Path(__file__).parent
        same_dir_ui = script_dir / "QtTest.ui"
        if same_dir_ui.exists():
            unreal.log(f"Found UI file in same directory: {same_dir_ui}")
            return same_dir_ui
        
        # 프로젝트 내 검색
        project_content = Path(unreal.Paths.project_content_dir())
        search_paths = [
            project_content / "Python" / "developer" / "ui",
            project_content / "Python" / "Test",
            project_content / "Python" / "ui",
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                ui_files = list(search_path.glob("*.ui"))
                if ui_files:
                    unreal.log(f"Found UI file: {ui_files[0]}")
                    return ui_files[0]
        
        unreal.log_warning("No .ui file found in standard locations")
        return None
    
    def load_ui_file(self, ui_file_path):
        """
        .ui 파일 로드
        """
        try:
            ui_file = QFile(str(ui_file_path))
            
            if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
                unreal.log_error(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
                return False
            
            loader = QUiLoader()
            self.loaded_widget = loader.load(ui_file)
            ui_file.close()
            
            if not self.loaded_widget:
                unreal.log_error(f"Failed to load UI: {loader.errorString()}")
                return False
            
            # 메인 레이아웃에 로드된 위젯 추가
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.loaded_widget)
            
            # 버튼 찾아서 연결
            self.connect_ui_elements()
            
            unreal.log(f"✅ Successfully loaded UI from: {ui_file_path}")
            return True
            
        except Exception as e:
            unreal.log_error(f"Error loading UI file: {e}")
            return False
    
    def connect_ui_elements(self):
        """
        로드된 UI의 요소들을 찾아서 자동으로 연결
        """
        try:
            # .ui 파일의 모든 버튼 찾기 및 연결
            buttons = self.loaded_widget.findChildren(QPushButton)
            
            for btn in buttons:
                btn_name = btn.objectName()
                
                # 버튼 이름에 따라 자동 연결
                if btn_name in ['pushButton', 'btnTest', 'btnExecute']:
                    btn.clicked.connect(self.on_button_clicked)
                    unreal.log(f"Connected {btn_name} -> on_button_clicked")
                
                elif btn_name in ['btnSelected', 'btnShowSelected']:
                    btn.clicked.connect(self.show_selected_assets)
                    unreal.log(f"Connected {btn_name} -> show_selected_assets")
                
                elif btn_name in ['btnRefresh', 'btnUpdate']:
                    btn.clicked.connect(self.update_engine_info)
                    unreal.log(f"Connected {btn_name} -> update_engine_info")
                
                elif btn_name in ['btnLoadUI', 'btnLoad']:
                    btn.clicked.connect(self.load_ui_dialog)
                    unreal.log(f"Connected {btn_name} -> load_ui_dialog")
                
                elif btn_name in ['btnClose', 'btnExit']:
                    btn.clicked.connect(self.close)
                    unreal.log(f"Connected {btn_name} -> close")
                
                else:
                    # 알 수 없는 버튼은 기본 핸들러 연결
                    btn.clicked.connect(lambda checked, name=btn_name: self.on_generic_button(name))
                    unreal.log(f"Connected {btn_name} -> on_generic_button")
            
            # 텍스트 편집 필드 찾기 (정보 표시용)
            text_edit = self.loaded_widget.findChild(QTextEdit, 'textEditInfo')
            if text_edit:
                self.info_text = text_edit
                self.update_engine_info()
                unreal.log("Found and connected textEditInfo")
            
        except Exception as e:
            unreal.log_warning(f"Could not connect UI elements: {e}")
    
    def create_fallback_ui(self):
        """
        .ui 파일이 없을 때 Fallback UI 생성
        """
        layout = QVBoxLayout(self)
        
        # 제목
        title = QLabel("🎮 Unreal Engine Qt Tool")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
            background-color: #2d2d30;
            color: #ffffff;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 정보 그룹
        info_group = QGroupBox("Unreal Engine Information")
        info_layout = QVBoxLayout()
        
        # 엔진 정보 표시
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.update_engine_info()
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 액션 그룹
        action_group = QGroupBox("Quick Actions")
        action_layout = QVBoxLayout()
        
        # 버튼들
        btn_layout1 = QHBoxLayout()
        
        btn_engine_ver = QPushButton("📋 Show Engine Version")
        btn_engine_ver.clicked.connect(self.show_engine_version)
        btn_layout1.addWidget(btn_engine_ver)
        
        btn_selected = QPushButton("🎯 Show Selected Assets")
        btn_selected.clicked.connect(self.show_selected_assets)
        btn_layout1.addWidget(btn_selected)
        
        action_layout.addLayout(btn_layout1)
        
        btn_layout2 = QHBoxLayout()
        
        btn_refresh = QPushButton("🔄 Refresh Info")
        btn_refresh.clicked.connect(self.update_engine_info)
        btn_layout2.addWidget(btn_refresh)
        
        btn_load_ui = QPushButton("📂 Load .ui File")
        btn_load_ui.clicked.connect(self.load_ui_dialog)
        btn_layout2.addWidget(btn_load_ui)
        
        action_layout.addLayout(btn_layout2)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # Spacer
        layout.addStretch()
        
        # 닫기 버튼
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
    
    def update_engine_info(self):
        """
        Unreal Engine 정보 업데이트
        """
        try:
            info_lines = [
                f"🎮 Engine Version: {unreal.SystemLibrary.get_engine_version()}",
                f"📁 Project Directory: {unreal.Paths.project_dir()}",
                f"📁 Content Directory: {unreal.Paths.project_content_dir()}",
                f"🐍 Python Version: {sys.version.split()[0]}",
                f"🖥️  Platform: {sys.platform}",
            ]
            
            self.info_text.setPlainText("\n".join(info_lines))
            
        except Exception as e:
            self.info_text.setPlainText(f"Error getting engine info: {e}")
    
    def on_button_clicked(self):
        """
        .ui 파일의 기본 버튼 클릭 핸들러
        """
        self.show_engine_version()
    
    def on_generic_button(self, button_name):
        """
        일반 버튼 클릭 핸들러
        """
        unreal.log(f"Button clicked: {button_name}")
        QMessageBox.information(
            self,
            "Button Clicked",
            f"Button '{button_name}' was clicked.\n\nAdd custom handler in connect_ui_elements()."
        )
    
    def show_engine_version(self):
        """
        엔진 버전 표시
        """
        version = unreal.SystemLibrary.get_engine_version()
        unreal.log(f"Engine Version: {version}")
        
        QMessageBox.information(
            self,
            "Engine Version",
            f"🎮 Unreal Engine Version:\n\n{version}"
        )
    
    def show_selected_assets(self):
        """
        선택된 에셋 표시
        """
        selected = unreal.EditorUtilityLibrary.get_selected_assets()
        
        if not selected:
            QMessageBox.information(self, "Selected Assets", "No assets selected")
            unreal.log_warning("No assets selected")
            return
        
        asset_info = [
            f"Selected {len(selected)} asset(s):\n"
        ]
        
        for asset in selected[:10]:  # 최대 10개까지만
            asset_info.append(f"  • {asset.get_name()} ({asset.get_class().get_name()})")
        
        if len(selected) > 10:
            asset_info.append(f"\n  ... and {len(selected) - 10} more")
        
        message = "\n".join(asset_info)
        unreal.log(message)
        
        QMessageBox.information(self, "Selected Assets", message)
    
    def load_ui_dialog(self):
        """
        .ui 파일 선택 대화상자
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Qt UI File",
            str(Path(unreal.Paths.project_content_dir()) / "Python"),
            "Qt UI Files (*.ui)"
        )
        
        if file_path:
            unreal.log(f"Loading UI from: {file_path}")
            # 새 윈도우로 다시 열기
            open_qt_window(file_path)


def open_qt_window(ui_file_path=None):
    """
    Qt 윈도우 열기
    
    Args:
        ui_file_path: .ui 파일 경로 (선택사항)
    
    Returns:
        UnrealQtWindow: 생성된 윈도우 인스턴스
    """
    # QApplication 확인/생성
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 기존 윈도우 정리
    for win in QApplication.allWindows():
        if win.objectName() == 'UnrealQtTestWindow':
            win.close()
            win.deleteLater()
    
    # 윈도우 생성
    window = UnrealQtWindow(ui_file_path)
    window.setObjectName('UnrealQtTestWindow')
    window.show()
    
    # Unreal Slate에 부모 지정
    unreal.parent_external_window_to_slate(window.winId())
    
    unreal.log("✅ Qt Window opened successfully")
    
    return window


# 메인 실행
if __name__ == "__main__":
    window = open_qt_window()