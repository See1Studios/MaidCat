#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Menu Editor

좌: Menu Anchor 트리뷰
중: 선택된 Anchor의 항목 트리뷰
우: 선택된 항목 상세 정보
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import unreal
import ui.helper

# Widget aka names — Status
AKA_STATUS = unreal.Name("StatusText")
AKA_FILE_PATH = unreal.Name("FilePathText")
AKA_DIRTY_INDICATOR = unreal.Name("DirtyIndicator")
AKA_LOCALE_COMBO = unreal.Name("LocaleCombo")
AKA_BTN_MENU_EDIT_TOGGLE_TEXT = unreal.Name("BtnMenuEditToggleText")
AKA_BTN_MENU_REFRESH_TEXT = unreal.Name("BtnMenuRefreshText")

# Widget aka names — Lists
AKA_LIST_ANCHORS = unreal.Name("ListMenuAnchors")
AKA_LIST_ENTRIES = unreal.Name("ListMenuEntries")
AKA_ENTRY_TREE_BORDER = unreal.Name("EntryTreeBorder")

# Widget aka names — Detail Panel (common)
AKA_DETAIL_PANEL = unreal.Name("DetailPanel")
AKA_DETAIL_EMPTY = unreal.Name("DetailEmptyText")
AKA_DETAIL = unreal.Name("DetailText")

# Widget aka names — Detail Panel (inputs)
AKA_DETAIL_TYPE_TEXT = unreal.Name("DetailTypeText")
AKA_DETAIL_NAME = unreal.Name("DetailNameInput")
AKA_DETAIL_TOOLTIP = unreal.Name("DetailTooltipInput")
AKA_DETAIL_COMMAND = unreal.Name("DetailCommandInput")
AKA_DETAIL_CAN_EXECUTE_ACTION = unreal.Name("DetailCanExecuteActionInput")
AKA_DETAIL_CHAMELEON_INPUT = unreal.Name("DetailChameleonInput")
AKA_DETAIL_ENABLED = unreal.Name("DetailEnabledCheck")
AKA_DETAIL_ICON_TYPE = unreal.Name("DetailIconTypeCombo")
AKA_DETAIL_ICON_NAME = unreal.Name("DetailIconNameInput")
AKA_DETAIL_ICON_PREVIEW_ROW = unreal.Name("DetailIconPreviewRow")
AKA_DETAIL_ICON_PREVIEW_HOST = unreal.Name("DetailIconPreviewHost")
AKA_DETAIL_ICON_PREVIEW_TEXT = unreal.Name("DetailIconPreviewText")
AKA_DETAIL_ICON_EXPANDABLE = unreal.Name("DetailIconExpandable")
AKA_DETAIL_DEBUG_EXPANDABLE = unreal.Name("DetailDebugExpandable")

# Widget aka names — Detail Panel (rows/labels)
AKA_DETAIL_TYPE_ROW = unreal.Name("DetailTypeRow")
AKA_DETAIL_NAME_ROW = unreal.Name("DetailNameRow")
AKA_DETAIL_TOOLTIP_ROW = unreal.Name("DetailTooltipRow")
AKA_DETAIL_ICON_ROW = unreal.Name("DetailIconRow")
AKA_DETAIL_COMMAND_LABEL = unreal.Name("DetailCommandLabel")
AKA_DETAIL_CAN_EXECUTE_ACTION_LABEL = unreal.Name("DetailCanExecuteActionLabel")
AKA_DETAIL_CHAMELEON_ROW = unreal.Name("DetailChameleonRow")
AKA_DETAIL_BUTTONS_ROW = unreal.Name("DetailButtonsRow")

# Widget aka names — Anchor Detail
AKA_ANCHOR_DETAIL_ROW = unreal.Name("AnchorDetailRow")
AKA_ANCHOR_ID_INPUT = unreal.Name("AnchorIdInput")
AKA_ANCHOR_DISPLAY_NAME_INPUT = unreal.Name("AnchorDisplayNameInput")
AKA_ANCHOR_TOOLTIP_INPUT = unreal.Name("AnchorTooltipInput")
AKA_ANCHOR_IS_READONLY_CHECK = unreal.Name("AnchorIsReadOnlyCheck")
AKA_BTN_ANCHOR_APPLY = unreal.Name("BtnAnchorApply")
AKA_BTN_ANCHOR_REVERT = unreal.Name("BtnAnchorRevert")
AKA_ANCHOR_READONLY_NOTICE = unreal.Name("LblAnchorReadOnlyNotice")

# Paths
TAPYTHON_MENUCONFIG_PATH = ["TA", "TAPython", "UI", "MenuConfig.json"]
LOCALE_SETTINGS_REL_PATH = ["Saved", "MaidCat", "tapython_menu_editor_settings.json"]

# Common engine anchor presets shown in add-anchor popup.
ANCHOR_PRESET_IDS = [
    # TAPython anchors
    "OnSelectFolderMenu",
    "OnSelectAssetsMenu",
    "OnMainMenu",
    "OnToolbar",
    "OnToolBarChameleon",
    "OnOutlineMenu",
    "OnMaterialEditorMenu",
    "OnPhysicsAssetEditorMenu",
    "OnControlRigEditorMenu",
    "OnTabContextMenu",
    # Unreal ToolMenu anchors
    "AssetEditor.AnimationBlueprintEditor.MainMenu",
    "AssetEditor.AnimationEditor.MainMenu",
    "AssetEditor.SkeletalMeshEditor.ToolBar",
    "AssetEditor.StaticMeshEditor.ToolBar",
    "ContentBrowser.AddNewContextMenu",
    "ContentBrowser.AssetContextMenu",
    "ContentBrowser.AssetContextMenu.AimOffsetBlendSpace",
    "ContentBrowser.AssetContextMenu.AnimBlueprint",
    "ContentBrowser.AssetContextMenu.AnimMontage",
    "ContentBrowser.AssetContextMenu.AnimSequence",
    "ContentBrowser.AssetContextMenu.BlendSpace",
    "ContentBrowser.AssetContextMenu.BlendSpace1D",
    "ContentBrowser.AssetContextMenu.CameraAnim",
    "ContentBrowser.AssetContextMenu.DatasmithScene",
    "ContentBrowser.AssetContextMenu.PoseAsset",
    "ContentBrowser.AssetContextMenu.SkeletalMesh",
    "ContentBrowser.AssetContextMenu.SkeletalMesh.CreateSkeletalMeshSubmenu",
    "ContentBrowser.AssetContextMenu.Skeleton.CreateSkeletalMeshSubmenu",
    "ContentBrowser.AssetContextMenu.SoundWave",
    "ContentBrowser.AssetContextMenu.StaticMesh",
    "ContentBrowser.AssetContextMenu.World",
    "ContentBrowser.AssetViewOptions",
    "ContentBrowser.AssetViewOptions.PathViewFilters",
    "ContentBrowser.DragDropContextMenu",
    "ContentBrowser.FolderContextMenu",
    "ContentBrowser.ItemContextMenu.PythonData",
    "ContentBrowser.ToolBar",
    "ControlRigEditor.RigHierarchy.ContextMenu",
    "ControlRigEditor.RigHierarchy.DragDropMenu",
    "Kismet.SubobjectEditorContextMenu",
    "Kismet.SCSEditorContextMenu",
    "LevelEditor.ActorContextMenu.AssetToolsSubMenu",
    "LevelEditor.ActorContextMenu.LevelSubMenu",
    "LevelEditor.InViewportPanel",
    "LevelEditor.LevelEditorSceneOutliner.ContextMenu.LevelSubMenu",
    "LevelEditor.LevelEditorToolBar",
    "LevelEditor.LevelEditorToolBar.AddQuickMenu",
    "LevelEditor.LevelEditorToolBar.User",
    "LevelEditor.LevelViewportToolBar.Options",
    "LevelEditor.LevelViewportToolBar.View",
    "LevelEditor.MainMenu.Build",
    "LevelEditor.MainMenu.File",
    "LevelEditor.MainMenu.Help",
    "LevelEditor.MainMenu.Select",
    "LevelEditor.MainMenu.Tools",
    "LevelEditor.MainMenu.Window",
    "LevelEditor.StatusBar.ToolBar",
    "MainFrame.MainMenu.Asset",
    "MainFrame.MainMenu.Tools",
    "MainFrame.MainMenu.Window",
    "StatusBar.ToolBar.SourceControl",
]

# Built-in Chameleon anchors should be view-only in detail panel.
CHAMELEON_BASE_ANCHOR_IDS = {
    "OnSelectFolderMenu",
    "OnSelectAssetsMenu",
    "OnMainMenu",
    "OnToolbar",
    "OnToolBarChameleon",
    "OnOutlineMenu",
    "OnMaterialEditorMenu",
    "OnPhysicsAssetEditorMenu",
    "OnControlRigEditorMenu",
    "OnTabContextMenu",
}

