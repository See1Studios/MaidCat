#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAPython Guide
TAPython 플러그인 설치 가이드 클래스
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Callable, Optional

from ..config.constants import DEFAULT_CONFIG_STRUCTURE
from ..utils.gui_utils import open_tapython_website, open_tapython_github
from ..utils.logging_utils import get_logger

logger = get_logger()


class TAPythonGuide:
    """TAPython 플러그인 설치 가이드 클래스"""
    
    def __init__(self, parent_widget: tk.Widget, main_container: tk.Widget, 
                 clear_container_callback: Callable, parent_tool):
        self.parent = parent_widget
        self.main_container = main_container
        self._clear_main_container = clear_container_callback
        self.parent_tool = parent_tool  # TAPythonTool 인스턴스 참조
        
    def show_guide_interface(self):
        """메인 창에 TAPython 플러그인 안내 인터페이스 표시"""
        try:
            # 가이드 모드용 메뉴바와 정보 프레임 설정
            self.parent_tool._setup_guide_menubar()
            self.parent_tool._setup_guide_info_frame()
            
            # 기존 내용 지우기
            self._clear_main_container()
            
            # 안내 인터페이스 생성
            self.guide_interface = ttk.Frame(self.main_container)
            self.guide_interface.pack(fill=tk.BOTH, expand=True)
            
            # 부모 도구의 guide_interface도 업데이트
            self.parent_tool.guide_interface = self.guide_interface
            
            # 중앙 정렬을 위한 컨테이너
            center_frame = ttk.Frame(self.guide_interface)
            center_frame.pack(expand=True, fill=tk.BOTH)
            center_frame.grid_rowconfigure(0, weight=1)
            center_frame.grid_columnconfigure(0, weight=1)
            
            # 메인 콘텐츠 프레임
            content_frame = ttk.Frame(center_frame)
            content_frame.grid(row=0, column=0, sticky="", padx=50, pady=50)
            
            # 아이콘과 제목
            title_frame = ttk.Frame(content_frame)
            title_frame.pack(pady=(0, 30))
            
            ttk.Label(title_frame, text="🔌", font=("Arial", 48)).pack()
            ttk.Label(title_frame, text="TAPython 플러그인이 필요합니다", 
                     font=("Arial", 16, "bold"), foreground="red").pack(pady=(10, 0))
            
            # 설명
            desc_frame = ttk.Frame(content_frame)
            desc_frame.pack(pady=(0, 30), fill=tk.X)
            
            description = """이 도구는 TAPython 플러그인과 함께 작동하도록 설계되었습니다.

다음 옵션 중 하나를 선택하세요:"""
            
            ttk.Label(desc_frame, text=description, justify=tk.CENTER, 
                     font=("Arial", 11), wraplength=500).pack()
            
            # 버튼들
            self._create_guide_buttons(content_frame)
            
            # 상세 정보 프레임
            self._create_guide_details(content_frame)
            
        except Exception as e:
            logger.error(f"가이드 인터페이스 표시 중 오류: {e}")
            messagebox.showerror("오류", f"가이드 인터페이스를 표시할 수 없습니다:\n{e}")
    
    def _create_guide_buttons(self, parent: tk.Widget):
        """가이드 버튼들 생성"""
        try:
            button_frame = ttk.Frame(parent)
            button_frame.pack(pady=(0, 30))
            
            # 첫 번째 줄: 파일 관련 버튼들
            file_row = ttk.Frame(button_frame)
            file_row.pack(pady=(0, 5))
            
            # 새 설정 파일 생성 버튼
            create_btn = ttk.Button(file_row, text="📄 새 설정 파일 생성",
                                  command=self._create_new_config_file_guide,
                                  style="Accent.TButton")
            create_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # 수동 파일 선택 버튼
            manual_btn = ttk.Button(file_row, text="📁 수동으로 파일 선택",
                                  command=self._manual_file_selection_guide)
            manual_btn.pack(side=tk.LEFT)
            
            # 두 번째 줄: 링크 버튼들
            link_row = ttk.Frame(button_frame)
            link_row.pack()
            
            # 공식 사이트 버튼
            website_btn = ttk.Button(link_row, text="🌐 TAPython 공식 사이트",
                                   command=lambda: open_tapython_website(logger))
            website_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # GitHub 저장소 버튼
            github_btn = ttk.Button(link_row, text="📦 GitHub 저장소",
                                  command=lambda: open_tapython_github(logger))
            github_btn.pack(side=tk.LEFT)
            
        except Exception as e:
            logger.error(f"가이드 버튼 생성 중 오류: {e}")
    
    def _create_guide_details(self, parent: tk.Widget):
        """가이드 상세 정보 생성"""
        try:
            # 상세 정보 프레임
            details_frame = ttk.LabelFrame(parent, text="💡 추가 정보", padding=15)
            details_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_text = """• TAPython 플러그인은 Unreal Engine용 Python 확장입니다
• 설치 후 TA 폴더에 MenuConfig.json 파일이 생성됩니다
• 이 도구는 해당 파일을 편집하여 Python 메뉴를 관리합니다
• 올바른 경로: [언리얼 프로젝트]/TA/TAPython/UI/MenuConfig.json"""
            
            ttk.Label(details_frame, text=info_text, justify=tk.LEFT, 
                     font=("Arial", 10), wraplength=500).pack(anchor=tk.W)
            
        except Exception as e:
            logger.error(f"가이드 상세 정보 생성 중 오류: {e}")
    
    def _create_new_config_file_guide(self):
        """새 설정 파일 생성 가이드"""
        try:
            # 파일 저장 다이얼로그
            file_path = filedialog.asksaveasfilename(
                title="MenuConfig.json 파일 저장 위치 선택",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="MenuConfig.json"
            )
            
            if file_path:
                # 기본 설정 구조 사용
                default_config = DEFAULT_CONFIG_STRUCTURE.copy()
                
                # 파일 저장
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_config, f, indent=4, ensure_ascii=False)
                    
                    messagebox.showinfo("성공", f"새 설정 파일이 생성되었습니다:\n{file_path}\n\n"
                                               "이제 이 파일을 편집할 수 있습니다.")
                    
                    # 생성된 파일로 도구 재시작
                    if hasattr(self.parent_tool, 'load_config_file'):
                        logger.info(f"가이드에서 파일 로드 시작: {file_path}")
                        self.parent_tool.load_config_file(file_path)
                        
                except Exception as e:
                    messagebox.showerror("오류", f"파일 저장 실패:\n{e}")
                    
        except Exception as e:
            logger.error(f"새 설정 파일 생성 가이드 중 오류: {e}")
            messagebox.showerror("오류", f"설정 파일 생성 중 오류가 발생했습니다:\n{e}")
    
    def _manual_file_selection_guide(self):
        """수동 파일 선택 가이드"""
        try:
            file_path = filedialog.askopenfilename(
                title="MenuConfig.json 파일 선택",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                if hasattr(self.parent_tool, 'load_config_file'):
                    logger.info(f"가이드에서 수동 파일 로드 시작: {file_path}")
                    self.parent_tool.load_config_file(file_path)
                    
        except Exception as e:
            logger.error(f"수동 파일 선택 가이드 중 오류: {e}")
            messagebox.showerror("오류", f"파일 선택 중 오류가 발생했습니다:\n{e}")