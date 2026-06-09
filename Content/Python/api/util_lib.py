"""
언리얼 엔진 에디터 유틸리티 라이브러리 래퍼 모듈
==============================================

이 모듈은 언리얼 엔진 에디터 유틸리티 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorUtilityLibrary 함수들:
- unreal.EditorUtilityLibrary.function_name → util_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# 에디터 유틸리티 라이브러리 래퍼들
# ===============================================================================

# 위젯 블루프린트 관리
def add_source_widget(widget_blueprint, widget_class, widget_name, widget_parent_name):
    """새 위젯을 생성하고 특정 위젯 블루프린트의 위젯 트리에 추가합니다."""
    return unreal.EditorUtilityLibrary.add_source_widget(widget_blueprint, widget_class, widget_name, widget_parent_name)


def cast_to_widget_blueprint(object):
    """위젯 블루프린트로 캐스팅합니다."""
    return unreal.EditorUtilityLibrary.cast_to_widget_blueprint(object)


def convert_to_editor_utility_widget(widget_bp):
    """에디터 유틸리티 위젯으로 변환합니다."""
    return unreal.EditorUtilityLibrary.convert_to_editor_utility_widget(widget_bp)


def find_source_widget_by_name(widget_blueprint, widget_name):
    """지정된 이름을 가진 위젯을 블루프린트의 위젯 계층구조에서 검색합니다."""
    return unreal.EditorUtilityLibrary.find_source_widget_by_name(widget_blueprint, widget_name)


# 액터 및 월드 관리
def get_actor_reference(path_to_actor):
    """현재 에디터 월드에서 PathToActor로 지정된 액터를 찾으려고 시도합니다."""
    # Note: This function requires an instance of EditorUtilityLibrary
    utility_lib = unreal.EditorUtilityLibrary()
    return utility_lib.get_actor_reference(path_to_actor)


def get_selection_set():
    """선택 세트를 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selection_set()


def get_selection_bounds():
    """선택 경계를 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selection_bounds()


# 콘텐츠 브라우저 탐색
def get_current_content_browser_item_path():
    """콘텐츠 브라우저가 열려있는 경우 현재 콘텐츠 브라우저 경로를 가져옵니다 (내부 또는 가상 경로)."""
    return unreal.EditorUtilityLibrary.get_current_content_browser_item_path()


def get_current_content_browser_path():
    """활성 콘텐츠 브라우저의 경로를 가져오려고 시도합니다."""
    return unreal.EditorUtilityLibrary.get_current_content_browser_path()


def sync_browser_to_folders(folder_list):
    """콘텐츠 브라우저를 주어진 폴더(들)와 동기화합니다."""
    return unreal.EditorUtilityLibrary.sync_browser_to_folders(folder_list)


# 에셋 선택 및 검색
def get_selected_asset_data():
    """현재 선택된 에셋 데이터 집합을 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selected_asset_data()


def get_selected_assets() -> list:
    """현재 선택된 에셋들의 집합을 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selected_assets()


def get_selected_assets_of_class(asset_class) -> list:
    """지정된 클래스의 선택된 에셋들을 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selected_assets_of_class(asset_class)


def get_selected_blueprint_classes() -> list:
    """현재 선택된 클래스들의 집합을 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selected_blueprint_classes()


# 폴더 및 경로 선택
def get_selected_folder_paths():
    """콘텐츠 브라우저에서 현재 선택된 폴더의 경로를 가져옵니다."""
    return unreal.EditorUtilityLibrary.get_selected_folder_paths()


def get_selected_path_view_folder_paths():
    """콘텐츠 브라우저의 경로 보기에서 선택된 폴더들을 반환합니다."""
    return unreal.EditorUtilityLibrary.get_selected_path_view_folder_paths()


# 에셋 관리 (에디터 유틸리티)
def rename_asset(asset, new_name):
    """에셋의 이름을 변경합니다 (폴더는 이동할 수 없음)."""
    return unreal.EditorUtilityLibrary.rename_asset(asset, new_name)