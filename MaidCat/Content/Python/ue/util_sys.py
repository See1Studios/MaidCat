"""
언리얼 엔진 에디터 유틸리티 서브시스템 라이브러리 래퍼 모듈
===============================================

이 모듈은 언리얼 엔진 에디터 유틸리티 서브시스템 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorUtilitySubsystem 함수들:
- unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem).function_name → utilsys.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# EditorUtilitySubsystem 인스턴스를 가져오는 헬퍼 함수
def _get_editor_utility_subsystem() -> unreal.EditorUtilitySubsystem:
    """EditorUtilitySubsystem 인스턴스를 가져옵니다."""
    return unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)


# ===============================================================================
# 에디터 유틸리티 서브시스템 래퍼들
# ===============================================================================

# 실행 관련 함수
def can_run(asset: unreal.Object) -> bool:
    """에셋을 실행할 수 있는지 확인합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.can_run(asset)


def try_run(asset: unreal.Object) -> bool:
    """에셋 실행을 시도합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.try_run(asset)


def try_run_class(object_class: type) -> bool:
    """클래스 실행을 시도합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.try_run_class(object_class)


# 탭 관리 함수
def close_tab_by_id(new_tab_id: unreal.Name) -> bool:
    """탭 ID로 기존 탭을 찾아 닫으려고 시도합니다. 닫을 탭을 찾으면 true를 반환합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.close_tab_by_id(new_tab_id)


def does_tab_exist(new_tab_id: unreal.Name) -> bool:
    """탭 ID로 기존 탭을 찾으려고 시도합니다. 탭을 찾으면 true를 반환합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.does_tab_exist(new_tab_id)


def spawn_registered_tab_by_id(new_tab_id: unreal.Name) -> bool:
    """탭 ID로 탭 스포너를 찾아 탭을 생성합니다. 매칭되는 탭 스포너를 찾으면 true를 반환합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_registered_tab_by_id(new_tab_id)


def unregister_tab_by_id(tab_id: unreal.Name) -> bool:
    """탭 ID로 이 서브시스템을 통해 등록된 탭을 닫고 등록 해제하려고 시도합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.unregister_tab_by_id(tab_id)


# 위젯 및 탭 생성/등록 함수
def find_utility_widget_from_blueprint(blueprint: unreal.EditorUtilityWidgetBlueprint) -> Optional[unreal.EditorUtilityWidget]:
    """에디터 유틸리티 위젯 블루프린트를 받아 그것이 생성하는 위젯을 가져옵니다. 위젯이 현재 탭에 없으면 null 포인터를 반환합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.find_utility_widget_from_blueprint(blueprint)


def register_tab_and_get_id(blueprint: unreal.EditorUtilityWidgetBlueprint) -> unreal.Name:
    """탭을 등록하고 ID를 가져옵니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.register_tab_and_get_id(blueprint)


def register_tab_and_get_id_generated_class(generated_widget_blueprint: type) -> unreal.Name:
    """생성된 클래스로 탭을 등록하고 ID를 가져옵니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.register_tab_and_get_id_generated_class(generated_widget_blueprint)


def spawn_and_register_tab(blueprint: unreal.EditorUtilityWidgetBlueprint) -> Optional[unreal.EditorUtilityWidget]:
    """탭을 생성하고 등록합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab(blueprint)


def spawn_and_register_tab_and_get_id(blueprint: unreal.EditorUtilityWidgetBlueprint) -> Tuple[Optional[unreal.EditorUtilityWidget], unreal.Name]:
    """탭을 생성하고 등록하며 ID를 가져옵니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab_and_get_id(blueprint)


def spawn_and_register_tab_and_get_id_generated_class(generated_widget_blueprint: type) -> Tuple[Optional[unreal.EditorUtilityWidget], unreal.Name]:
    """생성된 클래스로 탭을 생성하고 등록하며 ID를 가져옵니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab_and_get_id_generated_class(generated_widget_blueprint)


def spawn_and_register_tab_generated_class(generated_widget_blueprint: type) -> Optional[unreal.EditorUtilityWidget]:
    """생성된 클래스로 탭을 생성하고 등록합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab_generated_class(generated_widget_blueprint)


def spawn_and_register_tab_with_id(blueprint: unreal.EditorUtilityWidgetBlueprint, tab_id: unreal.Name) -> Optional[unreal.EditorUtilityWidget]:
    """SpawnAndRegisterTabAndGetID와 달리 Python 스크립트나 BP에서 TabID를 제공하면서 탭을 생성할 수 있습니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab_with_id(blueprint, tab_id)


def spawn_and_register_tab_with_id_generated_class(generated_widget_blueprint: type, tab_id: unreal.Name) -> Optional[unreal.EditorUtilityWidget]:
    """SpawnAndRegisterTabAndGetID와 달리 Python 스크립트나 BP에서 TabID를 제공하면서 생성된 클래스로 탭을 생성할 수 있습니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.spawn_and_register_tab_with_id_generated_class(generated_widget_blueprint, tab_id)


# 태스크 관리
def register_and_execute_task(new_task: unreal.EditorUtilityTask, optional_parent_task: Optional[unreal.EditorUtilityTask] = None) -> None:
    """태스크를 등록하고 실행합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.register_and_execute_task(new_task, optional_parent_task)


# 에셋 인스턴스 관리
def release_instance_of_asset(asset: unreal.Object) -> None:
    """시작 오브젝트가 가비지 컬렉션되도록 허용합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.release_instance_of_asset(asset)


# PIE 이벤트 프로퍼티들
def get_on_begin_pie():
    """PIE 시작 이벤트를 블루프린트에 노출합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.on_begin_pie


def get_on_end_pie():
    """PIE 종료 이벤트를 블루프린트에 노출합니다."""
    subsystem = _get_editor_utility_subsystem()
    return subsystem.on_end_pie