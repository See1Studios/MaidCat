"""
Smoothed Normal Baker
메시의 Smoothed Normal을 계산하여 Vertex Color 또는 UV 채널에 저장하는 도구

출력 모드:
  - VERTEX_COLOR: RGB 채널에 XYZ 노말 저장 (기본값)
  - UV_CHANNEL: 지정 UV 채널에 RG(XY)를 [-1,1] 그대로 저장, B(Z)는 셰이더에서 reconstruct
    - 셰이더 복원: float z = sqrt(1 - x*x - y*y)

버전: 1.2.0
날짜: 2026-03-11
"""

import unreal
from enum import Enum
from typing import Optional, List, Dict, Tuple
from collections import defaultdict


class OutputMode(Enum):
    """Smoothed Normal 출력 대상"""
    VERTEX_COLOR = "vertex_color"
    UV_CHANNEL = "uv_channel"


def get_dynamic_mesh() -> unreal.DynamicMesh:
    """새 DynamicMesh 인스턴스를 생성합니다."""
    # GeometryScriptMeshBasicEditFunctions을 사용하여 DynamicMesh 생성
    return unreal.DynamicMesh()


def copy_mesh_from_static_mesh(
    static_mesh: unreal.StaticMesh,
    lod_index: int = 0
) -> Optional[unreal.DynamicMesh]:
    """StaticMesh를 DynamicMesh로 복사합니다.

    Args:
        static_mesh: 원본 StaticMesh
        lod_index: 복사할 LOD 인덱스

    Returns:
        복사된 DynamicMesh 또는 실패 시 None
    """
    dynamic_mesh = get_dynamic_mesh()
    asset_options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    read_lod = unreal.GeometryScriptMeshReadLOD(
        lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,
        lod_index=lod_index
    )

    result, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(
        from_static_mesh_asset=static_mesh,
        to_dynamic_mesh=dynamic_mesh,
        asset_options=asset_options,
        requested_lod=read_lod
    )

    if outcome == unreal.GeometryScriptOutcomePins.FAILURE:
        unreal.log_error(f"StaticMesh 복사 실패: {static_mesh.get_name()}")
        return None
    return result


def copy_mesh_from_skeletal_mesh(
    skeletal_mesh: unreal.SkeletalMesh,
    lod_index: int = 0
) -> Optional[unreal.DynamicMesh]:
    """SkeletalMesh를 DynamicMesh로 복사합니다.

    Args:
        skeletal_mesh: 원본 SkeletalMesh
        lod_index: 복사할 LOD 인덱스

    Returns:
        복사된 DynamicMesh 또는 실패 시 None
    """
    dynamic_mesh = get_dynamic_mesh()
    asset_options = unreal.GeometryScriptCopyMeshFromAssetOptions()
    read_lod = unreal.GeometryScriptMeshReadLOD(
        lod_type=unreal.GeometryScriptLODType.SOURCE_MODEL,
        lod_index=lod_index
    )

    result, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
        from_skeletal_mesh_asset=skeletal_mesh,
        to_dynamic_mesh=dynamic_mesh,
        asset_options=asset_options,
        requested_lod=read_lod
    )

    if outcome == unreal.GeometryScriptOutcomePins.FAILURE:
        unreal.log_error(f"SkeletalMesh 복사 실패: {skeletal_mesh.get_name()}")
        return None
    return result


def copy_mesh_to_static_mesh(
    dynamic_mesh: unreal.DynamicMesh,
    static_mesh: unreal.StaticMesh,
    lod_index: int = 0
) -> bool:
    """DynamicMesh를 StaticMesh로 복사합니다.

    Args:
        dynamic_mesh: 원본 DynamicMesh
        static_mesh: 대상 StaticMesh
        lod_index: 저장할 LOD 인덱스

    Returns:
        성공 여부
    """
    to_asset_options = unreal.GeometryScriptCopyMeshToAssetOptions()
    # 노멀/탄젠트 재계산 방지 (저장된 버텍스 컬러를 보존하기 위함)
    to_asset_options.enable_recompute_normals = False
    to_asset_options.enable_recompute_tangents = False

    write_lod = unreal.GeometryScriptMeshWriteLOD(
        write_hi_res_source=False,
        lod_index=lod_index
    )

    result, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
        from_dynamic_mesh=dynamic_mesh,
        to_static_mesh_asset=static_mesh,
        options=to_asset_options,
        target_lod=write_lod
    )

    if outcome == unreal.GeometryScriptOutcomePins.FAILURE:
        unreal.log_error("StaticMesh 저장 실패")
        return False
    return True


