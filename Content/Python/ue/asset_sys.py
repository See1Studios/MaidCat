"""
언리얼 엔진 에디터 에셋 서브시스템 라이브러리 래퍼 모듈
===============================================

이 모듈은 언리얼 엔진 에디터 에셋 서브시스템 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorAssetSubsystem 함수들:
- unreal.EditorSubsystem.get().function_name → asset_sys.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# EditorAssetSubsystem 인스턴스를 가져오는 헬퍼 함수
def _get_editor_asset_subsystem() -> unreal.EditorAssetSubsystem:
    """EditorAssetSubsystem 인스턴스를 가져옵니다."""
    return unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


# ===============================================================================
# 에디터 에셋 서브시스템 래퍼들
# ===============================================================================

# 에셋 체크아웃 및 소스 컨트롤
def checkout_asset(asset_to_checkout: str) -> bool:
    """에셋을 체크아웃합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.checkout_asset(asset_to_checkout)


def checkout_directory(directory_path: str, recursive: bool = True) -> bool:
    """디렉토리의 모든 에셋을 체크아웃합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.checkout_directory(directory_path, recursive)


def checkout_loaded_asset(asset_to_checkout: unreal.Object) -> bool:
    """오브젝트에 해당하는 에셋을 체크아웃합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.checkout_loaded_asset(asset_to_checkout)


def checkout_loaded_assets(assets_to_checkout: Any) -> bool:
    """에셋들을 체크아웃합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.checkout_loaded_assets(assets_to_checkout)


# 에셋 삭제
def delete_asset(asset_path_to_delete: str) -> bool:
    """에셋이 포함된 패키지를 삭제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.delete_asset(asset_path_to_delete)


def delete_directory(directory_path: str) -> bool:
    """디렉토리 내부의 패키지들을 삭제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.delete_directory(directory_path)


def delete_loaded_asset(asset_to_delete: unreal.Object) -> bool:
    """이미 로드된 에셋을 삭제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.delete_loaded_asset(asset_to_delete)


def delete_loaded_assets(assets_to_delete: Any) -> bool:
    """이미 로드된 에셋들을 삭제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.delete_loaded_assets(assets_to_delete)


# 에셋 존재 여부 확인
def does_asset_exist(asset_path: str) -> bool:
    """에셋 레지스트리에서 에셋이 존재하는지 확인합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.does_asset_exist(asset_path)


def do_assets_exist(asset_paths: Any) -> bool:
    """에셋 레지스트리에서 에셋들이 존재하는지 확인합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.do_assets_exist(asset_paths)


def does_directory_exist(directory_path: str) -> bool:
    """디렉토리가 존재하는지 확인합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.does_directory_exist(directory_path)


def does_directory_contain_assets(directory_path: str, recursive: bool = True) -> bool:
    """디렉토리에 에셋이 포함되어 있는지 확인합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.does_directory_contain_assets(directory_path, recursive)


# 에셋 복제
def duplicate_asset(source_asset_path: str, destination_asset_path: str) -> Optional[unreal.Object]:
    """에셋을 복제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.duplicate_asset(source_asset_path, destination_asset_path)


def duplicate_directory(source_directory_path: str, destination_directory_path: str) -> bool:
    """디렉토리와 그 안의 에셋들을 복제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.duplicate_directory(source_directory_path, destination_directory_path)


def duplicate_loaded_asset(source_asset: unreal.Object, destination_asset_path: str) -> Optional[unreal.Object]:
    """이미 로드된 에셋을 복제합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.duplicate_loaded_asset(source_asset, destination_asset_path)


# 에셋 통합
def consolidate_assets(asset_to_consolidate_to: unreal.Object, assets_to_consolidate: Any) -> bool:
    """제공된 AssetsToConsolidate의 모든 참조/사용을 AssetToConsolidateTo에 대한 참조로 대체하여 에셋을 통합합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.consolidate_assets(asset_to_consolidate_to, assets_to_consolidate)


# 에셋 찾기 및 정보 조회
def find_asset_data(asset_path: str) -> Any:
    """AssetRegistryHelpers와 함께 사용할 수 있는 에셋의 AssetData를 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.find_asset_data(asset_path)


def find_package_referencers_for_asset(asset_path: str, load_assets_to_confirm: bool = False) -> Any:
    """에셋의 패키지 참조자들을 찾습니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.find_package_referencers_for_asset(asset_path, load_assets_to_confirm)


def get_path_name_for_loaded_asset(loaded_asset: unreal.Object) -> str:
    """로드된 에셋에 대한 유효한 AssetPath를 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_path_name_for_loaded_asset(loaded_asset)


# 에셋 메타데이터 관리
def get_metadata_tag(object: unreal.Object, tag: Any) -> str:
    """로드된 에셋의 메타데이터에서 주어진 태그와 연관된 값을 가져옵니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_metadata_tag(object, tag)


def get_metadata_tag_values(object: unreal.Object) -> Any:
    """로드된 에셋의 메타데이터의 모든 태그/값을 가져옵니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_metadata_tag_values(object)


