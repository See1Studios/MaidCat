"""
레벨 로더 테스트 스크립트
"""
import unreal
from tool import level_loader

def test_registration():
    """레벨 로더 메뉴 등록 테스트"""
    try:
        unreal.log("=" * 60)
        unreal.log("🧪 레벨 로더 메뉴 등록 테스트 시작")
        unreal.log("=" * 60)
        
        # 등록 함수 호출
        level_loader.register()
        
        # 메뉴 확인
        tool_menus = unreal.ToolMenus.get()
        
        # 아웃라이너 메뉴 확인
        outliner_menu = tool_menus.find_menu(unreal.Name("LevelEditor.LevelEditorSceneOutliner.ContextMenu"))
        if outliner_menu:
            unreal.log(f"✅ 아웃라이너 메뉴 발견: {outliner_menu.menu_name}")
        else:
            unreal.log_warning("⚠️ 아웃라이너 메뉴를 찾을 수 없습니다")
        
        # 월드 브라우저 메뉴 확인
        world_browser_menu = tool_menus.find_menu(unreal.Name("WorldBrowser.WorldHierachy.LevelContextMenu"))
        if world_browser_menu:
            unreal.log(f"✅ 월드 브라우저 메뉴 발견: {world_browser_menu.menu_name}")
        else:
            unreal.log_warning("⚠️ 월드 브라우저 메뉴를 찾을 수 없습니다")
        
        unreal.log("=" * 60)
        unreal.log("🎉 레벨 로더 메뉴 등록 테스트 완료")
        unreal.log("=" * 60)
        
    except Exception as e:
        unreal.log_error(f"❌ 테스트 실패: {e}")
        import traceback
        unreal.log_error(traceback.format_exc())

if __name__ == "__main__":
    test_registration()