def copy_mesh_to_skeletal_mesh(
    dynamic_mesh: unreal.DynamicMesh,
    skeletal_mesh: unreal.SkeletalMesh,
    lod_index: int = 0
) -> bool:
    """DynamicMesh를 SkeletalMesh로 복사합니다.

    Args:
        dynamic_mesh: 원본 DynamicMesh
        skeletal_mesh: 대상 SkeletalMesh
        lod_index: 저장할 LOD 인덱스

    Returns:
        성공 여부
    """
    to_asset_options = unreal.GeometryScriptCopyMeshToAssetOptions()
    to_asset_options.enable_recompute_normals = False
    to_asset_options.enable_recompute_tangents = False

    write_lod = unreal.GeometryScriptMeshWriteLOD(
        write_hi_res_source=False,
        lod_index=lod_index
    )

    result, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_to_skeletal_mesh(
        from_dynamic_mesh=dynamic_mesh,
        to_skeletal_mesh_asset=skeletal_mesh,
        options=to_asset_options,
        target_lod=write_lod
    )

    if outcome == unreal.GeometryScriptOutcomePins.FAILURE:
        unreal.log_error("SkeletalMesh 저장 실패")
        return False
    return True


def compute_smoothed_normals(
    positions: List[unreal.Vector],
    normals: List[unreal.Vector],
    threshold: float = 0.001
) -> List[unreal.Vector]:
    """동일 위치 버텍스들의 노멀을 평균내어 Smoothed Normal을 계산합니다.

    Args:
        positions: 버텍스 위치 리스트
        normals: 버텍스 노멀 리스트
        threshold: 동일 위치 판정 임계값 (cm)

    Returns:
        스무드된 노멀 리스트
    """
    if len(positions) != len(normals):
        unreal.log_error(f"위치/노멀 개수 불일치: {len(positions)} vs {len(normals)}")
        return normals

    # 위치별 노멀 그룹핑 (공간 해싱)
    # round()를 사용하여 버킷 경계에서 동일 위치가 분리되는 문제 방지
    # (int()를 사용하면 0.000999 → 0, 0.001001 → 1로 분리됨)
    position_to_normals: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)

    for i, pos in enumerate(positions):
        # 위치를 양자화하여 키 생성 (round로 가장 가까운 버킷 중심에 매핑)
        key = (
            round(pos.x / threshold),
            round(pos.y / threshold),
            round(pos.z / threshold)
        )
        position_to_normals[key].append(i)

    # 스무드된 노멀 계산 (각 원소가 독립 객체여야 함)
    smoothed_normals: List[unreal.Vector] = [unreal.Vector(0, 0, 0) for _ in range(len(normals))]

    for indices in position_to_normals.values():
        if len(indices) == 1:
            # 단독 버텍스는 원본 노멀 그대로 사용
            smoothed_normals[indices[0]] = normals[indices[0]]
            continue

        # 같은 위치의 버텍스를 노멀 방향 기준으로 클러스터링
        # (앞면/뒷면처럼 반대 방향 노멀이 상쇄되는 것을 방지)
        clusters: List[List[int]] = []
        for idx in indices:
            n = normals[idx]
            placed = False
            for cluster in clusters:
                # 클러스터의 첫 번째 노멀과 비교 (dot > 0 이면 같은 방향)
                ref = normals[cluster[0]]
                dot = _vec_dot(n, ref)
                if dot > 0.0:
                    cluster.append(idx)
                    placed = True
                    break
            if not placed:
                clusters.append([idx])

        # 각 클러스터별로 노멀 평균 계산
        for cluster in clusters:
            avg_x, avg_y, avg_z = 0.0, 0.0, 0.0
            for idx in cluster:
                avg_x += normals[idx].x
                avg_y += normals[idx].y
                avg_z += normals[idx].z

            avg_normal = _vec_normalize(unreal.Vector(avg_x, avg_y, avg_z))

            for idx in cluster:
                smoothed_normals[idx] = avg_normal

    return smoothed_normals


def _vec_dot(a: unreal.Vector, b: unreal.Vector) -> float:
    """두 벡터의 내적"""
    return a.x * b.x + a.y * b.y + a.z * b.z


def _vec_normalize(v: unreal.Vector) -> unreal.Vector:
    """벡터 정규화 (길이가 0에 가까우면 (0,0,1) 반환)"""
    length = (v.x ** 2 + v.y ** 2 + v.z ** 2) ** 0.5
    if length < 1e-8:
        return unreal.Vector(0, 0, 1)
    inv = 1.0 / length
    return unreal.Vector(v.x * inv, v.y * inv, v.z * inv)


