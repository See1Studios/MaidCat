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
from typing import Optional, Callable


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


# ===== 델리게이트 헬퍼 함수들 =====

def get_on_editor_camera_moved():
    """에디터 카메라 이동 이벤트 델리게이트를 가져옵니다.
    
    콜백 함수 시그니처: callback(location: unreal.Vector, rotation: unreal.Rotator, editor_viewport_type: int, viewport_index: int) -> None
    
    에디터 뷰포트 카메라가 이동할 때마다 호출됩니다.
    주의: 매우 자주 호출될 수 있으므로 무거운 작업은 피하세요.
    
    Returns:
        OnLevelEditorEditorCameraMoved 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_editor_camera_moved


def get_on_map_changed():
    """맵 변경 이벤트 델리게이트를 가져옵니다.
    맵의 다양한 변경 상태를 세밀하게 추적할 수 있습니다.
    
    콜백 함수 시그니처: callback(map_change_type: int) -> None
    
    맵 변경 타입 (map_change_type):
        0: SaveMap - 맵 저장 완료
        1: NewMap/LoadMap - 새 레벨 생성 또는 로드 시작
        2: LoadMap - 레벨 로드 완료  
        3: WorldTearDown - 현재 월드 해체/정리 시작
    
    이벤트 발생 순서: WorldTearDown(3) → NewMap/LoadMap(1) → LoadMap(2)
    
    ⚠️ WorldTearDown(3) 주의사항:
    - 월드 객체나 액터에 접근 금지! (이미 해체 과정 시작됨)
    - 안전한 작업만 수행: 데이터 저장, 임시 파일 정리, 메모리 해제 등
    - 발생 시점: 레벨 닫기, 에디터 종료, PIE 종료, 프로젝트 전환
    
    Returns:
        OnLevelEditorMapChanged 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_map_changed


def get_on_map_opened():
    """맵 열림 이벤트 델리게이트를 가져옵니다.
    
    콜백 함수 시그니처: callback(level_name: str) -> None
    
    맵이 성공적으로 열렸을 때 호출됩니다.
    get_on_map_changed()와 함께 사용하면 더 세밀한 맵 상태 추적이 가능합니다.
    
    Returns:
        OnLevelEditorMapOpened 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_map_opened


def get_on_post_save_world():
    """월드 저장 후 이벤트 델리게이트를 가져옵니다.
    
    콜백 함수 시그니처: callback(save_context: int, world: unreal.World, success: bool) -> None
    
    저장 성공/실패에 따른 후속 처리를 수행하기에 적합한 시점입니다.
    
    Returns:
        OnLevelEditorPostSaveWorld 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_post_save_world


def get_on_pre_save_world():
    """월드 저장 전 이벤트 델리게이트를 가져옵니다.
    
    콜백 함수 시그니처: callback(save_context: int, world: unreal.World) -> None
    
    저장 전 검증이나 준비 작업을 수행하기에 적합한 시점입니다.
    
    Returns:
        OnLevelEditorPreSaveWorld 델리게이트
    """
    subsystem = get_level_editor_subsystem()
    return subsystem.on_pre_save_world


# ===== 델리게이트 헬퍼 함수들 (시그니처 명확화) =====

def add_map_changed_callback(callback_func: Callable[[int], None]) -> bool:
    """맵 변경 이벤트 콜백을 등록합니다.
    
    Args:
        callback_func: 콜백 함수 - callback(map_change_type: int) -> None
    
    맵 변경 타입 (map_change_type):
        0: SaveMap - 맵 저장 완료
        1: NewMap/LoadMap - 새 레벨 생성 또는 로드 시작
        2: LoadMap - 레벨 로드 완료  
        3: WorldTearDown - 현재 월드 해체/정리 시작
    
    ⚠️ WorldTearDown(3) 주의사항:
    - 월드 객체나 액터에 접근 금지! (이미 해체 과정 시작됨)
    - 안전한 작업만 수행: 데이터 저장, 임시 파일 정리, 메모리 해제 등
    
    Returns:
        등록 성공 여부
    
    Example:
        def my_map_changed(map_change_type: int):
            if map_change_type == 3:  # WorldTearDown
                print("월드 정리 중...")
            else:
                print(f"맵 변경: {map_change_type}")
        
        add_map_changed_callback(my_map_changed)
    """
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_map_changed.add_callable(callback_func)
        return True
    except Exception as e:
        print(f"맵 변경 콜백 등록 실패: {e}")
        return False


