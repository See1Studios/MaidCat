"""
ToolMenus 빠른 테스트
Unreal Engine에서 바로 실행 가능한 간단한 예시들
"""

def quick_test_basic_menu():
    """기본 메뉴 테스트"""
    import unreal
    
    print("🧪 기본 메뉴 테스트 시작")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    if not menu:
        print("❌ 메뉴를 찾을 수 없습니다.")
        return
    
    # 테스트 섹션 추가
    test_section = unreal.Name("QuickTest")
    menu.add_section(test_section, unreal.Text("⚡ Quick Test"))
    
    # 기본 엔트리
    entry = unreal.ToolMenuEntry(
        name=unreal.Name("hello_world"),
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    entry.set_label(unreal.Text("👋 Hello World"))
    entry.set_tool_tip(unreal.Text("기본 테스트 엔트리"))
    entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name(""),
        string="print('👋 Hello from ToolMenu!')"
    )
    
    menu.add_menu_entry(test_section, entry)
    tool_menus.refresh_all_widgets()
    
    print("✅ 테스트 메뉴 추가됨! 콘텐츠 브라우저에서 우클릭해보세요.")

def quick_test_context_menu():
    """Context 인식 메뉴 테스트"""
    import unreal
    
    print("🧪 Context 메뉴 테스트 시작")
    
    # 현재 선택된 것들 확인
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    print(f"📋 현재 선택된 애셋: {len(selected_assets)}개")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    # 기존 테스트 섹션 제거
    try:
        menu.remove_section(unreal.Name("ContextTest"))
    except:
        pass
    
    # Context 기반 섹션 추가
    if selected_assets:
        context_section = unreal.Name("ContextTest")
        menu.add_section(context_section, unreal.Text("🎯 Context Test"))
        
        # 선택된 애셋 수 표시
        count_entry = unreal.ToolMenuEntry(
            name=unreal.Name("asset_count"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        count_entry.set_label(unreal.Text(f"📊 {len(selected_assets)}개 선택됨"))
        count_entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string=f"print('📊 총 {len(selected_assets)}개의 애셋이 선택되어 있습니다.')"
        )
        
        menu.add_menu_entry(context_section, count_entry)
        
        # 첫 번째 애셋 정보 표시
        if selected_assets:
            first_asset = selected_assets[0]
            asset_info_entry = unreal.ToolMenuEntry(
                name=unreal.Name("first_asset_info"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            asset_name = first_asset.get_name()
            asset_type = first_asset.get_class().get_name()
            asset_info_entry.set_label(unreal.Text(f"🔍 {asset_name}"))
            asset_info_entry.set_tool_tip(unreal.Text(f"타입: {asset_type}"))
            asset_info_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string=f"print('🔍 첫 번째 애셋: {asset_name} ({asset_type})')"
            )
            
            menu.add_menu_entry(context_section, asset_info_entry)
        
        tool_menus.refresh_all_widgets()
        print("✅ Context 테스트 메뉴 추가됨!")
    else:
        print("⚠️ 애셋을 먼저 선택해주세요.")

def quick_test_submenu():
    """서브메뉴 테스트"""
    import unreal
    
    print("🧪 서브메뉴 테스트 시작")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    # 기존 테스트 섹션 제거
    try:
        menu.remove_section(unreal.Name("SubmenuTest"))
    except:
        pass
    
    # 서브메뉴 섹션 생성
    submenu_section = unreal.Name("SubmenuTest")
    menu.add_section(submenu_section, unreal.Text("🌳 Submenu Test"))
    
    # 서브메뉴 생성
    test_submenu = menu.add_sub_menu(
        owner=unreal.Name(""),
        section_name=submenu_section,
        name=unreal.Name("test_submenu"),
        label=unreal.Text("📂 Test Submenu"),
        tool_tip=unreal.Text("서브메뉴 테스트")
    )
    
    if test_submenu:
        # 서브메뉴 섹션
        sub_section = unreal.Name("sub_options")
        test_submenu.add_section(sub_section, unreal.Text("Options"))
        
        # 서브메뉴 엔트리들
        for i in range(3):
            sub_entry = unreal.ToolMenuEntry(
                name=unreal.Name(f"sub_option_{i}"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            sub_entry.set_label(unreal.Text(f"⚙️ Option {i+1}"))
            sub_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string=f"print('⚙️ 서브메뉴 옵션 {i+1} 실행!')"
            )
            test_submenu.add_menu_entry(sub_section, sub_entry)
        
        tool_menus.refresh_all_widgets()
        print("✅ 서브메뉴 테스트 추가됨!")
    else:
        print("❌ 서브메뉴 생성 실패")

def cleanup_test_menus():
    """테스트 메뉴들 정리"""
    import unreal
    
    print("🧹 테스트 메뉴들 정리 중...")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    test_sections = ["QuickTest", "ContextTest", "SubmenuTest"]
    
    for section_name in test_sections:
        try:
            menu.remove_section(unreal.Name(section_name))
            print(f"  ✅ {section_name} 제거됨")
        except:
            print(f"  ⚠️ {section_name} 없음")
    
    tool_menus.refresh_all_widgets()
    print("✅ 정리 완료!")

def show_current_context():
    """현재 Context 정보 표시"""
    import unreal
    
    print("\n📋 현재 Context 정보:")
    
    # 선택된 애셋들
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        print(f"📦 선택된 애셋: {len(selected_assets)}개")
        for i, asset in enumerate(selected_assets[:5]):
            print(f"  {i+1}. {asset.get_name()} ({asset.get_class().get_name()})")
        if len(selected_assets) > 5:
            print(f"  ... 그외 {len(selected_assets) - 5}개 더")
    except Exception as e:
        print(f"❌ 애셋 정보 오류: {e}")
    
    # 선택된 폴더들
    try:
        selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
        print(f"📁 선택된 폴더: {len(selected_folders)}개")
        for folder in selected_folders:
            print(f"  📁 {folder}")
    except Exception as e:
        print(f"❌ 폴더 정보 오류: {e}")
    
    # 선택된 액터들
    try:
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        print(f"🎭 선택된 액터: {len(selected_actors)}개")
        for i, actor in enumerate(selected_actors[:3]):
            print(f"  {i+1}. {actor.get_name()} ({actor.get_class().get_name()})")
        if len(selected_actors) > 3:
            print(f"  ... 그외 {len(selected_actors) - 3}개 더")
    except Exception as e:
        print(f"❌ 액터 정보 오류: {e}")

# =============================================================================
# 실행용 함수들
# =============================================================================

def run_basic_test():
    """기본 테스트 실행"""
    quick_test_basic_menu()

def run_context_test():
    """Context 테스트 실행"""
    show_current_context()
    quick_test_context_menu()

def run_submenu_test():
    """서브메뉴 테스트 실행"""
    quick_test_submenu()

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 모든 테스트 실행 시작!\n")
    show_current_context()
    quick_test_basic_menu()
    quick_test_context_menu()
    quick_test_submenu()
    print("\n🎉 모든 테스트 완료! 콘텐츠 브라우저에서 우클릭해보세요.")

if __name__ == "__main__":
    print("📚 ToolMenus 빠른 테스트가 준비되었습니다!")
    print("\n🎯 사용 가능한 함수들:")
    print("  run_basic_test()     - 기본 메뉴 테스트")
    print("  run_context_test()   - Context 인식 테스트")
    print("  run_submenu_test()   - 서브메뉴 테스트")
    print("  run_all_tests()      - 모든 테스트 실행")
    print("  cleanup_test_menus() - 테스트 메뉴 정리")
    print("  show_current_context() - 현재 Context 표시")