def _vec_cross(a: unreal.Vector, b: unreal.Vector) -> unreal.Vector:
    """두 벡터의 외적"""
    return unreal.Vector(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    )


def transform_normal_to_tangent_space(
    world_normal: unreal.Vector,
    tangent: unreal.Vector,
    bitangent: unreal.Vector,
    vertex_normal: unreal.Vector
) -> unreal.Vector:
    """월드 노멀을 탄젠트 스페이스로 변환합니다.

    Gram-Schmidt 직교화를 적용하여 정확한 직교정규 TBN 행렬을 구성한 후,
    전치(=역행렬)를 이용해 변환합니다.

    Args:
        world_normal: 월드 스페이스 노멀
        tangent: 탄젠트 벡터 (X)
        bitangent: 바이탄젠트 벡터 (Y)
        vertex_normal: 버텍스 노멀 (Z)

    Returns:
        탄젠트 스페이스 노멀
    """
    # 1) N 정규화
    N = _vec_normalize(vertex_normal)

    # 2) Gram-Schmidt: T = normalize(tangent - dot(tangent, N) * N)
    t_dot_n = _vec_dot(tangent, N)
    T_raw = unreal.Vector(
        tangent.x - t_dot_n * N.x,
        tangent.y - t_dot_n * N.y,
        tangent.z - t_dot_n * N.z
    )
    T = _vec_normalize(T_raw)

    # 3) B = cross(N, T) * sign  (원본 bitangent 방향 보존)
    B_cross = _vec_cross(N, T)
    bitangent_sign = 1.0 if _vec_dot(B_cross, bitangent) >= 0.0 else -1.0
    B = unreal.Vector(
        B_cross.x * bitangent_sign,
        B_cross.y * bitangent_sign,
        B_cross.z * bitangent_sign
    )

    # 4) 직교정규 TBN^T * world_normal → tangent space
    ts_normal = unreal.Vector(
        _vec_dot(world_normal, T),
        _vec_dot(world_normal, B),
        _vec_dot(world_normal, N)
    )

    return _vec_normalize(ts_normal)


def normal_to_color(normal: unreal.Vector) -> unreal.LinearColor:
    """노멀 벡터를 컬러로 변환합니다.

    [-1, 1] 범위를 [0, 1]로 리맵합니다.

    Args:
        normal: 노멀 벡터 (각 성분 -1~1)

    Returns:
        LinearColor (각 성분 0~1)
    """
    return unreal.LinearColor(
        r=max(0.0, min(1.0, (normal.x * 0.5) + 0.5)),
        g=max(0.0, min(1.0, (normal.y * 0.5) + 0.5)),
        b=max(0.0, min(1.0, (normal.z * 0.5) + 0.5)),
        a=1.0
    )


def _get_mesh_data(
    dynamic_mesh: unreal.DynamicMesh
) -> Optional[Tuple[List[unreal.Vector], List[unreal.Vector], List[unreal.Vector], List[unreal.Vector]]]:
    """DynamicMesh에서 위치, 노멀, 탄젠트, 바이탄젠트 데이터를 추출합니다.

    Returns:
        (positions, normals, tangents, bitangents) 또는 실패 시 None
    """
    # 버텍스 위치 가져오기
    result, position_list, has_gaps = dynamic_mesh.get_all_vertex_positions(skip_gaps=False)
    positions = position_list.convert_vector_list_to_array()

    if len(positions) == 0:
        unreal.log_error("버텍스 인덱스를 가져올 수 없습니다.")
        return None

    # 버텍스 노멀 가져오기
    result, normal_list, normal_valid, normal_gaps = dynamic_mesh.get_mesh_per_vertex_normals()
    normals = normal_list.convert_vector_list_to_array()

    if not normal_valid:
        unreal.log_error("버텍스 노멀을 가져올 수 없습니다.")
        return None

    # 탄젠트 정보 가져오기
    result, tangent_x_list, tangent_y_list, tangent_valid, tangent_gaps = dynamic_mesh.get_mesh_per_vertex_tangents()
    tangents = tangent_x_list.convert_vector_list_to_array()   # Tangent (X)
    bitangents = tangent_y_list.convert_vector_list_to_array() # Bitangent (Y)

    if not tangent_valid:
        unreal.log_warning("탄젠트가 없습니다. 탄젠트를 재계산합니다.")
        tangent_options = unreal.GeometryScriptTangentsOptions()
        dynamic_mesh.compute_tangents(tangent_options)
        result, tangent_x_list, tangent_y_list, tangent_valid, tangent_gaps = dynamic_mesh.get_mesh_per_vertex_tangents()
        tangents = tangent_x_list.convert_vector_list_to_array()
        bitangents = tangent_y_list.convert_vector_list_to_array()

    vertex_count = len(positions)

    # 배열 크기 검증
    if vertex_count != len(normals) or len(tangents) != vertex_count or len(bitangents) != vertex_count:
        unreal.log_error(f"배열 크기 불일치: positions={vertex_count}, normals={len(normals)}, tangents={len(tangents)}, bitangents={len(bitangents)}")
        return None

    return positions, normals, tangents, bitangents


