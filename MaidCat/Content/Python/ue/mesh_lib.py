"""
언리얼 엔진 Python 메시 라이브러리 래퍼 모듈
============================================

이 모듈은 언리얼 엔진 Python 메시 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonMeshLib 함수들:
- unreal.PythonMeshLib.function_name → mesh_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 메시 라이브러리 래퍼들
# ===============================================================================

# 스태틱 메시 머티리얼 관리
def get_static_mesh_materials(mesh: unreal.StaticMesh) -> List[unreal.StaticMaterial]:
    """스태틱 메시의 모든 스태틱 머티리얼을 가져옵니다."""
    return unreal.PythonMeshLib.get_static_mesh_materials(mesh)


def set_static_mesh_materials(mesh: unreal.StaticMesh, materials: List[unreal.StaticMaterial], slot_names: List[unreal.Name]) -> None:
    """스태틱 메시의 모든 스태틱 머티리얼을 설정합니다."""
    return unreal.PythonMeshLib.set_static_mesh_materials(mesh, materials, slot_names)


def get_imported_original_mat_names(mesh: unreal.StaticMesh) -> Optional[List[str]]:
    """스태틱 메시의 ImportData에서 Mesh의 ImportMaterialOriginalNameData 이름들을 가져옵니다."""
    return unreal.PythonMeshLib.get_imported_original_mat_names(mesh)


# LOD 관리
def get_original_lod_data_count(mesh: unreal.StaticMesh) -> int:
    """ImportMeshData에서 LOD 수를 가져옵니다."""
    return unreal.PythonMeshLib.get_original_lod_data_count(mesh)


def get_original_lod_mat_names(mesh: unreal.StaticMesh, lod_level: int) -> Optional[List[str]]:
    """지정된 LOD의 섹션 원본 머티리얼 이름들을 가져옵니다."""
    return unreal.PythonMeshLib.get_original_lod_mat_names(mesh, lod_level)


def is_this_lod_generated_by_mesh_reduction(mesh: unreal.StaticMesh, lod_level: int) -> bool:
    """지정된 LOD가 에디터에서 생성되었는지 확인합니다."""
    return unreal.PythonMeshLib.is_this_lod_generated_by_mesh_reduction(mesh, lod_level)


def set_lod_section_material_slot_index(static_mesh: unreal.StaticMesh, lod_index: int, section_index: int, new_material_slot_index: int, new_material_slot_name: unreal.Name) -> None:
    """지정된 메시 LOD의 머티리얼 슬롯 인덱스를 설정합니다."""
    return unreal.PythonMeshLib.set_lod_section_material_slot_index(static_mesh, lod_index, section_index, new_material_slot_index, new_material_slot_name)


def get_section_cast_shadow(static_mesh: unreal.StaticMesh, lod_level: int, section_id: int) -> bool:
    """LOD의 지정된 섹션이 그림자를 생성하는지 확인합니다."""
    return unreal.PythonMeshLib.get_section_cast_shadow(static_mesh, lod_level, section_id)


# 계층적 인스턴스드 스태틱 메시 컴포넌트
def get_overlapping_box_count(hism: unreal.HierarchicalInstancedStaticMeshComponent, box: unreal.Box) -> int:
    """주어진 박스와 겹치는 인스턴스의 수를 가져옵니다."""
    return unreal.PythonMeshLib.get_overlapping_box_count(hism, box)


def get_overlapping_sphere_count(hism: unreal.HierarchicalInstancedStaticMeshComponent, sphere_center: unreal.Vector, sphere_radius: float) -> int:
    """주어진 구와 겹치는 인스턴스의 수를 가져옵니다."""
    return unreal.PythonMeshLib.get_overlapping_sphere_count(hism, sphere_center, sphere_radius)


# 스태틱 메시 소켓 관리
def get_static_mesh_sockets(obj: unreal.Object) -> List[unreal.StaticMeshSocket]:
    """메시 오브젝트의 스태틱 메시 소켓들을 가져옵니다."""
    return unreal.PythonMeshLib.get_static_mesh_sockets(obj)


def set_static_mesh_sockets(obj: unreal.Object, sockets: List[unreal.StaticMeshSocket]) -> bool:
    """메시 오브젝트의 스태틱 메시 소켓들을 설정합니다."""
    return unreal.PythonMeshLib.set_static_mesh_sockets(obj, sockets)


def set_static_mesh_socket_name(socket: unreal.StaticMeshSocket, socket_name: unreal.Name) -> unreal.StaticMeshSocket:
    """스태틱 메시 소켓의 이름을 설정합니다."""
    return unreal.PythonMeshLib.set_static_mesh_socket_name(socket, socket_name)


# 절차적 메시 변환
def convert_procedural_mesh_to_static_mesh(
    proc_mesh_comp: unreal.ProceduralMeshComponent, 
    package_path: str, 
    recompute_normals: bool = False, 
    recompute_tangents: bool = False, 
    remove_degenerates: bool = False, 
    use_high_precision_tangent_basis: bool = False, 
    use_full_precision_u_vs: bool = False, 
    generate_lightmap_u_vs: bool = True
) -> unreal.StaticMesh:
    """절차적 메시를 스태틱 메시 에셋으로 변환합니다."""
    return unreal.PythonMeshLib.convert_procedural_mesh_to_static_mesh(
        proc_mesh_comp, package_path, recompute_normals, recompute_tangents, 
        remove_degenerates, use_high_precision_tangent_basis, use_full_precision_u_vs, 
        generate_lightmap_u_vs
    )


# 나나이트 (UE5 전용)
def apply_nanite(static_mesh: unreal.StaticMesh, enable_nanite: bool) -> None:
    """스태틱 메시 에셋의 나나이트 활성화를 설정하고 적용합니다. (UE5 전용)"""
    return unreal.PythonMeshLib.apply_nanite(static_mesh, enable_nanite)


# 다이나믹 메시 - UV 및 카메라 프로젝션 (UE 5.1+)
def set_uvs_from_camera_projection(target_mesh: unreal.DynamicMesh, uv_set_index: int, selection: Any, m: unreal.Matrix, view_info: unreal.MinimalViewInfo) -> unreal.DynamicMesh:
    """현재 뷰에서 다이나믹 메시를 지정된 UV 세트에 프로젝션합니다."""
    return unreal.PythonMeshLib.set_uvs_from_camera_projection(target_mesh, uv_set_index, selection, m, view_info)


def get_visible_triangles(target_mesh: unreal.DynamicMesh, mesh_transform: unreal.Transform, view_info: unreal.MinimalViewInfo, invert: bool) -> Tuple[unreal.DynamicMesh, Any]:
    """현재 뷰에서 다이나믹 메시의 보이는 삼각형들을 가져옵니다."""
    return unreal.PythonMeshLib.get_visible_triangles(target_mesh, mesh_transform, view_info, invert)


# 실험적 기능들 (UE 5.2+)
def rasterize_and_trace_triangles_uv(
    world: unreal.World,
    target_mesh: unreal.DynamicMesh,
    triangle_ids: List[int],
    uv_channel: int,
    texture_width: int,
    texture_height: int,
    transform: unreal.Transform,
    start_point: unreal.Vector,
    profile_name: unreal.Name,
    debug_draw: bool
) -> Tuple[List[Any], List[Any], List[int], List[int]]:
    """현재 뷰에서 다이나믹 메시의 가시성을 추적합니다. (실험적)"""
    return unreal.PythonMeshLib.rasterize_and_trace_triangles_uv(
        world, target_mesh, triangle_ids, uv_channel, texture_width, texture_height,
        transform, start_point, profile_name, debug_draw
    )


def trace_dynamic_mesh_triangles_visibility(
    target_mesh_component: unreal.DynamicMeshComponent,
    triangle_ids: List[int],
    view_info: unreal.MinimalViewInfo,
    debug_draw: bool,
    profile_name: unreal.Name
) -> Optional[Any]:
    """현재 뷰에서 다이나믹 메시의 삼각형 가시성을 추적합니다."""
    return unreal.PythonMeshLib.trace_dynamic_mesh_triangles_visibility(
        target_mesh_component, triangle_ids, view_info, debug_draw, profile_name
    )


def get_triangles_face_normal_in_view(
    target_mesh_component: unreal.DynamicMeshComponent,
    triangle_ids: List[int],
    view_info: unreal.MinimalViewInfo
) -> List[unreal.Vector]:
    """현재 뷰에서 다이나믹 메시의 면 법선을 가져옵니다. (실험적)"""
    return unreal.PythonMeshLib.get_triangles_face_normal_in_view(target_mesh_component, triangle_ids, view_info)


def cal_triangles_derivatives(
    mesh_component: unreal.DynamicMeshComponent,
    triangle_ids: List[int],
    uv_channel: int,
    view_info: unreal.MinimalViewInfo,
    view_size: unreal.Vector2D
) -> List[unreal.Vector2D]:
    """현재 뷰에서 다이나믹 메시의 삼각형들의 병합된 ddxy를 계산합니다. (실험적)"""
    return unreal.PythonMeshLib.cal_triangles_derivatives(mesh_component, triangle_ids, uv_channel, view_info, view_size)


def export_normal_and_derivatives(
    mesh_component: unreal.DynamicMeshComponent,
    triangle_ids: List[int],
    uv_channel: int,
    view_info: unreal.MinimalViewInfo,
    view_size: unreal.Vector2D,
    export_tex_size: int
) -> List[int]:
    """현재 뷰에서 다이나믹 메시의 현재 법선과 mip을 원시 데이터로 내보냅니다. (실험적)"""
    return unreal.PythonMeshLib.export_normal_and_derivatives(
        mesh_component, triangle_ids, uv_channel, view_info, view_size, export_tex_size
    )