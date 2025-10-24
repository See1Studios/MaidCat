#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool
TAPython MenuConfig.json을 간단하게 편집할 수 있는 툴
"""

import json
import logging
import os
import sys
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any

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
        self.root.title("🐍 TA Python Tool")
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
    










    def show_log_viewer(self):
        """로그 뷰어 다이얼로그"""
        try:
            dialog = tk.Toplevel(self.root)
            self._setup_dialog(dialog, "📋 로그 뷰어", 800, 600, modal=False)
            
            # 메인 프레임
            main_frame = ttk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 로그 레벨 선택
            level_frame = ttk.Frame(main_frame)
            level_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(level_frame, text="로그 레벨:").pack(side=tk.LEFT, padx=(0, 5))
            level_var = tk.StringVar(value="DEBUG")
            level_combo = ttk.Combobox(level_frame, textvariable=level_var, 
                                     values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                     state="readonly", width=10)
            level_combo.pack(side=tk.LEFT, padx=(0, 10))
            
            # 새로고침 버튼
            ttk.Button(level_frame, text="🔄 새로고침", 
                      command=lambda: self._refresh_log_viewer(text_widget, level_var.get())).pack(side=tk.LEFT, padx=5)
            
            # 로그 텍스트 영역
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
            scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            text_widget.grid(row=0, column=0, sticky=tk.NSEW)
            scrollbar_y.grid(row=0, column=1, sticky=tk.NS)
            scrollbar_x.grid(row=1, column=0, sticky=tk.EW)
            
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            
            # 초기 로그 로드
            self._refresh_log_viewer(text_widget, level_var.get())
            
            # 레벨 변경 시 자동 새로고침
            level_combo.bind("<<ComboboxSelected>>", 
                           lambda e: self._refresh_log_viewer(text_widget, level_var.get()))
            
        except Exception as e:
            error_msg = f"로그 뷰어 표시 중 오류: {str(e)}"
            logger.error(error_msg)
            self._show_error("오류", error_msg)

    def _copy_to_clipboard(self, text):
        """텍스트를 클립보드에 복사"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("📋 클립보드에 복사되었습니다!")
        except Exception as e:
            logger.error(f"클립보드 복사 중 오류: {e}")
            self._show_error("오류", f"클립보드 복사 실패: {str(e)}")

    def _refresh_log_viewer(self, text_widget, level):
        """로그 뷰어 새로고침"""
        try:
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            
            # 로그 파일 읽기
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_file = os.path.join(script_dir, 'ta_python_tool.log')
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 레벨 필터링
                filtered_lines = []
                for line in lines:
                    if level == "DEBUG" or level in line:
                        filtered_lines.append(line)
                
                if filtered_lines:
                    text_widget.insert(tk.END, "".join(filtered_lines))
                else:
                    text_widget.insert(tk.END, f"선택된 레벨 '{level}'에 해당하는 로그가 없습니다.")
            else:
                text_widget.insert(tk.END, f"로그 파일을 찾을 수 없습니다: {log_file}")
            
            text_widget.configure(state=tk.DISABLED)
            # 맨 아래로 스크롤
            text_widget.see(tk.END)
            
        except Exception as e:
            logger.error(f"로그 뷰어 새로고침 중 오류: {e}")
            text_widget.configure(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"로그 로드 중 오류: {str(e)}")
            text_widget.configure(state=tk.DISABLED)

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
        """UI 구성 - 새로운 좌우 분할 레이아웃"""
        self._setup_menubar()
        self._setup_main_layout()  # 기존 _setup_main_frame 대신
        self._setup_status_bar()
        self._setup_keyboard_shortcuts()
    
    def _setup_main_layout(self):
        """메인 레이아웃 설정 - 가로 3개 패널 (카테고리 20%, 메뉴 아이템 30%, 편집 영역 50%)"""
        # 상단 정보 프레임 먼저 설정
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        self._setup_info_frame(info_frame)
        
        # 메인 컨테이너 (수평 분할)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 25))  # 상태바 공간 확보
        
        # 첫 번째 패널 - 카테고리 리스트 (20%)
        self.category_panel = self._create_panel(main_paned, "📂 메뉴 카테고리")
        main_paned.add(self.category_panel, weight=2)  # 20% 비율을 위해 weight 2
        
        # 두 번째 패널 - 메뉴 아이템 리스트 (30%)  
        self.menu_panel = self._create_panel(main_paned, "📄 메뉴 아이템을 선택하세요")
        main_paned.add(self.menu_panel, weight=3)  # 30% 비율을 위해 weight 3
        
        # 세 번째 패널 - 아이템 편집 영역 (50%)
        self.edit_panel = self._create_panel(main_paned, "✏️ 아이템을 선택하세요")
        main_paned.add(self.edit_panel, weight=5)  # 50% 비율을 위해 weight 5
        
        # 각 패널 설정
        self._setup_category_panel(self.category_panel)
        self._setup_menu_panel(self.menu_panel)
        self._setup_edit_panel(self.edit_panel)
        
        # 초기 분할 위치 설정 (20%, 50%, 100%)
        self.root.after(100, lambda: self._set_panel_proportions(main_paned))
    
    def _create_panel(self, parent, title):
        """일관된 스타일의 패널 생성"""
        panel = ttk.LabelFrame(parent, text=title, padding=(10, 5))
        return panel
    
    def _set_panel_proportions(self, paned_window):
        """패널 비율 설정 (20%, 30%, 50%)"""
        try:
            total_width = paned_window.winfo_width()
            if total_width > 100:  # 최소 크기 확인
                first_pos = int(total_width * 0.20)  # 첫 번째 구분선: 20% 위치
                second_pos = int(total_width * 0.50)  # 두 번째 구분선: 50% 위치 (20% + 30%)
                
                paned_window.sashpos(0, first_pos)
                paned_window.sashpos(1, second_pos)
        except tk.TclError:
            # 위젯이 아직 준비되지 않은 경우 다시 시도
            self.root.after(100, lambda: self._set_panel_proportions(paned_window))
    
    def _setup_category_panel(self, panel):
        """카테고리 패널 설정"""
        # 리스트박스 프레임
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # 스크롤바가 있는 리스트박스
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("맑은 고딕", 9),
            selectmode=tk.SINGLE
        )
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.category_listbox.yview)
        
        # 이벤트 바인딩
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        self.category_listbox.bind('<Button-3>', self.on_category_right_click)
        
        # 버튼들
        button_frame = ttk.Frame(panel)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="➕ 새 카테고리", command=self.add_new_category).pack(fill=tk.X, pady=1)
        ttk.Button(button_frame, text="🗑️ 카테고리 삭제", command=self.delete_selected_category).pack(fill=tk.X, pady=1)
        
        # 카테고리 우클릭 메뉴
        self.category_context_menu = tk.Menu(self.root, tearoff=0)
        self.category_context_menu.add_command(label="🗑️ 카테고리 삭제", command=self.delete_selected_category)
        
        # 카테고리 데이터 저장용
        self.category_data = {}
        
        # 기존 코드 호환성을 위한 tabs 초기화
        self.tabs = {}
        
        # 카테고리 목록 로드
        self.refresh_category_list()
    
    def _setup_menu_panel(self, panel):
        """메뉴 아이템 패널 설정"""
        # 트리뷰 컨테이너
        self.menu_tree_frame = ttk.Frame(panel)
        self.menu_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # 컨트롤 버튼들
        button_frame = ttk.Frame(panel)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 첫 번째 줄: 추가 관련 버튼들
        btn_row1 = ttk.Frame(button_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 3))
        
        self.add_item_btn = ttk.Button(btn_row1, text="➕ 추가", state=tk.DISABLED)
        self.add_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.add_submenu_btn = ttk.Button(btn_row1, text="📁 서브메뉴 추가", state=tk.DISABLED)
        self.add_submenu_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 두 번째 줄: 편집 관련 버튼들
        btn_row2 = ttk.Frame(button_frame)
        btn_row2.pack(fill=tk.X)
        
        self.delete_item_btn = ttk.Button(btn_row2, text="🗑️ 삭제", state=tk.DISABLED)
        self.delete_item_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.move_up_btn = ttk.Button(btn_row2, text="⬆️ 위로", state=tk.DISABLED)
        self.move_up_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.move_down_btn = ttk.Button(btn_row2, text="⬇️ 아래로", state=tk.DISABLED)
        self.move_down_btn.pack(side=tk.LEFT)
        
        # 현재 선택된 카테고리 ID
        self.current_category_id = None
        self.current_menu_treeview = None
    
    def _setup_edit_panel(self, panel):
        """편집 패널 설정"""
        # 편집 폼 컨테이너
        self.edit_form_frame = ttk.Frame(panel)
        self.edit_form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 현재 위젯들 저장용
        self.current_widgets = None
    
    def update_panel_titles(self, category_name=None, item_name=None):
        """패널 제목들을 현재 선택 상태에 따라 업데이트"""
        try:
            # 카테고리 패널은 항상 고정
            self.category_panel.configure(text="📂 메뉴 카테고리")
            
            # 메뉴 아이템 패널
            if category_name:
                menu_title = f"📄 {category_name}"
                self.menu_panel.configure(text=menu_title)
            else:
                self.menu_panel.configure(text="📄 카테고리를 선택하세요")
            
            # 편집 패널
            if item_name:
                edit_title = f"✏️ {item_name}"
                if len(edit_title) > 50:  # 제목이 너무 길면 축약
                    edit_title = f"✏️ {item_name[:45]}..."
                self.edit_panel.configure(text=edit_title)
            elif category_name:
                self.edit_panel.configure(text="✏️ 아이템을 선택하세요")
            else:
                self.edit_panel.configure(text="✏️ 카테고리를 선택하세요")
        except Exception as e:
            logger.error(f"패널 제목 업데이트 중 오류: {e}")
    

    
    def refresh_category_list(self):
        """카테고리 리스트 새로고침"""
        self.category_listbox.delete(0, tk.END)
        self.category_data = {}
        
        # 설정 파일에서 실제로 존재하는 카테고리만 표시
        available_categories = self._get_available_categories(self._get_all_menu_categories())
        
        for category_id, category_name in available_categories:
            self.category_listbox.insert(tk.END, category_name)
            self.category_data[len(self.category_data)] = (category_id, category_name)
    
    def on_category_select(self, event):
        """카테고리 선택 이벤트"""
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index in self.category_data:
            category_id, category_name = self.category_data[index]
            self.show_category_content(category_id, category_name)
    
    def on_category_right_click(self, event):
        """카테고리 우클릭 이벤트"""
        # 클릭한 위치의 아이템 선택
        index = self.category_listbox.nearest(event.y)
        self.category_listbox.selection_clear(0, tk.END)
        self.category_listbox.selection_set(index)
        
        # 컨텍스트 메뉴 표시
        self.category_context_menu.post(event.x_root, event.y_root)
    
    def add_new_category(self):
        """새 카테고리 추가"""
        dialog = NewCategoryDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            if len(dialog.result) == 4:  # 새 형식: (id, name, is_anchor, has_section)
                category_id, category_name, is_anchor, has_section = dialog.result
            else:  # 이전 호환성: (id, name)
                category_id, category_name = dialog.result
                is_anchor = "." in category_id
                has_section = True if is_anchor else None
            
            # 중복 확인
            if category_id in self.config_data:
                self._show_warning("경고", f"카테고리 '{category_id}'가 이미 존재합니다.")
                return
            
            # 새 카테고리 추가
            category_data = {"items": []}
            
            # Tool Menu Anchor인 경우 HasSection 추가
            if is_anchor and has_section is not None:
                category_data["HasSection"] = has_section
            
            self.config_data[category_id] = category_data
            self.mark_as_modified()
            self.refresh_category_list()
            
            category_type = "Tool Menu Anchor" if is_anchor else "메뉴 카테고리"
            self.update_status(f"🆕 {category_type} '{category_name}' 추가됨!")
    
    def delete_selected_category(self):
        """선택된 카테고리 삭제"""
        selection = self.category_listbox.curselection()
        if not selection:
            self._show_warning("경고", "삭제할 카테고리를 선택하세요.")
            return
        
        index = selection[0]
        if index not in self.category_data:
            return
        
        category_id, category_name = self.category_data[index]
        
        # 아이템 개수 확인
        item_count = len(self.config_data.get(category_id, {}).get("items", []))
        
        # 삭제 확인
        confirm_msg = f"정말로 '{category_name}' 카테고리를 삭제하시겠습니까?\n\n"
        confirm_msg += f"• {item_count}개의 메뉴 아이템이 함께 삭제됩니다.\n"
        confirm_msg += "• 이 작업은 되돌릴 수 없습니다."
        
        if messagebox.askyesno("카테고리 삭제 확인", confirm_msg, icon="warning"):
            # config_data에서 제거
            if category_id in self.config_data:
                del self.config_data[category_id]
            
            # UI 초기화
            if self.current_category_id == category_id:
                self.clear_content_area()
            
            self.mark_as_modified()
            self.refresh_category_list()
            self.update_status(f"🗑️ 카테고리 '{category_name}' 삭제됨!")
    
    def show_category_content(self, category_id, category_name):
        """선택된 카테고리의 내용을 표시"""
        self.current_category_id = category_id
        
        # 패널 제목 업데이트 (카테고리 선택됨, 아이템은 아직 선택 안됨)
        self.update_panel_titles(category_name=category_name)
        
        # 기존 트리뷰 제거
        for widget in self.menu_tree_frame.winfo_children():
            widget.destroy()
        
        # 새 트리뷰 생성
        self.current_menu_treeview = self._create_menu_treeview(self.menu_tree_frame, category_id)
        
        # 편집 폼 제거
        for widget in self.edit_form_frame.winfo_children():
            widget.destroy()
        
        # 새 편집 폼 생성
        self.current_widgets = self._create_edit_form(self.edit_form_frame, category_id)
        self.current_widgets['treeview'] = self.current_menu_treeview
        
        # 기존 코드 호환성을 위해 tabs에도 저장
        self.tabs[category_id] = self.current_widgets
        
        # 버튼 활성화
        self._enable_menu_buttons()
        
        # 트리뷰에 데이터 로드
        self.refresh_tab(category_id)
    
    def _create_menu_treeview(self, parent, category_id):
        """메뉴 트리뷰 생성"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("type",)
        treeview = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
        treeview.heading("#0", text="이름", anchor=tk.W)
        treeview.heading("type", text="타입", anchor=tk.W)
        treeview.column("#0", width=200, minwidth=150)
        treeview.column("type", width=80, minwidth=60)
        
        # 세로 스크롤바
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=treeview.yview)
        treeview.configure(yscrollcommand=tree_scrollbar_y.set)
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 트리뷰 선택 이벤트
        treeview.bind("<<TreeviewSelect>>", lambda e: self.on_item_select(category_id))
        
        return treeview
    
    def _enable_menu_buttons(self):
        """메뉴 버튼들 활성화"""
        if self.current_category_id:
            self.add_item_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.add_item(self.current_category_id)
            )
            self.add_submenu_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.add_submenu(self.current_category_id)
            )
            self.delete_item_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.delete_item(self.current_category_id)
            )
            self.move_up_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.move_item_up(self.current_category_id)
            )
            self.move_down_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.move_item_down(self.current_category_id)
            )
    
    def clear_content_area(self):
        """내용 영역 초기화"""
        self.current_category_id = None
        
        # 패널 제목 초기화
        self.update_panel_titles()
        
        # 트리뷰 제거
        for widget in self.menu_tree_frame.winfo_children():
            widget.destroy()
        
        # 편집 폼 제거
        for widget in self.edit_form_frame.winfo_children():
            widget.destroy()
        
        # 버튼 비활성화
        self.add_item_btn.configure(state=tk.DISABLED)
        self.add_submenu_btn.configure(state=tk.DISABLED)
        self.delete_item_btn.configure(state=tk.DISABLED)
        self.move_up_btn.configure(state=tk.DISABLED)
        self.move_down_btn.configure(state=tk.DISABLED)
        
        self.current_widgets = None
        self.current_menu_treeview = None
    
    def create_category_content(self, parent, category_id):
        """카테고리 내용 생성 (기존 create_tab_content와 동일)"""
        # 메인 컨테이너
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True)
        
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
        edit_menu.add_command(label="➕ 아이템 추가", command=lambda: self.add_item_dialog(modal=True))
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 도구", menu=tools_menu)
        tools_menu.add_command(label="🔄 Tool Menu 새로고침", command=self.refresh_tool_menus)
        tools_menu.add_separator()
        tools_menu.add_command(label="📋 로그 보기", command=self.show_log_viewer)
    
    def _setup_main_frame(self):
        """메인 프레임 설정 - 더 이상 사용되지 않음"""
        pass
    

    
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
    
    def _get_all_menu_categories(self):
        """모든 메뉴 카테고리 목록 반환"""
        return [
            # 전통적인 메뉴 카테고리들
            ("OnSelectFolderMenu", "폴더 메뉴"),
            ("OnSelectAssetsMenu", "에셋 메뉴"),
            ("OnMainMenu", "메인 메뉴"),
            ("OnToolbar", "툴바"),
            ("OnToolBarChameleon", "Chameleon 툴바"),
            ("OnOutlineMenu", "아웃라인 메뉴"),
            ("OnMaterialEditorMenu", "머티리얼 에디터"),
            ("OnPhysicsAssetEditorMenu", "Physics Asset 에디터"),
            ("OnControlRigEditorMenu", "ControlRig 에디터"),
            ("OnTabContextMenu", "탭 컨텍스트"),
            
            # Tool Menu Anchor 카테고리들
            ("AssetEditor.AnimationBlueprintEditor.MainMenu", "애니메이션 BP 에디터 메뉴"),
            ("AssetEditor.AnimationEditor.MainMenu", "애니메이션 에디터 메뉴"),
            ("AssetEditor.SkeletalMeshEditor.ToolBar", "스켈레탈 메시 에디터 툴바"),
            ("AssetEditor.StaticMeshEditor.ToolBar", "스태틱 메시 에디터 툴바"),
            ("ContentBrowser.AddNewContextMenu", "콘텐츠 브라우저 새로 추가"),
            ("ContentBrowser.AssetContextMenu", "에셋 컨텍스트 메뉴"),
            ("ContentBrowser.AssetContextMenu.AnimBlueprint", "애니메이션 BP 컨텍스트"),
            ("ContentBrowser.AssetContextMenu.AnimSequence", "애니메이션 시퀀스 컨텍스트"),
            ("ContentBrowser.AssetContextMenu.SkeletalMesh", "스켈레탈 메시 컨텍스트"),
            ("ContentBrowser.AssetContextMenu.StaticMesh", "스태틱 메시 컨텍스트"),
            ("ContentBrowser.AssetContextMenu.World", "월드 컨텍스트"),
            ("ContentBrowser.FolderContextMenu", "폴더 컨텍스트 메뉴"),
            ("ContentBrowser.ToolBar", "콘텐츠 브라우저 툴바"),
            ("Kismet.SubobjectEditorContextMenu", "컴포넌트 컨텍스트 메뉴"),
            ("Kismet.SCSEditorContextMenu", "SCS 에디터 컨텍스트"),
            ("ControlRigEditor.RigHierarchy.ContextMenu", "리그 계층 컨텍스트"),
            ("ControlRigEditor.RigHierarchy.DragDropMenu", "리그 드래그드롭 메뉴"),
            ("LevelEditor.ActorContextMenu.AssetToolsSubMenu", "액터 에셋 도구 서브메뉴"),
            ("LevelEditor.ActorContextMenu.LevelSubMenu", "액터 레벨 서브메뉴"),
            ("LevelEditor.InViewportPanel", "뷰포트 패널"),
            ("LevelEditor.LevelEditorSceneOutliner.ContextMenu.LevelSubMenu", "아웃라이너 레벨 서브메뉴"),
            ("LevelEditor.LevelEditorToolBar", "레벨 에디터 툴바"),
            ("LevelEditor.LevelEditorToolBar.AddQuickMenu", "빠른 추가 메뉴"),
            ("LevelEditor.LevelEditorToolBar.User", "사용자 툴바"),
            ("LevelEditor.LevelViewportToolBar.Options", "뷰포트 옵션"),
            ("LevelEditor.LevelViewportToolBar.View", "뷰포트 보기"),
            ("LevelEditor.MainMenu.Build", "빌드 메뉴"),
            ("LevelEditor.MainMenu.File", "파일 메뉴"),
            ("LevelEditor.MainMenu.Help", "도움말 메뉴"),
            ("LevelEditor.MainMenu.Select", "선택 메뉴"),
            ("LevelEditor.MainMenu.Tools", "도구 메뉴"),
            ("LevelEditor.MainMenu.Window", "윈도우 메뉴"),
            ("LevelEditor.StatusBar.ToolBar", "상태바 툴바"),
            ("MainFrame.MainMenu.Asset", "메인 에셋 메뉴"),
            ("MainFrame.MainMenu.Tools", "메인 도구 메뉴"),
            ("MainFrame.MainMenu.Window", "메인 윈도우 메뉴"),
            ("StatusBar.ToolBar.SourceControl", "소스 컨트롤 툴바")
        ]
    

    
    def _get_available_categories(self, all_categories):
        """설정 파일에 실제로 존재하는 카테고리만 반환"""
        available_categories = []
        
        # 기본 카테고리들 (처음 10개)
        default_categories = {
            "OnSelectFolderMenu", "OnSelectAssetsMenu", "OnMainMenu", "OnToolbar",
            "OnToolBarChameleon", "OnOutlineMenu", "OnMaterialEditorMenu",
            "OnPhysicsAssetEditorMenu", "OnControlRigEditorMenu", "OnTabContextMenu"
        }
        
        # 기본 카테고리들은 항상 표시 (데이터가 없어도)
        for category_id, category_name in all_categories:
            if category_id in default_categories:
                available_categories.append((category_id, category_name))
        
        # Tool Menu Anchor들은 설정 파일에 실제로 존재하는 것만 표시
        if self.config_data:
            for category_id, category_name in all_categories:
                if category_id not in default_categories and category_id in self.config_data:
                    available_categories.append((category_id, category_name))
        
        return available_categories
    
    def refresh_tabs_if_needed(self):
        """새로운 카테고리가 추가되었을 때 카테고리 리스트 새로고침"""
        self.refresh_category_list()
    
    def create_tab_content(self, parent, category_id):
        """탭 내용 생성 - 새 레이아웃에서는 create_category_content와 동일"""
        return self.create_category_content(parent, category_id)
    
    def _create_left_panel(self, parent, category_id):
        """좌측 패널 (아이템 목록) 생성"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        
        # 좌측 프레임의 폭을 제한
        left_frame.pack_propagate(False)
        left_frame.configure(width=380)
        
        # 카테고리 정보 및 설정
        self._create_category_info_section(left_frame, category_id)
        
        ttk.Label(left_frame, text="메뉴 아이템", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 트리뷰 생성
        treeview = self._create_treeview(left_frame, category_id)
        
        # 컨트롤 버튼들
        self._create_control_buttons(left_frame, category_id)
        
        return {'treeview': treeview}
    
    def _create_category_info_section(self, parent, category_id):
        """카테고리 정보 및 설정 섹션 생성"""
        info_frame = ttk.LabelFrame(parent, text="카테고리 설정")
        info_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # 카테고리 이름 표시
        display_name = category_id.replace(".", " > ") if "." in category_id else category_id
        ttk.Label(info_frame, text=f"카테고리: {display_name}", 
                 font=("Arial", 8, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # Tool Menu Anchor인지 확인
        is_tool_menu_anchor = "." in category_id and category_id not in [
            "OnSelectFolderMenu", "OnSelectAssetsMenu", "OnMainMenu", "OnToolbar",
            "OnToolBarChameleon", "OnOutlineMenu", "OnMaterialEditorMenu",
            "OnPhysicsAssetEditorMenu", "OnControlRigEditorMenu", "OnTabContextMenu"
        ]
        
        if is_tool_menu_anchor:
            # HasSection 설정 (Tool Menu Anchor만)
            has_section_var = tk.BooleanVar()
            # 현재 설정값 로드
            current_has_section = self.config_data.get(category_id, {}).get("HasSection", True)
            has_section_var.set(current_has_section)
            
            has_section_check = ttk.Checkbutton(
                info_frame, 
                text="HasSection (구분선 표시)", 
                variable=has_section_var,
                command=lambda: self._update_category_has_section(category_id, has_section_var.get())
            )
            has_section_check.pack(anchor=tk.W, padx=5, pady=2)
            
            # 툴팁 추가
            tooltip_text = """Tool Menu Anchor의 구분선 표시 여부를 설정합니다.

• 체크: 구분선이 표시됩니다 (기본값)
• 체크 해제: 구분선이 숨겨집니다 (툴바에서 권장)"""
            self.create_tooltip(has_section_check, tooltip_text)
            
            # 툴바인 경우 권장사항 표시
            if "ToolBar" in category_id or "Toolbar" in category_id:
                ttk.Label(info_frame, text="💡 툴바에서는 HasSection=false 권장", 
                         font=("Arial", 7), foreground="blue").pack(anchor=tk.W, padx=5, pady=1)
    
    def _update_category_has_section(self, category_id, has_section_value):
        """카테고리의 HasSection 값 업데이트"""
        try:
            # config_data에서 카테고리 확인/생성
            if category_id not in self.config_data:
                self.config_data[category_id] = {"items": []}
            
            # HasSection 값 설정
            if has_section_value:
                self.config_data[category_id]["HasSection"] = True
            else:
                self.config_data[category_id]["HasSection"] = False
            
            # 변경사항 추적
            self.mark_as_modified()
            
            # 상태 메시지
            status_msg = f"✅ HasSection = {has_section_value}" if has_section_value else f"❌ HasSection = {has_section_value}"
            self.update_status(f"🔧 '{category_id}' {status_msg}")
            
            logger.debug(f"카테고리 '{category_id}'의 HasSection을 {has_section_value}로 설정")
            
        except Exception as e:
            error_msg = f"HasSection 설정 중 오류: {str(e)}"
            logger.error(error_msg)
            self._show_error("오류", error_msg)
    
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
        
        # canExecuteAction 필드 (새로 추가)
        widgets.update(self._create_can_execute_action_field(edit_frame))
        
        # Chameleon 필드 (순서 변경)
        widgets.update(self._create_chameleon_field(edit_frame))
        
        # 아이콘 필드 (새로 추가)
        widgets.update(self._create_icon_field(edit_frame))
        
        # 업데이트 버튼
        widgets.update(self._create_update_button(edit_frame, category_id))
        
        # 그리드 가중치
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(3, weight=1)  # 명령어 필드가 확장되도록
        
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
        """Chameleon Tools 설정 필드 생성"""
        chameleon_frame = ttk.LabelFrame(parent, text="Chameleon Tools 설정")
        chameleon_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        chameleon_frame.columnconfigure(1, weight=1)
        
        # Chameleon Tools 경로
        ttk.Label(chameleon_frame, text="JSON 파일 경로:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # 경로 입력과 파일 선택 버튼을 같은 줄에 배치
        path_frame = ttk.Frame(chameleon_frame)
        path_frame.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        path_frame.columnconfigure(0, weight=1)
        
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(path_frame, textvariable=chameleon_var)
        chameleon_entry.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(0, 5))
        
        # 파일 선택 버튼
        def select_chameleon_file():
            file_path = filedialog.askopenfilename(
                title="Chameleon Tools JSON 파일 선택",
                filetypes=[
                    ("JSON 파일", "*.json"),
                    ("모든 파일", "*.*")
                ],
                initialdir=self._get_chameleon_tools_directory()
            )
            if file_path:
                # 상대 경로로 변환
                relative_path = self._convert_to_relative_path(file_path)
                chameleon_var.set(relative_path)
        
        chameleon_button = ttk.Button(path_frame, text="📁", command=select_chameleon_file, width=3)
        chameleon_button.grid(row=0, column=1)
        
        # 간단한 예시 하나만
        example_text = "예시: ../Python/Example/MinimalExample.json"
        ttk.Label(chameleon_frame, text=example_text, font=("Arial", 8), 
                 foreground="gray").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=1)
        
        return {'chameleon_var': chameleon_var, 'chameleon_entry': chameleon_entry, 'chameleon_button': chameleon_button}
    
    def _create_can_execute_action_field(self, parent):
        """canExecuteAction 입력 필드 생성"""
        ttk.Label(parent, text="canExecuteAction:").grid(row=5, column=0, sticky=tk.NW+tk.W, padx=(0, 5), pady=2)
        
        can_exec_frame = ttk.Frame(parent)
        can_exec_frame.grid(row=5, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=2)
        
        can_execute_text = tk.Text(can_exec_frame, height=3, width=40, wrap=tk.WORD)
        can_exec_scrollbar = ttk.Scrollbar(can_exec_frame, orient=tk.VERTICAL, command=can_execute_text.yview)
        can_execute_text.configure(yscrollcommand=can_exec_scrollbar.set)
        
        can_execute_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        can_exec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 툴팁 추가
        self.create_tooltip(can_execute_text, 
                           "메뉴 항목 클릭 가능 여부를 결정하는 Python 코드\n"
                           "True를 반환하면 클릭 가능, False면 비활성화")
        
        return {'can_execute_text': can_execute_text}
    
    def _create_icon_field(self, parent):
        """아이콘 설정 필드 생성"""
        icon_frame = ttk.LabelFrame(parent, text="아이콘 설정")
        icon_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        icon_frame.columnconfigure(1, weight=1)
        
        # 아이콘 타입 선택
        ttk.Label(icon_frame, text="아이콘 타입:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        icon_type_var = tk.StringVar(value="없음")
        icon_type_combo = ttk.Combobox(icon_frame, textvariable=icon_type_var, 
                                      values=["없음", "EditorStyle", "ChameleonStyle", "ImagePath"], 
                                      state="readonly", width=15)
        icon_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 아이콘 이름/경로
        ttk.Label(icon_frame, text="아이콘 이름/경로:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        icon_name_var = tk.StringVar()
        icon_name_entry = ttk.Entry(icon_frame, textvariable=icon_name_var, width=40)
        icon_name_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        # 예시 텍스트
        example_text = "예: LevelEditor.Tabs.Details (EditorStyle) / Resources/flash_32x.png (ImagePath)"
        ttk.Label(icon_frame, text=example_text, font=("Arial", 8), 
                 foreground="gray").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        return {
            'icon_type_var': icon_type_var, 
            'icon_type_combo': icon_type_combo,
            'icon_name_var': icon_name_var, 
            'icon_name_entry': icon_name_entry
        }
    
    def _get_chameleon_tools_directory(self):
        """Chameleon Tools 디렉토리 경로 반환"""
        try:
            # 기본 설정 파일 경로에서 TAPython 디렉토리 찾기
            config_dir = os.path.dirname(self.default_config_path)
            tapython_root = os.path.dirname(config_dir)  # TA 폴더에서 한 단계 위로
            python_dir = os.path.join(tapython_root, "Python")
            
            if os.path.exists(python_dir):
                return python_dir
            
            # 대체 경로들 시도
            alternative_paths = [
                os.path.join(tapython_root, "Content", "Python"),
                os.path.join(os.path.dirname(tapython_root), "TAPython", "Python"),
                os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트 디렉토리
            ]
            
            for path in alternative_paths:
                if os.path.exists(path):
                    return path
            
            # 마지막 대안: 현재 설정 파일 디렉토리
            return config_dir
            
        except Exception as e:
            logger.warning(f"Chameleon Tools 디렉토리 찾기 실패: {e}")
            return os.path.dirname(os.path.abspath(__file__))
    
    def _convert_to_relative_path(self, absolute_path):
        """절대 경로를 TAPython 기준 상대 경로로 변환"""
        try:
            # TAPython 루트 디렉토리 찾기
            config_dir = os.path.dirname(self.default_config_path)
            tapython_root = os.path.dirname(config_dir)
            
            # 절대 경로를 상대 경로로 변환
            relative_path = os.path.relpath(absolute_path, tapython_root)
            
            # 백슬래시를 슬래시로 변환 (JSON에서 사용)
            relative_path = relative_path.replace('\\', '/')
            
            # ../ 로 시작하지 않으면 추가
            if not relative_path.startswith('../'):
                relative_path = '../' + relative_path
            
            return relative_path
            
        except Exception as e:
            logger.warning(f"상대 경로 변환 실패: {e}")
            # 실패하면 파일명만 반환
            return '../Python/' + os.path.basename(absolute_path)
    
    def _create_update_button(self, parent, category_id):
        """업데이트 버튼 생성"""
        update_btn = ttk.Button(parent, text="💾 변경사항 저장", 
                               command=lambda: self.update_item(category_id))
        update_btn.grid(row=9, column=1, sticky=tk.W, pady=(10, 0))
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
            self.refresh_tabs_if_needed()  # 새로운 카테고리 확인 및 탭 추가
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
            traceback.print_exc()
            self._show_error("오류", error_msg)
            self.update_status(f"❌ 저장 실패: {str(e)}", auto_clear=False)
    
    def save_as_config(self):
        """다른 이름으로 저장"""
        # 초기 디렉토리 결정
        initial_dir = os.path.dirname(self.default_config_path)
        
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
        """모든 탭 새로고침 - 새 레이아웃에서는 현재 선택된 카테고리만 새로고침"""
        if self.current_category_id:
            self.refresh_current_category()
    
    def refresh_current_category(self):
        """현재 선택된 카테고리 새로고침"""
        if self.current_category_id and self.current_widgets:
            self.refresh_tab(self.current_category_id)
    
    def refresh_tab(self, category_id):
        """특정 탭 새로고침"""
        # 현재 선택된 카테고리인지 확인
        if category_id != self.current_category_id:
            return
        
        if not self.current_menu_treeview:
            return
        
        treeview = self.current_menu_treeview
        
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
        # 현재 카테고리인지 확인
        if category_id != self.current_category_id or not self.current_widgets:
            return
        
        # 패널 제목 업데이트 (아이템 선택 해제)
        category_name = None
        for cat_id, cat_name in self.category_data.values():
            if cat_id == self.current_category_id:
                category_name = cat_name
                break
        self.update_panel_titles(category_name=category_name, item_name=None)
        
        tab_widgets = self.current_widgets
        tab_widgets['name_var'].set("")
        tab_widgets['tooltip_var'].set("")
        tab_widgets['enabled_var'].set(True)
        tab_widgets['command_text'].delete(1.0, tk.END)
        tab_widgets['can_execute_text'].delete(1.0, tk.END)
        tab_widgets['chameleon_var'].set("")
        tab_widgets['icon_type_var'].set("없음")
        tab_widgets['icon_name_var'].set("")
        
        # 편집 불가능 상태로 설정
        self.set_edit_state(category_id, False)
    
    def set_edit_state(self, category_id, enabled):
        """편집 폼 활성화/비활성화"""
        # 현재 카테고리인지 확인
        if category_id != self.current_category_id or not self.current_widgets:
            return
        
        tab_widgets = self.current_widgets
        state = tk.NORMAL if enabled else tk.DISABLED
        
        widgets = [
            tab_widgets['name_entry'],
            tab_widgets['tooltip_entry'],
            tab_widgets['chameleon_entry'],
            tab_widgets['chameleon_button'],  # 파일 피커 버튼 추가
            tab_widgets['enabled_check'],
            tab_widgets['command_text'],
            tab_widgets['can_execute_text'],
            tab_widgets['icon_type_combo'],
            tab_widgets['icon_name_entry'],
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
            # 현재 선택된 카테고리가 아니면 리턴
            if category_id != self.current_category_id or not self.current_widgets:
                return
            
            if not self.current_menu_treeview:
                return
            
            treeview = self.current_menu_treeview
            tab_widgets = self.current_widgets
            
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
                
                # 패널 제목 업데이트 (아이템 선택됨)
                item_name = item_data.get("name", "")
                category_name = None
                # 현재 카테고리 이름 찾기
                for cat_id, cat_name in self.category_data.values():
                    if cat_id == self.current_category_id:
                        category_name = cat_name
                        break
                self.update_panel_titles(category_name=category_name, item_name=item_name)
                
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
                
                # canExecuteAction (새로 추가)
                tab_widgets['can_execute_text'].delete(1.0, tk.END)
                can_execute = item_data.get("canExecuteAction", "")
                if can_execute:
                    tab_widgets['can_execute_text'].insert(1.0, can_execute)
                
                # 아이콘 설정 (새로 추가)
                icon_data = item_data.get("icon", {})
                if icon_data:
                    if "style" in icon_data:
                        style = icon_data.get("style", "")
                        if style == "EditorStyle":
                            tab_widgets['icon_type_var'].set("EditorStyle")
                        elif style == "ChameleonStyle":
                            tab_widgets['icon_type_var'].set("ChameleonStyle")
                        tab_widgets['icon_name_var'].set(icon_data.get("name", ""))
                    elif "ImagePathInPlugin" in icon_data:
                        tab_widgets['icon_type_var'].set("ImagePath")
                        tab_widgets['icon_name_var'].set(icon_data.get("ImagePathInPlugin", ""))
                    else:
                        tab_widgets['icon_type_var'].set("없음")
                        tab_widgets['icon_name_var'].set("")
                else:
                    tab_widgets['icon_type_var'].set("없음")
                    tab_widgets['icon_name_var'].set("")
                
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
            # 현재 선택된 카테고리가 아니면 리턴
            if category_id != self.current_category_id or not self.current_widgets:
                return
            
            tab_widgets = self.current_widgets
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
            
            # canExecuteAction 처리 (새로 추가)
            can_execute_raw = tab_widgets['can_execute_text'].get(1.0, tk.END)
            can_execute = can_execute_raw.rstrip('\n').strip()
            if can_execute:
                item_data["canExecuteAction"] = can_execute
            elif "canExecuteAction" in item_data:
                del item_data["canExecuteAction"]  # 빈 값이면 키 삭제
            
            # 아이콘 설정 처리 (새로 추가)
            icon_type = tab_widgets['icon_type_var'].get()
            icon_name = tab_widgets['icon_name_var'].get().strip()
            
            if icon_type != "없음" and icon_name:
                icon_data = {}
                if icon_type == "EditorStyle":
                    icon_data = {"style": "EditorStyle", "name": icon_name}
                elif icon_type == "ChameleonStyle":
                    icon_data = {"style": "ChameleonStyle", "name": icon_name}
                elif icon_type == "ImagePath":
                    icon_data = {"ImagePathInPlugin": icon_name}
                
                if icon_data:
                    item_data["icon"] = icon_data
            elif "icon" in item_data:
                del item_data["icon"]  # 아이콘 설정이 없으면 키 삭제
            
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
            traceback.print_exc()
            self._show_error("오류", error_msg)
            self.update_status(f"저장 실패: {str(e)}", auto_clear=False)
    
    def add_item(self, category_id):
        """아이템 추가"""
        # modal 창으로 열어 포커스 유지
        self.add_item_dialog(category_id, modal=True)
    
    def add_submenu(self, category_id):
        """서브메뉴 추가"""
        # modal 창으로 열어 포커스 유지
        self.add_submenu_dialog(category_id, modal=True)
    
    def add_submenu_dialog(self, category_id, modal=True):
        """서브메뉴 추가 다이얼로그 (기본적으로 modal로 설정)"""
        # 현재 카테고리가 없으면 리턴
        if not self.current_category_id or not self.current_widgets:
            self._show_warning("경고", "카테고리를 먼저 선택해주세요.")
            return
        
        dialog = tk.Toplevel(self.root)
        
        # 사용자가 원하는 경우 modal로 설정
        self._setup_dialog(dialog, "새 서브메뉴 추가", 450, 225, modal=modal)
        
        # 서브메뉴를 추가할 부모 선택
        tab_widgets = self.current_widgets
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
    
    def add_item_dialog(self, category_id=None, modal=True):
        """아이템 추가 다이얼로그 (기본적으로 modal로 설정)"""
        dialog = tk.Toplevel(self.root)
        
        # 사용자가 원하는 경우 modal로 설정하여 포커스 유지
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
            # 현재 카테고리가 있는지 확인
            if not self.current_category_id or not self.current_widgets:
                self._show_warning("경고", "카테고리를 먼저 선택해주세요.")
                dialog.destroy()
                return
            
            ttk.Label(dialog, text="부모 아이템:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            parent_combo = ttk.Combobox(dialog, textvariable=parent_var, state="readonly")
            parent_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            
            # 부모 아이템 목록 구성
            tab_widgets = self.current_widgets
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
                
                # Tool Menu Anchor인 경우 새로고침 안내
                if "." in selected_category and selected_category not in [
                    "OnSelectFolderMenu", "OnSelectAssetsMenu", "OnMainMenu", "OnToolbar", 
                    "OnToolBarChameleon", "OnOutlineMenu", "OnMaterialEditorMenu", 
                    "OnPhysicsAssetEditorMenu", "OnControlRigEditorMenu", "OnTabContextMenu"
                ]:
                    self.update_status(f"➕ Tool Menu Anchor 아이템 '{name}' 추가됨 - 'TAPython.RefreshToolMenus' 실행 필요")
                else:
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
        # 현재 카테고리가 없으면 리턴
        if not self.current_category_id or not self.current_widgets:
            self._show_warning("경고", "카테고리를 먼저 선택해주세요.")
            return
        
        tab_widgets = self.current_widgets
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
        # 현재 카테고리가 없으면 리턴
        if not self.current_category_id or not self.current_widgets:
            return
        
        tab_widgets = self.current_widgets
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
        # 현재 카테고리가 없으면 리턴
        if not self.current_category_id or not self.current_widgets:
            return
        
        tab_widgets = self.current_widgets
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
    
    def add_tool_menu_anchor_dialog(self):
        """Tool Menu Anchor 추가 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        self._setup_dialog(dialog, "새 Tool Menu Anchor 추가", 600, 400, modal=True)
        
        # 메인 프레임
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 설명
        desc_text = """Tool Menu Anchor를 사용하면 Unreal Engine의 다양한 위치에 메뉴를 추가할 수 있습니다.
아래에서 Anchor 이름을 입력하거나 미리 정의된 목록에서 선택하세요."""
        ttk.Label(main_frame, text=desc_text, wraplength=550, 
                 font=("Arial", 9), foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # Anchor 입력
        ttk.Label(main_frame, text="Tool Menu Anchor 이름:").pack(anchor=tk.W, pady=(0, 5))
        anchor_var = tk.StringVar()
        anchor_entry = ttk.Entry(main_frame, textvariable=anchor_var, width=60)
        anchor_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 미리 정의된 Anchor 목록
        ttk.Label(main_frame, text="미리 정의된 Tool Menu Anchors:").pack(anchor=tk.W, pady=(10, 5))
        
        # 리스트박스와 스크롤바
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # 미리 정의된 Anchor들 추가
        predefined_anchors = [
            "AssetEditor.AnimationBlueprintEditor.MainMenu",
            "AssetEditor.AnimationEditor.MainMenu",
            "AssetEditor.SkeletalMeshEditor.ToolBar",
            "AssetEditor.StaticMeshEditor.ToolBar",
            "ContentBrowser.AddNewContextMenu",
            "ContentBrowser.AssetContextMenu",
            "ContentBrowser.AssetContextMenu.AnimBlueprint",
            "ContentBrowser.AssetContextMenu.AnimSequence",
            "ContentBrowser.AssetContextMenu.SkeletalMesh",
            "ContentBrowser.AssetContextMenu.StaticMesh",
            "ContentBrowser.AssetContextMenu.World",
            "ContentBrowser.FolderContextMenu",
            "ContentBrowser.ToolBar",
            "Kismet.SubobjectEditorContextMenu",
            "Kismet.SCSEditorContextMenu",
            "ControlRigEditor.RigHierarchy.ContextMenu",
            "LevelEditor.ActorContextMenu.AssetToolsSubMenu",
            "LevelEditor.LevelEditorToolBar",
            "LevelEditor.LevelViewportToolBar.Options",
            "LevelEditor.MainMenu.Build",
            "LevelEditor.MainMenu.File",
            "LevelEditor.MainMenu.Tools",
            "MainFrame.MainMenu.Asset",
            "MainFrame.MainMenu.Tools"
        ]
        
        for anchor in predefined_anchors:
            listbox.insert(tk.END, anchor)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스 선택 시 입력 필드에 복사
        def on_listbox_select(event):
            selection = listbox.curselection()
            if selection:
                anchor_var.set(listbox.get(selection[0]))
        
        listbox.bind("<<ListboxSelect>>", on_listbox_select)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # HasSection 설정 (Tool Menu Anchor 전용)
        has_section_frame = ttk.Frame(main_frame)
        has_section_frame.pack(fill=tk.X, pady=(10, 0))
        
        has_section_var = tk.BooleanVar(value=True)  # 기본값 True
        has_section_check = ttk.Checkbutton(
            has_section_frame, 
            text="HasSection (구분선 표시) - 새 Tool Menu Anchor의 기본 설정", 
            variable=has_section_var
        )
        has_section_check.pack(anchor=tk.W)
        
        # 툴팁 추가
        tooltip_text = """새로 추가될 Tool Menu Anchor의 HasSection 기본값을 설정합니다.

• 체크: 구분선이 표시됩니다 (기본값)
• 체크 해제: 구분선이 숨겨집니다 (툴바에서 권장)"""
        self.create_tooltip(has_section_check, tooltip_text)
        
        def add_anchor():
            anchor_name = anchor_var.get().strip()
            has_section_value = has_section_var.get()
            
            if not anchor_name:
                self._show_warning("경고", "Tool Menu Anchor 이름을 입력해주세요.")
                return
            
            # 새로운 카테고리로 추가
            if anchor_name not in self.config_data:
                self.config_data[anchor_name] = {
                    "HasSection": has_section_value,
                    "items": []
                }
                self.mark_as_modified()
                
                # 새로운 카테고리 추가 후 카테고리 리스트 새로고침
                self.mark_as_modified()
                self.refresh_category_list()
                
                status_msg = f"HasSection={has_section_value}" 
                self.update_status(f"🔧 Tool Menu Anchor '{anchor_name}' 추가됨 ({status_msg})")
                dialog.destroy()
            else:
                self._show_warning("중복", f"'{anchor_name}'는 이미 존재합니다.")
        
        ttk.Button(button_frame, text="✅ 추가", command=add_anchor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT)
        
        anchor_entry.focus_set()
    
    def remove_tool_menu_anchor_dialog(self):
        """Tool Menu Anchor 삭제 다이얼로그"""
        # 삭제 가능한 Tool Menu Anchor 목록 생성 (기본 카테고리 제외)
        default_categories = {
            "OnSelectFolderMenu", "OnSelectAssetsMenu", "OnMainMenu", "OnToolbar",
            "OnToolBarChameleon", "OnOutlineMenu", "OnMaterialEditorMenu",
            "OnPhysicsAssetEditorMenu", "OnControlRigEditorMenu", "OnTabContextMenu"
        }
        
        removable_anchors = []
        for category_id in self.config_data.keys():
            if category_id not in default_categories:
                removable_anchors.append(category_id)
        
        if not removable_anchors:
            messagebox.showinfo("정보", "삭제할 수 있는 Tool Menu Anchor가 없습니다.\n기본 메뉴 카테고리는 삭제할 수 없습니다.")
            return
        
        dialog = tk.Toplevel(self.root)
        self._setup_dialog(dialog, "Tool Menu Anchor 삭제", 500, 350, modal=True)
        
        # 메인 프레임
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 설명
        desc_text = """삭제할 Tool Menu Anchor를 선택하세요.
삭제하면 해당 카테고리의 모든 메뉴 아이템이 함께 제거됩니다.
기본 메뉴 카테고리는 삭제할 수 없습니다."""
        ttk.Label(main_frame, text=desc_text, wraplength=450, 
                 font=("Arial", 9), foreground="red").pack(anchor=tk.W, pady=(0, 10))
        
        # 삭제할 Anchor 선택
        ttk.Label(main_frame, text="삭제할 Tool Menu Anchor:").pack(anchor=tk.W, pady=(0, 5))
        
        # 리스트박스와 스크롤바
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # 삭제 가능한 Anchor들 추가
        for anchor in sorted(removable_anchors):
            # 아이템 개수도 함께 표시
            item_count = len(self.config_data.get(anchor, {}).get("items", []))
            display_text = f"{anchor} ({item_count}개 아이템)"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 선택된 항목 정보 표시
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_label = ttk.Label(info_frame, text="삭제할 항목을 선택하세요.", 
                              font=("Arial", 9), foreground="gray")
        info_label.pack(anchor=tk.W)
        
        def on_listbox_select(event):
            selection = listbox.curselection()
            if selection:
                selected_text = listbox.get(selection[0])
                anchor_name = selected_text.split(" (")[0]  # " (n개 아이템)" 부분 제거
                item_count = len(self.config_data.get(anchor_name, {}).get("items", []))
                info_label.configure(
                    text=f"선택: {anchor_name}\n아이템 수: {item_count}개\n⚠️ 이 카테고리의 모든 데이터가 삭제됩니다!",
                    foreground="red"
                )
        
        listbox.bind("<<ListboxSelect>>", on_listbox_select)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def remove_anchor():
            selection = listbox.curselection()
            if not selection:
                self._show_warning("경고", "삭제할 Tool Menu Anchor를 선택해주세요.")
                return
            
            selected_text = listbox.get(selection[0])
            anchor_name = selected_text.split(" (")[0]  # " (n개 아이템)" 부분 제거
            item_count = len(self.config_data.get(anchor_name, {}).get("items", []))
            
            # 최종 확인
            confirm_msg = f"정말로 '{anchor_name}'를 삭제하시겠습니까?\n\n"
            confirm_msg += f"• {item_count}개의 메뉴 아이템이 함께 삭제됩니다.\n"
            confirm_msg += "• 이 작업은 되돌릴 수 없습니다.\n"
            confirm_msg += "• 현재 설정을 저장하지 않았다면 먼저 저장하는 것을 권장합니다."
            
            if messagebox.askyesno("삭제 확인", confirm_msg, icon="warning"):
                try:
                    # config_data에서 제거
                    if anchor_name in self.config_data:
                        del self.config_data[anchor_name]
                    
                    # 현재 선택된 카테고리가 삭제된 카테고리인 경우 초기화
                    if self.current_category_id == anchor_name:
                        self.clear_content_area()
                    
                    self.mark_as_modified()
                    self.refresh_category_list()
                    self.update_status(f"🗑️ Tool Menu Anchor '{anchor_name}' 삭제됨!")
                    dialog.destroy()
                    
                except Exception as e:
                    error_msg = f"Tool Menu Anchor 삭제 중 오류: {str(e)}"
                    logger.error(error_msg)
                    self._show_error("오류", error_msg)
        
        ttk.Button(button_frame, text="🗑️ 삭제", command=remove_anchor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT)
        
        # 첫 번째 항목 자동 선택
        if removable_anchors:
            listbox.selection_set(0)
            on_listbox_select(None)
    
    def refresh_tool_menus(self):
        """Tool Menu 새로고침 (Unreal Engine 명령 실행)"""
        try:
            if UNREAL_AVAILABLE:
                # Unreal Engine에서 Tool Menu 새로고침 명령 실행
                unreal.SystemLibrary.execute_console_command(unreal.EditorLevelLibrary.get_editor_world(), "TAPython.RefreshToolMenus")
                self.update_status("🔄 Tool Menu가 새로고침되었습니다!")
                logger.info("Tool Menu 새로고침 명령 실행됨")
            else:
                # 독립 실행 모드에서는 메시지만 표시
                message = """Tool Menu 새로고침은 Unreal Engine 내에서만 가능합니다.

Unreal Engine의 콘솔에서 다음 명령을 실행하세요:
TAPython.RefreshToolMenus"""
                messagebox.showinfo("Tool Menu 새로고침", message)
                self.update_status("💡 Unreal Engine에서 'TAPython.RefreshToolMenus' 명령을 실행하세요")
        except Exception as e:
            error_msg = f"Tool Menu 새로고침 중 오류: {str(e)}"
            logger.error(error_msg)
            self._show_error("오류", error_msg)
    
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
        traceback.print_exc()
    finally:
        # 최종 리소스 정리 (앱이 정상적으로 정리되지 않은 경우에만)
        if app and not getattr(app, '_resources_cleaned', False):
            try:
                app.cleanup_resources()
            except:
                pass


class NewCategoryDialog:
    """새 카테고리 추가 다이얼로그"""
    
    def __init__(self, parent):
        self.result = None
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("새 카테고리 추가")
        self.dialog.geometry("600x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 중앙 정렬
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """다이얼로그 UI 설정"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ttk.Label(main_frame, text="새 메뉴 카테고리 추가", font=("맑은 고딕", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 카테고리 타입 선택
        type_frame = ttk.LabelFrame(main_frame, text="카테고리 타입", padding=10)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.category_type = tk.StringVar(value="traditional")
        ttk.Radiobutton(type_frame, text="전통적인 메뉴 (예: OnSelectFolderMenu)", 
                       variable=self.category_type, value="traditional", 
                       command=self.on_type_change).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(type_frame, text="Tool Menu Anchor (예: LevelEditor.MainMenu.Tools)", 
                       variable=self.category_type, value="anchor", 
                       command=self.on_type_change).pack(anchor=tk.W, pady=2)
        
        # 카테고리 ID 입력
        ttk.Label(main_frame, text="카테고리 ID:").pack(anchor=tk.W)
        self.category_id_entry = ttk.Entry(main_frame, width=50)
        self.category_id_entry.pack(fill=tk.X, pady=(5, 10))
        
        # 카테고리 이름 입력
        ttk.Label(main_frame, text="카테고리 이름:").pack(anchor=tk.W)
        self.category_name_entry = ttk.Entry(main_frame, width=50)
        self.category_name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Tool Menu Anchor 전용 옵션
        self.anchor_options_frame = ttk.LabelFrame(main_frame, text="Tool Menu Anchor 옵션", padding=10)
        self.anchor_options_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.has_section_var = tk.BooleanVar(value=True)
        self.has_section_check = ttk.Checkbutton(
            self.anchor_options_frame, 
            text="HasSection (구분선 표시)", 
            variable=self.has_section_var
        )
        self.has_section_check.pack(anchor=tk.W)
        
        # 미리 정의된 Tool Menu Anchor 목록
        self.predefined_frame = ttk.LabelFrame(main_frame, text="미리 정의된 Tool Menu Anchors", padding=10)
        self.predefined_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 리스트박스
        listbox_frame = ttk.Frame(self.predefined_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.anchor_listbox = tk.Listbox(listbox_frame, height=6)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.anchor_listbox.yview)
        self.anchor_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 미리 정의된 Anchor들 추가
        predefined_anchors = [
            "LevelEditor.MainMenu.Tools",
            "LevelEditor.MainMenu.Build", 
            "LevelEditor.LevelEditorToolBar",
            "ContentBrowser.ToolBar",
            "ContentBrowser.AssetContextMenu",
            "AssetEditor.StaticMeshEditor.ToolBar",
            "AssetEditor.SkeletalMeshEditor.ToolBar",
            "MainFrame.MainMenu.Tools"
        ]
        
        for anchor in predefined_anchors:
            self.anchor_listbox.insert(tk.END, anchor)
        
        self.anchor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스 선택 시 ID 필드에 복사
        self.anchor_listbox.bind("<<ListboxSelect>>", self.on_anchor_select)
        
        # 설명
        self.info_label = ttk.Label(main_frame, foreground="gray")
        self.info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 초기 상태 설정
        self.on_type_change()
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="추가", command=self.ok).pack(side=tk.RIGHT)
        
        # Enter 키 바인딩
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # 포커스 설정
        self.category_id_entry.focus()
    
    def on_type_change(self):
        """카테고리 타입 변경 시 UI 업데이트"""
        is_anchor = self.category_type.get() == "anchor"
        
        # Tool Menu Anchor 전용 옵션 표시/숨김
        if is_anchor:
            self.anchor_options_frame.pack(fill=tk.X, pady=(10, 15))
            self.predefined_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            self.info_label.configure(text="• Tool Menu Anchor는 점(.)이 포함된 형식입니다\n• HasSection으로 구분선 표시 여부를 설정할 수 있습니다")
        else:
            self.anchor_options_frame.pack_forget()
            self.predefined_frame.pack_forget()
            self.info_label.configure(text="• 전통적인 메뉴는 'OnSelectFolderMenu' 같은 형식입니다\n• 카테고리 ID는 고유해야 합니다")
    
    def on_anchor_select(self, event):
        """미리 정의된 Anchor 선택 시 ID 필드에 복사"""
        selection = self.anchor_listbox.curselection()
        if selection:
            anchor_name = self.anchor_listbox.get(selection[0])
            self.category_id_entry.delete(0, tk.END)
            self.category_id_entry.insert(0, anchor_name)
            # 이름 필드가 비어있으면 ID에서 추출해서 채움
            if not self.category_name_entry.get().strip():
                display_name = anchor_name.split('.')[-1]  # 마지막 부분만 사용
                self.category_name_entry.delete(0, tk.END)
                self.category_name_entry.insert(0, display_name)
    
    def ok(self):
        """확인 버튼"""
        category_id = self.category_id_entry.get().strip()
        category_name = self.category_name_entry.get().strip()
        
        if not category_id:
            messagebox.showerror("오류", "카테고리 ID를 입력하세요.")
            return
        
        if not category_name:
            messagebox.showerror("오류", "카테고리 이름을 입력하세요.")
            return
        
        # Tool Menu Anchor 타입인 경우 추가 정보 포함
        is_anchor = self.category_type.get() == "anchor"
        if is_anchor:
            has_section = self.has_section_var.get()
            self.result = (category_id, category_name, True, has_section)  # (id, name, is_anchor, has_section)
        else:
            self.result = (category_id, category_name, False, None)  # (id, name, is_anchor, has_section)
        
        self.dialog.destroy()
    
    def cancel(self):
        """취소 버튼"""
        self.dialog.destroy()


if __name__ == "__main__":
    main()