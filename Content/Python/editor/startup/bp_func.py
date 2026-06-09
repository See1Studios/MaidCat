"""
MaidCat Blueprint Function Library
블루프린트에서 사용할 수 있는 Python 함수들을 제공합니다.
"""

import unreal

@unreal.uclass()
class MaidCatBlueprintLibrary(unreal.BlueprintFunctionLibrary):
    """MaidCat Blueprint Function Library"""

    @unreal.ufunction(static=True, meta=dict(Category="MaidCat Python|Editor"))
    def get_selected_actors():
        """선택된 액터들 가져오기"""
        return unreal.EditorLevelLibrary.get_selected_level_actors()

    @unreal.ufunction(static=True, ret=int, params=[unreal.Class], meta=dict(Category="MaidCat Python|Editor"))
    def select_all_actors_of_class(actor_class):
        """특정 클래스의 모든 액터 선택"""
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        actors_of_class = [actor for actor in all_actors if isinstance(actor, actor_class)]
        unreal.EditorLevelLibrary.set_selected_level_actors(unreal.Array(unreal.Actor)(actors_of_class))
        return len(actors_of_class)

    @unreal.ufunction(static=True, ret=int, params=[unreal.Class], meta=dict(Category="MaidCat Python|Editor"))
    def get_actor_count_by_class(actor_class):
        """특정 클래스의 액터 개수 반환"""
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        count = len([actor for actor in all_actors if isinstance(actor, actor_class)])
        return count

    @unreal.ufunction(static=True, ret=int, params=[str, str], meta=dict(Category="MaidCat Python|Assets"))
    def bulk_rename_assets(old_prefix, new_prefix):
        """선택된 에셋들 일괄 이름 변경"""
        utility = unreal.EditorUtilityLibrary()
        selected_assets = utility.get_selected_assets()
        asset_paths = [asset.get_path_name() for asset in selected_assets]
        
        renamed_count = 0
        for asset_path in asset_paths:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            if asset:
                current_name = asset.get_name()
                if current_name.startswith(old_prefix):
                    new_name = current_name.replace(old_prefix, new_prefix, 1)
                    path_parts = asset_path.rsplit("/", 1)
                    new_path = f"{path_parts[0]}/{new_name}"
                    success = unreal.EditorAssetLibrary.rename_asset(asset_path, new_path)
                    if success:
                        renamed_count += 1
        
        return renamed_count

    @unreal.ufunction(static=True, ret=int, params=[unreal.StaticMesh], meta=dict(Category="MaidCat Python|Mesh"))
    def get_static_mesh_triangles(static_mesh):
        """스태틱 메시의 삼각형 개수 반환"""
        if static_mesh and static_mesh.get_render_data():
            render_data = static_mesh.get_render_data()
            if render_data.lod_resources:
                return render_data.lod_resources[0].get_num_triangles()
        return 0

    @unreal.ufunction(static=True, ret=int, meta=dict(Category="MaidCat Python|Debug"))
    def log_selected_actors_info():
        """선택된 액터들의 정보를 로그에 출력"""
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        
        unreal.log(f"=== 선택된 액터 정보 ({len(selected_actors)}개) ===")
        for i, actor in enumerate(selected_actors):
            location = actor.get_actor_location()
            rotation = actor.get_actor_rotation()
            scale = actor.get_actor_scale3d()
            
            unreal.log(f"[{i+1}] {actor.get_name()} ({actor.__class__.__name__})")
            unreal.log(f"    위치: {location}")
            unreal.log(f"    회전: {rotation}")
            unreal.log(f"    스케일: {scale}")
        
        return len(selected_actors)

    @unreal.ufunction(static=True, ret=float, params=[unreal.Actor, unreal.Actor], meta=dict(Category="MaidCat Python|Gameplay"))
    def get_distance_between_actors(actor1, actor2):
        """두 액터 사이의 거리 계산"""
        if not actor1 or not actor2:
            return 0.0
        
        location1 = actor1.get_actor_location()
        location2 = actor2.get_actor_location()
        
        return unreal.Vector.distance(location1, location2)

    @unreal.ufunction(static=True, ret=int, params=[unreal.StaticMesh], meta=dict(Category="MaidCat Python|Mesh"))
    def set_static_mesh_for_selected_actors(static_mesh):
        """선택된 액터들에 스태틱 메시 설정"""
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        updated_count = 0
        
        for actor in selected_actors:
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    mesh_component.set_static_mesh(static_mesh)
                    updated_count += 1
        
        return updated_count

    @unreal.ufunction(static=True, ret=int, params=[unreal.MaterialInterface, int], meta=dict(Category="MaidCat Python|Material"))
    def apply_material_to_selected_actors(material, material_slot):
        """선택된 액터들에 머티리얼 적용"""
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        updated_count = 0
        
        for actor in selected_actors:
            mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            if not mesh_component:
                mesh_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            
            if mesh_component:
                mesh_component.set_material(material_slot, material)
                updated_count += 1
        
        return updated_count

    @unreal.ufunction(static=True, ret=int, params=[float, str], meta=dict(Category="MaidCat Python|Transform"))
    def distribute_actors_evenly(spacing, axis):
        """선택된 액터들을 균등하게 배치"""
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        if len(selected_actors) < 2:
            return 0
        
        # 액터들을 정렬
        if axis.upper() == "X":
            selected_actors.sort(key=lambda a: a.get_actor_location().x)
        elif axis.upper() == "Y":
            selected_actors.sort(key=lambda a: a.get_actor_location().y)
        elif axis.upper() == "Z":
            selected_actors.sort(key=lambda a: a.get_actor_location().z)
        
        # 균등하게 배치
        for i, actor in enumerate(selected_actors):
            location = actor.get_actor_location()
            if axis.upper() == "X":
                location.x = i * spacing
            elif axis.upper() == "Y":
                location.y = i * spacing
            elif axis.upper() == "Z":
                location.z = i * spacing
            
            actor.set_actor_location(location, False, True)
        
        return len(selected_actors)


