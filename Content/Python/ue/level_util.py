"""
Unreal Engine EditorLevelUtils 래퍼 모듈

에디터에서 레벨과 관련된 유틸리티 함수들을 제공합니다.
EditorLevelUtils의 주요 기능을 한국어 문서와 함께 래핑합니다.

실제 EditorLevelUtils API 함수들:
- add_level_to_world() - 레벨을 월드에 추가
- add_level_to_world_with_transform() - 트랜스폼과 함께 레벨을 월드에 추가  
- create_new_streaming_level() - 새로운 스트리밍 레벨 생성
- get_levels() - 월드의 모든 레벨 가져오기
- make_level_current() - 현재 레벨로 설정
- move_actors_to_level() - 액터들을 레벨로 이동
- move_selected_actors_to_level() - 선택된 액터들을 레벨로 이동
- remove_level_from_world() - 월드에서 레벨 제거
- set_level_visibility() - 레벨 표시 설정
- set_levels_visibility() - 여러 레벨 표시 설정

이 모듈은 순수하게 EditorLevelUtils만 래핑합니다.
LevelEditorSubsystem 관련 기능은 별도 모듈에서 제공됩니다.

Author: MaidCat Team
"""

import unreal
from typing import List, Optional


def add_level_to_world(world: unreal.World, level_package_name: str, level_streaming_class: unreal.Class) -> Optional[unreal.LevelStreaming]:
    """기존 레벨을 월드에 추가합니다.
    
    Args:
        world: 레벨을 추가할 월드
        level_package_name: 추가할 레벨의 패키지 이름 (예: "/Game/MyLevel")
        level_streaming_class: 사용할 레벨 스트리밍 클래스
    
    Returns:
        생성된 LevelStreaming 객체 또는 None
    """
    return unreal.EditorLevelUtils.add_level_to_world(world, level_package_name, level_streaming_class)


def add_level_to_world_with_transform(world: unreal.World, level_package_name: str, 
                                    level_streaming_class: unreal.Class, 
                                    level_transform: unreal.Transform) -> Optional[unreal.LevelStreaming]:
    """트랜스폼과 함께 기존 레벨을 월드에 추가합니다.
    
    Args:
        world: 레벨을 추가할 월드
        level_package_name: 추가할 레벨의 패키지 이름 (예: "/Game/MyLevel")
        level_streaming_class: 사용할 레벨 스트리밍 클래스
        level_transform: 새 레벨의 월드 원점
    
    Returns:
        생성된 LevelStreaming 객체 또는 None
    """
    return unreal.EditorLevelUtils.add_level_to_world_with_transform(
        world, level_package_name, level_streaming_class, level_transform)


def create_new_streaming_level(level_streaming_class: unreal.Class, 
                              new_level_path: str = '', 
                              move_selected_actors_into_new_level: bool = False) -> Optional[unreal.LevelStreaming]:
    """현재 월드에 새로운 스트리밍 레벨을 생성합니다.
    
    Args:
        level_streaming_class: 레벨에 사용할 스트리밍 클래스 타입
        new_level_path: 레벨 패키지 경로 (예: "/Game/MyLevel"). 비어있으면 저장 시 사용자에게 묻습니다.
        move_selected_actors_into_new_level: True이면 선택된 액터들을 새 레벨로 이동
    
    Returns:
        새로 생성된 레벨 또는 None (실패시)
    """
    return unreal.EditorLevelUtils.create_new_streaming_level(
        level_streaming_class, new_level_path, move_selected_actors_into_new_level)


def get_levels(world: unreal.World) -> unreal.Array:
    """월드의 모든 레벨을 가져옵니다.
    
    Args:
        world: 대상 월드
    
    Returns:
        모든 레벨의 집합
    """
    return unreal.EditorLevelUtils.get_levels(world)


def make_level_current(streaming_level: unreal.LevelStreaming) -> None:
    """지정된 스트리밍 레벨을 편집용 현재 레벨로 설정합니다.
    현재 레벨은 SpawnActor 호출 시 액터가 스폰되는 위치입니다.
    
    Args:
        streaming_level: 현재 레벨로 설정할 스트리밍 레벨
    """
    unreal.EditorLevelUtils.make_level_current(streaming_level)


