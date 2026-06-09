"""
OutlineSystem 테스트 스크립트
- Custom Depth Stencil 활성화 확인
- 뷰포트의 선택된 액터에 Custom Depth 설정
- Outline 콘솔 명령어로 활성화
"""
import unreal

def test_outline():
    """OutlineSystem 테스트"""
    
    # 1. 선택된 액터 가져오기
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = actor_subsystem.get_selected_level_actors()
    
    if len(selected_actors) == 0:
        unreal.log_warning("OutlineTest: 뷰포트에서 액터를 먼저 선택해주세요!")
        return
    
    # 2. 선택된 액터들에 Custom Depth Stencil 설정
    for actor in selected_actors:
        components = actor.get_components_by_class(unreal.PrimitiveComponent)
        for comp in components:
            comp.set_render_custom_depth(True)
            comp.set_custom_depth_stencil_value(1)
            unreal.log(f"OutlineTest: {actor.get_actor_label()} - CustomDepth 활성화, Stencil=1")
    
    # 3. Outline 콘솔 명령어 실행
    unreal.SystemLibrary.execute_console_command(None, "Outline.SetEnabled 1")
    unreal.SystemLibrary.execute_console_command(None, "Outline.SetStencil 1")
    unreal.SystemLibrary.execute_console_command(None, "Outline.SetColor 1 0 0 1")
    unreal.SystemLibrary.execute_console_command(None, "Outline.SetThickness 2.0")
    
    unreal.log("OutlineTest: 아웃라인 시스템 활성화 완료! (빨간색, 두께 2.0)")
    unreal.log("OutlineTest: 비활성화하려면: Outline.SetEnabled 0")

test_outline()
