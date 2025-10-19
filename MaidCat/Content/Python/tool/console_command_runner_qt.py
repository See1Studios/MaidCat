"""
콘솔 명령어 실행기 - PySide2 GUI 버전

독립적인 Qt 윈도우로 동작하는 GUI 버전
"""

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    PYSIDE_AVAILABLE = True
except ImportError:
    print("PySide2가 설치되어 있지 않습니다.")
    print("설치 방법: pip install PySide2")
    PYSIDE_AVAILABLE = False

import unreal
import json
import os
import sys


# ============================================================================
# 설정
# ============================================================================

DATA_DIRECTORY = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandData/"
FAVORITES_FILE = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandFavorites.json"
HISTORY_FILE = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandHistory.json"


# ============================================================================
# 데이터 관리 클래스
# ============================================================================

class CommandDataManager:
    """명령어 데이터 관리"""
    
    def __init__(self):
        self.commands = []
        self.scopes = []
        self.load_all_commands()
    
    def load_all_commands(self):
        """모든 명령어 로드"""
        self.commands = []
        self.scopes = []
        
        if not os.path.exists(DATA_DIRECTORY):
            unreal.log_warning(f"데이터 디렉토리를 찾을 수 없습니다: {DATA_DIRECTORY}")
            return False
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        if not json_files:
            unreal.log_warning("JSON 데이터 파일이 없습니다.")
            return False
        
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            scope = json_file.replace('_commands_kr.json', '').replace('_TEST', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    cmd_data['scope'] = scope
                    self.commands.append(cmd_data)
                
                if scope not in self.scopes:
                    self.scopes.append(scope)
                    
            except Exception as e:
                unreal.log_error(f"파일 로드 실패 ({json_file}): {e}")
        
        unreal.log(f"✓ {len(self.commands)}개의 명령어 로드 완료")
        return True
    
    def search_commands(self, query, scope_filter=None):
        """명령어 검색"""
        if not query and not scope_filter:
            return self.commands
        
        results = []
        query_lower = query.lower() if query else ""
        
        for cmd in self.commands:
            # 스코프 필터
            if scope_filter and cmd.get('scope') != scope_filter:
                continue
            
            # 검색어 필터
            if query:
                if (query_lower in cmd.get('command', '').lower() or
                    query_lower in cmd.get('help_en', '').lower() or
                    query_lower in cmd.get('help_kr', '').lower()):
                    results.append(cmd)
            else:
                results.append(cmd)
        
        return results
    
    def get_command(self, command_name):
        """명령어 정보 가져오기"""
        for cmd in self.commands:
            if cmd.get('command') == command_name:
                return cmd
        return None
    
    def execute_command(self, command_name, args=""):
        """명령어 실행"""
        full_command = f"{command_name} {args}".strip()
        
        try:
            unreal.log(f"실행: {full_command}")
            unreal.SystemLibrary.execute_console_command(None, full_command)
            self.add_to_history(full_command)
            return True
        except Exception as e:
            unreal.log_error(f"실행 실패: {e}")
            return False
    
    def load_favorites(self):
        """즐겨찾기 로드"""
        if not os.path.exists(FAVORITES_FILE):
            return []
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_favorites(self, favorites):
        """즐겨찾기 저장"""
        try:
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def load_history(self):
        """히스토리 로드"""
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def add_to_history(self, command):
        """히스토리 추가"""
        history = self.load_history()
        if command in history:
            history.remove(command)
        history.insert(0, command)
        
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history[:50], f, indent=2, ensure_ascii=False)
        except:
            pass


# ============================================================================
# Qt GUI
# ============================================================================

