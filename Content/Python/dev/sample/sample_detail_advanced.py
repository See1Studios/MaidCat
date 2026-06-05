"""
TAPython DetailPanelCustomization - 고급 샘플

등록 상태 확인, 조건부 등록, 에러 처리 등 고급 기능 예제입니다.
"""

import unreal


def check_customization_status():
    """현재 등록된 커스터마이제이션 상태 확인"""
    
    unreal.log("=" * 60)
    unreal.log("📊 커스터마이제이션 상태 확인")
    unreal.log("=" * 60)
    
    # 1. 등록 가능한 클래스 목록 (296개)
    classes = unreal.ChameleonData.get_detail_panel_customized_class_names()
    unreal.log(f"\n✅ 등록 가능한 클래스: {len(classes)}개")
    
    # 주요 클래스만 표시
    important_classes = [
        "PostProcessVolume", "CameraComponent", "StaticMeshComponent",
        "Light", "DirectionalLight", "PointLight", "SpotLight",
        "Actor", "StaticMeshActor", "CameraActor"
    ]
    
    unreal.log("\n주요 클래스:")
    for cls in important_classes:
        if cls in classes:
            unreal.log(f"  ✅ {cls}")
        else:
            unreal.log(f"  ❌ {cls} (사용 불가)")
    
    # 2. 현재 등록된 커스터마이제이션 목록
    unreal.log("\n" + "-" * 60)
    unreal.log("현재 등록된 커스터마이제이션:")
    unreal.log("-" * 60)
    unreal.ChameleonData.log_all_saved_detail_customization()


def smart_register_customization(actor, json_path, force=False):
    """
    스마트 등록 함수 - 이미 등록되었는지 확인 후 등록
    
    Args:
        actor: 대상 액터/컴포넌트
        json_path: JSON 경로
        force: True면 재등록, False면 중복 체크
    
    Returns:
        bool: 등록 성공 여부
    """
    
    actor_name = actor.get_name()
    actor_type = actor.get_class().get_name()
    
    unreal.log(f"\n📌 대상: {actor_name} ({actor_type})")
    
    # 1. 클래스 지원 여부 확인
    supported_classes = unreal.ChameleonData.get_detail_panel_customized_class_names()
    if actor_type not in supported_classes:
        unreal.log_warning(f"⚠️ {actor_type}는 지원되지 않는 클래스입니다.")
        return False
    
    # 2. 이미 등록되었는지 확인 (force=False인 경우)
    if not force:
        # TODO: 등록 여부 확인 로직 (현재 API 제한으로 구현 어려움)
        unreal.log("ℹ️ 중복 체크 생략 (force=False)")
    
    # 3. 등록 시도
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    
    if result:
        unreal.log(f"✅ 등록 성공!")
    else:
        unreal.log_error(f"❌ 등록 실패!")
    
    return result


def register_with_validation():
    """검증 후 등록 - 선택된 액터에 대해 철저히 검증 후 등록"""
    
    unreal.log("=" * 60)
    unreal.log("🔍 검증 후 등록")
    unreal.log("=" * 60)
    
    # 1. 액터 선택 확인
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    if not actors:
        unreal.log_error("❌ 액터를 선택해주세요!")
        return False
    
    actor = actors[0]
    actor_name = actor.get_name()
    actor_type = actor.get_class().get_name()
    
    unreal.log(f"\n선택된 액터:")
    unreal.log(f"  이름: {actor_name}")
    unreal.log(f"  타입: {actor_type}")
    
    # 2. JSON 파일 경로
    json_path = "PPPreset/PPPreset.json"
    unreal.log(f"\nJSON 경로: {json_path}")
    
    # 3. 지원 클래스 확인
    supported_classes = unreal.ChameleonData.get_detail_panel_customized_class_names()
    if actor_type not in supported_classes:
        unreal.log_error(f"❌ {actor_type}는 지원되지 않는 클래스입니다!")
        unreal.log(f"   지원되는 클래스 수: {len(supported_classes)}개")
        return False
    
    unreal.log(f"✅ {actor_type}는 지원되는 클래스입니다.")
    
    # 4. 등록 시도
    unreal.log("\n🚀 등록 시도 중...")
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    
    if result:
        unreal.log("=" * 60)
        unreal.log("✅ 등록 완료!")
        unreal.log("=" * 60)
        unreal.log("👉 디테일 패널을 확인하세요.")
    else:
        unreal.log("=" * 60)
        unreal.log_error("❌ 등록 실패!")
        unreal.log("=" * 60)
        unreal.log("디버깅 팁:")
        unreal.log("  1. config.ini에서 LogCreateWidget=True 확인")
        unreal.log("  2. Saved/Logs/*.log 파일 확인")
        unreal.log("  3. JSON 파일 경로 확인")
        unreal.log("  4. InitPyCmd 필드 확인")
    
    return result


