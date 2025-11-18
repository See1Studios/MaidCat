# import unreal

# # 모듈 레벨에서 DynamicSectionB 인스턴스를 캐시
# _dynamic_section_b_cache = None

# def get_dynamic_section_b():
#     """DynamicSectionB 인스턴스를 가져오거나 생성"""
#     global _dynamic_section_b_cache
#     if _dynamic_section_b_cache is None:
#         _dynamic_section_b_cache = DynamicSection()
#         unreal.log(f"모듈 레벨에서 새로운 DynamicSectionB 생성: {_dynamic_section_b_cache}")
#     else:
#         unreal.log(f"캐시된 DynamicSectionB 재사용: {_dynamic_section_b_cache}")
#     return _dynamic_section_b_cache

# @unreal.uclass()
# class EntryScript(unreal.ToolMenuEntryScript):

    
#     @unreal.ufunction(override=True)
#     def can_execute(self, context):
#         return True
    
#     @unreal.ufunction(override=True)
#     def execute(self, context):
#         pass
        

# @unreal.uclass()
# class DynamicSectionTest(unreal.ToolMenuSectionDynamic):
#     """동적 섹션 예제 클래스"""



#     def __init__(self):
#         super().__init__()
#         unreal.log(f"DynamicSectionA 생성자 실행 (모듈 레벨 캐시 사용)")

#     @unreal.ufunction(override=True)
#     def construct_sections(self, menu, context):

#         # 여기에서 넘어온 menu 는 완전한 임시 객체 (menu_name : None) 이기 때문에 이후 사용하려면 식별시켜줄 필요가 있음.
#         menu.menu_name = unreal.Name("MyDynamicMenu")
#         section_name = unreal.Name("MyDynamicSectionA")
#         sub_menu_name = unreal.Name("MySubMenu")
#         sub_menu = menu.add_sub_menu(
#             owner=menu.get_name(),
#             section_name=section_name,
#             name=sub_menu_name,
#             label=unreal.Text("서브 메뉴 A"),
#             tool_tip=unreal.Text("서브 메뉴 A 예제입니다")
#         )
#         # 서브메뉴는 MENU 타입이어야 함
#         sub_menu.menu_type = unreal.MultiBoxType.MENU

#         unreal.log(f"생성자에서 넘어온 메뉴: {menu.menu_name}")
#         unreal.log(f"만들어진 메뉴(서브 메뉴): {sub_menu.menu_name}")
#         unreal.log(f"Owner: {sub_menu.menu_owner}")
#         unreal.log(f"Parent: {sub_menu.menu_parent}")
#         unreal.log(f"Type: {sub_menu.menu_type}")
#         unreal.log("✅ DynamicSectionA가 구성되었습니다.")

#         # 테스트용 일반 Entry
#         entry_name = unreal.Name("MyDynamicMenuEntryA")
#         menu_entry = unreal.ToolMenuEntry()
#         menu_entry.name = entry_name
#         menu_entry.set_label(unreal.Text("동적 메뉴 엔트리 A"))
#         menu_entry.type = unreal.MultiBlockType.MENU_ENTRY
#         menu_entry.insert_position = unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
#         menu_entry.user_interface_action_type = unreal.UserInterfaceActionType.BUTTON

#         # 서브메뉴에 대해서는 어떤 것도 안되고 있음
#         tm = unreal.ToolMenus.get()
#         sub_menu.menu_parent = menu.menu_name
        
#         # 서브메뉴를 ToolMenus에 등록 시도
#         full_sub_menu_name = unreal.Name(f"{menu.menu_name}.{sub_menu_name}")
#         unreal.log(f"서브메뉴 등록 시도: {full_sub_menu_name}")
#         # tm.register_menu(full_sub_menu_name)

#         # 서브메뉴에 직접 동적 항목들을 추가 (DynamicSectionB 대신)
#         unreal.log("서브메뉴에 동적 항목들을 직접 추가")
        
