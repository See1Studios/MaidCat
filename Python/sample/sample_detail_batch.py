"""
TAPython DetailPanelCustomization - 일괄 등록 샘플

레벨의 모든 PostProcessVolume에 커스터마이제이션을 일괄 등록하는 예제입니다.
"""

import unreal


def register_all_postprocess_volumes():
    """레벨의 모든 PostProcessVolume에 커스터마이제이션 등록"""
    
    unreal.log("=" * 60)
    unreal.log("PostProcessVolume 일괄 등록 시작")
    unreal.log("=" * 60)
    
    # 1. 레벨의 모든 액터 가져오기
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    unreal.log(f"📊 전체 액터 수: {len(all_actors)}")
    
    # 2. PostProcessVolume만 필터링
    pp_volumes = [a for a in all_actors if isinstance(a, unreal.PostProcessVolume)]
    unreal.log(f"🎯 PostProcessVolume 수: {len(pp_volumes)}")
    
    if not pp_volumes:
        unreal.log_warning("⚠️ PostProcessVolume이 없습니다!")
        return 0
    
    # 3. JSON 경로
    json_path = "PPPreset/PPPreset.json"
    
    # 4. 각 볼륨에 등록
    success_count = 0
    for i, volume in enumerate(pp_volumes, 1):
        unreal.log(f"\n[{i}/{len(pp_volumes)}] 처리 중: {volume.get_name()}")
        
        result = unreal.ChameleonData.add_detail_customization(volume, json_path)
        if result:
            success_count += 1
            unreal.log(f"  ✅ 등록 성공")
        else:
            unreal.log_error(f"  ❌ 등록 실패")
    
    # 5. 결과 요약
    unreal.log("\n" + "=" * 60)
    unreal.log(f"✨ 완료: {success_count}/{len(pp_volumes)}개 등록")
    unreal.log("=" * 60)
    
    return success_count


def register_all_camera_components():
    """레벨의 모든 CameraComponent에 커스터마이제이션 등록"""
    
    unreal.log("=" * 60)
    unreal.log("CameraComponent 일괄 등록 시작")
    unreal.log("=" * 60)
    
    # 1. 모든 액터 가져오기
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    
    # 2. CameraComponent가 있는 액터 찾기
    camera_actors = []
    for actor in all_actors:
        cameras = actor.get_components_by_class(unreal.CameraComponent)
        if cameras:
            camera_actors.append((actor, cameras[0]))  # 첫 번째 카메라만
    
    unreal.log(f"📊 카메라가 있는 액터: {len(camera_actors)}")
    
    if not camera_actors:
        unreal.log_warning("⚠️ CameraComponent가 없습니다!")
        return 0
    
    # 3. JSON 경로 (카메라용 다른 UI 사용 가능)
    json_path = "PPPreset/PPPreset.json"
    
    # 4. 각 컴포넌트에 등록
    success_count = 0
    for i, (actor, camera) in enumerate(camera_actors, 1):
        unreal.log(f"\n[{i}/{len(camera_actors)}] 처리 중: {actor.get_name()}")
        
        result = unreal.ChameleonData.add_detail_customization(camera, json_path)
        if result:
            success_count += 1
            unreal.log(f"  ✅ 등록 성공 (CameraComponent)")
        else:
            unreal.log_error(f"  ❌ 등록 실패")
    
    # 5. 결과 요약
    unreal.log("\n" + "=" * 60)
    unreal.log(f"✨ 완료: {success_count}/{len(camera_actors)}개 등록")
    unreal.log("=" * 60)
    
    return success_count


def clear_all_customizations():
    """모든 커스터마이제이션 제거"""
    
    unreal.log("🧹 모든 커스터마이제이션 제거 중...")
    
    # 제거 전 목록 출력
    unreal.ChameleonData.log_all_saved_detail_customization()
    
    # 모두 제거
    unreal.ChameleonData.clear_detail_customization()
    
    unreal.log("✅ 제거 완료!")


if __name__ == "__main__":
    # 옵션 1: PostProcessVolume 일괄 등록
    register_all_postprocess_volumes()
    
    # 옵션 2: CameraComponent 일괄 등록
    # register_all_camera_components()
    
    # 옵션 3: 모두 제거
    # clear_all_customizations()
