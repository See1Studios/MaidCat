"""
Unreal Engine Level Editor Event Delegates 샘플 코드

이 예제는 LevelEditorSubsystem의 다양한 이벤트 델리게이트를 사용하는 방법을 보여줍니다.
- 맵 변경 이벤트 감지
- 에디터 카메라 이동 추적
- 월드 저장 이벤트 처리
- 안전한 콜백 등록/해제

작성자: MaidCat Plugin
참조: Unreal Engine Python API - LevelEditorSubsystem
"""

import unreal
from typing import Optional
from ue import level_sys


class LevelEventsSample:
    """레벨 에디터 이벤트 샘플 클래스"""
    
    def __init__(self):
        self.level_subsystem: Optional[unreal.LevelEditorSubsystem] = None
        self._callbacks_registered = False
        
    def initialize(self):
        """이벤트 시스템 초기화"""
        try:
            # LevelEditorSubsystem 인스턴스 가져오기
            self.level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            if not self.level_subsystem:
                print("❌ LevelEditorSubsystem을 찾을 수 없습니다.")
                return False
                
            print("✅ LevelEventsSample 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            return False
    
    def register_all_events(self):
        """모든 이벤트 콜백 등록"""
        if not self.level_subsystem or self._callbacks_registered:
            return
            
        try:
            # 1. 맵 변경 이벤트 등록 (주의: 너무 빨리 실행될 수 있음)
            level_sys.add_map_changed_callback(self.on_map_changed)
            
            # 2. 맵 열림 이벤트 등록 (권장: 맵 변경보다 안정적)
            level_sys.add_map_opened_callback(self.on_map_opened)
            
            # 3. 에디터 카메라 이동 이벤트 등록
            level_sys.add_camera_moved_callback(self.on_camera_moved)
            
            # 4. 월드 저장 전 이벤트 등록
            level_sys.add_pre_save_world_callback(self.on_pre_save_world)
            
            # 5. 월드 저장 후 이벤트 등록
            level_sys.add_post_save_world_callback(self.on_post_save_world)
            
            self._callbacks_registered = True
            print("🎯 모든 레벨 이벤트 콜백이 등록되었습니다.")
            
        except Exception as e:
            print(f"❌ 이벤트 등록 실패: {e}")
    
    def unregister_all_events(self):
        """모든 이벤트 콜백 해제"""
        if not self.level_subsystem or not self._callbacks_registered:
            return
            
        try:
            # 등록된 모든 콜백 해제
            level_sys.remove_map_changed_callback(self.on_map_changed)
            level_sys.remove_map_opened_callback(self.on_map_opened)
            level_sys.remove_camera_moved_callback(self.on_camera_moved)
            level_sys.remove_pre_save_world_callback(self.on_pre_save_world)
            level_sys.remove_post_save_world_callback(self.on_post_save_world)
            
            self._callbacks_registered = False
            print("🔌 모든 레벨 이벤트 콜백이 해제되었습니다.")
            
        except Exception as e:
            print(f"❌ 이벤트 해제 실패: {e}")
    
    # ==========================================================================
    # 이벤트 콜백 함수들
    # ==========================================================================
    
    def on_map_changed(self, map_change_flags: int):
        """
        맵 변경 이벤트 콜백
        
        Args:
            map_change_flags (int): 맵 변경 플래그 (MapChangeEventFlags)
                                   - 0: 새로운 맵 생성
                                   - 1: 맵 로드
                                   - 2: 맵 저장
                                   - 4: 월드 컴포지션 변경 등
        """
        print(f"🗺️  맵 변경 이벤트: 플래그={map_change_flags}")
        
        # 맵 변경 플래그에 따른 처리
        if map_change_flags & 1:  # 맵 로드
            print("   📂 새로운 맵이 로드되었습니다.")
        if map_change_flags & 2:  # 맵 저장
            print("   💾 맵이 저장되었습니다.")
    
    def on_map_opened(self, filename: str, as_template: bool):
        """
        맵 열림 이벤트 콜백 (맵 변경보다 안정적)
        
        Args:
            filename (str): 열린 맵의 파일명
            as_template (bool): 템플릿으로 열었는지 여부
        """
        template_text = "템플릿으로" if as_template else "일반 맵으로"
        print(f"📖 맵 열림: {filename} ({template_text})")
        
        # 현재 레벨 정보 가져오기
        current_level = self.level_subsystem.get_current_level()
        if current_level:
            level_name = current_level.get_name()
            print(f"   현재 활성 레벨: {level_name}")
    
    def on_camera_moved(self, location: unreal.Vector, rotation: unreal.Rotator, 
                       viewport_type: unreal.LevelViewportType, view_index: int):
        """
        에디터 카메라 이동 이벤트 콜백
        
        Args:
            location (Vector): 카메라 위치
            rotation (Rotator): 카메라 회전
            viewport_type (LevelViewportType): 뷰포트 타입
            view_index (int): 뷰 인덱스
        """
        # 너무 많은 로그를 방지하기 위해 간헐적으로만 출력
        if view_index == 0:  # 주 뷰포트만
            print(f"📷 카메라 이동: 위치=({location.x:.1f}, {location.y:.1f}, {location.z:.1f})")
            print(f"   회전=({rotation.pitch:.1f}°, {rotation.yaw:.1f}°, {rotation.roll:.1f}°)")
            print(f"   뷰포트: {viewport_type}")
    
    def on_pre_save_world(self, save_flags: int, world: unreal.World):
        """
        월드 저장 전 이벤트 콜백
        
        Args:
            save_flags (int): 저장 플래그
            world (World): 저장될 월드 객체
        """
        world_name = world.get_name() if world else "Unknown"
        print(f"💾 월드 저장 준비 중: {world_name} (플래그: {save_flags})")
        
        # 저장 전 검증이나 준비 작업 수행
        print("   ✓ 저장 전 검증 완료")
    
    def on_post_save_world(self, save_flags: int, world: unreal.World, success: bool):
        """
        월드 저장 후 이벤트 콜백
        
        Args:
            save_flags (int): 저장 플래그
            world (World): 저장된 월드 객체
            success (bool): 저장 성공 여부
        """
        world_name = world.get_name() if world else "Unknown"
        status = "성공" if success else "실패"
        emoji = "✅" if success else "❌"
        
        print(f"{emoji} 월드 저장 {status}: {world_name}")
        
        if success:
            print("   📁 월드가 성공적으로 저장되었습니다.")
        else:
            print("   ⚠️  월드 저장 중 오류가 발생했습니다.")
    
    def cleanup(self):
        """리소스 정리"""
        self.unregister_all_events()
        self.level_subsystem = None
        print("🧹 LevelEventsSample 정리 완료")


# ==========================================================================
# 사용 예제
# ==========================================================================

def main():
    """메인 실행 함수"""
    print("🚀 Level Events Sample 시작")
    print("=" * 50)
    
    # 샘플 인스턴스 생성 및 초기화
    sample = LevelEventsSample()
    
    if not sample.initialize():
        print("❌ 초기화 실패로 프로그램을 종료합니다.")
        return
    
    # 이벤트 등록
    sample.register_all_events()
    
    print("\n🎯 이벤트 리스너가 활성화되었습니다!")
    print("다음 작업을 해보세요:")
    print("- 새 맵 생성 (File > New Level)")
    print("- 기존 맵 열기 (File > Open Level)")
    print("- 에디터 카메라 이동")
    print("- 맵 저장 (Ctrl+S)")
    print("\n종료하려면 Python 콘솔에서 sample.cleanup() 을 실행하세요.")
    
    return sample


def cleanup_sample(sample_instance):
    """샘플 정리 헬퍼 함수"""
    if sample_instance:
        sample_instance.cleanup()


# 직접 실행 시 메인 함수 호출
if __name__ == "__main__":
    # 전역 변수로 샘플 인스턴스 저장 (정리를 위해)
    global_sample = main()
    
    # 정리 함수를 전역으로 등록
    def cleanup():
        cleanup_sample(global_sample)
    
    print(f"\n💡 정리하려면: cleanup() 함수를 호출하세요.")


# ==========================================================================
# 추가 유틸리티 함수들
# ==========================================================================

def get_current_level_info():
    """현재 레벨 정보 출력"""
    try:
        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if not subsystem:
            print("❌ LevelEditorSubsystem을 찾을 수 없습니다.")
            return
        
        current_level = subsystem.get_current_level()
        if current_level:
            print(f"📍 현재 레벨: {current_level.get_name()}")
            print(f"   패키지: {current_level.get_package().get_name()}")
        else:
            print("❓ 현재 활성 레벨이 없습니다.")
            
    except Exception as e:
        print(f"❌ 레벨 정보 조회 실패: {e}")


def test_level_subsystem_methods():
    """LevelEditorSubsystem의 다양한 메서드 테스트"""
    try:
        subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        if not subsystem:
            print("❌ LevelEditorSubsystem을 찾을 수 없습니다.")
            return
        
        print("🔍 LevelEditorSubsystem 메서드 테스트:")
        
        # Play in Editor 상태 확인
        is_pie = subsystem.is_in_play_in_editor()
        print(f"   Play in Editor: {is_pie}")
        
        # 뷰포트 설정 키 목록
        viewport_keys = subsystem.get_viewport_config_keys()
        print(f"   뷰포트 설정 키: {[str(key) for key in viewport_keys]}")
        
        # 활성 뷰포트 키
        active_key = subsystem.get_active_viewport_config_key()
        print(f"   활성 뷰포트 키: {active_key}")
        
        # 선택 세트
        selection_set = subsystem.get_selection_set()
        print(f"   선택 세트: {selection_set}")
        
    except Exception as e:
        print(f"❌ 메서드 테스트 실패: {e}")


# 편의 함수들을 모듈 레벨에서 사용 가능하도록 등록
__all__ = [
    'LevelEventsSample', 
    'main', 
    'cleanup_sample',
    'get_current_level_info',
    'test_level_subsystem_methods'
]