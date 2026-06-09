"""
Unreal 오브젝트 배열 정렬 유틸리티.

주요 목적:
- 오브젝트 내부 Data 구조체의 Group 문자열 기준으로 그룹 정렬
- 그룹 내부 항목 정렬
- 그룹의 첫 번째 오브젝트에만 IsFirst 플래그 기록

특징:
- Data/Group/IsFirst 프로퍼티명 후보를 튜플로 받아 유연하게 동작
- UserDefinedStruct에서 필드명이 변형된 경우 export_text 파싱으로 Group 추출 보완
"""

from collections import defaultdict
import re


def _get_prop(obj, candidates, default=None):
    if obj is None:
        return default
    for name in candidates:
        try:
            return obj.get_editor_property(name)
        except Exception:
            pass
    return default


def _set_prop(obj, candidates, value):
    if obj is None:
        return False
    for name in candidates:
        try:
            obj.set_editor_property(name, value)
            return True
        except Exception:
            pass
    return False


def _export_text_safe(value):
    try:
        return value.export_text()
    except Exception:
        return ""


def _extract_group_from_data_struct(data_struct, group_prop_candidates=("Group", "group")):
    if data_struct is None:
        return ""

    value = _get_prop(data_struct, group_prop_candidates, None)
    if value is not None:
        return str(value).strip()

    # Fallback for UserDefinedStruct fields that may be name-mangled in Python.
    text = _export_text_safe(data_struct)
    if not text:
        return ""

    quoted = re.search(r'(?i)\bgroup[^=,\)]*\s*=\s*"([^"]*)"', text)
    if quoted:
        return quoted.group(1).strip()

    plain = re.search(r"(?i)\bgroup[^=,\)]*\s*=\s*([^,\)]+)", text)
    if plain:
        return plain.group(1).strip().strip('"')

    return ""


def _default_item_sort_key(obj):
    return obj.get_name().lower()


def sort_by_data_group(
    objects,
    in_group_item_key=None,
    data_prop_candidates=("Data", "data"),
    group_prop_candidates=("Group", "group"),
):
    """Data.Group 기준으로 정렬된 리스트를 반환한다.

    정렬 순서:
    1) Group 문자열 오름차순(대소문자 무시)
    2) 동일 Group 내 항목 정렬(in_group_item_key)

    Args:
        objects: Unreal Object 배열(list 또는 TArray).
        in_group_item_key: 그룹 내부 정렬 키 함수. 기본값은 obj.get_name().lower().
        data_prop_candidates: 오브젝트의 Data 구조체 프로퍼티 후보명.
        group_prop_candidates: Data 구조체의 Group 프로퍼티 후보명.

    Returns:
        tuple[list, dict]: (정렬된 1차원 리스트, 그룹별 dict)

    Example:
        sorted_list, grouped = sort_by_data_group(in_list)
    """
    if in_group_item_key is None:
        in_group_item_key = _default_item_sort_key

    grouped = defaultdict(list)

    for obj in objects:
        data_struct = _get_prop(obj, data_prop_candidates, None)
        group = _extract_group_from_data_struct(data_struct, group_prop_candidates)
        grouped[group].append(obj)

    result = []
    for group_name in sorted(grouped.keys(), key=lambda s: s.lower()):
        grouped[group_name].sort(key=in_group_item_key)
        result.extend(grouped[group_name])

    return result, grouped


def sort_by_data_group_and_mark_first(
    objects,
    in_group_item_key=None,
    data_prop_candidates=("Data", "data"),
    group_prop_candidates=("Group", "group"),
    is_first_prop_candidates=("IsFirst", "is_first"),
):
    """Data.Group 기준 정렬 후 그룹 첫 항목에 IsFirst=True를 기록한다.

    동작:
    - sort_by_data_group()로 먼저 정렬
    - 그룹이 바뀌는 경계의 첫 오브젝트만 IsFirst=True
    - 나머지 오브젝트는 IsFirst=False

    Args:
        objects: Unreal Object 배열(list 또는 TArray).
        in_group_item_key: 그룹 내부 정렬 키 함수.
        data_prop_candidates: 오브젝트의 Data 구조체 프로퍼티 후보명.
        group_prop_candidates: Data 구조체의 Group 프로퍼티 후보명.
        is_first_prop_candidates: 오브젝트의 IsFirst 프로퍼티 후보명.

    Returns:
        tuple[list, dict]: (정렬된 1차원 리스트, 그룹별 dict)

    Example:
        out_list, grouped = sort_by_data_group_and_mark_first(in_list)
    """
    sorted_list, grouped = sort_by_data_group(
        objects=objects,
        in_group_item_key=in_group_item_key,
        data_prop_candidates=data_prop_candidates,
        group_prop_candidates=group_prop_candidates,
    )

    previous_group_lower = None
    for index, obj in enumerate(sorted_list):
        data_struct = _get_prop(obj, data_prop_candidates, None)
        current_group = _extract_group_from_data_struct(data_struct, group_prop_candidates)
        current_group_lower = current_group.lower()
        is_first = index == 0 or current_group_lower != previous_group_lower

        _set_prop(obj, is_first_prop_candidates, is_first)
        previous_group_lower = current_group_lower

    return sorted_list, grouped