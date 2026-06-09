"""
디테일 커스터마이징 디버그 테스트

왜 디테일 패널에 버튼이 표시되지 않는지 확인합니다.
"""

import unreal
import os


def debug_detail_customization():
    """디테일 커스터마이징 상세 디버그"""
    
    unreal.log("="*80)
    unreal.log("🔍 디테일 커스터마이징 디버그")
    unreal.log("="*80)
    
    # 1. 등록된 클래스 확인
    unreal.log("\n1. 등록 가능한 클래스 확인:")
    try:
        class_names = unreal.ChameleonData.get_detail_panel_customized_class_names()
        unreal.log(f"   총 {len(class_names)}개 클래스")
        
        # PostProcessVolume이 있는지 확인
        if "PostProcessVolume" in class_names:
            unreal.log("   ✅ PostProcessVolume 등록됨")
        else:
            unreal.log("   ❌ PostProcessVolume 등록 안됨")
            unreal.log("   → config.ini에 ClassName=PostProcessVolume 추가 필요")
        
        if "CameraComponent" in class_names:
            unreal.log("   ✅ CameraComponent 등록됨")
        else:
            unreal.log("   ❌ CameraComponent 등록 안됨")
    except Exception as e:
        unreal.log_error(f"   예외: {e}")
    
    # 2. 선택된 Actor 확인
    unreal.log("\n2. 선택된 Actor 확인:")
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    
    if not selected_actors:
        unreal.log_warning("   ⚠️  선택된 Actor 없음")
        unreal.log("="*80)
        return
    
    actor = selected_actors[0]
    unreal.log(f"   Actor: {actor.get_name()}")
    unreal.log(f"   Class: {actor.__class__.__name__}")
    
    # 3. JSON 파일 확인
    unreal.log("\n3. UI JSON 파일 확인:")
    project_dir = unreal.Paths.project_dir()
    test_json = os.path.join(project_dir, "TA", "TAPython", "UI", "pp_preset_detail_test.json")
    
    if os.path.exists(test_json):
        unreal.log(f"   ✅ JSON 파일 존재: {test_json}")
        
        # JSON 내용 확인
        with open(test_json, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"IsDetailCustomization": true' in content:
                unreal.log("   ✅ IsDetailCustomization: true 설정됨")
            else:
                unreal.log("   ❌ IsDetailCustomization 설정 안됨")
    else:
        unreal.log(f"   ❌ JSON 파일 없음: {test_json}")
    
    # 4. 커스터마이징 추가 시도
    unreal.log("\n4. 커스터마이징 추가:")
    try:
        result = unreal.ChameleonData.add_detail_customization(actor, test_json)
        
        if result:
            unreal.log("   ✅ add_detail_customization() 성공")
            unreal.log("   → API 호출은 성공했지만 디테일 패널에 반영되지 않을 수 있음")
        else:
            unreal.log("   ❌ add_detail_customization() 실패 (False 반환)")
            
    except Exception as e:
        unreal.log_error(f"   예외: {e}")
    
    # 5. 대안: Chameleon Tool 직접 띄우기
    unreal.log("\n5. 대안: Chameleon Tool을 별도 창으로 띄우기 테스트:")
    unreal.log("   (디테일 패널 커스터마이징 대신 독립 창으로 표시)")
    
    try:
        # IsDetailCustomization을 false로 한 별도 JSON 사용
        standalone_json = os.path.join(project_dir, "TA", "TAPython", "UI", "pp_preset_standalone.json")
        
        # 독립 창용 JSON 생성
        standalone_content = """{
    "TabLabel": "Post Process Preset Manager",
    "InitTabSize": [400, 200],
    "InitTabPosition": [100, 100],
    "Body": {
        "type": "SVerticalBox",
        "slots": [
            {
                "slot": {"padding": {"left": 10, "top": 10, "right": 10, "bottom": 5}},
                "widget": {
                    "type": "STextBlock",
                    "text": "Post Process Preset Manager",
                    "justification": "Center",
                    "font": {"size": 16}
                }
            },
            {
                "slot": {"padding": {"left": 10, "top": 5, "right": 10, "bottom": 10}},
                "widget": {
                    "type": "SHorizontalBox",
                    "slots": [
                        {
                            "slot": {"h_align": "Fill", "padding": {"right": 5}},
                            "widget": {
                                "type": "SButton",
                                "text": "Save Preset",
                                "on_clicked": "print('✅ Save Preset 클릭!')"
                            }
                        },
                        {
                            "slot": {"h_align": "Fill", "padding": {"left": 5}},
                            "widget": {
                                "type": "SButton",
                                "text": "Load Preset",
                                "on_clicked": "print('✅ Load Preset 클릭!')"
                            }
                        }
                    ]
                }
            },
            {
                "slot": {"padding": {"left": 10, "top": 5, "right": 10, "bottom": 10}},
                "widget": {
                    "type": "STextBlock",
                    "text": "💡 이 창은 독립 창으로 표시됩니다",
                    "justification": "Center",
                    "color": [0.5, 0.8, 1.0, 1.0]
                }
            }
        ]
    }
}"""
        
        with open(standalone_json, 'w', encoding='utf-8') as f:
            f.write(standalone_content)
        
        unreal.log(f"   ✅ 독립 창용 JSON 생성: {standalone_json}")
        unreal.log("   → 다음 명령어로 창 띄우기:")
        unreal.log(f"   unreal.ChameleonData.launch_chameleon_tool('{standalone_json}')")
        
        # 실제로 창 띄우기
        unreal.log("\n   🚀 독립 창 띄우기 시도...")
        unreal.ChameleonData.launch_chameleon_tool(standalone_json)
        unreal.log("   ✅ 독립 창이 표시되어야 합니다!")
        
    except Exception as e:
        unreal.log_error(f"   예외: {e}")
    
    unreal.log("\n" + "="*80)
    unreal.log("📊 결론:")
    unreal.log("="*80)
    unreal.log("디테일 패널 커스터마이징이 작동하지 않는 이유:")
    unreal.log("1. config.ini 설정이 제대로 로드되지 않았을 수 있음")
    unreal.log("2. PostProcessVolume 클래스가 등록 목록에 없을 수 있음")
    unreal.log("3. TAPython 버전이 디테일 커스터마이징을 완벽히 지원하지 않을 수 있음")
    unreal.log("")
    unreal.log("💡 대안:")
    unreal.log("- 독립 Chameleon 창 사용 (위에서 테스트함)")
    unreal.log("- 메뉴 기반 접근 (레벨 에디터 메뉴에 추가)")
    unreal.log("- 컨텍스트 메뉴 추가 (Actor 우클릭 메뉴)")
    unreal.log("="*80)


if __name__ == "__main__":
    debug_detail_customization()
