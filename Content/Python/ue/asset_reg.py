"""
언리얼 엔진 에셋 레지스트리 라이브러리 래퍼 모듈
=========================================

이 모듈은 언리얼 엔진 에셋 레지스트리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

AssetRegistry 함수들:
- unreal.AssetRegistry.function_name → asset_reg.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# AssetRegistry 인스턴스를 가져오는 헬퍼 함수
def _get_asset_registry():
    """AssetRegistry 인스턴스를 가져옵니다."""
    return unreal.AssetRegistryHelpers.get_asset_registry()


# ===============================================================================
# 에셋 레지스트리 라이브러리 래퍼들
# ===============================================================================

# 에셋 검색 및 조회
def get_all_assets(include_only_on_disk_assets: bool = False) -> Optional[Any]:
    """레지스트리의 모든 에셋에 대한 에셋 데이터를 가져옵니다. 가능하면 필터를 사용하여 전체 레지스트리 반복을 피하세요."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_all_assets(include_only_on_disk_assets)


def get_assets(filter: Any, skip_ar_filtered_assets: bool = True) -> Optional[Any]:
    """필터와 일치하는 모든 에셋의 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_assets(filter, skip_ar_filtered_assets)


def get_assets_by_class(class_path_name: Any, search_sub_classes: bool = False) -> Optional[Any]:
    """지정된 클래스를 가진 모든 에셋의 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_assets_by_class(class_path_name, search_sub_classes)


def get_assets_by_package_name(package_name: Any, include_only_on_disk_assets: bool = False, skip_ar_filtered_assets: bool = True) -> Optional[Any]:
    """지정된 패키지 이름의 패키지에 있는 에셋들의 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_assets_by_package_name(package_name, include_only_on_disk_assets, skip_ar_filtered_assets)


def get_assets_by_path(package_path: Any, recursive: bool = False, include_only_on_disk_assets: bool = False) -> Optional[Any]:
    """지정된 폴더 경로의 모든 에셋에 대한 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_assets_by_path(package_path, recursive, include_only_on_disk_assets)


def get_assets_by_paths(package_paths: Any, recursive: bool = False, include_only_on_disk_assets: bool = False) -> Optional[Any]:
    """제공된 폴더 경로들 중 하나에 있는 모든 에셋의 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_assets_by_paths(package_paths, recursive, include_only_on_disk_assets)


def get_asset_by_object_path(object_path: Any, include_only_on_disk_assets: bool = False) -> Any:
    """오브젝트 경로로 에셋을 가져옵니다 (더 이상 사용되지 않음: SoftObjectPath를 받는 다른 버전을 사용하세요)."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_asset_by_object_path(object_path, include_only_on_disk_assets)


def k2_get_asset_by_object_path(object_path: Any, include_only_on_disk_assets: bool = False, skip_ar_filtered_assets: bool = True) -> Any:
    """지정된 오브젝트 경로의 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.k2_get_asset_by_object_path(object_path, include_only_on_disk_assets, skip_ar_filtered_assets)


def get_in_memory_assets(filter: Any, skip_ar_filtered_assets: bool = True) -> Optional[Any]:
    """메모리 내 에셋만 필터와 일치하는 에셋 데이터를 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_in_memory_assets(filter, skip_ar_filtered_assets)


# 경로 및 디렉토리 관리
def get_all_cached_paths() -> Any:
    """현재 캐시된 모든 경로의 목록을 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_all_cached_paths()


def get_sub_paths(base_path: str, recurse: bool) -> Any:
    """전달된 기본 경로 아래에 현재 캐시된 모든 경로의 목록을 가져옵니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_sub_paths(base_path, recurse)


