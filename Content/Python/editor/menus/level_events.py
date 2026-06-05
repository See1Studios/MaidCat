"""
Level Event Handler - Unreal Engine 레벨 이벤트 처리
"""

import unreal
import time


class LevelEventHandler:
    """레벨 이벤트 핸들러"""
    
    def __init__(self):
        self.subsystem = None
        self.is_initialized = False
        self.event_count = 0
        self.camera_last_time = 0
        self.last_save_time = 0  # 저장 이벤트 throttling용
        
    def initialize(self):
        """초기화"""
        if self.is_initialized:
            return True
            
        try:
            self.subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            if not self.subsystem:
                raise Exception("LevelEditorSubsystem을 가져올 수 없습니다.")
            
            # 이벤트 등록 (안전한 것들만)
            self.subsystem.on_map_changed.add_callable(self.on_map_changed)  # ⚠️ 조심스럽게 활성화
            print("   ⚠️ on_map_changed 등록됨 (WorldTearDown 주의)")
            
            print("🔧 델리게이트 등록 중...")
            self.subsystem.on_map_opened.add_callable(self.on_map_opened)
            print("   ✅ on_map_opened 등록됨")
            
            # self.subsystem.on_editor_camera_moved.add_callable(self.on_camera_moved)  # 크래시 발생!
            # print("   ✅ on_editor_camera_moved 등록됨 (throttled)")
            
            self.subsystem.on_pre_save_world.add_callable(self.on_pre_save_world)
            print("   ✅ on_pre_save_world 등록됨")
            
            self.subsystem.on_post_save_world.add_callable(self.on_post_save_world)
            print("   ✅ on_post_save_world 등록됨")
            
            self.is_initialized = True
            print("✅ 레벨 이벤트 핸들러 초기화 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 초기화 실패: {e}")
            return False
    
    def on_map_opened(self, filename: str, as_template: bool):
        """맵 열림 이벤트"""
        try:
            self.event_count += 1
            short_name = filename.split('/')[-1] if filename else "Unknown"
            template_text = " (템플릿)" if as_template else ""
            print(f"📖 맵 열림: {short_name}{template_text}")
        except Exception as e:
            print(f"❌ 맵 열림 오류: {e}")
    
    def on_camera_moved(self, location: unreal.Vector, rotation: unreal.Rotator, 
                       viewport_type: unreal.LevelViewportType, view_index: int):
        """카메라 이동 이벤트 (throttled)"""
        try:
            current_time = time.time()
            if current_time - self.camera_last_time >= 1.0:  # 1초마다
                print(f"📷 카메라: ({location.x:.0f}, {location.y:.0f}, {location.z:.0f})")
                self.camera_last_time = current_time
        except Exception as e:
            print(f"❌ 카메라 이동 오류: {e}")
    
    def on_map_changed(self, map_change_flags: int):
        """맵 변경 이벤트 - 안전한 처리"""
        try:
            # WorldTearDown(3) 시에는 최소한의 작업만
            if map_change_flags == 3:  # WorldTearDown
                print("🧹 월드 정리 중... (안전 모드)")
                return
            
            self.event_count += 1
            change_types = {0: "저장", 1: "새맵/로드", 2: "로드완료"}
            type_name = change_types.get(map_change_flags, f"기타({map_change_flags})")
            print(f"🗺️ 맵 변경: {type_name}")
        except Exception as e:
            print(f"❌ 맵 변경 오류: {e}")
    
    def on_pre_save_world(self, save_flags: int, world: unreal.World):
        """저장 전 이벤트"""
        try:
            world_name = world.get_name() if world else "Unknown"
            print(f"💾 저장 전: {world_name}")
        except Exception as e:
            print(f"❌ 저장 전 오류: {e}")
    
    def on_post_save_world(self, save_flags: int, world: unreal.World, success: bool):
        """저장 후 이벤트"""
        try:
            world_name = world.get_name() if world else "Unknown"
            status = "성공" if success else "실패"
            print(f"✅ 저장 후: {world_name} - {status}")
        except Exception as e:
            print(f"❌ 저장 후 오류: {e}")
    
    def get_status(self):
        """상태 확인"""
        print(f" 레벨 이벤트 핸들러: {'활성' if self.is_initialized else '비활성'}")
        print(f"   총 이벤트: {self.event_count}회")
    
    def shutdown(self):
        """종료"""
        if not self.is_initialized:
            return True
            
        try:
            if self.subsystem:
                self.subsystem.on_map_changed.remove_callable(self.on_map_changed)
                self.subsystem.on_map_opened.remove_callable(self.on_map_opened)
                # self.subsystem.on_editor_camera_moved.remove_callable(self.on_camera_moved)  # 비활성화됨
                self.subsystem.on_pre_save_world.remove_callable(self.on_pre_save_world)
                self.subsystem.on_post_save_world.remove_callable(self.on_post_save_world)
            
            self.is_initialized = False
            self.subsystem = None
            print("✅ 레벨 이벤트 핸들러 종료 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 종료 중 오류: {e}")
            return False

# 전역 딕셔너리를 사용한 핸들러 저장
import builtins
if not hasattr(builtins, '_maidcat_handlers'):
    builtins._maidcat_handlers = {}

def _get_handler():
    """핸들러 가져오기"""
    if 'level_events' not in builtins._maidcat_handlers:
        builtins._maidcat_handlers['level_events'] = LevelEventHandler()
    return builtins._maidcat_handlers['level_events']

def _clear_handler():
    """핸들러 정리"""
    if 'level_events' in builtins._maidcat_handlers:
        del builtins._maidcat_handlers['level_events']

def start_level_events():
    """레벨 이벤트 모니터링 시작"""
    handler = _get_handler()
    result = handler.initialize()
    
    if not result:
        _clear_handler()
    
    return result

def stop_level_events():
    """레벨 이벤트 모니터링 중지"""
    try:
        handler = _get_handler()
        if handler is not None:
            result = handler.shutdown()
            _clear_handler()
            return result
    except:
        pass
    return True

def get_level_events_status():
    """레벨 이벤트 핸들러 상태 출력"""
    try:
        handler = _get_handler()
        if handler is not None and handler.is_initialized:
            handler.get_status()
        else:
            print("❌ 레벨 이벤트 핸들러가 초기화되지 않았습니다.")
    except:
        print("❌ 레벨 이벤트 핸들러가 초기화되지 않았습니다.")