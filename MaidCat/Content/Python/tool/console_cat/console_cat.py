"""
MaidCat Console Runner 🐱
데이터 파일 기반 Qt 콘솔 명령어 실행기

특징:
- generate_console_command_list.py로 생성된 JSON 데이터 활용
- 카테고리별 버튼 그리드 UI
- 즐겨찾기 및 히스토리 관리
- 검색 및 필터링
"""

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    PYSIDE_AVAILABLE = True
    print("🎉 PySide6 사용 중")
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        PYSIDE_AVAILABLE = True
        print("⚠️ PySide2 fallback 사용 중")
    except ImportError:
        print("❌ PySide6 또는 PySide2가 필요합니다.")
        print("권장 설치: pip install PySide6")
        print("대안 설치: pip install PySide2")
        PYSIDE_AVAILABLE = False

import unreal
import json
import os
from pathlib import Path


# ============================================================================
# 설정
# ============================================================================

# 데이터 경로
DATA_DIR = Path(unreal.SystemLibrary.get_project_saved_directory()) / "ConsoleCommandData"
FAVORITES_FILE = Path(unreal.SystemLibrary.get_project_saved_directory()) / "ConsoleCatFavorites.json"
SETTINGS_FILE = Path(unreal.SystemLibrary.get_project_saved_directory()) / "ConsoleCatSettings.json"


# ============================================================================
# 데이터 매니저
# ============================================================================

