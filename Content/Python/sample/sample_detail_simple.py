"""
TAPython DetailPanelCustomization - 간단한 샘플

선택된 액터에 디테일 패널 커스터마이제이션을 등록하는 가장 간단한 예제입니다.
"""

import unreal


def register_simple_customization():
    """선택된 액터에 간단한 커스터마이제이션 등록"""
    
    # 1. 선택된 액터 가져오기
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    if not actors:
        unreal.log_error("❌ 액터를 선택해주세요!")
        return False
    
    actor = actors[0]
    unreal.log(f"📌 선택된 액터: {actor.get_name()} ({actor.get_class().get_name()})")
    
    # 2. JSON 경로 지정 (Content 디렉토리 기준 상대 경로)
    json_path = "PPPreset/PPPreset.json"
    
    # 3. 커스터마이제이션 등록
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    
    # 4. 결과 확인
    if result:
        unreal.log(f"✅ 등록 성공!")
        unreal.log(f"   액터: {actor.get_name()}")
        unreal.log(f"   JSON: {json_path}")
        unreal.log(f"   👉 디테일 패널을 확인하세요!")
    else:
        unreal.log_error(f"❌ 등록 실패!")
    
    return result


if __name__ == "__main__":
    register_simple_customization()
