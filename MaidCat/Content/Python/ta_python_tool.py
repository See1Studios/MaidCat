#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool
TAPython MenuConfig.json을 간단하게 편집할 수 있는 툴
"""

import json
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any

try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False

try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False

# 중복 초기화 방지
_logger_initialized = False

# 로깅 설정 개선 (리소스 관리)
def setup_logging():
    """로깅 설정 함수"""
    global _logger_initialized
    
    if _logger_initialized:
        return logging.getLogger(__name__), getattr(setup_logging, '_file_handler', None)
    
    # 기존 핸들러 정리
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    # 새로운 로거 설정 (propagate 방지)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)  # INFO 로그를 숨기고 WARNING 이상만 표시
    logger.propagate = False  # 부모 로거로 전파 방지
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 콘솔에는 WARNING 이상만 표시
    
    # 파일 핸들러 (스크립트 디렉토리에 저장)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(script_dir, 'ta_python_tool.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        setup_logging._file_handler = file_handler  # 함수 속성으로 저장
    except Exception:
        # 파일 생성 실패시 콘솔만 사용
        file_handler = None
        setup_logging._file_handler = None
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    if file_handler:
        file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    if file_handler:
        logger.addHandler(file_handler)
    
    _logger_initialized = True
    return logger, file_handler

logger, file_handler = setup_logging()


class ToolTip:
    """간단한 툴팁 클래스"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, 
                        background="lightyellow", relief="solid", borderwidth=1,
                        font=("Arial", 8))
        label.pack()
    
    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class TAPythonTool:
    """
    TAPython MenuConfig.json 편집기
    
    주요 기능:
    - 계층적 메뉴 구조 지원 (서브메뉴)
    - 트리뷰를 통한 직관적인 메뉴 구조 표시
    - 실시간 편집 및 저장
    - 다양한 메뉴 카테고리 지원
    
    메서드 구조:
    - __init__: 초기화 및 UI 설정
    - UI 관련: setup_ui, create_tab_content, update_status
    - 파일 관리: load_config_file, save_config, open_config
    - 데이터 관리: refresh_tab, on_item_select, update_item
    - 아이템 관리: add_item, add_submenu, delete_item, move_item_*
    - 헬퍼 메서드: _get_item_data_from_tree, _find_parent_by_name 등
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TA Python Tool")
        self.root.geometry("1000x700")
        
        # 초기 이벤트 큐 정리
        self.root.update_idletasks()
        self.root.update()
        
        # 창 닫기 이벤트 핸들러 설정
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 리소스 정리 상태 추적
        self._resources_cleaned = False
        
        self.config_data = {}
        self.config_file_path = ""
        self.has_unsaved_changes = False  # 저장하지 않은 변경사항 추적
        
        # 기본 경로 설정 - unreal.Paths 사용
        self.default_config_path = self._find_default_config_path()
        
        self.setup_ui()
        self.load_default_config()
    

    # === 유틸리티 메서드들 ===
    def _show_error(self, title, message, log_level="error"):
        """에러 메시지 표시 및 로깅"""
        if log_level == "error":
            logger.error(message)
        elif log_level == "warning":
            logger.warning(message)
        messagebox.showerror(title, message)
    
    def _show_warning(self, title, message):
        """경고 메시지 표시 및 로깅"""
        logger.warning(message)
        messagebox.showwarning(title, message)
    
    def _validate_config_data(self, category_id):
        """설정 데이터 검증 및 초기화"""
        if category_id not in self.config_data:
            self.config_data[category_id] = {"items": []}
        elif "items" not in self.config_data[category_id]:
            self.config_data[category_id]["items"] = []
        return self.config_data[category_id]["items"]
    
    def _center_dialog(self, dialog, width, height):
        """다이얼로그를 메인 윈도우 중앙에 위치시키기"""
        dialog.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        center_x = main_x + (main_width - width) // 2
        center_y = main_y + (main_height - height) // 2
        dialog.geometry(f"{width}x{height}+{center_x}+{center_y}")
    
    def _get_item_type_display(self, item_data, name):
        """아이템 타입에 따른 표시 형식 반환"""
        if "items" in item_data:
            return ("📁 서브메뉴", f"📁 {name}")
        elif item_data.get("command"):
            return ("⚡ 명령어", f"⚡ {name}")
        else:
            return ("📄 아이템", f"📄 {name}")
    
    def _setup_dialog(self, dialog, title, width, height, modal=False):
        """다이얼로그 공통 설정"""
        dialog.title(title)
        
        # modal이 True일 때만 grab_set 사용
        if modal:
            dialog.transient(self.root)
            dialog.grab_set()
        
        # 중앙에 위치시키기
        self._center_dialog(dialog, width, height)
        
        return dialog
    
    # === UI 생성 및 관리 메서드들 ===
    
    def create_tooltip(self, widget, text):
        """위젯에 툴팁 추가"""
        ToolTip(widget, text)
    
    def format_file_path(self, file_path, max_length=80):
        """긴 파일 경로를 적절히 줄여서 표시"""
        if not file_path or len(file_path) <= max_length:
            return f"파일: {file_path}" if file_path else "파일: 없음"
        
        # 경로가 너무 길면 중간을 생략
        filename = os.path.basename(file_path)
        dirname = os.path.dirname(file_path)
        
        # 파일명을 포함한 최소 필요 길이 계산
        min_needed = len("파일: ") + len(filename) + len("...\\")
        
        if min_needed >= max_length:
            # 파일명만 표시
            return f"파일: ...\\{filename}"
        
        # 디렉토리 부분에서 사용할 수 있는 길이
        available_for_dir = max_length - len("파일: ") - len(filename) - len("...\\")
        
        if len(dirname) <= available_for_dir:
            return f"파일: {file_path}"
        
        # 디렉토리의 앞부분만 표시
        truncated_dir = dirname[:available_for_dir]
        return f"파일: {truncated_dir}...\\{filename}"
    
    def update_file_label(self, file_path):
        """파일 레이블 업데이트 (툴팁 포함)"""
        display_text = self.format_file_path(file_path)
        self.file_label.configure(text=display_text)
        
        # 전체 경로를 툴팁으로 표시
        if file_path and hasattr(self, 'file_label'):
            # 기존 툴팁 제거하고 새로 생성
            for child in self.file_label.winfo_children():
                child.destroy()
            self.create_tooltip(self.file_label, f"전체 경로: {file_path}")
    
    def on_closing(self):
        """창 닫기 시 리소스 정리 및 저장하지 않은 변경사항 확인"""
        try:
            if self.has_unsaved_changes:
                result = messagebox.askyesnocancel(
                    "저장하지 않은 변경사항",
                    "저장하지 않은 변경사항이 있습니다.\n\n저장하고 종료하시겠습니까?",
                    icon="warning"
                )
                
                if result is True:  # 예 - 저장하고 종료
                    if self.save_config_before_exit():
                        self.cleanup_resources()
                        self.root.destroy()
                elif result is False:  # 아니오 - 저장하지 않고 종료
                    if messagebox.askyesno("확인", "정말로 저장하지 않고 종료하시겠습니까?"):
                        self.cleanup_resources()
                        self.root.destroy()
                # None (취소) - 아무것도 하지 않음
            else:
                self.cleanup_resources()
                self.root.destroy()
        except Exception as e:
            logger.error(f"창 닫기 중 오류: {e}")
            self.cleanup_resources()
            self.root.destroy()
    
    def save_config_before_exit(self):
        """종료 전 설정 저장"""
        try:
            if not self.config_file_path:
                # 파일 경로가 없으면 다른 이름으로 저장 다이얼로그 표시
                self.save_as_config()
                return bool(self.config_file_path)  # 저장이 성공했으면 True
            else:
                # 기존 파일에 저장
                with open(self.config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=4, ensure_ascii=False)
                self.has_unsaved_changes = False
                return True
        except PermissionError:
            self._show_error("권한 오류", f"파일에 쓸 권한이 없습니다: {self.config_file_path}")
            return False
        except OSError as e:
            self._show_error("시스템 오류", f"파일 저장 중 시스템 오류가 발생했습니다: {str(e)}")
            return False
        except Exception as e:
            self._show_error("저장 오류", f"저장 중 오류가 발생했습니다: {str(e)}")
            return False
    
    def mark_as_modified(self):
        """변경사항 표시"""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.update_title()
            self.update_save_button_state()
    
    def mark_as_saved(self):
        """저장됨 표시"""
        self.has_unsaved_changes = False
        self.update_title()
        self.update_save_button_state()
    
    def update_save_button_state(self):
        """저장 버튼 상태 업데이트"""
        if hasattr(self, 'save_button'):
            if self.has_unsaved_changes:
                self.save_button.configure(state=tk.NORMAL)
                # 버튼 텍스트도 변경하여 시각적 효과 증가
                self.save_button.configure(text="💾 저장 *")
                # 툴팁도 업데이트
                try:
                    self.save_button.configure(style="Accent.TButton")
                except:
                    pass  # 스타일이 지원되지 않는 경우 무시
            else:
                self.save_button.configure(state=tk.DISABLED)
                self.save_button.configure(text="💾 저장")
                try:
                    self.save_button.configure(style="TButton")
                except:
                    pass  # 스타일이 지원되지 않는 경우 무시
        
        # 상태바에도 저장 상태 표시
        if hasattr(self, 'status_label'):
            if self.has_unsaved_changes:
                self.update_status("⚠️ 저장하지 않은 변경사항이 있습니다", auto_clear=False)
            else:
                self.update_status("✅ 모든 변경사항이 저장되었습니다")
    
    def update_title(self):
        """창 제목 업데이트"""
        base_title = "TAPython Tool"
        if self.config_file_path:
            filename = os.path.basename(self.config_file_path)
            if self.has_unsaved_changes:
                self.root.title(f"{base_title} - {filename} *")
            else:
                self.root.title(f"{base_title} - {filename}")
        else:
            if self.has_unsaved_changes:
                self.root.title(f"{base_title} - 새 파일 *")
            else:
                self.root.title(base_title)
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _find_default_config_path(self):
        """파일 시스템 탐색으로 TA 폴더와 설정 파일 경로 찾기"""
        try:
            # 현재 스크립트 파일의 절대 경로에서 시작
            current_path = os.path.abspath(__file__)
            
            # 상위 폴더로 올라가면서 TA 폴더 찾기
            max_levels = 10  # 최대 10단계까지 상위로 탐색
            
            for level in range(max_levels):
                current_path = os.path.dirname(current_path)
                
                # 현재 경로에서 TA 폴더 확인
                ta_folder = os.path.join(current_path, "TA")
                if os.path.exists(ta_folder) and os.path.isdir(ta_folder):
                    # logger.info(f"TA 폴더 발견: {ta_folder}")  # 불필요한 로그 제거
                    
                    # TA 폴더 내에서 가능한 설정 파일 경로들
                    possible_paths = [
                        os.path.join(ta_folder, "TAPython", "UI", "MenuConfig.json"),
                        os.path.join(ta_folder, "TAPython", "MenuConfig.json"),
                        os.path.join(ta_folder, "UI", "MenuConfig.json"),
                        os.path.join(ta_folder, "MenuConfig.json"),
                    ]
                    
                    # 존재하는 첫 번째 파일 반환
                    for config_path in possible_paths:
                        if os.path.exists(config_path):
                            # logger.info(f"설정 파일 발견: {config_path}")  # 불필요한 로그 제거
                            return config_path
                    
                    # 파일이 없어도 TA 폴더를 찾았다면 기본 경로 반환
                    default_path = possible_paths[0]
                    # logger.info(f"TA 폴더는 있지만 설정 파일이 없음. 기본 경로 사용: {default_path}")  # 불필요한 로그 제거
                    return default_path
                
                # 루트 디렉토리에 도달하면 중단
                if current_path == os.path.dirname(current_path):
                    break
            
            # TA 폴더를 찾지 못한 경우 현재 스크립트 기준 경로 사용
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fallback_path = os.path.join(
                os.path.dirname(os.path.dirname(script_dir)), 
                "UI", "MenuConfig.json"
            )
            logger.warning(f"TA 폴더를 찾지 못함. 폴백 경로 사용: {fallback_path}")
            return fallback_path
            
        except Exception as e:
            logger.error(f"설정 파일 경로 찾기 중 오류: {e}")
            # 최종 폴백
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(script_dir, "MenuConfig.json")
    
    def setup_ui(self):
        """UI 구성"""
        self._setup_menubar()
        self._setup_main_frame()
        self._setup_status_bar()
        self._setup_keyboard_shortcuts()
        self.setup_tabs()
    
    def _setup_menubar(self):
        """메뉴바 설정"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 파일", menu=file_menu)
        file_menu.add_command(label="📂 열기\t\tCtrl+O", command=self.open_config)
        file_menu.add_command(label="💾 저장\t\tCtrl+S", command=self.save_config)
        file_menu.add_command(label="📄 다른 이름으로 저장\tCtrl+Shift+S", command=self.save_as_config)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 새로고침\t\tF5", command=self.reload_config)
        file_menu.add_separator()
        file_menu.add_command(label="📉 최소화\t\tCtrl+M", command=lambda: self.root.iconify())
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ 편집", menu=edit_menu)
        edit_menu.add_command(label="➕ 아이템 추가", command=lambda: self.add_item_dialog(modal=False))
    
    def _setup_main_frame(self):
        """메인 프레임 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        # 상단 정보
        self._setup_info_frame(main_frame)
        
        # 노트북 (탭)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def _setup_info_frame(self, parent):
        """상단 정보 프레임 설정"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 저장 버튼들 (맨 앞에 배치)
        self._setup_save_buttons(info_frame)
        
        # 파일 경로 표시
        self._setup_file_path_display(info_frame)
        
        # 제목 라벨
        ttk.Label(info_frame, text="TAPython Menu Configuration Editor", 
                 font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
    
    def _setup_save_buttons(self, parent):
        """저장 버튼들 설정"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(side=tk.LEFT)
        
        self.save_button = ttk.Button(button_frame, text="💾 저장", command=self.save_config, 
                                     state=tk.DISABLED, style="Accent.TButton")
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_as_button = ttk.Button(button_frame, text="📄 다른 이름으로 저장", 
                                        command=self.save_as_config)
        self.save_as_button.pack(side=tk.LEFT)
        
        # 툴팁 추가
        self.create_tooltip(self.save_button, "변경사항을 현재 파일에 저장합니다 (Ctrl+S)")
        self.create_tooltip(self.save_as_button, "설정을 새 파일로 저장합니다 (Ctrl+Shift+S)")
    
    def _setup_file_path_display(self, parent):
        """파일 경로 표시 설정"""
        path_frame = ttk.Frame(parent)
        path_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 10))
        
        self.file_label = ttk.Label(path_frame, text="파일: 없음", foreground="gray", anchor="w")
        self.file_label.pack(fill=tk.X)
    
    def _setup_status_bar(self):
        """상태바 설정"""
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))
        
        # 고정 높이 설정
        self.status_frame.pack_propagate(False)
        self.status_frame.configure(height=28)
        
        self.status_label = ttk.Label(self.status_frame, text="준비", anchor=tk.W, 
                                     font=("Arial", 9), padding=(8, 4))
        self.status_label.pack(fill=tk.BOTH, expand=True)
        
        # 상태 메시지를 자동으로 지우기 위한 after 참조
        self.status_after_id = None
    
    def _setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        self.root.bind('<Control-s>', lambda e: self.save_config() if self.has_unsaved_changes else None)
        self.root.bind('<Control-S>', lambda e: self.save_as_config())
        self.root.bind('<Control-o>', lambda e: self.open_config())
        self.root.bind('<F5>', lambda e: self.reload_config())
        # 언리얼 엔진 작업을 위한 빠른 최소화
        self.root.bind('<Control-m>', lambda e: self.root.iconify())
        self.root.bind('<Escape>', lambda e: self.root.iconify())
    
    def update_status(self, message, auto_clear=True, clear_delay=3000):
        """상태바 메시지 업데이트"""
        self.status_label.configure(text=message)
        
        # 이전 타이머가 있으면 취소
        if self.status_after_id:
            self.root.after_cancel(self.status_after_id)
            self.status_after_id = None
        
        # 자동으로 지우기
        if auto_clear:
            self.status_after_id = self.root.after(clear_delay, lambda: self.status_label.configure(text="준비"))
    
    def reload_config(self):
        """현재 파일 다시 로드"""
        if self.config_file_path and os.path.exists(self.config_file_path):
            self.load_config_file(self.config_file_path)
        else:
            self.load_default_config()
    
    def setup_tabs(self):
        """탭들 설정"""
        self.tabs = {}
        
        # 각 메뉴 카테고리별로 탭 생성
        menu_categories = [
            ("OnSelectFolderMenu", "폴더 메뉴"),
            ("OnSelectAssetsMenu", "에셋 메뉴"),
            ("OnMainMenu", "메인 메뉴"),
            ("OnToolbar", "툴바"),
            ("OnToolBarChameleon", "Chameleon 툴바"),
            ("OnOutlineMenu", "아웃라인 메뉴"),
            ("OnMaterialEditorMenu", "머티리얼 에디터"),
            ("OnTabContextMenu", "탭 컨텍스트")
        ]
        
        for category_id, category_name in menu_categories:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=category_name)
            self.tabs[category_id] = self.create_tab_content(tab_frame, category_id)
    
    def create_tab_content(self, parent, category_id):
        """탭 내용 생성"""
        # 메인 컨테이너
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 좌측: 아이템 목록
        left_frame = self._create_left_panel(main_container, category_id)
        
        # 구분선
        separator = ttk.Separator(main_container, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 우측: 아이템 편집
        widgets = self._create_right_panel(main_container, category_id)
        
        # 트리뷰 위젯을 위젯 딕셔너리에 추가
        widgets['treeview'] = left_frame['treeview']
        
        return widgets
    
    def _create_left_panel(self, parent, category_id):
        """좌측 패널 (아이템 목록) 생성"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        
        # 좌측 프레임의 폭을 제한
        left_frame.pack_propagate(False)
        left_frame.configure(width=380)
        
        ttk.Label(left_frame, text="메뉴 아이템", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 트리뷰 생성
        treeview = self._create_treeview(left_frame, category_id)
        
        # 컨트롤 버튼들
        self._create_control_buttons(left_frame, category_id)
        
        return {'treeview': treeview}
    
    def _create_treeview(self, parent, category_id):
        """트리뷰 위젯 생성"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        
        columns = ("type",)
        treeview = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=15)
        treeview.heading("#0", text="이름", anchor=tk.W)
        treeview.heading("type", text="타입", anchor=tk.W)
        treeview.column("#0", width=250, minwidth=180)
        treeview.column("type", width=90, minwidth=70)
        
        # 세로 스크롤바
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=treeview.yview)
        treeview.configure(yscrollcommand=tree_scrollbar_y.set)
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 트리뷰 선택 이벤트
        treeview.bind("<<TreeviewSelect>>", lambda e: self.on_item_select(category_id))
        
        return treeview
    
    def _create_control_buttons(self, parent, category_id):
        """아이템 컨트롤 버튼들 생성"""
        list_btn_frame = ttk.Frame(parent)
        list_btn_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        # 첫 번째 줄: 추가 관련 버튼들
        btn_row1 = ttk.Frame(list_btn_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Button(btn_row1, text="➕ 추가", 
                  command=lambda: self.add_item(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row1, text="📁 서브메뉴 추가", 
                  command=lambda: self.add_submenu(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        
        # 두 번째 줄: 편집 관련 버튼들
        btn_row2 = ttk.Frame(list_btn_frame)
        btn_row2.pack(fill=tk.X)
        
        ttk.Button(btn_row2, text="🗑️ 삭제", 
                  command=lambda: self.delete_item(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row2, text="⬆️ 위로", 
                  command=lambda: self.move_item_up(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row2, text="⬇️ 아래로", 
                  command=lambda: self.move_item_down(category_id)).pack(side=tk.LEFT)
    
    def _create_right_panel(self, parent, category_id):
        """우측 패널 (아이템 편집) 생성"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="아이템 편집", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 설명 라벨
        help_text = "아래에서 아이템 정보를 수정한 후 '변경사항 저장' 버튼을 클릭하세요."
        ttk.Label(right_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(anchor=tk.W, padx=5, pady=(2, 5))
        
        # 편집 폼
        return self._create_edit_form(right_frame, category_id)
    
    def _create_edit_form(self, parent, category_id):
        """편집 폼 생성"""
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 5))
        
        # 폼 위젯들 생성
        widgets = {}
        
        # 이름 필드
        widgets.update(self._create_name_field(edit_frame))
        
        # 툴팁 필드
        widgets.update(self._create_tooltip_field(edit_frame))
        
        # 활성화 체크박스
        widgets.update(self._create_enabled_field(edit_frame))
        
        # 명령어 필드
        widgets.update(self._create_command_field(edit_frame))
        
        # Chameleon 필드
        widgets.update(self._create_chameleon_field(edit_frame))
        
        # 업데이트 버튼
        widgets.update(self._create_update_button(edit_frame, category_id))
        
        # 그리드 가중치
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(3, weight=1)
        
        return widgets
    
    def _create_name_field(self, parent):
        """이름 입력 필드 생성"""
        ttk.Label(parent, text="이름:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(parent, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        return {'name_var': name_var, 'name_entry': name_entry}
    
    def _create_tooltip_field(self, parent):
        """툴팁 입력 필드 생성"""
        ttk.Label(parent, text="툴팁:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        tooltip_var = tk.StringVar()
        tooltip_entry = ttk.Entry(parent, textvariable=tooltip_var, width=40)
        tooltip_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        return {'tooltip_var': tooltip_var, 'tooltip_entry': tooltip_entry}
    
    def _create_enabled_field(self, parent):
        """활성화 체크박스 생성"""
        enabled_var = tk.BooleanVar()
        enabled_var.set(True)  # 기본값을 명시적으로 설정
        enabled_check = ttk.Checkbutton(parent, text="활성화", variable=enabled_var)
        enabled_check.grid(row=2, column=1, sticky=tk.W, pady=2)
        return {'enabled_var': enabled_var, 'enabled_check': enabled_check}
    
    def _create_command_field(self, parent):
        """명령어 입력 필드 생성"""
        ttk.Label(parent, text="명령어:").grid(row=3, column=0, sticky=tk.NW+tk.W, padx=(0, 5), pady=2)
        
        cmd_frame = ttk.Frame(parent)
        cmd_frame.grid(row=3, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=2)
        
        command_text = tk.Text(cmd_frame, height=6, width=40, wrap=tk.WORD)
        cmd_scrollbar = ttk.Scrollbar(cmd_frame, orient=tk.VERTICAL, command=command_text.yview)
        command_text.configure(yscrollcommand=cmd_scrollbar.set)
        
        command_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return {'command_text': command_text}
    
    def _create_chameleon_field(self, parent):
        """Chameleon Tools 입력 필드 생성"""
        ttk.Label(parent, text="Chameleon:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(parent, textvariable=chameleon_var, width=40)
        chameleon_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=2)
        return {'chameleon_var': chameleon_var, 'chameleon_entry': chameleon_entry}
    
    def _create_update_button(self, parent, category_id):
        """업데이트 버튼 생성"""
        update_btn = ttk.Button(parent, text="💾 변경사항 저장", 
                               command=lambda: self.update_item(category_id))
        update_btn.grid(row=5, column=1, sticky=tk.W, pady=(10, 0))
        return {'update_btn': update_btn}
    
    def load_default_config(self):
        """기본 설정 파일 로드"""
        if os.path.exists(self.default_config_path):
            self.load_config_file(self.default_config_path)
            # logger.info(f"기본 설정 파일 로드 완료: {self.default_config_path}")  # 불필요한 로그 제거
        else:
            # 모든 경로에서 찾지 못한 경우
            error_msg = f"기본 설정 파일을 찾을 수 없습니다.\n탐색된 경로: {self.default_config_path}"
            logger.error(error_msg)
            
            if not UNREAL_AVAILABLE:
                print("\nUnreal Engine Python API를 사용할 수 없습니다.")
                print("독립 실행 모드로 실행 중입니다.")
            
            # 빈 설정으로 시작
            self.config_data = {}
    
    def open_config(self):
        """설정 파일 열기"""
        # 기본 디렉토리를 TA 폴더 기준으로 설정
        initial_dir = os.path.dirname(self.default_config_path)
        
        file_path = filedialog.askopenfilename(
            title="MenuConfig.json 열기",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            initialdir=initial_dir
        )
        if file_path:
            self.load_config_file(file_path)
    
    def load_config_file(self, file_path):
        """설정 파일 로드"""
        try:
            logger.debug(f"로드하려는 파일 경로: {file_path}")
            logger.debug(f"파일 존재 여부: {os.path.exists(file_path)}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.config_file_path = file_path
            # 전체 경로 표시 (길면 축약)
            self.update_file_label(file_path)
            
            logger.debug(f"로드된 config_data 키들: {list(self.config_data.keys())}")
            # 첫 번째 카테고리의 첫 번째 아이템 샘플 출력 (메모리 효율적)
            for category, data in self.config_data.items():
                if "items" in data and data["items"]:
                    first_item = data["items"][0]
                    logger.debug(f"{category} 첫 번째 아이템 샘플: {first_item}")
                    break
            
            self.mark_as_saved()  # 로드 후 저장됨 상태로 설정
            self.refresh_all_tabs()
            self.update_status(f"📂 로드 완료: {os.path.basename(file_path)}")
        except FileNotFoundError:
            error_msg = f"파일을 찾을 수 없습니다: {file_path}"
            logger.error(error_msg)
            self._show_error("파일 오류", error_msg)
            self.update_status("❌ 파일을 찾을 수 없음", auto_clear=False)
        except PermissionError:
            error_msg = f"파일에 접근할 권한이 없습니다: {file_path}"
            logger.error(error_msg)
            self._show_error("권한 오류", error_msg)
            self.update_status("❌ 파일 접근 권한 없음", auto_clear=False)
        except json.JSONDecodeError as e:
            error_msg = f"JSON 파일 형식이 올바르지 않습니다: {str(e)}"
            logger.error(f"JSON 파싱 오류: {e}")
            self._show_error("JSON 오류", error_msg)
            self.update_status("❌ JSON 형식 오류", auto_clear=False)
        except UnicodeDecodeError:
            error_msg = f"파일 인코딩이 올바르지 않습니다. UTF-8 인코딩을 사용해주세요."
            logger.error(f"인코딩 오류: {file_path}")
            self._show_error("인코딩 오류", error_msg)
            self.update_status("❌ 인코딩 오류", auto_clear=False)
        except Exception as e:
            error_msg = f"파일 로드 실패: {str(e)}"
            logger.error(f"파일 로드 오류: {e}")
            self._show_error("오류", error_msg)
            self.update_status(f"❌ 로드 실패: {str(e)}", auto_clear=False)
    
    def save_config(self):
        """설정 저장"""
        if not self.config_file_path:
            self.save_as_config()
            return
        
        try:
            logger.debug(f"저장하려는 파일 경로: {self.config_file_path}")
            
            # 저장 전에 JSON 데이터 확인 (디버그) - 메모리 효율적
            logger.debug("저장 중인 config 데이터 샘플:")
            count = 0
            for category, data in self.config_data.items():
                if count >= 2:  # 처음 2개 카테고리만
                    break
                if "items" in data and data["items"]:
                    logger.debug(f"  {category}: {len(data['items'])}개 아이템")
                    for i, item in enumerate(data["items"][:2]):  # 처음 2개 아이템만
                        enabled_status = item.get("enabled", "키없음")
                        logger.debug(f"    [{i}] {item.get('name', '이름없음')}: enabled={enabled_status}")
                count += 1
            
            # 파일에 저장
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            logger.debug("파일 저장 완료")
            
            # 저장 후 파일 다시 읽어서 검증
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                verification_data = json.load(f)
            
            logger.debug("저장 후 검증 - 파일에서 다시 읽은 데이터:")
            for category, data in verification_data.items():
                if "items" in data and data["items"]:
                    first_item = data["items"][0]
                    logger.debug(f"  첫 번째 아이템: {first_item}")
                    break
                    
            self.mark_as_saved()  # 저장 후 저장됨 상태로 설정
            self.update_status("💾 설정이 저장되었습니다!")
        except PermissionError:
            error_msg = f"파일에 쓸 권한이 없습니다: {self.config_file_path}"
            logger.error(error_msg)
            self._show_error("권한 오류", error_msg)
            self.update_status("❌ 파일 쓰기 권한 없음", auto_clear=False)
        except OSError as e:
            error_msg = f"파일 저장 중 시스템 오류가 발생했습니다: {str(e)}"
            logger.error(f"파일 시스템 오류: {e}")
            self._show_error("시스템 오류", error_msg)
            self.update_status("❌ 파일 시스템 오류", auto_clear=False)
        except json.JSONDecodeError as e:
            error_msg = f"JSON 데이터 처리 오류: {str(e)}"
            logger.error(f"JSON 처리 오류: {e}")
            self._show_error("데이터 오류", error_msg)
            self.update_status("❌ 데이터 처리 오류", auto_clear=False)
        except Exception as e:
            error_msg = f"저장 실패: {str(e)}"
            logger.error(f"저장 오류: {e}")
            import traceback
            traceback.print_exc()
            self._show_error("오류", error_msg)
            self.update_status(f"❌ 저장 실패: {str(e)}", auto_clear=False)
    
    def save_as_config(self):
        """다른 이름으로 저장"""
        # 초기 디렉토리 결정
        initial_dir = os.path.dirname(self.default_config_path)
        if UNREAL_AVAILABLE:
            try:
                project_dir = unreal.Paths.project_dir()
                # 프로젝트 디렉토리가 존재하면 그것을 우선 사용
                if os.path.exists(project_dir):
                    initial_dir = project_dir
            except:
                pass
        
        file_path = filedialog.asksaveasfilename(
            title="MenuConfig.json 저장",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            defaultextension=".json",
            initialdir=initial_dir,
            initialfile="MenuConfig.json"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=4, ensure_ascii=False)
                self.config_file_path = file_path
                # 전체 경로 표시 (길면 축약)
                self.update_file_label(file_path)
                self.mark_as_saved()  # 저장 후 저장됨 상태로 설정
                self.update_status("💾 설정이 저장되었습니다!")
            except PermissionError:
                error_msg = f"파일에 쓸 권한이 없습니다: {file_path}"
                self._show_error("권한 오류", error_msg)
                self.update_status("❌ 파일 쓰기 권한 없음", auto_clear=False)
            except OSError as e:
                error_msg = f"파일 저장 중 시스템 오류가 발생했습니다: {str(e)}"
                self._show_error("시스템 오류", error_msg)
                self.update_status("❌ 파일 시스템 오류", auto_clear=False)
            except Exception as e:
                error_msg = f"저장 실패: {str(e)}"
                self._show_error("오류", error_msg)
                self.update_status(f"❌ 저장 실패: {str(e)}", auto_clear=False)
    
    def refresh_all_tabs(self):
        """모든 탭 새로고침"""
        for category_id, tab_widgets in self.tabs.items():
            self.refresh_tab(category_id)
    
    def refresh_tab(self, category_id):
        """특정 탭 새로고침"""
        tab_widgets = self.tabs[category_id]
        treeview = tab_widgets['treeview']
        
        # 트리뷰 초기화
        for item in treeview.get_children():
            treeview.delete(item)
        
        # 데이터가 있는 경우 추가
        if category_id in self.config_data and "items" in self.config_data[category_id]:
            items = self.config_data[category_id]["items"]
            self._populate_tree_items(treeview, "", items)
        
        # 편집 폼 초기화
        self.clear_edit_form(category_id)
    
    def _populate_tree_items(self, treeview, parent, items):
        """트리뷰에 아이템들을 추가 (재귀적으로 서브메뉴 처리)"""
        for i, item in enumerate(items):
            name = item.get("name", f"Item {i}")
            
            # 아이템 타입 결정 (헬퍼 메서드 사용)
            item_type, display_name = self._get_item_type_display(item, name)
            
            # 트리 아이템 추가
            tree_item = treeview.insert(parent, tk.END, text=display_name, values=(item_type,))
            
            # 서브메뉴가 있는 경우 재귀적으로 추가
            if "items" in item and item["items"]:
                self._populate_tree_items(treeview, tree_item, item["items"])
    
    def clear_edit_form(self, category_id):
        """편집 폼 초기화"""
        tab_widgets = self.tabs[category_id]
        tab_widgets['name_var'].set("")
        tab_widgets['tooltip_var'].set("")
        tab_widgets['enabled_var'].set(True)
        tab_widgets['command_text'].delete(1.0, tk.END)
        tab_widgets['chameleon_var'].set("")
        
        # 편집 불가능 상태로 설정
        self.set_edit_state(category_id, False)
    
    def set_edit_state(self, category_id, enabled):
        """편집 폼 활성화/비활성화"""
        tab_widgets = self.tabs[category_id]
        state = tk.NORMAL if enabled else tk.DISABLED
        
        widgets = [
            tab_widgets['name_entry'],
            tab_widgets['tooltip_entry'],
            tab_widgets['chameleon_entry'],
            tab_widgets['enabled_check'],
            tab_widgets['command_text'],
            tab_widgets['update_btn']
        ]
        
        for widget in widgets:
            widget.configure(state=state)
    
    def _verify_command_load(self, tab_widgets, expected_command):
        """Text 위젯에 명령어가 제대로 로드되었는지 검증"""
        try:
            loaded_command = tab_widgets['command_text'].get(1.0, tk.END).rstrip('\n').strip()
            logger.debug(f"100ms 후 재확인 - 로드된 명령어: '{loaded_command}'")
            logger.debug(f"예상 명령어: '{expected_command}'")
            logger.debug(f"일치 여부: {loaded_command == expected_command}")
        except tk.TclError as e:
            logger.error(f"Tkinter 위젯 오류: {e}")
        except AttributeError as e:
            logger.error(f"위젯 속성 오류: {e}")
        except Exception as e:
            logger.error(f"명령어 검증 중 오류: {e}")
    
    def on_item_select(self, category_id):
        """아이템 선택 이벤트"""
        try:
            tab_widgets = self.tabs[category_id]
            treeview = tab_widgets['treeview']
            
            selection = treeview.selection()
            if not selection:
                self.clear_edit_form(category_id)
                return
            
            selected_item = selection[0]
            
            # 선택된 아이템의 경로를 추적하여 데이터 찾기
            item_data = self._get_item_data_from_tree(treeview, selected_item, category_id)
            
            if item_data:
                # 편집 폼에 로드
                tab_widgets['name_var'].set(item_data.get("name", ""))
                tab_widgets['tooltip_var'].set(item_data.get("tooltip", ""))
                
                # enabled 값 처리: 기본값 True, 명시적으로 False인 경우만 False
                enabled_value = item_data.get("enabled", True)
                if "enabled" not in item_data:
                    item_data["enabled"] = enabled_value  # 데이터에 기본값 저장
                
                # 디버그: enabled 값 확인
                logger.debug(f"아이템 '{item_data.get('name')}' 로드됨 - enabled: {enabled_value} (타입: {type(enabled_value)})")
                
                tab_widgets['enabled_var'].set(bool(enabled_value))  # 명시적으로 bool 변환
                
                # 명령어
                tab_widgets['command_text'].delete(1.0, tk.END)
                command = item_data.get("command", "")
                if command:
                    tab_widgets['command_text'].insert(1.0, command)
                    logger.debug(f"명령어 Text 위젯에 로드됨: '{command}'")
                    
                    # 위젯 업데이트 강제 실행
                    tab_widgets['command_text'].update_idletasks()
                    
                    # 잠시 후 다시 읽어서 확인
                    self.root.after(100, lambda: self._verify_command_load(tab_widgets, command))
                else:
                    logger.debug("명령어가 비어있음")
                
                # Text 위젯에서 다시 읽어서 확인
                loaded_command = tab_widgets['command_text'].get(1.0, tk.END).rstrip('\n').strip()
                logger.debug(f"Text 위젯에서 즉시 읽은 명령어: '{loaded_command}'")
                
                # Chameleon
                tab_widgets['chameleon_var'].set(item_data.get("ChameleonTools", ""))
                
                # 편집 가능 상태로 설정
                self.set_edit_state(category_id, True)
            else:
                self.clear_edit_form(category_id)
        except tk.TclError as e:
            logger.error(f"Tkinter 트리뷰 오류: {e}")
            self.clear_edit_form(category_id)
        except AttributeError as e:
            logger.error(f"위젯 속성 오류: {e}")
            self.clear_edit_form(category_id)
        except KeyError as e:
            logger.error(f"데이터 키 오류: {e}")
            self.clear_edit_form(category_id)
        except Exception as e:
            logger.error(f"아이템 선택 중 오류: {e}")
            # 에러 발생 시 편집 폼 초기화
            self.clear_edit_form(category_id)
    
    def _get_item_data_from_tree(self, treeview, tree_item, category_id):
        """트리 아이템으로부터 실제 데이터 찾기 (메모리 효율적)"""
        try:
            # 선택된 아이템의 경로를 추적 (역순으로 생성 후 뒤집기)
            path = []
            current = tree_item
            
            while current:
                path.append(current)
                current = treeview.parent(current)
            
            # 경로를 올바른 순서로 변경
            path.reverse()
            
            # 루트 데이터에서 시작하여 경로를 따라 탐색
            if category_id not in self.config_data or "items" not in self.config_data[category_id]:
                logger.debug(f"카테고리 {category_id}가 config_data에 없음")
                return None
            
            current_items = self.config_data[category_id]["items"]
            current_item_ref = None
            
            for i, tree_id in enumerate(path):
                # 현재 레벨에서 해당 아이템의 인덱스 찾기
                index = self._get_tree_item_index(treeview, tree_id)
                if index >= len(current_items):
                    logger.debug(f"인덱스 {index}가 아이템 수 {len(current_items)}를 초과함")
                    return None
                
                current_item_ref = current_items[index]
                
                # 마지막 아이템이면 반환
                if i == len(path) - 1:  # 마지막 인덱스인지 확인
                    logger.debug(f"찾은 아이템 데이터: {current_item_ref}")
                    logger.debug(f"아이템 메모리 주소: {id(current_item_ref)}")
                    return current_item_ref
                
                # 서브메뉴로 이동
                if "items" in current_item_ref:
                    current_items = current_item_ref["items"]
                else:
                    logger.debug("서브메뉴가 없는 아이템에서 더 깊이 탐색 시도")
                    return None
            
            return None
        except Exception as e:
            logger.error(f"_get_item_data_from_tree 오류: {e}")
            return None
    
    def _get_tree_item_index(self, treeview, tree_item):
        """트리 아이템의 부모 내에서의 인덱스 구하기"""
        try:
            parent = treeview.parent(tree_item)
            siblings = treeview.get_children(parent)
            return siblings.index(tree_item)
        except (ValueError, tk.TclError, AttributeError):
            logger.warning(f"트리 아이템 인덱스 조회 실패: {tree_item}")
            return 0
    
    def update_item(self, category_id):
        """아이템 업데이트"""
        try:
            tab_widgets = self.tabs[category_id]
            treeview = tab_widgets['treeview']
            
            selection = treeview.selection()
            if not selection:
                messagebox.showwarning("경고", "업데이트할 아이템을 선택해주세요.")
                return
            
            selected_item = selection[0]
            item_data = self._get_item_data_from_tree(treeview, selected_item, category_id)
            
            if not item_data:
                self._show_error("오류", "선택된 아이템의 데이터를 찾을 수 없습니다.")
                return
            
            logger.debug(f"업데이트 전 아이템 데이터: {item_data}")
            logger.debug(f"업데이트 전 아이템 메모리 주소: {id(item_data)}")
            
            # 폼에서 데이터 가져와서 업데이트
            name = tab_widgets['name_var'].get().strip()
            if not name:
                self._show_warning("경고", "이름은 비워둘 수 없습니다.")
                return
            
            # enabled 값을 명시적으로 가져오기
            enabled_value = tab_widgets['enabled_var'].get()
            logger.debug(f"폼에서 가져온 enabled 값: {enabled_value} (타입: {type(enabled_value)})")
            
            # 데이터 업데이트 (enabled 값을 먼저 저장)
            old_enabled = item_data.get("enabled", "없음")
            item_data["enabled"] = enabled_value
            item_data["name"] = name
            item_data["tooltip"] = tab_widgets['tooltip_var'].get().strip()
            item_data["ChameleonTools"] = tab_widgets['chameleon_var'].get().strip()
            
            # 명령어 처리 (Text 위젯의 자동 개행 제거)
            raw_command = tab_widgets['command_text'].get(1.0, tk.END)
            command = raw_command.rstrip('\n').strip()
            logger.debug(f"Text 위젯에서 가져온 원본 명령어: '{raw_command}'")
            logger.debug(f"처리된 명령어: '{command}'")
            logger.debug(f"기존 명령어: '{item_data.get('command', '')}'")
            
            # 명령어 업데이트 로직 개선
            existing_command = item_data.get("command", "")
            if command.strip():  # 새 명령어가 있는 경우
                item_data["command"] = command
                logger.debug(f"명령어 업데이트됨: '{command}'")
            elif existing_command:  # Text 위젯이 비어있지만 기존 명령어가 있는 경우
                # 기존 명령어 유지 (Text 위젯 문제로 인한 데이터 손실 방지)
                logger.debug(f"Text 위젯이 비어있어 기존 명령어 유지: '{existing_command}'")
                # item_data["command"]는 그대로 두어 기존 값 유지
            else:  # 둘 다 비어있는 경우
                item_data["command"] = ""
                logger.debug("빈 명령어로 설정됨")
            
            logger.debug(f"업데이트 후 아이템 데이터: {item_data}")
            logger.debug(f"enabled 값 변경: {old_enabled} -> {item_data['enabled']}")
            
            # 트리뷰 업데이트 (헬퍼 메서드 사용)
            item_type, display_name = self._get_item_type_display(item_data, name)
            treeview.item(selected_item, text=display_name, values=(item_type,))
            
            # config_data에서 실제로 변경되었는지 다시 확인
            verification_data = self._get_item_data_from_tree(treeview, selected_item, category_id)
            if verification_data:
                logger.debug(f"검증 - 실제 저장된 enabled 값: {verification_data.get('enabled')}")
                logger.debug(f"검증 - 메모리 주소 동일한가: {id(item_data) == id(verification_data)}")
            
            # 상태 메시지 (enabled 값 확인)
            enabled_status = "✅ 활성화됨" if enabled_value else "❌ 비활성화됨"
            self.update_status(f"💾 '{name}' 저장 완료 ({enabled_status}) - enabled={enabled_value}")
            
            # 변경사항 추적
            self.mark_as_modified()
            
        except tk.TclError as e:
            error_msg = f"UI 위젯 오류: {str(e)}"
            logger.error(f"Tkinter 오류: {e}")
            self._show_error("UI 오류", error_msg)
            self.update_status("❌ UI 오류", auto_clear=False)
        except KeyError as e:
            error_msg = f"데이터 구조 오류: 필요한 키를 찾을 수 없습니다"
            logger.error(f"키 오류: {e}")
            self._show_error("데이터 오류", error_msg)
            self.update_status("❌ 데이터 구조 오류", auto_clear=False)
        except AttributeError as e:
            error_msg = f"객체 속성 오류: {str(e)}"
            logger.error(f"속성 오류: {e}")
            self._show_error("객체 오류", error_msg)
            self.update_status("❌ 객체 오류", auto_clear=False)
        except Exception as e:
            error_msg = f"아이템 업데이트 중 오류 발생: {str(e)}"
            logger.error(f"update_item 오류: {e}")
            import traceback
            traceback.print_exc()
            self._show_error("오류", error_msg)
            self.update_status(f"저장 실패: {str(e)}", auto_clear=False)
    
    def add_item(self, category_id):
        """아이템 추가"""
        # 기본적으로 non-modal로 열어 언리얼 엔진과의 상호작용 허용
        self.add_item_dialog(category_id, modal=False)
    
    def add_submenu(self, category_id):
        """서브메뉴 추가"""
        # 기본적으로 non-modal로 열어 언리얼 엔진과의 상호작용 허용
        self.add_submenu_dialog(category_id, modal=False)
    
    def add_submenu_dialog(self, category_id, modal=False):
        """서브메뉴 추가 다이얼로그 (언리얼 엔진 호환성 개선)"""
        dialog = tk.Toplevel(self.root)
        
        # 언리얼 엔진과의 호환성을 위해 기본적으로 non-modal로 설정
        self._setup_dialog(dialog, "새 서브메뉴 추가", 450, 225, modal=modal)
        
        # 서브메뉴를 추가할 부모 선택
        tab_widgets = self.tabs[category_id]
        treeview = tab_widgets['treeview']
        
        ttk.Label(dialog, text="부모 아이템:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        parent_var = tk.StringVar()
        parent_combo = ttk.Combobox(dialog, textvariable=parent_var, state="readonly")
        parent_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 부모 아이템 목록 구성 (루트 포함)
        parent_items = ["(루트)"]
        self._populate_parent_list(treeview, "", parent_items)
        parent_combo['values'] = parent_items
        parent_combo.current(0)
        
        # 이름
        ttk.Label(dialog, text="서브메뉴 이름:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Chameleon Tools
        ttk.Label(dialog, text="Chameleon:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(dialog, textvariable=chameleon_var)
        chameleon_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 버튼들
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def add_submenu():
            name = name_var.get().strip()
            chameleon = chameleon_var.get().strip()
            parent_selection = parent_var.get()
            
            if not name:
                self._show_warning("경고", "서브메뉴 이름을 입력해주세요.")
                return
            
            new_submenu = {"name": name, "enabled": True, "items": []}
            # Chameleon 값은 빈 문자열이어도 저장
            new_submenu["ChameleonTools"] = chameleon
            
            try:
                if parent_selection == "(루트)":
                    # 루트에 추가 (헬퍼 메서드 사용)
                    items = self._validate_config_data(category_id)
                    items.append(new_submenu)
                    self.update_status(f"📁 서브메뉴 '{name}' 추가됨")
                else:
                    # 선택된 부모에 추가
                    parent_item_data = self._find_parent_by_name(category_id, parent_selection)
                    if parent_item_data:
                        if "items" not in parent_item_data:
                            parent_item_data["items"] = []
                        parent_item_data["items"].append(new_submenu)
                        self.update_status(f"📁 '{parent_selection}'에 서브메뉴 '{name}' 추가됨")
                    else:
                        self._show_error("오류", f"부모 아이템 '{parent_selection}'를 찾을 수 없습니다.")
                        return
                
                # 해당 탭 새로고침
                self.refresh_tab(category_id)
                dialog.destroy()
                
            except Exception as e:
                error_msg = f"서브메뉴 추가 중 오류 발생: {str(e)}"
                self._show_error("오류", error_msg)
                self.update_status(f"서브메뉴 추가 실패: {str(e)}", auto_clear=False)
        
        ttk.Button(button_frame, text="✅ 추가", command=add_submenu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
        name_entry.focus_set()
    
    def _populate_parent_list(self, treeview, parent, parent_list, prefix=""):
        """부모 아이템 목록 생성 (메모리 효율적)"""
        children = treeview.get_children(parent)
        for child in children:
            text = treeview.item(child, "text")
            values = treeview.item(child, "values")
            if values and values[0] == "📁 서브메뉴":
                if prefix:
                    full_text = f"{prefix}{text}"
                    parent_list.append(full_text)
                    new_prefix = f"{full_text}/"
                else:
                    parent_list.append(text)
                    new_prefix = f"{text}/"
                self._populate_parent_list(treeview, child, parent_list, new_prefix)
    
    def _find_parent_by_name(self, category_id, parent_name):
        """이름으로 부모 아이템 데이터 찾기"""
        if category_id not in self.config_data or "items" not in self.config_data[category_id]:
            return None
        
        # 경로를 "/"로 분할
        path_parts = parent_name.split("/")
        
        # 루트에서 시작하여 경로를 따라 탐색
        current_items = self.config_data[category_id]["items"]
        
        for part in path_parts:
            found = False
            for item in current_items:
                if item.get("name") == part and "items" in item:
                    current_items = item["items"]
                    if part == path_parts[-1]:  # 마지막 부분이면 해당 아이템 반환
                        return item
                    found = True
                    break
            
            if not found:
                return None
        
        return None
    
    def add_item_dialog(self, category_id=None, modal=False):
        """아이템 추가 다이얼로그 (언리얼 엔진 호환성 개선)"""
        dialog = tk.Toplevel(self.root)
        
        # 언리얼 엔진과의 호환성을 위해 기본적으로 non-modal로 설정
        self._setup_dialog(dialog, "새 아이템 추가", 600, 300, modal=modal)
        
        # 메뉴 타입 선택
        if category_id is None:
            ttk.Label(dialog, text="메뉴 타입:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            category_var = tk.StringVar()
            category_combo = ttk.Combobox(dialog, textvariable=category_var, 
                                        values=tuple(self.config_data.keys()), state="readonly")
            category_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            if self.config_data:
                category_combo.current(0)
        else:
            category_var = tk.StringVar(value=category_id)
        
        # 부모 아이템 선택 (category_id가 지정된 경우만)
        parent_var = tk.StringVar()
        if category_id is not None:
            ttk.Label(dialog, text="부모 아이템:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            parent_combo = ttk.Combobox(dialog, textvariable=parent_var, state="readonly")
            parent_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # 부모 아이템 목록 구성
            tab_widgets = self.tabs[category_id]
            treeview = tab_widgets['treeview']
            parent_items = ["(루트)"]
            self._populate_parent_list(treeview, "", parent_items)
            parent_combo['values'] = parent_items
            parent_combo.current(0)
            
            name_row = 2
        else:
            parent_var.set("(루트)")
            name_row = 1
        
        # 이름
        ttk.Label(dialog, text="이름:").grid(row=name_row, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.grid(row=name_row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 명령어
        ttk.Label(dialog, text="명령어:").grid(row=name_row+1, column=0, sticky=tk.NW+tk.W, padx=5, pady=5)
        command_text = tk.Text(dialog, height=8, width=50)
        command_text.grid(row=name_row+1, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Chameleon Tools
        ttk.Label(dialog, text="Chameleon:").grid(row=name_row+2, column=0, sticky=tk.W, padx=5, pady=5)
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(dialog, textvariable=chameleon_var)
        chameleon_entry.grid(row=name_row+2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 버튼들
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=name_row+3, column=0, columnspan=2, pady=10)
        
        def add_item():
            name = name_var.get().strip()
            command = command_text.get(1.0, tk.END).strip()
            chameleon = chameleon_var.get().strip()
            selected_category = category_var.get()
            parent_selection = parent_var.get()
            
            if not name:
                self._show_warning("경고", "이름을 입력해주세요.")
                return
            
            if not selected_category:
                self._show_warning("경고", "메뉴 타입을 선택해주세요.")
                return
            
            new_item = {"name": name, "enabled": True}
            if command:
                new_item["command"] = command
            # Chameleon 값은 빈 문자열이어도 저장
            new_item["ChameleonTools"] = chameleon
            
            try:
                if parent_selection == "(루트)":
                    # 카테고리 데이터 확인/생성 (헬퍼 메서드 사용)
                    items = self._validate_config_data(selected_category)
                    items.append(new_item)
                else:
                    # 선택된 부모에 추가
                    parent_item_data = self._find_parent_by_name(selected_category, parent_selection)
                    if parent_item_data:
                        if "items" not in parent_item_data:
                            parent_item_data["items"] = []
                        parent_item_data["items"].append(new_item)
                    else:
                        self._show_error("오류", f"부모 아이템 '{parent_selection}'를 찾을 수 없습니다.")
                        return
                
                # 해당 탭 새로고침
                self.refresh_tab(selected_category)
                self.mark_as_modified()  # 변경사항 추적
                dialog.destroy()
                self.update_status(f"➕ 아이템 '{name}' 추가됨")
                
            except Exception as e:
                error_msg = f"아이템 추가 중 오류 발생: {str(e)}"
                self._show_error("오류", error_msg)
                self.update_status(f"아이템 추가 실패: {str(e)}", auto_clear=False)
        
        ttk.Button(button_frame, text="✅ 추가", command=add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 그리드 가중치
        dialog.columnconfigure(1, weight=1)
        dialog.rowconfigure(name_row+1, weight=1)
        
        name_entry.focus_set()
    
    def delete_item(self, category_id):
        """아이템 삭제"""
        tab_widgets = self.tabs[category_id]
        treeview = tab_widgets['treeview']
        
        selection = treeview.selection()
        if not selection:
            self._show_warning("경고", "삭제할 아이템을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "정말 이 아이템을 삭제하시겠습니까?"):
            selected_item = selection[0]
            
            # 아이템 경로 추적하여 삭제
            if self._delete_item_from_data(treeview, selected_item, category_id):
                self.refresh_tab(category_id)
                self.mark_as_modified()  # 변경사항 추적
                self.update_status("🗑️ 아이템이 삭제되었습니다!")
    
    def _delete_item_from_data(self, treeview, tree_item, category_id):
        """데이터에서 아이템 삭제"""
        # 선택된 아이템의 경로를 추적
        path = []
        current = tree_item
        
        while current:
            path.insert(0, current)
            current = treeview.parent(current)
        
        if category_id not in self.config_data or "items" not in self.config_data[category_id]:
            return False
        
        # 부모 컨테이너와 인덱스 찾기
        current_items = self.config_data[category_id]["items"]
        
        for i, tree_id in enumerate(path[:-1]):
            index = self._get_tree_item_index(treeview, tree_id)
            if index >= len(current_items):
                return False
            
            current_item = current_items[index]
            if "items" not in current_item:
                return False
            
            current_items = current_item["items"]
        
        # 마지막 아이템 삭제
        final_index = self._get_tree_item_index(treeview, path[-1])
        if final_index < len(current_items):
            del current_items[final_index]
            return True
        
        return False
    
    def move_item_up(self, category_id):
        """아이템 위로 이동"""
        tab_widgets = self.tabs[category_id]
        treeview = tab_widgets['treeview']
        
        selection = treeview.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        parent = treeview.parent(selected_item)
        siblings = treeview.get_children(parent)
        
        if not siblings or siblings[0] == selected_item:
            return  # 이미 첫 번째 아이템
        
        current_index = siblings.index(selected_item)
        if current_index > 0:
            # 데이터에서 이동
            if self._move_item_in_data(treeview, selected_item, category_id, -1):
                # 선택된 아이템의 경로를 기억
                item_path = self._get_item_path(treeview, selected_item)
                
                self.refresh_tab(category_id)
                self.mark_as_modified()  # 변경사항 추적
                
                # 이동된 위치에서 아이템을 다시 선택
                if item_path:
                    moved_item = self._find_item_by_path(treeview, item_path, current_index - 1)
                    if moved_item:
                        treeview.selection_set(moved_item)
                        self.on_item_select(category_id)
    
    def move_item_down(self, category_id):
        """아이템 아래로 이동"""
        tab_widgets = self.tabs[category_id]
        treeview = tab_widgets['treeview']
        
        selection = treeview.selection()
        if not selection:
            return
        
        selected_item = selection[0]
        parent = treeview.parent(selected_item)
        siblings = treeview.get_children(parent)
        
        if not siblings or siblings[-1] == selected_item:
            return  # 이미 마지막 아이템
        
        current_index = siblings.index(selected_item)
        if current_index < len(siblings) - 1:
            # 데이터에서 이동
            if self._move_item_in_data(treeview, selected_item, category_id, 1):
                # 선택된 아이템의 경로를 기억
                item_path = self._get_item_path(treeview, selected_item)
                
                self.refresh_tab(category_id)
                self.mark_as_modified()  # 변경사항 추적
                
                # 이동된 위치에서 아이템을 다시 선택
                if item_path:
                    moved_item = self._find_item_by_path(treeview, item_path, current_index + 1)
                    if moved_item:
                        treeview.selection_set(moved_item)
                        self.on_item_select(category_id)
    
    def _get_item_path(self, treeview, tree_item):
        """트리 아이템의 경로를 텍스트로 가져오기"""
        path = []
        current = tree_item
        
        while current:
            text = treeview.item(current, "text")
            path.insert(0, text)
            current = treeview.parent(current)
        
        return path
    
    def _find_item_by_path(self, treeview, path, target_index):
        """경로를 통해 트리 아이템 찾기"""
        if not path:
            return None
        
        # 루트에서 시작
        current_children = treeview.get_children("")
        
        # 경로의 마지막을 제외하고 탐색
        for path_name in path[:-1]:
            found = False
            for child in current_children:
                if treeview.item(child, "text") == path_name:
                    current_children = treeview.get_children(child)
                    found = True
                    break
            if not found:
                return None
        
        # 마지막 레벨에서 target_index에 해당하는 아이템 반환
        if target_index < len(current_children):
            return current_children[target_index]
        
        return None
    
    def _move_item_in_data(self, treeview, tree_item, category_id, direction):
        """데이터에서 아이템 이동 (direction: -1=위로, 1=아래로)"""
        # 선택된 아이템의 경로를 추적
        path = []
        current = tree_item
        
        while current:
            path.insert(0, current)
            current = treeview.parent(current)
        
        if category_id not in self.config_data or "items" not in self.config_data[category_id]:
            return False
        
        # 부모 컨테이너 찾기
        current_items = self.config_data[category_id]["items"]
        
        for i, tree_id in enumerate(path[:-1]):
            index = self._get_tree_item_index(treeview, tree_id)
            if index >= len(current_items):
                return False
            
            current_item = current_items[index]
            if "items" not in current_item:
                return False
            
            current_items = current_item["items"]
        
        # 마지막 아이템 이동
        final_index = self._get_tree_item_index(treeview, path[-1])
        new_index = final_index + direction
        
        if 0 <= new_index < len(current_items):
            # 아이템 교환
            current_items[final_index], current_items[new_index] = \
                current_items[new_index], current_items[final_index]
            return True
        
        return False
    
    def cleanup_resources(self):
        """리소스 정리 메서드 (중복 호출 방지)"""
        if self._resources_cleaned:
            return
            
        try:
            if file_handler:
                file_handler.close()
                logger.removeHandler(file_handler)
                # logger.info("파일 핸들러가 정리되었습니다.")  # 불필요한 로그 제거
            self._resources_cleaned = True
        except Exception as e:
            logger.error(f"파일 핸들러 정리 중 오류: {e}")
            self._resources_cleaned = True
    
    def run(self):
        """메인 루프 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    app = None
    try:
        app = TAPythonTool()
        app.run()
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # 최종 리소스 정리 (앱이 정상적으로 정리되지 않은 경우에만)
        if app and not getattr(app, '_resources_cleaned', False):
            try:
                app.cleanup_resources()
            except:
                pass


if __name__ == "__main__":
    main()