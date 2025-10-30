import unreal
import functools # 델리게이트에 인자를 전달하기 위해 사용

# 0. 가상의 데이터 소스
DYNAMIC_DATA = {
    "Props": ["Chair", "Table", "Lamp"],
    "Environment": ["Tree", "Rock"],
    "FX": ["Fire", "Smoke", "Water"],
    "EmptyCategory": []
}

# 3단계: 서브메뉴의 내용을 실제로 채우는 함수 (가장 안쪽)
# 이 함수는 사용자가 "Props" 같은 서브메뉴에 마우스를 올릴 때 호출됩니다.
def populate_submenu(section, category_name, items):
    """
    category_name과 items 목록을 기반으로 
    'section' (서브메뉴의 섹션)을 채웁니다.
    """
    print(f"Dynamically populating submenu for: {category_name}")

    if not items:
        entry = unreal.ToolMenuEntry(
            name="empty_item",
            type=unreal.ToolMenuEntryType.NONE, # 클릭 불가
            label=unreal.Text("(No items)")
        )
        section.add_entry(entry)
        return

    for item_name in items:
        entry = unreal.ToolMenuEntry(
            name=f"item_{category_name}_{item_name}",
            type=unreal.ToolMenuEntryType.MENU_ENTRY,
            label=unreal.Text(item_name)
        )
        
        # 클릭 시 실행할 Python 스크립트
        py_command = f"print('Selected Item: {item_name} (Category: {category_name})')"
        entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON, 
            string=py_command
        )
        section.add_entry(entry)

# 2단계: 최상위 동적 섹션을 채우는 함수
# 이 함수는 사용자가 우클릭 메뉴를 열 때 호출됩니다.
def populate_top_level_section(section):
    """
    'section' (최상위 섹션)에 카테고리별 서브메뉴를 추가합니다.
    """
    print("Dynamically populating top-level section (Categories)...")

    for category_name, items in DYNAMIC_DATA.items():
        
        # 1. '서브메뉴' 엔트리를 추가합니다. (예: "Props", "Environment")
        submenu_entry = section.add_sub_menu(
            owner=section.section_name,
            name=f"submenu_{category_name}",
            label=unreal.Text(category_name),
            tool_tip=unreal.Text(f"Items in {category_name}")
        )

        # 2. [핵심] 이 서브메뉴의 내용을 채울 '동적 섹션 객체'를 또 만듭니다.
        submenu_dyn_section = unreal.ToolMenuDynamicSectionScript(
            name=f"dynamic_section_for_{category_name}"
        )

        # 3. 델리게이트에 3단계 함수(populate_submenu)를 바인딩합니다.
        #    on_generate_section 델리게이트는 'section'만 인자로 받으므로,
        #    'category_name'과 'items'를 함께 넘기기 위해 functools.partial을 사용합니다.
        submenu_populator = functools.partial(
            populate_submenu, 
            category_name=category_name, 
            items=items
        )
        submenu_dyn_section.on_generate_section.set_function(submenu_populator)

        # 4. 생성된 서브메뉴 엔트리(submenu_entry)에 이 동적 섹션 객체를 추가합니다.
        submenu_entry.add_section_object(submenu_dyn_section)

# 1단계: 메뉴 등록을 시작하는 메인 함수
def register_dynamic_nested_menu():
    tool_menus = unreal.ToolMenus.get()
    
    # 콘텐츠 브라우저 애셋 우클릭 메뉴
    menu_name = "ContentBrowser.AssetContextMenu"
    menu = tool_menus.find_menu(menu_name)
    if not menu:
        print(f"Failed to find menu: {menu_name}")
        return

    # 1. '최상위' 동적 섹션 객체를 생성합니다.
    top_level_dyn_section = unreal.ToolMenuDynamicSectionScript(
        name="MyPythonTopLevelDynamicSection"
    )

    # 2. 2단계 함수(populate_top_level_section)를 바인딩합니다.
    top_level_dyn_section.on_generate_section.set_function(populate_top_level_section)

    # 3. 'ContentBrowser.AssetContextMenu'에 이 객체를 추가합니다.
    menu.add_section_object(top_level_dyn_section)
    
    # 4. 메뉴 UI 새로고침
    tool_menus.refresh_all_widgets()
    print("Registered dynamic nested menu (Python).")

# --- 스크립트 실행 ---
register_dynamic_nested_menu()