"""CameraComponent 선택 시 디테일 패널 확인"""
import unreal

print("=" * 80)
print("📷 CameraComponent 디테일 패널 테스트")
print("=" * 80)

# CameraActor 찾기
all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
camera_actor = None
for actor in all_actors:
    if isinstance(actor, unreal.CameraActor):
        camera_actor = actor
        break

if camera_actor:
    print(f"✅ CameraActor: {camera_actor.get_name()}")
    
    # CameraActor 선택
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    editor_actor_subsystem.set_selected_level_actors([camera_actor])
    
    print("\n" + "=" * 80)
    print("✅ CameraActor를 선택했습니다.")
    print("   디테일 패널에서 CameraComponent 섹션을 펼쳐보세요.")
    print("   커스텀 UI(PP Preset Test 버튼)가 보이는지 확인하세요.")
    print("=" * 80)
else:
    print("❌ CameraActor를 찾을 수 없습니다!")