class ConsoleCatDataManager:
    """Console Cat 데이터 관리"""
    
    def __init__(self):
        self.commands = {}  # {scope: [commands]}
        self.all_commands = []
        self.favorites = []
        self.settings = {}
        self.load_data()
    
    def load_data(self):
        """모든 데이터 로드"""
        self.load_commands()
        self.load_favorites()
        self.load_settings()
    
    def load_commands(self):
        """명령어 데이터 로드"""
        if not DATA_DIR.exists():
            print(f"⚠️ 데이터 폴더가 없습니다: {DATA_DIR}")
            print("먼저 generate_console_command_list.py를 실행하세요!")
            return
        
        json_files = list(DATA_DIR.glob("*.json"))
        if not json_files:
            print("⚠️ JSON 데이터 파일이 없습니다.")
            return
        
        self.commands = {}
        self.all_commands = []
        
        for json_file in json_files:
            scope = json_file.stem.replace('_commands_kr', '').replace('_TEST', '')
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                
                # 스코프별 명령어 저장
                self.commands[scope] = commands_data
                
                # 전체 명령어 리스트에 추가
                for cmd in commands_data:
                    cmd['scope'] = scope
                    self.all_commands.append(cmd)
                
                print(f"✅ {scope}: {len(commands_data)}개 명령어 로드")
                
            except Exception as e:
                print(f"❌ {json_file} 로드 실패: {e}")
        
        print(f"📊 총 {len(self.all_commands)}개 명령어 로드 완료")
    
    def load_favorites(self):
        """즐겨찾기 로드"""
        if FAVORITES_FILE.exists():
            try:
                with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
            except:
                self.favorites = []
        else:
            self.favorites = []
    
    def save_favorites(self):
        """즐겨찾기 저장"""
        try:
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"즐겨찾기 저장 실패: {e}")
    
    def load_settings(self):
        """설정 로드"""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        else:
            self.settings = {}
    
    def save_settings(self):
        """설정 저장"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 저장 실패: {e}")
    
    def execute_command(self, command, args=""):
        """명령어 실행"""
        full_command = f"{command} {args}".strip()
        
        try:
            print(f"🚀 실행: {full_command}")
            unreal.SystemLibrary.execute_console_command(None, full_command)
            return True
        except Exception as e:
            print(f"❌ 실행 실패: {e}")
            return False
    
    def search_commands(self, query):
        """명령어 검색"""
        if not query:
            return self.all_commands
        
        query_lower = query.lower()
        results = []
        
        for cmd in self.all_commands:
            if (query_lower in cmd.get('command', '').lower() or
                query_lower in cmd.get('help_kr', '').lower() or
                query_lower in cmd.get('help_en', '').lower()):
                results.append(cmd)
        
        return results
    
    def get_scope_commands(self, scope):
        """특정 스코프의 명령어 반환"""
        return self.commands.get(scope, [])


# ============================================================================
# Qt GUI
# ============================================================================

if PYSIDE_AVAILABLE:
    
    class ConsoleCatMainWindow(QtWidgets.QMainWindow):
        """Console Cat 메인 윈도우"""
        
        def __init__(self):
            super().__init__()
            
            self.data_manager = ConsoleCatDataManager()
            self.current_command = None
            self.init_ui()
            self.setup_styles()
        
        def init_ui(self):
            """UI 초기화"""
            self.setWindowTitle("🐱 Console Cat")
            self.setGeometry(100, 100, 600, 550)
            
            # 중앙 위젯
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            
            # 메인 레이아웃
            main_layout = QtWidgets.QHBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            
            # 스플리터로 고정 크기 분할
            splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            
            # 왼쪽: 카테고리 및 명령어 버튼들 (유동적 크기)
            left_widget = self.create_left_panel()
            left_widget.setMinimumWidth(200)  # 최소 크기만 설정
            splitter.addWidget(left_widget)
            
            # 오른쪽: 상세 정보 및 제어 (고정 크기)
            right_widget = self.create_right_panel()
            right_widget.setMinimumWidth(250)
            right_widget.setMaximumWidth(250)  # 오른쪽만 고정
            splitter.addWidget(right_widget)
            
            # 스플리터 설정
            splitter.setChildrenCollapsible(False)
            splitter.setStretchFactor(0, 1)  # 왼쪽은 늘어남
            splitter.setStretchFactor(1, 0)  # 오른쪽은 고정
            
            main_layout.addWidget(splitter)
            
            # 상태바
            self.statusBar().showMessage(f"🐱 {len(self.data_manager.all_commands)}개 명령어 준비됨")
            
            # 언리얼 슬레이트에 부모 지정 (qt_simple_example.py 방식)
            self.setup_unreal_parenting()
        
        def setup_unreal_parenting(self):
            """언리얼 슬레이트에 윈도우 부모 지정 - qt_simple_example.py 방식"""
            try:
                # qt_simple_example.py와 동일한 방식
                unreal.parent_external_window_to_slate(self.winId())
                print("✅ Console Cat이 언리얼 슬레이트에 연결됨")
            except Exception as e:
                print(f"⚠️ 언리얼 슬레이트 연결 실패: {e}")
                # 실패해도 계속 실행
        
        def refresh_all_tabs(self):
            """모든 탭 새로고침"""
            current_tab = self.category_tabs.currentIndex()
            
            # 탭 다시 생성
            self.category_tabs.clear()
            
            # 전체 탭
            all_tab = self.create_commands_tab(self.data_manager.all_commands)
            self.category_tabs.addTab(all_tab, "📋 전체")
            
            # 스코프별 탭
            for scope in sorted(self.data_manager.commands.keys()):
                commands = self.data_manager.commands[scope]
                tab = self.create_commands_tab(commands)
                self.category_tabs.addTab(tab, f"📂 {scope}")
            
            # 즐겨찾기 탭 (업데이트된 즐겨찾기로)
            fav_commands = [cmd for cmd in self.data_manager.all_commands 
                           if cmd.get('command') in self.data_manager.favorites]
            fav_tab = self.create_commands_tab(fav_commands)
            self.category_tabs.addTab(fav_tab, "⭐ 즐겨찾기")
            
            # 원래 탭으로 복원
            if current_tab < self.category_tabs.count():
                self.category_tabs.setCurrentIndex(current_tab)
        
        def refresh_button_styles(self):
            """버튼 스타일 새로고침 (현재 탭만)"""
            current_widget = self.category_tabs.currentWidget()
            if current_widget:
                # 현재 탭의 모든 버튼 찾기
                buttons = current_widget.findChildren(QtWidgets.QPushButton)
                for btn in buttons:
                    # 버튼의 툴팁에서 명령어 추출
                    tooltip = btn.toolTip()
                    if "] " in tooltip:
                        command = tooltip.split("] ")[1].split("\n")[0]
                        # 즐겨찾기 상태에 따라 스타일 적용
                        self.apply_button_style(btn, command)
        
        def apply_button_style(self, btn, command):
            """버튼에 스타일 적용"""
            if command in self.data_manager.favorites:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFB347;
                        border: 1px solid #FF8C00;
                        color: #000000;
                        font-weight: bold;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 9pt;
                        min-height: 20px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #FFA500;
                        border-color: #FF7F00;
                        color: #000000;
                    }
                    QPushButton:pressed {
                        background-color: #FF8C00;
                        border-color: #FF6347;
                    }
                """)
            else:
                # 기본 스타일로 복원 (상속된 스타일 사용)
                btn.setStyleSheet("")
        
        def create_left_panel(self):
            """왼쪽 패널 생성 (카테고리 + 명령어 버튼)"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            # 상단: 검색
            search_layout = QtWidgets.QHBoxLayout()
            self.search_input = QtWidgets.QLineEdit()
            self.search_input.setPlaceholderText("🔍 명령어 검색...")
            self.search_input.textChanged.connect(self.on_search_changed)
            search_layout.addWidget(self.search_input)
            
            clear_btn = QtWidgets.QPushButton("❌")
            clear_btn.setFixedWidth(30)
            clear_btn.clicked.connect(lambda: self.search_input.clear())
            search_layout.addWidget(clear_btn)
            
            layout.addLayout(search_layout)
            
            # 카테고리 탭
            self.category_tabs = QtWidgets.QTabWidget()
            
            # 전체 탭
            all_tab = self.create_commands_tab(self.data_manager.all_commands)
            self.category_tabs.addTab(all_tab, "📋 전체")
            
            # 스코프별 탭
            for scope in sorted(self.data_manager.commands.keys()):
                commands = self.data_manager.commands[scope]
                tab = self.create_commands_tab(commands)
                self.category_tabs.addTab(tab, f"📂 {scope}")
            
            # 즐겨찾기 탭
            fav_commands = [cmd for cmd in self.data_manager.all_commands 
                           if cmd.get('command') in self.data_manager.favorites]
            fav_tab = self.create_commands_tab(fav_commands)
            self.category_tabs.addTab(fav_tab, "⭐ 즐겨찾기")
            
            # 탭 변경 시 버튼 스타일 새로고침
            self.category_tabs.currentChanged.connect(self.on_tab_changed)
            
            layout.addWidget(self.category_tabs)
            
            return widget
        
        def create_commands_tab(self, commands):
            """명령어 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            # 스크롤 영역
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
            # 버튼 컨테이너 (1열 레이아웃)
            button_widget = QtWidgets.QWidget()
            button_layout = QtWidgets.QVBoxLayout(button_widget)
            button_layout.setSpacing(1)
            
            # 명령어 버튼들 생성 (1열)
            for cmd in commands:
                btn = self.create_command_button(cmd)
                button_layout.addWidget(btn)
            
            # 빈 공간 채우기
            button_layout.addStretch()
            
            scroll.setWidget(button_widget)
            layout.addWidget(scroll)
            
            return widget
        
        def create_command_button(self, cmd):
            """명령어 버튼 생성"""
            command = cmd.get('command', '')
            help_kr = cmd.get('help_kr', '')
            scope = cmd.get('scope', '')
            
            # 버튼 텍스트 (명령어만)
            btn = QtWidgets.QPushButton(command)
            btn.setFixedHeight(28)
            btn.setMinimumWidth(100)
            
            # 툴팁에 상세 정보
            tooltip = f"🔧 명령어: {command}\n📂 카테고리: {scope}\n📖 설명: {help_kr}"
            btn.setToolTip(tooltip)
            
            # 클릭 이벤트
            btn.clicked.connect(lambda checked, c=cmd: self.on_command_button_clicked(c))
            
            # 즐겨찾기 스타일 적용
            self.apply_button_style(btn, command)
            
            return btn
        
        def create_right_panel(self):
            """오른쪽 패널 생성 (상세 정보)"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            # 명령어 정보 그룹
            info_group = QtWidgets.QGroupBox("📋 명령어 정보")
            info_layout = QtWidgets.QVBoxLayout(info_group)
            
            # 명령어 이름
            self.cmd_label = QtWidgets.QLabel("명령어를 선택하세요")
            self.cmd_label.setStyleSheet("font-weight: bold; font-size: 14pt; color: #2E86AB;")
            info_layout.addWidget(self.cmd_label)
            
            # 스코프
            self.scope_label = QtWidgets.QLabel("")
            self.scope_label.setStyleSheet("color: #666666;")
            info_layout.addWidget(self.scope_label)
            
            # 설명
            info_layout.addWidget(QtWidgets.QLabel("📖 설명:"))
            self.desc_kr = QtWidgets.QTextEdit()
            self.desc_kr.setReadOnly(True)
            self.desc_kr.setMaximumHeight(80)
            info_layout.addWidget(self.desc_kr)
            
            layout.addWidget(info_group)
            
            # 실행 그룹
            exec_group = QtWidgets.QGroupBox("🚀 실행")
            exec_layout = QtWidgets.QVBoxLayout(exec_group)
            
            # 인자 입력
            exec_layout.addWidget(QtWidgets.QLabel("매개변수 (선택사항):"))
            self.args_input = QtWidgets.QLineEdit()
            self.args_input.setPlaceholderText("예: 1920x1080w")
            exec_layout.addWidget(self.args_input)
            
            # 버튼들
            btn_layout = QtWidgets.QHBoxLayout()
            
            self.execute_btn = QtWidgets.QPushButton("▶️ 실행")
            self.execute_btn.clicked.connect(self.on_execute_clicked)
            self.execute_btn.setEnabled(False)
            btn_layout.addWidget(self.execute_btn)
            
            self.favorite_btn = QtWidgets.QPushButton("⭐ 즐겨찾기")
            self.favorite_btn.clicked.connect(self.on_favorite_clicked)
            self.favorite_btn.setEnabled(False)
            btn_layout.addWidget(self.favorite_btn)
            
            exec_layout.addLayout(btn_layout)
            
            layout.addWidget(exec_group)
            
            # 프리셋 명령어 그룹
            preset_group = self.create_preset_group()
            layout.addWidget(preset_group)
            
            # 빈 공간
            layout.addStretch()
            
            return widget
        
        def create_preset_group(self):
            """프리셋 명령어 그룹 생성"""
            group = QtWidgets.QGroupBox("⚡ 빠른 실행")
            layout = QtWidgets.QGridLayout(group)
            
            presets = [
                ("🧹 지우기", "stat none"),
                ("📊 FPS", "stat fps"),
                ("📈 메모리", "stat memory"),
                ("⚡ 렌더링", "stat rhi"),
                ("📱 유닛", "stat unit"),
                ("🎮 게임", "stat game"),
                ("🌊 스트리밍", "stat streaming"),
                ("🔧 엔진", "stat engine"),
                ("🎨 GPU", "stat gpu"),
                ("🎬 씬", "stat scene"),
            ]
            
            # 콘솔 메시지 토글 (특별 처리)
            self.console_messages_enabled = True  # 기본값은 활성화
            self.console_toggle_btn = QtWidgets.QPushButton("📺 콘솔 메시지 ON")
            self.console_toggle_btn.setToolTip("콘솔 명령어 결과 메시지 표시/숨김 토글")
            self.console_toggle_btn.clicked.connect(self.toggle_console_messages)
            layout.addWidget(self.console_toggle_btn, (len(presets) + 1) // 2, 0, 1, 2)  # 전체 너비로 배치
            
            # 언어 토글 (특별 처리)
            self.current_language = "ko"  # 기본값은 한국어
            self.language_toggle_btn = QtWidgets.QPushButton("🌐 한국어")
            self.language_toggle_btn.setToolTip("언리얼 에디터 언어 전환 (한국어/영어)")
            self.language_toggle_btn.clicked.connect(self.toggle_language)
            layout.addWidget(self.language_toggle_btn, (len(presets) + 1) // 2 + 1, 0, 1, 2)  # 전체 너비로 배치
            
            for i, (name, cmd) in enumerate(presets):
                btn = QtWidgets.QPushButton(name)
                btn.setToolTip(f"명령어: {cmd}")  # 툴팁으로 영어 명령어 표시
                btn.clicked.connect(lambda checked, c=cmd: self.execute_preset(c))
                layout.addWidget(btn, i // 2, i % 2)  # 2열로 변경
            
            return group
        
        def setup_styles(self):
            """스타일 설정 - 어두운 테마"""
            style = """
            QMainWindow {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QWidget {
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4A4A4A;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #353535;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #FFFFFF;
                background-color: #353535;
            }
            QPushButton {
                border: 1px solid #4A4A4A;
                border-radius: 3px;
                padding: 4px 8px;
                background-color: #404040;
                color: #FFFFFF;
                font-size: 9pt;
                font-weight: 500;
                min-height: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #6A6A6A;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
                border-color: #333333;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #666666;
                border-color: #333333;
            }
            QLineEdit {
                border: 1px solid #4A4A4A;
                border-radius: 3px;
                padding: 4px;
                background-color: #404040;
                color: #FFFFFF;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border-color: #6A9BD1;
                background-color: #454545;
            }
            QTextEdit {
                border: 1px solid #4A4A4A;
                border-radius: 3px;
                padding: 4px;
                background-color: #404040;
                color: #FFFFFF;
                font-size: 9pt;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 9pt;
            }
            QTabWidget::pane {
                border: 2px solid #4A4A4A;
                background-color: #353535;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #FFFFFF;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 2px solid #4A4A4A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #353535;
                border-color: #6A9BD1;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
            QScrollArea {
                border: 2px solid #4A4A4A;
                border-radius: 4px;
                background-color: #353535;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 16px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #6A6A6A;
                border-radius: 8px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #8A8A8A;
            }
            QStatusBar {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border-top: 1px solid #4A4A4A;
            }
            QToolTip {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 2px solid #4A4A4A;
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }
            QSplitter::handle {
                background: transparent;
                width: 0px;
                height: 0px;
            }
            QSplitter::handle:horizontal {
                width: 0px;
            }
            QSplitter::handle:vertical {
                height: 0px;
            }
            """
            self.setStyleSheet(style)
        
        def on_search_changed(self, text):
            """검색어 변경"""
            # 현재는 단순 구현, 향후 실시간 필터링 구현 가능
            pass
        
        def on_command_button_clicked(self, cmd):
            """명령어 버튼 클릭"""
            self.current_command = cmd
            self.display_command_info(cmd)
        
        def display_command_info(self, cmd):
            """명령어 정보 표시"""
            command = cmd.get('command', '')
            scope = cmd.get('scope', '')
            help_kr = cmd.get('help_kr', '설명 없음')
            
            self.cmd_label.setText(command)
            self.scope_label.setText(f"카테고리: {scope}")
            self.desc_kr.setText(help_kr)
            
            self.execute_btn.setEnabled(True)
            self.favorite_btn.setEnabled(True)
            
            # 즐겨찾기 버튼 업데이트
            if command in self.data_manager.favorites:
                self.favorite_btn.setText("⭐ 즐겨찾기 해제")
            else:
                self.favorite_btn.setText("☆ 즐겨찾기 추가")
        
        def on_execute_clicked(self):
            """실행 버튼 클릭"""
            if not self.current_command:
                return
            
            command = self.current_command.get('command')
            args = self.args_input.text().strip()
            
            success = self.data_manager.execute_command(command, args)
            
            if success:
                self.statusBar().showMessage(f"✅ 실행됨: {command} {args}", 3000)
                self.args_input.clear()
            else:
                self.statusBar().showMessage("❌ 실행 실패", 3000)
        
        def on_favorite_clicked(self):
            """즐겨찾기 버튼 클릭"""
            if not self.current_command:
                return
            
            command = self.current_command.get('command')
            
            if command in self.data_manager.favorites:
                self.data_manager.favorites.remove(command)
                self.favorite_btn.setText("☆ 즐겨찾기 추가")
                self.statusBar().showMessage("즐겨찾기에서 제거됨", 2000)
            else:
                self.data_manager.favorites.append(command)
                self.favorite_btn.setText("⭐ 즐겨찾기 해제")
                self.statusBar().showMessage("즐겨찾기에 추가됨", 2000)
            
            self.data_manager.save_favorites()
            
            # 즉시 UI 업데이트
            self.refresh_all_tabs()
            self.refresh_button_styles()
        
        def on_tab_changed(self, index):
            """탭 변경 시 버튼 스타일 새로고침"""
            self.refresh_button_styles()
        
        def execute_preset(self, command):
            """프리셋 명령어 실행"""
            success = self.data_manager.execute_command(command)
            
            if success:
                self.statusBar().showMessage(f"✅ 실행됨: {command}", 3000)
            else:
                self.statusBar().showMessage("❌ 실행 실패", 3000)
        
        def toggle_console_messages(self):
            """콘솔 메시지 표시/숨김 토글"""
            if self.console_messages_enabled:
                # 콘솔 메시지 비활성화
                command = "DISABLEALLSCREENMESSAGES"
                self.console_messages_enabled = False
                self.console_toggle_btn.setText("📺 콘솔 메시지 OFF")
                self.console_toggle_btn.setStyleSheet("background-color: #8B4513; color: white;")  # 갈색 배경
            else:
                # 콘솔 메시지 활성화
                command = "ENABLEALLSCREENMESSAGES"
                self.console_messages_enabled = True
                self.console_toggle_btn.setText("📺 콘솔 메시지 ON")
                self.console_toggle_btn.setStyleSheet("")  # 기본 스타일로 복원
            
            success = self.data_manager.execute_command(command)
            
            if success:
                status = "활성화" if self.console_messages_enabled else "비활성화"
                self.statusBar().showMessage(f"✅ 콘솔 메시지 {status}", 3000)
            else:
                self.statusBar().showMessage("❌ 콘솔 메시지 토글 실패", 3000)
        
        def toggle_language(self):
            """언리얼 에디터 언어 토글 (한국어/영어)"""
            if self.current_language == "ko":
                # 영어로 전환
                command = "culture=en.us"
                self.current_language = "en"
                self.language_toggle_btn.setText("🌐 English")
                self.language_toggle_btn.setStyleSheet("background-color: #4169E1; color: white;")  # 파란색 배경
            else:
                # 한국어로 전환
                command = "culture=ko.kr"
                self.current_language = "ko"
                self.language_toggle_btn.setText("🌐 한국어")
                self.language_toggle_btn.setStyleSheet("")  # 기본 스타일로 복원
            
            success = self.data_manager.execute_command(command)
            
            if success:
                language_name = "영어" if self.current_language == "en" else "한국어"
                self.statusBar().showMessage(f"✅ 언어 전환: {language_name} (재시작 필요)", 5000)
            else:
                self.statusBar().showMessage("❌ 언어 전환 실패", 3000)


# ============================================================================
# 메인 함수
# ============================================================================

def main():
    """Console Cat 실행"""
    if not PYSIDE_AVAILABLE:
        print("❌ PySide6가 필요합니다.")
        print("설치: pip install PySide6")
        return None
    
    # Qt 애플리케이션
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    
    # 기존 Console Cat 윈도우 닫기 (qt_simple_example.py와 동일한 방식)
    for win in QtWidgets.QApplication.topLevelWidgets():
        if win.objectName() == 'ConsoleCatMainWindow':
            win.close()
    
    # 메인 윈도우 생성 및 표시
    window = ConsoleCatMainWindow()
    window.setObjectName('ConsoleCatMainWindow')
    window.show()
    
    # Unreal Slate에 부모 지정 (qt_simple_example.py와 동일)
    try:
        unreal.parent_external_window_to_slate(window.winId())
        print("✅ Console Cat 메인 윈도우가 언리얼 슬레이트에 연결됨")
    except Exception as e:
        print(f"⚠️ 메인 함수에서 슬레이트 연결 실패: {e}")
    
    print("🐱 Console Cat이 시작되었습니다!")
    return window


# 편의 함수들
show = main
run = main

if __name__ == "__main__":
    main()
