#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple MenuConfig Editor
TAPython MenuConfig.json을 간단하게 편집할 수 있는 툴
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any

try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False


class SimpleMenuEditor:
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
        self.root.title("TAPython MenuConfig Editor")
        self.root.geometry("1000x700")
        
        self.config_data = {}
        self.config_file_path = ""
        
        # 기본 경로 설정 - unreal.Paths 사용
        self.default_config_path = self._find_default_config_path()
        
        self.setup_ui()
        self.load_default_config()
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _find_default_config_path(self):
        """unreal.Paths를 사용하여 기본 설정 파일 경로 찾기"""
        if UNREAL_AVAILABLE:
            try:
                # Unreal Engine 프로젝트 경로 가져오기
                project_dir = unreal.Paths.project_dir()
                
                # TAPython 플러그인 경로들 시도 (유효한 경로 우선)
                possible_paths = [
                    # 유효한 경로를 첫 번째로 배치
                    os.path.join(project_dir, "TA", "TAPython", "UI", "MenuConfig.json"),
                    # 다른 가능한 경로들
                    os.path.join(project_dir, "Plugins", "TAPython", "UI", "MenuConfig.json"),
                    os.path.join(project_dir, "Plugins", "MaidCat", "UI", "MenuConfig.json"),
                    # Engine 플러그인 경로
                    os.path.join(unreal.Paths.engine_plugins_dir(), "TAPython", "UI", "MenuConfig.json"),
                ]
                
                # 존재하는 첫 번째 파일 경로 반환
                for path in possible_paths:
                    if os.path.exists(path):
                        return path
                
                # 모든 경로에서 찾지 못한 경우 유효한 경로를 기본값으로 사용
                return possible_paths[0]
                
            except Exception as e:
                print(f"Unreal Paths 사용 중 오류: {e}")
                # fallback to script directory based path
                pass
        
        # Unreal을 사용할 수 없거나 오류가 발생한 경우 기존 방식 사용
        script_dir = os.path.dirname(__file__)
        return os.path.join(
            os.path.dirname(os.path.dirname(script_dir)), 
            "UI", "MenuConfig.json"
        )
    
    def setup_ui(self):
        """UI 구성"""
        # 메뉴바
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 파일", menu=file_menu)
        file_menu.add_command(label="📂 열기", command=self.open_config)
        file_menu.add_command(label="💾 저장", command=self.save_config)
        file_menu.add_command(label="📄 다른 이름으로 저장", command=self.save_as_config)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 새로고침", command=self.reload_config)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ 편집", menu=edit_menu)
        edit_menu.add_command(label="➕ 아이템 추가", command=self.add_item_dialog)
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        # 상단 정보
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_label = ttk.Label(info_frame, text="파일: 없음", foreground="gray")
        self.file_label.pack(side=tk.LEFT)
        
        # Unreal 상태 표시
        unreal_status = "Unreal Engine 연결됨" if UNREAL_AVAILABLE else "독립 실행 모드"
        status_color = "green" if UNREAL_AVAILABLE else "orange"
        status_label = ttk.Label(info_frame, text=f"[{unreal_status}]", foreground=status_color)
        status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(info_frame, text="TAPython Menu Configuration Editor", 
                 font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
        
        # 노트북 (탭)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 상태바
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="준비", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.LEFT, padx=(0, 5))
        
        # 상태 메시지를 자동으로 지우기 위한 after 참조
        self.status_after_id = None
        
        self.setup_tabs()
    
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
        # 좌우 분할
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 좌측: 아이템 목록
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="메뉴 아이템", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        # 트리뷰와 스크롤바 (서브메뉴 지원을 위해)
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 트리뷰 생성
        columns = ("type",)
        treeview = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=10)
        treeview.heading("#0", text="이름", anchor=tk.W)
        treeview.heading("type", text="타입", anchor=tk.W)
        treeview.column("#0", width=200, minwidth=150)
        treeview.column("type", width=80, minwidth=60)
        
        # 스크롤바
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=treeview.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=treeview.xview)
        treeview.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 리스트 컨트롤 버튼
        list_btn_frame = ttk.Frame(left_frame)
        list_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(list_btn_frame, text="➕ 추가", 
                  command=lambda: self.add_item(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_btn_frame, text="📁 서브메뉴 추가", 
                  command=lambda: self.add_submenu(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_btn_frame, text="🗑️ 삭제", 
                  command=lambda: self.delete_item(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_btn_frame, text="⬆️ 위로", 
                  command=lambda: self.move_item_up(category_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_btn_frame, text="⬇️ 아래로", 
                  command=lambda: self.move_item_down(category_id)).pack(side=tk.LEFT)
        
        # 우측: 아이템 편집
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="아이템 편집", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        # 설명 라벨
        help_text = "아래에서 아이템 정보를 수정한 후 '변경사항 저장' 버튼을 클릭하세요."
        ttk.Label(right_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(anchor=tk.W, pady=(2, 5))
        
        # 편집 폼
        edit_frame = ttk.Frame(right_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 이름
        ttk.Label(edit_frame, text="이름:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(edit_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2)
        
        # 툴팁
        ttk.Label(edit_frame, text="툴팁:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        tooltip_var = tk.StringVar()
        tooltip_entry = ttk.Entry(edit_frame, textvariable=tooltip_var, width=40)
        tooltip_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2)
        
        # 활성화
        enabled_var = tk.BooleanVar()
        enabled_var.set(True)  # 기본값을 명시적으로 설정
        enabled_check = ttk.Checkbutton(edit_frame, text="활성화", variable=enabled_var)
        enabled_check.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 명령어
        ttk.Label(edit_frame, text="명령어:").grid(row=3, column=0, sticky=tk.NW+tk.W, padx=(0, 5), pady=2)
        
        cmd_frame = ttk.Frame(edit_frame)
        cmd_frame.grid(row=3, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=2)
        
        command_text = tk.Text(cmd_frame, height=6, width=40, wrap=tk.WORD)
        cmd_scrollbar = ttk.Scrollbar(cmd_frame, orient=tk.VERTICAL, command=command_text.yview)
        command_text.configure(yscrollcommand=cmd_scrollbar.set)
        
        command_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Chameleon Tools
        ttk.Label(edit_frame, text="Chameleon:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(edit_frame, textvariable=chameleon_var, width=40)
        chameleon_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=2)
        
        # 업데이트 버튼
        update_btn = ttk.Button(edit_frame, text="💾 변경사항 저장", 
                               command=lambda: self.update_item(category_id))
        update_btn.grid(row=5, column=1, sticky=tk.W, pady=(10, 0))
        
        # 그리드 가중치
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(3, weight=1)
        
        # 트리뷰 선택 이벤트
        treeview.bind("<<TreeviewSelect>>", lambda e: self.on_item_select(category_id))
        
        return {
            'treeview': treeview,
            'name_var': name_var,
            'tooltip_var': tooltip_var,
            'enabled_var': enabled_var,
            'command_text': command_text,
            'chameleon_var': chameleon_var,
            'name_entry': name_entry,
            'tooltip_entry': tooltip_entry,
            'chameleon_entry': chameleon_entry,
            'enabled_check': enabled_check,
            'update_btn': update_btn
        }
    
    def load_default_config(self):
        """기본 설정 파일 로드"""
        if os.path.exists(self.default_config_path):
            self.load_config_file(self.default_config_path)
        else:
            # 추가 경로들을 시도해보기
            if UNREAL_AVAILABLE:
                try:
                    project_dir = unreal.Paths.project_dir()
                    additional_paths = [
                        # 유효한 경로와 관련된 추가 경로들
                        os.path.join(project_dir, "TA", "TAPython", "Content", "UI", "MenuConfig.json"),
                        os.path.join(project_dir, "Plugins", "TAPython", "Content", "UI", "MenuConfig.json"),
                        os.path.join(project_dir, "Content", "Python", "MenuConfig.json"),
                    ]
                    
                    found_path = None
                    for path in additional_paths:
                        if os.path.exists(path):
                            found_path = path
                            break
                    
                    if found_path:
                        self.default_config_path = found_path
                        self.load_config_file(found_path)
                        return
                except Exception as e:
                    print(f"추가 경로 검색 중 오류: {e}")
            
            # 모든 경로에서 찾지 못한 경우
            error_msg = f"기본 설정 파일을 찾을 수 없습니다.\n"
            error_msg += f"기본 경로: {self.default_config_path}\n\n"
            
            if UNREAL_AVAILABLE:
                try:
                    project_dir = unreal.Paths.project_dir()
                    error_msg += f"프로젝트 디렉토리: {project_dir}\n"
                    error_msg += "다음 경로들을 확인해보세요:\n"
                    error_msg += f"• {os.path.join(project_dir, 'TA', 'TAPython', 'UI', 'MenuConfig.json')} (권장)\n"
                    error_msg += f"• {os.path.join(project_dir, 'Plugins', 'TAPython', 'UI', 'MenuConfig.json')}\n"
                except:
                    pass
            else:
                error_msg += "Unreal Engine Python API를 사용할 수 없습니다.\n"
                error_msg += "Unreal Editor에서 실행해주세요."
            
            messagebox.showerror("오류", error_msg)
    
    def open_config(self):
        """설정 파일 열기"""
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
            print(f"DEBUG: 로드하려는 파일 경로: {file_path}")
            print(f"DEBUG: 파일 존재 여부: {os.path.exists(file_path)}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.config_file_path = file_path
            self.file_label.configure(text=f"파일: {os.path.basename(file_path)}")
            
            print(f"DEBUG: 로드된 config_data 키들: {list(self.config_data.keys())}")
            # 첫 번째 카테고리의 첫 번째 아이템 샘플 출력
            for category, data in list(self.config_data.items())[:1]:
                if "items" in data and data["items"]:
                    first_item = data["items"][0]
                    print(f"DEBUG: {category} 첫 번째 아이템 샘플: {first_item}")
                    break
            
            self.refresh_all_tabs()
            self.update_status(f"📂 로드 완료: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"DEBUG: 파일 로드 오류: {e}")
            messagebox.showerror("오류", f"파일 로드 실패: {str(e)}")
            self.update_status(f"❌ 로드 실패: {str(e)}", auto_clear=False)
    
    def save_config(self):
        """설정 저장"""
        if not self.config_file_path:
            self.save_as_config()
            return
        
        try:
            print(f"DEBUG: 저장하려는 파일 경로: {self.config_file_path}")
            
            # 저장 전에 JSON 데이터 확인 (디버그)
            print(f"DEBUG: 저장 중인 config 데이터 샘플:")
            for category, data in list(self.config_data.items())[:2]:  # 처음 2개 카테고리 출력
                if "items" in data and data["items"]:
                    print(f"  {category}: {len(data['items'])}개 아이템")
                    for i, item in enumerate(data["items"][:2]):  # 처음 2개 아이템만
                        enabled_status = item.get("enabled", "키없음")
                        print(f"    [{i}] {item.get('name', '이름없음')}: enabled={enabled_status}")
            
            # 파일에 저장
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            
            print(f"DEBUG: 파일 저장 완료")
            
            # 저장 후 파일 다시 읽어서 검증
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                verification_data = json.load(f)
            
            print(f"DEBUG: 저장 후 검증 - 파일에서 다시 읽은 데이터:")
            for category, data in list(verification_data.items())[:1]:
                if "items" in data and data["items"]:
                    first_item = data["items"][0]
                    print(f"  첫 번째 아이템: {first_item}")
                    break
                    
            self.update_status("💾 설정이 저장되었습니다!")
        except Exception as e:
            print(f"DEBUG: 저장 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"저장 실패: {str(e)}")
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
                self.file_label.configure(text=f"파일: {os.path.basename(file_path)}")
                self.update_status("💾 설정이 저장되었습니다!")
            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {str(e)}")
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
            
            # 아이템 타입 결정 (아이콘 포함)
            if "items" in item:
                item_type = "📁 서브메뉴"
                display_name = f"📁 {name}"
            elif item.get("command"):
                item_type = "⚡ 명령어"
                display_name = f"⚡ {name}"
            else:
                item_type = "📄 아이템"
                display_name = f"📄 {name}"
            
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
            print(f"DEBUG: 100ms 후 재확인 - 로드된 명령어: '{loaded_command}'")
            print(f"DEBUG: 예상 명령어: '{expected_command}'")
            print(f"DEBUG: 일치 여부: {loaded_command == expected_command}")
        except Exception as e:
            print(f"DEBUG: 명령어 검증 중 오류: {e}")
    
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
                print(f"DEBUG: 아이템 '{item_data.get('name')}' 로드됨 - enabled: {enabled_value} (타입: {type(enabled_value)})")
                
                tab_widgets['enabled_var'].set(bool(enabled_value))  # 명시적으로 bool 변환
                
                # 명령어
                tab_widgets['command_text'].delete(1.0, tk.END)
                command = item_data.get("command", "")
                if command:
                    tab_widgets['command_text'].insert(1.0, command)
                    print(f"DEBUG: 명령어 Text 위젯에 로드됨: '{command}'")
                    
                    # 위젯 업데이트 강제 실행
                    tab_widgets['command_text'].update_idletasks()
                    
                    # 잠시 후 다시 읽어서 확인
                    self.root.after(100, lambda: self._verify_command_load(tab_widgets, command))
                else:
                    print(f"DEBUG: 명령어가 비어있음")
                
                # Text 위젯에서 다시 읽어서 확인
                loaded_command = tab_widgets['command_text'].get(1.0, tk.END).rstrip('\n').strip()
                print(f"DEBUG: Text 위젯에서 즉시 읽은 명령어: '{loaded_command}'")
                
                # Chameleon
                tab_widgets['chameleon_var'].set(item_data.get("ChameleonTools", ""))
                
                # 편집 가능 상태로 설정
                self.set_edit_state(category_id, True)
            else:
                self.clear_edit_form(category_id)
        except Exception as e:
            print(f"DEBUG: 아이템 선택 중 오류: {e}")
            # 에러 발생 시 편집 폼 초기화
            self.clear_edit_form(category_id)
    
    def _get_item_data_from_tree(self, treeview, tree_item, category_id):
        """트리 아이템으로부터 실제 데이터 찾기"""
        try:
            # 선택된 아이템의 경로를 추적
            path = []
            current = tree_item
            
            while current:
                path.insert(0, current)
                current = treeview.parent(current)
            
            # 루트 데이터에서 시작하여 경로를 따라 탐색
            if category_id not in self.config_data or "items" not in self.config_data[category_id]:
                print(f"DEBUG: 카테고리 {category_id}가 config_data에 없음")
                return None
            
            current_items = self.config_data[category_id]["items"]
            current_item_ref = None
            
            for i, tree_id in enumerate(path):
                # 현재 레벨에서 해당 아이템의 인덱스 찾기
                index = self._get_tree_item_index(treeview, tree_id)
                if index >= len(current_items):
                    print(f"DEBUG: 인덱스 {index}가 아이템 수 {len(current_items)}를 초과함")
                    return None
                
                current_item_ref = current_items[index]
                
                # 마지막 아이템이면 반환
                if tree_id == path[-1]:
                    print(f"DEBUG: 찾은 아이템 데이터: {current_item_ref}")
                    print(f"DEBUG: 아이템 메모리 주소: {id(current_item_ref)}")
                    return current_item_ref
                
                # 서브메뉴로 이동
                if "items" in current_item_ref:
                    current_items = current_item_ref["items"]
                else:
                    print(f"DEBUG: 서브메뉴가 없는 아이템에서 더 깊이 탐색 시도")
                    return None
            
            return None
        except Exception as e:
            print(f"DEBUG: _get_item_data_from_tree 오류: {e}")
            return None
    
    def _get_tree_item_index(self, treeview, tree_item):
        """트리 아이템의 부모 내에서의 인덱스 구하기"""
        try:
            parent = treeview.parent(tree_item)
            siblings = treeview.get_children(parent)
            return siblings.index(tree_item)
        except (ValueError, tk.TclError):
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
                messagebox.showerror("오류", "선택된 아이템의 데이터를 찾을 수 없습니다.")
                return
            
            print(f"DEBUG: 업데이트 전 아이템 데이터: {item_data}")
            print(f"DEBUG: 업데이트 전 아이템 메모리 주소: {id(item_data)}")
            
            # 폼에서 데이터 가져와서 업데이트
            name = tab_widgets['name_var'].get().strip()
            if not name:
                messagebox.showwarning("경고", "이름은 비워둘 수 없습니다.")
                return
            
            # enabled 값을 명시적으로 가져오기
            enabled_value = tab_widgets['enabled_var'].get()
            print(f"DEBUG: 폼에서 가져온 enabled 값: {enabled_value} (타입: {type(enabled_value)})")
            
            # 데이터 업데이트 (enabled 값을 먼저 저장)
            old_enabled = item_data.get("enabled", "없음")
            item_data["enabled"] = enabled_value
            item_data["name"] = name
            item_data["tooltip"] = tab_widgets['tooltip_var'].get().strip()
            item_data["ChameleonTools"] = tab_widgets['chameleon_var'].get().strip()
            
            # 명령어 처리 (Text 위젯의 자동 개행 제거)
            raw_command = tab_widgets['command_text'].get(1.0, tk.END)
            command = raw_command.rstrip('\n').strip()
            print(f"DEBUG: Text 위젯에서 가져온 원본 명령어: '{raw_command}'")
            print(f"DEBUG: 처리된 명령어: '{command}'")
            print(f"DEBUG: 기존 명령어: '{item_data.get('command', '')}'")
            
            # 명령어 업데이트 로직 개선
            existing_command = item_data.get("command", "")
            if command.strip():  # 새 명령어가 있는 경우
                item_data["command"] = command
                print(f"DEBUG: 명령어 업데이트됨: '{command}'")
            elif existing_command:  # Text 위젯이 비어있지만 기존 명령어가 있는 경우
                # 기존 명령어 유지 (Text 위젯 문제로 인한 데이터 손실 방지)
                print(f"DEBUG: Text 위젯이 비어있어 기존 명령어 유지: '{existing_command}'")
                # item_data["command"]는 그대로 두어 기존 값 유지
            else:  # 둘 다 비어있는 경우
                item_data["command"] = ""
                print(f"DEBUG: 빈 명령어로 설정됨")
            
            print(f"DEBUG: 업데이트 후 아이템 데이터: {item_data}")
            print(f"DEBUG: enabled 값 변경: {old_enabled} -> {item_data['enabled']}")
            
            # 트리뷰 업데이트
            if "items" in item_data:
                item_type = "📁 서브메뉴"
                display_name = f"📁 {name}"
            elif command:
                item_type = "⚡ 명령어"
                display_name = f"⚡ {name}"
            else:
                item_type = "📄 아이템"
                display_name = f"📄 {name}"
            
            treeview.item(selected_item, text=display_name, values=(item_type,))
            
            # config_data에서 실제로 변경되었는지 다시 확인
            verification_data = self._get_item_data_from_tree(treeview, selected_item, category_id)
            if verification_data:
                print(f"DEBUG: 검증 - 실제 저장된 enabled 값: {verification_data.get('enabled')}")
                print(f"DEBUG: 검증 - 메모리 주소 동일한가: {id(item_data) == id(verification_data)}")
            
            # 상태 메시지 (enabled 값 확인)
            enabled_status = "✅ 활성화됨" if enabled_value else "❌ 비활성화됨"
            self.update_status(f"💾 '{name}' 저장 완료 ({enabled_status}) - enabled={enabled_value}")
            
        except Exception as e:
            print(f"DEBUG: update_item 오류: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("오류", f"아이템 업데이트 중 오류 발생: {str(e)}")
            self.update_status(f"저장 실패: {str(e)}", auto_clear=False)
    
    def add_item(self, category_id):
        """아이템 추가"""
        self.add_item_dialog(category_id)
    
    def add_submenu(self, category_id):
        """서브메뉴 추가"""
        self.add_submenu_dialog(category_id)
    
    def add_submenu_dialog(self, category_id):
        """서브메뉴 추가 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title("새 서브메뉴 추가")
        dialog.geometry("450x225")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 메인 윈도우 중앙에 위치시키기
        dialog.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        dialog_width = 450
        dialog_height = 225
        center_x = main_x + (main_width - dialog_width) // 2
        center_y = main_y + (main_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
        
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
                messagebox.showwarning("경고", "서브메뉴 이름을 입력해주세요.")
                return
            
            new_submenu = {"name": name, "enabled": True, "items": []}
            # Chameleon 값은 빈 문자열이어도 저장
            new_submenu["ChameleonTools"] = chameleon
            
            try:
                if parent_selection == "(루트)":
                    # 루트에 추가
                    if category_id not in self.config_data:
                        self.config_data[category_id] = {"items": []}
                    elif "items" not in self.config_data[category_id]:
                        self.config_data[category_id]["items"] = []
                    
                    self.config_data[category_id]["items"].append(new_submenu)
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
                        messagebox.showerror("오류", f"부모 아이템 '{parent_selection}'를 찾을 수 없습니다.")
                        return
                
                # 해당 탭 새로고침
                self.refresh_tab(category_id)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("오류", f"서브메뉴 추가 중 오류 발생: {str(e)}")
                self.update_status(f"서브메뉴 추가 실패: {str(e)}", auto_clear=False)
        
        ttk.Button(button_frame, text="✅ 추가", command=add_submenu).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        dialog.columnconfigure(1, weight=1)
        name_entry.focus_set()
    
    def _populate_parent_list(self, treeview, parent, parent_list, prefix=""):
        """부모 아이템 목록 생성"""
        for child in treeview.get_children(parent):
            text = treeview.item(child, "text")
            values = treeview.item(child, "values")
            if values and values[0] == "서브메뉴":
                parent_list.append(f"{prefix}{text}")
                self._populate_parent_list(treeview, child, parent_list, f"{prefix}{text}/")
    
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
    
    def add_item_dialog(self, category_id=None):
        """아이템 추가 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title("새 아이템 추가")
        dialog.geometry("600x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 메인 윈도우 중앙에 위치시키기
        dialog.update_idletasks()  # 윈도우 크기 계산을 위해
        
        # 메인 윈도우 위치와 크기 가져오기
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        # 다이얼로그 크기 (고정값 사용)
        dialog_width = 600
        dialog_height = 300
        
        # 중앙 위치 계산
        center_x = main_x + (main_width - dialog_width) // 2
        center_y = main_y + (main_height - dialog_height) // 2
        
        # 다이얼로그 위치 설정
        dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
        
        # 메뉴 타입 선택
        if category_id is None:
            ttk.Label(dialog, text="메뉴 타입:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            category_var = tk.StringVar()
            category_combo = ttk.Combobox(dialog, textvariable=category_var, 
                                        values=list(self.config_data.keys()), state="readonly")
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
                messagebox.showwarning("경고", "이름을 입력해주세요.")
                return
            
            if not selected_category:
                messagebox.showwarning("경고", "메뉴 타입을 선택해주세요.")
                return
            
            new_item = {"name": name, "enabled": True}
            if command:
                new_item["command"] = command
            # Chameleon 값은 빈 문자열이어도 저장
            new_item["ChameleonTools"] = chameleon
            
            try:
                if parent_selection == "(루트)":
                    # 카테고리 데이터 확인/생성
                    if selected_category not in self.config_data:
                        self.config_data[selected_category] = {"items": []}
                    elif "items" not in self.config_data[selected_category]:
                        self.config_data[selected_category]["items"] = []
                    
                    # 아이템 추가
                    self.config_data[selected_category]["items"].append(new_item)
                else:
                    # 선택된 부모에 추가
                    parent_item_data = self._find_parent_by_name(selected_category, parent_selection)
                    if parent_item_data:
                        if "items" not in parent_item_data:
                            parent_item_data["items"] = []
                        parent_item_data["items"].append(new_item)
                    else:
                        messagebox.showerror("오류", f"부모 아이템 '{parent_selection}'를 찾을 수 없습니다.")
                        return
                
                # 해당 탭 새로고침
                self.refresh_tab(selected_category)
                dialog.destroy()
                self.update_status(f"➕ 아이템 '{name}' 추가됨")
                
            except Exception as e:
                messagebox.showerror("오류", f"아이템 추가 중 오류 발생: {str(e)}")
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
            messagebox.showwarning("경고", "삭제할 아이템을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "정말 이 아이템을 삭제하시겠습니까?"):
            selected_item = selection[0]
            
            # 아이템 경로 추적하여 삭제
            if self._delete_item_from_data(treeview, selected_item, category_id):
                self.refresh_tab(category_id)
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
    
    def run(self):
        """메인 루프 실행"""
        self.root.mainloop()
    
    def on_closing(self):
        """창 닫기 이벤트 처리"""
        try:
            # 상태 타이머가 있으면 취소
            if hasattr(self, 'status_after_id') and self.status_after_id:
                self.root.after_cancel(self.status_after_id)
        except:
            pass  # 에러 무시
        
        try:
            self.root.destroy()
        except:
            pass  # 에러 무시


def main():
    """메인 함수"""
    app = SimpleMenuEditor()
    app.run()


if __name__ == "__main__":
    main()