"""
Unreal Engine LevelEditorSubsystem 래퍼 모듈

레벨 에디터와 관련된 서브시스템 기능들을 제공합니다.
LevelEditorSubsystem의 주요 기능을 한국어 문서와 함께 래핑합니다.

주요 기능:
- 레벨 생성/로드/저장 (new_level, load_level, save_current_level, save_all_dirty_levels)
- 플레이 인 에디터 (editor_request_begin_play, editor_request_end_play, editor_play_simulate)
- 뷰포트 제어 (editor_set_game_view, editor_set_viewport_realtime, editor_invalidate_viewports)
- 카메라 파일럿 (pilot_level_actor, eject_pilot_level_actor, get_pilot_level_actor)
- 현재 레벨 관리 (get_current_level, set_current_level_by_name)
- 뷰포트 설정 (get_active_viewport_config_key, get_viewport_config_keys)
- 카메라 뷰 제어 (get_exact_camera_view, set_exact_camera_view)
- 시네마틱 제어 (get_allows_cinematic_control, set_allows_cinematic_control)
- 라이팅 빌드 (build_light_maps)
- 선택 관리 (get_selection_set)
- 에디터 모드 관리 (get_level_editor_mode_manager)
- 퀵 액션 메뉴 (extend_quick_action_menu)

이벤트 프로퍼티들 (읽기 전용):
- on_editor_camera_moved - 에디터 카메라 이동 이벤트
- on_map_changed - 맵 변경 이벤트  
- on_map_opened - 맵 열림 이벤트
- on_post_save_world - 월드 저장 후 이벤트
- on_pre_save_world - 월드 저장 전 이벤트

Author: MaidCat Team
"""

import unreal
from typing import Optional


def get_level_editor_subsystem() -> unreal.LevelEditorSubsystem:
    """레벨 에디터 서브시스템을 가져옵니다.
    
    Returns:
        LevelEditorSubsystem 인스턴스
    """
    return unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


# 레벨 관리 함수들
def get_current_level() -> Optional[unreal.Level]:
    """월드 에디터에서 사용하는 현재 레벨을 가져옵니다.
    
    Returns:
        현재 레벨
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_current_level()


def set_current_level_by_name(level_name: unreal.Name) -> bool:
    """월드 에디터에서 사용할 현재 레벨을 설정합니다.
    같은 이름을 가진 레벨이 여러 개 있으면, 첫 번째로 발견된 레벨이 사용됩니다.
    
    Args:
        level_name: 액터가 속한 레벨의 이름 (ContentBrowser에서와 같은 이름)
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.set_current_level_by_name(level_name)


def load_level(asset_path: str) -> bool:
    """현재 Persistent Level을 닫고(저장하지 않음) 지정된 레벨을 로드합니다.
    
    Args:
        asset_path: 로드할 레벨의 에셋 경로 (예: /Game/MyFolder/MyAsset)
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.load_level(asset_path)


def new_level(asset_path: str, is_partitioned_world: bool = False) -> bool:
    """현재 Persistent Level을 닫고(저장하지 않음) 새로운 빈 레벨을 생성하여 저장합니다.
    새로 생성된 레벨을 로드합니다.
    
    Args:
        asset_path: 레벨이 저장될 에셋 경로 (예: /Game/MyFolder/MyAsset)
        is_partitioned_world: True이면 새 맵이 파티션됩니다
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.new_level(asset_path, is_partitioned_world)


def new_level_from_template(asset_path: str, template_asset_path: str) -> bool:
    """현재 Persistent Level을 닫고(저장하지 않음) 다른 레벨을 기반으로 새 레벨을 생성하여 저장합니다.
    새로 생성된 레벨을 로드합니다.
    
    Args:
        asset_path: 레벨이 저장될 에셋 경로 (예: /Game/MyFolder/MyAsset)
        template_asset_path: 템플릿으로 사용할 레벨 (예: /Game/MyFolder/MyAsset)
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.new_level_from_template(asset_path, template_asset_path)


def save_current_level() -> bool:
    """지정된 레벨을 저장합니다. 유효한 경로를 가지려면 이미 한 번은 저장되어 있어야 합니다.
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.save_current_level()


def save_all_dirty_levels() -> bool:
    """월드 에디터에서 현재 로드된 모든 레벨을 저장합니다.
    
    Returns:
        작업 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.save_all_dirty_levels()


# 플레이 인 에디터 함수들
def is_in_play_in_editor() -> bool:
    """플레이 인 에디터 상태인지 확인합니다.
    
    Returns:
        플레이 인 에디터 상태이면 True
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.is_in_play_in_editor()


def editor_request_begin_play() -> None:
    """에디터 플레이 시작을 요청합니다."""
    subsystem = get_level_editor_subsystem()
    subsystem.editor_request_begin_play()


def editor_request_end_play() -> None:
    """에디터 플레이 종료를 요청합니다."""
    subsystem = get_level_editor_subsystem()
    subsystem.editor_request_end_play()


