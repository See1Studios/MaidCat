"""
언리얼 엔진 에디터 에셋 라이브러리 래퍼 모듈
============================================

이 모듈은 언리얼 엔진 에디터 에셋 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorAssetLibrary 함수들:
- unreal.EditorAssetLibrary.function_name → asset_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# 에디터 에셋 라이브러리 래퍼들
# ===============================================================================

# 에셋 체크아웃 및 소스 컨트롤
def checkout_asset(asset_to_checkout: str) -> bool:
    """콘텐츠 브라우저에서 에셋을 체크아웃합니다."""
    return unreal.EditorAssetLibrary.checkout_asset(asset_to_checkout)


def checkout_directory(directory_path: str, recursive: bool = True) -> bool:
    """콘텐츠 브라우저에서 에셋들을 체크아웃합니다."""
    return unreal.EditorAssetLibrary.checkout_directory(directory_path, recursive)


def checkout_loaded_asset(asset_to_checkout: unreal.Object) -> bool:
    """콘텐츠 브라우저에서 에셋을 체크아웃합니다."""
    return unreal.EditorAssetLibrary.checkout_loaded_asset(asset_to_checkout)


def checkout_loaded_assets(assets_to_checkout: Any) -> bool:
    """콘텐츠 브라우저에서 에셋들을 체크아웃합니다."""
    return unreal.EditorAssetLibrary.checkout_loaded_assets(assets_to_checkout)


def consolidate_assets(asset_to_consolidate_to: unreal.Object, assets_to_consolidate: Any) -> bool:
    """제공된 AssetsToConsolidate의 모든 참조/사용을 AssetToConsolidateTo에 대한 참조로 대체하여 에셋을 통합합니다."""
    return unreal.EditorAssetLibrary.consolidate_assets(asset_to_consolidate_to, assets_to_consolidate)


# 에셋 삭제 및 정리
def delete_asset(asset_path_to_delete: str) -> bool:
    """에셋이 있는 패키지를 삭제합니다."""
    return unreal.EditorAssetLibrary.delete_asset(asset_path_to_delete)


def delete_directory(directory_path: str) -> bool:
    """디렉토리 내부의 패키지들을 삭제합니다."""
    return unreal.EditorAssetLibrary.delete_directory(directory_path)


def delete_loaded_asset(asset_to_delete: unreal.Object) -> bool:
    """이미 로드된 콘텐츠 브라우저에서 에셋을 삭제합니다."""
    return unreal.EditorAssetLibrary.delete_loaded_asset(asset_to_delete)


def delete_loaded_assets(assets_to_delete: Any) -> bool:
    """이미 로드된 콘텐츠 브라우저에서 에셋들을 삭제합니다."""
    return unreal.EditorAssetLibrary.delete_loaded_assets(assets_to_delete)


# 에셋 존재 여부 및 유효성 검사
def do_assets_exist(asset_paths: Any) -> bool:
    """콘텐츠 브라우저에서 에셋들이 존재하는지 확인합니다."""
    return unreal.EditorAssetLibrary.do_assets_exist(asset_paths)


def does_asset_exist(asset_path: str) -> bool:
    """콘텐츠 브라우저에서 에셋이 존재하는지 확인합니다."""
    return unreal.EditorAssetLibrary.does_asset_exist(asset_path)


def does_directory_exist(directory_path: str) -> bool:
    """콘텐츠 브라우저에서 디렉토리가 존재하는지 확인합니다."""
    return unreal.EditorAssetLibrary.does_directory_exist(directory_path)


def does_directory_have_assets(directory_path: str, recursive: bool = True) -> bool:
    """디렉토리에 에셋이 있는지 확인합니다."""
    return unreal.EditorAssetLibrary.does_directory_have_assets(directory_path, recursive)


# 에셋 복제 및 복사
def duplicate_asset(source_asset_path: str, destination_asset_path: str) -> Optional[unreal.Object]:
    """콘텐츠 브라우저에서 에셋을 복제합니다."""
    return unreal.EditorAssetLibrary.duplicate_asset(source_asset_path, destination_asset_path)


def duplicate_directory(source_directory_path: str, destination_directory_path: str) -> bool:
    """폴더에 있는 콘텐츠 브라우저의 에셋들을 복제합니다."""
    return unreal.EditorAssetLibrary.duplicate_directory(source_directory_path, destination_directory_path)


def duplicate_loaded_asset(source_asset: unreal.Object, destination_asset_path: str) -> Optional[unreal.Object]:
    """이미 로드된 콘텐츠 브라우저의 에셋을 복제합니다."""
    return unreal.EditorAssetLibrary.duplicate_loaded_asset(source_asset, destination_asset_path)


# 에셋 탐색 및 검색
def find_asset_data(asset_path):
    """더 복잡한 AssetRegistryHelpers 라이브러리와 함께 사용할 수 있는 에셋의 AssetData를 반환합니다."""
    return unreal.EditorAssetLibrary.find_asset_data(asset_path)


def find_package_referencers_for_asset(asset_path, load_assets_to_confirm=False):
    """에셋의 패키지 참조자들을 찾습니다."""
    return unreal.EditorAssetLibrary.find_package_referencers_for_asset(asset_path, load_assets_to_confirm)


# 에셋 메타데이터 관리
def get_metadata_tag(object, tag):
    """로드된 에셋의 메타데이터에서 주어진 태그와 연관된 값을 가져옵니다."""
    return unreal.EditorAssetLibrary.get_metadata_tag(object, tag)


def get_metadata_tag_values(object):
    """로드된 에셋의 메타데이터의 모든 태그/값을 가져옵니다."""
    return unreal.EditorAssetLibrary.get_metadata_tag_values(object)


def get_package_for_object(object):
    """오브젝트를 포함하는 패키지를 반환합니다."""
    return unreal.EditorAssetLibrary.get_package_for_object(object)


def get_path_name_for_loaded_asset(loaded_asset):
    """로드된 에셋에 대한 유효한 AssetPath를 반환합니다."""
    return unreal.EditorAssetLibrary.get_path_name_for_loaded_asset(loaded_asset)


def get_project_root_asset_directory():
    """프로젝트 루트 에셋 디렉토리를 가져옵니다."""
    return unreal.EditorAssetLibrary.get_project_root_asset_directory()


def get_tag_values(asset_path):
    """(로드되지 않은) 에셋과 연관된 모든 TagValues를 Asset Registry에서 문자열 값으로 가져옵니다."""
    return unreal.EditorAssetLibrary.get_tag_values(asset_path)


# 에셋 목록 및 디렉토리 작업
def list_asset_by_tag_value(tag_name, tag_value):
    """Tag/Value 쌍을 가진 모든 에셋들의 목록을 반환합니다."""
    return unreal.EditorAssetLibrary.list_asset_by_tag_value(tag_name, tag_value)


def list_assets(directory_path, recursive=True, include_folder=False):
    """DirectoryPath에서 찾은 모든 에셋들의 목록을 반환합니다."""
    return unreal.EditorAssetLibrary.list_assets(directory_path, recursive, include_folder)


def load_asset(asset_path: str) -> Optional[unreal.Object]:
    """콘텐츠 브라우저에서 에셋을 로드합니다."""
    return unreal.EditorAssetLibrary.load_asset(asset_path)


def load_blueprint_class(asset_path: str) -> Optional[type]:
    """콘텐츠 브라우저에서 블루프린트 에셋을 로드하고 생성된 클래스를 반환합니다."""
    return unreal.EditorAssetLibrary.load_blueprint_class(asset_path)


def make_directory(directory_path):
    """디스크와 콘텐츠 브라우저에 디렉토리를 생성합니다."""
    return unreal.EditorAssetLibrary.make_directory(directory_path)


def remove_metadata_tag(object, tag):
    """로드된 에셋의 메타데이터에서 주어진 태그를 제거합니다."""
    return unreal.EditorAssetLibrary.remove_metadata_tag(object, tag)


# 에셋 이름 변경 및 이동
def rename_asset(source_asset_path, destination_asset_path):
    """콘텐츠 브라우저에서 에셋의 이름을 변경합니다."""
    return unreal.EditorAssetLibrary.rename_asset(source_asset_path, destination_asset_path)


def rename_directory(source_directory_path, destination_directory_path):
    """폴더에 있는 콘텐츠 브라우저의 에셋들의 이름을 변경합니다."""
    return unreal.EditorAssetLibrary.rename_directory(source_directory_path, destination_directory_path)


def rename_loaded_asset(source_asset, destination_asset_path):
    """이미 로드된 콘텐츠 브라우저의 에셋 이름을 변경합니다."""
    return unreal.EditorAssetLibrary.rename_loaded_asset(source_asset, destination_asset_path)


def save_asset(asset_to_save: str, only_if_is_dirty: bool = True) -> bool:
    """에셋이 있는 패키지를 저장합니다."""
    return unreal.EditorAssetLibrary.save_asset(asset_to_save, only_if_is_dirty)


def save_directory(directory_path: str, only_if_is_dirty: bool = True, recursive: bool = True) -> bool:
    """디렉토리 내부에 있는 에셋들이 포함된 패키지를 저장합니다."""
    return unreal.EditorAssetLibrary.save_directory(directory_path, only_if_is_dirty, recursive)


def save_loaded_asset(asset_to_save: unreal.Object, only_if_is_dirty: bool = True) -> bool:
    """에셋이 있는 패키지를 저장합니다."""
    return unreal.EditorAssetLibrary.save_loaded_asset(asset_to_save, only_if_is_dirty)


def save_loaded_assets(assets_to_save, only_if_is_dirty=True):
    """에셋들이 있는 패키지들을 저장합니다."""
    return unreal.EditorAssetLibrary.save_loaded_assets(assets_to_save, only_if_is_dirty)


def set_metadata_tag(object, tag, value):
    """로드된 에셋의 메타데이터에서 주어진 태그와 연관된 값을 설정합니다."""
    return unreal.EditorAssetLibrary.set_metadata_tag(object, tag, value)


def sync_browser_to_objects(asset_paths):
    """연관된 에셋으로 이동하고 가장 최근에 사용된 콘텐츠 브라우저에서 선택합니다."""
    return unreal.EditorAssetLibrary.sync_browser_to_objects(asset_paths)