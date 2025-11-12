"""
간단한 Level Events 테스트 스크립트

이 스크립트를 Unreal Python 콘솔에서 실행하면
레벨 에디터 이벤트를 쉽게 테스트할 수 있습니다.

사용법:
1. Unreal Editor에서 Python 콘솔 열기
2. exec(open('examples/quick_test.py').read()) 실행
3. 맵 변경, 저장 등을 테스트해보기
"""

import unreal
from ue import level_sys

print("🚀 Quick Level Events Test")
print("=" * 40)

# 간단한 콜백 함수들
def simple_map_changed(flags):
    print(f"📍 맵 변경됨: {flags}")

def simple_map_opened(filename, as_template):
    print(f"📂 맵 열림: {filename} (템플릿: {as_template})")

def simple_camera_moved(loc, rot, viewport, index):
    if index == 0:  # 메인 뷰포트만
        print(f"📷 카메라: ({loc.x:.0f}, {loc.y:.0f}, {loc.z:.0f})")

def simple_pre_save(flags, world):
    world_name = world.get_name() if world else "Unknown"
    print(f"💾 저장 준비: {world_name}")

def simple_post_save(flags, world, success):
    world_name = world.get_name() if world else "Unknown"
    status = "성공" if success else "실패"
    print(f"✅ 저장 {status}: {world_name}")

# 이벤트 등록
try:
    level_sys.add_map_changed_callback(simple_map_changed)
    level_sys.add_map_opened_callback(simple_map_opened)
    level_sys.add_camera_moved_callback(simple_camera_moved)
    level_sys.add_pre_save_world_callback(simple_pre_save)
    level_sys.add_post_save_world_callback(simple_post_save)
    
    print("✅ 모든 이벤트 등록 완료!")
    print("\n테스트해보세요:")
    print("- File > New Level (새 맵)")
    print("- File > Open Level (맵 열기)")
    print("- 뷰포트에서 카메라 이동")
    print("- Ctrl+S (저장)")
    
except Exception as e:
    print(f"❌ 오류: {e}")

# 정리 함수
def cleanup_quick_test():
    """퀵 테스트 정리"""
    try:
        level_sys.remove_map_changed_callback(simple_map_changed)
        level_sys.remove_map_opened_callback(simple_map_opened)
        level_sys.remove_camera_moved_callback(simple_camera_moved)
        level_sys.remove_pre_save_world_callback(simple_pre_save)
        level_sys.remove_post_save_world_callback(simple_post_save)
        print("🧹 퀵 테스트 정리 완료!")
    except Exception as e:
        print(f"❌ 정리 실패: {e}")

print(f"\n💡 종료시: cleanup_quick_test() 호출")