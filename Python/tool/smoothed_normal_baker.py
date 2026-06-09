"""
Smoothed Normal Baker
메시의 Smoothed Normal을 계산하여 UV 채널에 저장하는 도구

출력: 지정 UV 채널에 per-triangle-corner로 RG(XY)를 [-1,1] 그대로 저장
  - B(Z)는 셰이더에서 reconstruct: float z = sqrt(1 - x*x - y*y)
  - 하드 엣지에서 같은 버텍스라도 코너별 개별 TBN으로 변환하여 정확한 결과 보장
  - DynamicMesh의 set_mesh_triangle_u_vs를 사용하여 per-corner UV 저장

버전: 2.0.0
날짜: 2026-03-11
"""

import unreal
from typing import Optional, List, Dict, Tuple
from collections import defaultdict


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
    # 노멀/탄젠트 재계산 방지 (저장된 UV 데이터를 보존하기 위함)
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


def bake_smoothed_normal_to_uv(
    dynamic_mesh: unreal.DynamicMesh,
    uv_channel: int = 1,
    smooth_threshold: float = 0.001
) -> bool:
    """DynamicMesh의 Smoothed Normal을 Tangent Space로 변환하여 UV 채널에 per-corner로 저장합니다.

    각 삼각형 코너별로 개별 TBN을 사용하여 변환하므로,
    하드 엣지에서 같은 버텍스라도 다른 TS 노멀을 가질 수 있습니다.
    set_mesh_triangle_u_vs로 per-corner UV 값을 직접 설정합니다.

    B(Z) 채널은 셰이더에서 reconstruct: z = sqrt(1 - x*x - y*y)

    중요: GeometryScriptTriangle의 vector0/1/2 프로퍼티는 C++ 임시 참조를 반환하므로,
    다음 API 호출 시 무효화됩니다. 반드시 float 값을 즉시 복사해야 합니다.

    Args:
        dynamic_mesh: 대상 DynamicMesh
        uv_channel: 저장할 UV 채널 인덱스 (기본값: 1, UV1)
        smooth_threshold: 동일 위치 판정 임계값 (cm)

    Returns:
        성공 여부
    """
    # --- 타입 별칭 & 로컬 헬퍼 (plain tuple로 저장하여 참조 무효화 방지) ---
    Vec3 = Tuple[float, float, float]

    def _dot(a: Vec3, b: Vec3) -> float:
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

    def _normalize(v: Vec3) -> Vec3:
        length = (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5
        if length < 1e-8:
            return (0.0, 0.0, 1.0)
        inv = 1.0 / length
        return (v[0]*inv, v[1]*inv, v[2]*inv)

    def _cross(a: Vec3, b: Vec3) -> Vec3:
        return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])

    def _copy_vec(v: unreal.Vector) -> Vec3:
        """unreal.Vector의 float 값을 즉시 복사하여 Python tuple로 반환"""
        return (float(v.x), float(v.y), float(v.z))

    def _ts_transform(world_n: Vec3, tangent: Vec3, bitangent: Vec3, vertex_n: Vec3) -> Vec3:
        """월드 노멀 → 탄젠트 스페이스 변환 (Gram-Schmidt 직교화, tuple 버전)"""
        N = _normalize(vertex_n)
        t_dot_n = _dot(tangent, N)
        T = _normalize((tangent[0] - t_dot_n*N[0], tangent[1] - t_dot_n*N[1], tangent[2] - t_dot_n*N[2]))
        B_cross = _cross(N, T)
        sign = 1.0 if _dot(B_cross, bitangent) >= 0.0 else -1.0
        B = (B_cross[0]*sign, B_cross[1]*sign, B_cross[2]*sign)
        return _normalize((_dot(world_n, T), _dot(world_n, B), _dot(world_n, N)))

    # 1. 버텍스 위치 가져오기
    _, pos_list, _ = dynamic_mesh.get_all_vertex_positions(skip_gaps=False)
    positions_raw = pos_list.convert_vector_list_to_array()
    vertex_count = len(positions_raw)

    if vertex_count == 0:
        unreal.log_error("버텍스가 없습니다.")
        return False

    # 위치도 즉시 tuple로 복사
    positions: List[Vec3] = [_copy_vec(p) for p in positions_raw]

    # 2. 탄젠트가 없으면 재계산
    _, _, _, tangent_valid, _ = dynamic_mesh.get_mesh_per_vertex_tangents()
    if not tangent_valid:
        unreal.log_warning("탄젠트가 없습니다. 탄젠트를 재계산합니다.")
        dynamic_mesh.compute_tangents(unreal.GeometryScriptTangentsOptions())

    # 3. 삼각형 순회 1차: 오버레이 노멀 수집 (위치별 Smoothed Normal 계산용)
    #    (unreal.Vector 참조를 저장하면 다음 API 호출 시 무효화됨!)
    _, tri_id_list, _ = dynamic_mesh.get_all_triangle_i_ds()
    tri_ids = tri_id_list.convert_index_list_to_array()

    # 위치별 오버레이 노멀 수집
    position_normals: Dict[Tuple[int, int, int], List[Vec3]] = defaultdict(list)

    # 삼각형별 데이터 캐시 (2차 패스에서 재사용)
    # tri_id -> (vid0,vid1,vid2, n0,n1,n2, t0,t1,t2, b0,b1,b2)
    tri_cache: Dict[int, Tuple] = {}

    for tri_id in tri_ids:
        vert_vec, valid = dynamic_mesh.get_triangle_indices(tri_id)
        if not valid:
            continue

        _, has_valid, normals_tri, tangents_tri, bitangents_tri = \
            dynamic_mesh.get_triangle_normal_tangents(tri_id)
        if not has_valid:
            continue

        vid0, vid1, vid2 = int(vert_vec.x), int(vert_vec.y), int(vert_vec.z)

        # 즉시 float tuple로 복사 (C++ 임시 참조 무효화 방지)
        n0 = _copy_vec(normals_tri.vector0)
        n1 = _copy_vec(normals_tri.vector1)
        n2 = _copy_vec(normals_tri.vector2)
        t0 = _copy_vec(tangents_tri.vector0)
        t1 = _copy_vec(tangents_tri.vector1)
        t2 = _copy_vec(tangents_tri.vector2)
        b0 = _copy_vec(bitangents_tri.vector0)
        b1 = _copy_vec(bitangents_tri.vector1)
        b2 = _copy_vec(bitangents_tri.vector2)

        tri_cache[tri_id] = (vid0, vid1, vid2, n0, n1, n2, t0, t1, t2, b0, b1, b2)

        # 위치 → 노멀 매핑
        for vid, n in [(vid0, n0), (vid1, n1), (vid2, n2)]:
            if vid < vertex_count:
                px, py, pz = positions[vid]
                key = (
                    round(px / smooth_threshold),
                    round(py / smooth_threshold),
                    round(pz / smooth_threshold)
                )
                position_normals[key].append(n)

    # 4. 위치별 Smoothed Normal 계산 (월드 스페이스에서 평균)
    position_smoothed: Dict[Tuple[int, int, int], Vec3] = {}
    for key, norms in position_normals.items():
        ax, ay, az = 0.0, 0.0, 0.0
        for nx, ny, nz in norms:
            ax += nx
            ay += ny
            az += nz
        position_smoothed[key] = _normalize((ax, ay, az))

    # 5. UV 채널 준비
    current_uv_sets = dynamic_mesh.get_num_uv_sets()
    if uv_channel >= current_uv_sets:
        dynamic_mesh.set_num_uv_sets(uv_channel + 1)
        unreal.log(f"UV 채널 수를 {current_uv_sets} → {uv_channel + 1}로 확장했습니다.")

    # 6. 삼각형 순회 2차: 코너별 TS 변환 → per-corner UV 저장
    non_neutral_count = 0
    debug_samples: List[str] = []
    tri_count = len(tri_cache)
    progress_idx = 0

    for tri_id, data in tri_cache.items():
        vid0, vid1, vid2, n0, n1, n2, t0, t1, t2, b0, b1, b2 = data
        progress_idx += 1
        defer = (progress_idx < tri_count)

        uvs: List[unreal.Vector2D] = []
        for vid, cn, ct, cb in [(vid0, n0, t0, b0), (vid1, n1, t1, b1), (vid2, n2, t2, b2)]:
            # 해당 버텍스 위치의 Smoothed Normal 가져오기
            if vid < vertex_count:
                px, py, pz = positions[vid]
                key = (
                    round(px / smooth_threshold),
                    round(py / smooth_threshold),
                    round(pz / smooth_threshold)
                )
                sm = position_smoothed.get(key, (0.0, 0.0, 1.0))
            else:
                sm = (0.0, 0.0, 1.0)

            # 이 코너의 고유 TBN으로 탄젠트 스페이스 변환
            ts = _ts_transform(sm, ct, cb, cn)
            uvs.append(unreal.Vector2D(ts[0], ts[1]))

            is_non_neutral = abs(ts[0]) > 0.01 or abs(ts[1]) > 0.01 or ts[2] < 0.99
            if is_non_neutral:
                non_neutral_count += 1
                if len(debug_samples) < 5:
                    debug_samples.append(
                        f"  tri={tri_id} vid={vid}: smoothed=({sm[0]:.3f},{sm[1]:.3f},{sm[2]:.3f}) "
                        f"N=({cn[0]:.3f},{cn[1]:.3f},{cn[2]:.3f}) "
                        f"→ TS=({ts[0]:.3f},{ts[1]:.3f},{ts[2]:.3f})"
                    )

        # per-corner UV 값을 삼각형 단위로 직접 설정
        uv_tri = unreal.GeometryScriptUVTriangle(
            uv0=uvs[0], uv1=uvs[1], uv2=uvs[2]
        )
        dynamic_mesh.set_mesh_triangle_u_vs(
            uv_set_index=uv_channel,
            triangle_id=tri_id,
            u_vs=uv_tri,
            defer_change_notifications=defer
        )

    unreal.log(f"버텍스 수: {vertex_count}, 삼각형 수: {len(tri_ids)}, "
               f"비중립 코너: {non_neutral_count}")
    if debug_samples:
        unreal.log("디버그 샘플:\n" + "\n".join(debug_samples))

    unreal.log(f"Smoothed Normal을 UV{uv_channel}에 per-corner로 저장했습니다. (RG only)")
    return True


