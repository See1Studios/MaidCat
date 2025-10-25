#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog Classes
다이얼로그 관련 클래스들
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Tuple, Any, Dict, List

from ..config.constants import ALL_TOOL_MENUS, ENTRY_TYPES
from ..utils.gui_utils import setup_dialog


class NewToolMenuAnchorDialog:
    """새 툴 메뉴 추가 다이얼로그"""
    
    def __init__(self, parent: tk.Widget, config_data: Optional[Dict] = None):
        self.result: Optional[Tuple[str, str, bool, bool]] = None
        self.config_data = config_data or {}
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        setup_dialog(self.dialog, "새 툴 메뉴 항목 추가", 600, 650, parent, modal=True)
        self.dialog.resizable(False, False)
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """다이얼로그 UI 설정"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ttk.Label(main_frame, text="새 툴 메뉴 항목 추가", font=("맑은 고딕", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 툴 메뉴 ID 입력
        ttk.Label(main_frame, text="툴 메뉴 ID:").pack(anchor=tk.W)
        self.tool_menu_id_entry = ttk.Entry(main_frame, width=50)
        self.tool_menu_id_entry.pack(fill=tk.X, pady=(5, 10))
        self.tool_menu_id_entry.bind('<KeyRelease>', self._validate_input)
        
        # 툴 메뉴 이름 입력
        ttk.Label(main_frame, text="툴 메뉴 이름:").pack(anchor=tk.W)
        self.category_name_entry = ttk.Entry(main_frame, width=50)
        self.category_name_entry.pack(fill=tk.X, pady=(5, 10))
        self.category_name_entry.bind('<KeyRelease>', self._validate_input)
        
        # HasSection 옵션
        self.section_options_frame = ttk.LabelFrame(main_frame, text="툴 메뉴 옵션", padding=10)
        self.section_options_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.has_section_var = tk.BooleanVar(value=True)
        self.has_section_check = ttk.Checkbutton(
            self.section_options_frame, 
            text="HasSection (구분선 표시)", 
            variable=self.has_section_var
        )
        self.has_section_check.pack(anchor=tk.W)
        
        # 미리 정의된 메뉴 목록
        self.predefined_frame = ttk.LabelFrame(main_frame, text="미리 정의된 메뉴 예시", padding=10)
        self.predefined_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 리스트박스
        listbox_frame = ttk.Frame(self.predefined_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.anchor_listbox = tk.Listbox(listbox_frame, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.anchor_listbox.yview)
        self.anchor_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.anchor_listbox.bind("<<ListboxSelect>>", self.on_anchor_select)
        
        self.anchor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 설명
        self.info_label = ttk.Label(main_frame, foreground="gray")
        self.info_label.pack(anchor=tk.W, pady=(0, 15))
        self.info_label.configure(text="• 회색 텍스트는 이미 존재하는 툴 메뉴입니다")
        
        # 사용 가능한 툴 메뉴 목록 채우기
        self._populate_available_categories()
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        self.add_button = ttk.Button(button_frame, text="추가", command=self.add_category, state=tk.DISABLED)
        self.add_button.pack(side=tk.RIGHT)
        
        # 키 바인딩
        self.dialog.bind('<Return>', lambda e: self.add_category())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # 포커스 설정
        self.tool_menu_id_entry.focus()
        
        # 초기 버튼 상태 설정
        self._validate_input()
    
    def _populate_available_categories(self):
        """사용 가능한 툴 메뉴 목록 채우기"""
        existing_categories = set(self.config_data.keys())
        
        for category in sorted([tool_menu_id for tool_menu_id, _ in ALL_TOOL_MENUS]):
            if category in existing_categories:
                self.anchor_listbox.insert(tk.END, f"{category} (이미 존재)")
                last_index = self.anchor_listbox.size() - 1
                self.anchor_listbox.itemconfig(last_index, {'fg': 'gray'})
            else:
                self.anchor_listbox.insert(tk.END, category)
    
    def on_anchor_select(self, event):
        """미리 정의된 메뉴 선택 시 ID 필드에 복사"""
        selection = self.anchor_listbox.curselection()
        if selection:
            anchor_name = self.anchor_listbox.get(selection[0])
            
            if "(이미 존재)" in anchor_name:
                self.add_button.configure(state=tk.DISABLED)
                self.anchor_listbox.selection_clear(0, tk.END)
                return
            else:
                self.add_button.configure(state=tk.NORMAL)
            
            self.tool_menu_id_entry.delete(0, tk.END)
            self.tool_menu_id_entry.insert(0, anchor_name)
            
            # 표시명 찾기
            display_name = None
            for tool_menu_id, category_name in ALL_TOOL_MENUS:
                if tool_menu_id == anchor_name:
                    display_name = category_name
                    break
            
            if display_name:
                self.category_name_entry.delete(0, tk.END)
                self.category_name_entry.insert(0, display_name)
            else:
                fallback_name = anchor_name.split('.')[-1]
                self.category_name_entry.delete(0, tk.END)
                self.category_name_entry.insert(0, fallback_name)
            
            self._validate_input()

    def _validate_input(self, event=None):
        """입력 필드 내용을 검증하고 추가 버튼 상태를 업데이트"""
        tool_menu_id = self.tool_menu_id_entry.get().strip()
        category_name = self.category_name_entry.get().strip()
        
        if tool_menu_id and category_name and not self._is_existing_category(tool_menu_id, category_name):
            self.add_button.config(state=tk.NORMAL)
        else:
            self.add_button.config(state=tk.DISABLED)

    def _is_existing_category(self, tool_menu_id: str, category_name: str) -> bool:
        """툴 메뉴가 이미 존재하는지 확인"""
        if tool_menu_id in self.config_data:
            return True
        
        for existing_id in self.config_data.keys():
            if existing_id == category_name:
                return True
        
        return False
    
    def add_category(self):
        """추가 버튼"""
        tool_menu_id = self.tool_menu_id_entry.get().strip()
        category_name = self.category_name_entry.get().strip()
        
        if not tool_menu_id:
            messagebox.showerror("오류", "툴 메뉴 ID를 입력하세요.")
            return
        
        if not category_name:
            messagebox.showerror("오류", "툴 메뉴 이름을 입력하세요.")
            return
        
        has_section = self.has_section_var.get()
        self.result = (tool_menu_id, category_name, False, has_section)
        
        self.dialog.destroy()
    
    def cancel(self):
        """취소 버튼"""
        self.dialog.destroy()


class NewEntryDialog:
    """새 엔트리 추가 다이얼로그"""
    
    def __init__(self, parent: tk.Widget, ta_tool, tool_menu_id: Optional[str] = None):
        self.result: Optional[Dict[str, Any]] = None
        self.ta_tool = ta_tool
        self.tool_menu_id = tool_menu_id
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        setup_dialog(self.dialog, "새 엔트리 추가", 400, 200, parent, modal=True)
        self.dialog.resizable(False, False)
        
        self.setup_dialog()
    
    def setup_dialog(self):
        """다이얼로그 UI 설정"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        row = 0
        
        # 메뉴 타입 선택 (tool_menu_id가 None인 경우만)
        if self.tool_menu_id is None:
            ttk.Label(main_frame, text="메뉴 타입:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            self.category_var = tk.StringVar()
            self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                            values=tuple(self.ta_tool.config_data.keys()), state="readonly")
            self.category_combo.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
            if self.ta_tool.config_data:
                self.category_combo.current(0)
            row += 1
        else:
            self.category_var = tk.StringVar(value=self.tool_menu_id)
        
        # 엔트리 타입 선택
        ttk.Label(main_frame, text="엔트리 타입:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_type_var = tk.StringVar(value="command")
        entry_type_combo = ttk.Combobox(main_frame, textvariable=self.entry_type_var, 
                                       values=list(ENTRY_TYPES.keys()), state="readonly")
        entry_type_combo.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 엔트리 타입 설명
        self.type_desc_label = ttk.Label(main_frame, text=ENTRY_TYPES["command"]["description"], 
                                        foreground="gray", font=("Arial", 8))
        self.type_desc_label.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))
        
        def on_type_change(*args):
            selected_type = self.entry_type_var.get()
            desc = ENTRY_TYPES.get(selected_type, {}).get("description", "")
            icon = ENTRY_TYPES.get(selected_type, {}).get("icon", "")
            self.type_desc_label.config(text=f"{icon} {desc}")
        
        self.entry_type_var.trace('w', on_type_change)
        row += 2
        
        # 이름
        ttk.Label(main_frame, text="이름:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var)
        self.name_entry.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        row += 1
        
        # 위치 (부모 엔트리 선택)
        ttk.Label(main_frame, text="위치:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.parent_var = tk.StringVar()
        self.parent_combo = ttk.Combobox(main_frame, textvariable=self.parent_var, state="readonly")
        self.parent_combo.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 부모 엔트리 목록 구성
        self._populate_parent_list()
        row += 1
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="✅ 추가", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ 취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 그리드 설정
        main_frame.columnconfigure(1, weight=1)
        
        # 포커스 설정
        self.name_entry.focus()
        
        # 키 바인딩
        self.dialog.bind('<Return>', lambda e: self.add_entry())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def _populate_parent_list(self):
        """부모 엔트리 목록 구성"""
        if self.tool_menu_id is not None and self.ta_tool.current_tool_menu_id and self.ta_tool.current_widgets:
            tab_widgets = self.ta_tool.current_widgets
            treeview = tab_widgets['treeview']
            parent_items = ["(루트)"]
            self.ta_tool._populate_parent_list(treeview, "", parent_items)
            self.parent_combo['values'] = parent_items
            self.parent_combo.current(0)
        else:
            self.parent_combo['values'] = ["(루트)"]
            self.parent_combo.current(0)
    
    def add_entry(self):
        """엔트리 추가"""
        name = self.name_var.get().strip()
        selected_category = self.category_var.get()
        parent_selection = self.parent_var.get()
        entry_type = self.entry_type_var.get()
        
        if not name:
            messagebox.showwarning("경고", "이름을 입력해주세요.")
            return
        
        if not selected_category:
            messagebox.showwarning("경고", "메뉴 타입을 선택해주세요.")
            return
        
        if not entry_type:
            messagebox.showwarning("경고", "엔트리 타입을 선택해주세요.")
            return
        
        # 엔트리 타입에 따라 다른 기본 구조 생성
        if entry_type == "submenu":
            new_entry = {
                "name": name,
                "items": []
            }
        elif entry_type == "command":
            new_entry = {
                "name": name,
                "enabled": True,
                "command": ""
            }
        elif entry_type == "chameleonTools":
            new_entry = {
                "name": name,
                "enabled": True,
                "ChameleonTools": ""
            }
        else:
            messagebox.showerror("오류", f"알 수 없는 엔트리 타입: {entry_type}")
            return
        
        try:
            if parent_selection == "(루트)":
                items = self.ta_tool._validate_config_data(selected_category)
                items.append(new_entry)
            else:
                parent_item_data = self.ta_tool._find_parent_by_name(selected_category, parent_selection)
                if parent_item_data:
                    if "items" not in parent_item_data:
                        parent_item_data["items"] = []
                    parent_item_data["items"].append(new_entry)
                else:
                    messagebox.showerror("오류", f"부모 엔트리 '{parent_selection}'를 찾을 수 없습니다.")
                    return
            
            # 해당 탭 새로고침
            self.ta_tool.refresh_tab(selected_category)
            self.ta_tool.mark_as_modified()
            
            # 타입별 메시지
            type_names = {
                "submenu": "서브메뉴",
                "command": "명령어 엔트리", 
                "chameleonTools": "Chameleon 엔트리"
            }
            type_name = type_names.get(entry_type, "엔트리")
            
            if "." in selected_category:
                self.ta_tool.update_status(f"➕ {type_name} '{name}' 추가됨 - 'TAPython.RefreshToolMenus' 실행 필요")
            else:
                self.ta_tool.update_status(f"➕ {type_name} '{name}' 추가됨")
            
            self.result = new_entry
            self.dialog.destroy()
            
        except Exception as e:
            error_msg = f"엔트리 추가 중 오류 발생: {str(e)}"
            messagebox.showerror("오류", error_msg)
            self.ta_tool.update_status(f"엔트리 추가 실패: {str(e)}", auto_clear=False)
    
    def cancel(self):
        """취소"""
        self.result = None
        self.dialog.destroy()