def _compute_tangent_space_normals(
    positions: List[unreal.Vector],
    normals: List[unreal.Vector],
    tangents: List[unreal.Vector],
    bitangents: List[unreal.Vector],
    smooth_threshold: float = 0.001
) -> List[unreal.Vector]:
    """위치/노멀/탄젠트 데이터로부터 Smoothed Normal의 Tangent Space 변환 결과를 계산합니다."""
    smoothed_normals = compute_smoothed_normals(positions, normals, smooth_threshold)

    ts_normals: List[unreal.Vector] = []
    for i in range(len(positions)):
        ts_normal = transform_normal_to_tangent_space(
            smoothed_normals[i],
            tangents[i],
            bitangents[i],
            normals[i]
        )
        ts_normals.append(ts_normal)

    return ts_normals


def bake_smoothed_normal_to_vertex_color(
    dynamic_mesh: unreal.DynamicMesh,
    smooth_threshold: float = 0.001
) -> bool:
    """DynamicMesh의 Smoothed Normal을 Tangent Space로 변환하여 Vertex Color로 저장합니다.

    Args:
        dynamic_mesh: 대상 DynamicMesh
        smooth_threshold: 동일 위치 판정 임계값 (cm)

    Returns:
        성공 여부
    """
    mesh_data = _get_mesh_data(dynamic_mesh)
    if mesh_data is None:
        return False

    positions, normals, tangents, bitangents = mesh_data
    vertex_count = len(positions)
    unreal.log(f"버텍스 수: {vertex_count}")

    ts_normals = _compute_tangent_space_normals(positions, normals, tangents, bitangents, smooth_threshold)

    # Tangent Space 노멀 → Vertex Color 변환
    vertex_colors: List[unreal.LinearColor] = []
    for ts_normal in ts_normals:
        vertex_colors.append(normal_to_color(ts_normal))

    # 메시에 적용
    color_list = unreal.GeometryScript_List.convert_array_to_color_list(vertex_colors)
    dynamic_mesh.set_mesh_per_vertex_colors(color_list)

    unreal.log(f"Smoothed Normal을 Vertex Color로 저장했습니다. ({vertex_count}개 버텍스)")
    return True


def normal_to_uv(normal: unreal.Vector) -> unreal.Vector2D:
    """노멀 벡터의 XY를 UV 좌표로 직접 저장합니다.

    UV 채널은 [-1, 1] 범위를 그대로 저장할 수 있으므로 패킹 불필요.
    Z(B) 채널은 셰이더에서 reconstruct: z = sqrt(1 - x*x - y*y)

    Args:
        normal: Tangent Space 노멀 벡터 (각 성분 -1~1)

    Returns:
        Vector2D (U=X, V=Y) — 셰이더에서 unpack 없이 바로 사용
    """
    return unreal.Vector2D(
        x=normal.x,
        y=normal.y
    )


