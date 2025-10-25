#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants Module
애플리케이션에서 사용되는 상수들을 정의
"""

from typing import List, Tuple

# 모든 툴 메뉴 정의 (한 곳에서 관리)
ALL_TOOL_MENUS: List[Tuple[str, str]] = [
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

# 애플리케이션 설정
APP_TITLE = "🐍 TA Python Tool"
APP_GEOMETRY = "1000x700"

# 기본 설정
DEFAULT_CONFIG_STRUCTURE = {
    "menu_items": [
        {
            "type": "button",
            "label": "선택된 에셋 정보 출력",
            "tooltip": "현재 선택된 에셋들의 정보를 출력합니다",
            "command": "import unreal\nselected = unreal.EditorUtilityLibrary.get_selected_assets()\nfor asset in selected:\n    print(f'Asset: {asset.get_name()}, Class: {asset.get_class().get_name()}')"
        }
    ]
}

# 로깅 설정
LOG_FILE_NAME = "ta_python_tool.log"
LOG_LEVEL_CONSOLE = "WARNING"
LOG_LEVEL_FILE = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# UI 설정
UI_FONT_MAIN = ("맑은 고딕", 9)
UI_FONT_TITLE = ("Arial", 12, "bold")
UI_FONT_SMALL = ("Arial", 8)
UI_FONT_CODE = ("Consolas", 9)

# 파일 및 경로 설정
DEFAULT_FILE_NAME = "MenuConfig.json"
FILE_TYPES = [("JSON files", "*.json"), ("All files", "*.*")]

# 메뉴 타입별 설정
ENTRY_TYPES = {
    "submenu": {
        "display_name": "📁 서브메뉴",
        "description": "하위 엔트리들을 그룹화합니다",
        "icon": "📁"
    },
    "command": {
        "display_name": "⚡ Python 명령어",
        "description": "Python 코드를 실행합니다", 
        "icon": "⚡"
    },
    "chameleonTools": {
        "display_name": "🎨 Chameleon Tools",
        "description": "UI 도구를 실행합니다",
        "icon": "🎨"
    }
}

# 아이콘 타입
ICON_TYPES = ["없음", "EditorStyle", "ChameleonStyle", "ImagePath"]

# 웹 링크
TAPYTHON_WEBSITE = "https://www.tacolor.xyz/"
TAPYTHON_GITHUB = "https://github.com/cgerchenhp/UE_TAPython_Plugin_Release/releases"
UNREAL_ICONS_REFERENCE = "https://github.com/EpicKiwi/unreal-engine-editor-icons"