"""
TAPython DetailPanelCustomization - UniqueID 활용 샘플

DetailPanelCustomization에서 생성되는 UniqueID를 활용하여
위젯 인스턴스에 접근하고 동적으로 제어하는 예제입니다.

UniqueID는 TAPython이 각 커스터마이징된 객체에 할당하는 고유 식별자입니다.
로그에서 "UniqueID: 12345" 형태로 확인할 수 있습니다.
"""

import unreal


def extract_uniqueid_from_log():
    """
    로그 파일에서 UniqueID 추출하기
    
    로그 예시:
    PythonTA: SetDetailCustomizationWidget call. UniqueID: 54867, type: PostProcessVolume
    """
    
    unreal.log("=" * 60)
    unreal.log("📋 로그에서 UniqueID 추출 방법")
    unreal.log("=" * 60)
    
    unreal.log("""
로그 파일 위치:
  {ProjectRoot}/Saved/Logs/See1Unreal.log (또는 프로젝트명.log)

찾을 내용:
  "PythonTA: SetDetailCustomizationWidget call. UniqueID: XXXXX"

UniqueID 사용처:
  - get_customized_object(unique_id) - 객체 가져오기
  - get_chameleon_data(json_path, unique_id) - ChameleonData 가져오기
    """)
    
    unreal.log("=" * 60)


def get_object_by_uniqueid(unique_id):
    """
    UniqueID로 커스터마이징된 객체 가져오기
    
    Args:
        unique_id (int): 로그에서 확인한 UniqueID
    
    Returns:
        Object: 커스터마이징된 객체 (없으면 None)
    """
    
    unreal.log("=" * 60)
    unreal.log(f"🔍 UniqueID {unique_id}로 객체 조회")
    unreal.log("=" * 60)
    
    try:
        obj = unreal.ChameleonData.get_customized_object(unique_id)
        
        if obj:
            unreal.log(f"✅ 객체 발견!")
            unreal.log(f"   타입: {obj.get_class().get_name()}")
            unreal.log(f"   이름: {obj.get_name()}")
            unreal.log(f"   경로: {obj.get_path_name()}")
            
            # 추가 정보 (타입별)
            if isinstance(obj, unreal.PostProcessVolume):
                unreal.log(f"   우선순위: {obj.get_editor_property('priority')}")
                unreal.log(f"   블렌드 반경: {obj.get_editor_property('blend_radius')}")
            
            elif isinstance(obj, unreal.CameraComponent):
                unreal.log(f"   FOV: {obj.get_editor_property('field_of_view')}")
            
            return obj
        else:
            unreal.log_warning(f"⚠️ UniqueID {unique_id}에 해당하는 객체가 없습니다.")
            unreal.log("   가능한 이유:")
            unreal.log("   1. 해당 객체가 제거되었음")
            unreal.log("   2. 커스터마이징이 clear되었음")
            unreal.log("   3. UniqueID가 잘못되었음")
            return None
            
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return None
    finally:
        unreal.log("=" * 60)


def get_chameleon_data_by_uniqueid(json_path, unique_id):
    """
    UniqueID로 ChameleonData 인스턴스 가져오기
    
    ChameleonData는 JSON UI의 Python 측 컨트롤러입니다.
    이를 통해 위젯의 내용을 동적으로 변경할 수 있습니다.
    
    Args:
        json_path (str): JSON 경로 (상대 경로)
        unique_id (int): UniqueID
    
    Returns:
        ChameleonData: UI 컨트롤러 객체
    """
    
    unreal.log("=" * 60)
    unreal.log(f"🎨 ChameleonData 가져오기")
    unreal.log("=" * 60)
    unreal.log(f"   JSON: {json_path}")
    unreal.log(f"   UniqueID: {unique_id}")
    
    try:
        # ChameleonData 가져오기
        data = unreal.PythonBPLib.get_chameleon_data(json_path, unique_id)
        
        if data:
            unreal.log("✅ ChameleonData 가져오기 성공!")
            unreal.log(f"   타입: {type(data)}")
            
            # ChameleonData를 통해 위젯 제어 가능
            unreal.log("\n📝 ChameleonData 주요 메서드:")
            unreal.log("   - set_text(aka_name, text) - 텍스트 변경")
            unreal.log("   - get_text(aka_name) - 텍스트 가져오기")
            unreal.log("   - set_visibility(aka_name, visible) - 가시성 제어")
            unreal.log("   - set_combo_box_items(aka_name, items) - 콤보박스 아이템 설정")
            unreal.log("   - 등등... (Chameleon Data API 참조)")
            
            return data
        else:
            unreal.log_warning("⚠️ ChameleonData를 가져올 수 없습니다.")
            return None
            
    except Exception as e:
        unreal.log_error(f"❌ 예외 발생: {e}")
        return None
    finally:
        unreal.log("=" * 60)