def has_assets(package_path: Any, recursive: bool = False) -> bool:
    """주어진 경로에 에셋이 포함되어 있는지, 선택적으로 하위 경로도 테스트합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.has_assets(package_path, recursive)


# 종속성 및 참조 관리
def get_dependencies(package_name: Any, dependency_options: Any) -> Optional[Any]:
    """제공된 패키지에서 참조되는 오브젝트의 경로 목록을 가져옵니다. (디스크 참조만)"""
    asset_registry = _get_asset_registry()
    return asset_registry.get_dependencies(package_name, dependency_options)


def get_referencers(package_name: Any, reference_options: Any) -> Optional[Any]:
    """제공된 패키지를 참조하는 패키지 목록을 가져옵니다. (디스크 참조만)"""
    asset_registry = _get_asset_registry()
    return asset_registry.get_referencers(package_name, reference_options)


# 클래스 계층 관리
def get_ancestor_class_names(class_path_name: Any) -> Optional[Any]:
    """지정된 클래스 이름의 조상을 찾을 수 있으면 true를 반환합니다. 그렇다면 OutAncestorClassNames는 모든 조상의 목록입니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_ancestor_class_names(class_path_name)


def get_derived_class_names(class_names: Any, excluded_class_names: Any) -> Any:
    """제공된 클래스 이름에서 파생된 모든 클래스의 이름을 반환하며, 제외된 클래스 이름과 일치하는 클래스는 제외합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.get_derived_class_names(class_names, excluded_class_names)


# 에셋 스캔 및 검색
def scan_files_synchronous(file_paths: Any, force_rescan: bool = False) -> None:
    """지정된 개별 파일들을 지금 스캔하고 에셋 레지스트리를 채웁니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.scan_files_synchronous(file_paths, force_rescan)


def scan_modified_asset_files(file_paths: Any) -> None:
    """특정 파일명의 재스캔을 강제합니다. 디스크에서 새로 고침이 필요할 때 호출하세요."""
    asset_registry = _get_asset_registry()
    return asset_registry.scan_modified_asset_files(file_paths)


def scan_paths_synchronous(paths: Any, force_rescan: bool = False, ignore_deny_list_scan_filters: bool = False) -> None:
    """제공된 경로들을 재귀적으로 지금 스캔하고 에셋 레지스트리를 채웁니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.scan_paths_synchronous(paths, force_rescan, ignore_deny_list_scan_filters)


def search_all_assets(synchronous_search: bool) -> None:
    """디스크의 모든 에셋을 찾습니다 (비동기 또는 동기식 가능)."""
    asset_registry = _get_asset_registry()
    return asset_registry.search_all_assets(synchronous_search)


def prioritize_search_path(path_to_prioritize: str) -> None:
    """지정된 경로에서 에셋이 현재 비동기적으로 스캔되고 있다면, 다른 에셋들보다 먼저 스캔되도록 합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.prioritize_search_path(path_to_prioritize)


# 에셋 필터링
def run_assets_through_filter(asset_data_list: Any, filter: Any) -> Any:
    """제공된 필터를 통과하지 않는 항목들을 에셋 데이터 목록에서 제거합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.run_assets_through_filter(asset_data_list, filter)


def use_filter_to_exclude_assets(asset_data_list: Any, filter: Any) -> Any:
    """제공된 필터를 통과하는 항목들을 에셋 데이터 목록에서 제거합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.use_filter_to_exclude_assets(asset_data_list, filter)


# 상태 및 대기 함수
def is_loading_assets() -> bool:
    """에셋 레지스트리가 현재 파일을 로드 중이고 아직 모든 에셋에 대해 알지 못하면 true를 반환합니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.is_loading_assets()


def is_search_all_assets() -> bool:
    """SearchAllAssets가 호출되었거나 시작 시 자동 호출되었는지 여부입니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.is_search_all_assets()


def is_search_async() -> bool:
    """검색이 비동기적으로 (시작 시 시작) 수행되는지, 아니면 동기적이고 온디맨드로 수행되는지 여부입니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.is_search_async()


def wait_for_completion() -> None:
    """스캔이 완료될 때까지 기다립니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.wait_for_completion()


def wait_for_package(package_name: str) -> None:
    """특정 패키지의 스캔이 완료될 때까지 기다립니다."""
    asset_registry = _get_asset_registry()
    return asset_registry.wait_for_package(package_name)