def bake_smoothed_normal_to_uv(
    dynamic_mesh: unreal.DynamicMesh,
    uv_channel: int = 1,
    smooth_threshold: float = 0.001
) -> bool:
    """DynamicMesh의 Smoothed Normal을 Tangent Space로 변환하여 UV 채널에 RG(XY)만 저장합니다.

    B(Z) 채널은 셰이더에서 reconstruct: z = sqrt(1 - x*x - y*y)

    Args:
        dynamic_mesh: 대상 DynamicMesh
        uv_channel: 저장할 UV 채널 인덱스 (기본값: 1, UV1)
        smooth_threshold: 동일 위치 판정 임계값 (cm)

    Returns:
        성공 여부
    """
    mesh_data = _get_mesh_data(dynamic_mesh)
    if mesh_data is None:
        return False

    positions, normals, tangents, bitangents = mesh_data
    vertex_count = len(positions)
    unreal.log(f"버텍스 수: {vertex_count}")

    # UV 채널 수 확인 및 확장
    current_uv_sets = dynamic_mesh.get_num_uv_sets()
    if uv_channel >= current_uv_sets:
        dynamic_mesh.set_num_uv_sets(uv_channel + 1)
        unreal.log(f"UV 채널 수를 {current_uv_sets} → {uv_channel + 1}로 확장했습니다.")

    ts_normals = _compute_tangent_space_normals(positions, normals, tangents, bitangents, smooth_threshold)

    # element_id == vertex_id (새 UV 채널 또는 split 없는 경우)
    # 각 버텍스에 대해 UV element 설정
    fail_count = 0
    for i in range(vertex_count):
        uv = normal_to_uv(ts_normals[i])
        result, is_valid = dynamic_mesh.set_mesh_uv_element_position(
            uv_set_index=uv_channel,
            element_id=i,
            new_uv_position=uv,
            defer_change_notifications=(i < vertex_count - 1)
        )
        if not is_valid:
            fail_count += 1

    if fail_count > 0:
        unreal.log_warning(f"UV element 설정 실패: {fail_count}개 (UV seam split으로 인한 element ID 불일치 가능)")

    unreal.log(f"Smoothed Normal을 UV{uv_channel}에 저장했습니다. ({vertex_count}개 버텍스, RG only)")
    return True


def _bake_to_mesh(
    dynamic_mesh: unreal.DynamicMesh,
    output_mode: OutputMode = OutputMode.VERTEX_COLOR,
    uv_channel: int = 1,
    smooth_threshold: float = 0.001
) -> bool:
    """출력 모드에 따라 Smoothed Normal을 Vertex Color 또는 UV에 저장합니다."""
    if output_mode == OutputMode.UV_CHANNEL:
        return bake_smoothed_normal_to_uv(dynamic_mesh, uv_channel, smooth_threshold)
    else:
        return bake_smoothed_normal_to_vertex_color(dynamic_mesh, smooth_threshold)


def process_static_mesh(
    static_mesh: unreal.StaticMesh,
    lod_index: int = 0,
    smooth_threshold: float = 0.001,
    save_asset: bool = True,
    output_mode: OutputMode = OutputMode.VERTEX_COLOR,
    uv_channel: int = 1
) -> bool:
    """StaticMesh의 Smoothed Normal을 Vertex Color 또는 UV 채널에 저장합니다.

    Args:
        static_mesh: 대상 StaticMesh
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_asset: 애셋 저장 여부
        output_mode: 출력 대상 (VERTEX_COLOR 또는 UV_CHANNEL)
        uv_channel: UV 출력 시 채널 인덱스 (기본값: 1)

    Returns:
        성공 여부
    """
    asset_path = static_mesh.get_path_name()
    mode_str = f"UV{uv_channel}" if output_mode == OutputMode.UV_CHANNEL else "VertexColor"
    unreal.log(f"StaticMesh 처리 시작 [{mode_str}]: {asset_path}")

    # Undo 지원을 위한 트랜잭션
    with unreal.ScopedEditorTransaction(f"Bake Smoothed Normal: {static_mesh.get_name()}"):
        # DynamicMesh로 복사
        dynamic_mesh = copy_mesh_from_static_mesh(static_mesh, lod_index)
        if dynamic_mesh is None:
            return False

        # Smoothed Normal 저장
        if not _bake_to_mesh(dynamic_mesh, output_mode, uv_channel, smooth_threshold):
            return False

        # StaticMesh로 다시 저장
        if not copy_mesh_to_static_mesh(dynamic_mesh, static_mesh, lod_index):
            return False

    # 애셋 저장
    if save_asset:
        unreal.EditorAssetLibrary.save_loaded_asset(static_mesh)
        unreal.log(f"애셋 저장 완료: {asset_path}")

    return True


