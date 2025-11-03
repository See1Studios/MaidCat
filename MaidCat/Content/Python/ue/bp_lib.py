"""
언리얼 엔진 Python BP 라이브러리 래퍼 모듈
==========================================

이 모듈은 언리얼 엔진 Python BP 라이브러리 함수들에 대한 편리한 래퍼를 제공합니다.
전체 모듈 경로 대신 더 짧은 함수 호출을 사용할 수 있습니다:

PythonBPLib 함수들:
- unreal.PythonBPLib.function_name → pybplib.function_name

작성자: MaidCat Plugin
버전: 1.0
"""

import unreal
from typing import List, Optional, Tuple, Dict, Any, Union


# ===============================================================================
# Python BP 라이브러리 래퍼들
# ===============================================================================

# 프로퍼티 관리
def get_all_property_names(class_: type, flag: int = -1) -> Any:
    """주어진 UClass의 모든 프로퍼티 이름을 가져옵니다."""
    return unreal.PythonBPLib.get_all_property_names(class_, flag)


def get_bool_property(object: unreal.Object, property_name: str) -> bool:
    """GetEditorProperty로 가져올 수 없는 Bool 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_bool_property(object, property_name)


def set_bool_property(object: unreal.Object, property_name: str, new_value: bool) -> bool:
    """SetEditorProperty로 설정할 수 없는 Bool 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_bool_property(object, property_name, new_value)


def get_string_property(object: unreal.Object, property_name: str) -> str:
    """GetEditorProperty로 가져올 수 없는 String 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_string_property(object, property_name)


def set_string_property(object: unreal.Object, property_name: str, new_value: str) -> bool:
    """SetEditorProperty로 설정할 수 없는 String 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_string_property(object, property_name, new_value)


def get_float_property(object: unreal.Object, property_name: str) -> float:
    """GetEditorProperty로 가져올 수 없는 Float 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_float_property(object, property_name)


def set_float_property(object: unreal.Object, property_name: str, new_value: float) -> bool:
    """SetEditorProperty로 설정할 수 없는 Float 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_float_property(object, property_name, new_value)


def get_int_property(object: unreal.Object, property_name: str) -> int:
    """GetEditorProperty로 가져올 수 없는 Int 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_int_property(object, property_name)


def set_int_property(object: unreal.Object, property_name: str, new_value: int) -> bool:
    """SetEditorProperty로 설정할 수 없는 Int 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_int_property(object, property_name, new_value)


def get_vector_property(object: unreal.Object, property_name: str) -> unreal.Vector:
    """GetEditorProperty로 가져올 수 없는 Vector 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_vector_property(object, property_name)


def set_vector_property(object: unreal.Object, property_name: str, new_value: unreal.Vector) -> bool:
    """SetEditorProperty로 설정할 수 없는 Vector 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_vector_property(object, property_name, new_value)


def get_object_property(object: unreal.Object, property_name: str) -> unreal.Object:
    """GetEditorProperty로 가져올 수 없는 Object 프로퍼티 값을 가져옵니다."""
    return unreal.PythonBPLib.get_object_property(object, property_name)


def set_object_property(object: unreal.Object, property_name: str, new_value: unreal.Object) -> bool:
    """SetEditorProperty로 설정할 수 없는 Object 프로퍼티 값을 설정합니다."""
    return unreal.PythonBPLib.set_object_property(object, property_name, new_value)


def get_object_flags(object: unreal.Object) -> int:
    """오브젝트의 플래그를 가져옵니다."""
    return unreal.PythonBPLib.get_object_flags(object)


# 오브젝트 및 월드 관리
def get_all_objects(world: unreal.World, include_dead: bool) -> Any:
    """월드의 모든 UObject를 가져옵니다."""
    return unreal.PythonBPLib.get_all_objects(world, include_dead)


def get_objects_by_class(world: unreal.World, object_class: type) -> Any:
    """월드에서 지정된 클래스의 모든 UObject를 가져옵니다."""
    return unreal.PythonBPLib.get_objects_by_class(world, object_class)


def get_all_worlds() -> Any:
    """에디터의 모든 월드를 가져옵니다."""
    return unreal.PythonBPLib.get_all_worlds()