# Tool-only readonly anchor metadata (does not modify MenuConfig schema).
# Keys may include: displayName, tooltip
ANCHOR_INLINE_META: Dict[str, Dict[str, str]] = {
    "OnSelectFolderMenu": {"displayName": "폴더 컨텍스트 메뉴", "tooltip": "콘텐츠 브라우저 폴더 오른 클릭 시 표시되는 TAPython 기본 메뉴 앵커"},
    "OnSelectAssetsMenu": {"displayName": "애셋 컨텍스트 메뉴", "tooltip": "콘텐츠 브라우저 애셋 오른 클릭 시 표시되는 TAPython 기본 메뉴 앵커"},
    "OnMainMenu": {"displayName": "메인 메뉴 툴 메뉴", "tooltip": "TAPython 메인 메뉴 툴 영역 앵커"},
    "OnToolbar": {"displayName": "TAPython 기본툴바", "tooltip": "TAPython 기본 툴바 앵커"},
    "OnToolBarChameleon": {"displayName": "Chameleon 툴바", "tooltip": "Chameleon 도구에서 사용하는 TAPython 기본 툴바 앵커"},
    "OnOutlineMenu": {"displayName": "아웃라이너 컨텍스트 메뉴", "tooltip": "TAPython 기본 아웃라이너 컨텍스트 메뉴 앵커"},
    "OnMaterialEditorMenu": {"displayName": "머티리얼 에디터 툴 메뉴", "tooltip": "머티리얼 에디터에서 사용하는 TAPython 기본 메뉴 앵커"},
    "OnPhysicsAssetEditorMenu": {"displayName": "피직스 애셋 에디터 툴 메뉴", "tooltip": "피직스 애셋 에디터에서 사용하는 TAPython 기본 메뉴 앵커"},
    "OnControlRigEditorMenu": {"displayName": "컨트롤 릭 에디터 툴 메뉴", "tooltip": "컨트롤 릭 에디터에서 사용하는 TAPython 기본 메뉴 앵커"},
    "OnTabContextMenu": {"displayName": "카멜레온 툴 탭 컨텍스트 메뉴", "tooltip": "에디터 탭 우클릭 메뉴에 연결되는 TAPython 기본 앵커"},
    "AssetEditor.AnimationBlueprintEditor.MainMenu": {"displayName": "애니메이션 블루프린트 메인 메뉴", "tooltip": "애니메이션 블루프린트 에디터 상단 메인 메뉴"},
    "AssetEditor.AnimationEditor.MainMenu": {"displayName": "애니메이션 에디터 메인 메뉴", "tooltip": "애니메이션 에디터 상단 메인 메뉴"},
    "AssetEditor.SkeletalMeshEditor.ToolBar": {"displayName": "스켈레탈 메시 에디터 툴바", "tooltip": "스켈레탈 메시 에디터 툴바"},
    "AssetEditor.StaticMeshEditor.ToolBar": {"displayName": "스태틱 메시 에디터 툴바", "tooltip": "스태틱 메시 에디터 툴바"},
    "ContentBrowser.AddNewContextMenu": {"displayName": "콘텐츠 브라우저 새로 만들기 메뉴", "tooltip": "콘텐츠 브라우저의 Add New 메뉴"},
    "ContentBrowser.AssetContextMenu": {"displayName": "콘텐츠 브라우저 애셋 컨텍스트 메뉴", "tooltip": "콘텐츠 브라우저 공통 애셋 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.AimOffsetBlendSpace": {"displayName": "Aim Offset Blend Space 컨텍스트", "tooltip": "Aim Offset Blend Space 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.AnimBlueprint": {"displayName": "애니메이션 블루프린트 컨텍스트", "tooltip": "애니메이션 블루프린트 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.AnimMontage": {"displayName": "애니메이션 몽타주 컨텍스트", "tooltip": "애니메이션 몽타주 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.AnimSequence": {"displayName": "애니메이션 시퀀스 컨텍스트", "tooltip": "애니메이션 시퀀스 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.BlendSpace": {"displayName": "Blend Space 컨텍스트", "tooltip": "Blend Space 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.BlendSpace1D": {"displayName": "Blend Space 1D 컨텍스트", "tooltip": "Blend Space 1D 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.CameraAnim": {"displayName": "Camera Anim 컨텍스트", "tooltip": "Camera Anim 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.DatasmithScene": {"displayName": "Datasmith Scene 컨텍스트", "tooltip": "Datasmith Scene 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.PoseAsset": {"displayName": "Pose Asset 컨텍스트", "tooltip": "Pose Asset 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.SkeletalMesh": {"displayName": "Skeletal Mesh 컨텍스트", "tooltip": "스켈레탈 메시 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.SkeletalMesh.CreateSkeletalMeshSubmenu": {"displayName": "스켈레탈 메시 생성 서브메뉴", "tooltip": "스켈레탈 메시 관련 생성 서브메뉴"},
    "ContentBrowser.AssetContextMenu.Skeleton.CreateSkeletalMeshSubmenu": {"displayName": "스켈레톤 메시 생성 서브메뉴", "tooltip": "스켈레톤 애셋에서 스켈레탈 메시 생성 서브메뉴"},
    "ContentBrowser.AssetContextMenu.SoundWave": {"displayName": "사운드 웨이브 컨텍스트", "tooltip": "사운드 웨이브 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.StaticMesh": {"displayName": "스태틱 메시 컨텍스트", "tooltip": "스태틱 메시 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetContextMenu.World": {"displayName": "월드 애셋 컨텍스트", "tooltip": "월드 애셋 전용 우클릭 메뉴"},
    "ContentBrowser.AssetViewOptions": {"displayName": "애셋 뷰 옵션", "tooltip": "콘텐츠 브라우저 애셋 뷰 옵션 메뉴"},
    "ContentBrowser.AssetViewOptions.PathViewFilters": {"displayName": "경로 뷰 필터", "tooltip": "콘텐츠 브라우저 경로 뷰 필터 옵션"},
    "ContentBrowser.DragDropContextMenu": {"displayName": "드래그 앤 드롭 컨텍스트 메뉴", "tooltip": "콘텐츠 브라우저 드래그 앤 드롭 컨텍스트 메뉴"},
    "ContentBrowser.FolderContextMenu": {"displayName": "폴더 컨텍스트 메뉴", "tooltip": "콘텐츠 브라우저 폴더 우클릭 메뉴"},
    "ContentBrowser.ItemContextMenu.PythonData": {"displayName": "Python 데이터 컨텍스트", "tooltip": "PythonData 항목 전용 컨텍스트 메뉴"},
    "ContentBrowser.ToolBar": {"displayName": "콘텐츠 브라우저 툴바", "tooltip": "콘텐츠 브라우저 상단 툴바"},
    "ControlRigEditor.RigHierarchy.ContextMenu": {"displayName": "릭 계층 컨텍스트 메뉴", "tooltip": "컨트롤 릭 Rig Hierarchy 우클릭 메뉴"},
    "ControlRigEditor.RigHierarchy.DragDropMenu": {"displayName": "릭 계층 드래그 앤 드롭 메뉴", "tooltip": "컨트롤 릭 Rig Hierarchy 드래그 앤 드롭 메뉴"},
    "Kismet.SubobjectEditorContextMenu": {"displayName": "블루프린트 서브오브젝트 컨텍스트 메뉴", "tooltip": "블루프린트 서브오브젝트 에디터 우클릭 메뉴"},
    "Kismet.SCSEditorContextMenu": {"displayName": "블루프린트 컴포넌트 컨텍스트 메뉴", "tooltip": "블루프린트 컴포넌트 트리 우클릭 메뉴"},
    "LevelEditor.ActorContextMenu.AssetToolsSubMenu": {"displayName": "액터 애셋 도구 서브메뉴", "tooltip": "레벨 에디터 액터 컨텍스트 메뉴의 Asset Tools 서브메뉴"},
    "LevelEditor.ActorContextMenu.LevelSubMenu": {"displayName": "액터 레벨 서브메뉴", "tooltip": "레벨 에디터 액터 컨텍스트 메뉴의 Level 서브메뉴"},
    "LevelEditor.InViewportPanel": {"displayName": "뷰포트 내부 패널", "tooltip": "레벨 에디터 뷰포트 내부 패널 영역"},
    "LevelEditor.LevelEditorSceneOutliner.ContextMenu.LevelSubMenu": {"displayName": "씬 아웃라이너 레벨 서브메뉴", "tooltip": "씬 아웃라이너 컨텍스트 메뉴의 Level 서브메뉴"},
    "LevelEditor.LevelEditorToolBar": {"displayName": "레벨 에디터 툴바", "tooltip": "레벨 에디터 메인 툴바"},
    "LevelEditor.LevelEditorToolBar.AddQuickMenu": {"displayName": "빠른 실행 메뉴 추가", "tooltip": "레벨 에디터 툴바의 Add 빠른 실행 메뉴"},
    "LevelEditor.LevelEditorToolBar.User": {"displayName": "사용자 툴바 메뉴", "tooltip": "레벨 에디터 툴바의 사용자 메뉴 영역"},
    "LevelEditor.LevelViewportToolBar.Options": {"displayName": "뷰포트 옵션 툴바", "tooltip": "레벨 뷰포트 툴바의 옵션 메뉴"},
    "LevelEditor.LevelViewportToolBar.View": {"displayName": "뷰포트 뷰 툴바", "tooltip": "레벨 뷰포트 툴바의 뷰 메뉴"},
    "LevelEditor.MainMenu.Build": {"displayName": "빌드 메뉴", "tooltip": "레벨 에디터 상단 빌드 메뉴"},
    "LevelEditor.MainMenu.File": {"displayName": "파일 메뉴", "tooltip": "레벨 에디터 상단 파일 메뉴"},
    "LevelEditor.MainMenu.Help": {"displayName": "도움말 메뉴", "tooltip": "레벨 에디터 상단 도움말 메뉴"},
    "LevelEditor.MainMenu.Select": {"displayName": "선택 메뉴", "tooltip": "레벨 에디터 상단 선택 메뉴"},
    "LevelEditor.MainMenu.Tools": {"displayName": "도구 메뉴", "tooltip": "레벨 에디터 상단 도구 메뉴"},
    "LevelEditor.MainMenu.Window": {"displayName": "창 메뉴", "tooltip": "레벨 에디터 상단 창 메뉴"},
    "LevelEditor.StatusBar.ToolBar": {"displayName": "레벨 에디터 상태바", "tooltip": "레벨 에디터 하단 상태바 툴바"},
    "MainFrame.MainMenu.Asset": {"displayName": "메인 프레임 애셋 메뉴", "tooltip": "에디터 메인 프레임 상단 애셋 메뉴"},
    "MainFrame.MainMenu.Tools": {"displayName": "메인 프레임 도구 메뉴", "tooltip": "에디터 메인 프레임 상단 도구 메뉴"},
    "MainFrame.MainMenu.Window": {"displayName": "메인 프레임 창 메뉴", "tooltip": "에디터 메인 프레임 상단 창 메뉴"},
    "StatusBar.ToolBar.SourceControl": {"displayName": "소스 컨트롤 툴바", "tooltip": "상태바의 소스 컨트롤 툴바 영역"},
}

ANCHOR_META_EMPTY_DISPLAY_NAME = "등록된 표시 이름이 없습니다"
ANCHOR_META_EMPTY_TOOLTIP = "이 앵커 ID에 대한 설명이 아직 등록되지 않았습니다"

# Localization
DEFAULT_LOCALE = "ko"
TEXTS: Dict[str, Dict[str, str]] = {
    "ko": {
        "ui.file_label": "파일:",
        "ui.file_path_placeholder": "(파일 선택 필요)",
        "ui.file_path_missing": "(MenuConfig.json 없음)",
        "ui.language": "언어",
        "ui.save": "저장",
        "ui.menu_edit_toggle_on": "메뉴편집 ON",
        "ui.menu_edit_toggle_off": "메뉴편집 OFF",
        "ui.menu_refresh": "메뉴 새로고침",
        "ui.dirty_indicator": "● 저장되지 않은 변경 사항이 있습니다.",
        "ui.menu_anchors": "메뉴 앵커",
        "ui.add": "추가",
        "ui.delete": "삭제",
        "ui.entry_tree": "항목 트리",
        "ui.copy": "복사",
        "ui.move_up": "위로",
        "ui.paste": "붙여넣기",
        "ui.move_down": "아래로",
        "ui.detail": "상세 정보",
        "ui.select_item": "항목을 선택하세요.",
        "ui.id": "ID",
        "ui.display_name": "표시 이름",
        "ui.anchor_tooltip": "Tooltip",
        "ui.is_readonly": "IsReadOnly",
        "ui.anchor_readonly_notice": "빌트인 Chameleon 앵커는 참고용으로만 표시되며 이 화면에서 수정할 수 없습니다.",
        "ui.apply": "적용",
        "ui.revert": "되돌리기",
        "ui.cancel": "취소",
        "ui.type": "Type",
        "ui.name": "Name",
        "ui.tooltip": "Tooltip",
        "ui.icon": "Icon",
        "ui.icon_section": "아이콘",
        "ui.preview": "미리보기",
        "ui.icon_preview": "아이콘 미리보기",
        "ui.enabled": "Enabled",
        "ui.command": "Command",
        "ui.can_execute_action": "CanExecuteAction",
        "ui.chameleon_tools": "ChameleonTools",
        "ui.debug_section": "디버그 JSON",
        "ui.initializing": "초기화 중...",
        "entry_type.command": "⚡ 명령어",
        "entry_type.submenu": "📁 서브메뉴",
        "entry_type.chameleon": "🎨 카멜레온",
        "entry_type.unknown": "📄 {entry_type}",
        "status.disabled_no_menuconfig": "MenuConfig.json을 찾지 못해 툴이 비활성화되었습니다.",
        "status.file_not_found": "파일이 없습니다: {path}",
        "status.load_complete": "로드 완료: {name} (앵커 {count}개)",
        "status.json_parse_error": "JSON 파싱 오류: {error}",
        "status.file_load_failed": "파일 로드 실패: {error}",
        "status.save_complete": "저장 완료: {name}",
        "status.save_failed": "저장 실패: {error}",
        "status.menuconfig_not_found": "MenuConfig.json 경로를 찾지 못했습니다",
        "status.select_entry_first": "먼저 가운데 트리에서 항목을 선택하세요",
        "status.selected_entry_not_found": "선택한 항목을 찾지 못했습니다",
        "status.detail_applied": "디테일 변경 적용 완료",
        "status.anchor_selected": "앵커 선택: {anchor}",
        "status.anchor_exists": "앵커 '{anchor}'가 이미 존재합니다",
        "status.anchor_added": "앵커 추가: {anchor}",
        "status.anchor_deleted": "앵커 삭제: {anchor}",
        "status.select_anchor_first": "먼저 왼쪽에서 메뉴 앵커를 선택하세요",
        "status.anchor_delete_canceled": "앵커 삭제 취소됨",
        "status.anchor_id_required": "앵커 ID를 입력하세요",
        "status.anchor_apply": "앵커 적용: {anchor}",
        "status.anchor_updated": "앵커 업데이트: {anchor}",
        "status.anchor_readonly_base": "기본 카멜레온 앵커는 수정할 수 없습니다: {anchor}",
        "status.anchor_detail_reloaded": "앵커 메타데이터를 다시 표시했습니다",
        "status.item_added": "항목 추가 ({item_type}): {anchor}",
        "status.select_entry_to_delete": "가운데에서 삭제할 항목을 선택하세요",
        "status.entry_delete_failed": "항목 삭제 실패",
        "status.entry_deleted": "항목 삭제 완료",
        "status.select_entry": "항목을 선택하세요",
        "status.entry_moved_up": "항목을 위로 이동했습니다",
        "status.entry_at_top": "맨 위에 있는 항목입니다",
        "status.entry_moved_down": "항목을 아래로 이동했습니다",
        "status.entry_at_bottom": "맨 아래에 있는 항목입니다",
        "status.entry_copied": "항목을 복사했습니다",
        "status.no_clipboard_entry": "복사된 항목이 없습니다",
        "status.entry_pasted": "항목을 붙여넣었습니다",
        "status.disabled_missing_menuconfig": "MenuConfig.json이 없어 비활성화 상태입니다.",
        "status.editorstyle_preview_guide": "EditorStyle 아이콘은 외부 목록에서 확인해 사용하세요",
        "status.corestyle_preview_guide": "CoreStyle 아이콘은 외부 목록에서 확인해 사용하세요",
        "status.locale_changed": "언어 변경: {locale_code}",
        "status.menu_edit_enabled": "메뉴 편집 활성화됨 (ToolMenus.Edit 1)",
        "status.menu_edit_disabled": "메뉴 편집 비활성화됨 (ToolMenus.Edit 0)",
        "status.menu_refreshed": "툴 메뉴 새로고침 실행됨 (TAPython.RefreshToolMenus)",
        "status.console_command_failed": "콘솔 명령 실행 실패: {command}",
        "preview.none": "아이콘 미리보기",
        "preview.imagepath_failed": "ImagePath 미리보기 실패",
        "preview.editorstyle_disabled": "EditorStyle 프리뷰 비활성화",
        "preview.corestyle_disabled": "CoreStyle 프리뷰 비활성화",
        "preview.chameleon_unsupported": "ChameleonStyle 미리보기는 현재 미지원",
        "dialog.add_anchor_message": "추가할 메뉴 앵커 ID를 입력하세요.\n예) LevelEditor.MainMenu.MyTools",
        "dialog.add_anchor_title": "앵커 추가",
        "dialog.add_anchor_pick_message": "추가할 메뉴 앵커를 선택하세요.",
        "dialog.add_anchor_pick_label": "앵커 :",
        "dialog.add_anchor_manual_input": "직접 입력...",
        "dialog.delete_anchor_title": "앵커 삭제 확인",
        "dialog.delete_anchor_message": "'{anchor_id}' 를 삭제합니다.\n({item_count}개 항목 포함)\n\n계속하시겠습니까?",
        "dialog.add_type_message": "추가할 항목 타입을 선택하세요.",
        "dialog.type_label": "타입 :",
    },
    "en": {
        "ui.file_label": "File:",
        "ui.file_path_placeholder": "(Select a file)",
        "ui.file_path_missing": "(MenuConfig.json missing)",
        "ui.language": "Language",
        "ui.save": "Save",
        "ui.menu_edit_toggle_on": "Menu Edit ON",
        "ui.menu_edit_toggle_off": "Menu Edit OFF",
        "ui.menu_refresh": "Refresh Menus",
        "ui.dirty_indicator": "● You have unsaved changes.",
        "ui.menu_anchors": "Menu Anchors",
        "ui.add": "Add",
        "ui.delete": "Delete",
        "ui.entry_tree": "Entry Tree",
        "ui.copy": "Copy",
        "ui.move_up": "Up",
        "ui.paste": "Paste",
        "ui.move_down": "Down",
        "ui.detail": "Details",
        "ui.select_item": "Select an item.",
        "ui.id": "ID",
        "ui.display_name": "Display Name",
        "ui.anchor_tooltip": "Tooltip",
        "ui.is_readonly": "IsReadOnly",
        "ui.anchor_readonly_notice": "Built-in Chameleon anchors are shown for reference only and cannot be edited here.",
        "ui.apply": "Apply",
        "ui.revert": "Revert",
        "ui.cancel": "Cancel",
        "ui.type": "Type",
        "ui.name": "Name",
        "ui.tooltip": "Tooltip",
        "ui.icon": "Icon",
        "ui.icon_section": "Icon",
        "ui.preview": "Preview",
        "ui.icon_preview": "Icon preview",
        "ui.enabled": "Enabled",
        "ui.command": "Command",
        "ui.can_execute_action": "CanExecuteAction",
        "ui.chameleon_tools": "ChameleonTools",
        "ui.debug_section": "Debug JSON",
        "ui.initializing": "Initializing...",
        "entry_type.command": "⚡ Command",
        "entry_type.submenu": "📁 Submenu",
        "entry_type.chameleon": "🎨 Chameleon",
        "entry_type.unknown": "📄 {entry_type}",
        "status.disabled_no_menuconfig": "Tool is disabled because MenuConfig.json could not be found.",
        "status.file_not_found": "File not found: {path}",
        "status.load_complete": "Load complete: {name} (anchors: {count})",
        "status.json_parse_error": "JSON parse error: {error}",
        "status.file_load_failed": "Failed to load file: {error}",
        "status.save_complete": "Saved: {name}",
        "status.save_failed": "Failed to save: {error}",
        "status.menuconfig_not_found": "Could not resolve MenuConfig.json path",
        "status.select_entry_first": "Select an entry in the middle tree first",
        "status.selected_entry_not_found": "Could not find the selected entry",
        "status.detail_applied": "Detail changes applied",
        "status.anchor_selected": "Anchor selected: {anchor}",
        "status.anchor_exists": "Anchor '{anchor}' already exists",
        "status.anchor_added": "Anchor added: {anchor}",
        "status.anchor_deleted": "Anchor deleted: {anchor}",
        "status.select_anchor_first": "Select a menu anchor on the left first",
        "status.anchor_delete_canceled": "Anchor deletion canceled",
        "status.anchor_id_required": "Enter an anchor ID",
        "status.anchor_apply": "Anchor applied: {anchor}",
        "status.anchor_updated": "Anchor updated: {anchor}",
        "status.anchor_readonly_base": "Built-in Chameleon anchor cannot be edited: {anchor}",
        "status.anchor_detail_reloaded": "Anchor metadata refreshed",
        "status.item_added": "Item added ({item_type}): {anchor}",
        "status.select_entry_to_delete": "Select an entry to delete from the middle list",
        "status.entry_delete_failed": "Failed to delete entry",
        "status.entry_deleted": "Entry deleted",
        "status.select_entry": "Select an entry",
        "status.entry_moved_up": "Moved entry up",
        "status.entry_at_top": "Entry is already at the top",
        "status.entry_moved_down": "Moved entry down",
        "status.entry_at_bottom": "Entry is already at the bottom",
        "status.entry_copied": "Entry copied",
        "status.no_clipboard_entry": "No copied entry",
        "status.entry_pasted": "Entry pasted",
        "status.disabled_missing_menuconfig": "Tool is disabled because MenuConfig.json is missing.",
        "status.editorstyle_preview_guide": "Use an external list to choose EditorStyle icons",
        "status.corestyle_preview_guide": "Use an external list to choose CoreStyle icons",
        "status.locale_changed": "Language changed: {locale_code}",
        "status.menu_edit_enabled": "Menu editing enabled (ToolMenus.Edit 1)",
        "status.menu_edit_disabled": "Menu editing disabled (ToolMenus.Edit 0)",
        "status.menu_refreshed": "Menu refresh executed (TAPython.RefreshToolMenus)",
        "status.console_command_failed": "Failed to execute console command: {command}",
        "preview.none": "Icon preview",
        "preview.imagepath_failed": "ImagePath preview failed",
        "preview.editorstyle_disabled": "EditorStyle preview is disabled",
        "preview.corestyle_disabled": "CoreStyle preview is disabled",
        "preview.chameleon_unsupported": "ChameleonStyle preview is not supported yet",
        "dialog.add_anchor_message": "Enter a menu anchor ID to add.\nExample) LevelEditor.MainMenu.MyTools",
        "dialog.add_anchor_title": "Add Anchor",
        "dialog.add_anchor_pick_message": "Select a menu anchor to add.",
        "dialog.add_anchor_pick_label": "Anchor :",
        "dialog.add_anchor_manual_input": "Manual input...",
        "dialog.delete_anchor_title": "Confirm Anchor Deletion",
        "dialog.delete_anchor_message": "Delete '{anchor_id}'.\n(Includes {item_count} entries)\n\nContinue?",
        "dialog.add_type_message": "Select the item type to add.",
        "dialog.type_label": "Type :",
    },
}


def tr(key: str, locale: str = DEFAULT_LOCALE, **kwargs: object) -> str:
    lang = TEXTS.get(locale, TEXTS[DEFAULT_LOCALE])
    fallback = TEXTS[DEFAULT_LOCALE]
    template = lang.get(key, fallback.get(key, key))
    try:
        return template.format(**kwargs)
    except Exception:
        return template

# Entry types
class EntryType:
    COMMAND = "command"
    SUBMENU = "submenu"
    CHAMELEON = "chameleon"


# 타입별 필드 설정
class EntryTypeConfig:
    """Each entry type's visible fields and input widget aka names."""
    CONFIGS = {
        EntryType.COMMAND: {
            "label": "Command",
            "input_aka_name": "DetailCommandInput",
            "input_json_key": "command",
        },
        EntryType.CHAMELEON: {
            "label": "ChameleonTools",
            "input_aka_name": "DetailChameleonInput",
            "input_json_key": "ChameleonTools",
        },
        EntryType.SUBMENU: {
            "label": "(No input)",
            "input_aka_name": None,
            "input_json_key": None,
        },
    }

    @classmethod
    def get_config(cls, entry_type: str) -> Dict[str, Any]:
        return cls.CONFIGS.get(entry_type, cls.CONFIGS[EntryType.COMMAND])


ENTRY_TYPE_LABEL_KEYS: Dict[str, str] = {
    EntryType.COMMAND: "entry_type.command",
    EntryType.SUBMENU: "entry_type.submenu",
    EntryType.CHAMELEON: "entry_type.chameleon",
}

# 타입
PathTuple = Tuple[int, ...]


class TAPythonMenuEditor:
    ICON_TYPES = ["없음", "EditorStyle", "CoreStyle", "ChameleonStyle", "ImagePath"]

    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        self.data: unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(json_path)
        self._locale = DEFAULT_LOCALE
        self._locale_options = sorted(TEXTS.keys())

        self._config_data: Dict[str, Any] = {}
        self._file_path: str = ""
        self._is_dirty: bool = False
        self._tool_enabled: bool = False
        self._menu_edit_enabled: bool = False

        self._anchor_names: List[str] = []
        self._anchor_selection: set[int] = set()
        self._entry_selection: set[int] = set()

        self._active_anchor: Optional[str] = None
        self._selected_entry_path: Optional[PathTuple] = None

        # 중간 패널용 플랫 노드
        # [{"path": (0,1), "depth": 1, "item": {...}}, ...]
        self._entry_nodes: List[Dict[str, Any]] = []

        # 복사 버퍼
        self._clipboard_entry: Optional[Dict[str, Any]] = None

    # ──────────────────────────────────────────────────────────────────────────
    # lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def init(self) -> None:
        self._load_locale_setting()
        self._init_locale_combo()
        self._apply_localized_gui_texts()
        self._init_icon_type_combo()
        default_path = self._find_default_config()
        if default_path:
            self._load_config_file(default_path)
            self._tool_enabled = True
        else:
            self._tool_enabled = False
            self._file_path = ""
            self._config_data = {}
            self._anchor_names = []
            self._entry_nodes = []
            self._selected_entry_path = None
            self._update_file_path_display(self._tr("ui.file_path_missing"))
            self._clear_detail_form()
            self._set_detail_panel_enabled(False)
            self._set_detail_editor_visible(False)
            self._refresh_all_views()
            self._update_status(self._tr("status.disabled_no_menuconfig"))

    def _tr(self, key: str, **kwargs: object) -> str:
        return tr(key, self._locale, **kwargs)

    def _apply_localized_gui_texts(self) -> None:
        mapping = {
            "LblFile": "ui.file_label",
            "BtnSaveText": "ui.save",
            "BtnMenuRefreshText": "ui.menu_refresh",
            "DirtyIndicator": "ui.dirty_indicator",
            "LblLocale": "ui.language",
            "LblMenuAnchors": "ui.menu_anchors",
            "BtnAddAnchorText": "ui.add",
            "BtnDeleteAnchorText": "ui.delete",
            "LblEntryTree": "ui.entry_tree",
            "BtnAddText": "ui.add",
            "BtnCopyText": "ui.copy",
            "BtnMoveUpText": "ui.move_up",
            "BtnDeleteText": "ui.delete",
            "BtnPasteText": "ui.paste",
            "BtnMoveDownText": "ui.move_down",
            "LblDetailTitle": "ui.detail",
            "DetailEmptyText": "ui.select_item",
            "LblAnchorId": "ui.id",
            "LblAnchorDisplayName": "ui.display_name",
            "LblAnchorTooltip": "ui.anchor_tooltip",
            "LblAnchorIsReadOnly": "ui.is_readonly",
            "LblAnchorReadOnlyNotice": "ui.anchor_readonly_notice",
            "LblType": "ui.type",
            "LblName": "ui.name",
            "LblTooltip": "ui.tooltip",
            "LblIcon": "ui.icon",
            "LblIconSection": "ui.icon_section",
            "BtnPreviewIconText": "ui.preview",
            "DetailIconPreviewText": "ui.icon_preview",
            "LblEnabled": "ui.enabled",
            "DetailCommandLabel": "ui.command",
            "DetailCanExecuteActionLabel": "ui.can_execute_action",
            "LblChameleonTools": "ui.chameleon_tools",
            "LblDebugSection": "ui.debug_section",
            "BtnAnchorApplyText": "ui.apply",
            "BtnAnchorRevertText": "ui.revert",
            "BtnDetailApplyText": "ui.apply",
            "BtnDetailRevertText": "ui.revert",
            "StatusText": "ui.initializing",
        }
        for aka_name, key in mapping.items():
            try:
                self.data.set_text(unreal.Name(aka_name), self._tr(key))
            except Exception:
                pass

        # 파일 경로 라벨은 실제 상태를 반영해야 하므로 placeholder로 덮어쓰지 않는다.
        if self._file_path:
            self._update_file_path_display(self._file_path)
        elif not self._tool_enabled:
            self._update_file_path_display(self._tr("ui.file_path_missing"))
        else:
            self._update_file_path_display(self._tr("ui.file_path_placeholder"))

        self._refresh_menu_edit_toggle_text()

    def _refresh_menu_edit_toggle_text(self) -> None:
        key = "ui.menu_edit_toggle_on" if self._menu_edit_enabled else "ui.menu_edit_toggle_off"
        try:
            self.data.set_text(AKA_BTN_MENU_EDIT_TOGGLE_TEXT, self._tr(key))
        except Exception:
            pass

    def _init_locale_combo(self) -> None:
        try:
            self.data.set_combo_box_items(AKA_LOCALE_COMBO, self._locale_options)  # type: ignore[arg-type]
            idx = self._locale_options.index(self._locale) if self._locale in self._locale_options else 0
            self.data.set_combo_box_selected_item(AKA_LOCALE_COMBO, idx)  # type: ignore[arg-type]
        except Exception:
            pass

    def _get_locale_settings_path(self) -> Path:
        project_dir = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
        return project_dir.joinpath(*LOCALE_SETTINGS_REL_PATH)

    def _load_locale_setting(self) -> None:
        try:
            settings_path = self._get_locale_settings_path()
            if not settings_path.exists():
                return
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            locale = str(data.get("locale", "")).strip()
            if locale in TEXTS:
                self._locale = locale
        except Exception as e:
            unreal.log_warning(f"TAPythonMenuEditor: locale 설정 로드 실패 — {e}")

    def _save_locale_setting(self) -> None:
        try:
            settings_path = self._get_locale_settings_path()
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"locale": self._locale}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            unreal.log_warning(f"TAPythonMenuEditor: locale 설정 저장 실패 — {e}")

    def on_locale_changed(self, selected_locale: Any = None) -> None:
        locale = ""
        if isinstance(selected_locale, str):
            locale = selected_locale.strip()
        if not locale:
            locale = str(self.data.get_combo_box_selected_item(AKA_LOCALE_COMBO) or "").strip()

        if locale not in TEXTS:
            return
        if locale == self._locale:
            return

        self._locale = locale
        self._save_locale_setting()
        self._apply_localized_gui_texts()
        self._update_status(self._tr("status.locale_changed", locale_code=locale))

    def _init_icon_type_combo(self) -> None:
        try:
            self.data.set_combo_box_items(AKA_DETAIL_ICON_TYPE, self.ICON_TYPES)  # type: ignore[arg-type]
            self.data.set_combo_box_selected_item(AKA_DETAIL_ICON_TYPE, 0)  # type: ignore[arg-type]
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    # path / file io
    # ──────────────────────────────────────────────────────────────────────────

    def _find_default_config(self) -> Optional[str]:
        try:
            project_dir = Path(
                unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
            )
            menuconfig = project_dir.joinpath(*TAPYTHON_MENUCONFIG_PATH)
            if menuconfig.exists():
                unreal.log(f"TAPythonMenuEditor: MenuConfig 발견 — {menuconfig}")
                return str(menuconfig)
            unreal.log_warning(f"TAPythonMenuEditor: MenuConfig 없음 — {menuconfig}")
            return None
        except Exception as e:
            unreal.log_error(f"TAPythonMenuEditor: 경로 탐색 오류 — {e}")
            return None

    def _load_config_file(self, file_path: str) -> None:
        try:
            path = Path(file_path)
            if not path.exists():
                self._update_status(self._tr("status.file_not_found", path=file_path))
                return

            with open(path, "r", encoding="utf-8") as f:
                self._config_data = json.load(f)
            self._file_path = file_path
            self._set_dirty(False)

            self._rebuild_anchor_cache()
            self._update_file_path_display(file_path)
            self._refresh_all_views()
            self._update_status(
                self._tr("status.load_complete", name=path.name, count=len(self._anchor_names))
            )

        except json.JSONDecodeError as e:
            self._update_status(self._tr("status.json_parse_error", error=e))
            unreal.log_error(f"TAPythonMenuEditor: JSON 파싱 오류 — {e}")
        except Exception as e:
            self._update_status(self._tr("status.file_load_failed", error=e))
            unreal.log_error(f"TAPythonMenuEditor: 파일 로드 실패 — {e}")

    def save_file(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._file_path:
            self._update_status(self._tr("status.menuconfig_not_found"))
            return
        self._do_save_file(self._file_path)

    def _execute_console_command(self, command: str) -> bool:
        try:
            unreal.PythonBPLib.execute_console_command(command)
            return True
        except Exception as e:
            self._update_status(self._tr("status.console_command_failed", command=command))
            unreal.log_error(f"TAPythonMenuEditor: 콘솔 명령 실행 실패 — {command} / {e}")
            return False

    def enable_menu_edit(self) -> None:
        if self._execute_console_command("ToolMenus.Edit 1"):
            self._menu_edit_enabled = True
            self._refresh_menu_edit_toggle_text()
            self._update_status(self._tr("status.menu_edit_enabled"))

    def disable_menu_edit(self) -> None:
        if self._execute_console_command("ToolMenus.Edit 0"):
            self._menu_edit_enabled = False
            self._refresh_menu_edit_toggle_text()
            self._update_status(self._tr("status.menu_edit_disabled"))

    def toggle_menu_edit(self) -> None:
        if self._menu_edit_enabled:
            self.disable_menu_edit()
        else:
            self.enable_menu_edit()

    def refresh_tool_menus(self) -> None:
        if self._execute_console_command("TAPython.RefreshToolMenus"):
            self._update_status(self._tr("status.menu_refreshed"))

    def _do_save_file(self, file_path: str) -> None:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._config_data, f, indent=4, ensure_ascii=False)
            self._file_path = file_path
            self._set_dirty(False)
            self._update_file_path_display(file_path)
            self._update_status(self._tr("status.save_complete", name=path.name))
        except Exception as e:
            self._update_status(self._tr("status.save_failed", error=e))
            unreal.log_error(f"TAPythonMenuEditor: 저장 실패 — {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # data cache / flatten
    # ──────────────────────────────────────────────────────────────────────────

    def _rebuild_anchor_cache(self) -> None:
        self._anchor_names = []
        for key, val in self._config_data.items():
            if isinstance(val, dict) and isinstance(val.get("items"), list):
                self._anchor_names.append(key)

        if not self._anchor_names:
            self._active_anchor = None
            self._entry_nodes = []
            return

        if self._active_anchor not in self._anchor_names:
            self._active_anchor = self._anchor_names[0]

        self._rebuild_entry_nodes()

    def _rebuild_entry_nodes(self) -> None:
        self._entry_nodes = []
        if not self._active_anchor:
            return

        anchor_data = self._config_data.get(self._active_anchor, {})
        items = anchor_data.get("items", []) if isinstance(anchor_data, dict) else []
        self._append_nodes_recursive(items, parent_path=(), depth=0)

    def _append_nodes_recursive(
        self,
        items: List[Dict[str, Any]],
        parent_path: PathTuple,
        depth: int,
    ) -> None:
        for idx, item in enumerate(items):
            path = parent_path + (idx,)
            self._entry_nodes.append({"path": path, "depth": depth, "item": item})
            children = item.get("items", [])
            if isinstance(children, list) and children:
                self._append_nodes_recursive(children, parent_path=path, depth=depth + 1)

    def _get_items_of_active_anchor(self) -> List[Dict[str, Any]]:
        if not self._active_anchor:
            return []
        anchor_data = self._config_data.get(self._active_anchor)
        if not isinstance(anchor_data, dict):
            return []
        items = anchor_data.get("items")
        return items if isinstance(items, list) else []

    # ──────────────────────────────────────────────────────────────────────────
    # callbacks - left/middle/right
    # ──────────────────────────────────────────────────────────────────────────

    def on_anchor_selection_changed(self, index: Any = -1) -> None:
        if not self._ensure_enabled():
            return
        try:
            idx = int(index)
            if idx < 0:
                return
            if 0 <= idx < len(self._anchor_names):
                self._active_anchor = self._anchor_names[idx]
                self._entry_selection.clear()
                self._selected_entry_path = None
                self._rebuild_entry_nodes()
                self._refresh_entry_list()
                # 앵커만 선택된 상태: 앵커 디테일 패널 표시
                self._show_anchor_detail()
                self._update_status(self._tr("status.anchor_selected", anchor=self._active_anchor))
        except Exception as e:
            unreal.log_error(f"TAPythonMenuEditor: 앵커 선택 콜백 오류 — {e}")

    def on_entry_selection_changed(self, index: Any = -1) -> None:
        if not self._ensure_enabled():
            return
        try:
            self._sync_entry_selection_from_widget(fallback_index=index)
        except Exception as e:
            unreal.log_error(f"TAPythonMenuEditor: 항목 선택 콜백 오류 — {e}")

    def apply_detail_changes(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._selected_entry_path:
            self._update_status(self._tr("status.select_entry_first"))
            return

        item = self._get_item_by_path(self._selected_entry_path)
        if item is None:
            self._update_status(self._tr("status.selected_entry_not_found"))
            return

        name = (self.data.get_text(AKA_DETAIL_NAME) or "").strip()
        tooltip = (self.data.get_text(AKA_DETAIL_TOOLTIP) or "").strip()
        enabled = bool(self.data.get_is_checked(AKA_DETAIL_ENABLED))
        entry_type = self._get_entry_type(item)

        if name:
            item["name"] = name
        else:
            item.pop("name", None)

        if tooltip:
            item["tooltip"] = tooltip
        else:
            item.pop("tooltip", None)

        item["enabled"] = enabled

        self._apply_icon_data(item)

        if entry_type == EntryType.COMMAND:
            command = self.data.get_text(AKA_DETAIL_COMMAND) or ""
            if command.strip():
                item["command"] = command
            else:
                item.pop("command", None)

            can_execute_action = self.data.get_text(AKA_DETAIL_CAN_EXECUTE_ACTION) or ""
            if can_execute_action.strip():
                item["canExecuteAction"] = can_execute_action
            else:
                item.pop("canExecuteAction", None)
        elif entry_type == EntryType.CHAMELEON:
            chameleon_path = (self.data.get_text(AKA_DETAIL_CHAMELEON_INPUT) or "").strip()
            if chameleon_path:
                item["ChameleonTools"] = chameleon_path
            else:
                item.pop("ChameleonTools", None)
        # submenu: items 리스트는 건드리지 않음

        self._set_dirty(True)
        self._rebuild_entry_nodes()
        self._refresh_entry_list()
        self._update_status(self._tr("status.detail_applied"))

        refreshed = self._get_item_by_path(self._selected_entry_path)
        if refreshed is not None:
            self._bind_detail_form(refreshed, self._selected_entry_path)

    def reload_detail_from_selection(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._selected_entry_path:
            self._clear_detail_form()
            return
        item = self._get_item_by_path(self._selected_entry_path)
        if item is None:
            self._clear_detail_form()
            return
        self._bind_detail_form(item, self._selected_entry_path)

    def preview_selected_icon(self) -> None:
        """현재 아이콘 설정으로 미리보기를 갱신한다."""
        icon_type = self.data.get_combo_box_selected_item(AKA_DETAIL_ICON_TYPE) or "없음"
        icon_name = (self.data.get_text(AKA_DETAIL_ICON_NAME) or "").strip()
        self._update_icon_preview(icon_type, icon_name)

    # ──────────────────────────────────────────────────────────────────────────
    # anchor actions (left panel)
    # ──────────────────────────────────────────────────────────────────────────

    def _pick_anchor_id_from_popup(self) -> Optional[str]:
        option_to_anchor: Dict[str, str] = {}
        options: List[str] = []
        for idx, anchor_id in enumerate(ANCHOR_PRESET_IDS):
            # Keep popup options unique even when short labels are identical.
            label = f"{idx + 1}. {self._format_anchor_label(anchor_id)}"
            option_to_anchor[label] = anchor_id
            options.append(label)

        manual_input_option = self._tr("dialog.add_anchor_manual_input")
        options.append(manual_input_option)

        selected = ui.helper.OptionDialog.open_dialog(
            options,
            message=self._tr("dialog.add_anchor_pick_message"),
            label=self._tr("dialog.add_anchor_pick_label"),
            submit_text=self._tr("ui.add"),
            cancel_text=self._tr("ui.cancel"),
        )
        if not selected:
            return None
        if selected == manual_input_option:
            return (
                ui.helper.NameDialog.open_dialog(
                    message=self._tr("dialog.add_anchor_message"),
                    title_text=self._tr("dialog.add_anchor_title"),
                )
                or None
            )
        return option_to_anchor.get(selected)

    def add_anchor(self) -> None:
        """새 앵커를 추가한다. NameDialog로 ID를 입력받는다."""
        if not self._ensure_enabled():
            return
        anchor_id = self._pick_anchor_id_from_popup()
        if not anchor_id:
            return
        if anchor_id in self._config_data:
            self._update_status(self._tr("status.anchor_exists", anchor=anchor_id))
            return
        self._config_data[anchor_id] = {"items": []}
        self._set_dirty(True)
        self._rebuild_anchor_cache()
        self._active_anchor = anchor_id
        self._refresh_anchor_list()
        self._refresh_entry_list()
        self._update_status(self._tr("status.anchor_added", anchor=anchor_id))

    def delete_anchor(self) -> None:
        """선택된 앵커를 삭제한다."""
        if not self._ensure_enabled():
            return
        if not self._active_anchor:
            self._update_status(self._tr("status.select_anchor_first"))
            return
        anchor_id = self._active_anchor
        item_count = len(self._config_data.get(anchor_id, {}).get("items", []))
        title: Any = self._tr("dialog.delete_anchor_title")
        message: Any = self._tr("dialog.delete_anchor_message", anchor_id=anchor_id, item_count=item_count)
        result = unreal.EditorDialog.show_message(
            title,
            message,
            unreal.AppMsgType.YES_NO,
        )
        if result != unreal.AppReturnType.YES:
            self._update_status(self._tr("status.anchor_delete_canceled"))
            return
        del self._config_data[anchor_id]
        self._active_anchor = None
        self._set_dirty(True)
        self._rebuild_anchor_cache()
        self._refresh_anchor_list()
        self._refresh_entry_list()
        self.data.set_text(AKA_DETAIL, "")
        self._update_status(self._tr("status.anchor_deleted", anchor=anchor_id))

    def rename_anchor(self) -> None:
        """선택된 앵커 ID를 변경한다. (apply_anchor_changes로 대체됨 — 하위 호환용)"""
        self.apply_anchor_changes()

    def apply_anchor_changes(self) -> None:
        """앵커 디테일 패널의 변경사항을 적용한다."""
        if not self._ensure_enabled() or not self._active_anchor:
            return
        self._update_status(self._tr("status.anchor_detail_reloaded"))

    def reload_anchor_detail(self) -> None:
        """앵커 디테일 패널을 현재 데이터로 되돌린다."""
        self._show_anchor_detail()
        self._update_status(self._tr("status.anchor_detail_reloaded"))

    # ──────────────────────────────────────────────────────────────────────────
    # edit actions (middle panel)
    # ──────────────────────────────────────────────────────────────────────────

    def show_add_type_dialog(self) -> None:
        """타입 선택 다이얼로그를 열고 항목을 추가한다."""
        if not self._ensure_enabled():
            return
        if not self._active_anchor:
            self._update_status(self._tr("status.select_anchor_first"))
            return
        selected_type = ui.helper.OptionDialog.open_dialog(
            ["command", "submenu", "chameleon"],
            message=self._tr("dialog.add_type_message"),
            label=self._tr("dialog.type_label"),
            submit_text=self._tr("ui.add"),
            cancel_text=self._tr("ui.cancel"),
        )
        if selected_type:
            self.add_menu_item(selected_type)

    def add_menu_item(self, item_type: str = "command") -> None:
        if not self._ensure_enabled():
            return
        if not self._active_anchor:
            self._update_status(self._tr("status.select_anchor_first"))
            return

        items = self._get_items_of_active_anchor()
        item_count = len(items) + 1
        if item_type == "submenu":
            new_item = {
                "name": f"New Submenu {item_count}",
                "items": [],
                "tooltip": "",
            }
        elif item_type == "chameleon":
            new_item = {
                "name": f"New Chameleon {item_count}",
                "ChameleonTools": "",
                "tooltip": "",
            }
        else:
            new_item = {
                "name": f"New Item {item_count}",
                "command": "print('new item')",
                "tooltip": "",
            }

        # 선택된 항목이 있으면 삽입 위치 결정:
        # - submenu 선택 시: 그 하위 children의 끝에 추가
        # - 일반 항목 선택 시: 같은 레벨 바로 아래에 삽입
        # - 선택 없으면: 루트 끝에 추가
        inserted_path: Optional[PathTuple] = None
        if self._entry_selection:
            idx = next(iter(self._entry_selection))
            if 0 <= idx < len(self._entry_nodes):
                selected_path = self._entry_nodes[idx]["path"]
                selected_item = self._entry_nodes[idx]["item"]
                if self._get_entry_type(selected_item) == EntryType.SUBMENU:
                    # submenu 내부 children에 추가
                    children: Optional[List[Dict[str, Any]]] = selected_item.get("items")
                    if children is not None:
                        children.append(new_item)
                        inserted_path = selected_path + (len(children) - 1,)
                else:
                    parent_path = selected_path[:-1]
                    insert_idx = selected_path[-1] + 1
                    target_list = self._get_list_by_parent_path(parent_path)
                    if target_list is not None and 0 <= insert_idx <= len(target_list):
                        target_list.insert(insert_idx, new_item)
                        inserted_path = parent_path + (insert_idx,)

        if inserted_path is None:
            items.append(new_item)
            inserted_path = (len(items) - 1,)
        self._set_dirty(True)
        self._rebuild_entry_nodes()
        self._refresh_entry_list()
        self._selected_entry_path = inserted_path
        self._update_status(self._tr("status.item_added", item_type=item_type, anchor=self._active_anchor))

    def delete_menu_item(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._active_anchor:
            self._update_status(self._tr("status.select_anchor_first"))
            return
        if not self._entry_selection:
            self._update_status(self._tr("status.select_entry_to_delete"))
            return

        idx = next(iter(self._entry_selection))
        if not (0 <= idx < len(self._entry_nodes)):
            return

        path = self._entry_nodes[idx]["path"]
        ok = self._delete_by_path(path)
        if not ok:
            self._update_status(self._tr("status.entry_delete_failed"))
            return

        self._entry_selection.clear()
        self._set_dirty(True)
        self._rebuild_entry_nodes()
        self._refresh_entry_list()
        self.data.set_text(AKA_DETAIL, "")
        self._update_status(self._tr("status.entry_deleted"))

    def move_entry_up(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._active_anchor or not self._entry_selection:
            self._update_status(self._tr("status.select_entry"))
            return

        idx = next(iter(self._entry_selection))
        if not (0 <= idx < len(self._entry_nodes)):
            return

        path = self._entry_nodes[idx]["path"]
        if self._move_entry_in_path(path, -1):
            self._set_dirty(True)
            self._rebuild_entry_nodes()
            self._refresh_entry_list()
            self._update_status(self._tr("status.entry_moved_up"))
        else:
            self._update_status(self._tr("status.entry_at_top"))

    def move_entry_down(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._active_anchor or not self._entry_selection:
            self._update_status(self._tr("status.select_entry"))
            return

        idx = next(iter(self._entry_selection))
        if not (0 <= idx < len(self._entry_nodes)):
            return

        path = self._entry_nodes[idx]["path"]
        if self._move_entry_in_path(path, 1):
            self._set_dirty(True)
            self._rebuild_entry_nodes()
            self._refresh_entry_list()
            self._update_status(self._tr("status.entry_moved_down"))
        else:
            self._update_status(self._tr("status.entry_at_bottom"))

    def _move_entry_in_path(self, path: PathTuple, direction: int) -> bool:
        """Move entry up (direction=-1) or down (direction=1). Return True if moved."""
        if not path:
            return False

        items = self._get_items_of_active_anchor()
        target_list = items
        for idx in path[:-1]:
            if not (0 <= idx < len(target_list)):
                return False
            next_item = target_list[idx]
            children = next_item.get("items")
            if not isinstance(children, list):
                return False
            target_list = children

        last_idx = path[-1]
        new_idx = last_idx + direction
        if not (0 <= new_idx < len(target_list)):
            return False

        target_list[last_idx], target_list[new_idx] = target_list[new_idx], target_list[last_idx]
        return True

    def copy_entry(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._entry_selection:
            self._update_status(self._tr("status.select_entry"))
            return

        idx = next(iter(self._entry_selection))
        if not (0 <= idx < len(self._entry_nodes)):
            return

        item = self._entry_nodes[idx]["item"]
        # 깊은 복사로 독립적인 복사본 생성
        self._clipboard_entry = json.loads(json.dumps(item))
        self._update_status(self._tr("status.entry_copied"))

    def paste_entry(self) -> None:
        if not self._ensure_enabled():
            return
        if not self._active_anchor:
            self._update_status(self._tr("status.select_anchor_first"))
            return
        if not self._clipboard_entry:
            self._update_status(self._tr("status.no_clipboard_entry"))
            return

        # 깊은 복사로 클립보드 항목의 복사본 생성
        pasted_item = json.loads(json.dumps(self._clipboard_entry))

        # 선택된 항목이 있으면 그 바로 아래에 삽입, 없으면 루트 끝에 추가
        inserted_path: Optional[PathTuple] = None
        if self._entry_selection:
            idx = next(iter(self._entry_selection))
            if 0 <= idx < len(self._entry_nodes):
                selected_path = self._entry_nodes[idx]["path"]
                parent_path = selected_path[:-1]
                insert_idx = selected_path[-1] + 1
                target_list = self._get_list_by_parent_path(parent_path)
                if target_list is not None and 0 <= insert_idx <= len(target_list):
                    target_list.insert(insert_idx, pasted_item)
                    inserted_path = parent_path + (insert_idx,)

        if inserted_path is None:
            items = self._get_items_of_active_anchor()
            items.append(pasted_item)
            inserted_path = (len(items) - 1,)

        self._set_dirty(True)
        self._rebuild_entry_nodes()
        self._refresh_entry_list()
        self._selected_entry_path = inserted_path
        self._update_status(self._tr("status.entry_pasted"))

    def _delete_by_path(self, path: PathTuple) -> bool:
        if not path:
            return False

        parent_path = path[:-1]
        target_list = self._get_list_by_parent_path(parent_path)
        if target_list is None:
            return False

        idx = path[-1]
        if not (0 <= idx < len(target_list)):
            return False

        target_list.pop(idx)
        return True

    def _get_list_by_parent_path(self, parent_path: PathTuple) -> Optional[List[Dict[str, Any]]]:
        target_list = self._get_items_of_active_anchor()
        if not parent_path:
            return target_list

        for idx in parent_path:
            if not (0 <= idx < len(target_list)):
                return None
            next_item = target_list[idx]
            children = next_item.get("items")
            if not isinstance(children, list):
                return None
            target_list = children

        return target_list

    # ──────────────────────────────────────────────────────────────────────────
    # view refresh
    # ──────────────────────────────────────────────────────────────────────────

    def _refresh_all_views(self) -> None:
        self._refresh_anchor_list()
        self._refresh_entry_list()
        # 항목 선택 전에는 디테일 패널을 항상 비운다.
        self._clear_detail_form()

    def _refresh_anchor_list(self) -> None:
        names = [self._format_anchor_label(name) for name in self._anchor_names] if self._anchor_names else ["(empty)"]
        parents = [-1 for _ in names]
        try:
            self.data.set_tree_view_items(AKA_LIST_ANCHORS, names, parents)  # type: ignore[arg-type]
        except Exception:
            # fallback for older API builds
            self.data.set_list_view_items(AKA_LIST_ANCHORS, names)  # type: ignore[arg-type]

    @staticmethod
    def _friendly_anchor_name(anchor_id: str) -> str:
        """Convert a dotted anchor ID to a readable display name."""
        leaf = anchor_id.split(".")[-1].strip() if anchor_id else ""
        if not leaf:
            return anchor_id

        # snake_case / kebab-case -> spaces
        text = leaf.replace("_", " ").replace("-", " ")
        # CamelCase -> Camel Case
        text = re.sub(r"(?<!^)(?=[A-Z][a-z])", " ", text)
        # Collapse duplicate spaces
        text = " ".join(text.split())

        return text if text else anchor_id

    def _format_anchor_label(self, anchor_id: str) -> str:
        meta = ANCHOR_INLINE_META.get(anchor_id, {})
        if isinstance(meta, dict):
            display_name = str(meta.get("displayName", "")).strip()
            if display_name:
                return f"📂 {display_name}"

        friendly = self._friendly_anchor_name(anchor_id)
        if friendly:
            return f"📂 {friendly}"
        return "📂 (Unnamed)"

    def _refresh_entry_list(self) -> None:
        labels: List[str] = []
        parents: List[int] = []
        path_to_flat_index: Dict[Tuple[int, ...], int] = {}

        for node in self._entry_nodes:
            depth = node["depth"]
            item = node["item"]
            path = node["path"]
            name = str(item.get("name", "(No Name)"))
            entry_type = self._get_entry_type(item)
            icon = self._get_entry_icon(entry_type)
            indent = "  " * depth
            labels.append(f"{indent}{icon} {name}")
            current_index = len(labels) - 1
            path_to_flat_index[path] = current_index
            parent_path = path[:-1]
            parents.append(path_to_flat_index.get(parent_path, -1) if parent_path else -1)
        if not labels:
            labels = ["(empty)"]
            parents = [-1]

        try:
            self.data.set_tree_view_items(AKA_LIST_ENTRIES, labels, parents)  # type: ignore[arg-type]
        except Exception:
            self.data.set_list_view_items(AKA_LIST_ENTRIES, labels)  # type: ignore[arg-type]

    def _sync_entry_selection_from_widget(self, fallback_index: Any = -1) -> None:
        selected_indexes = self._get_selected_entry_indexes_from_widget()
        if not selected_indexes:
            try:
                idx = int(fallback_index)
            except Exception:
                idx = -1
            if idx >= 0:
                selected_indexes = [idx]

        if not selected_indexes:
            self._entry_selection.clear()
            self._selected_entry_path = None
            self._clear_detail_form()
            self._set_detail_panel_enabled(False)
            return

        idx = selected_indexes[0]
        self._entry_selection = {idx}
        if 0 <= idx < len(self._entry_nodes):
            node = self._entry_nodes[idx]
            self._selected_entry_path = node["path"]
            self._show_entry_detail(node)
            self._set_detail_panel_enabled(True)
            return

        self._entry_selection.clear()
        self._selected_entry_path = None
        self._clear_detail_form()
        self._set_detail_panel_enabled(False)

    def _get_selected_entry_indexes_from_widget(self) -> List[int]:
        try:
            tree_state = self.data.get_tree_view_items(AKA_LIST_ENTRIES)
        except Exception:
            return []

        if not tree_state or len(tree_state) != 2:
            return []

        _, item_states = tree_state
        selected_indexes: List[int] = []
        for idx, state in enumerate(item_states):
            try:
                if int(state) != 0:
                    selected_indexes.append(idx)
            except Exception:
                continue
        return selected_indexes

    # ──────────────────────────────────────────────────────────────────────────
    # detail pane
    # ──────────────────────────────────────────────────────────────────────────

    def _show_entry_detail(self, node: Dict[str, Any]) -> None:
        path = node["path"]
        item = node["item"]
        self._bind_detail_form(item, path)

    @staticmethod
    def _get_entry_type(item: Dict[str, Any]) -> str:
        """Return EntryType value based on item keys."""
        if "ChameleonTools" in item:
            return EntryType.CHAMELEON
        if isinstance(item.get("items"), list):
            return EntryType.SUBMENU
        return EntryType.COMMAND

    @staticmethod
    def _get_entry_icon(entry_type: str) -> str:
        if entry_type == EntryType.SUBMENU:
            return "📁"
        if entry_type == EntryType.CHAMELEON:
            return "🎨"
        if entry_type == EntryType.COMMAND:
            return "⚡"
        return "📄"

    def _bind_detail_form(self, item: Dict[str, Any], path: PathTuple) -> None:
        entry_type = self._get_entry_type(item)
        self.data.set_text(AKA_DETAIL_TYPE_TEXT, self._get_entry_type_label(entry_type))
        self.data.set_text(AKA_DETAIL_NAME, str(item.get("name", "")))
        self.data.set_text(AKA_DETAIL_TOOLTIP, str(item.get("tooltip", "")))
        self.data.set_is_checked(AKA_DETAIL_ENABLED, bool(item.get("enabled", True)))

        self._bind_entry_type_fields(item, entry_type)
        self._bind_icon_fields(item)

        lines = [
            "--- Entry JSON (Preview) ---",
            json.dumps(item, indent=2, ensure_ascii=False),
        ]
        self.data.set_text(AKA_DETAIL, "\n".join(lines))
        self._set_detail_panel_enabled(True)
        self._set_detail_editor_visible(True, entry_type)

    def _get_entry_type_label(self, entry_type: str) -> str:
        key = ENTRY_TYPE_LABEL_KEYS.get(entry_type)
        if key:
            return self._tr(key)
        return self._tr("entry_type.unknown", entry_type=entry_type)

    def _bind_entry_type_fields(self, item: Dict[str, Any], entry_type: str) -> None:
        """Bind type-specific input fields."""
        if entry_type == EntryType.CHAMELEON:
            self.data.set_text(AKA_DETAIL_CHAMELEON_INPUT, str(item.get("ChameleonTools", "")))
            self.data.set_text(AKA_DETAIL_COMMAND, "")
            self.data.set_text(AKA_DETAIL_CAN_EXECUTE_ACTION, "")
        elif entry_type == EntryType.COMMAND:
            self.data.set_text(AKA_DETAIL_COMMAND, str(item.get("command", "")))
            self.data.set_text(AKA_DETAIL_CAN_EXECUTE_ACTION, str(item.get("canExecuteAction", "")))
            self.data.set_text(AKA_DETAIL_CHAMELEON_INPUT, "")
        else:  # EntryType.SUBMENU
            self.data.set_text(AKA_DETAIL_COMMAND, "")
            self.data.set_text(AKA_DETAIL_CAN_EXECUTE_ACTION, "")
            self.data.set_text(AKA_DETAIL_CHAMELEON_INPUT, "")

    def _bind_icon_fields(self, item: Dict[str, Any]) -> None:
        icon_data = item.get("icon", {})
        icon_type = "없음"
        icon_name = ""
        if isinstance(icon_data, dict):
            if "style" in icon_data:
                style = str(icon_data.get("style", ""))
                if style in ("EditorStyle", "CoreStyle", "ChameleonStyle"):
                    icon_type = style
                    icon_name = str(icon_data.get("name", ""))
                elif style == "AppStyle":
                    # 구버전 데이터 호환: AppStyle은 EditorStyle로 통합
                    icon_type = "EditorStyle"
                    icon_name = str(icon_data.get("name", ""))
            elif "ImagePathInPlugin" in icon_data:
                icon_type = "ImagePath"
                icon_name = str(icon_data.get("ImagePathInPlugin", ""))

        try:
            self.data.set_combo_box_items(AKA_DETAIL_ICON_TYPE, self.ICON_TYPES)  # type: ignore[arg-type]
            idx = self.ICON_TYPES.index(icon_type) if icon_type in self.ICON_TYPES else 0
            self.data.set_combo_box_selected_item(AKA_DETAIL_ICON_TYPE, idx)  # type: ignore[arg-type]
        except Exception:
            pass
        self.data.set_text(AKA_DETAIL_ICON_NAME, icon_name)
        # 항목 선택 시 자동 프리뷰 탐색은 누락 브러시 경고 로그를 유발할 수 있어,
        # 여기서는 플레이스홀더만 보여주고 사용자가 버튼을 눌렀을 때만 프리뷰를 시도한다.
        self._update_icon_preview("없음", "")

    def _apply_icon_data(self, item: Dict[str, Any]) -> None:
        icon_type = self.data.get_combo_box_selected_item(AKA_DETAIL_ICON_TYPE) or "없음"
        icon_name = (self.data.get_text(AKA_DETAIL_ICON_NAME) or "").strip()

        if icon_type != "없음" and icon_name:
            if icon_type == "EditorStyle":
                item["icon"] = {"style": "EditorStyle", "name": icon_name}
            elif icon_type == "CoreStyle":
                item["icon"] = {"style": "CoreStyle", "name": icon_name}
            elif icon_type == "ChameleonStyle":
                item["icon"] = {"style": "ChameleonStyle", "name": icon_name}
            elif icon_type == "ImagePath":
                item["icon"] = {"ImagePathInPlugin": icon_name}
            else:
                item.pop("icon", None)
        else:
            item.pop("icon", None)

    def _get_item_by_path(self, path: PathTuple) -> Optional[Dict[str, Any]]:
        if not path:
            return None
        items = self._get_items_of_active_anchor()
        current: Optional[Dict[str, Any]] = None
        target_list = items
        for idx in path:
            if not (0 <= idx < len(target_list)):
                return None
            current = target_list[idx]
            children = current.get("items")
            if isinstance(children, list):
                target_list = children
            else:
                target_list = []
        return current

    def _clear_detail_inputs(self) -> None:
        self.data.set_text(AKA_DETAIL_NAME, "")
        self.data.set_text(AKA_DETAIL_TOOLTIP, "")
        self.data.set_text(AKA_DETAIL_COMMAND, "")
        self.data.set_text(AKA_DETAIL_CAN_EXECUTE_ACTION, "")
        self.data.set_text(AKA_DETAIL_CHAMELEON_INPUT, "")
        self.data.set_is_checked(AKA_DETAIL_ENABLED, True)
        self.data.set_text(AKA_DETAIL_ICON_NAME, "")
        try:
            self.data.set_combo_box_selected_item(AKA_DETAIL_ICON_TYPE, 0)  # type: ignore[arg-type]
        except Exception:
            pass
        self._update_icon_preview("없음", "")

    def _update_icon_preview(self, icon_type: str, icon_name: str) -> None:
        """아이콘 설정에 따라 프리뷰 호스트를 갱신한다."""
        if icon_type == "없음" or not icon_name:
            self.data.set_content_from_json(
                AKA_DETAIL_ICON_PREVIEW_HOST,
                '{"STextBlock": {"Text": "' + self._tr("preview.none") + '"}}',
            )
            return

        if icon_type == "ImagePath":
            try:
                normalized_path = icon_name.replace("\\", "/").strip()
                # TAPython의 set_image_from_path는 플러그인 Resources를 기준으로 해석하므로
                # 사용자가 Resources/ 접두를 넣으면 Resources/Resources/...가 되어 실패한다.
                if normalized_path.lower().startswith("resources/"):
                    normalized_path = normalized_path[len("Resources/"):]
                elif normalized_path.lower().startswith("/resources/"):
                    normalized_path = normalized_path[len("/Resources/"):]

                self.data.set_content_from_json(
                    AKA_DETAIL_ICON_PREVIEW_HOST,
                    '{"SHorizontalBox": {"Slots": ['
                    '{"AutoWidth": true, "VAlign": "Center", '
                    '"SImage": {"Aka": "DetailIconPreviewImage", "DesiredSizeOverride": [18, 18]}}'
                    ']}}',
                )
                self.data.set_image_from_path(unreal.Name("DetailIconPreviewImage"), normalized_path, 18, 18)  # type: ignore[arg-type]
            except Exception:
                self.data.set_content_from_json(
                    AKA_DETAIL_ICON_PREVIEW_HOST,
                    '{"STextBlock": {"Text": "' + self._tr("preview.imagepath_failed") + '"}}',
                )
            return

        if icon_type == "EditorStyle":
            # EditorStyle 프리뷰는 엔진/Chameleon 버전별 편차가 커서
            # 오탐 경고와 로그 노이즈를 줄이기 위해 비활성화한다.
            self.data.set_content_from_json(
                AKA_DETAIL_ICON_PREVIEW_HOST,
                '{"STextBlock": {"Text": "' + self._tr("preview.editorstyle_disabled") + '"}}',
            )
            self._update_status(self._tr("status.editorstyle_preview_guide"))
            return

        if icon_type == "CoreStyle":
            self.data.set_content_from_json(
                AKA_DETAIL_ICON_PREVIEW_HOST,
                '{"STextBlock": {"Text": "' + self._tr("preview.corestyle_disabled") + '"}}',
            )
            self._update_status(self._tr("status.corestyle_preview_guide"))
            return

        # ChameleonStyle은 엔트리 아이콘 포맷으로는 지원되지만,
        # SImage style 렌더링 style-name 정보가 별도로 필요할 수 있어 안내만 출력.
        if icon_type == "ChameleonStyle":
            self.data.set_content_from_json(
                AKA_DETAIL_ICON_PREVIEW_HOST,
                '{"STextBlock": {"Text": "' + self._tr("preview.chameleon_unsupported") + '"}}',
            )
            return

    def _clear_detail_form(self) -> None:
        self._clear_detail_inputs()
        self.data.set_text(AKA_DETAIL, "")
        self._set_detail_panel_enabled(False)
        self._set_detail_editor_visible(False)
        try:
            self.data.set_visibility(AKA_ANCHOR_DETAIL_ROW, "Collapsed")
        except Exception:
            pass

    def _show_anchor_detail(self) -> None:
        """앵커 디테일 패널을 표시하고 현재 앵커 데이터로 채운다."""
        if not self._active_anchor:
            return
        meta = ANCHOR_INLINE_META.get(self._active_anchor, {})
        display_name = ANCHOR_META_EMPTY_DISPLAY_NAME
        tooltip = ANCHOR_META_EMPTY_TOOLTIP
        if isinstance(meta, dict) and meta:
            display_name = str(meta.get("displayName", "")).strip() or ANCHOR_META_EMPTY_DISPLAY_NAME
            tooltip = str(meta.get("tooltip", "")).strip() or ANCHOR_META_EMPTY_TOOLTIP

        is_builtin_anchor = self._is_chameleon_base_anchor(self._active_anchor)
        self._set_detail_panel_enabled(True)
        try:
            # 엔트리 디테일 숨기고 앵커 디테일 표시
            self.data.set_visibility(AKA_DETAIL_EMPTY, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_TYPE_ROW, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_NAME_ROW, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_TOOLTIP_ROW, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_ICON_EXPANDABLE, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_ENABLED, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_BUTTONS_ROW, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_COMMAND_LABEL, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_CAN_EXECUTE_ACTION_LABEL, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_CAN_EXECUTE_ACTION, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_COMMAND, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_CHAMELEON_ROW, "Collapsed")
            self.data.set_visibility(AKA_DETAIL_DEBUG_EXPANDABLE, "Collapsed")
            self.data.set_visibility(AKA_DETAIL, "Collapsed")
            self.data.set_text(AKA_ANCHOR_ID_INPUT, self._active_anchor)
            self.data.set_text(AKA_ANCHOR_DISPLAY_NAME_INPUT, display_name)
            self.data.set_text(AKA_ANCHOR_TOOLTIP_INPUT, tooltip)
            self.data.set_is_checked(AKA_ANCHOR_IS_READONLY_CHECK, is_builtin_anchor)
            self.data.set_visibility(AKA_ANCHOR_READONLY_NOTICE, "Visible" if is_builtin_anchor else "Collapsed")
            self._set_anchor_detail_readonly(True)
            self.data.set_visibility(AKA_ANCHOR_DETAIL_ROW, "Visible")
        except Exception as e:
            unreal.log_error(f"TAPythonMenuEditor: 앵커 디테일 표시 오류 — {e}")

    def _set_anchor_detail_readonly(self, is_readonly: bool) -> None:
        """Set anchor detail controls to read-only mode for built-in Chameleon anchors."""
        try:
            # Some ChameleonData builds support read-only toggling on editable text boxes.
            self.data.set_text_read_only(AKA_ANCHOR_ID_INPUT, is_readonly)
            self.data.set_text_read_only(AKA_ANCHOR_DISPLAY_NAME_INPUT, is_readonly)
            self.data.set_text_read_only(AKA_ANCHOR_TOOLTIP_INPUT, is_readonly)
        except Exception:
            pass

        try:
            # Apply는 읽기 전용일 때만 숨긴다.
            self.data.set_visibility(AKA_BTN_ANCHOR_APPLY, "Collapsed" if is_readonly else "Visible")
        except Exception:
            pass

        try:
            # Anchor detail에서는 Revert 버튼을 항상 숨긴다.
            self.data.set_visibility(AKA_BTN_ANCHOR_REVERT, "Collapsed")
        except Exception:
            pass

    @staticmethod
    def _is_chameleon_base_anchor(anchor_id: str) -> bool:
        return anchor_id in CHAMELEON_BASE_ANCHOR_IDS

    def _is_anchor_readonly(self, anchor_id: str) -> bool:
        return self._is_chameleon_base_anchor(anchor_id)

    def _set_detail_panel_enabled(self, enabled: bool) -> None:
        try:
            self.data.set_enabled(AKA_DETAIL_PANEL, enabled)
        except Exception:
            # 일부 TAPython 빌드에서 set_enabled 지원이 제한될 수 있음
            pass

    def _set_detail_editor_visible(self, visible: bool, entry_type: str = "command") -> None:
        try:
            ev = "Visible" if visible else "Collapsed"
            empty_v = "Collapsed" if visible else "Visible"

            self.data.set_visibility(AKA_DETAIL_EMPTY, empty_v)
            self.data.set_visibility(AKA_DETAIL_TYPE_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_NAME_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_TOOLTIP_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_ICON_EXPANDABLE, ev)
            self.data.set_visibility(AKA_DETAIL_ICON_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_ICON_PREVIEW_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_ENABLED, ev)
            self.data.set_visibility(AKA_DETAIL_BUTTONS_ROW, ev)
            self.data.set_visibility(AKA_DETAIL_DEBUG_EXPANDABLE, ev)
            self.data.set_visibility(AKA_DETAIL, ev)
            # 앵커 디테일은 항상 숨김
            self.data.set_visibility(AKA_ANCHOR_DETAIL_ROW, "Collapsed")

            # Command 타입만 Command 입력란 표시, Chameleon 타입만 ChameleonTools 행 표시
            command_v = "Visible" if (visible and entry_type == EntryType.COMMAND) else "Collapsed"
            chameleon_v = "Visible" if (visible and entry_type == EntryType.CHAMELEON) else "Collapsed"

            self.data.set_visibility(AKA_DETAIL_COMMAND_LABEL, command_v)
            self.data.set_visibility(AKA_DETAIL_CAN_EXECUTE_ACTION_LABEL, command_v)
            self.data.set_visibility(AKA_DETAIL_CAN_EXECUTE_ACTION, command_v)
            self.data.set_visibility(AKA_DETAIL_COMMAND, command_v)
            self.data.set_visibility(AKA_DETAIL_CHAMELEON_ROW, chameleon_v)
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    # misc
    # ──────────────────────────────────────────────────────────────────────────

    def _update_status(self, msg: str) -> None:
        self.data.set_text(AKA_STATUS, msg)
        unreal.log(f"TAPythonMenuEditor: {msg}")

    def _set_dirty(self, dirty: bool) -> None:
        self._is_dirty = dirty
        try:
            vis = "Visible" if dirty else "Collapsed"
            self.data.set_visibility(AKA_DIRTY_INDICATOR, vis)
        except Exception:
            pass

    def _update_file_path_display(self, file_path: str) -> None:
        self.data.set_text(AKA_FILE_PATH, file_path)

    def _ensure_enabled(self) -> bool:
        if self._tool_enabled:
            return True
        self._update_status(self._tr("status.disabled_missing_menuconfig"))
        return False


def launch() -> None:
    json_path = Path(__file__).with_suffix(".json").as_posix()
    json_name = Path(json_path).name

    # 동일 json 이름의 기존 탭은 모두 닫고 항상 새로 실행하여
    # InitPyCmd(모듈 reload 포함)가 확실히 다시 수행되도록 한다.
    for p in unreal.PythonBPLib.get_all_chameleon_data_paths():
        if Path(p).name == json_name:
            unreal.ChameleonData.request_close(p)

    unreal.ChameleonData.launch_chameleon_tool(json_path)


if __name__ == "__main__":
    launch()
