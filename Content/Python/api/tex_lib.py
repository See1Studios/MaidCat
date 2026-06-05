"""
언리얼 엔진 Python 텍스처 라이브러리 래퍼 모듈
===============================================

이 모듈은 언리얼 엔진 Python 텍스처 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonTextureLib 함수들:
- unreal.PythonTextureLib.function_name → tex_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 텍스처 라이브러리 래퍼들
# ===============================================================================

# 텍스처 생성
def create_texture2d_from_raw(
    raw_data: List[int], 
    width: int, 
    height: int, 
    channel_num: int, 
    use_srgb: bool = False, 
    texture_filter_value: int = -1, 
    bgr: bool = False, 
    flip_y: bool = False
) -> unreal.Texture2D:
    """
    픽셀 원시 데이터로부터 Texture2D를 생성합니다.
    
    Args:
        raw_data: 이미지의 평면화된 uint8 원시 데이터
        width: Texture2D의 폭
        height: Texture2D의 높이
        channel_num: 원시 데이터의 채널 수 (1:그레이스케일, 2:그레이스케일+알파, 3:RGB, 4:RGBA)
        use_srgb: SRGB 사용 여부
        texture_filter_value: 텍스처 필터 (0:Nearest, 1:Bilinear, 2:Trilinear, 3:텍스처 그룹 설정 사용)
        bgr: 원시 데이터 순서가 BGR인지 여부 (기본값은 RGB)
        flip_y: Y축 뒤집기 여부
    
    Returns:
        생성된 Texture2D (EPixelFormat::PF_R8G8B8A8 타입)
    """
    return unreal.PythonTextureLib.create_texture2d_from_raw(
        raw_data, width, height, channel_num, use_srgb, 
        texture_filter_value, bgr, flip_y
    )


def create_texture2d(
    width: int, 
    height: int, 
    use_srgb: bool = False, 
    texture_filter_value: int = -1
) -> unreal.Texture2D:
    """
    지정된 크기로 Texture2D를 생성합니다.
    
    Args:
        width: Texture2D의 폭
        height: Texture2D의 높이
        use_srgb: SRGB 사용 여부
        texture_filter_value: 텍스처 필터 (0:Nearest, 1:Bilinear, 2:Trilinear, 3:텍스처 그룹 설정 사용)
    
    Returns:
        생성된 Texture2D (EPixelFormat::PF_B8G8R8A8 타입)
    """
    return unreal.PythonTextureLib.create_texture2d(width, height, use_srgb, texture_filter_value)


# 텍스처 컴파일레이션
def finish_compilation_texture(texture: unreal.Texture2D) -> unreal.Texture2D:
    """
    요청된 텍스처의 컴파일레이션이 완료될 때까지 블로킹합니다. (UE5 필요)
    
    Args:
        texture: 컴파일레이션을 기다릴 텍스처
    
    Returns:
        컴파일레이션이 완료된 Texture2D
    """
    return unreal.PythonTextureLib.finish_compilation_texture(texture)


# 렌더 타겟 관리
def set_render_target_data(
    render_target_texture: unreal.TextureRenderTarget2D, 
    raw_data: List[int], 
    raw_data_width: int, 
    raw_data_height: int, 
    raw_data_channel_num: int, 
    use_srgb: bool = False, 
    texture_filter_value: int = -1, 
    bgr: bool = False
) -> None:
    """
    원시 데이터로 RenderTexture2D를 설정합니다.
    
    Args:
        render_target_texture: 대상 RenderTarget2D
        raw_data: 이미지의 평면화된 uint8 원시 데이터
        raw_data_width: 원시 데이터의 폭
        raw_data_height: 원시 데이터의 높이
        raw_data_channel_num: 원시 데이터의 채널 수 (1:그레이스케일, 2:그레이스케일+알파, 3:RGB, 4:RGBA)
        use_srgb: SRGB 사용 여부
        texture_filter_value: 텍스처 필터
        bgr: 원시 데이터 순서가 BGR인지 여부
    
    Note:
        원시 데이터의 순서는 행 우선입니다. 좌하단 모서리가 첫 번째 픽셀이고, 우상단이 마지막 픽셀입니다.
    """
    return unreal.PythonTextureLib.set_render_target_data(
        render_target_texture, raw_data, raw_data_width, raw_data_height, 
        raw_data_channel_num, use_srgb, texture_filter_value, bgr
    )


def get_render_target_raw_data(render_target_texture: unreal.TextureRenderTarget2D) -> List[int]:
    """
    RenderTarget2D에서 원시 데이터를 가져옵니다.
    
    Args:
        render_target_texture: 소스 RenderTarget2D
    
    Returns:
        RenderTarget2D의 원시 데이터 (uint8 배열)
    """
    return unreal.PythonTextureLib.get_render_target_raw_data(render_target_texture)


# 텍스처 데이터 추출
def get_texture2d_content(texture: unreal.Texture2D, mip_level: int) -> Optional[List[int]]:
    """
    Texture2D에서 원시 데이터를 가져옵니다.
    
    Args:
        texture: 소스 Texture2D
        mip_level: Texture2D의 mip 레벨
    
    Returns:
        Texture2D의 원시 데이터 (픽셀 순서는 BGRA), 실패 시 None
    """
    return unreal.PythonTextureLib.get_texture2d_content(texture, mip_level)