# 블루프린트 관리
def get_bp_class_hierarchy_package(class_: type) -> Optional[Any]:
    """블루프린트 인스턴스 클래스의 클래스 계층 구조를 가져옵니다."""
    return unreal.PythonBPLib.get_bp_class_hierarchy_package(class_)


def get_anim_blueprint_generated_class(anim_blueprint: unreal.AnimBlueprint) -> type:
    """애니메이션 블루프린트의 생성된 클래스를 가져옵니다."""
    return unreal.PythonBPLib.get_anim_blueprint_generated_class(anim_blueprint)


def get_blueprint_generated_class(blueprint: unreal.Blueprint) -> unreal.Object:
    """블루프린트의 생성된 클래스를 가져옵니다."""
    return unreal.PythonBPLib.get_blueprint_generated_class(blueprint)


# 에셋 선택 및 관리
def get_selected_assets_paths() -> Any:
    """콘텐츠 브라우저에서 선택된 에셋 경로를 가져옵니다."""
    return unreal.PythonBPLib.get_selected_assets_paths()


def set_selected_assets_by_paths(paths: Any) -> None:
    """콘텐츠 브라우저에서 지정된 에셋을 선택합니다."""
    return unreal.PythonBPLib.set_selected_assets_by_paths(paths)


def get_selected_folder() -> Any:
    """콘텐츠 브라우저에서 선택된 폴더 경로를 가져옵니다."""
    return unreal.PythonBPLib.get_selected_folder()


def set_selected_folder(folders: Any) -> None:
    """콘텐츠 브라우저에서 지정된 폴더를 선택합니다."""
    return unreal.PythonBPLib.set_selected_folder(folders)


def set_folder_color(folder_path: str, color: unreal.LinearColor) -> None:
    """콘텐츠 브라우저에서 지정된 폴더의 색상을 설정합니다."""
    return unreal.PythonBPLib.set_folder_color(folder_path, color)


def clear_folder_color(folder_path: str) -> None:
    """콘텐츠 브라우저에서 지정된 폴더의 색상을 지웁니다."""
    return unreal.PythonBPLib.clear_folder_color(folder_path)


def sync_to_assets(asset_data_list: Any, allow_locked_browsers: bool = False, focus_content_browser: bool = True) -> None:
    """콘텐츠 브라우저에서 에셋을 동기화합니다."""
    return unreal.PythonBPLib.sync_to_assets(asset_data_list, allow_locked_browsers, focus_content_browser)


# 액터 선택 및 관리
def select_none(note_selection_change: bool = True, deselect_bsp_surfs: bool = True) -> None:
    """모든 액터의 선택을 해제합니다."""
    return unreal.PythonBPLib.select_none(note_selection_change, deselect_bsp_surfs)


def select_named_actor(name: str, clear_selected: bool = True) -> Optional[unreal.Actor]:
    """이름으로 액터를 선택합니다."""
    return unreal.PythonBPLib.select_named_actor(name, clear_selected)


def select_component(component: unreal.ActorComponent, selected: bool, notify: bool = True) -> None:
    """지정된 컴포넌트를 선택합니다."""
    return unreal.PythonBPLib.select_component(component, selected, notify)


def select_actor(actor: unreal.Actor, selected: bool, notify: bool, select_even_if_hidden: bool = False, force_refresh: bool = False) -> None:
    """지정된 액터를 선택합니다."""
    return unreal.PythonBPLib.select_actor(actor, selected, notify, select_even_if_hidden, force_refresh)


def find_actor_by_name(name: str, world: Optional[unreal.World] = None, include_dead: bool = True) -> Optional[unreal.Actor]:
    """지정된 월드에서 이름으로 액터를 찾습니다."""
    return unreal.PythonBPLib.find_actor_by_name(name, world, include_dead)


def find_actors_by_label_name(name: str, world: Optional[unreal.World] = None, include_dead: bool = True) -> Any:
    """지정된 월드에서 라벨 이름으로 액터를 찾습니다."""
    return unreal.PythonBPLib.find_actors_by_label_name(name, world, include_dead)


def get_selected_components() -> Any:
    """월드 아웃라이너에서 선택된 컴포넌트를 가져옵니다."""
    return unreal.PythonBPLib.get_selected_components()


# 월드 아웃라이너 폴더 관리
def create_folder_in_outliner(world: unreal.World, new_folder_name: unreal.Name) -> None:
    """월드 아웃라이너에 새 폴더를 생성합니다."""
    return unreal.PythonBPLib.create_folder_in_outliner(world, new_folder_name)