def process_static_mesh(
    static_mesh: unreal.StaticMesh,
    lod_index: int = 0,
    smooth_threshold: float = 0.001,
    save_asset: bool = True,
    uv_channel: int = 1
) -> bool:
    """StaticMesh의 Smoothed Normal을 UV 채널에 저장합니다.

    Args:
        static_mesh: 대상 StaticMesh
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_asset: 애셋 저장 여부
        uv_channel: UV 채널 인덱스 (기본값: 1)

    Returns:
        성공 여부
    """
    asset_path = static_mesh.get_path_name()
    unreal.log(f"StaticMesh 처리 시작 [UV{uv_channel}]: {asset_path}")

    # Undo 지원을 위한 트랜잭션
    with unreal.ScopedEditorTransaction(f"Bake Smoothed Normal: {static_mesh.get_name()}"):
        # DynamicMesh로 복사
        dynamic_mesh = copy_mesh_from_static_mesh(static_mesh, lod_index)
        if dynamic_mesh is None:
            return False

        # Smoothed Normal을 UV에 저장
        if not bake_smoothed_normal_to_uv(dynamic_mesh, uv_channel, smooth_threshold):
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
    uv_channel: int = 1
) -> bool:
    """SkeletalMesh의 Smoothed Normal을 UV 채널에 저장합니다.

    Args:
        skeletal_mesh: 대상 SkeletalMesh
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_asset: 애셋 저장 여부
        uv_channel: UV 채널 인덱스 (기본값: 1)

    Returns:
        성공 여부
    """
    asset_path = skeletal_mesh.get_path_name()
    unreal.log(f"SkeletalMesh 처리 시작 [UV{uv_channel}]: {asset_path}")

    # Undo 지원을 위한 트랜잭션
    with unreal.ScopedEditorTransaction(f"Bake Smoothed Normal: {skeletal_mesh.get_name()}"):
        # DynamicMesh로 복사
        dynamic_mesh = copy_mesh_from_skeletal_mesh(skeletal_mesh, lod_index)
        if dynamic_mesh is None:
            return False

        # Smoothed Normal을 UV에 저장
        if not bake_smoothed_normal_to_uv(dynamic_mesh, uv_channel, smooth_threshold):
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
    uv_channel: int = 1
) -> Tuple[int, int]:
    """Content Browser에서 선택된 현재 에셋들을 처리합니다.

    Args:
        lod_index: 처리할 LOD 인덱스
        smooth_threshold: 동일 위치 판정 임계값 (cm)
        save_assets: 애셋 저장 여부
        uv_channel: UV 채널 인덱스 (기본값: 1)

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
                result = process_static_mesh(asset, lod_index, smooth_threshold, save_assets, uv_channel)
            elif isinstance(asset, unreal.SkeletalMesh):
                result = process_skeletal_mesh(asset, lod_index, smooth_threshold, save_assets, uv_channel)

            if result:
                success_count += 1
            else:
                fail_count += 1

    unreal.log(f"Smoothed Normal 처리 완료: 성공 {success_count}, 실패 {fail_count}")
    return success_count, fail_count


def run(uv_channel: int = 1):
    """에디터 메뉴에서 호출되는 진입점

    Args:
        uv_channel: UV 채널 인덱스 (기본값: 1)
    """
    process_selected_assets(uv_channel=uv_channel)