"""
언리얼 엔진 Python 머티리얼 라이브러리 래퍼 모듈
==============================================

이 모듈은 언리얼 엔진 Python 머티리얼 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonMaterialLib 함수들:
- unreal.PythonMaterialLib.function_name → matlib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python 머티리얼 라이브러리 래퍼들
# ===============================================================================

# 스태틱 스위치 파라미터 관리
def get_static_switch_parameter_values(material_interface: unreal.MaterialInterface) -> Any:
    """머티리얼 인스턴스의 스태틱 스위치 정보를 가져옵니다."""
    return unreal.PythonMaterialLib.get_static_switch_parameter_values(material_interface)


def set_static_switch_parameter_value(material_instance: unreal.MaterialInstanceConstant, switch_name: str, enabled: bool, update_static_permutation: bool = True) -> None:
    """머티리얼 인스턴스의 스태틱 스위치 정보를 설정합니다."""
    return unreal.PythonMaterialLib.set_static_switch_parameter_value(material_instance, switch_name, enabled, update_static_permutation)


def set_static_switch_parameters_values(material_instance: unreal.MaterialInstanceConstant, switch_names: Any, values: Any, overrides: Any) -> None:
    """머티리얼 인스턴스의 스태틱 스위치 상태를 일괄 설정합니다."""
    return unreal.PythonMaterialLib.set_static_switch_parameters_values(material_instance, switch_names, values, overrides)


def get_mf_static_switch_parameter(material_function: unreal.MaterialFunction) -> Any:
    """머티리얼 함수의 스태틱 스위치 정보를 가져옵니다."""
    return unreal.PythonMaterialLib.get_mf_static_switch_parameter(material_function)


def get_static_parameters_summary(material_instance: unreal.MaterialInstance) -> Tuple[Any, Any]:
    """머티리얼 인스턴스의 각 StaticSwitchParameter 수를 가져옵니다."""
    return unreal.PythonMaterialLib.get_static_parameters_summary(material_instance)


# 머티리얼 정보 및 로깅
def log_mat(material_interface: unreal.MaterialInterface) -> None:
    """머티리얼의 모든 연결을 로그로 출력합니다."""
    return unreal.PythonMaterialLib.log_mat(material_interface)


def log_mf(material_function: unreal.MaterialFunction) -> None:
    """머티리얼 함수의 모든 연결을 로그로 출력합니다."""
    return unreal.PythonMaterialLib.log_mf(material_function)


def log_material_expression(material_expression: unreal.MaterialExpression) -> None:
    """MaterialExpression의 입력, 출력 등을 포함한 세부 정보를 로그로 출력합니다."""
    return unreal.PythonMaterialLib.log_material_expression(material_expression)


def log_editing_nodes(material_or_mf: unreal.Object) -> None:
    """머티리얼 또는 머티리얼 함수의 세부 정보를 로그로 출력합니다."""
    return unreal.PythonMaterialLib.log_editing_nodes(material_or_mf)


# 머티리얼 익스프레션 관리
def get_material_expressions(material_interface: unreal.MaterialInterface) -> Any:
    """머티리얼의 모든 머티리얼 익스프레션을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_expressions(material_interface)


def get_all_referenced_expressions(material_interface: unreal.MaterialInterface, feature_level: int = 3) -> Any:
    """지정된 피처 레벨을 가진 머티리얼의 머티리얼 익스프레션을 가져옵니다."""
    return unreal.PythonMaterialLib.get_all_referenced_expressions(material_interface, feature_level)


def get_material_function_expressions(material_function: unreal.MaterialFunction, recursive: bool = False) -> Any:
    """머티리얼 함수의 모든 익스프레션을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_function_expressions(material_function, recursive)


def get_material_function_output_expressions(material_function: unreal.MaterialFunction) -> Any:
    """머티리얼 함수의 모든 출력 익스프레션을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_function_output_expressions(material_function)


def get_selected_material_nodes(material: unreal.Material) -> Any:
    """머티리얼 에디터에서 선택된 노드를 가져옵니다."""
    return unreal.PythonMaterialLib.get_selected_material_nodes(material)


def get_selected_nodes_in_material_editor(material_or_mf: unreal.Object) -> Any:
    """머티리얼 에디터에서 선택된 노드를 가져옵니다."""
    return unreal.PythonMaterialLib.get_selected_nodes_in_material_editor(material_or_mf)


def get_material_expression_id(expression: unreal.MaterialExpression) -> unreal.Guid:
    """머티리얼 익스프레션의 ParameterExpressionId를 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_expression_id(expression)


# 머티리얼 익스프레션 핀 정보
def get_material_expression_input_names(expression: unreal.MaterialExpression, raw_name: bool = False) -> Any:
    """머티리얼 익스프레션의 입력 핀 이름을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_expression_input_names(expression, raw_name)


