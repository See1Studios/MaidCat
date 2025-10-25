#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool
TAPython MenuConfig.json을 간단하게 편집할 수 있는 툴
"""

import json
import logging
import os
import stat
import subprocess
import sys
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any

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
    logger.setLevel(logging.ERROR)  # WARNING에서 ERROR로 변경하여 로그 출력 최소화
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


def is_file_writable(file_path):
    """파일이 쓰기 가능한지 확인"""
    try:
        if not os.path.exists(file_path):
            return True  # 새 파일은 쓰기 가능
        
        # 파일 권한 확인
        file_stat = os.stat(file_path)
        return bool(file_stat.st_mode & stat.S_IWRITE)
    except (OSError, IOError):
        return False


def ensure_file_writable(file_path):
    """파일을 쓰기 가능한 상태로 만들기"""
    try:
        # 파일이 없으면 쓰기 가능
        if not os.path.exists(file_path):
            return True, "새 파일 생성 가능"
        
        # 이미 쓰기 가능하면 OK
        if is_file_writable(file_path):
            return True, "파일이 이미 쓰기 가능"
        
        # 읽기 전용 파일이면 권한 변경 시도
        try:
            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
            if is_file_writable(file_path):
                return True, "파일 권한이 변경됨"
            else:
                return False, "권한 변경 후에도 쓰기 불가"
        except OSError as e:
            return False, f"권한 변경 실패: {str(e)}"
            
    except Exception as e:
        return False, f"예상치 못한 오류: {str(e)}"


class TAPythonGuide:
    """TAPython 플러그인 설치 가이드 클래스"""
    
    def __init__(self, parent_widget, main_container, clear_container_callback, parent_tool):
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
    
    def _create_guide_buttons(self, parent):
        """가이드 버튼들 생성"""
        try:
            button_frame = ttk.Frame(parent)
            button_frame.pack(pady=(0, 30))
            
            # 첫 번째 줄: 파일 관련 버튼들
            file_row = ttk.Frame(button_frame)
            file_row.pack(pady=(0, 5))
            
            # 새 설정 파일 생성 버튼
            create_btn = ttk.Button(file_row, text="� 새 설정 파일 생성",
                                  command=self._create_new_config_file_guide,
                                  style="Accent.TButton")
            create_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # 수동 파일 선택 버튼
            manual_btn = ttk.Button(file_row, text="� 수동으로 파일 선택",
                                  command=self._manual_file_selection_guide)
            manual_btn.pack(side=tk.LEFT)
            
            # 두 번째 줄: 링크 버튼들
            link_row = ttk.Frame(button_frame)
            link_row.pack()
            
            # 공식 사이트 버튼
            website_btn = ttk.Button(link_row, text="🌐 TAPython 공식 사이트",
                                   command=lambda: self._open_url("https://www.tacolor.xyz/"))
            website_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # GitHub 저장소 버튼
            github_btn = ttk.Button(link_row, text="� GitHub 저장소",
                                  command=lambda: self._open_url("https://github.com/cgerchenhp/UE_TAPython_Plugin_Release/releases"))
            github_btn.pack(side=tk.LEFT)
            
        except Exception as e:
            logger.error(f"가이드 버튼 생성 중 오류: {e}")
    
    def _create_guide_details(self, parent):
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
                # 기본 설정 구조
                default_config = {
                    "menu_items": [
                        {
                            "type": "button",
                            "label": "선택된 에셋 정보 출력",
                            "tooltip": "현재 선택된 에셋들의 정보를 출력합니다",
                            "command": "import unreal\nselected = unreal.EditorUtilityLibrary.get_selected_assets()\nfor asset in selected:\n    print(f'Asset: {asset.get_name()}, Class: {asset.get_class().get_name()}')"
                        }
                    ]
                }
                
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
    
    def _open_url(self, url):
        """웹 브라우저에서 URL 열기"""
        try:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"웹 브라우저에서 열기: {url}")
        except Exception as e:
            logger.error(f"URL 열기 실패: {e}")
            messagebox.showerror("오류", f"웹 브라우저를 열 수 없습니다:\n{url}\n\n오류: {e}")
    
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


# 모든 툴 메뉴 정의 (한 곳에서 관리)
ALL_TOOL_MENUS = [
    # 전통적인 툴 메뉴들
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
    
    # 언리얼 엔진 툴 메뉴들 (Tool Menu Anchor)
    ("AssetEditor.AnimationBlueprintEditor.MainMenu", "애니메이션 BP 에디터 메뉴"),
    ("AssetEditor.AnimationEditor.MainMenu", "애니메이션 에디터 메뉴"),
    ("AssetEditor.SkeletalMeshEditor.ToolBar", "스켈레탈 메시 에디터 툴바"),
    ("AssetEditor.StaticMeshEditor.ToolBar", "스태틱 메시 에디터 툴바"),
    ("ContentBrowser.AddNewContextMenu", "콘텐츠 브라우저 새로 추가"),
    ("ContentBrowser.AssetContextMenu", "에셋 컨텍스트 메뉴"),
    ("ContentBrowser.AssetContextMenu.AimOffsetBlendSpace", "AimOffsetBlendSpace 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.AnimBlueprint", "애니메이션 BP 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.AnimMontage", "애니메이션 몽타주 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.AnimSequence", "애니메이션 시퀀스 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.BlendSpace", "BlendSpace 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.BlendSpace1D", "BlendSpace1D 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.CameraAnim", "카메라 애니메이션 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.DatasmithScene", "Datasmith 씬 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.PoseAsset", "포즈 에셋 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.SkeletalMesh", "스켈레탈 메시 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.SkeletalMesh.CreateSkeletalMeshSubmenu", "스켈레탈 메시 생성 서브메뉴"),
    ("ContentBrowser.AssetContextMenu.Skeleton.CreateSkeletalMeshSubmenu", "스켈레톤 생성 서브메뉴"),
    ("ContentBrowser.AssetContextMenu.SoundWave", "사운드 웨이브 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.StaticMesh", "스태틱 메시 컨텍스트"),
    ("ContentBrowser.AssetContextMenu.World", "월드 컨텍스트"),
    ("ContentBrowser.AssetViewOptions", "에셋 뷰 옵션"),
    ("ContentBrowser.AssetViewOptions.PathViewFilters", "경로 뷰 필터"),
    ("ContentBrowser.DragDropContextMenu", "드래그드롭 컨텍스트 메뉴"),
    ("ContentBrowser.FolderContextMenu", "폴더 컨텍스트 메뉴"),
    ("ContentBrowser.ItemContextMenu.PythonData", "Python 데이터 컨텍스트"),
    ("ContentBrowser.ToolBar", "콘텐츠 브라우저 툴바"),
    ("ControlRigEditor.RigHierarchy.ContextMenu", "리그 계층 컨텍스트"),
    ("ControlRigEditor.RigHierarchy.DragDropMenu", "리그 드래그드롭 메뉴"),
    ("Kismet.SubobjectEditorContextMenu", "컴포넌트 컨텍스트 메뉴"),
    ("Kismet.SCSEditorContextMenu", "SCS 에디터 컨텍스트"),
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



class TAPythonTool:
    """
    TAPython MenuConfig.json 편집기
    
    주요 기능:
    - 계층적 메뉴 구조 지원 (서브메뉴)
    - 트리뷰를 통한 직관적인 메뉴 구조 표시
    - 실시간 편집 및 저장
    - 다양한 툴 메뉴 지원
    
    메서드 구조:
    - __init__: 초기화 및 UI 설정
    - UI 관련: setup_ui, create_tab_content, update_status
    - 파일 관리: load_config_file, save_config, open_config
    - 데이터 관리: refresh_tab, on_item_select, update_item
    - 엔트리 관리: add_entry, delete_entry, move_entry_*
    - 헬퍼 메서드: _get_item_data_from_tree, _find_parent_by_name 등
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐍 TA Python Tool")
        self.root.geometry("1000x700")
        
        # 리소스 정리 상태 추적
        self._resources_cleaned = False
        
        self.config_data = {}
        self.config_file_path = ""
        self.has_unsaved_changes = False  # 저장하지 않은 변경사항 추적
        
        # 인터페이스 상태 초기화
        self.guide_interface = None
        self.edit_interface = None
        
        # 기본 경로 설정 (정확한 탐색으로 변경)
        self.default_config_path = ""  # 빈 문자열로 초기화
        
        # UI 먼저 설정 (사용자에게 빠른 피드백)
        self.setup_ui()
        
        # 가이드 클래스 초기화
        self.guide = TAPythonGuide(self.root, self.main_container, self._clear_main_container, self)
        
        # 창 닫기 이벤트 핸들러 설정
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 비동기로 처리할 초기화 작업들
        self.root.after(10, self._delayed_initialization)
    
    def _delayed_initialization(self):
        """지연된 초기화 작업들 (UI 표시 후 비동기 처리)"""
        try:
            # TAPython 플러그인 설치 상태 확인
            self.tapython_available = self._check_tapython_availability()
            
            # 설정 파일 로드 및 플러그인 상태 확인
            self.load_default_config()
            
            # 제목 업데이트 (플러그인 상태 반영)
            self.update_title()
            
            # 이벤트 큐 정리
            self.root.update_idletasks()
            
        except Exception as e:
            logger.error(f"지연된 초기화 중 오류: {e}")
            # 오류가 발생해도 기본 가이드 인터페이스는 표시
            if not self.edit_interface and not self.guide_interface:
                self.guide.show_guide_interface()
    
    def _check_tapython_availability(self):
        """TAPython 플러그인 설치 여부 확인 - 최적화된 버전"""
        try:
            # 이미 계산된 기본 경로가 있으면 빠른 확인
            if hasattr(self, 'default_config_path') and self.default_config_path:
                if os.path.exists(self.default_config_path):
                    logger.info(f"TAPython 설정 파일 발견: {self.default_config_path}")
                    return True
                else:
                    logger.info(f"TAPython 설정 파일 없음: {self.default_config_path}")
                    return False
            
            # 기본 경로가 없으면 빠른 탐색
            current_path = os.path.abspath(__file__)
            logger.info(f"파일 탐색 시작 경로: {current_path}")
            
            # 상위 폴더로 올라가면서 목표 파일 찾기 (충분한 단계로 확장)
            for level in range(10):  # 6에서 10으로 다시 확장
                current_path = os.path.dirname(current_path)
                logger.debug(f"탐색 중 ({level+1}/10): {current_path}")
                
                # .uproject 파일 확인을 더 효율적으로
                try:
                    items = os.listdir(current_path)
                    has_uproject = any(item.endswith('.uproject') for item in items)
                    if has_uproject:
                        uproject_files = [item for item in items if item.endswith('.uproject')]
                        logger.info(f"언리얼 프로젝트 발견: {current_path}, 파일: {uproject_files}")
                except (OSError, PermissionError):
                    logger.debug(f"경로 접근 불가: {current_path}")
                    continue
                
                # 언리얼 프로젝트라면 목표 파일 경로 확인
                if has_uproject:
                    target_config_path = os.path.join(current_path, "TA", "TAPython", "UI", "MenuConfig.json")
                    logger.info(f"목표 파일 경로 확인: {target_config_path}")
                    
                    if os.path.exists(target_config_path):
                        # 파일이 존재하면 해당 경로로 업데이트하고 True 반환
                        self.default_config_path = target_config_path
                        logger.info(f"TAPython 설정 파일 발견: {target_config_path}")
                        return True
                    else:
                        # 언리얼 프로젝트는 맞지만 파일이 없으면 기본 경로로 설정
                        self.default_config_path = target_config_path
                        logger.info(f"언리얼 프로젝트 발견했지만 MenuConfig.json 없음: {target_config_path}")
                        return False
                
                # 루트 디렉토리에 도달하면 중단
                if current_path == os.path.dirname(current_path):
                    break
            
            # 언리얼 프로젝트를 찾지 못한 경우
            logger.warning("언리얼 프로젝트를 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            logger.error(f"TAPython 가용성 확인 중 오류: {e}")
            return False


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
    
    def _validate_config_data(self, tool_menu_id):
        """설정 데이터 검증 및 초기화"""
        if tool_menu_id not in self.config_data:
            self.config_data[tool_menu_id] = {"items": []}
        elif "items" not in self.config_data[tool_menu_id]:
            self.config_data[tool_menu_id]["items"] = []
        return self.config_data[tool_menu_id]["items"]
    
    def _get_default_tool_menu_name(self, tool_menu_id):
        """툴 메뉴 ID에 대응하는 기본 이름 반환"""
        # ALL_TOOL_MENUS에서 기본 이름 찾기
        for menu_id, menu_name in ALL_TOOL_MENUS:
            if menu_id == tool_menu_id:
                return menu_name
        
        # 기본 이름이 없으면 ID를 기반으로 가독성 있는 이름 생성
        if "." in tool_menu_id:
            # 계층형 ID를 사람이 읽기 쉬운 형태로 변환
            parts = tool_menu_id.split(".")
            return " > ".join(parts)
        else:
            # 단순 ID는 그대로 사용
            return tool_menu_id
    
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
    
    def _get_entry_type_display(self, item_data, name):
        """엔트리 타입에 따른 표시 형식 반환"""
        if "items" in item_data:
            return ("📁 서브메뉴", f"📁 {name}")
        elif item_data.get("ChameleonTools"):
            return ("🎨 카멜레온", f"🎨 {name}")
        elif item_data.get("command"):
            return ("⚡ 명령어", f"⚡ {name}")
        else:
            return ("📄 엔트리", f"📄 {name}")
    
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
        """파일 레이블 업데이트"""
        if not hasattr(self, 'file_label') or not self.file_label:
            logger.debug("file_label이 아직 생성되지 않아 파일 경로 업데이트를 건너뜁니다.")
            return
        
        # 기본 파일 경로 표시
        display_text = self.format_file_path(file_path)
        
        self.file_label.configure(text=display_text)
        
        # 전체 경로를 툴팁으로 표시
        if file_path and hasattr(self, 'file_label'):
            # 기존 툴팁 제거하고 새로 생성
            for child in self.file_label.winfo_children():
                child.destroy()
            
            tooltip_text = f"전체 경로: {file_path}"
            self.create_tooltip(self.file_label, tooltip_text)
    
    def _get_perforce_status_display(self, file_path):
        """파일의 Perforce 상태를 표시용 텍스트로 반환 - 비활성화됨"""
        return ""  # Perforce 기능 비활성화
    
    def _get_perforce_status_details(self, file_path):
        """파일의 Perforce 상태 상세 정보를 반환 - 비활성화됨"""
        return "Perforce 기능이 비활성화되었습니다"
    
    def perforce_checkout_current_file(self):
        """현재 파일을 Perforce에서 체크아웃 - 비활성화됨"""
        messagebox.showinfo("알림", "Perforce 기능이 비활성화되었습니다.")
    
    def perforce_show_file_status(self):
        """현재 파일의 Perforce 상태를 상세히 표시 - 비활성화됨"""
        messagebox.showinfo("알림", "Perforce 기능이 비활성화되었습니다.")
    
    def perforce_refresh_status(self):
        """Perforce 상태를 새로고침 - 비활성화됨"""
        self.update_status("Perforce 기능이 비활성화되었습니다.")
    
    def open_file_location(self):
        """현재 파일의 위치를 탐색기/파인더에서 열기"""
        if not self.config_file_path:
            messagebox.showwarning("경고", "현재 열린 파일이 없습니다.")
            return
        
        if not os.path.exists(self.config_file_path):
            messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{self.config_file_path}")
            return
        
        file_dir = os.path.dirname(self.config_file_path)
        
        try:
            if sys.platform.startswith('win'):
                # Windows - 탐색기로 폴더 열기
                subprocess.run(['explorer', file_dir])
                self.update_status(f"📂 탐색기에서 폴더를 열었습니다: {os.path.basename(file_dir)}")
            elif sys.platform.startswith('darwin'):
                # macOS - Finder로 폴더 열기
                subprocess.run(['open', file_dir])
                self.update_status(f"📂 Finder에서 폴더를 열었습니다: {os.path.basename(file_dir)}")
            else:
                # Linux - 파일 매니저로 폴더 열기
                subprocess.run(['xdg-open', file_dir])
                self.update_status(f"📂 파일 매니저에서 폴더를 열었습니다: {os.path.basename(file_dir)}")
                
        except Exception as e:
            logger.error(f"파일 위치 열기 실패: {e}")
            messagebox.showerror("오류", f"파일 위치를 열 수 없습니다:\n{e}\n\n폴더 경로: {file_dir}")
            self.update_status("❌ 파일 위치 열기 실패", auto_clear=False)

    def open_in_external_editor(self):
        """현재 파일을 외부 편집기(VS Code 등)로 열기"""
        if not self.config_file_path:
            messagebox.showwarning("경고", "현재 열린 파일이 없습니다.")
            return
        
        if not os.path.exists(self.config_file_path):
            messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{self.config_file_path}")
            return
        
        try:
            # Windows에서 기본 연결된 편집기로 파일 열기
            if sys.platform.startswith('win'):
                # Windows에서는 os.startfile 사용
                os.startfile(self.config_file_path)
                self.update_status(f"📝 외부 편집기에서 파일을 열었습니다: {os.path.basename(self.config_file_path)}")
            elif sys.platform.startswith('darwin'):
                # macOS에서는 open 명령 사용
                subprocess.run(['open', self.config_file_path], check=True)
                self.update_status(f"📝 외부 편집기에서 파일을 열었습니다: {os.path.basename(self.config_file_path)}")
            else:
                # Linux에서는 xdg-open 사용
                subprocess.run(['xdg-open', self.config_file_path], check=True)
                self.update_status(f"📝 외부 편집기에서 파일을 열었습니다: {os.path.basename(self.config_file_path)}")
                
        except FileNotFoundError:
            messagebox.showerror("오류", "기본 편집기를 찾을 수 없습니다.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("오류", f"외부 편집기 실행 실패:\n{e}")
        except Exception as e:
            logger.error(f"외부 편집기로 파일 열기 실패: {e}")
            messagebox.showerror("오류", f"파일을 외부 편집기로 열 수 없습니다:\n{e}")

    def test_file_write_permission(self):
        """현재 파일의 쓰기 권한을 테스트"""
        if not self.config_file_path:
            messagebox.showwarning("경고", "현재 열린 파일이 없습니다.")
            return
        
        try:
            file_path = self.config_file_path
            logger.info(f"=== 파일 쓰기 권한 테스트 시작 ===")
            logger.info(f"테스트 파일: {file_path}")
            
            # 1. 기본 파일 정보
            exists = os.path.exists(file_path)
            logger.info(f"파일 존재: {exists}")
            
            if exists:
                file_stat = os.stat(file_path)
                stat_writable = bool(file_stat.st_mode & stat.S_IWRITE)
                logger.info(f"stat 쓰기 권한: {stat_writable}")
            
            # 2. 실제 쓰기 권한 테스트
            actual_writable = is_file_writable(file_path)
            logger.info(f"실제 쓰기 권한: {actual_writable}")
            
            # 3. 전체 권한 확인 테스트
            logger.info("=== _ensure_file_writable 테스트 ===")
            can_write = self._ensure_file_writable(file_path)
            logger.info(f"최종 쓰기 가능 여부: {can_write}")
            
            # 결과 표시
            result_msg = []
            result_msg.append(f"파일: {os.path.basename(file_path)}")
            result_msg.append(f"파일 존재: {'예' if exists else '아니오'}")
            if exists:
                result_msg.append(f"실제 쓰기 권한: {'예' if actual_writable else '아니오'}")
            
            result_msg.append("")
            result_msg.append(f"최종 결과: {'쓰기 가능' if can_write else '쓰기 불가'}")
            
            messagebox.showinfo("파일 쓰기 권한 테스트 결과", "\n".join(result_msg))
            
        except Exception as e:
            error_msg = f"테스트 중 오류: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("오류", error_msg)
    
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
                # 버튼 텍스트에 * 표시
                self.save_button.configure(text="💾 저장 *")
            else:
                self.save_button.configure(state=tk.DISABLED)
                self.save_button.configure(text="💾 저장")
        
        # "다른 이름으로 저장" 버튼도 동일하게 처리
        if hasattr(self, 'save_as_button'):
            if self.has_unsaved_changes:
                self.save_as_button.configure(text="📄 다른 이름으로 저장 *")
            else:
                self.save_as_button.configure(text="📄 다른 이름으로 저장")
        
        # 상태바에도 저장 상태 표시
        if hasattr(self, 'status_label'):
            if self.has_unsaved_changes:
                self.update_status("⚠️ 저장하지 않은 변경사항이 있습니다", auto_clear=False)
            else:
                self.update_status("✅ 모든 변경사항이 저장되었습니다")
    
    def update_title(self):
        """창 제목 업데이트"""
        base_title = "🐍 TA Python Tool"
        
        # TAPython 플러그인이 없으면 제목에 표시
        if not getattr(self, 'tapython_available', True):
            base_title += " (TAPython 플러그인 필요)"
        
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
        """기본 설정 파일 경로 찾기 - 폴백 경로만 제공"""
        try:
            # 폴백 경로 (실제 유효성은 _check_tapython_availability에서 확인)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fallback_path = os.path.join(
                os.path.dirname(os.path.dirname(script_dir)), 
                "UI", "MenuConfig.json"
            )
            logger.debug(f"폴백 경로 사용: {fallback_path}")
            return fallback_path
            
        except Exception as e:
            logger.error(f"설정 파일 경로 찾기 중 오류: {e}")
            # 최종 폴백
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(script_dir, "MenuConfig.json")
    
    def setup_ui(self):
        """UI 구성 - 새로운 좌우 분할 레이아웃"""
        self._setup_main_layout()  # 메뉴바는 상태에 따라 동적으로 설정
        self._setup_status_bar()
        self._setup_keyboard_shortcuts()
    
    def _setup_main_layout(self):
        """메인 레이아웃 설정 - 동적 내용 변경 가능한 구조"""
        # 상단 정보 프레임은 동적으로 설정 (가이드/편집 상태에 따라)
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 메인 컨테이너 (동적 내용 교체 가능)
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 25))  # 상태바 공간 확보
        
        # 편집 인터페이스와 안내 인터페이스 플레이스홀더
        self.edit_interface = None
        self.guide_interface = None
    
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
        """툴 메뉴 패널 설정"""
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
        self.category_listbox.bind('<<ListboxSelect>>', self.on_tool_menu_select)
        self.category_listbox.bind('<Button-3>', self.on_tool_menu_right_click)
        self.category_listbox.bind('<Double-Button-1>', self.on_tool_menu_double_click)
        
        # 버튼들
        button_frame = ttk.Frame(panel)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="➕ 추가", command=self.add_new_tool_menu).pack(fill=tk.X, pady=1)
        ttk.Button(button_frame, text="🗑️삭제", command=self.delete_selected_tool_menu).pack(fill=tk.X, pady=1)

        # 툴 메뉴 우클릭 메뉴
        self.category_context_menu = tk.Menu(self.root, tearoff=0)
        self.category_context_menu.add_command(label="🔧 HasSection 토글", command=self.toggle_has_section)
        self.category_context_menu.add_separator()
        self.category_context_menu.add_command(label="🗑️ 툴 메뉴 삭제", command=self.delete_selected_tool_menu)
        
        # 툴 메뉴 데이터 저장용
        self.category_data = {}
        
        # 기존 코드 호환성을 위한 tabs 초기화
        self.tabs = {}
        
        # 툴 메뉴 목록 로드
        self.refresh_category_list()
    
    def _setup_menu_panel(self, panel):
        """메뉴 엔트리 패널 설정"""
        # 트리뷰 컨테이너
        self.menu_tree_frame = ttk.Frame(panel)
        self.menu_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # 컨트롤 버튼들
        button_frame = ttk.Frame(panel)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 왼쪽 수직 패널: 추가/삭제
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        self.add_btn = ttk.Button(left_frame, text="➕ 추가", state=tk.DISABLED, command=lambda: self.add_entry(self.current_tool_menu_id))
        self.add_btn.pack(pady=(0, 3))  # 세로 배치
        
        self.delete_item_btn = ttk.Button(left_frame, text="🗑️ 삭제", state=tk.DISABLED)
        self.delete_item_btn.pack()  # 세로 배치
        
        # 오른쪽 수직 패널: 위로/아래로
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        self.move_up_btn = ttk.Button(right_frame, text="⬆️ 위로", state=tk.DISABLED)
        self.move_up_btn.pack(pady=(0, 3))  # 세로 배치
        
        self.move_down_btn = ttk.Button(right_frame, text="⬇️ 아래로", state=tk.DISABLED)
        self.move_down_btn.pack()  # 세로 배치
        
        # 현재 선택된 카테고리 ID
        self.current_tool_menu_id = None
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
            # 편집 인터페이스가 활성화되어 있을 때만 실행
            if self.edit_interface is None or not hasattr(self, 'category_panel'):
                return
            
            # 툴 메뉴 패널은 항상 고정
            self.category_panel.configure(text="📂 툴 메뉴")
            
            # 메뉴 엔트리 패널
            if category_name:
                menu_title = f"📄 {category_name}"
                self.menu_panel.configure(text=menu_title)
            else:
                self.menu_panel.configure(text="📄 툴 메뉴를 선택하세요")
            
            # 편집 패널
            if item_name:
                edit_title = f"✏️ {item_name}"
                if len(edit_title) > 50:  # 제목이 너무 길면 축약
                    edit_title = f"✏️ {item_name[:45]}..."
                self.edit_panel.configure(text=edit_title)
            elif category_name:
                self.edit_panel.configure(text="✏️ 엔트리를 선택하세요")
            else:
                self.edit_panel.configure(text="✏️ 툴 메뉴를 선택하세요")
        except Exception as e:
            logger.error(f"패널 제목 업데이트 중 오류: {e}")
    

    
    def refresh_category_list(self):
        """툴 메뉴 리스트 새로고침"""
        # 편집 인터페이스가 활성화되어 있을 때만 실행
        if self.edit_interface is None or not hasattr(self, 'category_listbox'):
            return
        
        self.category_listbox.delete(0, tk.END)
        self.category_data = {}
        
        # 설정 파일에서 실제로 존재하는 툴 메뉴만 표시
        available_categories = self._get_available_tool_menus(self._get_all_tool_menus())
        
        for tool_menu_id, category_name in available_categories:
            self.category_listbox.insert(tk.END, category_name)
            self.category_data[len(self.category_data)] = (tool_menu_id, category_name)
    
    def on_tool_menu_select(self, event):
        """툴 메뉴 선택 이벤트"""
        selection = self.category_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index in self.category_data:
            tool_menu_id, category_name = self.category_data[index]
            self.show_tool_menu_content(tool_menu_id, category_name)
    
    def on_tool_menu_right_click(self, event):
        """툴 메뉴 우클릭 이벤트"""
        # 클릭한 위치의 엔트리 선택
        index = self.category_listbox.nearest(event.y)
        self.category_listbox.selection_clear(0, tk.END)
        self.category_listbox.selection_set(index)
        
        # 선택된 툴 메뉴 정보 가져오기
        if index in self.category_data:
            tool_menu_id, category_name = self.category_data[index]
            
            # HasSection 현재 상태 확인
            current_has_section = self.config_data.get(tool_menu_id, {}).get("HasSection", True)
            
            # 메뉴 텍스트를 현재 상태에 따라 업데이트
            if current_has_section:
                toggle_text = "❌ HasSection 끄기 (구분선 숨기기)"
            else:
                toggle_text = "✅ HasSection 켜기 (구분선 표시)"
            
            # 메뉴 항목 업데이트
            self.category_context_menu.entryconfig(0, label=toggle_text)
        
        # 컨텍스트 메뉴 표시
        self.category_context_menu.post(event.x_root, event.y_root)
    
    def on_tool_menu_double_click(self, event):
        """툴 메뉴 더블클릭 이벤트 - 편집 창으로 전환"""
        # 더블클릭한 위치의 엔트리 선택
        index = self.category_listbox.nearest(event.y)
        self.category_listbox.selection_clear(0, tk.END)
        self.category_listbox.selection_set(index)
        
        # 편집 창으로 전환
        if index in self.category_data:
            # 가짜 이벤트 객체 생성
            fake_event = type('Event', (), {})()
            self.on_tool_menu_select(fake_event)
    
    def toggle_has_section(self):
        """선택된 툴 메뉴의 HasSection 속성 토글"""
        selection = self.category_listbox.curselection()
        if not selection:
            self._show_warning("경고", "HasSection을 변경할 툴 메뉴를 선택하세요.")
            return
        
        index = selection[0]
        if index not in self.category_data:
            return
        
        tool_menu_id, category_name = self.category_data[index]
        
        # 현재 HasSection 값 가져오기
        current_has_section = self.config_data.get(tool_menu_id, {}).get("HasSection", True)
        new_has_section = not current_has_section
        
        # HasSection 값 업데이트
        self._update_category_has_section(tool_menu_id, new_has_section)
        
        # 현재 편집 중인 툴 메뉴라면 UI도 업데이트
        if self.current_tool_menu_id == tool_menu_id and hasattr(self, 'current_widgets'):
            # 카테고리 정보 섹션의 체크박스도 업데이트
            self._refresh_category_info_section(tool_menu_id)
        
        # 상태 메시지
        status_msg = "활성화됨" if new_has_section else "비활성화됨"
        self.update_status(f"🔧 '{category_name}' HasSection {status_msg}")
    
    def _refresh_category_info_section(self, tool_menu_id):
        """카테고리 정보 섹션의 HasSection 체크박스 상태 새로고침"""
        try:
            # 편집 인터페이스가 활성화되어 있고 해당 툴 메뉴가 선택되어 있을 때만 실행
            if (self.edit_interface is None or 
                self.current_tool_menu_id != tool_menu_id or 
                not hasattr(self, 'current_has_section_var')):
                return
            
            # 현재 HasSection 값 가져오기
            current_has_section = self.config_data.get(tool_menu_id, {}).get("HasSection", True)
            
            # 체크박스 상태 업데이트
            self.current_has_section_var.set(current_has_section)
                        
        except Exception as e:
            logger.error(f"카테고리 정보 섹션 새로고침 중 오류: {e}")
    
    def add_new_tool_menu(self):
        """새 카테고리 추가"""
        dialog = NewToolMenuAnchorDialog(self.root, self.config_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            result = dialog.result  # 타입 힌트를 위한 임시 변수
            if isinstance(result, (list, tuple)) and len(result) == 4:  # 새 형식: (id, name, is_anchor, has_section)
                tool_menu_id, category_name, _, has_section = result
            elif isinstance(result, (list, tuple)) and len(result) >= 2:  # 이전 호환성: (id, name)
                tool_menu_id, category_name = result[0], result[1]
                has_section = True  # 기본값
            else:
                self._show_error("오류", "유효하지 않은 결과 형식입니다.")
                return
            
            # 중복 확인
            if tool_menu_id in self.config_data:
                self._show_warning("경고", f"카테고리 '{tool_menu_id}'가 이미 존재합니다.")
                return
            
            # 새 카테고리 추가
            category_data: Dict[str, Any] = {"items": []}
            
            # HasSection 설정 추가
            if has_section is not None:
                category_data["HasSection"] = has_section
            
            self.config_data[tool_menu_id] = category_data
            self.mark_as_modified()
            self.refresh_category_list()

            self.update_status(f"🆕 툴 메뉴 '{category_name}' 추가됨!")

    def delete_selected_tool_menu(self):
        """선택된 툴 메뉴 삭제"""
        selection = self.category_listbox.curselection()
        if not selection:
            self._show_warning("경고", "삭제할 툴 메뉴를 선택하세요.")
            return
        
        index = selection[0]
        if index not in self.category_data:
            return
        
        tool_menu_id, category_name = self.category_data[index]
        
        # 엔트리 개수 확인
        item_count = len(self.config_data.get(tool_menu_id, {}).get("items", []))
        
        # 삭제 확인
        confirm_msg = f"정말로 '{category_name}' 툴 메뉴를 삭제하시겠습니까?\n\n"
        confirm_msg += f"• {item_count}개의 메뉴 엔트리가 함께 삭제됩니다.\n"
        confirm_msg += "• 이 작업은 되돌릴 수 없습니다."

        if messagebox.askyesno("툴 메뉴 삭제 확인", confirm_msg, icon="warning"):
            # config_data에서 제거
            if tool_menu_id in self.config_data:
                del self.config_data[tool_menu_id]
            
            # UI 초기화
            if self.current_tool_menu_id == tool_menu_id:
                self.clear_content_area()
            
            self.mark_as_modified()
            self.refresh_category_list()
            self.update_status(f"🗑️ 툴 메뉴 '{category_name}' 삭제됨!")
    
    def show_tool_menu_content(self, tool_menu_id, category_name):
        """선택된 툴 메뉴의 내용을 표시"""
        self.current_tool_menu_id = tool_menu_id
        
        # 패널 제목 업데이트 (툴 메뉴 선택됨, 엔트리는 아직 선택 안됨)
        self.update_panel_titles(category_name=category_name)
        
        # 기존 트리뷰 제거
        for widget in self.menu_tree_frame.winfo_children():
            widget.destroy()
        
        # 새 트리뷰 생성
        self.current_menu_treeview = self._create_menu_treeview(self.menu_tree_frame, tool_menu_id)
        
        # 편집 폼 제거
        for widget in self.edit_form_frame.winfo_children():
            widget.destroy()
        
        # 새 편집 폼 생성
        self.current_widgets = self._create_edit_form(self.edit_form_frame, tool_menu_id)
        self.current_widgets['treeview'] = self.current_menu_treeview
        
        # 기존 코드 호환성을 위해 tabs에도 저장
        self.tabs[tool_menu_id] = self.current_widgets
        
        # 버튼 활성화
        self._enable_menu_buttons()
        
        # 트리뷰에 데이터 로드
        self.refresh_tab(tool_menu_id)
    
    def _create_menu_treeview(self, parent, tool_menu_id):
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
        treeview.bind("<<TreeviewSelect>>", lambda e: self.on_item_select(tool_menu_id))
        
        return treeview
    
    def _enable_menu_buttons(self):
        """메뉴 버튼들 활성화"""
        if self.current_tool_menu_id:
            self.add_btn.configure(state=tk.NORMAL)
            self.delete_item_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.delete_entry(self.current_tool_menu_id)
            )
            self.move_up_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.move_entry_up(self.current_tool_menu_id)
            )
            self.move_down_btn.configure(
                state=tk.NORMAL, 
                command=lambda: self.move_entry_down(self.current_tool_menu_id)
            )
    
    def clear_content_area(self):
        """내용 영역 초기화"""
        self.current_tool_menu_id = None
        
        # 패널 제목 초기화
        self.update_panel_titles()
        
        # 트리뷰 제거
        for widget in self.menu_tree_frame.winfo_children():
            widget.destroy()
        
        # 편집 폼 제거
        for widget in self.edit_form_frame.winfo_children():
            widget.destroy()
        
        # 버튼 비활성화
        self.add_btn.configure(state=tk.DISABLED)
        self.delete_item_btn.configure(state=tk.DISABLED)
        self.move_up_btn.configure(state=tk.DISABLED)
        self.move_down_btn.configure(state=tk.DISABLED)
        
        self.current_widgets = None
        self.current_menu_treeview = None
    
    def create_category_content(self, parent, tool_menu_id):
        """카테고리 내용 생성 (기존 create_tab_content와 동일)"""
        # 메인 컨테이너
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 좌측: 엔트리 목록
        left_frame = self._create_left_panel(main_container, tool_menu_id)
        
        # 구분선
        separator = ttk.Separator(main_container, orient='vertical')
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 우측: 엔트리 편집
        widgets = self._create_right_panel(main_container, tool_menu_id)
        
        # 트리뷰 위젯을 위젯 딕셔너리에 추가
        widgets['treeview'] = left_frame['treeview']
        
        return widgets
    
    def _setup_menubar(self):
        """편집 모드용 메뉴바 설정"""
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
        edit_menu.add_command(label="➕ 엔트리 추가", command=lambda: self.add_entry_dialog(modal=True))
        edit_menu.add_separator()
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 도구", menu=tools_menu)
        tools_menu.add_command(label="📝 외부 편집기로 열기", command=self.open_in_external_editor)
        tools_menu.add_command(label="📂 파일 위치 열기", command=self.open_file_location)
        tools_menu.add_separator()
        tools_menu.add_command(label="🧪 파일 쓰기 권한 테스트", command=self.test_file_write_permission)
        tools_menu.add_command(label="📋 로그 보기", command=self.show_log_viewer)
    
    def _setup_guide_menubar(self):
        """가이드 모드용 메뉴바 설정"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # TAPython 메뉴
        tapython_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔌 TAPython", menu=tapython_menu)
        tapython_menu.add_command(label="🌐 공식 사이트", command=lambda: self.guide._open_url("https://www.tacolor.xyz/"))
        tapython_menu.add_command(label="📦 GitHub 저장소", command=lambda: self.guide._open_url("https://github.com/cgerchenhp/UE_TAPython_Plugin_Release/releases"))
        tapython_menu.add_separator()
        tapython_menu.add_command(label="📄 새 설정 파일 생성", command=self.guide._create_new_config_file_guide)
        tapython_menu.add_command(label="📁 수동으로 파일 선택", command=self.guide._manual_file_selection_guide)
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ 도움말", menu=help_menu)
        help_menu.add_command(label="📋 로그 보기", command=self.show_log_viewer)
        help_menu.add_separator()
        help_menu.add_command(label="� 최소화\t\tCtrl+M", command=lambda: self.root.iconify())
    
    def _setup_guide_info_frame(self):
        """가이드 모드용 정보 프레임 설정"""
        # 기존 정보 프레임 내용 제거
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        # 가이드 전용 정보 표시
        guide_info = ttk.Frame(self.info_frame)
        guide_info.pack(fill=tk.X, expand=True)
        
        # TAPython 로고와 제목
        title_frame = ttk.Frame(guide_info)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(title_frame, text="🔌", font=("Arial", 16)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(title_frame, text="TAPython Menu Configuration Tool", 
                 font=("Arial", 12, "bold"), foreground="blue").pack(side=tk.LEFT)
        
        # 상태 정보
        status_frame = ttk.Frame(guide_info)
        status_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(status_frame, text="플러그인 설치가 필요합니다", 
                 font=("Arial", 10), foreground="red").pack(side=tk.RIGHT)
    
    def _setup_edit_info_frame(self):
        """편집 모드용 정보 프레임 설정"""
        # 기존 정보 프레임 내용 제거
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        info_frame = ttk.Frame(self.info_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 저장 버튼들 (맨 앞에 배치)
        self._setup_save_buttons(info_frame)
        
        # 파일 경로 표시
        self._setup_file_path_display(info_frame)
        
        # Perforce 상태 표시
        self._setup_perforce_status_display(info_frame)
    
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
        
        # 저장 버튼
        self.save_button = ttk.Button(button_frame, text="💾 저장", command=self.save_config, 
                                     state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 다른 이름으로 저장 버튼
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
    
    def _setup_perforce_status_display(self, parent):
        """Perforce 상태 표시 설정"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Perforce 상태 라벨
        self.perforce_status_label = ttk.Label(
            status_frame, 
            text="Perforce: 비활성화됨", 
            font=("Arial", 10, "bold"),
            foreground="gray"
        )
        self.perforce_status_label.pack(side=tk.RIGHT)
        
        # 초기 상태 업데이트 (비동기로 처리하여 UI 로딩 속도 향상)
        self.root.after(500, self._update_perforce_status_display)  # 100ms에서 500ms로 변경하여 초기 로딩 우선
    
    def _update_perforce_status_display(self):
        """Perforce 상태 표시 업데이트 - 비활성화됨"""
        try:
            self.perforce_status_label.configure(
                text="Perforce: 비활성화됨",
                foreground="gray"
            )
            self.create_tooltip(self.perforce_status_label, 
                              "Perforce 기능이 비활성화되었습니다.")
                
        except Exception as e:
            logger.error(f"Perforce 상태 표시 업데이트 중 오류: {e}")
            self.perforce_status_label.configure(
                text="Perforce: 오류",
                foreground="red"
            )
            self.create_tooltip(self.perforce_status_label, 
                              f"Perforce 상태 확인 중 오류: {str(e)}")
    
    def _get_perforce_status_text(self, p4_status):
        """Perforce 상태에 따른 표시 텍스트, 색상, 툴팁 반환"""
        status_map = {
            "edit": ("편집 중", "green", "파일이 체크아웃되어 편집 가능합니다."),
            "add": ("추가됨", "blue", "새 파일로 추가되었습니다."),
            "delete": ("삭제 예정", "orange", "파일이 삭제 예정입니다."),
            "sync": ("읽기 전용", "red", "파일이 읽기 전용 상태입니다. 편집하려면 체크아웃이 필요합니다."),
            "locked_by_other": ("다른 사용자가 사용 중", "purple", "다른 사용자가 이 파일을 체크아웃했습니다."),
            "not_in_perforce": ("관리 외", "gray", "파일이 Perforce 관리 하에 있지 않습니다."),
            "error": ("오류", "red", "Perforce 상태를 확인할 수 없습니다."),
            "unknown": ("알 수 없음", "gray", "Perforce 상태를 알 수 없습니다.")
        }
        
        return status_map.get(p4_status, ("알 수 없음", "gray", f"알 수 없는 상태: {p4_status}"))
    
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
    
    def _get_all_tool_menus(self):
        """모든 툴 메뉴 목록 반환"""
        return ALL_TOOL_MENUS
    

    
    def _get_available_tool_menus(self, all_tool_menus):
        """설정 파일에 실제로 존재하는 툴 메뉴만 반환"""
        available_tool_menus = []
        
        # 모든 툴 메뉴를 동등하게 처리 - 설정 파일에 존재하는 것만 표시
        if self.config_data:
            for tool_menu_id, tool_menu_name in all_tool_menus:
                if tool_menu_id in self.config_data:
                    # JSON의 name 필드는 무시하고 항상 기본 이름 사용
                    available_tool_menus.append((tool_menu_id, tool_menu_name))
        
        return available_tool_menus
    
    def refresh_tabs_if_needed(self):
        """새로운 툴 메뉴가 추가되었을 때 툴 메뉴 리스트 새로고침"""
        # 편집 인터페이스가 활성화되어 있을 때만 실행
        if self.edit_interface is not None and hasattr(self, 'category_listbox'):
            self.refresh_category_list()
    
    def create_tab_content(self, parent, tool_menu_id):
        """탭 내용 생성 - 새 레이아웃에서는 create_category_content와 동일"""
        return self.create_category_content(parent, tool_menu_id)
    
    def _create_left_panel(self, parent, tool_menu_id):
        """좌측 패널 (엔트리 목록) 생성"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        
        # 좌측 프레임의 폭을 제한
        left_frame.pack_propagate(False)
        left_frame.configure(width=380)
        
        # 카테고리 정보 및 설정
        self._create_category_info_section(left_frame, tool_menu_id)
        
        ttk.Label(left_frame, text="메뉴 엔트리", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 트리뷰 생성
        treeview = self._create_treeview(left_frame, tool_menu_id)
        
        # 컨트롤 버튼들
        self._create_control_buttons(left_frame, tool_menu_id)
        
        return {'treeview': treeview}
    
    def _create_category_info_section(self, parent, tool_menu_id):
        """카테고리 정보 및 설정 섹션 생성"""
        info_frame = ttk.LabelFrame(parent, text="카테고리 설정")
        info_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # 카테고리 이름 표시
        display_name = tool_menu_id.replace(".", " > ") if "." in tool_menu_id else tool_menu_id
        ttk.Label(info_frame, text=f"카테고리: {display_name}", 
                 font=("Arial", 8, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # HasSection 설정 (모든 카테고리에 적용 가능)
        self.current_has_section_var = tk.BooleanVar()
        # 현재 설정값 로드
        current_has_section = self.config_data.get(tool_menu_id, {}).get("HasSection", True)
        self.current_has_section_var.set(current_has_section)
        
        has_section_check = ttk.Checkbutton(
            info_frame, 
            text="HasSection (구분선 표시)", 
            variable=self.current_has_section_var,
            command=lambda: self._update_category_has_section(tool_menu_id, self.current_has_section_var.get())
        )
        has_section_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # 툴팁 추가
        tooltip_text = """메뉴 툴 메뉴의 구분선 표시 여부를 설정합니다.

