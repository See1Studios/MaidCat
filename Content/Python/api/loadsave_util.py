"""
Unreal Engine EditorLoadingAndSavingUtils 래퍼 모듈

에디터에서 애셋과 패키지의 로딩 및 저장을 관리하는 유틸리티 함수들을 제공합니다.
EditorLoadingAndSavingUtils의 주요 기능을 한국어 문서와 함께 래핑합니다.

Author: MaidCat Team
"""

import unreal
from typing import List


def save_package(package_to_save: unreal.Package, only_if_is_dirty: bool = True) -> bool:
    """패키지를 디스크에 저장합니다.
    
    Args:
        package_to_save: 저장할 패키지
        only_if_is_dirty: True면 수정된 패키지만 저장, False면 무조건 저장
    
    Returns:
        저장 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.save_package(package_to_save, only_if_is_dirty)


def save_packages(packages_to_save: unreal.Array, only_if_is_dirty: bool = True) -> bool:
    """여러 패키지를 한번에 저장합니다.
    
    Args:
        packages_to_save: 저장할 패키지들의 배열
        only_if_is_dirty: True면 수정된 패키지만 저장, False면 무조건 저장
    
    Returns:
        모든 패키지 저장 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.save_packages(packages_to_save, only_if_is_dirty)


def save_dirty_packages(save_map_packages: bool = True, save_content_packages: bool = True) -> bool:
    """수정된 모든 패키지를 저장합니다.
    
    Args:
        save_map_packages: 맵 패키지 저장 여부
        save_content_packages: 콘텐츠 패키지 저장 여부
    
    Returns:
        저장 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.save_dirty_packages(save_map_packages, save_content_packages)


def save_dirty_packages_with_dialog(save_assets: bool = True, save_map_packages: bool = True) -> bool:
    """수정된 패키지들을 다이얼로그와 함께 저장합니다.
    
    Args:
        save_assets: 애셋 패키지 저장 여부
        save_map_packages: 맵 패키지 저장 여부
    
    Returns:
        저장 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.save_dirty_packages_with_dialog(save_assets, save_map_packages)


def save_current_level() -> bool:
    """현재 레벨을 저장합니다.
    
    Returns:
        저장 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.save_current_level()


def reload_packages(packages_to_reload: unreal.Array) -> tuple:
    """지정된 패키지들을 다시 로드합니다.
    
    Args:
        packages_to_reload: 다시 로드할 패키지들의 배열
    
    Returns:
        (성공 여부, 결과 메시지) 튜플
    """
    return unreal.EditorLoadingAndSavingUtils.reload_packages(packages_to_reload)


def load_map(map_name: str) -> bool:
    """지정된 맵을 로드합니다.
    
    Args:
        map_name: 로드할 맵의 이름 또는 경로
    
    Returns:
        맵 로드 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.load_map(map_name)


def new_map(template_path: str = "") -> bool:
    """새로운 맵을 생성합니다.
    
    Args:
        template_path: 템플릿 맵의 경로 (비어있으면 기본 템플릿 사용)
    
    Returns:
        새 맵 생성 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.new_map(template_path)


def new_map_from_template(template_path: str, save_existing_map: bool = True) -> bool:
    """템플릿에서 새로운 맵을 생성합니다.
    
    Args:
        template_path: 템플릿 맵의 경로
        save_existing_map: 기존 맵 저장 여부
    
    Returns:
        새 맵 생성 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.new_map_from_template(template_path, save_existing_map)


def export_scene(export_selected_actors_only: bool = False) -> None:
    """현재 씬을 파일로 내보냅니다.
    
    Args:
        export_selected_actors_only: 선택된 액터만 내보낼지 여부
    """
    unreal.EditorLoadingAndSavingUtils.export_scene(export_selected_actors_only)


def import_scene(import_path: str) -> None:
    """파일에서 씬을 가져옵니다.
    
    Args:
        import_path: 가져올 파일 경로
    """
    unreal.EditorLoadingAndSavingUtils.import_scene(import_path)


def force_delete_assets(object_paths: unreal.Array, show_confirmation: bool = True) -> bool:
    """지정된 애셋들을 강제로 삭제합니다.
    
    Args:
        object_paths: 삭제할 애셋 경로들의 배열
        show_confirmation: 삭제 확인 다이얼로그 표시 여부
    
    Returns:
        삭제 성공 여부
    """
    return unreal.EditorLoadingAndSavingUtils.force_delete_assets(object_paths, show_confirmation)


def unload_packages(packages_to_unload: unreal.Array) -> tuple:
    """지정된 패키지들을 언로드합니다.
    
    Args:
        packages_to_unload: 언로드할 패키지들의 배열
    
    Returns:
        (성공 여부, 결과 메시지) 튜플
    """
    return unreal.EditorLoadingAndSavingUtils.unload_packages(packages_to_unload)


def check_for_dirty_packages() -> bool:
    """수정된 패키지가 있는지 확인합니다.
    
    Returns:
        수정된 패키지가 있으면 True
    """
    return unreal.EditorLoadingAndSavingUtils.check_for_dirty_packages()


def get_dirty_map_packages() -> unreal.Array:
    """수정된 맵 패키지들을 가져옵니다.
    
    Returns:
        수정된 맵 패키지들의 배열
    """
    return unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()


def get_dirty_content_packages() -> unreal.Array:
    """수정된 콘텐츠 패키지들을 가져옵니다.
    
    Returns:
        수정된 콘텐츠 패키지들의 배열
    """
    return unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()


# 편의 함수들
def save_all() -> bool:
    """모든 수정된 패키지와 현재 레벨을 저장합니다.
    
    Returns:
        모든 저장 작업 성공 여부
    """
    success = True
    success &= save_current_level()
    success &= save_dirty_packages()
    return success


def has_unsaved_changes() -> bool:
    """저장되지 않은 변경사항이 있는지 확인합니다.
    
    Returns:
        저장되지 않은 변경사항이 있으면 True
    """
    return check_for_dirty_packages()


def count_dirty_packages() -> int:
    """수정된 패키지의 개수를 반환합니다.
    
    Returns:
        수정된 패키지 개수
    """
    dirty_maps = get_dirty_map_packages()
    dirty_content = get_dirty_content_packages()
    return len(dirty_maps) + len(dirty_content)


def list_dirty_packages() -> None:
    """수정된 패키지들의 이름을 출력합니다."""
    print("=== 수정된 패키지 목록 ===")
    
    dirty_maps = get_dirty_map_packages()
    if dirty_maps:
        print("📍 수정된 맵 패키지:")
        for pkg in dirty_maps:
            print(f"  - {pkg.get_name()}")
    
    dirty_content = get_dirty_content_packages()
    if dirty_content:
        print("📦 수정된 콘텐츠 패키지:")
        for pkg in dirty_content:
            print(f"  - {pkg.get_name()}")
    
    if not dirty_maps and not dirty_content:
        print("✅ 수정된 패키지가 없습니다.")