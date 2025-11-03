"""
언리얼 엔진 레벨/월드 에디터 라이브러리 래퍼 모듈
============================================

이 모듈은 언리얼 엔진 레벨 에디터 유틸리티 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

EditorLevelLibrary 함수들:
- unreal.EditorLevelLibrary.function_name → levellib.function_name

PythonLevelLib 함수들 (외부 라이브러리):
- unreal.PythonLevelLib.function_name → levellib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# 에디터 레벨 라이브러리 래퍼들
# ===============================================================================

# 액터 선택 및 관리
def clear_actor_selection_set() -> None:
    """액터 선택 세트를 지웁니다."""
    return unreal.EditorLevelLibrary.clear_actor_selection_set()


def convert_actors(actors: Any, actor_class: Any, static_mesh_package_path: str) -> Any:
    """액터들을 변환합니다."""
    return unreal.EditorLevelLibrary.convert_actors(actors, actor_class, static_mesh_package_path)


def destroy_actor(actor_to_destroy: Any) -> bool:
    """액터를 삭제합니다."""
    return unreal.EditorLevelLibrary.destroy_actor(actor_to_destroy)


def get_actor_reference(path_to_actor: str) -> Optional[Any]:
    """액터 참조를 가져옵니다."""
    return unreal.EditorLevelLibrary.get_actor_reference(path_to_actor)


def get_all_level_actors() -> Any:
    """레벨의 모든 액터들을 가져옵니다."""
    return unreal.EditorLevelLibrary.get_all_level_actors()


def get_all_level_actors_components() -> Any:
    """레벨의 모든 액터 컴포넌트들을 가져옵니다."""
    return unreal.EditorLevelLibrary.get_all_level_actors_components()


def get_selected_level_actors() -> Any:
    """선택된 레벨 액터들을 가져옵니다."""
    return unreal.EditorLevelLibrary.get_selected_level_actors()


def select_nothing() -> None:
    """아무것도 선택하지 않습니다."""
    return unreal.EditorLevelLibrary.select_nothing()


def set_actor_selection_state(actor: Any, should_be_selected: bool) -> None:
    """액터의 선택 상태를 설정합니다."""
    return unreal.EditorLevelLibrary.set_actor_selection_state(actor, should_be_selected)


def set_selected_level_actors(actors_to_select: Any) -> None:
    """선택된 레벨 액터들을 설정합니다."""
    return unreal.EditorLevelLibrary.set_selected_level_actors(actors_to_select)


# 월드 및 레벨 관리
def get_editor_world() -> Optional[Any]:
    """에디터 월드를 가져옵니다."""
    return unreal.EditorLevelLibrary.get_editor_world()


def get_game_world() -> Optional[Any]:
    """게임 월드를 가져옵니다."""
    return unreal.EditorLevelLibrary.get_game_world()


def get_pie_worlds(include_dedicated_server: bool) -> Any:
    """PIE(Play In Editor) 월드들을 가져옵니다."""
    return unreal.EditorLevelLibrary.get_pie_worlds(include_dedicated_server)


def load_level(asset_path: str) -> bool:
    """레벨을 로드합니다."""
    return unreal.EditorLevelLibrary.load_level(asset_path)


def new_level(asset_path: str) -> bool:
    """새 레벨을 생성합니다."""
    return unreal.EditorLevelLibrary.new_level(asset_path)


def new_level_from_template(asset_path: str, template_asset_path: str) -> bool:
    """템플릿에서 새 레벨을 생성합니다."""
    return unreal.EditorLevelLibrary.new_level_from_template(asset_path, template_asset_path)


def save_all_dirty_levels() -> bool:
    """모든 더티 레벨들을 저장합니다."""
    return unreal.EditorLevelLibrary.save_all_dirty_levels()


def save_current_level() -> bool:
    """현재 레벨을 저장합니다."""
    return unreal.EditorLevelLibrary.save_current_level()


def set_current_level_by_name(level_name: Any) -> bool:
    """이름으로 현재 레벨을 설정합니다."""
    return unreal.EditorLevelLibrary.set_current_level_by_name(level_name)


# 에디터 플레이 모드 및 뷰포트
def editor_end_play() -> None:
    """에디터 플레이를 종료합니다."""
    return unreal.EditorLevelLibrary.editor_end_play()


def editor_invalidate_viewports() -> None:
    """에디터 뷰포트를 무효화합니다."""
    return unreal.EditorLevelLibrary.editor_invalidate_viewports()


def editor_play_simulate() -> None:
    """에디터에서 시뮬레이션 플레이를 시작합니다."""
    return unreal.EditorLevelLibrary.editor_play_simulate()


def editor_set_game_view(game_view: bool) -> None:
    """에디터 게임 뷰를 설정합니다."""
    return unreal.EditorLevelLibrary.editor_set_game_view(game_view)


def get_level_viewport_camera_info() -> Optional[Tuple[Any, Any]]:
    """레벨 뷰포트 카메라 정보를 가져옵니다."""
    return unreal.EditorLevelLibrary.get_level_viewport_camera_info()


def set_level_viewport_camera_info(camera_location: Any, camera_rotation: Any) -> None:
    """레벨 뷰포트 카메라 정보를 설정합니다."""
    return unreal.EditorLevelLibrary.set_level_viewport_camera_info(camera_location, camera_rotation)


def eject_pilot_level_actor() -> None:
    """파일럿 레벨 액터를 배출합니다."""
    return unreal.EditorLevelLibrary.eject_pilot_level_actor()


def pilot_level_actor(actor_to_pilot: Any) -> None:
    """레벨 액터를 파일럿합니다."""
    return unreal.EditorLevelLibrary.pilot_level_actor(actor_to_pilot)


# 액터 생성 및 교체
def spawn_actor_from_class(actor_class: Any, location: Any, rotation: Any = None, transient: bool = False) -> Optional[Any]:
    """클래스에서 액터를 생성합니다."""
    if rotation is None:
        rotation = unreal.Rotator(0.0, 0.0, 0.0)
    return unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, location, rotation, transient)


def spawn_actor_from_object(object_to_use: unreal.Object, location: Any, rotation: Any = None, transient: bool = False) -> Optional[Any]:
    """오브젝트에서 액터를 생성합니다."""
    if rotation is None:
        rotation = unreal.Rotator(0.0, 0.0, 0.0)
    return unreal.EditorLevelLibrary.spawn_actor_from_object(object_to_use, location, rotation, transient)


def replace_selected_actors(asset_path: str) -> None:
    """선택된 액터들을 교체합니다."""
    return unreal.EditorLevelLibrary.replace_selected_actors(asset_path)


# 스태틱 메시 관리
def create_proxy_mesh_actor(actors_to_merge: Any, merge_options: Any) -> Optional[Any]:
    """프록시 메시 액터를 생성합니다."""
    return unreal.EditorLevelLibrary.create_proxy_mesh_actor(actors_to_merge, merge_options)


def join_static_mesh_actors(actors_to_join: Any, join_options: Any) -> Optional[Any]:
    """스태틱 메시 액터들을 조인합니다."""
    return unreal.EditorLevelLibrary.join_static_mesh_actors(actors_to_join, join_options)


def merge_static_mesh_actors(actors_to_merge: Any, merge_options: Any) -> Optional[Any]:
    """스태틱 메시 액터들을 병합합니다."""
    return unreal.EditorLevelLibrary.merge_static_mesh_actors(actors_to_merge, merge_options)


# 메시 및 머티리얼 교체
def replace_mesh_components_materials(mesh_components: Any, material_to_be_replaced: Any, new_material: Any) -> None:
    """메시 컴포넌트들의 머티리얼을 교체합니다."""
    return unreal.EditorLevelLibrary.replace_mesh_components_materials(mesh_components, material_to_be_replaced, new_material)


def replace_mesh_components_materials_on_actors(actors: Any, material_to_be_replaced: Any, new_material: Any) -> None:
    """액터들의 메시 컴포넌트 머티리얼을 교체합니다."""
    return unreal.EditorLevelLibrary.replace_mesh_components_materials_on_actors(actors, material_to_be_replaced, new_material)


def replace_mesh_components_meshes(mesh_components: Any, mesh_to_be_replaced: Any, new_mesh: Any) -> None:
    """메시 컴포넌트들의 메시를 교체합니다."""
    return unreal.EditorLevelLibrary.replace_mesh_components_meshes(mesh_components, mesh_to_be_replaced, new_mesh)


def replace_mesh_components_meshes_on_actors(actors: Any, mesh_to_be_replaced: Any, new_mesh: Any) -> None:
    """액터들의 메시 컴포넌트 메시를 교체합니다."""
    return unreal.EditorLevelLibrary.replace_mesh_components_meshes_on_actors(actors, mesh_to_be_replaced, new_mesh)


# ===============================================================================
# Python 레벨 라이브러리 래퍼들 (외부 라이브러리)
# ===============================================================================

# 레벨 관리
def remove_level_from_world(level_short_name: str) -> bool:
    """현재 월드에서 지정된 레벨을 제거합니다."""
    return unreal.PythonLevelLib.remove_level_from_world(level_short_name)


def get_levels(world_in: unreal.World) -> List[unreal.Level]:
    """월드의 모든 레벨들을 가져옵니다."""
    return unreal.PythonLevelLib.get_levels(world_in)