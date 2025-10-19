# /Content/Python/mesh_slicer_tool.py

import unreal
import math

# ----------------------------------------------------------------------------------
# 설정값 (필요에 따라 수정)
# ----------------------------------------------------------------------------------
SLICE_HEIGHT_FROM_BOTTOM = 50.0  # 메시 최하단으로부터 자를 높이
NEW_MATERIAL_SLOT_NAME = "CapMaterial" # 단면에 적용될 머티리얼 슬롯 이름
CAP_VERTEX_COLOR = unreal.LinearColor(1.0, 0.0, 0.0, 1.0)  # 단면 버텍스 컬러 (빨간색)
NEW_UV_CHANNEL = 1 # 단면 UV를 저장할 UV 채널
# ----------------------------------------------------------------------------------

def slice_static_mesh_at_height():
    """
    현재 스태틱 메시 에디터에 열려있는 메시를 지정된 높이에서 자르고,
    단면 생성, 머티리얼 할당, 버텍스 컬러 및 UV를 추가합니다.
    """
    # 에디터 유틸리티 및 서브시스템 가져오기
    editor_utility = unreal.EditorUtilityLibrary()
    asset_editor_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    geo_script_lib = unreal.GeometryScriptLibrary_StaticMeshFunctions
    mesh_query_lib = unreal.GeometryScriptLibrary_MeshQueryFunctions
    mesh_mod_lib = unreal.GeometryScriptLibrary_MeshModificationFunctions
    mesh_uv_lib = unreal.GeometryScriptLibrary_MeshUVFunctions
    
    # 현재 열려있는 애셋(스태틱 메시) 가져오기
    current_asset = asset_editor_subsystem.get_focused_asset()
    if not isinstance(current_asset, unreal.StaticMesh):
        unreal.log_error("활성화된 애셋이 스태틱 메시가 아닙니다.")
        return

    static_mesh = current_asset
    unreal.log(f"선택된 스태틱 메시: {static_mesh.get_name()}")

    # 1. 스태틱 메시를 다이내믹 메시로 복사
    # 옵션을 설정하여 모든 속성을 그대로 가져옵니다.
    copy_options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    copy_options.set_editor_property('b_request_vertex_colors', True)
    copy_options.set_editor_property('b_request_vertex_normals', True)
    copy_options.set_editor_property('b_request_uvs', True)
    
    dynamic_mesh = unreal.DynamicMesh()
    geo_script_lib.copy_mesh_from_static_mesh(static_mesh, dynamic_mesh, copy_options)

    # 2. 절단 위치 계산
    bounding_box = mesh_query_lib.get_local_mesh_bounding_box(dynamic_mesh)
    slice_z = bounding_box.min.z + SLICE_HEIGHT_FROM_BOTTOM
    
    plane_origin = unreal.Vector(0, 0, slice_z)
    plane_normal = unreal.Vector(0, 0, 1)
    
    # 3. 메시 절단 및 단면(Cap) 생성
    slice_options = unreal.GeometryScriptPlaneCutOptions()
    slice_options.set_editor_property('b_create_new_section_for_cap', True)
    slice_options.set_editor_property('b_fill_hole', True)
    
    mesh_mod_lib.apply_plane_slice(dynamic_mesh, plane_origin, plane_normal, slice_options)

    # 4. 단면에 데이터 추가
    # 단면의 폴리곤 그룹 ID는 가장 마지막에 생성된 ID 입니다.
    poly_group_info = mesh_query_lib.get_poly_group_info(dynamic_mesh)
    cap_polygroup_id = len(poly_group_info.groups) -1

    # 4-1. 새 머티리얼 슬롯 할당
    # 기존 머티리얼 슬롯 개수가 새 머티리얼 ID가 됩니다.
    mat_names = static_mesh.get_material_slot_names()
    new_material_id = len(mat_names)
    mesh_mod_lib.assign_material_id_to_poly_group(dynamic_mesh, cap_polygroup_id, new_material_id)

    # 4-2. 단면 버텍스 컬러 설정
    mesh_mod_lib.enable_vertex_colors(dynamic_mesh)
    result, cap_triangles = mesh_query_lib.get_triangles_in_poly_group(dynamic_mesh, cap_polygroup_id)
    
    vertex_indices_to_color = set()
    for tri in cap_triangles:
        vertex_indices_to_color.add(tri.x)
        vertex_indices_to_color.add(tri.y)
        vertex_indices_to_color.add(tri.z)
        
    for vert_id in list(vertex_indices_to_color):
        mesh_mod_lib.set_vertex_color(dynamic_mesh, vert_id, CAP_VERTEX_COLOR)

    # 4-3. 단면 UV 설정
    uv_options = unreal.GeometryScriptPlanarProjectionUVOptions()
    plane = unreal.Transform(plane_origin, plane_normal.to_vector_rotation())
    mesh_uv_lib.set_poly_group_planar_uvs(dynamic_mesh, cap_polygroup_id, NEW_UV_CHANNEL, plane, uv_options)

    # 5. 새 스태틱 메시 애셋으로 저장
    new_asset_path = static_mesh.get_path_name().replace(".","-sliced.")
    
    create_options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    create_options.set_editor_property('b_overwrite_if_exists', True)
    create_options.set_editor_property('b_enable_vertex_colors', True)
    create_options.set_editor_property('num_uv_channels', NEW_UV_CHANNEL + 1)
    
    # 새 머티리얼 슬롯 이름 설정
    new_slot_names = [unreal.Name(n) for n in mat_names]
    new_slot_names.append(unreal.Name(NEW_MATERIAL_SLOT_NAME))
    create_options.set_editor_property('material_slot_names', new_slot_names)

    geo_script_lib.create_new_static_mesh_asset_from_mesh(dynamic_mesh, new_asset_path, create_options)
    unreal.log(f"성공! 새 스태틱 메시가 다음 경로에 저장되었습니다: {new_asset_path}")

# 이 파일이 직접 실행될 때 테스트용으로 함수를 호출할 수 있습니다.
if __name__ == "__main__":
    slice_static_mesh_at_height()