def batch_register_by_class(class_type, json_path):
    """
    특정 클래스의 모든 인스턴스에 일괄 등록
    
    Args:
        class_type: 대상 클래스 (예: unreal.PostProcessVolume)
        json_path: JSON 경로
    
    Returns:
        int: 등록 성공 개수
    """
    
    class_name = class_type.__name__
    unreal.log("=" * 60)
    unreal.log(f"📦 {class_name} 일괄 등록")
    unreal.log("=" * 60)
    
    # 1. 지원 클래스 확인
    supported_classes = unreal.ChameleonData.get_detail_panel_customized_class_names()
    if class_name not in supported_classes:
        unreal.log_error(f"❌ {class_name}는 지원되지 않는 클래스입니다!")
        return 0
    
    # 2. 해당 클래스의 모든 인스턴스 찾기
    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    targets = [a for a in all_actors if isinstance(a, class_type)]
    
    unreal.log(f"\n🎯 발견된 {class_name}: {len(targets)}개")
    
    if not targets:
        unreal.log_warning(f"⚠️ {class_name} 인스턴스가 없습니다!")
        return 0
    
    # 3. 일괄 등록
    success_count = 0
    fail_count = 0
    
    for i, target in enumerate(targets, 1):
        unreal.log(f"\n[{i}/{len(targets)}] {target.get_name()}")
        
        result = unreal.ChameleonData.add_detail_customization(target, json_path)
        if result:
            success_count += 1
            unreal.log(f"  ✅ 성공")
        else:
            fail_count += 1
            unreal.log_error(f"  ❌ 실패")
    
    # 4. 결과 요약
    unreal.log("\n" + "=" * 60)
    unreal.log("결과 요약:")
    unreal.log(f"  ✅ 성공: {success_count}")
    unreal.log(f"  ❌ 실패: {fail_count}")
    unreal.log(f"  📊 총계: {len(targets)}")
    unreal.log("=" * 60)
    
    return success_count


def get_customized_object_info(unique_id):
    """UniqueID로 커스터마이즈된 객체 정보 가져오기"""
    
    unreal.log(f"🔍 UniqueID {unique_id} 조회 중...")
    
    obj = unreal.ChameleonData.get_customized_object(unique_id)
    if obj:
        unreal.log(f"✅ 객체 발견!")
        unreal.log(f"   타입: {obj.get_class().get_name()}")
        unreal.log(f"   이름: {obj.get_name()}")
        unreal.log(f"   경로: {obj.get_path_name()}")
        return obj
    else:
        unreal.log_warning(f"⚠️ UniqueID {unique_id}에 해당하는 객체가 없습니다.")
        return None


if __name__ == "__main__":
    # 옵션 1: 상태 확인
    check_customization_status()
    
    # 옵션 2: 검증 후 등록
    # register_with_validation()
    
    # 옵션 3: 클래스별 일괄 등록
    # batch_register_by_class(unreal.PostProcessVolume, "PPPreset/PPPreset.json")
    # batch_register_by_class(unreal.DirectionalLight, "PPPreset/PPPreset.json")
    
    # 옵션 4: UniqueID로 객체 조회
    # get_customized_object_info(54867)
