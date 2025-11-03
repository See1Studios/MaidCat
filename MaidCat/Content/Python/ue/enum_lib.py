"""
언리얼 엔진 Python 열거형 라이브러리 래퍼 모듈
==============================================

이 모듈은 언리얼 엔진 Python 열거형 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonEnumLib 함수들:
- unreal.PythonEnumLib.function_name → enum_lib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 열거형 라이브러리 래퍼들
# ===============================================================================

# 열거형 표시 이름 관리
def get_display_name_map(enum: unreal.UserDefinedEnum) -> Dict[unreal.Name, unreal.Text]:
    """
    주어진 사용자 정의 열거형의 표시 이름 맵을 가져옵니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
    
    Returns:
        키: 원시 열거형 번호, 값: 표시 이름인 맵 (순서 없음)
    """
    return unreal.PythonEnumLib.get_display_name_map(enum)


def set_enum_items(enum: unreal.UserDefinedEnum, display_names: List[str]) -> None:
    """
    주어진 사용자 정의 열거형의 항목들을 설정합니다.
    
    Args:
        enum: 수정할 사용자 정의 열거형
        display_names: 열거형 항목들의 표시 이름들. 원시 열거형 이름은 자동으로 생성됩니다.
    """
    return unreal.PythonEnumLib.set_enum_items(enum, display_names)


# 열거형 기본 정보
def get_enum_len(enum: unreal.UserDefinedEnum) -> int:
    """주어진 사용자 정의 열거형의 항목 수를 가져옵니다."""
    return unreal.PythonEnumLib.get_enum_len(enum)


# 인덱스별 정보 조회
def get_display_name_by_index(enum: unreal.UserDefinedEnum, index: int) -> str:
    """
    주어진 사용자 정의 열거형의 표시 이름을 가져옵니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
        index: 열거형 항목의 인덱스 (0부터 시작)
    """
    return unreal.PythonEnumLib.get_display_name_by_index(enum, index)


def set_display_name(enum: unreal.UserDefinedEnum, index: int, new_display_name: str) -> bool:
    """
    주어진 사용자 정의 열거형의 표시 이름을 설정합니다.
    
    Args:
        enum: 수정할 사용자 정의 열거형
        index: 열거형 항목의 인덱스 (0부터 시작)
        new_display_name: 새로운 표시 이름
    
    Returns:
        새 이름이 설정되었으면 True
    """
    return unreal.PythonEnumLib.set_display_name(enum, index, new_display_name)


def get_description_by_index(enum: unreal.UserDefinedEnum, index: int) -> str:
    """
    주어진 사용자 정의 열거형 항목의 설명을 가져옵니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
        index: 열거형 항목의 인덱스 (0부터 시작)
    """
    return unreal.PythonEnumLib.get_description_by_index(enum, index)


def set_description_by_index(enum: unreal.UserDefinedEnum, index: int, description: str) -> bool:
    """
    주어진 사용자 정의 열거형 항목의 설명을 설정합니다.
    
    Args:
        enum: 수정할 사용자 정의 열거형
        index: 열거형 항목의 인덱스 (0부터 시작)
        description: 열거형 항목의 설명
    
    Returns:
        설명이 설정되었으면 True
    """
    return unreal.PythonEnumLib.set_description_by_index(enum, index, description)


def get_name_by_index(enum: unreal.UserDefinedEnum, index: int) -> str:
    """
    주어진 사용자 정의 열거형의 원시 이름을 가져옵니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
        index: 열거형 항목의 인덱스 (0부터 시작)
    """
    return unreal.PythonEnumLib.get_name_by_index(enum, index)


# 열거형 항목 이동
def move_enum_item(enum: unreal.UserDefinedEnum, initial_index: int, target_index: int) -> None:
    """
    주어진 초기 인덱스의 열거자를 새로운 대상 인덱스로 이동시키고, 필요에 따라 다른 열거자들을 이동시킵니다.
    
    Args:
        enum: 수정할 사용자 정의 열거형
        initial_index: 열거형 항목의 초기 인덱스
        target_index: 열거형 항목의 대상 인덱스
    
    Example:
        열거형 [A, B, C, D, E]에서 인덱스 1을 인덱스 3으로 이동하면 [A, C, D, B, E]가 됩니다.
    """
    return unreal.PythonEnumLib.move_enum_item(enum, initial_index, target_index)


# 비트플래그 관리
def is_bitflags_type(enum: unreal.UserDefinedEnum) -> bool:
    """
    enumerator-as-bitflags 메타데이터가 설정되어 있는지 확인합니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
    
    Returns:
        비트플래그 여부
    """
    return unreal.PythonEnumLib.is_bitflags_type(enum)


def set_bitflags_type(enum: unreal.UserDefinedEnum, bitflags_type: bool) -> None:
    """
    주어진 사용자 정의 열거형의 비트플래그 상태를 설정합니다.
    
    Args:
        enum: 수정할 사용자 정의 열거형
        bitflags_type: 비트플래그 값
    """
    return unreal.PythonEnumLib.set_bitflags_type(enum, bitflags_type)


# C++ 형식 정보
def get_cpp_form(enum: unreal.UserDefinedEnum) -> int:
    """
    주어진 사용자 정의 열거형의 CppForm 값을 정수로 가져옵니다.
    
    Args:
        enum: 조회할 사용자 정의 열거형
    
    Returns:
        ECppForm 값 (정수): 0: Regular, 1: Namespaced, 2: EnumClass
    """
    return unreal.PythonEnumLib.get_cpp_form(enum)