def editor_play_simulate() -> None:
    """에디터 시뮬레이트를 시작합니다."""
    subsystem = get_level_editor_subsystem()
    subsystem.editor_play_simulate()


# 뷰포트 제어 함수들
def get_active_viewport_config_key() -> unreal.Name:
    """활성 뷰포트 설정 키를 가져옵니다.
    
    Returns:
        활성 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_active_viewport_config_key()


def get_viewport_config_keys() -> unreal.Array:
    """뷰포트 설정 키들을 가져옵니다.
    
    Returns:
        뷰포트 설정 키들의 배열
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_viewport_config_keys()


def editor_get_game_view(viewport_config_key: unreal.Name = unreal.Name("None")) -> bool:
    """에디터 게임 뷰 상태를 가져옵니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    
    Returns:
        게임 뷰 상태
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.editor_get_game_view(viewport_config_key)


def editor_set_game_view(game_view: bool, viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """에디터 게임 뷰를 설정합니다.
    
    Args:
        game_view: 게임 뷰 활성화 여부
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.editor_set_game_view(game_view, viewport_config_key)


def editor_set_viewport_realtime(realtime: bool, viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """에디터 뷰포트 실시간 모드를 설정합니다.
    
    Args:
        realtime: 실시간 모드 활성화 여부
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.editor_set_viewport_realtime(realtime, viewport_config_key)


def editor_invalidate_viewports() -> None:
    """에디터 뷰포트를 무효화합니다."""
    subsystem = get_level_editor_subsystem()
    subsystem.editor_invalidate_viewports()


# 카메라 파일럿 함수들
def get_pilot_level_actor(viewport_config_key: unreal.Name = unreal.Name("None")) -> Optional[unreal.Actor]:
    """파일럿 레벨 액터를 가져옵니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    
    Returns:
        파일럿 액터 또는 None
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_pilot_level_actor(viewport_config_key)


def pilot_level_actor(actor_to_pilot: unreal.Actor, viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """레벨 액터를 파일럿합니다.
    
    Args:
        actor_to_pilot: 파일럿할 액터
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.pilot_level_actor(actor_to_pilot, viewport_config_key)


def eject_pilot_level_actor(viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """파일럿 레벨 액터를 해제합니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.eject_pilot_level_actor(viewport_config_key)


# 카메라 뷰 제어 함수들
def get_exact_camera_view(viewport_config_key: unreal.Name = unreal.Name("None")) -> bool:
    """정확한 카메라 뷰 상태를 가져옵니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    
    Returns:
        정확한 카메라 뷰 활성화 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_exact_camera_view(viewport_config_key)


def set_exact_camera_view(exact_camera_view: bool, viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """정확한 카메라 뷰를 설정합니다.
    
    Args:
        exact_camera_view: 정확한 카메라 뷰 활성화 여부
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.set_exact_camera_view(exact_camera_view, viewport_config_key)


def get_allows_cinematic_control(viewport_config_key: unreal.Name = unreal.Name("None")) -> bool:
    """시네마틱 제어 허용 상태를 가져옵니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    
    Returns:
        시네마틱 제어 허용 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_allows_cinematic_control(viewport_config_key)


def set_allows_cinematic_control(allow: bool, viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """시네마틱 제어 허용을 설정합니다.
    
    Args:
        allow: 시네마틱 제어 허용 여부
        viewport_config_key: 뷰포트 설정 키
    """
    subsystem = get_level_editor_subsystem()
    subsystem.set_allows_cinematic_control(allow, viewport_config_key)


# 라이팅 빌드 함수들
def build_light_maps(quality: unreal.LightingBuildQuality = unreal.LightingBuildQuality.QUALITY_PRODUCTION, 
                    with_reflection_captures: bool = False) -> bool:
    """라이트 맵과 선택적으로 리플렉션 캡처를 빌드합니다.
    
    Args:
        quality: LightingBuildQuality 열거형 값 중 하나. 기본값은 Quality_Production
        with_reflection_captures: 라이트 맵 빌드 후 관련 리플렉션 캡처도 빌드할지 여부
    
    Returns:
        빌드 성공 여부
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.build_light_maps(quality, with_reflection_captures)


# 선택 관리 함수들
def get_selection_set() -> unreal.TypedElementSelectionSet:
    """현재 월드의 선택 집합을 가져옵니다.
    이것을 사용하여 레벨 에디터의 선택을 추적하고 변경할 수 있습니다.
    
    Returns:
        TypedElementSelectionSet 인스턴스
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.get_selection_set()


def get_level_editor_mode_manager():
    """글로벌 레벨 에디터 모드 매니저를 가져옵니다 (가능한 경우).
    
    Returns:
        레벨 에디터 모드 매니저 또는 None
    """
    subsystem = get_level_editor_subsystem()
    # Python API에서는 이 함수가 노출되지 않을 수 있음
    if hasattr(subsystem, 'get_level_editor_mode_manager'):
        return subsystem.get_level_editor_mode_manager()
    return None


def extend_quick_action_menu():
    """퀵 액션 메뉴를 확장합니다."""
    subsystem = get_level_editor_subsystem()
    # Python API에서는 이 함수가 노출되지 않을 수 있음
    if hasattr(subsystem, 'extend_quick_action_menu'):
        subsystem.extend_quick_action_menu()


# 편의 함수들
def get_editor_world() -> Optional[unreal.World]:
    """에디터 월드를 가져옵니다.
    
    Returns:
        에디터 월드 또는 None
    """
    current_level = get_current_level()
    if current_level:
        return current_level.get_world()
    return None


def is_level_dirty() -> bool:
    """현재 레벨이 수정되었는지 확인합니다.
    
    Returns:
        레벨이 수정되었으면 True
    """
    current_level = get_current_level()
    if current_level:
        return current_level.get_package().is_dirty()
    return False


def toggle_game_view(viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """게임 뷰를 토글합니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    """
    current_state = editor_get_game_view(viewport_config_key)
    editor_set_game_view(not current_state, viewport_config_key)


def toggle_realtime_viewport(viewport_config_key: unreal.Name = unreal.Name("None")) -> None:
    """실시간 뷰포트를 토글합니다.
    
    Args:
        viewport_config_key: 뷰포트 설정 키
    """
    # 현재 상태를 확인하는 함수가 없으므로 단순히 True로 설정
    editor_set_viewport_realtime(True, viewport_config_key)


def quick_save_current_level() -> bool:
    """현재 레벨을 빠르게 저장합니다.
    
    Returns:
        저장 성공 여부
    """
    return save_current_level()


def quick_save_all_levels() -> bool:
    """모든 더티 레벨을 빠르게 저장합니다.
    
    Returns:
        저장 성공 여부
    """
    return save_all_dirty_levels()


def create_new_level_at_path(level_path: str, use_template: bool = False, 
                           template_path: str = "", partitioned: bool = False) -> bool:
    """지정된 경로에 새 레벨을 생성합니다.
    
    Args:
        level_path: 새 레벨의 경로
        use_template: 템플릿 사용 여부
        template_path: 사용할 템플릿 경로 (use_template이 True일 때)
        partitioned: 파티션된 월드 생성 여부
    
    Returns:
        생성 성공 여부
    """
    if use_template and template_path:
        return new_level_from_template(level_path, template_path)
    else:
        return new_level(level_path, partitioned)


# 상태 확인 함수들
def get_level_editor_status() -> dict:
    """레벨 에디터의 현재 상태를 반환합니다.
    
    Returns:
        상태 정보를 담은 딕셔너리
    """
    status = {
        "current_level": None,
        "editor_world": None,
        "is_playing": is_in_play_in_editor(),
        "active_viewport": get_active_viewport_config_key(),
        "level_dirty": False
    }
    
    current_level = get_current_level()
    if current_level:
        status["current_level"] = current_level.get_name()
        status["level_dirty"] = current_level.get_package().is_dirty()
        
    editor_world = get_editor_world()
    if editor_world:
        status["editor_world"] = editor_world.get_name()
    
    return status


def print_level_editor_status() -> None:
    """레벨 에디터 상태를 출력합니다."""
    status = get_level_editor_status()
    print("=== 레벨 에디터 상태 ===")
    print(f"현재 레벨: {status['current_level']}")
    print(f"에디터 월드: {status['editor_world']}")
    print(f"플레이 중: {status['is_playing']}")
    print(f"활성 뷰포트: {status['active_viewport']}")
    print(f"레벨 수정됨: {status['level_dirty']}")


# 이벤트 프로퍼티 접근 함수들
def get_on_editor_camera_moved():
    """에디터 카메라 이동 이벤트 델리게이트를 가져옵니다.
    
    Returns:
        OnLevelEditorEditorCameraMoved 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_editor_camera_moved


def get_on_map_changed():
    """맵 변경 이벤트 델리게이트를 가져옵니다.
    참고: 일부 에디터 스크립팅에는 너무 일찍 실행되므로, 작동하지 않으면 on_map_opened 사용을 고려하세요.
    
    Returns:
        OnLevelEditorMapChanged 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_map_changed


def get_on_map_opened():
    """맵 열림 이벤트 델리게이트를 가져옵니다.
    
    Returns:
        OnLevelEditorMapOpened 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_map_opened


def get_on_post_save_world():
    """월드 저장 후 이벤트 델리게이트를 가져옵니다.
    
    Returns:
        OnLevelEditorPostSaveWorld 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_post_save_world


def get_on_pre_save_world():
    """월드 저장 전 이벤트 델리게이트를 가져옵니다.
    
    Returns:
        OnLevelEditorPreSaveWorld 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_pre_save_world