#         # 시간 기반 동적 항목 예제
#         import datetime
#         current_time = datetime.datetime.now()
        
#         dynamic_section_name = unreal.Name("DynamicItems")
#         sub_menu.add_section(dynamic_section_name, unreal.Text("동적 항목들"))
        
#         # 현재 시간을 포함한 동적 항목
#         time_entry = unreal.ToolMenuEntry()
#         time_entry.name = unreal.Name("TimeEntry")
#         time_entry.set_label(unreal.Text(f"현재 시간: {current_time.strftime('%H:%M:%S')}"))
#         time_entry.type = unreal.MultiBlockType.MENU_ENTRY
#         time_entry.user_interface_action_type = unreal.UserInterfaceActionType.BUTTON
        
#         # 컨텍스트 기반 동적 항목
#         context_entry = unreal.ToolMenuEntry()
#         context_entry.name = unreal.Name("ContextEntry")
#         context_entry.set_label(unreal.Text(f"컨텍스트: {context}"))
#         context_entry.type = unreal.MultiBlockType.MENU_ENTRY
#         context_entry.user_interface_action_type = unreal.UserInterfaceActionType.BUTTON
        
#         sub_menu.add_menu_entry(dynamic_section_name, time_entry)
#         sub_menu.add_menu_entry(dynamic_section_name, context_entry)
        
#         unreal.log("서브메뉴에 동적 항목 직접 추가 완료")
#         # 서브 메뉴에 정적인 섹션 추가도 안됨
#         static_section_name = unreal.Name("StaticSectionA")
#         static_section_label = unreal.Text("Static Section A")
#         sub_menu.add_section(
#             static_section_name,
#             static_section_label
#         )
#         # 서브 메뉴에 정적으로 엔트리 추가도 안됨
#         sub_menu.add_menu_entry(static_section_name, menu_entry)


        
#         tm.refresh_menu_widget(sub_menu_name)



#         # 유일하게 메뉴에 엔트리 추가만 의도대로 동작하고 있음
#         # menu.add_menu_entry(section_name, menu_entry)
#         # menu.add_menu_entry(section_name, menu_entry)
#         # menu.add_menu_entry(section_name, menu_entry)
#         # menu.add_menu_entry(section_name, menu_entry)







#         # tm.refresh_menu_widget(menu.menu_name)
#         # unreal.log(f"✅ {entry_name} 추가하였습니다.")
#         # tm.refresh_all_widgets()


# @unreal.uclass()
# class DynamicSection(unreal.ToolMenuSectionDynamic):
#     """동적 섹션 예제 클래스"""
    
#     @unreal.ufunction(override=True)
#     def construct_sections(self, menu, context):
#         menu.menu_name = unreal.Name("MyDynamicMenuB")
#         unreal.log(f"DynamicSectionB.construct_sections 호출됨, 메뉴: {menu.menu_name}")
#         # 서브메뉴에 섹션 추가
#         section_name = unreal.Name("MyDynamicSectionB")
#         menu.add_section(section_name, unreal.Text("동적 섹션 B"))
        
#         # 동적 섹션에 ToolMenuEntryScript 도 안되나?
#         # 서브메뉴에 실제 메뉴 항목 추가
#         entry1 = EntryScript()
#         entry1_owner = unreal.Name("Owner")
#         entry1_name = unreal.Name("SubMenuEntry1")
#         entry1_label = unreal.Text("SubMenuEntry1")
#         entry1.init_entry(entry1_owner,menu.menu_name,section_name, entry1_name, entry1_label)
#         entry1.register_menu_entry()

#         entry2 = EntryScript()
#         entry2_owner = unreal.Name("Owner")
#         entry2_name = unreal.Name("SubMenuEntry2")
#         entry2_label = unreal.Text("SubMenuEntry2")
#         entry2.init_entry(entry2_owner,menu.menu_name,section_name, entry2_name, entry2_label)
#         entry2.register_menu_entry()

