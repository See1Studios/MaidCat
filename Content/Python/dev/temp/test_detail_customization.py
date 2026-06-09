import unreal
import os

# IsDetailCustomization 플래그 테스트

unreal.ChameleonData.clear_detail_customization()
unreal.log("=" * 50)

# PPPreset.json (IsDetailCustomization: true 추가)
json_path = os.path.abspath(r"d:\Projects\Unreal\PerforceTest\PerforceTest\TA\TAPython\Python\PPPreset\PPPreset.json")
json_path = json_path.replace("\\", "/")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = actor_subsystem.get_all_level_actors()

floor_actor = None
for actor in actors:
    if isinstance(actor, unreal.StaticMeshActor) and "Floor" in actor.get_actor_label():
        floor_actor = actor
        break

if floor_actor:
    components = floor_actor.get_components_by_class(unreal.StaticMeshComponent)
    if components:
        mesh_comp = components[0]
        result = unreal.ChameleonData.add_detail_customization(mesh_comp, json_path)
        unreal.log(f"IsDetailCustomization: true로 등록 결과: {result}")
        unreal.ChameleonData.log_all_saved_detail_customization()
        unreal.log("=" * 50)
        unreal.log(f"{floor_actor.get_actor_label()} 선택하세요")
        unreal.log("=" * 50)