def set_selected_folder_path(path: unreal.Name) -> None:
    """선택된 모든 액터의 폴더 경로를 설정합니다."""
    return unreal.PythonBPLib.set_selected_folder_path(path)


def delete_folder(world: unreal.World, folder_to_delete: unreal.Name) -> None:
    """월드 아웃라이너에서 지정된 폴더를 삭제합니다."""
    return unreal.PythonBPLib.delete_folder(world, folder_to_delete)


def get_actors_from_folder(world: unreal.World, path: str) -> Any:
    """월드 아웃라이너에서 지정된 폴더의 액터를 가져옵니다."""
    return unreal.PythonBPLib.get_actors_from_folder(world, path)


def rename_folder_in_world(world: unreal.World, old_path: unreal.Name, new_path: unreal.Name) -> bool:
    """지정된 경로를 새 이름으로 변경합니다."""
    return unreal.PythonBPLib.rename_folder_in_world(world, old_path, new_path)


# 에셋 의존성 및 참조
def get_all_deps(package_path: unreal.Name, recursive: bool, dependency_type: int = 3) -> Tuple[Any, Any]:
    """지정된 패키지 경로의 모든 의존성을 가져옵니다."""
    return unreal.PythonBPLib.get_all_deps(package_path, recursive, dependency_type)


def get_all_refs(package_path: unreal.Name, recursive: bool, dependency_type: int = 3) -> Tuple[Any, Any]:
    """지정된 패키지 경로의 모든 참조자를 가져옵니다."""
    return unreal.PythonBPLib.get_all_refs(package_path, recursive, dependency_type)


def get_assets_data_by_package_names(package_names: Any) -> Any:
    """패키지의 에셋에 대한 에셋 데이터를 가져옵니다."""
    return unreal.PythonBPLib.get_assets_data_by_package_names(package_names)


def get_assets_data_by_class(paths_folders: Any, class_names: Any) -> Any:
    """지정된 폴더와 타입의 에셋에 대한 AssetData를 가져옵니다."""
    return unreal.PythonBPLib.get_assets_data_by_class(paths_folders, class_names)


def list_assets_by_class(paths_folders: Any, class_names: Any) -> Any:
    """지정된 폴더와 타입의 에셋 경로를 가져옵니다."""
    return unreal.PythonBPLib.list_assets_by_class(paths_folders, class_names)


# 리다이렉터 관리
def get_redirectors_destination_object(redirector_obj: unreal.Object) -> unreal.Object:
    """리다이렉터의 대상 오브젝트를 가져옵니다."""
    return unreal.PythonBPLib.get_redirectors_destination_object(redirector_obj)


def fix_up_redirectors_in_folder(folder_paths: Any, allowed_to_prompt_to_load_assets: bool = True) -> bool:
    """지정된 폴더의 모든 리다이렉터를 수정합니다."""
    return unreal.PythonBPLib.fix_up_redirectors_in_folder(folder_paths, allowed_to_prompt_to_load_assets)


def fix_up_redirectors(redirector_objs: Any) -> bool:
    """지정된 리다이렉터를 수정합니다."""
    return unreal.PythonBPLib.fix_up_redirectors(redirector_objs)


# 명령 실행
def execute_console_command(console_command: str) -> None:
    """콘솔 명령을 실행합니다."""
    return unreal.PythonBPLib.execute_console_command(console_command)


def exec_python_command(python_command: str, force_game_thread: bool = False) -> None:
    """Python 명령을 실행합니다."""
    return unreal.PythonBPLib.exec_python_command(python_command, force_game_thread)


def call_function(object: unreal.Object, functio_name_and_args: str) -> bool:
    """주어진 오브젝트에서 이름으로 함수를 호출합니다. (deprecated)"""
    return unreal.PythonBPLib.call_function(object, functio_name_and_args)


# 다이얼로그
def message_dialog(message: str, dialog_title: str) -> None:
    """모달 메시지 박스 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.message_dialog(message, dialog_title)


def confirm_dialog(message: str, dialog_title: str, with_cancel_button: bool = False) -> bool:
    """Yes/No/Cancel 버튼이 있는 모달 메시지 박스 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.confirm_dialog(message, dialog_title, with_cancel_button)


