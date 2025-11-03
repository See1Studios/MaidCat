"""
언리얼 엔진 Python 데이터테이블 라이브러리 래퍼 모듈
=================================================

이 모듈은 언리얼 엔진 Python 데이터테이블 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonDataTableLib 함수들:
- unreal.PythonDataTableLib.function_name → datalib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 데이터테이블 라이브러리 래퍼들
# ===============================================================================

# 데이터테이블 구조 정보
def get_data_table_struct_path(data_table: unreal.DataTable) -> str:
    """주어진 데이터테이블의 행 구조체 경로를 가져옵니다."""
    return unreal.PythonDataTableLib.get_data_table_struct_path(data_table)


def get_data_table_struct(data_table: unreal.DataTable) -> unreal.ScriptStruct:
    """주어진 데이터테이블의 행 구조체를 가져옵니다."""
    return unreal.PythonDataTableLib.get_data_table_struct(data_table)


# 데이터테이블 내용 조회
def get_table_as_json(data_table: unreal.DataTable) -> str:
    """데이터테이블 내용을 JSON 형식으로 가져옵니다."""
    return unreal.PythonDataTableLib.get_table_as_json(data_table)


def get_row_names(data_table: unreal.DataTable) -> List[unreal.Name]:
    """주어진 데이터테이블의 행 이름들을 가져옵니다."""
    return unreal.PythonDataTableLib.get_row_names(data_table)


def get_column_names(data_table: unreal.DataTable, friendly_name: bool = True, include_name: bool = False) -> List[unreal.Name]:
    """
    주어진 데이터테이블의 열 이름들을 가져옵니다.
    
    Args:
        data_table: 조회할 데이터테이블
        friendly_name: 친숙한 이름 또는 원시 이름 가져올지 여부
        include_name: 행 이름 열을 포함할지 여부
    """
    return unreal.PythonDataTableLib.get_column_names(data_table, friendly_name, include_name)


def get_shape(data_table: unreal.DataTable) -> List[int]:
    """
    주어진 데이터테이블의 형태를 가져옵니다.
    제목과 행 이름은 포함되지 않습니다.
    
    Returns:
        [행 수, 열 수] 형태의 리스트
    """
    return unreal.PythonDataTableLib.get_shape(data_table)


# 행 관리
def remove_row(data_table: unreal.DataTable, row_name: unreal.Name) -> bool:
    """주어진 데이터테이블에서 지정된 행을 제거합니다."""
    return unreal.PythonDataTableLib.remove_row(data_table, row_name)


def add_row(data_table: unreal.DataTable, row_name: unreal.Name) -> bool:
    """주어진 데이터테이블에 행을 추가합니다."""
    return unreal.PythonDataTableLib.add_row(data_table, row_name)


def duplicate_row(data_table: unreal.DataTable, source_row_name: unreal.Name, row_name: unreal.Name) -> bool:
    """주어진 데이터테이블에서 행을 복제합니다."""
    return unreal.PythonDataTableLib.duplicate_row(data_table, source_row_name, row_name)


def rename_row(data_table: unreal.DataTable, old_name: unreal.Name, new_name: unreal.Name) -> bool:
    """주어진 데이터테이블에서 지정된 행의 이름을 변경합니다."""
    return unreal.PythonDataTableLib.rename_row(data_table, old_name, new_name)


def reset_row(data_table: unreal.DataTable, row_name: unreal.Name) -> bool:
    """주어진 데이터테이블에서 지정된 행을 기본값으로 리셋합니다."""
    return unreal.PythonDataTableLib.reset_row(data_table, row_name)


def move_row(data_table: unreal.DataTable, row_name: unreal.Name, up: bool, num_rows_to_move_by: int = 1) -> bool:
    """
    주어진 데이터테이블에서 지정된 행을 이동합니다.
    
    Args:
        data_table: 수정할 데이터테이블
        row_name: 이동할 '소스 행'의 행 이름
        up: 위로 이동할지 여부
        num_rows_to_move_by: 이동할 행의 수
    """
    return unreal.PythonDataTableLib.move_row(data_table, row_name, up, num_rows_to_move_by)


# 행/열 이름 조회
def get_row_name(data_table: unreal.DataTable, row_id: int) -> unreal.Name:
    """데이터테이블에서 지정된 행의 행 이름을 가져옵니다."""
    return unreal.PythonDataTableLib.get_row_name(data_table, row_id)


def get_column_name(data_table: unreal.DataTable, column_id: int, friendly_name: bool = True) -> unreal.Name:
    """데이터테이블에서 지정된 열의 열 이름을 가져옵니다."""
    return unreal.PythonDataTableLib.get_column_name(data_table, column_id, friendly_name)


# 데이터 조회
def get_flatten_data_table(data_table: unreal.DataTable, include_header: bool = False) -> List[str]:
    """
    데이터테이블의 내용을 1차원 문자열 리스트로 가져옵니다.
    
    Args:
        data_table: 조회할 데이터테이블
        include_header: 제목과 행 이름 열을 포함할지 여부
    
    Note:
        include_header가 False인 경우 반환값의 길이는 행수 * 열수와 같습니다.
    """
    return unreal.PythonDataTableLib.get_flatten_data_table(data_table, include_header)


def get_property_as_string(data_table: unreal.DataTable, row_name: unreal.Name, column_name: unreal.Name) -> str:
    """데이터테이블에서 지정된 셀의 값을 문자열로 가져옵니다."""
    return unreal.PythonDataTableLib.get_property_as_string(data_table, row_name, column_name)


def get_property_as_string_at(data_table: unreal.DataTable, row_id: int, column_id: int) -> str:
    """
    데이터테이블에서 지정된 셀의 값을 문자열로 가져옵니다.
    
    Args:
        data_table: 조회할 데이터테이블
        row_id: 셀의 행 인덱스 (제목 포함하지 않음)
        column_id: 셀의 열 인덱스 (제목 포함하지 않음)
    """
    return unreal.PythonDataTableLib.get_property_as_string_at(data_table, row_id, column_id)


# 데이터 설정
def set_property_by_string(data_table: unreal.DataTable, row_name: unreal.Name, column_name: unreal.Name, value_as_string: str) -> bool:
    """데이터테이블에서 지정된 셀의 속성을 설정합니다."""
    return unreal.PythonDataTableLib.set_property_by_string(data_table, row_name, column_name, value_as_string)


def set_property_by_string_at(data_table: unreal.DataTable, row_index: int, column_index: int, value_as_string: str) -> bool:
    """
    데이터테이블에서 지정된 셀의 속성을 설정합니다.
    
    Args:
        data_table: 조회할 데이터테이블
        row_index: 셀의 행 인덱스 (제목 포함하지 않음)
        column_index: 셀의 열 인덱스 (제목 포함하지 않음)
        value_as_string: 문자열 형식의 새로운 속성값
    """
    return unreal.PythonDataTableLib.set_property_by_string_at(data_table, row_index, column_index, value_as_string)