def move_actors_to_level(actors_to_move: unreal.Array, dest_streaming_level: unreal.LevelStreaming, 
                        warn_about_references: bool = True, warn_about_renaming: bool = True) -> int:
    """지정된 액터 목록을 지정된 스트리밍 레벨로 이동합니다. 새 액터들이 선택됩니다.
    
    Args:
        actors_to_move: 이동할 액터들의 목록
        dest_streaming_level: 액터를 이동할 현재 월드의 목적지 스트리밍 레벨
        warn_about_references: 이동 후 더 이상 작동하지 않을 수 있는 참조된 액터에 대한 모달 경고 표시 여부
        warn_about_renaming: 이름 변경에 대한 경고 표시 여부
    
    Returns:
        새 레벨로 성공적으로 이동된 액터의 수
    """
    return unreal.EditorLevelUtils.move_actors_to_level(
        actors_to_move, dest_streaming_level, warn_about_references, warn_about_renaming)


def move_selected_actors_to_level(dest_level: unreal.LevelStreaming, warn_about_references: bool = True) -> int:
    """현재 선택된 액터들을 지정된 스트리밍 레벨로 이동합니다. 새 액터들이 선택됩니다.
    
    Args:
        dest_level: 목적지 레벨 스트리밍
        warn_about_references: 이동 후 더 이상 작동하지 않을 수 있는 참조된 액터에 대한 모달 경고 표시 여부
    
    Returns:
        새 레벨로 성공적으로 이동된 액터의 수
    """
    return unreal.EditorLevelUtils.move_selected_actors_to_level(dest_level, warn_about_references)


def remove_level_from_world(level: unreal.Level, clear_selection: bool = True, 
                           reset_transaction_buffer: bool = True) -> bool:
    """주어진 레벨을 월드에서 제거합니다. 메인 레벨의 서브레벨에서만 작동합니다.
    
    Args:
        level: 월드에서 제거할 레벨 에셋
        clear_selection: True이면 에디터 선택을 지웁니다
        reset_transaction_buffer: True이면 트랜잭션 버퍼를 리셋합니다 (즉, 실행 취소 히스토리 지우기)
    
    Returns:
        레벨이 성공적으로 제거되었으면 True
    """
    return unreal.EditorLevelUtils.remove_level_from_world(level, clear_selection, reset_transaction_buffer)


def set_level_visibility(level: unreal.Level, should_be_visible: bool, force_layers_visible: bool, 
                        modify_mode: unreal.LevelVisibilityDirtyMode = unreal.LevelVisibilityDirtyMode.MODIFY_ON_CHANGE) -> None:
    """에디터에서 레벨의 표시 여부를 설정합니다.
    여러 레벨의 표시 여부를 동시에 변경할 때는 set_levels_visibility가 더 효율적입니다.
    
    Args:
        level: 수정할 레벨
        should_be_visible: 레벨의 새로운 표시 상태
        force_layers_visible: True이고 레벨이 표시되면, 레벨의 레이어를 강제로 표시
        modify_mode: ELevelVisibilityDirtyMode 모드 값
    """
    unreal.EditorLevelUtils.set_level_visibility(level, should_be_visible, force_layers_visible, modify_mode)


def set_levels_visibility(levels: unreal.Array, should_be_visible: unreal.Array, force_layers_visible: bool,
                         modify_mode: unreal.LevelVisibilityDirtyMode = unreal.LevelVisibilityDirtyMode.MODIFY_ON_CHANGE) -> None:
    """에디터에서 여러 레벨의 표시 여부를 설정합니다.
    여러 레벨의 표시 여부를 동시에 변경할 때 set_level_visibility보다 더 효율적입니다.
    
    Args:
        levels: 수정할 레벨들
        should_be_visible: 각 레벨의 새로운 표시 상태
        force_layers_visible: True이고 레벨이 표시되면, 레벨의 레이어를 강제로 표시
        modify_mode: ELevelVisibilityDirtyMode 모드 값
    """
    unreal.EditorLevelUtils.set_levels_visibility(levels, should_be_visible, force_layers_visible, modify_mode)