def open_file_dialog(dialog_title: str, default_path: str, default_file: str, file_types: str) -> Any:
    """파일 선택 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.open_file_dialog(dialog_title, default_path, default_file, file_types)


def save_file_dialog(dialog_title: str, default_path: str, default_file: str, file_types: str) -> Any:
    """파일 저장 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.save_file_dialog(dialog_title, default_path, default_file, file_types)


def open_directory_dialog(dialog_title: str, default_path: str) -> Optional[str]:
    """디렉토리 선택 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.open_directory_dialog(dialog_title, default_path)


def open_pick_path_dialog(dialog_title: str = "Pick Path", default_path: str = "/Game/") -> str:
    """UE 스타일 경로 선택 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.open_pick_path_dialog(dialog_title, default_path)


def open_new_asset_path_dialog(dialog_title: str = "Pick Asset Path", default_path: str = "", allow_read_only_folders: bool = True) -> str:
    """UE 스타일 새 에셋 경로 다이얼로그를 엽니다."""
    return unreal.PythonBPLib.open_new_asset_path_dialog(dialog_title, default_path, allow_read_only_folders)


# 클립보드
def set_clipboard_content(str: str) -> None:
    """클립보드에 문자열 내용을 설정합니다."""
    return unreal.PythonBPLib.set_clipboard_content(str)


def get_clipboard_content() -> str:
    """클립보드에서 문자열 내용을 가져옵니다."""
    return unreal.PythonBPLib.get_clipboard_content()


# 알림
def notification(message: str, info_level: int = 0, expire_duration: float = 5.0, width_override: float = -1.0, log_to_console: bool = True, hyperlink_text: str = "", on_hyperlink_click_command: str = "") -> None:
    """플로팅 알림을 추가합니다."""
    return unreal.PythonBPLib.notification(message, info_level, expire_duration, width_override, log_to_console, hyperlink_text, on_hyperlink_click_command)


# 뷰포트 카메라 관리
def get_level_viewport_camera_info() -> Optional[Tuple[unreal.Vector, unreal.Rotator]]:
    """레벨 뷰포트 카메라의 위치와 회전을 가져옵니다."""
    return unreal.PythonBPLib.get_level_viewport_camera_info()


def set_level_viewport_camera_info(camera_location: unreal.Vector, camera_rotation: unreal.Rotator) -> None:
    """레벨 뷰포트 카메라의 위치와 회전을 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_camera_info(camera_location, camera_rotation)


def get_level_viewport_camera_fov() -> float:
    """레벨 뷰포트 카메라의 FOV를 가져옵니다."""
    return unreal.PythonBPLib.get_level_viewport_camera_fov()


def set_level_viewport_camera_fov(fov: float) -> bool:
    """레벨 뷰포트 카메라의 FOV를 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_camera_fov(fov)


def get_level_viewport_camera_speed() -> int:
    """레벨 뷰포트 카메라의 속도 설정(1-8)을 가져옵니다."""
    return unreal.PythonBPLib.get_level_viewport_camera_speed()


def set_level_viewport_camera_speed(speed: int) -> None:
    """레벨 뷰포트 카메라의 속도 설정(1-8)을 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_camera_speed(speed)


def pilot_level_actor(actor_to_pilot: unreal.Actor) -> None:
    """액터의 위치와 회전에 따라 뷰포트 카메라를 이동합니다."""
    return unreal.PythonBPLib.pilot_level_actor(actor_to_pilot)


def eject_pilot_level_actor() -> None:
    """뷰포트 카메라를 배출합니다."""
    return unreal.PythonBPLib.eject_pilot_level_actor()


def get_pilot_level_actor() -> Optional[unreal.Actor]:
    """현재 활성 뷰포트의 파일럿 액터를 가져옵니다."""
    return unreal.PythonBPLib.get_pilot_level_actor()


# 뷰포트 설정
def set_level_viewport_real_time(realtime: bool) -> None:
    """뷰포트 실시간 상태를 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_real_time(realtime)


