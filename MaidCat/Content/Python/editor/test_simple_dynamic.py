import unreal

@unreal.uclass()
class SimpleDynamicSection(unreal.ToolMenuSectionDynamic):
    
    @unreal.ufunction(override=True)
    def construct_sections(self, menu, context):
        """
        간단한 동적 섹션에서 서브메뉴 테스트
        """
        unreal.log("🔄 SimpleDynamicSection construct_sections called")
        
        # 일반 메뉴 항목 추가
        entry1 = unreal.ToolMenuEntry(
            name=unreal.Name("SimpleTest.Item1"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry1.set_label(unreal.Text("Simple Test Item"))
        entry1.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(''),
            string='unreal.log("✅ Simple test item executed!")'
        )
        menu.add_menu_entry(unreal.Name("Default"), entry1)
        
        # 서브메뉴 테스트
        unreal.log("🔄 Attempting to create submenu in dynamic section...")
        
        sub_menu = menu.add_sub_menu(
            owner=unreal.Name("MaidCat"),
            section_name=unreal.Name("Default"),
            name=unreal.Name("SimpleTest.SubMenu"),
            label=unreal.Text("Test SubMenu"),
            tool_tip=unreal.Text("Testing submenu in dynamic section")
        )
        
        if sub_menu:
            unreal.log(f"✅ Submenu created: {sub_menu.get_name()}")
            
            # 포럼에서 제안한 방법: ToolMenuEntry 직접 생성 + add_menu_entry 사용
            sub_entry = unreal.ToolMenuEntry(
                name=unreal.Name("SimpleTest.SubMenu.DirectItem"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            sub_entry.set_label(unreal.Text("Direct Entry (Forum Method)"))
            sub_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(''),
                string='unreal.log("✅ Direct submenu item executed!")'
            )
            
            # add_menu_entry 사용 (add_menu_entry_object 대신)
            sub_menu.add_menu_entry(unreal.Name("Default"), sub_entry)
            unreal.log("✅ Added direct entry to submenu")
            
            # 서브메뉴에 동적 섹션도 추가
            sub_dynamic_section = SubMenuDynamicSection()
            sub_menu.add_dynamic_section(unreal.Name("MaidCat"), sub_dynamic_section)
            unreal.log("✅ Added SubMenuDynamicSection to submenu")
            
        else:
            unreal.log("❌ Failed to create submenu in dynamic section")
        
        unreal.log("✅ Dynamic section construction completed")

@unreal.uclass()
class SubMenuDynamicSection(unreal.ToolMenuSectionDynamic):
    
    @unreal.ufunction(override=True)
    def construct_sections(self, menu, context):
        """
        서브메뉴 내부의 동적 섹션
        """
        unreal.log("🔄 SubMenuDynamicSection construct_sections called!")
        
        # 동적으로 현재 시간 기반 메뉴 생성
        import datetime
        current_time = datetime.datetime.now()
        
        # 시간 정보 표시
        time_entry = unreal.ToolMenuEntry(
            name=unreal.Name("SubDynamic.TimeInfo"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        time_entry.set_label(unreal.Text(f"Generated at: {current_time.strftime('%H:%M:%S')}"))
        time_entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(''),
            string=f'unreal.log("Time entry clicked at {current_time.strftime("%H:%M:%S")}")'
        )
        menu.add_menu_entry(unreal.Name("TimeSection"), time_entry)
        
        # 동적으로 몇 개의 도구들 추가
        tools = ["Dynamic Tool A", "Dynamic Tool B", "Dynamic Tool C"]
        for i, tool in enumerate(tools):
            tool_entry = unreal.ToolMenuEntry(
                name=unreal.Name(f"SubDynamic.Tool{i}"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            tool_entry.set_label(unreal.Text(f"{tool} (Dynamic)"))
            tool_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(''),
                string=f'unreal.log("✅ {tool} executed!")'
            )
            menu.add_menu_entry(unreal.Name("ToolsSection"), tool_entry)
        
        unreal.log("✅ SubMenuDynamicSection construction completed")

def test_submenu_with_dynamic_section():
    """
    서브메뉴에 동적 섹션을 추가하는 단순 테스트
    """
    menu_system = unreal.ToolMenus.get()
    
    # 메인 메뉴 찾기
    main_menu = menu_system.find_menu(unreal.Name("LevelEditor.MainMenu"))
    if not main_menu:
        unreal.log("❌ Main menu not found!")
        return
    
    # 서브메뉴 생성
    submenu_name = unreal.Name("LevelEditor.MainMenu.TestSubMenuDynamic")
    
    # 기존 메뉴 제거
    if menu_system.find_menu(submenu_name):
        menu_system.remove_menu(submenu_name)
    
    # 서브메뉴 생성
    submenu = main_menu.add_sub_menu(
        owner=unreal.Name("MaidCat"),
        section_name=unreal.Name("WindowLayout"),
        name=submenu_name,
        label=unreal.Text("SubMenu Dynamic"),
        tool_tip=unreal.Text("Testing submenu with dynamic section")
    )
    
    if submenu:
        unreal.log(f"✅ Created submenu: {submenu.get_name()}")
        
        # 서브메뉴에 동적 섹션 추가
        dynamic_section = SubMenuDynamicSection()
        submenu.add_dynamic_section(unreal.Name("MaidCat"), dynamic_section)
        
        unreal.log("✅ Added dynamic section to submenu")
        
        menu_system.refresh_all_widgets()
        unreal.log("🎉 Test completed! Check: Window → Main Menu → SubMenu Dynamic")
    else:
        unreal.log("❌ Failed to create submenu")

def setup_simple_dynamic_test():
    """
    간단한 동적 섹션만 테스트
    """
    menu_system = unreal.ToolMenus.get()
    
    # 메인 메뉴 찾기
    main_menu = menu_system.find_menu(unreal.Name("LevelEditor.MainMenu"))
    if not main_menu:
        unreal.log("❌ Main menu not found!")
        return
    
    # Simple Test 메뉴 생성
    test_menu_name = unreal.Name("LevelEditor.MainMenu.SimpleTest")
    
    # 기존 메뉴 제거
    if menu_system.find_menu(test_menu_name):
        menu_system.remove_menu(test_menu_name)
        unreal.log("🗑️ Removed existing test menu")
    
    # Simple Test 서브메뉴 생성
    test_menu = main_menu.add_sub_menu(
        owner=unreal.Name("MaidCat"),
        section_name=unreal.Name("WindowLayout"),
        name=test_menu_name,
        label=unreal.Text("Simple Test"),
        tool_tip=unreal.Text("Simple dynamic section test")
    )
    
    if not test_menu:
        unreal.log("❌ Failed to create test menu!")
        return
    
    unreal.log(f"✅ Created test menu: {test_menu.get_name()}")
    
    # 동적 섹션 추가
    dynamic_section = SimpleDynamicSection()
    test_menu.add_dynamic_section(unreal.Name("MaidCat"), dynamic_section)
    
    # 메뉴 시스템 새로고침
    menu_system.refresh_all_widgets()
    
    unreal.log("🎉 Simple dynamic section setup completed!")

# 실행
if __name__ == "__main__":
    setup_simple_dynamic_test()