def set_metadata_tag(object: unreal.Object, tag: Any, value: str) -> None:
    """로드된 에셋의 메타데이터에서 주어진 태그와 연관된 값을 설정합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.set_metadata_tag(object, tag, value)


def remove_metadata_tag(object: unreal.Object, tag: Any) -> None:
    """로드된 에셋의 메타데이터에서 주어진 태그를 제거합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.remove_metadata_tag(object, tag)


def get_tag_values(asset_path: str) -> Any:
    """(로드되지 않은) 에셋과 연관된 모든 TagValues를 Asset Registry에서 문자열 값으로 가져옵니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_tag_values(asset_path)


# 에셋 목록 및 검색
def list_assets(directory_path: str, recursive: bool = True, include_folder: bool = False) -> Any:
    """DirectoryPath에서 찾은 모든 에셋들의 목록을 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.list_assets(directory_path, recursive, include_folder)


def list_assets_by_tag_value(tag_name: Any, tag_value: str) -> Any:
    """Tag/Value 쌍을 가진 모든 에셋들의 목록을 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.list_assets_by_tag_value(tag_name, tag_value)


def get_all_assets_by_meta_data_tags(required_tags: Any, allowed_classes: Any) -> Any:
    """주어진 태그를 가진 모든 에셋을 가져옵니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_all_assets_by_meta_data_tags(required_tags, allowed_classes)


# 에셋 로드
def load_asset(asset_path: str) -> Optional[unreal.Object]:
    """에셋을 로드합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.load_asset(asset_path)


def load_blueprint_class(asset_path: str) -> Optional[type]:
    """블루프린트 에셋을 로드하고 생성된 클래스를 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.load_blueprint_class(asset_path)


# 디렉토리 관리
def make_directory(directory_path: str) -> bool:
    """디스크에 디렉토리를 생성합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.make_directory(directory_path)


# 에셋 이름 변경
def rename_asset(source_asset_path: str, destination_asset_path: str) -> bool:
    """에셋의 이름을 변경합니다. 이동 작업과 동일합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.rename_asset(source_asset_path, destination_asset_path)


def rename_directory(source_directory_path: str, destination_directory_path: str) -> bool:
    """디렉토리의 이름을 변경합니다. 포함된 모든 에셋을 이동하는 이동 작업과 동일합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.rename_directory(source_directory_path, destination_directory_path)


def rename_loaded_asset(source_asset: unreal.Object, destination_asset_path: str) -> bool:
    """이미 로드된 에셋의 이름을 변경합니다. 이동 작업과 동일합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.rename_loaded_asset(source_asset, destination_asset_path)


# 에셋 저장
def save_asset(asset_to_save: str, only_if_is_dirty: bool = True) -> bool:
    """에셋이 있는 패키지를 저장합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.save_asset(asset_to_save, only_if_is_dirty)


def save_directory(directory_path: str, only_if_is_dirty: bool = True, recursive: bool = True) -> bool:
    """디렉토리 내부에 있는 에셋들이 포함된 패키지를 저장합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.save_directory(directory_path, only_if_is_dirty, recursive)


def save_loaded_asset(asset_to_save: unreal.Object, only_if_is_dirty: bool = True) -> bool:
    """에셋이 있는 패키지를 저장합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.save_loaded_asset(asset_to_save, only_if_is_dirty)


def save_loaded_assets(assets_to_save: Any, only_if_is_dirty: bool = True) -> bool:
    """에셋들이 있는 패키지들을 저장합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.save_loaded_assets(assets_to_save, only_if_is_dirty)


# 에셋 상태 관리
def set_dirty_flag(object: unreal.Object, dirty_state: bool) -> bool:
    """에셋의 패키지 더티 플래그를 설정합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.set_dirty_flag(object, dirty_state)


# 고급 기능
def get_asset_filename_length_for_cooking(asset_path: str) -> int:
    """계산된 쿠킹용 패키지 이름과 경로의 길이를 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_asset_filename_length_for_cooking(asset_path)


def get_loaded_asset_filename_length_for_cooking(asset: unreal.Object) -> int:
    """계산된 쿠킹용 패키지 이름과 경로의 길이를 반환합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.get_loaded_asset_filename_length_for_cooking(asset)


def sort_by_meta_data(assets: Any, meta_data_tag: Any, meta_data_type: Any, sort_order: Any) -> Optional[Any]:
    """메타데이터 타입에 따라 에셋을 정렬합니다. 지원되는 타입: FString, int, float, FDateTime."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.sort_by_meta_data(assets, meta_data_tag, meta_data_type, sort_order)


# 콜백 관리
def add_on_extract_asset_from_file(delegate: Any) -> None:
    """파일에서 에셋을 추출하는 콜백을 추가합니다 (예: 드래그 앤 드롭 작업)."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.add_on_extract_asset_from_file(delegate)


def remove_on_extract_asset_from_file(delegate: Any) -> None:
    """AddOnExtractAssetFromFile로 추가된 콜백을 제거합니다."""
    subsystem = _get_editor_asset_subsystem()
    return subsystem.remove_on_extract_asset_from_file(delegate)