#         static_entry = unreal.ToolMenuEntry(
#         name=unreal.Name("StaticEntry1"),
#         type=unreal.MultiBlockType.MENU_ENTRY,
#         insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
#         user_interface_action_type=unreal.UserInterfaceActionType.BUTTON,
#         )
#         static_entry.set_label(unreal.Text("정적 엔트리 1"))
#         menu.add_menu_entry(section_name, static_entry)
#         ToolMenus = unreal.ToolMenus.get()
#         ToolMenus.refresh_all_widgets()
#         unreal.log("✅ DynamicSectionB가 구성되었습니다 - 2개 항목 추가됨")
#         # build_sub_menu()  # 이 함수 호출 제거

# # 만약 MultiBoxType.MENU 인 엔트리를 만들 수 있으면?
# @unreal.uclass()
# class DynamicSubmenu(unreal.ToolMenuEntryScript):
    
#     @unreal.ufunction(override=True)
#     def can_execute(self, context):
#         return True
    
#     @unreal.ufunction(override=True)
#     def execute(self, context):
#         unreal.log(f"✅{context} DynamicSubmenu가 실행되었습니다.")

# def register():
#     """메뉴 동적 섹션 등록 함수"""
#     tool_menus = unreal.ToolMenus.get()
    
#     menu_name = unreal.Name("ContentBrowser.ItemContextMenu.PythonData") # Python 파일 컨텍스트 메뉴
#     menu = tool_menus.extend_menu(menu_name)
#     unreal.log(f"동적 섹션을 추가하기 시작하는 메뉴 이름: {menu.menu_name}")

#     owner = unreal.Name("")
#     preset_section_name = unreal.Name("StaticSection")
#     sub_menu_save_name = unreal.Name("SaveMenu")
#     sub_menu_load_name = unreal.Name("LoadMenu")
#     sub_menu_save_label = unreal.Name("저장하기")
#     sub_menu_load_label = unreal.Name("불러오기")
#     sub_menu_save = menu.add_sub_menu(owner,preset_section_name, sub_menu_save_name, sub_menu_save_label)
#     sub_menu_load = menu.add_sub_menu(owner,preset_section_name, sub_menu_load_name, sub_menu_load_label)
#     for i in range(10):      
#         save_slot_sub_menu_name = unreal.Name(f"SaveSlot{i+1}SubMenu")
#         save_owner = unreal.Name("")
#         save_section = unreal.Name("SaveSlots")
#         save_name = unreal.Name(f"Save Slot {i+1}")
#         save_label = unreal.Text(f"📁 슬롯 {i+1}")
#         save_slot = sub_menu_save.add_sub_menu(owner, save_section, save_name, save_label)
#         save_dynamic_section_name = unreal.Name("SaveDynamicSectionA")
#         save_dynamic_section = DynamicSection()
#         save_slot.add_dynamic_section(save_dynamic_section_name, save_dynamic_section)
#         load_slot_sub_menu_name = unreal.Name(f"LoadSlot{i+1}SubMenu")
#         load_owner = unreal.Name("")
#         load_section = unreal.Name("LoadSlots")
#         load_name = unreal.Name(f"Load Slot {i+1}")
#         load_label = unreal.Text(f"📁 슬롯 {i+1}")

#         load_slot = sub_menu_load.add_sub_menu(load_owner, load_section, load_name, load_label)
#         load_dynamic_section_name = unreal.Name("LoadDynamicSectionA")
#         load_dynamic_section = DynamicSection()
#         load_slot.add_dynamic_section(load_dynamic_section_name, load_dynamic_section)