def add_map_opened_callback(callback_func: Callable[[str], None]) -> bool:
    """맵 열림 이벤트 콜백을 등록합니다.
    
    Args:
        callback_func: 콜백 함수 - callback(level_name: str) -> None
    
    Returns:
        등록 성공 여부
    
    Example:
        def my_map_opened(level_name: str):
            print(f"맵 열림: {level_name}")
        
        add_map_opened_callback(my_map_opened)
    """
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_map_opened.add_callable(callback_func)
        return True
    except Exception as e:
        print(f"맵 열림 콜백 등록 실패: {e}")
        return False


def add_pre_save_world_callback(callback_func: Callable[[int, unreal.World], None]) -> bool:
    """월드 저장 전 이벤트 콜백을 등록합니다.
    
    Args:
        callback_func: 콜백 함수 - callback(save_context: int, world: unreal.World) -> None
    
    Returns:
        등록 성공 여부
    
    Example:
        def my_pre_save(save_context: int, world: unreal.World):
            print(f"저장 전: {world.get_name()}")
        
        add_pre_save_world_callback(my_pre_save)
    """
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_pre_save_world.add_callable(callback_func)
        return True
    except Exception as e:
        print(f"저장 전 콜백 등록 실패: {e}")
        return False


def add_post_save_world_callback(callback_func: Callable[[int, unreal.World, bool], None]) -> bool:
    """월드 저장 후 이벤트 콜백을 등록합니다.
    
    Args:
        callback_func: 콜백 함수 - callback(save_context: int, world: unreal.World, success: bool) -> None
    
    Returns:
        등록 성공 여부
    
    Example:
        def my_post_save(save_context: int, world: unreal.World, success: bool):
            status = "성공" if success else "실패"
            print(f"저장 후: {world.get_name()} - {status}")
        
        add_post_save_world_callback(my_post_save)
    """
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_post_save_world.add_callable(callback_func)
        return True
    except Exception as e:
        print(f"저장 후 콜백 등록 실패: {e}")
        return False


def add_editor_camera_moved_callback(callback_func: Callable[[unreal.Vector, unreal.Rotator, int, int], None]) -> bool:
    """에디터 카메라 이동 이벤트 콜백을 등록합니다.
    
    Args:
        callback_func: 콜백 함수 - callback(location: unreal.Vector, rotation: unreal.Rotator, editor_viewport_type: int, viewport_index: int) -> None
    
    ⚠️ 주의: 매우 자주 호출되므로 가벼운 작업만 수행하세요!
    
    Returns:
        등록 성공 여부
    
    Example:
        def my_camera_moved(location: unreal.Vector, rotation: unreal.Rotator, editor_viewport_type: int, viewport_index: int):
            print(f"카메라 이동: {location}")
        
        add_editor_camera_moved_callback(my_camera_moved)
    """
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_editor_camera_moved.add_callable(callback_func)
        return True
    except Exception as e:
        print(f"카메라 이동 콜백 등록 실패: {e}")
        return False


# ===== 콜백 제거 함수들 =====

def remove_map_changed_callback(callback_func) -> bool:
    """맵 변경 이벤트 콜백을 제거합니다."""
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_map_changed.remove_callable(callback_func)
        return True
    except Exception as e:
        print(f"맵 변경 콜백 제거 실패: {e}")
        return False


def remove_map_opened_callback(callback_func) -> bool:
    """맵 열림 이벤트 콜백을 제거합니다."""
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_map_opened.remove_callable(callback_func)
        return True
    except Exception as e:
        print(f"맵 열림 콜백 제거 실패: {e}")
        return False


def remove_pre_save_world_callback(callback_func) -> bool:
    """월드 저장 전 이벤트 콜백을 제거합니다."""
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_pre_save_world.remove_callable(callback_func)
        return True
    except Exception as e:
        print(f"저장 전 콜백 제거 실패: {e}")
        return False


def remove_post_save_world_callback(callback_func) -> bool:
    """월드 저장 후 이벤트 콜백을 제거합니다."""
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_post_save_world.remove_callable(callback_func)
        return True
    except Exception as e:
        print(f"저장 후 콜백 제거 실패: {e}")
        return False


def remove_editor_camera_moved_callback(callback_func) -> bool:
    """에디터 카메라 이동 이벤트 콜백을 제거합니다."""
    try:
        subsystem = get_level_editor_subsystem()
        subsystem.on_editor_camera_moved.remove_callable(callback_func)
        return True
    except Exception as e:
        print(f"카메라 이동 콜백 제거 실패: {e}")
        return False