def initialize_maidcat_library():
    """MaidCat 라이브러리 초기화"""
    unreal.log("🐱 MaidCat Blueprint Function Library 초기화 완료!")
    unreal.log("사용 가능한 함수들:")
    unreal.log("  📁 MaidCat Python|Editor:")
    unreal.log("    - get_selected_actors: 선택된 액터들 가져오기")
    unreal.log("    - select_all_actors_of_class: 특정 클래스의 모든 액터 선택")
    unreal.log("    - get_actor_count_by_class: 특정 클래스의 액터 개수 반환")
    unreal.log("  📦 MaidCat Python|Assets:")
    unreal.log("    - bulk_rename_assets: 선택된 에셋들 일괄 이름 변경")
    unreal.log("  🔺 MaidCat Python|Mesh:")
    unreal.log("    - get_static_mesh_triangles: 스태틱 메시의 삼각형 개수 반환")
    unreal.log("    - set_static_mesh_for_selected_actors: 선택된 액터들에 스태틱 메시 설정")
    unreal.log("  🎨 MaidCat Python|Material:")
    unreal.log("    - apply_material_to_selected_actors: 선택된 액터들에 머티리얼 적용")
    unreal.log("  📐 MaidCat Python|Transform:")
    unreal.log("    - distribute_actors_evenly: 선택된 액터들을 균등하게 배치")
    unreal.log("  🐛 MaidCat Python|Debug:")
    unreal.log("    - log_selected_actors_info: 선택된 액터들의 정보를 로그에 출력")
    unreal.log("  🎮 MaidCat Python|Gameplay:")
    unreal.log("    - get_distance_between_actors: 두 액터 사이의 거리 계산")

if __name__ == "__main__":
    initialize_maidcat_library()