#     entry1 = EntryScript()
#     entry1_owner = unreal.Name("Owner")
#     entry1_name = unreal.Name("SubMenuEntry1")
#     entry1_label = unreal.Text("SubMenuEntry1")
#     entry1.init_entry(entry1_owner,menu.menu_name,preset_section_name, entry1_name, entry1_label)
#     entry1.register_menu_entry()
#     # static_sub_menu_name = unreal.Name("StaticSubMenu")
#     # static_sub_menu = menu.add_sub_menu(
#     #     owner=menu.get_name(),
#     #     section_name=preset_section_name,
#     #     name=static_sub_menu_name,
#     #     label=unreal.Text("정적 서브 메뉴")
#     # )
#     # static_entry = unreal.ToolMenuEntry(
#     #     name=unreal.Name("StaticEntry1"),
#     #     type=unreal.MultiBlockType.MENU_ENTRY,
#     #     insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
#     #     user_interface_action_type=unreal.UserInterfaceActionType.BUTTON,
#     # )
#     # static_entry.set_label(unreal.Text("정적 엔트리 1"))
#     # static_sub_menu.add_menu_entry(preset_section_name, static_entry)

#     # unreal.ToolMenuEntryScriptDataAdvanced()
#     # - ``entry_type`` (MultiBlockType):  [Read-Write]
#     # - ``is_sub_menu`` (bool):  [Read-Write]
#     # - ``open_sub_menu_on_click`` (bool):  [Read-Write]
#     # - ``should_close_window_after_menu_selection`` (bool):  [Read-Write]
#     # - ``simple_combo_box`` (bool):  [Read-Write]
#     # - ``style_name_override`` (Name):  [Read-Write]
#     # - ``tutorial_highlight`` (Name):  [Read-Write]
#     # - ``user_interface_action_type`` (UserInterfaceActionType):  [Read-Write]
#     # sub_test_entry_name = unreal.Name("SubTestEntry")
#     # sub_test_entry = DynamicSubmenu()
#     # sub_test_entry.data = unreal.ToolMenuEntryScriptData()
#     # sub_test_entry.data.label = unreal.Text("서브 테스트 엔트리")
#     # # sub_test_entry.data.advanced = unreal.ToolMenuEntryScriptDataAdvanced()
#     # # sub_test_entry.data.advanced.entry_type = unreal.MultiBlockType.SEPARATOR
#     # sub_test_entry.data.advanced.is_sub_menu = True
#     # sub_test_entry.data.advanced.open_sub_menu_on_click = True
#     # sub_test_entry.data.advanced.should_close_window_after_menu_selection = False



#     # menu.add_menu_entry_object(sub_test_entry)


# def build_sub_menu():
#     """메뉴 동적 섹션 등록 함수"""
#     tool_menus = unreal.ToolMenus.get()

#     menu_name = unreal.Name("ContentBrowser.ItemContextMenu.PythonData") # Python 파일 컨텍스트 메뉴
#     save_menu_name = unreal.Name("ContentBrowser.ItemContextMenu.PythonData.SaveMenu") # Python 파일 컨텍스트 메뉴
#     load_menu_name = unreal.Name("ContentBrowser.ItemContextMenu.PythonData.LoadMenu") # Python 파일 컨텍스트 메뉴

#     menu = tool_menus.extend_menu(menu_name)
#     owner = unreal.Name("")
#     preset_section_name = unreal.Name("StaticSection2")
#     sub_menu_save_name = unreal.Name("SaveMenu")
#     sub_menu_load_name = unreal.Name("LoadMenu")
#     sub_menu_save_label = unreal.Name("저장하기")
#     sub_menu_load_label = unreal.Name("불러오기")
#     sub_menu_save = menu.add_sub_menu(owner,preset_section_name, save_menu_name, sub_menu_save_label)
#     sub_menu_load = menu.add_sub_menu(owner,preset_section_name, load_menu_name, sub_menu_load_label)
#     tool_menus.refresh_all_widgets()
#     # menu.add_menu_entry_object(sub_test_entry)

# if __name__ == "__main__":
#     register()