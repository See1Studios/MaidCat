"""
언리얼 엔진 Python 랜드스케이프 라이브러리 래퍼 모듈
================================================

이 모듈은 언리얼 엔진 Python 랜드스케이프 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonLandscapeLib 함수들:
- unreal.PythonLandscapeLib.function_name → landscape_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 랜드스케이프 라이브러리 래퍼들
# ===============================================================================

# 랜드스케이프 생성
def create_landscape(
    landscape_transform: unreal.Transform,
    section_size: int,
    sections_per_component: int,
    component_count_x: int,
    component_count_y: int
) -> unreal.Landscape:
    """
    에디터에서 랜드스케이프를 생성합니다.
    
    Args:
        landscape_transform: 랜드스케이프의 트랜스폼
        section_size: 랜드스케이프의 섹션 크기 (63, 127, 255 등)
        sections_per_component: 각 컴포넌트의 섹션 수 (1 또는 2)
        component_count_x: X축 컴포넌트 수
        component_count_y: Y축 컴포넌트 수
    
    Returns:
        생성된 랜드스케이프
    """
    return unreal.PythonLandscapeLib.create_landscape(
        landscape_transform, section_size, sections_per_component,
        component_count_x, component_count_y
    )


def create_landscape_proxy(
    landscape_transform: unreal.Transform,
    section_size: int,
    sections_per_component: int,
    component_count_x: int,
    component_count_y: int,
    shared_landscape_actor: unreal.Landscape
) -> unreal.LandscapeStreamingProxy:
    """
    에디터에서 스트리밍 프록시를 생성합니다.
    
    Args:
        landscape_transform: 랜드스케이프의 트랜스폼
        section_size: 랜드스케이프의 섹션 크기 (63, 127, 255 등)
        sections_per_component: 각 컴포넌트의 섹션 수 (1 또는 2)
        component_count_x: X축 컴포넌트 수
        component_count_y: Y축 컴포넌트 수
        shared_landscape_actor: 프록시와 GUID를 공유하는 공유 랜드스케이프
    
    Returns:
        생성된 랜드스케이프 스트리밍 프록시
    
    Note:
        UE5에서는 아직 테스트되지 않았습니다.
    """
    return unreal.PythonLandscapeLib.create_landscape_proxy(
        landscape_transform, section_size, sections_per_component,
        component_count_x, component_count_y, shared_landscape_actor
    )


def create_landscape_proxy_with_guid(
    landscape_transform: unreal.Transform,
    section_size: int,
    sections_per_component: int,
    component_count_x: int,
    component_count_y: int,
    guid: unreal.Guid,
    quads_space_offset_x: int = -1,
    quads_space_offset_y: int = -1
) -> unreal.LandscapeStreamingProxy:
    """
    GUID를 사용하여 에디터에서 스트리밍 프록시를 생성합니다.
    
    Args:
        landscape_transform: 랜드스케이프의 트랜스폼
        section_size: 랜드스케이프의 섹션 크기 (63, 127, 255 등)
        sections_per_component: 각 컴포넌트의 섹션 수 (1 또는 2)
        component_count_x: X축 컴포넌트 수
        component_count_y: Y축 컴포넌트 수
        guid: 프록시와 함께 사용할 GUID
        quads_space_offset_x: X축 쿼드 공간 오프셋
        quads_space_offset_y: Y축 쿼드 공간 오프셋
    
    Returns:
        생성된 랜드스케이프 스트리밍 프록시
    
    Note:
        UE5에서는 아직 테스트되지 않았습니다.
    """
    return unreal.PythonLandscapeLib.create_landscape_proxy_with_guid(
        landscape_transform, section_size, sections_per_component,
        component_count_x, component_count_y, guid,
        quads_space_offset_x, quads_space_offset_y
    )


def add_adjacent_landscape_proxy(
    world_in: unreal.World,
    source_landscape: unreal.LandscapeProxy,
    direction: int
) -> unreal.LandscapeStreamingProxy:
    """
    지정된 방향에 인접한 스트리밍 프록시를 추가합니다.
    
    Args:
        world_in: 월드
        source_landscape: 소스 랜드스케이프 프록시
        direction: 방향 (동:0, 남:1, 서:2, 북:3)
    
    Returns:
        생성된 랜드스케이프 스트리밍 프록시
    """
    return unreal.PythonLandscapeLib.add_adjacent_landscape_proxy(world_in, source_landscape, direction)


# 랜드스케이프 정보 조회
def get_landscape_guid(landscape_proxy: unreal.LandscapeProxy) -> unreal.Guid:
    """
    랜드스케이프에서 GUID를 가져옵니다.
    
    Args:
        landscape_proxy: 랜드스케이프 인스턴스
    
    Returns:
        랜드스케이프의 GUID
    """
    return unreal.PythonLandscapeLib.get_landscape_guid(landscape_proxy)


def get_landscape_components(landscape_proxy: unreal.LandscapeProxy) -> List[unreal.LandscapeComponent]:
    """
    랜드스케이프에서 컴포넌트들을 가져옵니다.
    
    Args:
        landscape_proxy: 랜드스케이프 인스턴스
    
    Returns:
        랜드스케이프의 컴포넌트들
    """
    return unreal.PythonLandscapeLib.get_landscape_components(landscape_proxy)


# 하이트맵 데이터 관리
def set_heightmap_data(landscape: unreal.LandscapeProxy, height_data: List[int]) -> bool:
    """
    지정된 랜드스케이프의 높이 데이터를 설정합니다.
    
    Args:
        landscape: 대상 랜드스케이프 인스턴스
        height_data: 평면화된 정수 리스트 형식의 랜드스케이프 높이 데이터 (0-65535)
    
    Returns:
        성공 여부
    """
    return unreal.PythonLandscapeLib.set_heightmap_data(landscape, height_data)


def get_heightmap_data(landscape: unreal.LandscapeProxy) -> List[int]:
    """
    지정된 랜드스케이프의 높이 데이터를 가져옵니다.
    
    Args:
        landscape: 조회할 랜드스케이프 인스턴스
    
    Returns:
        평면화된 정수 리스트 형식의 랜드스케이프 높이 데이터 (0-65535)
    """
    return unreal.PythonLandscapeLib.get_heightmap_data(landscape)


# 랜드스케이프 크기 계산
def cal_landscape_size(
    section_size: int,
    sections_per_component: int,
    component_count_x: int,
    component_count_y: int
) -> Tuple[int, int]:
    """
    랜드스케이프의 크기를 계산합니다 (하이트맵 데이터의 크기).
    
    Args:
        section_size: 랜드스케이프의 섹션 크기
        sections_per_component: 각 컴포넌트의 섹션 수 (1 또는 2)
        component_count_x: X축 컴포넌트 수
        component_count_y: Y축 컴포넌트 수
    
    Returns:
        (X축 크기, Y축 크기) 튜플
        X축 크기 = ComponentCountX * QuadsPerComponent + 1
    """
    return unreal.PythonLandscapeLib.cal_landscape_size(
        section_size, sections_per_component, component_count_x, component_count_y
    )


# 잔디 시스템 관리
def landscape_get_grass_components(landscape_proxy: unreal.LandscapeProxy) -> List[unreal.HierarchicalInstancedStaticMeshComponent]:
    """
    GrassType을 그리기 위한 HISM 컴포넌트를 가져옵니다.
    
    Args:
        landscape_proxy: GrassType을 소유한 랜드스케이프
    
    Returns:
        GrassType을 그리기 위한 HISM 컴포넌트들
    """
    return unreal.PythonLandscapeLib.landscape_get_grass_components(landscape_proxy)


def landscape_flush_grass_components(landscape_proxy: unreal.LandscapeProxy, flush_grass_maps: bool = True) -> None:
    """
    랜드스케이프의 잔디 캐시를 플러시합니다.
    
    Args:
        landscape_proxy: 랜드스케이프 프록시
        flush_grass_maps: GrassMaps를 플러시할지 여부
    """
    return unreal.PythonLandscapeLib.landscape_flush_grass_components(landscape_proxy, flush_grass_maps)


def landscape_update_grass(landscape_proxy: unreal.LandscapeProxy, cameras: List[unreal.Vector], force_sync: bool) -> None:
    """
    랜드스케이프 프록시의 잔디 캐시를 업데이트합니다.
    
    Args:
        landscape_proxy: GrassType을 소유한 랜드스케이프
        cameras: 컬링에 사용할 카메라들, 비어있으면 컬링 없음
        force_sync: True이면 모든 작업을 블로킹하고 완료
    """
    return unreal.PythonLandscapeLib.landscape_update_grass(landscape_proxy, cameras, force_sync)