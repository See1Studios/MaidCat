"""
언리얼 엔진 에셋 툴즈 라이브러리 래퍼 모듈
=====================================

이 모듈은 언리얼 엔진 에셋 툴즈 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

AssetTools 함수들:
- unreal.AssetTools.function_name → assettool.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# AssetTools 인스턴스를 가져오는 헬퍼 함수
def _get_asset_tools():
    """AssetTools 인스턴스를 가져옵니다."""
    return unreal.AssetToolsHelpers.get_asset_tools()


# ===============================================================================
# 에셋 툴즈 라이브러리 래퍼들
# ===============================================================================

# 에셋 생성 및 복제
def create_asset(asset_name: str, package_path: str, asset_class: Any, factory: Any, calling_context: Any = None) -> Optional[unreal.Object]:
    """지정된 이름, 경로 및 팩토리로 에셋을 생성합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.create_asset(asset_name, package_path, asset_class, factory, calling_context)


def create_asset_with_dialog(asset_name: str, package_path: str, asset_class: Any, factory: Any, calling_context: Any = None, call_configure_properties: bool = True) -> Optional[unreal.Object]:
    """에셋 피커 다이얼로그를 열고 지정된 이름과 경로로 에셋을 생성합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.create_asset_with_dialog(asset_name, package_path, asset_class, factory, calling_context, call_configure_properties)


def create_unique_asset_name(base_package_name: str, suffix: str) -> Tuple[str, str]:
    """InBasePackageName+InSuffix 형태의 고유한 패키지 및 에셋 이름을 생성합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.create_unique_asset_name(base_package_name, suffix)


def duplicate_asset(asset_name: str, package_path: str, original_object: unreal.Object) -> Optional[unreal.Object]:
    """지정된 이름과 경로로 에셋을 생성합니다. OriginalObject를 복제 소스로 사용합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.duplicate_asset(asset_name, package_path, original_object)


def duplicate_asset_with_dialog(asset_name: str, package_path: str, original_object: unreal.Object) -> Optional[unreal.Object]:
    """에셋 피커 다이얼로그를 열고 지정된 이름과 경로로 에셋을 생성합니다. OriginalObject를 복제 소스로 사용합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.duplicate_asset_with_dialog(asset_name, package_path, original_object)


def duplicate_asset_with_dialog_and_title(asset_name: str, package_path: str, original_object: unreal.Object, dialog_title: Any) -> Optional[unreal.Object]:
    """에셋 피커 다이얼로그를 열고 지정된 이름과 경로로 에셋을 생성합니다. DialogTitle을 다이얼로그 제목으로 사용합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.duplicate_asset_with_dialog_and_title(asset_name, package_path, original_object, dialog_title)


# 에셋 가져오기 및 내보내기
def import_asset_tasks(import_tasks: Any) -> None:
    """지정된 작업을 사용하여 에셋을 가져옵니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.import_asset_tasks(import_tasks)


def import_assets_automated(import_data: Any) -> Any:
    """미리 완전히 지정된 데이터를 사용하여 에셋을 가져옵니다. 사용자에게 질문하거나 모달 오류 메시지를 표시하지 않습니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.import_assets_automated(import_data)


def import_assets_with_dialog(destination_path: str) -> Any:
    """파일 열기 다이얼로그를 열어 대상 경로로 가져올 파일을 선택합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.import_assets_with_dialog(destination_path)


def export_assets(assets_to_export: Any, export_path: str) -> None:
    """지정된 오브젝트들을 파일로 내보냅니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.export_assets(assets_to_export, export_path)


def export_assets_with_dialog(assets_to_export: Any, prompt_for_individual_filenames: bool) -> None:
    """지정된 오브젝트들을 파일로 내보냅니다. 먼저 사용자에게 내보내기 디렉토리를 선택하도록 하고 선택적으로 파일별 고유 디렉토리를 선택하도록 합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.export_assets_with_dialog(assets_to_export, prompt_for_individual_filenames)


# 에셋 이름 변경 및 관리
def rename_assets(assets_and_names: Any) -> bool:
    """지정된 이름을 사용하여 에셋의 이름을 변경합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.rename_assets(assets_and_names)


def rename_assets_with_dialog(assets_and_names: Any, auto_checkout: bool = False) -> Any:
    """지정된 이름을 사용하여 에셋의 이름을 변경합니다 (다이얼로그 포함)."""
    asset_tools = _get_asset_tools()
    return asset_tools.rename_assets_with_dialog(assets_and_names, auto_checkout)


def rename_referencing_soft_object_paths(packages_to_check: Any, asset_redirector_map: Any) -> None:
    """이전 에셋 경로를 가진 모든 FSoftObjectPath 오브젝트의 이름을 새 경로로 변경합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.rename_referencing_soft_object_paths(packages_to_check, asset_redirector_map)


# 에셋 유틸리티 및 분석
def is_asset_read_only(asset_data: Any) -> bool:
    """에셋이 편집을 위해 읽기 전용으로 간주되는지 플래그와 현재 권한에 따라 결정합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.is_asset_read_only(asset_data)


def find_soft_references_to_object(target_object: Any) -> Any:
    """주어진 소프트 오브젝트 경로를 소프트 참조하는 오브젝트 목록을 반환합니다. 검증을 위해 에셋을 메모리에 로드합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.find_soft_references_to_object(target_object)


def open_editor_for_assets(assets: Any) -> None:
    """에셋용 에디터를 엽니다 (더 이상 사용되지 않음: UAssetEditorSubsystem::OpenEditorForAssets을 대신 사용하세요)."""
    asset_tools = _get_asset_tools()
    return asset_tools.open_editor_for_assets(assets)


# 에셋 비교 및 차이점 분석
def diff_against_depot(object: unreal.Object, package_path: str, package_name: str) -> None:
    """에셋의 로컬 버전을 데포의 최신 버전과 비교하려고 시도합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.diff_against_depot(object, package_path, package_name)


def diff_assets(old_asset: unreal.Object, new_asset: unreal.Object, old_revision: Any, new_revision: Any) -> None:
    """클래스별 도구를 사용하여 두 에셋의 차이점을 비교하려고 시도합니다. 에셋이 NULL이거나 같은 클래스가 아닌 경우 아무것도 하지 않습니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.diff_assets(old_asset, new_asset, old_revision, new_revision)


# 패키지 관리
def begin_advanced_copy_packages(input_names_to_copy: Any, target_path: str, on_copy_complete: Any) -> None:
    """고급 패키지 복사를 시작합니다."""
    asset_tools = _get_asset_tools()
    return asset_tools.begin_advanced_copy_packages(input_names_to_copy, target_path, on_copy_complete)


def migrate_packages(package_names_to_migrate: Any, destination_path: str, options: Any = None) -> None:
    """패키지와 종속성을 다른 폴더로 이전합니다."""
    asset_tools = _get_asset_tools()
    if options is None:
        # 기본 옵션 설정
        options = [False, False, unreal.AssetMigrationConflict.SKIP, '']
    return asset_tools.migrate_packages(package_names_to_migrate, destination_path, options)