• 체크: 구분선이 표시됩니다 (기본값)
• 체크 해제: 구분선이 숨겨집니다 (툴바에서 권장)"""
        self.create_tooltip(has_section_check, tooltip_text)
        
        # 툴바인 경우 권장사항 표시
        if "ToolBar" in tool_menu_id or "Toolbar" in tool_menu_id:
            ttk.Label(info_frame, text="💡 툴바에서는 HasSection=false 권장", 
                     font=("Arial", 7), foreground="blue").pack(anchor=tk.W, padx=5, pady=1)
    
    def _update_category_has_section(self, tool_menu_id, has_section_value):
        """카테고리의 HasSection 값 업데이트"""
        try:
            # config_data에서 카테고리 확인/생성
            if tool_menu_id not in self.config_data:
                self.config_data[tool_menu_id] = {"items": []}
            
            # HasSection 값 설정
            if has_section_value:
                self.config_data[tool_menu_id]["HasSection"] = True
            else:
                self.config_data[tool_menu_id]["HasSection"] = False
            
            # 변경사항 추적
            self.mark_as_modified()
            
            # 상태 메시지
            status_msg = f"✅ HasSection = {has_section_value}" if has_section_value else f"❌ HasSection = {has_section_value}"
            self.update_status(f"🔧 '{tool_menu_id}' {status_msg}")
            
            logger.debug(f"카테고리 '{tool_menu_id}'의 HasSection을 {has_section_value}로 설정")
            
        except Exception as e:
            error_msg = f"HasSection 설정 중 오류: {str(e)}"
            logger.error(error_msg)
            self._show_error("오류", error_msg)
    
    def _create_treeview(self, parent, tool_menu_id):
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
        treeview.bind("<<TreeviewSelect>>", lambda e: self.on_item_select(tool_menu_id))
        
        return treeview
    
    def _create_control_buttons(self, parent, tool_menu_id):
        """엔트리 컨트롤 버튼들 생성"""
        list_btn_frame = ttk.Frame(parent)
        list_btn_frame.pack(fill=tk.X, padx=5, pady=(5, 5))
        
        # 첫 번째 줄: 추가 관련 버튼들
        btn_row1 = ttk.Frame(list_btn_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Button(btn_row1, text="➕ 추가", 
                  command=lambda: self.add_entry(tool_menu_id)).pack(side=tk.LEFT, padx=(0, 5))
        
        # 두 번째 줄: 편집 관련 버튼들
        btn_row2 = ttk.Frame(list_btn_frame)
        btn_row2.pack(fill=tk.X)
        
        ttk.Button(btn_row2, text="🗑️ 삭제", 
                  command=lambda: self.delete_entry(tool_menu_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row2, text="⬆️ 위로", 
                  command=lambda: self.move_entry_up(tool_menu_id)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row2, text="⬇️ 아래로", 
                  command=lambda: self.move_entry_down(tool_menu_id)).pack(side=tk.LEFT)
    
    def _create_right_panel(self, parent, tool_menu_id):
        """우측 패널 (엔트리 편집) 생성"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="엔트리 편집", font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 설명 라벨
        help_text = "아래에서 엔트리 정보를 수정한 후 '변경사항 저장' 버튼을 클릭하세요."
        ttk.Label(right_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(anchor=tk.W, padx=5, pady=(2, 5))
        
        # 편집 폼
        return self._create_edit_form(right_frame, tool_menu_id)
    
    def _create_edit_form(self, parent, tool_menu_id):
        """편집 폼 생성 - 타입별 전용 UI"""
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 5))
        
        # 폼 위젯들 생성
        widgets = {}
        
        # 공통 필드들: 이름 (항상 표시)
        widgets.update(self._create_name_field(edit_frame))
        
        # 타입별 전용 UI를 위한 컨테이너
        widgets.update(self._create_type_specific_container(edit_frame))
        
        # 공통 필드들: 아이콘 (항상 표시)
        widgets.update(self._create_icon_field(edit_frame))
        
        # 업데이트 버튼
        widgets.update(self._create_update_button(edit_frame, tool_menu_id))
        
        # 그리드 가중치
        edit_frame.columnconfigure(1, weight=1)
        edit_frame.rowconfigure(2, weight=1)  # 타입별 컨테이너가 확장되도록
        
        return widgets
    
    def _create_type_specific_container(self, parent):
        """타입별 전용 UI 컨테이너 생성"""
        # 타입별 UI가 들어갈 컨테이너
        container_frame = ttk.Frame(parent)
        container_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        container_frame.columnconfigure(0, weight=1)
        container_frame.rowconfigure(0, weight=1)
        
        # 세 가지 타입별 UI 생성
        submenu_widgets = self._create_submenu_ui(container_frame)
        command_widgets = self._create_command_ui(container_frame)
        chameleon_widgets = self._create_chameleon_ui(container_frame)
        
        # 모든 위젯들을 통합하여 반환
        widgets = {}
        widgets.update(submenu_widgets)
        widgets.update(command_widgets)
        widgets.update(chameleon_widgets)
        widgets['type_container'] = container_frame
        
        # 초기에는 command UI만 표시
        self._show_type_ui(widgets, "command")
        
        return widgets
    
    def _create_submenu_ui(self, parent):
        """서브메뉴 전용 UI 생성"""
        submenu_frame = ttk.LabelFrame(parent, text="📁 서브메뉴 설정")
        submenu_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        submenu_frame.columnconfigure(1, weight=1)
        
        # 툴팁
        ttk.Label(submenu_frame, text="툴팁:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        submenu_tooltip_var = tk.StringVar()
        submenu_tooltip_entry = ttk.Entry(submenu_frame, textvariable=submenu_tooltip_var)
        submenu_tooltip_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 설명
        desc_label = ttk.Label(submenu_frame, 
                              text="서브메뉴는 하위 엔트리들을 그룹화합니다.\n이름, 툴팁, 아이콘을 설정할 수 있습니다.",
                              foreground="gray", font=("Arial", 9), justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        return {
            'submenu_frame': submenu_frame,
            'submenu_tooltip_var': submenu_tooltip_var,
            'submenu_tooltip_entry': submenu_tooltip_entry
        }
    
    def _create_command_ui(self, parent):
        """명령어 전용 UI 생성"""
        command_frame = ttk.LabelFrame(parent, text="⚡ Python 명령어 설정")
        command_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        command_frame.columnconfigure(1, weight=1)
        command_frame.rowconfigure(2, weight=1)
        
        # 툴팁
        ttk.Label(command_frame, text="툴팁:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        command_tooltip_var = tk.StringVar()
        command_tooltip_entry = ttk.Entry(command_frame, textvariable=command_tooltip_var)
        command_tooltip_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 활성화
        command_enabled_var = tk.BooleanVar(value=True)
        command_enabled_check = ttk.Checkbutton(command_frame, text="활성화", variable=command_enabled_var)
        command_enabled_check.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Python 명령어
        ttk.Label(command_frame, text="Python 명령어:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        
        cmd_text_frame = ttk.Frame(command_frame)
        cmd_text_frame.grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        command_text = tk.Text(cmd_text_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
        cmd_scrollbar = ttk.Scrollbar(cmd_text_frame, orient=tk.VERTICAL, command=command_text.yview)
        command_text.configure(yscrollcommand=cmd_scrollbar.set)
        
        command_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # canExecuteAction
        ttk.Label(command_frame, text="canExecuteAction:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        
        can_exec_frame = ttk.Frame(command_frame)
        can_exec_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        can_execute_text = tk.Text(can_exec_frame, height=3, wrap=tk.WORD, font=("Consolas", 9))
        can_exec_scrollbar = ttk.Scrollbar(can_exec_frame, orient=tk.VERTICAL, command=can_execute_text.yview)
        can_execute_text.configure(yscrollcommand=can_exec_scrollbar.set)
        
        can_execute_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        can_exec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return {
            'command_frame': command_frame,
            'command_tooltip_var': command_tooltip_var,
            'command_tooltip_entry': command_tooltip_entry,
            'command_enabled_var': command_enabled_var,
            'command_enabled_check': command_enabled_check,
            'command_text': command_text,
            'can_execute_text': can_execute_text
        }
    
    def _create_chameleon_ui(self, parent):
        """Chameleon 전용 UI 생성"""
        chameleon_frame = ttk.LabelFrame(parent, text="🎨 Chameleon Tools 설정")
        chameleon_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        chameleon_frame.columnconfigure(1, weight=1)
        
        # 툴팁
        ttk.Label(chameleon_frame, text="툴팁:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        chameleon_tooltip_var = tk.StringVar()
        chameleon_tooltip_entry = ttk.Entry(chameleon_frame, textvariable=chameleon_tooltip_var)
        chameleon_tooltip_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 활성화
        chameleon_enabled_var = tk.BooleanVar(value=True)
        chameleon_enabled_check = ttk.Checkbutton(chameleon_frame, text="활성화", variable=chameleon_enabled_var)
        chameleon_enabled_check.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ChameleonTools 경로
        ttk.Label(chameleon_frame, text="JSON 파일 경로:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        path_frame = ttk.Frame(chameleon_frame)
        path_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(path_frame, textvariable=chameleon_var, font=("Consolas", 9))
        chameleon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def select_chameleon_file():
            file_path = filedialog.askopenfilename(
                title="Chameleon Tools JSON 파일 선택",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
                initialdir=self._get_chameleon_tools_directory()
            )
            if file_path:
                relative_path = self._convert_to_relative_path(file_path)
                chameleon_var.set(relative_path)
        
        chameleon_button = ttk.Button(path_frame, text="📁 파일 선택", command=select_chameleon_file)
        chameleon_button.pack(side=tk.RIGHT)
        
        # 예시
        example_label = ttk.Label(chameleon_frame, text="예시: ../Python/Example/MinimalExample.json",
                                 foreground="gray", font=("Arial", 8))
        example_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 10))
        
        return {
            'chameleon_frame': chameleon_frame,
            'chameleon_tooltip_var': chameleon_tooltip_var,
            'chameleon_tooltip_entry': chameleon_tooltip_entry,
            'chameleon_enabled_var': chameleon_enabled_var,
            'chameleon_enabled_check': chameleon_enabled_check,
            'chameleon_var': chameleon_var,
            'chameleon_entry': chameleon_entry,
            'chameleon_button': chameleon_button
        }
    
    def _determine_entry_type(self, item_data):
        """엔트리 데이터에서 타입을 결정합니다."""
        if "items" in item_data:
            return "submenu"
        elif "ChameleonTools" in item_data:
            return "chameleonTools"
        elif "command" in item_data or "canExecuteAction" in item_data:
            return "command"
        else:
            # 기본값은 command로 설정
            return "command"

    def _show_type_ui(self, widgets, entry_type):
        """선택된 타입의 UI만 표시"""
        # 모든 타입 UI 숨기기
        for frame_key in ['submenu_frame', 'command_frame', 'chameleon_frame']:
            if frame_key in widgets:
                widgets[frame_key].grid_remove()
        
        # 선택된 타입 UI 표시
        type_frame_map = {
            'submenu': 'submenu_frame',
            'command': 'command_frame', 
            'chameleonTools': 'chameleon_frame'
        }
        
        frame_key = type_frame_map.get(entry_type)
        if frame_key and frame_key in widgets:
            widgets[frame_key].grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
    
    def _load_icon_data(self, tab_widgets, item_data, entry_type=None):
        """아이콘 데이터를 위젯에 로드"""
        try:
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
        except Exception as e:
            logger.error(f"아이콘 데이터 로딩 중 오류: {e}")
            tab_widgets['icon_type_var'].set("없음")
            tab_widgets['icon_name_var'].set("")
    
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
    
    def _create_execution_type_tabs(self, parent):
        """실행 타입 선택 탭 생성 (Command vs Chameleon)"""
        # 탭 컨테이너
        tab_frame = ttk.LabelFrame(parent, text="실행 타입")
        tab_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)
        
        # 탭 노트북
        notebook = ttk.Notebook(tab_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command 탭
        command_frame = ttk.Frame(notebook)
        notebook.add(command_frame, text="Python 명령어")
        
        # Chameleon 탭
        chameleon_frame = ttk.Frame(notebook)
        notebook.add(chameleon_frame, text="Chameleon Tools")
        
        # Command 탭 내용
        command_widgets = self._create_command_tab_content(command_frame)
        
        # Chameleon 탭 내용
        chameleon_widgets = self._create_chameleon_tab_content(chameleon_frame)
        
        # 탭 변경 이벤트 처리
        def on_tab_changed(event):
            selected_tab = notebook.index(notebook.select())
            # 탭이 변경될 때 다른 탭의 내용을 비움
            if selected_tab == 0:  # Command 탭 선택
                if 'chameleon_var' in chameleon_widgets:
                    chameleon_widgets['chameleon_var'].set("")
            elif selected_tab == 1:  # Chameleon 탭 선택
                if 'command_text' in command_widgets:
                    command_widgets['command_text'].delete("1.0", tk.END)
        
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
        
        # 위젯들 통합
        widgets = {}
        widgets.update(command_widgets)
        widgets.update(chameleon_widgets)
        widgets['execution_notebook'] = notebook
        
        return widgets
    
    def _create_command_tab_content(self, parent):
        """Command 탭 내용 생성"""
        # 명령어 텍스트 영역
        cmd_frame = ttk.Frame(parent)
        cmd_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(cmd_frame, text="Python 명령어:").pack(anchor=tk.W, pady=(0, 5))
        
        # 텍스트 위젯과 스크롤바
        text_frame = ttk.Frame(cmd_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        command_text = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
        cmd_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=command_text.yview)
        command_text.configure(yscrollcommand=cmd_scrollbar.set)
        
        command_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # canExecuteAction 필드
        separator = ttk.Separator(cmd_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        ttk.Label(cmd_frame, text="canExecuteAction (선택사항):").pack(anchor=tk.W, pady=(0, 5))
        
        can_exec_frame = ttk.Frame(cmd_frame)
        can_exec_frame.pack(fill=tk.X)
        
        can_execute_text = tk.Text(can_exec_frame, height=3, wrap=tk.WORD, font=("Consolas", 9))
        can_exec_scrollbar = ttk.Scrollbar(can_exec_frame, orient=tk.VERTICAL, command=can_execute_text.yview)
        can_execute_text.configure(yscrollcommand=can_exec_scrollbar.set)
        
        can_execute_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        can_exec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 툴팁 추가
        self.create_tooltip(can_execute_text, 
                           "메뉴 항목 클릭 가능 여부를 결정하는 Python 코드\n"
                           "True를 반환하면 클릭 가능, False면 비활성화")
        
        return {
            'command_text': command_text,
            'can_execute_text': can_execute_text
        }
    
    def _create_chameleon_tab_content(self, parent):
        """Chameleon 탭 내용 생성"""
        # Chameleon Tools 설정
        chameleon_frame = ttk.Frame(parent)
        chameleon_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(chameleon_frame, text="Chameleon Tools JSON 파일 경로:").pack(anchor=tk.W, pady=(0, 5))
        
        # 경로 입력과 파일 선택 버튼
        path_frame = ttk.Frame(chameleon_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        chameleon_var = tk.StringVar()
        chameleon_entry = ttk.Entry(path_frame, textvariable=chameleon_var, font=("Consolas", 9))
        chameleon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
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
        
        chameleon_button = ttk.Button(path_frame, text="📁 파일 선택", command=select_chameleon_file)
        chameleon_button.pack(side=tk.RIGHT)
        
        # 예시 텍스트
        example_text = "예시: ../Python/Example/MinimalExample.json"
        ttk.Label(chameleon_frame, text=example_text, font=("Arial", 8), 
                 foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # 설명 텍스트
        desc_text = """Chameleon Tools는 Unreal Engine의 UI 도구를 생성합니다.
JSON 파일에는 UI 레이아웃과 동작이 정의되어 있어야 합니다."""
        
        desc_label = ttk.Label(chameleon_frame, text=desc_text, font=("Arial", 8), 
                              foreground="gray", wraplength=300, justify=tk.LEFT)
        desc_label.pack(anchor=tk.W, pady=10)
        
        return {
            'chameleon_var': chameleon_var,
            'chameleon_entry': chameleon_entry,
            'chameleon_button': chameleon_button
        }
    
    def _create_enabled_field(self, parent):
        """활성화 체크박스 생성"""
        enabled_var = tk.BooleanVar()
        enabled_var.set(True)  # 기본값을 명시적으로 설정
        enabled_check = ttk.Checkbutton(parent, text="활성화", variable=enabled_var)
        enabled_check.grid(row=2, column=1, sticky=tk.W, pady=2)
        return {'enabled_var': enabled_var, 'enabled_check': enabled_check}
    
    def _create_icon_field(self, parent):
        """아이콘 설정 필드 생성"""
        icon_frame = ttk.LabelFrame(parent, text="아이콘 설정")
        icon_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        icon_frame.columnconfigure(1, weight=1)
        
        # 아이콘 타입 선택과 URL 링크 버튼을 같은 줄에 배치
        ttk.Label(icon_frame, text="아이콘 타입:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # 아이콘 타입 콤보박스와 URL 버튼을 담을 프레임
        icon_type_frame = ttk.Frame(icon_frame)
        icon_type_frame.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        icon_type_frame.columnconfigure(0, weight=0)  # 콤보박스는 고정 크기
        
        icon_type_var = tk.StringVar(value="없음")
        icon_type_combo = ttk.Combobox(icon_type_frame, textvariable=icon_type_var, 
                                      values=["없음", "EditorStyle", "ChameleonStyle", "ImagePath"], 
                                      state="readonly", width=15)
        icon_type_combo.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # URL 링크 버튼 추가
        def open_icon_reference():
            try:
                import webbrowser
                webbrowser.open("https://github.com/EpicKiwi/unreal-engine-editor-icons")
                self.update_status("🌐 언리얼 엔진 아이콘 레퍼런스가 브라우저에서 열렸습니다")
            except Exception as e:
                logger.error(f"URL 열기 실패: {e}")
                messagebox.showerror("오류", f"브라우저를 열 수 없습니다:\n{e}")
        
        icon_ref_button = ttk.Button(icon_type_frame, text="🔗 아이콘 목록", 
                                   command=open_icon_reference, width=12)
        icon_ref_button.grid(row=0, column=1)
        
        # 툴팁 추가
        self.create_tooltip(icon_ref_button, 
                           "언리얼 엔진 에디터 아이콘 목록을 브라우저에서 엽니다\n"
                           "EditorStyle 아이콘 이름을 찾을 때 유용합니다")
        
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
            'icon_name_entry': icon_name_entry,
            'icon_ref_button': icon_ref_button
        }
    
    def _get_chameleon_tools_directory(self):
        """Chameleon Tools 디렉토리 경로 반환"""
        try:
            # 기본 설정 파일 경로에서 TAPython 디렉토리 찾기
            if not self.default_config_path:
                return None
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
    
    def _create_update_button(self, parent, tool_menu_id):
        """업데이트 버튼 생성"""
        update_btn = ttk.Button(parent, text="💾 변경사항 저장", 
                               command=lambda: self.update_entry(tool_menu_id))
        update_btn.grid(row=5, column=1, sticky=tk.W, pady=(10, 0))
        return {'update_btn': update_btn}
    
    def load_default_config(self):
        """기본 설정 파일 로드"""
        if self.default_config_path and os.path.exists(self.default_config_path):
            self.load_config_file(self.default_config_path)
            # load_config_file에서 이미 편집 인터페이스 전환을 처리함
        else:
            # TAPython 플러그인이 설치되지 않은 경우 처리
            self._handle_missing_tapython_plugin()
    
    def _handle_missing_tapython_plugin(self):
        """TAPython 플러그인이 없을 때 처리"""
        error_msg = f"TAPython 플러그인을 찾을 수 없습니다.\n탐색된 경로: {self.default_config_path or '알 수 없음'}"
        logger.error(error_msg)
        
        # 빈 설정으로 시작
        self.config_data = {}
        
        # 플러그인 가용성 상태 업데이트
        self.tapython_available = False
        
        # 메인 창에 안내 화면 표시
        self.guide.show_guide_interface()
    
    def _show_edit_interface(self):
        """메인 창에 편집 인터페이스 표시"""
        try:
            logger.info("편집 인터페이스 생성 시작")
            # 편집 모드용 메뉴바와 정보 프레임 설정
            self._setup_menubar()
            self._setup_edit_info_frame()
            
            # 기존 내용 지우기
            self._clear_main_container()
            
            # 편집 인터페이스 생성 (기존 3패널 구조)
            self.edit_interface = self._create_edit_interface()
            logger.info("편집 인터페이스 생성 완료")
            
        except Exception as e:
            logger.error(f"편집 인터페이스 표시 중 오류: {e}")
    
    def _clear_main_container(self):
        """메인 컨테이너의 모든 위젯 제거"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # 인터페이스 참조 초기화
        self.edit_interface = None
        self.guide_interface = None
    
    def _create_edit_interface(self):
        """편집 인터페이스 생성 (기존 3패널 구조)"""
        # 메인 컨테이너 (수평 분할)
        main_paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 첫 번째 패널 - 툴 메뉴 리스트 (20%)
        self.category_panel = self._create_panel(main_paned, "📂 툴 메뉴")
        main_paned.add(self.category_panel, weight=2)
        
        # 두 번째 패널 - 메뉴 엔트리 리스트 (30%)  
        self.menu_panel = self._create_panel(main_paned, "📄 툴 메뉴 항목을 선택하세요")
        main_paned.add(self.menu_panel, weight=3)
        
        # 세 번째 패널 - 엔트리 편집 영역 (50%)
        self.edit_panel = self._create_panel(main_paned, "✏️ 엔트리 항목을 선택하세요")
        main_paned.add(self.edit_panel, weight=5)
        
        # 각 패널 설정
        self._setup_category_panel(self.category_panel)
        self._setup_menu_panel(self.menu_panel)
        self._setup_edit_panel(self.edit_panel)
        
        # 초기 분할 위치 설정
        self.root.after(100, lambda: self._set_panel_proportions(main_paned))
        
        return main_paned
    
    def _disable_main_interface(self):
        """메인 인터페이스 비활성화"""
        try:
            # 카테고리 리스트박스 비활성화
            if hasattr(self, 'category_listbox'):
                self.category_listbox.configure(state=tk.DISABLED)
            
            # 버튼들 비활성화
            buttons_to_disable = [
                'add_btn', 'delete_item_btn', 
                'move_up_btn', 'move_down_btn', 'save_button'
            ]
            
            for btn_name in buttons_to_disable:
                if hasattr(self, btn_name):
                    getattr(self, btn_name).configure(state=tk.DISABLED)
            
            # 상태 메시지 업데이트
            self.update_status("❌ TAPython 플러그인이 필요합니다", auto_clear=False)
            
        except Exception as e:
            logger.error(f"메인 인터페이스 비활성화 중 오류: {e}")
    
    def open_config_manual(self):
        """수동으로 파일 선택"""
        try:
            file_path = filedialog.askopenfilename(
                title="MenuConfig.json 파일 선택",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")],
                initialdir=os.path.dirname(self.default_config_path)
            )
            
            if file_path:
                self.load_config_file(file_path)
                self._enable_main_interface()
                self.update_status("✅ 설정 파일이 로드되었습니다!")
                
        except Exception as e:
            error_msg = f"파일 선택 중 오류: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("오류", error_msg)
    
    def _enable_main_interface(self):
        """메인 인터페이스 활성화"""
        try:
            # 카테고리 리스트박스 활성화
            if hasattr(self, 'category_listbox'):
                self.category_listbox.configure(state=tk.NORMAL)
            
            # 저장 버튼 활성화 (변경사항이 있는 경우에만)
            if hasattr(self, 'save_button') and self.has_unsaved_changes:
                self.save_button.configure(state=tk.NORMAL)
            
            # 카테고리 목록 새로고침
            self.refresh_category_list()
            
        except Exception as e:
            logger.error(f"메인 인터페이스 활성화 중 오류: {e}")
    
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
            
            logger.debug(f"로드된 config_data 키들: {list(self.config_data.keys())}")
            # 첫 번째 카테고리의 첫 번째 아이템 샘플 출력 (메모리 효율적)
            for category, data in self.config_data.items():
                if isinstance(data, dict) and "items" in data and data["items"]:
                    first_item = data["items"][0]
                    logger.debug(f"{category} 첫 번째 아이템 샘플: {first_item}")
                    break
            
            # 플러그인 가용성 상태 업데이트
            self.tapython_available = True
            
            self.mark_as_saved()  # 로드 후 저장됨 상태로 설정
            
            # 편집 인터페이스로 전환 (파일 로드 성공시 항상 편집 모드)
            logger.info("파일 로드 성공, 편집 인터페이스로 전환 시작")
            self._show_edit_interface()
            
            # 편집 인터페이스가 생성된 후 파일 경로 표시 및 데이터 새로고침
            self.update_file_label(file_path)
            self.refresh_tabs_if_needed()  # 새로운 카테고리 확인 및 탭 추가
            self.refresh_all_tabs()
            logger.info("편집 인터페이스 전환 완료")
            
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
            
            # Perforce 상태 확인 및 체크아웃
            if not self._ensure_file_writable(self.config_file_path):
                return  # 쓰기 권한 확보 실패시 저장 중단
            
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
        # 편집 인터페이스가 활성화되어 있을 때만 실행
        if self.edit_interface is not None and self.current_tool_menu_id:
            self.refresh_current_category()
    
    def refresh_current_category(self):
        """현재 선택된 카테고리 새로고침"""
        if self.current_tool_menu_id and self.current_widgets:
            self.refresh_tab(self.current_tool_menu_id)
    
    def refresh_tab(self, tool_menu_id):
        """특정 탭 새로고침"""
        # 현재 선택된 카테고리인지 확인
        if tool_menu_id != self.current_tool_menu_id:
            return
        
        if not self.current_menu_treeview:
            return
        
        treeview = self.current_menu_treeview
        
        # 트리뷰 초기화
        for item in treeview.get_children():
            treeview.delete(item)
        
        # 데이터가 있는 경우 추가
        if tool_menu_id in self.config_data and "items" in self.config_data[tool_menu_id]:
            items = self.config_data[tool_menu_id]["items"]
            self._populate_tree_items(treeview, "", items)
        
        # 편집 폼 초기화
        self.clear_edit_form(tool_menu_id)
    
    def _populate_tree_items(self, treeview, parent, items):
        """트리뷰에 아이템들을 추가 (재귀적으로 서브메뉴 처리)"""
        for i, item in enumerate(items):
            name = item.get("name", f"Item {i}")
            
            # 엔트리 타입 결정 (헬퍼 메서드 사용)
            item_type, display_name = self._get_entry_type_display(item, name)
            
            # 트리 아이템 추가
            tree_item = treeview.insert(parent, tk.END, text=display_name, values=(item_type,))
            
            # 서브메뉴가 있는 경우 재귀적으로 추가
            if "items" in item and item["items"]:
                self._populate_tree_items(treeview, tree_item, item["items"])
    
    def clear_edit_form(self, tool_menu_id):
        """편집 폼 초기화"""
        # 현재 카테고리인지 확인
        if tool_menu_id != self.current_tool_menu_id or not self.current_widgets:
            return
        
        # 패널 제목 업데이트 (아이템 선택 해제)
        category_name = None
        for cat_id, cat_name in self.category_data.values():
            if cat_id == self.current_tool_menu_id:
                category_name = cat_name
                break
        self.update_panel_titles(category_name=category_name, item_name=None)
        
        tab_widgets = self.current_widgets
        
        # 공통 필드 초기화
        tab_widgets['name_var'].set("")
        
        # 모든 타입별 UI 숨기기
        for frame_key in ['submenu_frame', 'command_frame', 'chameleon_frame']:
            if frame_key in tab_widgets:
                tab_widgets[frame_key].grid_remove()
        
        # 타입별 필드들 초기화
        self._clear_all_type_fields(tab_widgets)
        
        # 아이콘 초기화
        tab_widgets['icon_type_var'].set("없음")
        tab_widgets['icon_name_var'].set("")
        
        # 편집 불가능 상태로 설정
        self.set_edit_state(tool_menu_id, False)
    
    def _clear_all_type_fields(self, tab_widgets):
        """모든 타입별 필드들 초기화"""
        # 서브메뉴 필드들
        if 'submenu_tooltip_var' in tab_widgets:
            tab_widgets['submenu_tooltip_var'].set("")
            
        # 명령어 필드들
        if 'command_tooltip_var' in tab_widgets:
            tab_widgets['command_tooltip_var'].set("")
        if 'command_enabled_var' in tab_widgets:
            tab_widgets['command_enabled_var'].set(True)
        if 'command_text' in tab_widgets:
            tab_widgets['command_text'].delete(1.0, tk.END)
        if 'can_execute_text' in tab_widgets:
            tab_widgets['can_execute_text'].delete(1.0, tk.END)
            
        # Chameleon 필드들
        if 'chameleon_tooltip_var' in tab_widgets:
            tab_widgets['chameleon_tooltip_var'].set("")
        if 'chameleon_enabled_var' in tab_widgets:
            tab_widgets['chameleon_enabled_var'].set(True)
        if 'chameleon_var' in tab_widgets:
            tab_widgets['chameleon_var'].set("")
    
    def set_edit_state(self, tool_menu_id, enabled):
        """편집 폼 활성화/비활성화 (타입별 위젯 처리)"""
        # 현재 카테고리인지 확인
        if tool_menu_id != self.current_tool_menu_id or not self.current_widgets:
            return
        
        tab_widgets = self.current_widgets
        state = tk.NORMAL if enabled else tk.DISABLED
        
        # 공통 위젯들
        common_widgets = [
            'name_entry',
            'icon_type_combo',
            'icon_name_entry',
            'icon_ref_button',
            'update_btn'
        ]
        
        # 타입별 위젯들
        type_widgets = {
            'submenu': [
                'submenu_tooltip_entry'
            ],
            'command': [
                'command_tooltip_entry',
                'command_enabled_check',
                'command_text',
                'can_execute_text'
            ],
            'chameleon': [
                'chameleon_tooltip_entry',
                'chameleon_enabled_check',
                'chameleon_entry',
                'chameleon_button'
            ]
        }
        
        # 공통 위젯들 상태 변경
        for widget_key in common_widgets:
            if widget_key in tab_widgets:
                try:
                    tab_widgets[widget_key].configure(state=state)
                except (tk.TclError, AttributeError):
                    continue
        
        # 현재 표시된 타입별 위젯들만 상태 변경
        for entry_type, widget_keys in type_widgets.items():
            frame_key = f'{entry_type}_frame'
            
            # 해당 타입 프레임이 표시되어 있는지 확인
            if frame_key in tab_widgets:
                try:
                    # grid_info()가 비어있지 않으면 표시된 상태
                    if tab_widgets[frame_key].grid_info():
                        for widget_key in widget_keys:
                            if widget_key in tab_widgets:
                                try:
                                    tab_widgets[widget_key].configure(state=state)
                                except (tk.TclError, AttributeError):
                                    continue
                except (tk.TclError, AttributeError):
                    continue
    
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
    
    def on_item_select(self, tool_menu_id):
        """아이템 선택 이벤트"""
        try:
            # 현재 선택된 카테고리가 아니면 리턴
            if tool_menu_id != self.current_tool_menu_id or not self.current_widgets:
                return
            
            if not self.current_menu_treeview:
                return
            
            treeview = self.current_menu_treeview
            tab_widgets = self.current_widgets
            
            selection = treeview.selection()
            if not selection:
                self.clear_edit_form(tool_menu_id)
                return
            
            selected_item = selection[0]
            
            # 선택된 아이템의 경로를 추적하여 데이터 찾기
            item_data = self._get_item_data_from_tree(treeview, selected_item, tool_menu_id)
            
            if item_data:
                # 엔트리 타입 결정
                entry_type = self._determine_entry_type(item_data)
                
                # 적절한 타입 UI 표시
                self._show_type_ui(tab_widgets, entry_type)
                
                # 공통 필드 로드: 이름
                tab_widgets['name_var'].set(item_data.get("name", ""))
                
                # 타입별 필드 로드
                if entry_type == "submenu":
                    # 서브메뉴: 툴팁만
                    tab_widgets['submenu_tooltip_var'].set(item_data.get("tooltip", ""))
                    
                elif entry_type == "command":
                    # 명령어: 툴팁, 활성화, 명령어, canExecuteAction
                    tab_widgets['command_tooltip_var'].set(item_data.get("tooltip", ""))
                    
                    enabled_value = item_data.get("enabled", True)
                    tab_widgets['command_enabled_var'].set(bool(enabled_value))
                    
                    # 명령어
                    tab_widgets['command_text'].delete(1.0, tk.END)
                    command = item_data.get("command", "")
                    if command:
                        tab_widgets['command_text'].insert(1.0, command)
                    
                    # canExecuteAction
                    tab_widgets['can_execute_text'].delete(1.0, tk.END)
                    can_execute = item_data.get("canExecuteAction", "")
                    if can_execute:
                        tab_widgets['can_execute_text'].insert(1.0, can_execute)
                        
                elif entry_type == "chameleonTools":
                    # Chameleon: 툴팁, 활성화, ChameleonTools
                    tab_widgets['chameleon_tooltip_var'].set(item_data.get("tooltip", ""))
                    
                    enabled_value = item_data.get("enabled", True)
                    tab_widgets['chameleon_enabled_var'].set(bool(enabled_value))
                    
                    tab_widgets['chameleon_var'].set(item_data.get("ChameleonTools", ""))
                
                # 공통: 아이콘 설정 로드
                self._load_icon_data(tab_widgets, item_data, entry_type)
                
                # 패널 제목 업데이트 (아이템 선택됨)
                item_name = item_data.get("name", "")
                category_name = None
                # 현재 카테고리 이름 찾기
                for cat_id, cat_name in self.category_data.values():
                    if cat_id == self.current_tool_menu_id:
                        category_name = cat_name
                        break
                self.update_panel_titles(category_name=category_name, item_name=item_name)
                
                # 편집 가능 상태로 설정
                self.set_edit_state(tool_menu_id, True)
            else:
                self.clear_edit_form(tool_menu_id)
        except tk.TclError as e:
            logger.error(f"Tkinter 트리뷰 오류: {e}")
            self.clear_edit_form(tool_menu_id)
        except AttributeError as e:
            logger.error(f"위젯 속성 오류: {e}")
            self.clear_edit_form(tool_menu_id)
        except KeyError as e:
            logger.error(f"데이터 키 오류: {e}")
            self.clear_edit_form(tool_menu_id)
        except Exception as e:
            logger.error(f"아이템 선택 중 오류: {e}")
            # 에러 발생 시 편집 폼 초기화
            self.clear_edit_form(tool_menu_id)
    
    def _get_item_data_from_tree(self, treeview, tree_item, tool_menu_id):
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
            if tool_menu_id not in self.config_data or "items" not in self.config_data[tool_menu_id]:
                logger.debug(f"카테고리 {tool_menu_id}가 config_data에 없음")
                return None
            
            current_items = self.config_data[tool_menu_id]["items"]
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
    
    def update_entry(self, tool_menu_id):
        """엔트리 업데이트 (타입별 처리)"""
        try:
            # 현재 선택된 툴 메뉴가 아니면 리턴
            if tool_menu_id != self.current_tool_menu_id or not self.current_widgets:
                return
            
            tab_widgets = self.current_widgets
            treeview = tab_widgets['treeview']
            
            selection = treeview.selection()
            if not selection:
                messagebox.showwarning("경고", "업데이트할 엔트리를 선택해주세요.")
                return
            
            selected_item = selection[0]
            item_data = self._get_item_data_from_tree(treeview, selected_item, tool_menu_id)
            
            if not item_data:
                self._show_error("오류", "선택된 엔트리의 데이터를 찾을 수 없습니다.")
                return
            
            # 엔트리 타입 결정
            entry_type = self._determine_entry_type(item_data)
            
            # 공통 필드: 이름
            name = tab_widgets['name_var'].get().strip()
            if not name:
                self._show_warning("경고", "이름은 비워둘 수 없습니다.")
                return
            
            item_data["name"] = name
            
            # 타입별 데이터 업데이트
            if entry_type == "submenu":
                self._update_submenu_data(item_data, tab_widgets)
            elif entry_type == "command":
                self._update_command_data(item_data, tab_widgets)
            elif entry_type == "chameleonTools":
                self._update_chameleon_data(item_data, tab_widgets)
            
            # 아이콘 설정 처리 (모든 타입 공통)
            self._update_icon_data(item_data, tab_widgets)
            
            logger.debug(f"업데이트 후 엔트리 데이터: {item_data}")
            
            # 트리뷰 업데이트
            item_type, display_name = self._get_entry_type_display(item_data, name)
            treeview.item(selected_item, text=display_name, values=(item_type,))
            
            # 상태 메시지
            self.update_status(f"💾 '{name}' 저장 완료 ({entry_type})")
            
            # 변경사항 추적
            self.mark_as_modified()
            
        except Exception as e:
            error_msg = f"엔트리 업데이트 중 오류 발생: {str(e)}"
            logger.error(f"update_entry 오류: {e}")
            traceback.print_exc()
            self._show_error("오류", error_msg)
            self.update_status(f"저장 실패: {str(e)}", auto_clear=False)
    
    def _update_submenu_data(self, item_data, tab_widgets):
        """서브메뉴 데이터 업데이트"""
        # 서브메뉴 전용 필드
        item_data["tooltip"] = tab_widgets['submenu_tooltip_var'].get().strip()
        
        # 불필요한 필드들 제거
        fields_to_remove = ["enabled", "command", "ChameleonTools", "canExecuteAction"]
        for field in fields_to_remove:
            if field in item_data:
                del item_data[field]
    
    def _update_command_data(self, item_data, tab_widgets):
        """명령어 엔트리 데이터 업데이트"""
        # 명령어 전용 필드들
        item_data["tooltip"] = tab_widgets['command_tooltip_var'].get().strip()
        item_data["enabled"] = tab_widgets['command_enabled_var'].get()
        
        # command
        raw_command = tab_widgets['command_text'].get(1.0, tk.END)
        command = raw_command.rstrip('\n').strip()
        if command:
            item_data["command"] = command
        elif "command" in item_data:
            del item_data["command"]
        
        # canExecuteAction
        can_execute_raw = tab_widgets['can_execute_text'].get(1.0, tk.END)
        can_execute = can_execute_raw.rstrip('\n').strip()
        if can_execute:
            item_data["canExecuteAction"] = can_execute
        elif "canExecuteAction" in item_data:
            del item_data["canExecuteAction"]
        
        # ChameleonTools 제거 (배타적 관계)
        if "ChameleonTools" in item_data:
            del item_data["ChameleonTools"]
    
    def _update_chameleon_data(self, item_data, tab_widgets):
        """Chameleon 엔트리 데이터 업데이트"""
        # Chameleon 전용 필드들
        item_data["tooltip"] = tab_widgets['chameleon_tooltip_var'].get().strip()
        item_data["enabled"] = tab_widgets['chameleon_enabled_var'].get()
        
        # ChameleonTools
        chameleon_tools = tab_widgets['chameleon_var'].get().strip()
        if chameleon_tools:
            item_data["ChameleonTools"] = chameleon_tools
        elif "ChameleonTools" in item_data:
            del item_data["ChameleonTools"]
        
        # command 관련 필드들 제거 (배타적 관계)
        fields_to_remove = ["command", "canExecuteAction"]
        for field in fields_to_remove:
            if field in item_data:
                del item_data[field]
    
    def _update_icon_data(self, item_data, tab_widgets):
        """아이콘 데이터 업데이트 (모든 타입 공통)"""
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
            del item_data["icon"]
    
    def add_entry(self, tool_menu_id):
        """엔트리 추가"""
        # modal 창으로 열어 포커스 유지
        self.add_entry_dialog(tool_menu_id, modal=True)
    
    def _populate_parent_list(self, treeview, parent, parent_list, prefix=""):
        """부모 아이템 목록 생성 (메모리 효율적)"""
        children = treeview.get_children(parent)
        for child in children:
            values = treeview.item(child, "values")
            if values and values[0] == "📁 서브메뉴":
                # 트리에서 실제 데이터를 가져와서 순수한 이름 사용
                item_data = self._get_item_data_from_tree(treeview, child, self.current_tool_menu_id)
                if item_data and "name" in item_data:
                    actual_name = item_data["name"]
                    if prefix:
                        full_text = f"{prefix}{actual_name}"
                        parent_list.append(full_text)
                        new_prefix = f"{full_text}/"
                    else:
                        parent_list.append(actual_name)
                        new_prefix = f"{actual_name}/"
                    self._populate_parent_list(treeview, child, parent_list, new_prefix)
    
    def _find_parent_by_name(self, tool_menu_id, parent_name):
        """이름으로 부모 아이템 데이터 찾기"""
        if tool_menu_id not in self.config_data or "items" not in self.config_data[tool_menu_id]:
            return None
        
        # 경로를 "/"로 분할
        path_parts = parent_name.split("/")
        
        # 루트에서 시작하여 경로를 따라 탐색
        current_items = self.config_data[tool_menu_id]["items"]
        
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
    
    def add_entry_dialog(self, tool_menu_id=None, modal=True):
        """엔트리 추가 다이얼로그 (새로운 클래스 사용)"""
        dialog = NewEntryDialog(self.root, self, tool_menu_id)
        self.root.wait_window(dialog.dialog)
        return dialog.result
    
    def delete_entry(self, tool_menu_id):
        """엔트리 삭제"""
        # 현재 카테고리가 없으면 리턴
        if not self.current_tool_menu_id or not self.current_widgets:
            self._show_warning("경고", "툴 메뉴를 먼저 선택해주세요.")
            return
        
        tab_widgets = self.current_widgets
        treeview = tab_widgets['treeview']
        
        selection = treeview.selection()
        if not selection:
            self._show_warning("경고", "삭제할 엔트리를 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "정말 이 엔트리를 삭제하시겠습니까?"):
            selected_item = selection[0]
            
            # 엔트리 경로 추적하여 삭제
            if self._delete_entry_from_data(treeview, selected_item, tool_menu_id):
                self.refresh_tab(tool_menu_id)
                self.mark_as_modified()  # 변경사항 추적
                self.update_status("🗑️ 엔트리가 삭제되었습니다!")
    
    def _delete_entry_from_data(self, treeview, tree_item, tool_menu_id):
        """데이터에서 엔트리 삭제"""
        # 선택된 엔트리의 경로를 추적
        path = []
        current = tree_item
        
        while current:
            path.insert(0, current)
            current = treeview.parent(current)
        
        if tool_menu_id not in self.config_data or "items" not in self.config_data[tool_menu_id]:
            return False
        
        # 부모 컨테이너와 인덱스 찾기
        current_items = self.config_data[tool_menu_id]["items"]
        
        for i, tree_id in enumerate(path[:-1]):
            index = self._get_tree_item_index(treeview, tree_id)
            if index >= len(current_items):
                return False
            
            current_item = current_items[index]
            if "items" not in current_item:
                return False
            
            current_items = current_item["items"]
        
        # 마지막 엔트리 삭제
        final_index = self._get_tree_item_index(treeview, path[-1])
        if final_index < len(current_items):
            del current_items[final_index]
            return True
        
        return False
    
    def move_entry_up(self, tool_menu_id):
        """엔트리 위로 이동"""
        # 현재 카테고리가 없으면 리턴
        if not self.current_tool_menu_id or not self.current_widgets:
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
            return  # 이미 첫 번째 엔트리
        
        current_index = siblings.index(selected_item)
        if current_index > 0:
            # 데이터에서 이동
            if self._move_entry_in_data(treeview, selected_item, tool_menu_id, -1):
                # 선택된 엔트리의 경로를 기억
                item_path = self._get_entry_path(treeview, selected_item)
                
                self.refresh_tab(tool_menu_id)
                self.mark_as_modified()  # 변경사항 추적
                
                # 이동된 위치에서 엔트리를 다시 선택
                if item_path:
                    moved_item = self._find_entry_by_path(treeview, item_path, current_index - 1)
                    if moved_item:
                        treeview.selection_set(moved_item)
                        self.on_item_select(tool_menu_id)
    
    def move_entry_down(self, tool_menu_id):
        """엔트리 아래로 이동"""
        # 현재 카테고리가 없으면 리턴
        if not self.current_tool_menu_id or not self.current_widgets:
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
            return  # 이미 마지막 엔트리
        
        current_index = siblings.index(selected_item)
        if current_index < len(siblings) - 1:
            # 데이터에서 이동
            if self._move_entry_in_data(treeview, selected_item, tool_menu_id, 1):
                # 선택된 엔트리의 경로를 기억
                item_path = self._get_entry_path(treeview, selected_item)
                
                self.refresh_tab(tool_menu_id)
                self.mark_as_modified()  # 변경사항 추적
                
                # 이동된 위치에서 엔트리를 다시 선택
                if item_path:
                    moved_item = self._find_entry_by_path(treeview, item_path, current_index + 1)
                    if moved_item:
                        treeview.selection_set(moved_item)
                        self.on_item_select(tool_menu_id)
    
    def _get_entry_path(self, treeview, tree_item):
        """트리 엔트리의 경로를 텍스트로 가져오기"""
        path = []
        current = tree_item
        
        while current:
            text = treeview.item(current, "text")
            path.insert(0, text)
            current = treeview.parent(current)
        
        return path
    
    def _find_entry_by_path(self, treeview, path, target_index):
        """경로를 통해 트리 엔트리 찾기"""
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
        
        # 마지막 레벨에서 target_index에 해당하는 엔트리 반환
        if target_index < len(current_children):
            return current_children[target_index]
        
        return None
    
    def _move_entry_in_data(self, treeview, tree_item, tool_menu_id, direction):
        """데이터에서 엔트리 이동 (direction: -1=위로, 1=아래로)"""
        # 선택된 엔트리의 경로를 추적
        path = []
        current = tree_item
        
        while current:
            path.insert(0, current)
            current = treeview.parent(current)
        
        if tool_menu_id not in self.config_data or "items" not in self.config_data[tool_menu_id]:
            return False
        
        # 부모 컨테이너 찾기
        current_items = self.config_data[tool_menu_id]["items"]
        
        for i, tree_id in enumerate(path[:-1]):
            index = self._get_tree_item_index(treeview, tree_id)
            if index >= len(current_items):
                return False
            
            current_item = current_items[index]
            if "items" not in current_item:
                return False
            
            current_items = current_item["items"]
        
        # 마지막 엔트리 이동
        final_index = self._get_tree_item_index(treeview, path[-1])
        new_index = final_index + direction
        
        if 0 <= new_index < len(current_items):
            # 엔트리 교환
            current_items[final_index], current_items[new_index] = \
                current_items[new_index], current_items[final_index]
            return True
        
        return False
    
    def add_new_category_dialog(self):
        """새 카테고리 추가 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        self._setup_dialog(dialog, "새 카테고리 추가", 600, 400, modal=True)
        
        # 메인 프레임
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 설명
        desc_text = """메뉴 카테고리를 추가하면 Unreal Engine의 다양한 위치에 메뉴를 추가할 수 있습니다.
아래에서 카테고리 이름을 입력하거나 미리 정의된 목록에서 선택하세요."""
        ttk.Label(main_frame, text=desc_text, wraplength=550, 
                 font=("Arial", 9), foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # 카테고리 입력
        ttk.Label(main_frame, text="카테고리 이름:").pack(anchor=tk.W, pady=(0, 5))
        category_var = tk.StringVar()
        category_entry = ttk.Entry(main_frame, textvariable=category_var, width=60)
        category_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 미리 정의된 카테고리 목록
        ttk.Label(main_frame, text="미리 정의된 메뉴 카테고리:").pack(anchor=tk.W, pady=(10, 5))
        
        # 리스트박스와 스크롤바
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # 미리 정의된 툴 메뉴들 추가 (Tool Menu Anchor 부분만)
        predefined_categories = [tool_menu_id for tool_menu_id, _ in ALL_TOOL_MENUS 
                               if not tool_menu_id.startswith('On')]
        
        for category in predefined_categories:
            listbox.insert(tk.END, category)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 리스트박스 선택 시 입력 필드에 복사
        def on_listbox_select(event):
            selection = listbox.curselection()
            if selection:
                category_var.set(listbox.get(selection[0]))
        
        listbox.bind("<<ListboxSelect>>", on_listbox_select)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # HasSection 설정 (Tool Menu Anchor 스타일 카테고리용)
        has_section_frame = ttk.Frame(main_frame)
        has_section_frame.pack(fill=tk.X, pady=(10, 0))
        
        has_section_var = tk.BooleanVar(value=True)  # 기본값 True
        has_section_check = ttk.Checkbutton(
            has_section_frame, 
            text="HasSection (구분선 표시) - 새 카테고리의 기본 설정", 
            variable=has_section_var
        )
        has_section_check.pack(anchor=tk.W)
        
        # 툴팁 추가
        tooltip_text = """새로 추가될 카테고리의 HasSection 기본값을 설정합니다.

• 체크: 구분선이 표시됩니다 (기본값)
• 체크 해제: 구분선이 숨겨집니다 (툴바에서 권장)"""
        self.create_tooltip(has_section_check, tooltip_text)
        
        def add_category():
            category_name = category_var.get().strip()
            has_section_value = has_section_var.get()
            
            if not category_name:
                self._show_warning("경고", "카테고리 이름을 입력해주세요.")
                return
            
            # 새로운 카테고리로 추가
            if category_name not in self.config_data:
                self.config_data[category_name] = {
                    "HasSection": has_section_value,
                    "items": []
                }
                self.mark_as_modified()
                
                # 새로운 카테고리 추가 후 카테고리 리스트 새로고침
                self.mark_as_modified()
                self.refresh_category_list()
                
                status_msg = f"HasSection={has_section_value}" 
                self.update_status(f"🔧 카테고리 '{category_name}' 추가됨 ({status_msg})")
                dialog.destroy()
            else:
                self._show_warning("중복", f"'{category_name}'는 이미 존재합니다.")
        
        ttk.Button(button_frame, text="✅ 추가", command=add_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT)
        
        category_entry.focus_set()
    
    def remove_category_dialog(self):
        """카테고리 삭제 다이얼로그 - 모든 카테고리를 동등하게 취급"""
        # 삭제 가능한 카테고리 목록 생성 (모든 카테고리 삭제 가능)
        removable_categories = list(self.config_data.keys())
        
        if not removable_categories:
            messagebox.showinfo("정보", "삭제할 수 있는 카테고리가 없습니다.")
            return
        
        dialog = tk.Toplevel(self.root)
        self._setup_dialog(dialog, "카테고리 삭제", 500, 350, modal=True)
        
        # 메인 프레임
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 설명
        desc_text = """삭제할 툴 메뉴를 선택하세요.
삭제하면 해당 툴 메뉴의 모든 메뉴 엔트리가 함께 제거됩니다."""
        ttk.Label(main_frame, text=desc_text, wraplength=450, 
                 font=("Arial", 9), foreground="red").pack(anchor=tk.W, pady=(0, 10))
        
        # 삭제할 툴 메뉴 선택
        ttk.Label(main_frame, text="삭제할 툴 메뉴:").pack(anchor=tk.W, pady=(0, 5))
        
        # 리스트박스와 스크롤바
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(list_frame, height=10)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # 삭제 가능한 툴 메뉴들 추가
        for category in sorted(removable_categories):
            # 엔트리 개수도 함께 표시
            item_count = len(self.config_data.get(category, {}).get("items", []))
            display_text = f"{category} ({item_count}개 엔트리)"
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
                anchor_name = selected_text.split(" (")[0]  # " (n개 엔트리)" 부분 제거
                item_count = len(self.config_data.get(anchor_name, {}).get("items", []))
                info_label.configure(
                    text=f"선택: {anchor_name}\n엔트리 수: {item_count}개\n⚠️ 이 툴 메뉴의 모든 데이터가 삭제됩니다!",
                    foreground="red"
                )
        
        listbox.bind("<<ListboxSelect>>", on_listbox_select)
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def remove_category():
            selection = listbox.curselection()
            if not selection:
                self._show_warning("경고", "삭제할 툴 메뉴를 선택해주세요.")
                return
            
            selected_text = listbox.get(selection[0])
            category_name = selected_text.split(" (")[0]  # " (n개 엔트리)" 부분 제거
            item_count = len(self.config_data.get(category_name, {}).get("items", []))
            
            # 최종 확인
            confirm_msg = f"정말로 '{category_name}'를 삭제하시겠습니까?\n\n"
            confirm_msg += f"• {item_count}개의 메뉴 엔트리가 함께 삭제됩니다.\n"
            confirm_msg += "• 이 작업은 되돌릴 수 없습니다.\n"
            confirm_msg += "• 현재 설정을 저장하지 않았다면 먼저 저장하는 것을 권장합니다."
            
            if messagebox.askyesno("삭제 확인", confirm_msg, icon="warning"):
                try:
                    # config_data에서 제거
                    if category_name in self.config_data:
                        del self.config_data[category_name]
                    
                    # 현재 선택된 툴 메뉴가 삭제된 툴 메뉴인 경우 초기화
                    if self.current_tool_menu_id == category_name:
                        self.clear_content_area()
                    
                    self.mark_as_modified()
                    self.refresh_category_list()
                    self.update_status(f"🗑️ 툴 메뉴 '{category_name}' 삭제됨!")
                    dialog.destroy()
                    
                except Exception as e:
                    error_msg = f"툴 메뉴 삭제 중 오류: {str(e)}"
                    logger.error(error_msg)
                    self._show_error("오류", error_msg)
        
        ttk.Button(button_frame, text="🗑️ 삭제", command=remove_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 취소", command=dialog.destroy).pack(side=tk.LEFT)
        
        # 첫 번째 항목 자동 선택
        if removable_categories:
            listbox.selection_set(0)
            on_listbox_select(None)
    
    def _ensure_file_writable(self, file_path):
        """파일이 쓰기 가능한지 확인하고 필요시 처리"""
        try:
            logger.info(f"파일 쓰기 권한 확인 시작: {file_path}")
            
            # 함수를 통해 파일을 쓰기 가능하게 만들기
            success, message = ensure_file_writable(file_path)
            
            if success:
                logger.info(f"파일 쓰기 가능: {file_path} - {message}")
                self.update_status(f"✅ {message}")
                return True
            else:
                logger.warning(f"파일 쓰기 불가: {file_path} - {message}")
                
                # 사용자에게 수동 처리 옵션 제공
                result = messagebox.askyesnocancel(
                    "파일 쓰기 권한 없음",
                    f"파일을 쓰기 가능한 상태로 만들 수 없습니다:\n{file_path}\n\n"
                    f"상태: {message}\n\n"
                    "수동으로 파일 권한을 변경한 후 '예'를 클릭하세요.\n\n"
                    "계속 진행하시겠습니까?",
                    icon="warning"
                )
                
                if result is True:
                    # 다시 확인
                    return is_file_writable(file_path)
                else:
                    return False
            
        except Exception as e:
            logger.error(f"파일 쓰기 권한 확인 중 오류: {e}")
            self._show_error("오류", f"파일 쓰기 권한을 확인할 수 없습니다:\n{str(e)}")
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
        traceback.print_exc()
    finally:
        # 최종 리소스 정리 (앱이 정상적으로 정리되지 않은 경우에만)
        if app and not getattr(app, '_resources_cleaned', False):
            try:
                app.cleanup_resources()
            except:
                pass


class NewToolMenuAnchorDialog:
    """새 툴 메뉴 추가 다이얼로그"""
    
    def __init__(self, parent, config_data=None):
        self.result = None
        self.config_data = config_data or {}
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("새 툴 메뉴 항목 추가")
        self.dialog.geometry("600x650")
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
        
        # HasSection 옵션 (모든 툴 메뉴에 적용)
        self.section_options_frame = ttk.LabelFrame(main_frame, text="툴 메뉴 옵션", padding=10)
        self.section_options_frame.pack(fill=tk.X, pady=(10, 15))
        
        self.has_section_var = tk.BooleanVar(value=True)
        self.has_section_check = ttk.Checkbutton(
            self.section_options_frame, 
            text="HasSection (구분선 표시)", 
            variable=self.has_section_var
        )
        self.has_section_check.pack(anchor=tk.W)
        
        # 미리 정의된 메뉴 목록 (참고용)
        self.predefined_frame = ttk.LabelFrame(main_frame, text="미리 정의된 메뉴 예시", padding=10)
        self.predefined_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 리스트박스
        listbox_frame = ttk.Frame(self.predefined_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.anchor_listbox = tk.Listbox(listbox_frame, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.anchor_listbox.yview)
        self.anchor_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 리스트박스 선택 시 ID 필드에 복사
        self.anchor_listbox.bind("<<ListboxSelect>>", self.on_anchor_select)
        
        self.anchor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 설명
        self.info_label = ttk.Label(main_frame, foreground="gray")
        self.info_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 항상 미리 정의된 목록과 설명 표시
        self.predefined_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.info_label.configure(text="• 회색 텍스트는 이미 존재하는 툴 메뉴입니다")
        
        # 사용 가능한 툴 메뉴 목록 채우기
        self._populate_available_categories()
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        self.add_button = ttk.Button(button_frame, text="추가", command=self.add_category, state=tk.DISABLED)
        self.add_button.pack(side=tk.RIGHT)
        
        # Enter 키 바인딩
        self.dialog.bind('<Return>', lambda e: self.add_category())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # 포커스 설정
        self.tool_menu_id_entry.focus()
        
        # 초기 버튼 상태 설정
        self._validate_input()
    
    def _populate_available_categories(self):
        """사용 가능한 툴 메뉴 목록 채우기 (이미 존재하는 것은 제외)"""
        # 중앙화된 툴 메뉴 목록에서 ID만 추출
        all_categories = [tool_menu_id for tool_menu_id, _ in ALL_TOOL_MENUS]
        
        # 이미 존재하는 툴 메뉴와 사용 가능한 툴 메뉴 구분
        existing_categories = set(self.config_data.keys())
        
        for category in sorted(all_categories):
            if category in existing_categories:
                # 이미 존재하는 툴 메뉴는 회색으로 표시하고 비활성화
                self.anchor_listbox.insert(tk.END, f"{category} (이미 존재)")
                # 마지막 항목의 색상을 회색으로 변경
                last_index = self.anchor_listbox.size() - 1
                self.anchor_listbox.itemconfig(last_index, {'fg': 'gray'})
            else:
                # 사용 가능한 툴 메뉴는 일반 텍스트로 표시
                self.anchor_listbox.insert(tk.END, category)
    
    def on_anchor_select(self, event):
        """미리 정의된 메뉴 선택 시 ID 필드에 복사"""
        selection = self.anchor_listbox.curselection()
        if selection:
            anchor_name = self.anchor_listbox.get(selection[0])
            
            # 이미 존재하는 툴 메뉴인지 확인
            if "(이미 존재)" in anchor_name:
                # 이미 존재하는 툴 메뉴는 추가 버튼 비활성화
                self.add_button.configure(state=tk.DISABLED)
                # 선택 해제
                self.anchor_listbox.selection_clear(0, tk.END)
                return
            else:
                # 사용 가능한 툴 메뉴는 추가 버튼 활성화
                self.add_button.configure(state=tk.NORMAL)
            
            # 사용 가능한 툴 메뉴면 ID 필드에 입력
            self.tool_menu_id_entry.delete(0, tk.END)
            self.tool_menu_id_entry.insert(0, anchor_name)
            
            # 중앙화된 툴 메뉴 목록에서 해당하는 표시명 찾기
            display_name = None
            for tool_menu_id, category_name in ALL_TOOL_MENUS:
                if tool_menu_id == anchor_name:
                    display_name = category_name
                    break
            
            # 표시명을 찾았으면 사용하고, 못 찾았으면 ID의 마지막 부분 사용
            if display_name:
                self.category_name_entry.delete(0, tk.END)
                self.category_name_entry.insert(0, display_name)
            else:
                # 백업: ID의 마지막 부분만 사용
                fallback_name = anchor_name.split('.')[-1]
                self.category_name_entry.delete(0, tk.END)
                self.category_name_entry.insert(0, fallback_name)
            
            # 입력 필드 변경 후 검증
            self._validate_input()

    def _validate_input(self, event=None):
        """입력 필드 내용을 검증하고 추가 버튼 상태를 업데이트합니다."""
        tool_menu_id = self.tool_menu_id_entry.get().strip()
        category_name = self.category_name_entry.get().strip()
        
        # 입력값이 있고, 기존 툴 메뉴와 중복되지 않는 경우 버튼 활성화
        if tool_menu_id and category_name and not self._is_existing_category(tool_menu_id, category_name):
            self.add_button.config(state=tk.NORMAL)
        else:
            self.add_button.config(state=tk.DISABLED)

    def _is_existing_category(self, tool_menu_id, category_name):
        """툴 메뉴가 이미 존재하는지 확인합니다."""
        # config_data에서 툴 메뉴 ID 확인
        if tool_menu_id in self.config_data:
            return True
        
        # 툴 메뉴 이름 중복 확인 (필요시 추가 검증)
        for existing_id in self.config_data.keys():
            if existing_id == category_name:  # ID로 이름이 사용된 경우
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
        
        # HasSection 정보를 포함한 결과 반환 (모든 툴 메뉴에 적용)
        has_section = self.has_section_var.get()
        self.result = (tool_menu_id, category_name, False, has_section)  # (id, name, legacy_is_anchor, has_section)
        
        self.dialog.destroy()
    
    def cancel(self):
        """취소 버튼"""
        self.dialog.destroy()



class NewEntryDialog:
    """새 엔트리 추가 다이얼로그"""
    
    def __init__(self, parent, ta_tool, tool_menu_id=None):
        self.result = None
        self.ta_tool = ta_tool
        self.tool_menu_id = tool_menu_id
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("새 엔트리 추가")
        self.dialog.geometry("400x200")
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
        
        # 엔트리 타입 선택 (새로 추가)
        ttk.Label(main_frame, text="엔트리 타입:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_type_var = tk.StringVar(value="command")
        entry_type_combo = ttk.Combobox(main_frame, textvariable=self.entry_type_var, 
                                       values=["submenu", "command", "chameleonTools"], state="readonly")
        entry_type_combo.grid(row=row, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # 엔트리 타입 설명
        type_descriptions = {
            "submenu": "📁 서브메뉴 - 하위 엔트리들을 그룹화",
            "command": "⚡ Python 명령어 - Python 코드 실행", 
            "chameleonTools": "🎨 Chameleon Tools - UI 도구 실행"
        }
        
        self.type_desc_label = ttk.Label(main_frame, text=type_descriptions["command"], 
                                        foreground="gray", font=("Arial", 8))
        self.type_desc_label.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=(0, 5))
        
        def on_type_change(*args):
            selected_type = self.entry_type_var.get()
            self.type_desc_label.config(text=type_descriptions.get(selected_type, ""))
        
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
        self.name_entry.focus_set()
        
        # Enter/Escape 키 바인딩
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
            self.ta_tool._show_warning("경고", "이름을 입력해주세요.")
            return
        
        if not selected_category:
            self.ta_tool._show_warning("경고", "메뉴 타입을 선택해주세요.")
            return
        
        if not entry_type:
            self.ta_tool._show_warning("경고", "엔트리 타입을 선택해주세요.")
            return
        
        # 엔트리 타입에 따라 다른 기본 구조 생성
        if entry_type == "submenu":
            # 서브메뉴: 이름, 툴팁, 아이콘, items
            new_entry = {
                "name": name,
                "items": []  # 서브메뉴는 하위 항목 배열 가짐
            }
        elif entry_type == "command":
            # 명령어: 이름, 툴팁, 활성화, 아이콘, command, canExecuteAction
            new_entry = {
                "name": name,
                "enabled": True,
                "command": ""
            }
        elif entry_type == "chameleonTools":
            # Chameleon: 이름, 툴팁, 활성화, 아이콘, ChameleonTools
            new_entry = {
                "name": name,
                "enabled": True,
                "ChameleonTools": ""
            }
        else:
            self.ta_tool._show_error("오류", f"알 수 없는 엔트리 타입: {entry_type}")
            return
        
        try:
            if parent_selection == "(루트)":
                # 툴 메뉴 데이터 확인/생성
                items = self.ta_tool._validate_config_data(selected_category)
                items.append(new_entry)
            else:
                # 선택된 부모에 추가
                parent_item_data = self.ta_tool._find_parent_by_name(selected_category, parent_selection)
                if parent_item_data:
                    if "items" not in parent_item_data:
                        parent_item_data["items"] = []
                    parent_item_data["items"].append(new_entry)
                else:
                    self.ta_tool._show_error("오류", f"부모 엔트리 '{parent_selection}'를 찾을 수 없습니다.")
                    return
            
            # 해당 탭 새로고침
            self.ta_tool.refresh_tab(selected_category)
            self.ta_tool.mark_as_modified()  # 변경사항 추적
            
            # 타입별 메시지
            type_names = {
                "submenu": "서브메뉴",
                "command": "명령어 엔트리", 
                "chameleonTools": "Chameleon 엔트리"
            }
            type_name = type_names.get(entry_type, "엔트리")
            
            # 점(.)이 포함된 언리얼 엔진 메뉴인 경우 새로고침 안내
            if "." in selected_category:
                self.ta_tool.update_status(f"➕ {type_name} '{name}' 추가됨 - 'TAPython.RefreshToolMenus' 실행 필요")
            else:
                self.ta_tool.update_status(f"➕ {type_name} '{name}' 추가됨")
            
            self.result = new_entry
            self.dialog.destroy()
            
        except Exception as e:
            error_msg = f"엔트리 추가 중 오류 발생: {str(e)}"
            self.ta_tool._show_error("오류", error_msg)
            self.ta_tool.update_status(f"엔트리 추가 실패: {str(e)}", auto_clear=False)
    
    def cancel(self):
        """취소"""
        self.result = None
        self.dialog.destroy()


if __name__ == "__main__":
    main()