"""
언리얼 엔진 에디터 액터 서브시스템 라이브러리 래퍼 모듈
===============================================

이 모듈은 언리얼 엔진 에디터 액터 서브시스템 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorActorSubsystem 함수들:
- unreal.get_editor_subsystem(unreal.EditorActorSubsystem).function_name → actorsys.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# EditorActorSubsystem 인스턴스를 가져오는 헬퍼 함수
def _get_editor_actor_subsystem() -> unreal.EditorActorSubsystem:
    """EditorActorSubsystem 인스턴스를 가져옵니다."""
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


# ===============================================================================
# 에디터 액터 서브시스템 래퍼들
# ===============================================================================

# 액터 선택 관리
def clear_actor_selection_set() -> None:
    """선택 세트에서 모든 액터를 제거합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.clear_actor_selection_set()


def select_all(world: unreal.World) -> None:
    """주어진 월드에서 숨겨진 액터를 제외한 모든 액터와 BSP 모델을 선택합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.select_all(world)


def select_all_children(recurse_children: bool) -> None:
    """현재 선택된 액터의 모든 자식 액터를 선택합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.select_all_children(recurse_children)


def select_nothing() -> None:
    """에디터에서 아무것도 선택하지 않습니다 (선택 해제)."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.select_nothing()


def invert_selection(world: unreal.World) -> None:
    """주어진 월드에서 선택을 반전시킵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.invert_selection(world)


def set_actor_selection_state(actor: unreal.Actor, should_be_selected: bool) -> None:
    """선택된 액터의 선택 상태를 설정합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.set_actor_selection_state(actor, should_be_selected)


def get_selected_level_actors() -> Any:
    """월드 에디터에서 선택된 모든 로드된 액터를 찾습니다. PIE, PreviewEditor 등에서 대기 중인 액터는 제외됩니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.get_selected_level_actors()


def set_selected_level_actors(actors_to_select: Any) -> None:
    """현재 월드 에디터 선택을 지우고 제공된 액터들을 선택합니다. PIE, PreviewEditor 등에서 대기 중인 액터는 제외됩니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.set_selected_level_actors(actors_to_select)


# 액터 정보 조회
def get_all_level_actors() -> Any:
    """월드 에디터에서 로드된 모든 액터를 찾습니다. PIE, PreviewEditor 등에서 대기 중인 액터는 제외됩니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.get_all_level_actors()


def get_all_level_actors_components() -> Any:
    """월드 에디터에서 액터가 소유한 모든 로드된 ActorComponent를 찾습니다. PIE, PreviewEditor 등에서 대기 중인 액터는 제외됩니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.get_all_level_actors_components()


def get_actor_reference(path_to_actor: str) -> Optional[unreal.Actor]:
    """현재 에디터 월드에서 PathToActor로 지정된 액터를 찾으려고 시도합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.get_actor_reference(path_to_actor)


# 액터 생성
def spawn_actor_from_class(actor_class: type, location: unreal.Vector, 
                          rotation: unreal.Rotator = unreal.Rotator(0, 0, 0), 
                          transient: bool = False) -> Optional[unreal.Actor]:
    """액터를 생성하고 월드 에디터에 배치합니다. 블루프린트나 클래스에서 생성할 수 있습니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.spawn_actor_from_class(actor_class, location, rotation, transient)


def spawn_actor_from_object(object_to_use: unreal.Object, location: unreal.Vector,
                           rotation: unreal.Rotator = unreal.Rotator(0, 0, 0),
                           transient: bool = False) -> Optional[unreal.Actor]:
    """액터를 생성하고 월드 에디터에 배치합니다. Factory, Archetype, Blueprint, Class 또는 Asset에서 생성할 수 있습니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.spawn_actor_from_object(object_to_use, location, rotation, transient)


# 액터 삭제
def destroy_actor(actor_to_destroy: unreal.Actor) -> bool:
    """월드 에디터에서 액터를 삭제합니다. 에디터에 액터가 삭제되었음을 알립니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.destroy_actor(actor_to_destroy)


def destroy_actors(actors_to_destroy: Any) -> bool:
    """월드 에디터에서 액터들을 삭제합니다. 에디터에 액터들이 삭제되었음을 알립니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.destroy_actors(actors_to_destroy)


def delete_selected_actors(world: unreal.World) -> None:
    """주어진 월드에서 선택된 모든 액터를 삭제합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.delete_selected_actors(world)


# 액터 복제
def duplicate_actor(actor_to_duplicate: unreal.Actor, 
                   to_world: Optional[unreal.World] = None,
                   offset: unreal.Vector = unreal.Vector(0, 0, 0)) -> Optional[unreal.Actor]:
    """월드 에디터에서 액터를 복제합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.duplicate_actor(actor_to_duplicate, to_world, offset)


def duplicate_actors(actors_to_duplicate: Any,
                    to_world: Optional[unreal.World] = None,
                    offset: unreal.Vector = unreal.Vector(0, 0, 0)) -> Any:
    """월드 에디터에서 액터들을 복제합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.duplicate_actors(actors_to_duplicate, to_world, offset)


def duplicate_selected_actors(world: unreal.World) -> None:
    """주어진 월드에서 선택된 모든 액터를 복제합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.duplicate_selected_actors(world)


# 액터 변환
def convert_actors(actors: Any, actor_class: type, static_mesh_package_path: str) -> Any:
    """레벨에서 제공된 모든 액터를 ActorClass 타입의 새 액터로 교체합니다. 제공된 모든 액터를 삭제합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.convert_actors(actors, actor_class, static_mesh_package_path)


# 액터 변형 설정
def set_actor_transform(actor: unreal.Actor, world_transform: unreal.Transform) -> bool:
    """가능한 경우 주어진 액터의 월드 변형을 설정합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.set_actor_transform(actor, world_transform)


def set_component_transform(scene_component: unreal.SceneComponent, world_transform: unreal.Transform) -> bool:
    """가능한 경우 주어진 컴포넌트의 월드 변형을 설정합니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.set_component_transform(scene_component, world_transform)


# 이벤트 프로퍼티들 (콜백 관리)
def get_on_actor_label_changed():
    """액터 라벨 변경 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_actor_label_changed


def get_on_delete_actors_begin():
    """액터 삭제 시작 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_delete_actors_begin


def get_on_delete_actors_end():
    """액터 삭제 완료 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_delete_actors_end


def get_on_duplicate_actors_begin():
    """액터 복제 시작 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_duplicate_actors_begin


def get_on_duplicate_actors_end():
    """액터 복제 완료 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_duplicate_actors_end


def get_on_edit_copy_actors_begin():
    """액터 복사 편집 시작 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_copy_actors_begin


def get_on_edit_copy_actors_end():
    """액터 복사 편집 완료 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_copy_actors_end


def get_on_edit_cut_actors_begin():
    """액터 잘라내기 편집 시작 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_cut_actors_begin


def get_on_edit_cut_actors_end():
    """액터 잘라내기 편집 완료 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_cut_actors_end


def get_on_edit_paste_actors_begin():
    """액터 붙여넣기 편집 시작 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_paste_actors_begin


def get_on_edit_paste_actors_end():
    """액터 붙여넣기 편집 완료 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_edit_paste_actors_end


def get_on_new_actors_dropped():
    """새 액터 드롭 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_new_actors_dropped


def get_on_new_actors_placed():
    """새 액터 배치 이벤트를 가져옵니다."""
    subsystem = _get_editor_actor_subsystem()
    return subsystem.on_new_actors_placed