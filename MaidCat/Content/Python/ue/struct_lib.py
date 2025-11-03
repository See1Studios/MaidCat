"""
언리얼 엔진 Python 구조체 라이브러리 래퍼 모듈
==============================================

이 모듈은 언리얼 엔진 Python 구조체 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonStructLib 함수들:
- unreal.PythonStructLib.function_name → structlib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 구조체 라이브러리 래퍼들
# ===============================================================================

# 로깅 및 디버깅
def log_var_desc(struct: unreal.UserDefinedStruct) -> None:
    """
    주어진 사용자 정의 구조체의 세부 정보를 출력합니다.
    변수 이름, 카테고리, GUID, 핀 값 등을 포함합니다.
    """
    return unreal.PythonStructLib.log_var_desc(struct)


def log_var_desc_by_friendly_name(struct: unreal.UserDefinedStruct, var_name: str) -> None:
    """
    사용자 정의 구조체의 지정된 변수의 세부 정보를 출력합니다.
    
    Args:
        struct: 조회할 사용자 정의 구조체
        var_name: 지정된 변수의 친숙한 이름
    """
    return unreal.PythonStructLib.log_var_desc_by_friendly_name(struct, var_name)


# 변수 설명 및 정보 조회
def get_variable_description(struct: unreal.UserDefinedStruct, friendly_name: str) -> Dict[str, str]:
    """
    사용자 정의 구조체에서 지정된 변수의 VariableDescription 내용을 가져옵니다.
    
    Args:
        struct: 조회할 사용자 정의 구조체
        friendly_name: 지정된 변수의 친숙한 이름
    
    Returns:
        VariableDescription의 내용을 키-값 문자열 맵으로 반환
    """
    return unreal.PythonStructLib.get_variable_description(struct, friendly_name)


# GUID 관리
def get_guid_from_friendly_name(struct: unreal.UserDefinedStruct, friendly_name: str) -> unreal.Guid:
    """
    친숙한 이름으로 사용자 정의 구조체에서 지정된 변수의 GUID를 가져옵니다.
    
    Args:
        struct: 조회할 사용자 정의 구조체
        friendly_name: 변수의 친숙한 이름
    """
    return unreal.PythonStructLib.get_guid_from_friendly_name(struct, friendly_name)


def get_guid_from_property_name(name: unreal.Name) -> unreal.Guid:
    """
    프로퍼티 이름으로 사용자 정의 구조체에서 지정된 변수의 GUID를 가져옵니다.
    
    Args:
        name: 프로퍼티 변수의 프로퍼티 이름
    
    Note:
        프로퍼티 이름의 GUID는 어떤 구조체에 속하는지와 무관합니다.
    """
    return unreal.PythonStructLib.get_guid_from_property_name(name)


# 변수 이름 관리
def get_variable_names(struct: unreal.UserDefinedStruct) -> List[unreal.Name]:
    """
    지정된 사용자 정의 구조체의 변수 이름들을 가져옵니다.
    
    Returns:
        변수 이름 목록
    """
    return unreal.PythonStructLib.get_variable_names(struct)


def get_friendly_names(struct: unreal.UserDefinedStruct) -> List[str]:
    """
    지정된 사용자 정의 구조체의 친숙한 이름들을 가져옵니다.
    
    Returns:
        친숙한 이름 목록
    """
    return unreal.PythonStructLib.get_friendly_names(struct)


def is_unique_friendly_name(struct: unreal.UserDefinedStruct, friendly_name: str) -> bool:
    """
    친숙한 이름이 고유한지 확인합니다.
    
    Args:
        struct: 조회할 사용자 정의 구조체
        friendly_name: 새로운 친숙한 이름
    
    Returns:
        친숙한 이름이 구조체에서 고유하면 True
    """
    return unreal.PythonStructLib.is_unique_friendly_name(struct, friendly_name)


# 변수 추가
def add_variable(
    struct: unreal.UserDefinedStruct,
    category: unreal.Name,
    sub_category: unreal.Name,
    sub_category_object: unreal.Object,
    container_type_value: int,
    is_reference: bool = False,
    friendly_name: str = ""
) -> bool:
    """
    지정된 사용자 정의 구조체에 새로운 변수를 추가합니다.
    
    Args:
        struct: 수정할 사용자 정의 구조체
        category: 새 변수의 카테고리
        sub_category: 새 변수의 서브카테고리
        sub_category_object: 새 변수의 서브카테고리 오브젝트
        container_type_value: 컨테이너 타입 (0: single, 1: array, 2: set)
        is_reference: 새 변수가 참조로 전달되는지 여부
        friendly_name: 새 변수의 친숙한 이름
    
    Returns:
        새 변수가 추가되었으면 True
    
    Note:
        딕셔너리 변수를 추가하려면 add_directory_variable을 사용하세요.
        더 많은 예제는 웹사이트에서 찾을 수 있습니다.
    """
    return unreal.PythonStructLib.add_variable(
        struct, category, sub_category, sub_category_object, 
        container_type_value, is_reference, friendly_name
    )


def add_directory_variable(
    struct: unreal.UserDefinedStruct,
    category: unreal.Name,
    sub_category: unreal.Name,
    sub_category_object: unreal.Object,
    terminal_category: unreal.Name,
    terminal_sub_category: unreal.Name,
    terminal_sub_category_object: unreal.Object,
    is_reference: bool = False,
    friendly_name: str = ""
) -> bool:
    """
    지정된 사용자 정의 구조체에 새로운 딕셔너리 변수를 추가합니다.
    
    Args:
        struct: 수정할 사용자 정의 구조체
        category: 새 변수의 키 카테고리
        sub_category: 새 변수의 키 서브카테고리
        sub_category_object: 새 변수의 키 서브카테고리 오브젝트
        terminal_category: 새 변수의 값 카테고리
        terminal_sub_category: 새 변수의 값 서브카테고리
        terminal_sub_category_object: 새 변수의 값 서브카테고리 오브젝트
        is_reference: 새 변수가 참조로 전달되는지 여부
        friendly_name: 새 변수의 친숙한 이름
    
    Returns:
        새 변수가 추가되었으면 True
    """
    return unreal.PythonStructLib.add_directory_variable(
        struct, category, sub_category, sub_category_object,
        terminal_category, terminal_sub_category, terminal_sub_category_object,
        is_reference, friendly_name
    )


# 변수 제거 및 이름 변경
def remove_variable_by_name(struct: unreal.UserDefinedStruct, var_name: unreal.Name) -> bool:
    """
    프로퍼티 이름으로 사용자 정의 구조체에서 지정된 변수를 제거합니다.
    
    Args:
        struct: 수정할 사용자 정의 구조체
        var_name: 변수의 프로퍼티 이름
    """
    return unreal.PythonStructLib.remove_variable_by_name(struct, var_name)


def rename_variable(struct: unreal.UserDefinedStruct, var_guid: unreal.Guid, new_friendly_name: str) -> bool:
    """
    변수의 이름을 변경합니다.
    
    Args:
        struct: 수정할 사용자 정의 구조체
        var_guid: 변수의 GUID
        new_friendly_name: 새로운 친숙한 이름
    """
    return unreal.PythonStructLib.rename_variable(struct, var_guid, new_friendly_name)


# 기본값 관리
def change_variable_default_value(struct: unreal.UserDefinedStruct, var_guid: unreal.Guid, new_default_value: str) -> bool:
    """
    사용자 정의 구조체에서 지정된 변수의 기본값을 수정합니다.
    
    Args:
        struct: 수정할 사용자 정의 구조체
        var_guid: 변수의 GUID
        new_default_value: 문자열 형식의 새로운 기본값
    
    Returns:
        기본값이 설정되었으면 True
    """
    return unreal.PythonStructLib.change_variable_default_value(struct, var_guid, new_default_value)


def get_variable_default_value(struct: unreal.UserDefinedStruct, var_guid: unreal.Guid) -> str:
    """
    변수의 기본값을 가져옵니다.
    
    Args:
        struct: 조회할 사용자 정의 구조체
        var_guid: 변수의 GUID
    """
    return unreal.PythonStructLib.get_variable_default_value(struct, var_guid)