if PYSIDE_AVAILABLE:
    
    class ConsoleCommandRunnerGUI(QtWidgets.QMainWindow):
        """콘솔 명령어 실행기 메인 윈도우"""
        
        def __init__(self):
            super().__init__()
            self.data_manager = CommandDataManager()
            self.favorites = self.data_manager.load_favorites()
            self.init_ui()
            self.refresh_command_list()
        
        def init_ui(self):
            """UI 초기화"""
            self.setWindowTitle("언리얼 콘솔 명령어 실행기")
            self.setGeometry(100, 100, 1000, 700)
            
            # 중앙 위젯
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            
            # 메인 레이아웃
            main_layout = QtWidgets.QVBoxLayout(central_widget)
            
            # 상단: 검색 & 필터
            search_layout = QtWidgets.QHBoxLayout()
            
            # 검색창
            self.search_input = QtWidgets.QLineEdit()
            self.search_input.setPlaceholderText("명령어 또는 설명 검색...")
            self.search_input.textChanged.connect(self.on_search_changed)
            search_layout.addWidget(QtWidgets.QLabel("검색:"))
            search_layout.addWidget(self.search_input)
            
            # 스코프 필터
            self.scope_combo = QtWidgets.QComboBox()
            self.scope_combo.addItem("전체", None)
            for scope in sorted(self.data_manager.scopes):
                self.scope_combo.addItem(scope, scope)
            self.scope_combo.currentIndexChanged.connect(self.on_scope_changed)
            search_layout.addWidget(QtWidgets.QLabel("스코프:"))
            search_layout.addWidget(self.scope_combo)
            
            main_layout.addLayout(search_layout)
            
            # 중앙: 탭 위젯
            self.tab_widget = QtWidgets.QTabWidget()
            
            # 탭 1: 명령어 목록
            self.commands_tab = self.create_commands_tab()
            self.tab_widget.addTab(self.commands_tab, "명령어")
            
            # 탭 2: 즐겨찾기
            self.favorites_tab = self.create_favorites_tab()
            self.tab_widget.addTab(self.favorites_tab, "즐겨찾기")
            
            # 탭 3: 히스토리
            self.history_tab = self.create_history_tab()
            self.tab_widget.addTab(self.history_tab, "히스토리")
            
            # 탭 4: 프리셋
            self.presets_tab = self.create_presets_tab()
            self.tab_widget.addTab(self.presets_tab, "프리셋")
            
            self.tab_widget.currentChanged.connect(self.on_tab_changed)
            main_layout.addWidget(self.tab_widget)
            
            # 하단: 상세 정보 & 실행
            detail_group = QtWidgets.QGroupBox("명령어 상세 정보")
            detail_layout = QtWidgets.QVBoxLayout(detail_group)
            
            # 명령어 이름
            self.command_name_label = QtWidgets.QLabel("명령어: (선택 없음)")
            self.command_name_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            detail_layout.addWidget(self.command_name_label)
            
            # 설명 (한국어)
            self.description_kr = QtWidgets.QTextEdit()
            self.description_kr.setReadOnly(True)
            self.description_kr.setMaximumHeight(60)
            detail_layout.addWidget(QtWidgets.QLabel("설명 (한국어):"))
            detail_layout.addWidget(self.description_kr)
            
            # 설명 (영어)
            self.description_en = QtWidgets.QTextEdit()
            self.description_en.setReadOnly(True)
            self.description_en.setMaximumHeight(60)
            detail_layout.addWidget(QtWidgets.QLabel("설명 (영어):"))
            detail_layout.addWidget(self.description_en)
            
            # 실행 영역
            exec_layout = QtWidgets.QHBoxLayout()
            
            self.args_input = QtWidgets.QLineEdit()
            self.args_input.setPlaceholderText("명령어 인자 (선택사항)")
            exec_layout.addWidget(QtWidgets.QLabel("인자:"))
            exec_layout.addWidget(self.args_input)
            
            self.execute_btn = QtWidgets.QPushButton("실행")
            self.execute_btn.clicked.connect(self.on_execute_clicked)
            self.execute_btn.setEnabled(False)
            exec_layout.addWidget(self.execute_btn)
            
            self.favorite_btn = QtWidgets.QPushButton("⭐")
            self.favorite_btn.setFixedWidth(40)
            self.favorite_btn.clicked.connect(self.on_favorite_clicked)
            self.favorite_btn.setEnabled(False)
            exec_layout.addWidget(self.favorite_btn)
            
            detail_layout.addLayout(exec_layout)
            
            main_layout.addWidget(detail_group)
            
            # 상태바
            self.statusBar().showMessage(f"{len(self.data_manager.commands)}개의 명령어 로드됨")
        
        def create_commands_tab(self):
            """명령어 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            self.command_list = QtWidgets.QListWidget()
            self.command_list.itemClicked.connect(self.on_command_selected)
            self.command_list.itemDoubleClicked.connect(self.on_command_double_clicked)
            layout.addWidget(self.command_list)
            
            return widget
        
        def create_favorites_tab(self):
            """즐겨찾기 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            self.favorites_list = QtWidgets.QListWidget()
            self.favorites_list.itemClicked.connect(self.on_favorite_selected)
            self.favorites_list.itemDoubleClicked.connect(self.on_command_double_clicked)
            layout.addWidget(self.favorites_list)
            
            return widget
        
        def create_history_tab(self):
            """히스토리 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            self.history_list = QtWidgets.QListWidget()
            self.history_list.itemDoubleClicked.connect(self.on_history_double_clicked)
            layout.addWidget(self.history_list)
            
            btn_layout = QtWidgets.QHBoxLayout()
            clear_btn = QtWidgets.QPushButton("히스토리 지우기")
            clear_btn.clicked.connect(self.on_clear_history)
            btn_layout.addStretch()
            btn_layout.addWidget(clear_btn)
            layout.addLayout(btn_layout)
            
            return widget
        
        def create_presets_tab(self):
            """프리셋 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            presets = {
                "Performance": {
                    "FPS 표시": "stat fps",
                    "프레임 시간": "stat unit",
                    "GPU 통계": "stat gpu",
                    "렌더 통계": "stat rhi",
                    "메모리 통계": "stat memory",
                },
                "Rendering": {
                    "1080p 창모드": "r.SetRes 1920x1080w",
                    "1080p 전체화면": "r.SetRes 1920x1080f",
                    "4K 창모드": "r.SetRes 3840x2160w",
                    "V-Sync 켜기": "r.VSync 1",
                    "V-Sync 끄기": "r.VSync 0",
                },
                "Debug": {
                    "와이어프레임": "viewmode wireframe",
                    "라이팅": "viewmode lit",
                    "언릿": "viewmode unlit",
                    "콜리전 표시": "show collision",
                    "네비메시 표시": "show navigation",
                },
            }
            
            for category, commands in presets.items():
                group = QtWidgets.QGroupBox(category)
                group_layout = QtWidgets.QGridLayout(group)
                
                row = 0
                col = 0
                for name, command in commands.items():
                    btn = QtWidgets.QPushButton(name)
                    btn.clicked.connect(lambda checked, cmd=command: self.execute_preset_command(cmd))
                    group_layout.addWidget(btn, row, col)
                    
                    col += 1
                    if col >= 2:
                        col = 0
                        row += 1
                
                layout.addWidget(group)
            
            layout.addStretch()
            
            return widget
        
        def refresh_command_list(self, commands=None):
            """명령어 리스트 갱신"""
            if commands is None:
                commands = self.data_manager.commands
            
            self.command_list.clear()
            
            for cmd in commands:
                text = f"[{cmd.get('scope')}] {cmd.get('command')}"
                item = QtWidgets.QListWidgetItem(text)
                item.setData(QtCore.Qt.UserRole, cmd)
                self.command_list.addItem(item)
            
            self.statusBar().showMessage(f"{len(commands)}개의 명령어")
        
        def refresh_favorites_list(self):
            """즐겨찾기 리스트 갱신"""
            self.favorites_list.clear()
            
            for cmd_name in self.favorites:
                cmd = self.data_manager.get_command(cmd_name)
                if cmd:
                    text = f"[{cmd.get('scope')}] {cmd.get('command')}"
                    item = QtWidgets.QListWidgetItem(text)
                    item.setData(QtCore.Qt.UserRole, cmd)
                    self.favorites_list.addItem(item)
        
        def refresh_history_list(self):
            """히스토리 리스트 갱신"""
            self.history_list.clear()
            history = self.data_manager.load_history()
            
            for cmd_text in history:
                self.history_list.addItem(cmd_text)
        
        def on_search_changed(self, text):
            """검색어 변경"""
            scope = self.scope_combo.currentData()
            results = self.data_manager.search_commands(text, scope)
            self.refresh_command_list(results)
        
        def on_scope_changed(self, index):
            """스코프 변경"""
            scope = self.scope_combo.currentData()
            query = self.search_input.text()
            results = self.data_manager.search_commands(query, scope)
            self.refresh_command_list(results)
        
        def on_command_selected(self, item):
            """명령어 선택"""
            cmd = item.data(QtCore.Qt.UserRole)
            self.display_command_info(cmd)
        
        def on_favorite_selected(self, item):
            """즐겨찾기 선택"""
            cmd = item.data(QtCore.Qt.UserRole)
            self.display_command_info(cmd)
        
        def display_command_info(self, cmd):
            """명령어 정보 표시"""
            if not cmd:
                return
            
            self.current_command = cmd.get('command')
            self.command_name_label.setText(f"명령어: {self.current_command}")
            self.description_kr.setText(cmd.get('help_kr', '설명 없음'))
            self.description_en.setText(cmd.get('help_en', 'No description'))
            
            self.execute_btn.setEnabled(True)
            self.favorite_btn.setEnabled(True)
            
            # 즐겨찾기 버튼 업데이트
            if self.current_command in self.favorites:
                self.favorite_btn.setText("⭐")
            else:
                self.favorite_btn.setText("☆")
        
        def on_command_double_clicked(self, item):
            """명령어 더블클릭 (즉시 실행)"""
            cmd = item.data(QtCore.Qt.UserRole)
            if cmd:
                self.data_manager.execute_command(cmd.get('command'), "")
                self.statusBar().showMessage(f"실행: {cmd.get('command')}", 3000)
        
        def on_history_double_clicked(self, item):
            """히스토리 더블클릭 (재실행)"""
            command = item.text()
            parts = command.split(' ', 1)
            cmd_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            self.data_manager.execute_command(cmd_name, args)
            self.statusBar().showMessage(f"재실행: {command}", 3000)
        
        def on_execute_clicked(self):
            """실행 버튼 클릭"""
            if hasattr(self, 'current_command'):
                args = self.args_input.text()
                success = self.data_manager.execute_command(self.current_command, args)
                
                if success:
                    self.statusBar().showMessage(f"실행 완료: {self.current_command}", 3000)
                    self.args_input.clear()
                else:
                    self.statusBar().showMessage("실행 실패!", 3000)
        
        def on_favorite_clicked(self):
            """즐겨찾기 버튼 클릭"""
            if not hasattr(self, 'current_command'):
                return
            
            if self.current_command in self.favorites:
                self.favorites.remove(self.current_command)
                self.favorite_btn.setText("☆")
                self.statusBar().showMessage("즐겨찾기에서 제거됨", 2000)
            else:
                self.favorites.append(self.current_command)
                self.favorite_btn.setText("⭐")
                self.statusBar().showMessage("즐겨찾기에 추가됨", 2000)
            
            self.data_manager.save_favorites(self.favorites)
            self.refresh_favorites_list()
        
        def on_tab_changed(self, index):
            """탭 변경"""
            if index == 1:  # 즐겨찾기 탭
                self.refresh_favorites_list()
            elif index == 2:  # 히스토리 탭
                self.refresh_history_list()
        
        def on_clear_history(self):
            """히스토리 지우기"""
            reply = QtWidgets.QMessageBox.question(
                self, '확인', '히스토리를 모두 지우시겠습니까?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                try:
                    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    self.refresh_history_list()
                    self.statusBar().showMessage("히스토리가 지워졌습니다.", 2000)
                except:
                    pass
        
        def execute_preset_command(self, command):
            """프리셋 명령어 실행"""
            parts = command.split(' ', 1)
            cmd_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            success = self.data_manager.execute_command(cmd_name, args)
            
            if success:
                self.statusBar().showMessage(f"실행: {command}", 3000)
            else:
                self.statusBar().showMessage("실행 실패!", 3000)


# ============================================================================
# 실행 함수
# ============================================================================

def show_gui():
    """GUI 창 표시"""
    if not PYSIDE_AVAILABLE:
        print("PySide2가 설치되어 있지 않습니다.")
        print("pip install PySide2")
        return None
    
    # Qt 애플리케이션 인스턴스 확인
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    # 메인 윈도우 생성
    window = ConsoleCommandRunnerGUI()
    window.show()
    
    return window


if __name__ == "__main__":
    if PYSIDE_AVAILABLE:
        print("콘솔 명령어 실행기 Qt GUI")
        print("실행: show_gui()")
    else:
        print("PySide2를 설치해주세요: pip install PySide2")
