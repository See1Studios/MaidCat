#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Utilities
GUI 관련 유틸리티 함수들
"""

import tkinter as tk
import webbrowser
from typing import Optional

from ..config.constants import TAPYTHON_WEBSITE, TAPYTHON_GITHUB, UNREAL_ICONS_REFERENCE


class ToolTip:
    """간단한 툴팁 클래스"""
    
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """마우스가 위젯에 들어왔을 때"""
        # 간단히 위젯 위치 기반으로 툴팁 표시
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window, 
            text=self.text,
            background="lightyellow", 
            relief="solid", 
            borderwidth=1,
            font=("Arial", 8)
        )
        label.pack()
    
    def on_leave(self, event=None):
        """마우스가 위젯에서 벗어났을 때"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def create_tooltip(widget: tk.Widget, text: str) -> ToolTip:
    """위젯에 툴팁을 추가합니다."""
    return ToolTip(widget, text)


def center_window(window: tk.Toplevel, parent: tk.Widget, width: int, height: int):
    """다이얼로그를 부모 윈도우 중앙에 위치시킵니다."""
    window.update_idletasks()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    
    center_x = parent_x + (parent_width - width) // 2
    center_y = parent_y + (parent_height - height) // 2
    window.geometry(f"{width}x{height}+{center_x}+{center_y}")


def setup_dialog(dialog: tk.Toplevel, title: str, width: int, height: int, 
                parent: tk.Widget, modal: bool = False) -> tk.Toplevel:
    """다이얼로그 공통 설정"""
    dialog.title(title)
    
    # modal이 True일 때만 grab_set 사용
    if modal:
        # parent가 Toplevel이나 Tk인 경우에만 transient 설정
        if isinstance(parent, (tk.Toplevel, tk.Tk)):
            dialog.transient(parent)
        dialog.grab_set()
    
    # 중앙에 위치시키기
    center_window(dialog, parent, width, height)
    
    return dialog


def open_url(url: str, logger=None):
    """웹 브라우저에서 URL 열기"""
    try:
        webbrowser.open(url)
        if logger:
            logger.info(f"웹 브라우저에서 열기: {url}")
    except Exception as e:
        if logger:
            logger.error(f"URL 열기 실패: {e}")
        else:
            print(f"URL 열기 실패: {e}")


def open_tapython_website(logger=None):
    """TAPython 공식 웹사이트 열기"""
    open_url(TAPYTHON_WEBSITE, logger)


def open_tapython_github(logger=None):
    """TAPython GitHub 저장소 열기"""
    open_url(TAPYTHON_GITHUB, logger)


def open_unreal_icons_reference(logger=None):
    """언리얼 엔진 아이콘 레퍼런스 열기"""
    open_url(UNREAL_ICONS_REFERENCE, logger)


def get_entry_type_display(item_data: dict, name: str) -> tuple[str, str]:
    """엔트리 타입에 따른 표시 형식 반환"""
    if "items" in item_data:
        return ("📁 서브메뉴", f"📁 {name}")
    elif item_data.get("ChameleonTools"):
        return ("🎨 카멜레온", f"🎨 {name}")
    elif item_data.get("command"):
        return ("⚡ 명령어", f"⚡ {name}")
    else:
        return ("📄 엔트리", f"📄 {name}")


def copy_to_clipboard(root: tk.Tk, text: str) -> bool:
    """텍스트를 클립보드에 복사"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        return True
    except Exception:
        return False