"""
PostProcessVolume 디테일 패널 커스터마이징 모듈

액터 선택 시 자동으로 커스텀 디테일 패널을 등록합니다.
TAPython의 Chameleon 시스템을 사용하여 UI를 구성합니다.
"""

import unreal
import traceback
from typing import Optional, Set

# 전역 상태 (GC 방지)
_selection_set: Optional[unreal.TypedElementSelectionSet] = None
_selection_delegate_handle = None
_last_registered_path: Optional[str] = None
_registered_actors: Set[str] = set()  # 등록된 액터 경로 추적

# 설정
JSON_PATH = "DetailCustomization/PostProcessVolume.json"


def _try_register_actor(actor: unreal.Actor) -> bool:
    """액터에 커스터마이징 등록 시도"""
    if not isinstance(actor, unreal.PostProcessVolume):
        return False
    
    return unreal.ChameleonData.add_detail_customization(actor, JSON_PATH)


def _cleanup_invalid_actors() -> None:
    """삭제된 액터의 커스터마이징 정리"""
    global _registered_actors
    
    # 레벨의 모든 PostProcessVolume 가져오기
    editor_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = editor_actor.get_all_level_actors()
    
    valid_paths = set()
    for actor in all_actors:
        if isinstance(actor, unreal.PostProcessVolume):
            valid_paths.add(actor.get_path_name())
    
    # 등록되었지만 더 이상 존재하지 않는 액터 찾기
    invalid_paths = _registered_actors - valid_paths
    
    if invalid_paths:
        # 삭제된 액터가 있으면 모두 정리하고 재등록
        unreal.ChameleonData.clear_detail_customization()
        _registered_actors.clear()
        unreal.log(f"🗑️ {len(invalid_paths)}개 삭제된 액터 정리 완료")


def _on_selection_changed(selection_set) -> None:
    """선택 변경 이벤트 핸들러"""
    global _last_registered_path, _registered_actors
    
    try:
        # 먼저 삭제된 액터 정리
        _cleanup_invalid_actors()
        
        editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        selected_actors = editor_actor_subsystem.get_selected_level_actors()
        
        if not selected_actors:
            _last_registered_path = None
            return
        
        # PostProcessVolume 찾기
        target_actor = None
        for actor in selected_actors:
            if isinstance(actor, unreal.PostProcessVolume):
                target_actor = actor
                break
        
        if target_actor is None:
            return
        
        actor_path = target_actor.get_path_name()
        if actor_path == _last_registered_path:
            return
        
        # 새로운 액터 선택 시 이전 커스터마이징 제거 후 재등록
        unreal.ChameleonData.clear_detail_customization()
        _registered_actors.clear()
        
        if _try_register_actor(target_actor):
            _last_registered_path = actor_path
            _registered_actors.add(actor_path)
            unreal.log(f"✅ Detail Customization 등록: {target_actor.get_name()}")
                
    except Exception as e:
        unreal.log_error(f"❌ 선택 이벤트 처리 실패: {e}")
        unreal.log_error(traceback.format_exc())


def _cleanup_delegate() -> None:
    """델리게이트 정리"""
    global _selection_set, _selection_delegate_handle, _last_registered_path, _registered_actors
    
    if _selection_set is not None:
        try:
            _selection_set.on_selection_change.remove_callable(_on_selection_changed)  # type: ignore
        except Exception:
            pass
    
    _selection_set = None
    _selection_delegate_handle = None
    _last_registered_path = None
    _registered_actors.clear()


def register() -> bool:
    """이벤트 핸들러 등록
    
    Returns:
        bool: 등록 성공 여부
    """
    global _selection_set, _selection_delegate_handle
    
    _cleanup_delegate()
    
    unreal.log("")
    unreal.log("=" * 80)
    unreal.log("🚀 PostProcessVolume 디테일 커스터마이징 시작")
    unreal.log("=" * 80)
    unreal.log(f"📄 JSON: {JSON_PATH}")
    
    try:
        # 선택 변경 이벤트 등록
        level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        _selection_set = level_editor.get_selection_set()
        
        # 기존 콜백 제거 후 등록
        try:
            _selection_set.on_selection_change.remove_callable(_on_selection_changed)  # type: ignore
        except:
            pass
        _selection_delegate_handle = _selection_set.on_selection_change.add_callable(_on_selection_changed)  # type: ignore
        
        unreal.log("✅ 이벤트 핸들러 등록 완료")
        unreal.log("   • 선택 변경 시 자동으로 삭제된 액터 정리")
        unreal.log("=" * 80)
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ 이벤트 등록 실패: {e}")
        unreal.log_error(traceback.format_exc())
        unreal.log("=" * 80)
        return False


def unregister() -> bool:
    """이벤트 핸들러 해제
    
    Returns:
        bool: 해제 성공 여부
    """
    if _selection_set is None:
        return True
    
    try:
        _cleanup_delegate()
        unreal.log("✅ 이벤트 핸들러 해제 완료")
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ 핸들러 해제 실패: {e}")
        unreal.log_error(traceback.format_exc())
        return False


def clear_customizations() -> bool:
    """모든 커스터마이징 제거
    
    Returns:
        bool: 제거 성공 여부
    """
    try:
        unreal.ChameleonData.clear_detail_customization()
        unreal.log("✅ 모든 커스터마이징 제거 완료")
        return True
    except Exception as e:
        unreal.log_error(f"❌ 커스터마이징 제거 실패: {e}")
        return False


def list_customizations() -> bool:
    """등록된 커스터마이징 목록 출력
    
    Returns:
        bool: 조회 성공 여부
    """
    try:
        unreal.ChameleonData.log_all_saved_detail_customization()
        return True
    except Exception as e:
        unreal.log_error(f"❌ 커스터마이징 조회 실패: {e}")
        return False


if __name__ == "__main__":
    register()