def get_material_expression_output_names(expression: unreal.MaterialExpression) -> Any:
    """머티리얼 익스프레션의 출력 핀 이름을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_expression_output_names(expression)


def get_material_expression_captions(expression: unreal.MaterialExpression) -> Any:
    """머티리얼 익스프레션의 캡션을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_expression_captions(expression)


# 머티리얼 연결 관리
def get_material_connections(material_interface: unreal.MaterialInterface) -> Any:
    """머티리얼의 모든 연결을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_connections(material_interface)


def get_material_function_connections(material_function: unreal.MaterialFunction) -> Any:
    """머티리얼 함수의 모든 연결을 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_function_connections(material_function)


def connect_material_expressions(from_expression: unreal.MaterialExpression, from_output_name: str, to_expression: unreal.MaterialExpression, to_input_name: str) -> bool:
    """두 머티리얼 익스프레션 간의 연결을 생성합니다."""
    return unreal.PythonMaterialLib.connect_material_expressions(from_expression, from_output_name, to_expression, to_input_name)


def disconnect_expression(expression: unreal.MaterialExpression, input_name: str) -> bool:
    """머티리얼 익스프레션의 입력 연결을 해제합니다."""
    return unreal.PythonMaterialLib.disconnect_expression(expression, input_name)


def connect_material_property(from_expression: unreal.MaterialExpression, from_output_name: str, material_property_str: str) -> bool:
    """머티리얼 익스프레션 출력을 머티리얼 프로퍼티 입력 중 하나에 연결합니다."""
    return unreal.PythonMaterialLib.connect_material_property(from_expression, from_output_name, material_property_str)


def disconnect_material_property(material: unreal.Material, material_property_str: str) -> bool:
    """머티리얼 프로퍼티 입력 연결을 해제합니다."""
    return unreal.PythonMaterialLib.disconnect_material_property(material, material_property_str)


# 머티리얼 프로퍼티 및 GUID 관리
def get_material_proper_str_from_guid(guid: unreal.Guid) -> str:
    """GUID에서 EMaterialProperty를 문자열 형식으로 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_proper_str_from_guid(guid)


def gen_guid_from_material_property_str(property_str: str) -> unreal.Guid:
    """EMaterialProperty에서 GUID를 생성합니다."""
    return unreal.PythonMaterialLib.gen_guid_from_material_property_str(property_str)


# 머티리얼 설정
def set_shading_model(material: unreal.Material, shading_model_value: int) -> None:
    """숨겨진 셰이딩 모델을 위한 머티리얼의 셰이딩 모델을 설정합니다."""
    return unreal.PythonMaterialLib.set_shading_model(material, shading_model_value)


# 머티리얼 어트리뷰트 관리
def add_input_at_expression_set_material_attributes(expression_set_material_attributes: unreal.MaterialExpressionSetMaterialAttributes, property_str: str) -> None:
    """머티리얼 익스프레션 'SetMaterialAttributes'에 Attribute Get Type 핀을 추가합니다."""
    return unreal.PythonMaterialLib.add_input_at_expression_set_material_attributes(expression_set_material_attributes, property_str)


def add_output_at_expression_get_material_attributes(expression_get_material_attributes: unreal.MaterialExpressionGetMaterialAttributes, property_str: str) -> None:
    """머티리얼 익스프레션 'GetMaterialAttributes'에 Attribute Get Type 핀을 추가합니다."""
    return unreal.PythonMaterialLib.add_output_at_expression_get_material_attributes(expression_get_material_attributes, property_str)


# 머티리얼 콘텐츠 및 코드 생성
def get_hlsl_code(material_interface: unreal.MaterialInterface) -> Optional[str]:
    """머티리얼의 HLSL 코드를 가져옵니다."""
    return unreal.PythonMaterialLib.get_hlsl_code(material_interface)


def get_shader_map_info(material: unreal.Material, platform_str: str, detail: bool = False) -> str:
    """ShaderMap 정보를 문자열 형식으로 가져옵니다."""
    return unreal.PythonMaterialLib.get_shader_map_info(material, platform_str, detail)


def get_material_content(material: unreal.Material, only_editable: bool = True, include_comments: bool = False) -> str:
    """머티리얼의 콘텐츠를 JSON 형식으로 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_content(material, only_editable, include_comments)


def get_material_function_content(material_function: unreal.MaterialFunction, only_editable: bool = True, include_comments: bool = False) -> str:
    """머티리얼 함수의 콘텐츠를 JSON 형식으로 가져옵니다."""
    return unreal.PythonMaterialLib.get_material_function_content(material_function, only_editable, include_comments)