def dynamic_control_example():
    """
    ChameleonData를 통한 동적 위젯 제어 예제
    
    실제 사용하려면:
    1. 로그에서 UniqueID 확인
    2. 아래 unique_id 값 수정
    3. 실행
    """
    
    unreal.log("=" * 60)
    unreal.log("🎮 동적 위젯 제어 예제")
    unreal.log("=" * 60)
    
    # ⚠️ 여기에 실제 UniqueID 입력!
    unique_id = 54867  # 예시 값 - 로그에서 확인 필요!
    json_path = "PPPreset/PPPreset.json"
    
    # 1. ChameleonData 가져오기
    data = unreal.PythonBPLib.get_chameleon_data(json_path, unique_id)
    
    if not data:
        unreal.log_error("❌ ChameleonData를 가져올 수 없습니다.")
        unreal.log("   로그에서 올바른 UniqueID를 확인하세요!")
        unreal.log("=" * 60)
        return
    
    unreal.log("✅ ChameleonData 가져오기 성공!")
    
    # 2. 위젯 제어 예제 (JSON에 aka_name이 있어야 함)
    # JSON 예시:
    # {
    #     "STextBlock": {
    #         "aka_name": "status_text",
    #         "Text": "Ready"
    #     }
    # }
    
    try:
        # 텍스트 변경 (aka_name이 "status_text"인 위젯)
        # data.set_text("status_text", "✅ 프리셋 로드 완료!")
        
        # 버튼 활성화/비활성화
        # data.set_enabled("save_button", False)
        
        # 콤보박스 아이템 설정
        # presets = ["Default", "Day", "Night", "Sunset"]
        # data.set_combo_box_items("preset_combo", presets)
        
        unreal.log("ℹ️ 위젯 제어를 위해서는:")
        unreal.log("   1. JSON에 aka_name 추가")
        unreal.log("   2. 위 주석 해제하여 테스트")
        
    except Exception as e:
        unreal.log_error(f"❌ 위젯 제어 실패: {e}")
    
    unreal.log("=" * 60)


def register_and_get_uniqueid():
    """
    객체를 등록하고 UniqueID를 얻는 워크플로우
    
    문제: add_detail_customization은 UniqueID를 반환하지 않음
    해결: 로그 파일 파싱 또는 log_all_saved_detail_customization 사용
    """
    
    unreal.log("=" * 60)
    unreal.log("📋 등록 후 UniqueID 얻기")
    unreal.log("=" * 60)
    
    # 1. 선택된 액터 가져오기
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    if not actors:
        unreal.log_error("❌ 액터를 선택해주세요!")
        unreal.log("=" * 60)
        return None
    
    actor = actors[0]
    json_path = "PPPreset/PPPreset.json"
    
    unreal.log(f"대상: {actor.get_name()}")
    unreal.log(f"JSON: {json_path}")
    
    # 2. 등록
    unreal.log("\n🚀 등록 중...")
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    
    if not result:
        unreal.log_error("❌ 등록 실패!")
        unreal.log("=" * 60)
        return None
    
    unreal.log("✅ 등록 성공!")
    
    # 3. UniqueID 찾기
    unreal.log("\n🔍 등록된 커스터마이징 목록 확인:")
    unreal.log("-" * 60)
    unreal.ChameleonData.log_all_saved_detail_customization()
    unreal.log("-" * 60)
    
    unreal.log("""
📝 UniqueID 확인 방법:

방법 1: 로그 파일 확인
  - 위치: Saved/Logs/*.log
  - 검색: "UniqueID:"
  - 예: "UniqueID: 54867, type: PostProcessVolume"

방법 2: 액터 선택 후 로그 확인
  - 에디터에서 액터 선택
  - 로그에 "SetDetailCustomizationWidget call. UniqueID: XXXXX" 출력됨

방법 3: log_all_saved_detail_customization 출력 확인
  - 위 출력에서 경로와 매칭되는 항목 찾기
    """)
    
    unreal.log("=" * 60)
    
    return actor


