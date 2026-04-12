"""
언리얼 엔진 Python 피지컬 에셋 라이브러리 래퍼 모듈
=================================================

이 모듈은 언리얼 엔진 Python 피지컬 에셋 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonPhysicsAssetLib 함수들:
- unreal.PythonPhysicsAssetLib.function_name → phys_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 피지컬 에셋 라이브러리 래퍼들
# ===============================================================================

# 선택된 바디 관리
def get_selected_bodies_indexes(physics_asset: unreal.PhysicsAsset) -> List[int]:
    """피지컬 에셋 에디터에서 선택된 바디들의 인덱스를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_selected_bodies_indexes(physics_asset)


def rotate_selected_body(physics_asset: unreal.PhysicsAsset, rotation: unreal.Rotator) -> bool:
    """피지컬 에셋 에디터에서 선택된 바디의 회전을 설정합니다."""
    return unreal.PythonPhysicsAssetLib.rotate_selected_body(physics_asset, rotation)


def rotate_selected_constraint(physics_asset: unreal.PhysicsAsset, rotation: unreal.Rotator) -> bool:
    """피지컬 에셋 에디터에서 선택된 제약조건의 회전을 설정합니다."""
    return unreal.PythonPhysicsAssetLib.rotate_selected_constraint(physics_asset, rotation)


def get_selected(physics_asset: unreal.PhysicsAsset) -> bool:
    """선택된 항목 정보를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_selected(physics_asset)


# 바디 중심점 관리
def get_body_center(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[unreal.Vector]:
    """지정된 바디의 중심값을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_body_center(physics_asset, body_index)


def set_body_center(physics_asset: unreal.PhysicsAsset, body_index: int, center: unreal.Vector) -> bool:
    """지정된 바디의 중심값을 설정합니다."""
    return unreal.PythonPhysicsAssetLib.set_body_center(physics_asset, body_index, center)