def set_level_viewport_is_in_game_view(game_view: bool) -> None:
    """레벨 뷰의 IsInGameView를 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_is_in_game_view(game_view)


def set_level_viewport_locked(locked: bool) -> None:
    """카메라에 뷰포트를 잠글 때 정확한 카메라 뷰를 표시할지 여부를 설정합니다."""
    return unreal.PythonBPLib.set_level_viewport_locked(locked)


def request_viewport_focus_on_selection(context_obj: Optional[unreal.Object] = None) -> None:
    """선택 항목 앞으로 에디터 카메라를 이동합니다."""
    return unreal.PythonBPLib.request_viewport_focus_on_selection(context_obj)


def viewport_redraw() -> None:
    """첫 번째 활성 뷰포트를 다시 그립니다."""
    return unreal.PythonBPLib.viewport_redraw()


# 뷰포트 픽셀
def get_viewport_pixels() -> Tuple[Any, unreal.IntPoint]:
    """첫 번째 활성 뷰포트에서 원시 픽셀을 가져옵니다."""
    return unreal.PythonBPLib.get_viewport_pixels()


def get_viewport_pixels_as_texture() -> Optional[unreal.Texture2D]:
    """첫 번째 활성 뷰포트의 내용을 Texture2D로 가져옵니다."""
    return unreal.PythonBPLib.get_viewport_pixels_as_texture()


# 액터 생성
def spawn_actor_from_object(obj_to_use: unreal.Object, location: unreal.Vector, rotation: unreal.Rotator = unreal.Rotator(0, 0, 0), transient: bool = False, select_actors: bool = False) -> Optional[unreal.Actor]:
    """오브젝트로부터 액터를 생성하고 월드 에디터에 배치합니다."""
    return unreal.PythonBPLib.spawn_actor_from_object(obj_to_use, location, rotation, transient, select_actors)


def spawn_actor_from_class(actor_class: type, location: unreal.Vector, rotation: unreal.Rotator = unreal.Rotator(0, 0, 0), transient: bool = False, select_actors: bool = False) -> Optional[unreal.Actor]:
    """클래스로부터 액터를 생성하고 월드 에디터에 배치합니다."""
    return unreal.PythonBPLib.spawn_actor_from_class(actor_class, location, rotation, transient, select_actors)


def add_component(component_class: type, actor: unreal.Actor, parent_component: Optional[unreal.SceneComponent], name: unreal.Name = "None") -> Optional[unreal.ActorComponent]:
    """액터에 지정된 컴포넌트를 생성합니다."""
    return unreal.PythonBPLib.add_component(component_class, actor, parent_component, name)


# 기타 유틸리티
def get_resource_size(object: unreal.Object, exclusive: bool) -> int:
    """메모리 도구에 사용할 오브젝트/리소스의 크기를 가져옵니다."""
    return unreal.PythonBPLib.get_resource_size(object, exclusive)


def get_plugin_base_dir(plugin_name: str) -> str:
    """명명된 플러그인의 기본 디렉토리를 가져옵니다."""
    return unreal.PythonBPLib.get_plugin_base_dir(plugin_name)


def get_unreal_version() -> Dict[str, int]:
    """언리얼 엔진의 버전을 맵(딕셔너리)으로 가져옵니다."""
    return unreal.PythonBPLib.get_unreal_version()


def get_ta_python_version() -> Dict[str, int]:
    """TAPython의 버전을 맵(딕셔너리)으로 가져옵니다."""
    return unreal.PythonBPLib.get_ta_python_version()


def guid_from_string(guid_str: str) -> unreal.Guid:
    """GUID 값 문자열에서 GUID 인스턴스를 생성합니다."""
    return unreal.PythonBPLib.guid_from_string(guid_str)


def get_modifier_keys_state() -> Dict[str, bool]:
    """수정자 키 상태를 TMap으로 가져옵니다."""
    return unreal.PythonBPLib.get_modifier_keys_state()


def gc(keep_flags: int, perform_full_purge: bool = True) -> None:
    """참조되지 않은 모든 오브젝트를 삭제합니다."""
    return unreal.PythonBPLib.gc(keep_flags, perform_full_purge)


def delete_asset(asset_path_to_delete: str, show_confirmation: bool = True) -> bool:
    """경로의 에셋을 삭제합니다."""
    return unreal.PythonBPLib.delete_asset(asset_path_to_delete, show_confirmation)


def close_editor_for_assets(assets: Any) -> None:
    """제공된 에셋에 대한 모든 활성 에디터를 닫습니다."""
    return unreal.PythonBPLib.close_editor_for_assets(assets)