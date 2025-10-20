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
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        PYSIDE_AVAILABLE = True
    except ImportError:
        print("ERROR: PySide6 or PySide2 is required.")
        print("Recommended: pip install PySide6")
        print("Alternative: pip install PySide2")
        PYSIDE_AVAILABLE = False

import unreal
import json
import sys
import os
import subprocess
from pathlib import Path

# 같은 패키지의 데이터 생성 모듈 import
try:
    from . import generate_console_command_list
except ImportError:
    try:
        import generate_console_command_list
    except ImportError:
        generate_console_command_list = None


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
                
            except Exception as e:
                print(f"❌ {json_file} 로드 실패: {e}")
        
        if self.all_commands:
            print(f"Console Cat: {len(self.all_commands)}개 명령어 로드 완료")
    
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
            # 언리얼 엔진 콘솔 명령어 실행
            try:
                # 방법 1: EditorSubsystem을 통한 실행 (가장 안전한 방법)
                editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
                if editor_subsystem:
                    world = editor_subsystem.get_editor_world()
                    if world:
                        unreal.SystemLibrary.execute_console_command(world, full_command)
                        return True
            except:
                pass
            
            try:
                # 방법 2: 현재 월드 가져오기
                world = unreal.EditorLevelLibrary.get_editor_world()
                if world:
                    unreal.SystemLibrary.execute_console_command(world, full_command)
                    return True
            except:
                pass
            
            try:
                # 방법 3: 게임 인스턴스를 통한 실행
                game_instance = unreal.GameplayStatics.get_game_instance(unreal.EditorLevelLibrary.get_editor_world())
                if game_instance:
                    world = game_instance.get_world()
                    if world:
                        unreal.SystemLibrary.execute_console_command(world, full_command)
                        return True
            except:
                pass
            
            # 모든 방법이 실패한 경우
            return False
            
        except Exception as e:
            print(f"❌ 명령어 실행 실패: {e}")
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
            splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
            
            # 왼쪽: 카테고리 및 명령어 버튼들 (유동적 크기)
            left_widget = self.create_left_panel()
            left_widget.setMinimumWidth(200)  # 최소 크기만 설정
            splitter.addWidget(left_widget)
            
            # 오른쪽: 상세 정보 및 제어 (고정 크기)
            right_widget = self.create_right_panel()
            right_widget.setMinimumWidth(220)
            right_widget.setMaximumWidth(220)  # 오른쪽만 고정
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
            
            # 초기 탭 상태 올바르게 설정 (즐겨찾기 버튼 상태 반영)
            QtCore.QTimer.singleShot(50, self.refresh_current_tab)
        
        def setup_unreal_parenting(self):
            """언리얼 슬레이트에 윈도우 부모 지정"""
            try:
                unreal.parent_external_window_to_slate(self.winId())
            except Exception as e:
                # 실패해도 계속 실행
                pass
        
        def refresh_button_styles(self):
            """버튼 스타일 새로고침 (현재 탭만)"""
            current_widget = self.category_tabs.currentWidget()
            if current_widget:
                # 현재 탭의 모든 버튼 찾기
                buttons = current_widget.findChildren(QtWidgets.QPushButton)
                for btn in buttons:
                    # 메인 명령어 버튼인지 확인 (크기로 판단)
                    if btn.size().width() > 100:  # 메인 버튼
                        command = btn.text()
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
            
            # 즐겨찾기 필터 토글
            filter_layout = QtWidgets.QHBoxLayout()
            self.favorites_filter = QtWidgets.QCheckBox("⭐ 즐겨찾기만 보기")
            self.favorites_filter.toggled.connect(self.on_favorites_filter_changed)
            filter_layout.addWidget(self.favorites_filter)
            filter_layout.addStretch()
            layout.addLayout(filter_layout)
            
            # 카테고리 탭 (즐겨찾기 탭 제거)
            self.category_tabs = QtWidgets.QTabWidget()
            
            # 전체 탭
            all_tab = self.create_commands_tab(self.data_manager.all_commands, "all")
            self.category_tabs.addTab(all_tab, "� 전체")
            
            # 스코프별 탭
            for scope in sorted(self.data_manager.commands.keys()):
                commands = self.data_manager.commands[scope]
                tab = self.create_commands_tab(commands, scope)
                self.category_tabs.addTab(tab, f"📂 {scope}")
            
            # 탭 변경 시 이벤트
            self.category_tabs.currentChanged.connect(self.on_tab_changed)
            
            layout.addWidget(self.category_tabs)
            
            return widget
        
        def create_commands_tab(self, commands, scope="all"):
            """명령어 탭 생성"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            
            # 스크롤 영역
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # 버튼 컨테이너 (1열 레이아웃)
            button_widget = QtWidgets.QWidget()
            button_layout = QtWidgets.QVBoxLayout(button_widget)
            button_layout.setSpacing(1)
            
            # scope 정보를 프로퍼티로 저장
            button_widget.setProperty("scope", scope)
            
            # 명령어 버튼들 생성 (1열)
            self.update_tab_commands(button_layout, commands)
            
            scroll.setWidget(button_widget)
            layout.addWidget(scroll)
            
            return widget
        
        def is_widget_valid(self, widget):
            """Qt 위젯이 유효한지 검사"""
            if widget is None:
                return False
            try:
                # C++ 객체에 접근해서 유효성 검사
                widget.objectName()
                return True
            except RuntimeError:
                # C++ 객체가 이미 삭제됨
                return False
        
        def replace_tab_content(self, scroll_area, commands):
            """탭 내용을 완전히 새로 생성해서 교체 (안전한 방식)"""
            try:
                # 즐겨찾기 필터 적용
                if hasattr(self, 'favorites_filter') and self.favorites_filter.isChecked():
                    filtered_commands = [cmd for cmd in commands if cmd.get('command') in self.data_manager.favorites]
                    commands = filtered_commands
                
                # 새로운 버튼 위젯 생성
                new_button_widget = QtWidgets.QWidget()
                new_button_layout = QtWidgets.QVBoxLayout(new_button_widget)
                new_button_layout.setSpacing(1)
                
                # 명령어 버튼들 생성
                for cmd in commands:
                    try:
                        btn_layout = self.create_command_button_with_favorite(cmd)
                        new_button_layout.addLayout(btn_layout)
                    except Exception as e:
                        print(f"   ⚠️ 버튼 생성 실패: {cmd.get('command', 'Unknown')} - {e}")
                        continue
                
                # 빈 공간 채우기
                new_button_layout.addStretch()
                
                # 기존 위젯을 안전하게 교체
                try:
                    old_widget = scroll_area.widget()
                    scroll_area.setWidget(new_button_widget)
                    
                    # 기존 위젯이 유효한 경우에만 정리
                    if self.is_widget_valid(old_widget):
                        try:
                            old_widget.setParent(None)
                            old_widget.deleteLater()
                        except RuntimeError:
                            # 삭제 중 오류 발생 시 무시
                            pass
                except Exception as e:
                    # 위젯 교체 중 오류 발생 시 무시하고 진행
                    pass
                
            except Exception as e:
                print(f"   ❌ 탭 내용 교체 실패: {e}")
                import traceback
                traceback.print_exc()
        
        def update_tab_commands(self, layout, commands):
            """탭의 명령어 버튼들 업데이트"""
            try:
                # 기존 모든 아이템 제거 (위젯, 레이아웃, 스트레치 포함)
                self.clear_layout_completely(layout)
                
                # 즐겨찾기 필터 적용
                if hasattr(self, 'favorites_filter') and self.favorites_filter.isChecked():
                    filtered_commands = [cmd for cmd in commands if cmd.get('command') in self.data_manager.favorites]
                    commands = filtered_commands
                
                # 명령어 버튼들 생성
                for cmd in commands:
                    try:
                        btn_layout = self.create_command_button_with_favorite(cmd)
                        layout.addLayout(btn_layout)
                    except Exception as e:
                        # 버튼 생성 실패 시 건너뛰기
                        continue
                
                # 빈 공간 채우기
                layout.addStretch()
                
                # 즉시 업데이트 적용
                layout.update()
                
            except Exception as e:
                # 탭 명령어 업데이트 실패 시 무시
                pass
                import traceback
                traceback.print_exc()
        
        def clear_layout_completely(self, layout):
            """레이아웃 완전히 정리 (스트레치 포함)"""
            try:
                # 안전한 방식으로 모든 아이템 제거
                while layout.count():
                    item = layout.takeAt(0)
                    if item is None:
                        break
                    
                    try:
                        # 위젯인 경우
                        widget = item.widget()
                        if widget is not None:
                            widget.setParent(None)
                            widget.deleteLater()
                            continue
                        
                        # 중첩 레이아웃인 경우
                        child_layout = item.layout()
                        if child_layout is not None:
                            self.clear_layout_completely(child_layout)
                            child_layout.setParent(None)
                            child_layout.deleteLater()
                            continue
                        
                        # 스페이서인 경우
                        spacer = item.spacerItem()
                        if spacer is not None:
                            # 스페이서는 takeAt에서 이미 제거됨
                            del spacer
                            continue
                            
                    except (RuntimeError, AttributeError) as e:
                        # C++ 객체가 이미 삭제된 경우 등 무시
                        continue
                        
            except Exception as e:
                # 레이아웃 정리 중 오류 발생 시 간단한 방식으로 폴백
                self.simple_clear_layout(layout)
        
        def simple_clear_layout(self, layout):
            """간단한 레이아웃 정리 (폴백)"""
            try:
                # 가장 간단한 방식
                for i in reversed(range(layout.count())):
                    try:
                        item = layout.itemAt(i)
                        if item and item.widget():
                            item.widget().deleteLater()
                        layout.removeItem(item)
                    except:
                        pass
            except:
                pass
        
        def create_command_button_with_favorite(self, cmd):
            """명령어 버튼 + 즐겨찾기 버튼 생성"""
            command = cmd.get('command', '')
            help_kr = cmd.get('help_kr', '')
            scope = cmd.get('scope', '')
            
            # 수평 레이아웃
            btn_layout = QtWidgets.QHBoxLayout()
            btn_layout.setSpacing(1)  # 버튼 간 간격 줄임
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            # 메인 명령어 버튼
            main_btn = QtWidgets.QPushButton(command)
            main_btn.setFixedHeight(28)
            main_btn.setMinimumWidth(100)
            
            # 툴팁에 상세 정보
            tooltip = f"🔧 명령어: {command}\n📂 카테고리: {scope}\n📖 설명: {help_kr}"
            main_btn.setToolTip(tooltip)
            
            # 클릭 이벤트
            main_btn.clicked.connect(lambda checked, c=cmd: self.on_command_button_clicked(c))
            
            # 즐겨찾기 버튼
            fav_btn = QtWidgets.QPushButton()
            fav_btn.setFixedSize(32, 28)  # 약간 더 넓게
            fav_btn.setToolTip("즐겨찾기 추가/제거")
            
            # 즐겨찾기 상태에 따른 아이콘 설정
            is_favorite = command in self.data_manager.favorites
            fav_btn.setText("⭐" if is_favorite else "☆")
            
            # 즐겨찾기 버튼 스타일 (원래 버튼과 일체감)
            if is_favorite:
                fav_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFB347;
                        border: 1px solid #FF8C00;
                        color: #000000;
                        font-weight: bold;
                        border-radius: 3px;
                        padding: 2px;
                        font-size: 14pt;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #FFA500;
                        border-color: #FF7F00;
                    }
                    QPushButton:pressed {
                        background-color: #FF8C00;
                        border-color: #FF6347;
                    }
                """)
            else:
                fav_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4A4A4A;
                        border: 1px solid #666666;
                        color: #CCCCCC;
                        border-radius: 3px;
                        padding: 2px;
                        font-size: 14pt;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #5A5A5A;
                        border-color: #777777;
                        color: #FFFFFF;
                    }
                    QPushButton:pressed {
                        background-color: #3A3A3A;
                        border-color: #555555;
                    }
                """)
            
            # 즐겨찾기 토글 이벤트
            fav_btn.clicked.connect(lambda checked, c=command: self.toggle_favorite(c))
            
            # 레이아웃에 추가
            btn_layout.addWidget(main_btn)
            btn_layout.addWidget(fav_btn)
            
            # 즐겨찾기 상태에 따른 스타일 적용
            self.apply_button_style(main_btn, command)
            
            return btn_layout
            
            # 즐겨찾기 스타일 적용
            self.apply_button_style(btn, command)
            
            return btn
        
        def create_right_panel(self):
            """오른쪽 패널 생성 (상세 정보)"""
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            layout.setSpacing(6)  # 그룹 간 간격 줄임
            layout.setContentsMargins(4, 4, 4, 4)  # 외부 여백 줄임
            
            # 명령어 정보 그룹
            info_group = QtWidgets.QGroupBox("📋 명령어 정보")
            info_layout = QtWidgets.QVBoxLayout(info_group)
            info_layout.setSpacing(4)  # 간격 줄임
            info_layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임
            
            # 명령어 이름
            self.cmd_label = QtWidgets.QLabel("명령어를 선택하세요")
            self.cmd_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #2E86AB;")  # 폰트 크기 줄임
            info_layout.addWidget(self.cmd_label)
            
            # 스코프
            self.scope_label = QtWidgets.QLabel("")
            self.scope_label.setStyleSheet("color: #666666; font-size: 9pt;")  # 폰트 크기 추가
            info_layout.addWidget(self.scope_label)
            
            # 설명
            info_layout.addWidget(QtWidgets.QLabel("📖 설명:"))
            self.desc_kr = QtWidgets.QTextEdit()
            self.desc_kr.setReadOnly(True)
            self.desc_kr.setMaximumHeight(65)  # 높이 줄임
            self.desc_kr.setMinimumHeight(65)  # 최소 높이 설정
            info_layout.addWidget(self.desc_kr)
            
            layout.addWidget(info_group)
            
            # 실행 그룹
            exec_group = QtWidgets.QGroupBox("🚀 실행")
            exec_layout = QtWidgets.QVBoxLayout(exec_group)
            exec_layout.setSpacing(4)  # 간격 줄임
            exec_layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임
            
            # 인자 입력
            exec_layout.addWidget(QtWidgets.QLabel("매개변수 (선택사항):"))
            self.args_input = QtWidgets.QLineEdit()
            self.args_input.setPlaceholderText("예: 1920x1080w")
            exec_layout.addWidget(self.args_input)
            
            # 실행 버튼
            self.execute_btn = QtWidgets.QPushButton("▶️ 실행")
            self.execute_btn.clicked.connect(self.on_execute_clicked)
            self.execute_btn.setEnabled(False)
            exec_layout.addWidget(self.execute_btn)
            
            layout.addWidget(exec_group)
            
            # 데이터 관리 그룹 추가
            data_group = self.create_data_management_group()
            layout.addWidget(data_group)
            
            # 프리셋 명령어 그룹
            preset_group = self.create_preset_group()
            layout.addWidget(preset_group)
            
            # 약간의 여백만 추가 (빈 공간 최소화)
            layout.addStretch(1)
            
            return widget
        
        def create_data_management_group(self):
            """데이터 관리 그룹 생성"""
            group = QtWidgets.QGroupBox("🗂️ 데이터 관리")
            layout = QtWidgets.QVBoxLayout(group)
            layout.setSpacing(4)  # 간격 줄임
            layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임
            
            # 데이터 파일 생성 버튼
            generate_btn = QtWidgets.QPushButton("🔧 데이터 파일 생성")
            generate_btn.setToolTip("generate_console_command_list.py를 실행하여 콘솔 명령어 데이터 파일을 생성합니다")
            generate_btn.clicked.connect(self.on_generate_data_clicked)
            layout.addWidget(generate_btn)
            
            # 데이터 파일 편집 버튼
            edit_btn = QtWidgets.QPushButton("📝 데이터 폴더 열기")
            edit_btn.setToolTip("콘솔 명령어 데이터 파일이 저장된 폴더를 엽니다")
            edit_btn.clicked.connect(self.on_edit_data_clicked)
            layout.addWidget(edit_btn)
            
            # 데이터 새로고침 버튼
            refresh_btn = QtWidgets.QPushButton("🔄 데이터 새로고침")
            refresh_btn.setToolTip("수정된 데이터 파일을 다시 불러옵니다")
            refresh_btn.clicked.connect(self.on_refresh_data_clicked)
            layout.addWidget(refresh_btn)
            
            return group
        
        def create_preset_group(self):
            """프리셋 명령어 그룹 생성"""
            group = QtWidgets.QGroupBox("⚡ 빠른 실행")
            layout = QtWidgets.QGridLayout(group)
            layout.setSpacing(3)  # 간격 줄임
            layout.setContentsMargins(8, 8, 8, 8)  # 여백 줄임
            
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
        
        def toggle_favorite(self, command):
            """즐겨찾기 토글 (명령어별 즐겨찾기 버튼용)"""
            if command in self.data_manager.favorites:
                self.data_manager.favorites.remove(command)
                self.statusBar().showMessage("즐겨찾기에서 제거됨", 2000)
            else:
                self.data_manager.favorites.append(command)
                self.statusBar().showMessage("즐겨찾기에 추가됨", 2000)
            
            self.data_manager.save_favorites()
            
            # 항상 현재 탭 새로고침 (즐겨찾기 버튼 아이콘 즉시 반영)
            self.refresh_current_tab()
        
        def on_favorites_filter_changed(self, checked):
            """즐겨찾기 필터 토글"""
            try:
                # 현재 탭만 새로고침
                self.refresh_current_tab()
            except Exception as e:
                # 즐겨찾기 필터 변경 중 오류 발생 시 무시
                pass
        
        def refresh_current_tab(self):
            """현재 탭만 새로고침"""
            try:
                current_index = self.category_tabs.currentIndex()
                current_widget = self.category_tabs.currentWidget()
                
                if not current_widget:
                    return
                
                # 스크롤 영역 찾기
                scroll_area = current_widget.findChild(QtWidgets.QScrollArea)
                if not scroll_area:
                    return
                
                button_widget = scroll_area.widget()
                if not button_widget:
                    return
                
                button_layout = button_widget.layout()
                if not button_layout:
                    return
                
                # 현재 탭에 해당하는 명령어들 가져오기
                tab_text = self.category_tabs.tabText(current_index)
                if current_index == 0:  # 전체 탭
                    commands = self.data_manager.all_commands
                    scope = "전체"
                else:
                    # 스코프별 탭
                    scope = tab_text.replace("📂 ", "")
                    commands = self.data_manager.get_scope_commands(scope)
                
                # 버튼들 업데이트 (새로운 방식: 위젯 교체)
                self.replace_tab_content(scroll_area, commands)
                
                # 강제 UI 업데이트 (안전하게)
                try:
                    if self.is_widget_valid(current_widget):
                        current_widget.update()
                    if self.is_widget_valid(scroll_area):
                        scroll_area.update()
                except RuntimeError:
                    # 위젯이 이미 삭제된 경우 무시
                    pass
                    
            except Exception as e:
                # 탭 새로고침 중 오류 발생 시 무시
                pass
        
        def refresh_favorite_buttons(self):
            """즐겨찾기 버튼들만 업데이트"""
            current_widget = self.category_tabs.currentWidget()
            if not current_widget:
                return
            
            # 모든 즐겨찾기 버튼 찾기
            fav_buttons = current_widget.findChildren(QtWidgets.QPushButton)
            for btn in fav_buttons:
                # 즐겨찾기 버튼인지 확인 (크기로 판단)
                if btn.size().width() == 32 and btn.size().height() == 28:
                    # 해당 버튼의 부모 위젯에서 명령어 찾기
                    parent_widget = btn.parent()
                    if parent_widget:
                        # 형제 위젯들 중에서 메인 버튼 찾기
                        siblings = parent_widget.findChildren(QtWidgets.QPushButton)
                        for sibling in siblings:
                            if sibling != btn and sibling.size().width() > 100:  # 메인 버튼
                                command = sibling.text()
                                is_favorite = command in self.data_manager.favorites
                                btn.setText("⭐" if is_favorite else "☆")
                                # 메인 버튼 스타일도 업데이트
                                self.apply_button_style(sibling, command)
                                break
        
        def refresh_all_tabs(self):
            """모든 탭 새로고침 (기존 함수 수정)"""
            current_tab = self.category_tabs.currentIndex()
            
            # 각 탭 새로고침 (탭을 다시 만들지 않고 내용만 업데이트)
            for i in range(self.category_tabs.count()):
                tab_widget = self.category_tabs.widget(i)
                if not tab_widget:
                    continue
                
                scroll_area = tab_widget.findChild(QtWidgets.QScrollArea)
                if not scroll_area:
                    continue
                
                button_widget = scroll_area.widget()
                if not button_widget:
                    continue
                
                button_layout = button_widget.layout()
                if not button_layout:
                    continue
                
                # 탭에 해당하는 명령어들 가져오기
                if i == 0:  # 전체 탭
                    commands = self.data_manager.all_commands
                else:
                    # 스코프별 탭
                    tab_text = self.category_tabs.tabText(i)
                    scope = tab_text.replace("📂 ", "")
                    commands = self.data_manager.get_scope_commands(scope)
                
                # 임시로 탭을 변경해서 업데이트
                self.category_tabs.setCurrentIndex(i)
                self.update_tab_commands(button_layout, commands)
            
            # 원래 탭으로 복원
            self.category_tabs.setCurrentIndex(current_tab)
        
        def on_tab_changed(self, index):
            """탭 변경 시 이벤트"""
            # 원래 탭 인덱스 저장
            self._original_tab_index = index
            
            # 탭 변경 시 항상 해당 탭 새로고침 (즐겨찾기 버튼 상태 정확히 반영)
            # 새로운 탭으로 변경될 때 기존 탭의 내용을 올바르게 로드
            # 탭 변경 시 동작
            
            # 약간의 지연 후 새로고침 (탭 변경이 완전히 완료된 후)
            QtCore.QTimer.singleShot(10, self.refresh_current_tab)
        
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
        
        def on_generate_data_clicked(self):
            """데이터 파일 생성 버튼 클릭"""
            try:
                if generate_console_command_list is None:
                    self.statusBar().showMessage("❌ generate_console_command_list.py를 찾을 수 없습니다", 5000)
                    return
                
                self.statusBar().showMessage("🔧 데이터 파일 생성 중...", 2000)
                
                # 백그라운드에서 실행 (UI 블록 방지)
                QtCore.QTimer.singleShot(100, self.run_generator_file)
                
            except Exception as e:
                self.statusBar().showMessage(f"❌ 데이터 파일 생성 실패: {e}", 5000)
        
        def run_generator_file(self):
            """generate_console_command_list.py 실행"""
            try:
                if generate_console_command_list is None:
                    self.statusBar().showMessage("❌ generate_console_command_list.py를 찾을 수 없습니다", 5000)
                    return
                
                # main 함수 실행
                if hasattr(generate_console_command_list, 'main'):
                    generate_console_command_list.main()
                    self.statusBar().showMessage("✅ 데이터 파일 생성 완료", 3000)
                    # 2초 후 데이터 새로고침
                    QtCore.QTimer.singleShot(2000, self.on_refresh_data_clicked)
                else:
                    self.statusBar().showMessage("❌ generate_console_command_list에 main 함수가 없습니다", 5000)
                
            except Exception as e:
                self.statusBar().showMessage(f"❌ 데이터 생성 중 오류: {e}", 5000)
        
        def on_edit_data_clicked(self):
            """데이터 폴더 열기 버튼 클릭"""
            try:
                import subprocess
                import os
                
                if DATA_DIR.exists():
                    # Windows에서 폴더 열기
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(['explorer', str(DATA_DIR)])
                    else:  # macOS, Linux
                        subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(DATA_DIR)])
                    
                    self.statusBar().showMessage(f"📁 데이터 폴더 열기: {DATA_DIR}", 3000)
                else:
                    self.statusBar().showMessage("❌ 데이터 폴더가 존재하지 않습니다. 먼저 데이터 파일을 생성하세요.", 5000)
                    
            except Exception as e:
                self.statusBar().showMessage(f"❌ 폴더 열기 실패: {e}", 5000)
        
        def on_refresh_data_clicked(self):
            """데이터 새로고침 버튼 클릭"""
            try:
                self.statusBar().showMessage("🔄 데이터 새로고침 중...", 1000)
                
                # 데이터 다시 로드
                old_count = len(self.data_manager.all_commands)
                self.data_manager.load_data()
                new_count = len(self.data_manager.all_commands)
                
                if new_count > 0:
                    # 모든 탭 새로고침
                    self.refresh_all_tabs_after_data_reload()
                    
                    # 상태바 업데이트
                    self.statusBar().showMessage(f"✅ 데이터 새로고침 완료: {new_count}개 명령어 ({new_count - old_count:+d})", 5000)
                else:
                    self.statusBar().showMessage("⚠️ 데이터 파일이 없습니다. 먼저 데이터 파일을 생성하세요.", 5000)
                    
            except Exception as e:
                self.statusBar().showMessage(f"❌ 데이터 새로고침 실패: {e}", 5000)
        
        def refresh_all_tabs_after_data_reload(self):
            """데이터 새로고침 후 모든 탭 다시 생성"""
            try:
                current_tab_index = self.category_tabs.currentIndex()
                
                # 모든 탭 제거
                self.category_tabs.clear()
                
                # 탭 다시 생성
                # 전체 탭
                all_tab = self.create_commands_tab(self.data_manager.all_commands, "all")
                self.category_tabs.addTab(all_tab, "📋 전체")
                
                # 스코프별 탭
                for scope in sorted(self.data_manager.commands.keys()):
                    commands = self.data_manager.commands[scope]
                    tab = self.create_commands_tab(commands, scope)
                    self.category_tabs.addTab(tab, f"📂 {scope}")
                
                # 원래 탭 인덱스로 복원 (가능한 경우)
                if current_tab_index < self.category_tabs.count():
                    self.category_tabs.setCurrentIndex(current_tab_index)
                
                # 현재 탭 새로고침
                QtCore.QTimer.singleShot(50, self.refresh_current_tab)
                
            except Exception as e:
                pass  # 오류 무시


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
        # 슬레이트 연결 성공
        pass
    except Exception as e:
        # 슬레이트 연결 실패 시 무시
        pass
    
    print("Console Cat이 시작되었습니다!")
    return window


# 편의 함수들
show = main
run = main

if __name__ == "__main__":
    main()