# 바디 회전 관리
def get_body_rotation(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[unreal.Rotator]:
    """지정된 바디의 회전값을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_body_rotation(physics_asset, body_index)


def get_bodies_rotations(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[List[unreal.Rotator]]:
    """지정된 바디의 회전값들을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_bodies_rotations(physics_asset, body_index)


def set_body_rotation(physics_asset: unreal.PhysicsAsset, body_index: int, rotation: unreal.Rotator) -> bool:
    """지정된 바디의 회전값을 설정합니다."""
    return unreal.PythonPhysicsAssetLib.set_body_rotation(physics_asset, body_index, rotation)


# 바디 크기 관리 (반지름)
def get_body_radius(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[float]:
    """바디의 반지름 값을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_body_radius(physics_asset, body_index)


def set_body_radius(physics_asset: unreal.PhysicsAsset, body_index: int, radius: float) -> bool:
    """
    바디의 반지름 값을 설정합니다.
    구(Sphere)와 캡슐(Capsule) 바디를 지원합니다.
    """
    return unreal.PythonPhysicsAssetLib.set_body_radius(physics_asset, body_index, radius)


# 바디 크기 관리 (길이)
def get_body_length(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[float]:
    """캡슐 바디의 길이를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_body_length(physics_asset, body_index)


def set_body_length(physics_asset: unreal.PhysicsAsset, body_index: int, length: float) -> bool:
    """캡슐 바디의 길이를 설정합니다."""
    return unreal.PythonPhysicsAssetLib.set_body_length(physics_asset, body_index, length)


# 바디 크기 관리 (박스 크기)
def get_body_size(physics_asset: unreal.PhysicsAsset, body_index: int) -> Optional[unreal.Vector]:
    """박스 바디의 크기 값을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_body_size(physics_asset, body_index)


def set_body_size(physics_asset: unreal.PhysicsAsset, body_index: int, size: unreal.Vector) -> bool:
    """박스 바디의 크기 값을 설정합니다."""
    return unreal.PythonPhysicsAssetLib.set_body_size(physics_asset, body_index, size)


# 바디 스케일링
def scale_body(physics_asset: unreal.PhysicsAsset, body_index: int, scale: float) -> bool:
    """
    지정된 바디를 스케일링합니다.
    구(Sphere), 캡슐(Capsule), 박스(Box) 바디를 지원합니다.
    """
    return unreal.PythonPhysicsAssetLib.scale_body(physics_asset, body_index, scale)


# 피지컬 에셋 에디터 관리
def get_edited_physics_assets() -> List[unreal.PhysicsAsset]:
    """현재 열린 에디터로 추적되고 있는 모든 피지컬 에셋을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_edited_physics_assets()


def get_physics_asset_from_top_window() -> unreal.PhysicsAsset:
    """
    상단 열린 에디터 창에서 피지컬 에셋을 가져옵니다.
    
    Note:
        피지컬 에셋 에디터 창이 도킹된 경우 null을 반환합니다.
    """
    return unreal.PythonPhysicsAssetLib.get_physics_asset_from_top_window()


def log_selected(physics_asset: unreal.PhysicsAsset) -> None:
    """선택된 항목을 로그로 출력합니다."""
    return unreal.PythonPhysicsAssetLib.log_selected(physics_asset)


# 선택 관리
def get_selected_item_names(physics_asset: unreal.PhysicsAsset) -> List[unreal.Name]:
    """피지컬 에셋 에디터 창에서 선택된 모든 항목의 이름을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_selected_item_names(physics_asset)


def select_body_by_name(physics_asset: unreal.PhysicsAsset, name_in: unreal.Name) -> bool:
    """피지컬 에셋 에디터 창에서 이름으로 바디를 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_body_by_name(physics_asset, name_in)


def select_body_by_names(physics_asset: unreal.PhysicsAsset, names: List[unreal.Name]) -> bool:
    """피지컬 에셋 에디터 창에서 이름들로 바디들을 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_body_by_names(physics_asset, names)


def select_shape_by_name(physics_asset: unreal.PhysicsAsset, name_in: unreal.Name) -> bool:
    """피지컬 에셋 에디터 창에서 이름으로 형태를 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_shape_by_name(physics_asset, name_in)


def select_shape_by_names(physics_asset: unreal.PhysicsAsset, names: List[unreal.Name]) -> bool:
    """피지컬 에셋 에디터 창에서 이름들로 형태들을 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_shape_by_names(physics_asset, names)


def select_constraint_by_name(physics_asset: unreal.PhysicsAsset, name_in: unreal.Name) -> bool:
    """피지컬 에셋 에디터 창에서 이름으로 제약조건을 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_constraint_by_name(physics_asset, name_in)


def select_constraint_by_names(physics_asset: unreal.PhysicsAsset, names: List[unreal.Name]) -> bool:
    """피지컬 에셋 에디터 창에서 이름들로 제약조건들을 선택합니다."""
    return unreal.PythonPhysicsAssetLib.select_constraint_by_names(physics_asset, names)


# 제약조건 관리
def add_constraints(physics_asset: unreal.PhysicsAsset, parent_body_index: int, child_bodies_indexes: List[int]) -> List[unreal.Name]:
    """지정된 바디들에 제약조건을 추가합니다."""
    return unreal.PythonPhysicsAssetLib.add_constraints(physics_asset, parent_body_index, child_bodies_indexes)


# 계층구조 정보
def get_skeleton_hierarchy(physics_asset: unreal.PhysicsAsset) -> Tuple[List[unreal.Name], List[int]]:
    """본들의 계층구조를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_skeleton_hierarchy(physics_asset)


def get_bodies_hierarchy(physics_asset: unreal.PhysicsAsset) -> Tuple[List[unreal.Name], List[int]]:
    """모든 바디들의 이름과 그들의 부모 본의 인덱스를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_bodies_hierarchy(physics_asset)


def get_constraints_names(physics_asset: unreal.PhysicsAsset) -> List[unreal.Name]:
    """
    피지컬 에셋의 모든 제약조건의 표시 이름을 가져옵니다.
    
    Note:
        표시 이름 형식: "[ {parent_bone_name} -> {child_bone_name} ] Constraint"
    """
    return unreal.PythonPhysicsAssetLib.get_constraints_names(physics_asset)


def get_bone_indexes_of_constraint(physics_asset: unreal.PhysicsAsset, constraint_index: int) -> Tuple[int, int]:
    """지정된 제약조건의 부모와 자식 본의 인덱스를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_bone_indexes_of_constraint(physics_asset, constraint_index)


def get_bone_index_from_body(physics_asset: unreal.PhysicsAsset, body_index: int) -> int:
    """지정된 본 아래의 첫 번째 바디를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_bone_index_from_body(physics_asset, body_index)


def get_bodies_from_bone(physics_asset: unreal.PhysicsAsset, bone_index: int) -> List[int]:
    """지정된 본 아래의 바디들을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_bodies_from_bone(physics_asset, bone_index)


# 제약조건 인스턴스 관리
def get_constraint_instance_accessor(physics_asset: unreal.PhysicsAsset, constraint_index: int) -> unreal.ConstraintInstanceAccessor:
    """피지컬 에셋에서 ConstraintInstanceAccessor를 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_constraint_instance_accessor(physics_asset, constraint_index)


def reset_constraint_properties(physics_asset: unreal.PhysicsAsset, constraint_index: int) -> None:
    """지정된 제약조건의 값들을 리셋합니다."""
    return unreal.PythonPhysicsAssetLib.reset_constraint_properties(physics_asset, constraint_index)


def update_profile_instance(physics_asset: unreal.PhysicsAsset, constraint_index: int) -> None:
    """지정된 제약조건에 따라 프로파일을 업데이트합니다."""
    return unreal.PythonPhysicsAssetLib.update_profile_instance(physics_asset, constraint_index)


def break_constraint_accessor(accessor: unreal.ConstraintInstanceAccessor) -> Optional[Tuple[unreal.Object, int]]:
    """
    ConstraintInstanceAccessor에서 소유자와 제약조건 인덱스를 가져옵니다. (UE5 필요)
    
    Returns:
        None 또는 (소유자, 제약조건 인덱스) 튜플
    """
    return unreal.PythonPhysicsAssetLib.break_constraint_accessor(accessor)


def get_constraint_name(physics_asset: unreal.PhysicsAsset, constraint_index: int) -> unreal.Name:
    """제약조건 인덱스로 제약조건의 이름을 가져옵니다."""
    return unreal.PythonPhysicsAssetLib.get_constraint_name(physics_asset, constraint_index)