import unreal

# ToolMenus 싱글턴 가져오기
tool_menus = unreal.ToolMenus.get()
# 새로운 메뉴 생성하거나 확장할 메뉴 얻어오기
menu_name = unreal.Name("ContentBrowser.ItemContextMenu.PythonData") # Python 파일 컨텍스트 메뉴
# 메뉴 등록.
tool_menus.register_menu(menu_name)
# 메뉴 찾기. 이걸로 추가하면 메뉴가 덮어써지는 듯.
tool_menus.find_menu(menu_name)
# 메뉴 확장. 찾기와 미묘하게 다름...기존 메뉴에 변동이 없음.
menu = tool_menus.extend_menu(menu_name)
# 기존에 존재하는 섹션 이름 
section_name = unreal.Name("PythonScript")
# 새로운 섹션을 추가하겠다면
section_name = unreal.Name("NewSection")
label = unreal.Text("새로운 섹션")
insert_name = section_name
insert_type = unreal.ToolMenuInsertType.FIRST
menu.add_section(section_name, label, insert_name, insert_type)
# 서브메뉴 추가
functions_submenu = menu.add_sub_menu(
    owner=menu_name,
    section_name=section_name,
    name=unreal.Name("NewSubMenu"),
    label=unreal.Text("새로운 서브 메뉴"),
    tool_tip=unreal.Text("섹션을 추가하고 엔트리를 추가합니다")
)
# 이후 메뉴에 다양한 요소들 추가
# functions_submenu.add_dynamic_section(...)
# functions_submenu.add_menu_entry(...)
# functions_submenu.add_menu_entry_object(...)
# functions_submenu.add_section(...)
# functions_submenu.add_sub_menu(...)