def find_uniqueid_for_actor(actor):
    """
    특정 액터의 UniqueID 찾기 (간접적 방법)
    
    현재 TAPython API는 직접적으로 UniqueID를 조회하는 방법을 제공하지 않습니다.
    따라서 액터를 선택하여 로그를 유발하는 방법을 사용합니다.
    
    Args:
        actor: 대상 액터
    """
    
    unreal.log("=" * 60)
    unreal.log("🔍 액터의 UniqueID 찾기")
    unreal.log("=" * 60)
    
    actor_name = actor.get_name()
    actor_path = actor.get_path_name()
    
    unreal.log(f"대상 액터: {actor_name}")
    unreal.log(f"경로: {actor_path}")
    
    unreal.log("""
UniqueID를 확인하는 방법:

1. 에디터에서 해당 액터 선택
   → 디테일 패널 열림
   → 로그에 "SetDetailCustomizationWidget call. UniqueID: XXXXX" 출력

2. 출력 로그 창에서 "UniqueID:" 검색
   → type이 해당 액터와 일치하는지 확인

3. 로그 파일 확인
   → Saved/Logs/*.log 파일 열기
   → 해당 액터 경로로 검색
   → 근처에서 UniqueID 확인

⚠️ 제한사항:
  - TAPython API는 Actor → UniqueID 직접 조회 미지원
  - 로그 파싱이 필요함
    """)
    
    unreal.log("=" * 60)


def complete_workflow_example():
    """완전한 워크플로우 예제"""
    
    unreal.log("\n" + "=" * 60)
    unreal.log("🎬 완전한 워크플로우 예제")
    unreal.log("=" * 60)
    
    # 단계 1: 액터 선택 확인
    actors = unreal.EditorLevelLibrary.get_selected_level_actors()
    if not actors:
        unreal.log_error("❌ PostProcessVolume을 선택하고 실행하세요!")
        return
    
    actor = actors[0]
    unreal.log(f"\n📌 1단계: 액터 선택")
    unreal.log(f"   이름: {actor.get_name()}")
    unreal.log(f"   타입: {actor.get_class().get_name()}")
    
    # 단계 2: 커스터마이징 등록
    json_path = "PPPreset/PPPreset.json"
    unreal.log(f"\n📝 2단계: 커스터마이징 등록")
    unreal.log(f"   JSON: {json_path}")
    
    result = unreal.ChameleonData.add_detail_customization(actor, json_path)
    if result:
        unreal.log("   ✅ 등록 성공!")
    else:
        unreal.log_error("   ❌ 등록 실패!")
        return
    
    # 단계 3: UniqueID 확인 안내
    unreal.log(f"\n🔍 3단계: UniqueID 확인")
    unreal.log("   방법 1: 에디터에서 다시 선택")
    unreal.log("           → 로그에 'UniqueID: XXXXX' 출력됨")
    unreal.log("   방법 2: log_all_saved_detail_customization() 호출")
    
    unreal.log("\n📋 현재 등록된 커스터마이징:")
    unreal.ChameleonData.log_all_saved_detail_customization()
    
    # 단계 4: ChameleonData 사용 안내
    unreal.log(f"\n🎨 4단계: ChameleonData로 위젯 제어")
    unreal.log("   # UniqueID를 54867로 가정")
    unreal.log(f"   data = unreal.PythonBPLib.get_chameleon_data('{json_path}', 54867)")
    unreal.log("   if data:")
    unreal.log("       data.set_text('status', 'Hello!')")
    unreal.log("       # 기타 위젯 제어...")
    
    unreal.log("\n" + "=" * 60)
    unreal.log("✨ 워크플로우 완료!")
    unreal.log("=" * 60)


if __name__ == "__main__":
    # 옵션 1: UniqueID 사용법 설명
    extract_uniqueid_from_log()
    
    # 옵션 2: UniqueID로 객체 가져오기
    # get_object_by_uniqueid(54867)  # 실제 UniqueID로 변경
    
    # 옵션 3: ChameleonData 가져오기
    # get_chameleon_data_by_uniqueid("PPPreset/PPPreset.json", 54867)
    
    # 옵션 4: 동적 제어 예제
    # dynamic_control_example()
    
    # 옵션 5: 등록 후 UniqueID 얻기
    # register_and_get_uniqueid()
    
    # 옵션 6: 완전한 워크플로우
    # complete_workflow_example()