def process_skeletal_mesh(
    skeletal_mesh: unreal.SkeletalMesh,
    lod_index: int = 0,
    smooth_threshold: float = 0.001,
    save_asset: bool = True,
    output_mode: OutputMode = OutputMode.VERTEX_COLOR,
    uv_channel: int = 1
) -> bool:
    """SkeletalMesh의 Smoothed Normal을 Vertex Color 또는 UV 채널에 저장합니다.

    Args:
        skeletal_mesh: 대상 SkeletalMesh
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_asset: 애셋 저장 여부
        output_mode: 출력 대상 (VERTEX_COLOR 또는 UV_CHANNEL)
        uv_channel: UV 출력 시 채널 인덱스 (기본값: 1)

    Returns:
        성공 여부
    """
    asset_path = skeletal_mesh.get_path_name()
    mode_str = f"UV{uv_channel}" if output_mode == OutputMode.UV_CHANNEL else "VertexColor"
    unreal.log(f"SkeletalMesh 처리 시작 [{mode_str}]: {asset_path}")

    # Undo 지원을 위한 트랜잭션
    with unreal.ScopedEditorTransaction(f"Bake Smoothed Normal: {skeletal_mesh.get_name()}"):
        # DynamicMesh로 복사
        dynamic_mesh = copy_mesh_from_skeletal_mesh(skeletal_mesh, lod_index)
        if dynamic_mesh is None:
            return False

        # Smoothed Normal 저장
        if not _bake_to_mesh(dynamic_mesh, output_mode, uv_channel, smooth_threshold):
            return False

        # SkeletalMesh로 다시 저장
        if not copy_mesh_to_skeletal_mesh(dynamic_mesh, skeletal_mesh, lod_index):
            return False

    # 애셋 저장
    if save_asset:
        unreal.EditorAssetLibrary.save_loaded_asset(skeletal_mesh)
        unreal.log(f"애셋 저장 완료: {asset_path}")

    return True


def process_selected_assets(
    lod_index: int = 0,
    smooth_threshold: float = 0.001,
    save_assets: bool = True,
    output_mode: OutputMode = OutputMode.VERTEX_COLOR,
    uv_channel: int = 1
) -> Tuple[int, int]:
    """Content Browser에서 선택된 현재 에셋들을 처리합니다.

    Args:
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_assets: 애셋 저장 여부
        output_mode: 출력 대상 (VERTEX_COLOR 또는 UV_CHANNEL)
        uv_channel: UV 출력 시 채널 인덱스 (기본값: 1)

    Returns:
        (성공 수, 실패 수)
    """
    # 선택된 애셋 가져오기
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

    if not selected_assets:
        unreal.log_warning("선택된 애셋이 없습니다. Content Browser에서 메시 애셋을 선택해주세요.")
        return (0, 0)

    # 메시 에셋만 필터링
    mesh_assets = [a for a in selected_assets if isinstance(a, (unreal.StaticMesh, unreal.SkeletalMesh))]
    if not mesh_assets:
        unreal.log_warning(f"{len(selected_assets)}개 애셋 중 StaticMesh/SkeletalMesh가 없습니다.")
        return (0, 0)

    success_count = 0
    fail_count = 0

    unreal.log(f"Smoothed Normal 처리 대상: {len(mesh_assets)}개 메시 애셋")

    with unreal.ScopedSlowTask(len(mesh_assets), "Smoothed Normal 처리 중...") as slow_task:
        slow_task.make_dialog(True)

        for asset in mesh_assets:
            if slow_task.should_cancel():
                break

            asset_name = asset.get_name()
            slow_task.enter_progress_frame(1, f"처리 중: {asset_name}")

            result = False

            if isinstance(asset, unreal.StaticMesh):
                result = process_static_mesh(asset, lod_index, smooth_threshold, save_assets, output_mode, uv_channel)
            elif isinstance(asset, unreal.SkeletalMesh):
                result = process_skeletal_mesh(asset, lod_index, smooth_threshold, save_assets, output_mode, uv_channel)

            if result:
                success_count += 1
            else:
                fail_count += 1

    unreal.log(f"Smoothed Normal 처리 완료: 성공 {success_count}, 실패 {fail_count}")
    return success_count, fail_count


def run(output_mode: OutputMode = OutputMode.VERTEX_COLOR, uv_channel: int = 1):
    """에디터 메뉴에서 호출되는 진입점

    Args:
        output_mode: 출력 대상 (VERTEX_COLOR 또는 UV_CHANNEL)
        uv_channel: UV 출력 시 채널 인덱스 (기본값: 1)
    """
    process_selected_assets(output_mode=output_mode, uv_channel=uv_channel)


def run_vertex_color():
    """Vertex Color로 출력 (에디터 메뉴용)"""
    run(OutputMode.VERTEX_COLOR)


def run_uv(uv_channel: int = 1):
    """UV 채널로 출력 (에디터 메뉴용)

    Args:
        uv_channel: UV 채널 인덱스 (기본값: 1)
    """
    run(OutputMode.UV_CHANNEL, uv_channel)