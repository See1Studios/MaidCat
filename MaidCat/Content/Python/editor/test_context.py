import unreal

# 예시: 생성할 계층적 메뉴 구조를 정의하는 데이터
HIERARCHICAL_DATA = {
    "Rendering": {
        "Lighting": ["Check Lighting", "Optimize Lighting"],
        "Materials": {
            "Utilities": ["Material Converter", "Texture Optimizer"],
            "Reports": ["List Unused Materials"]
        }
    },
    "Asset Management": {
        "Validation": ["Validate All Assets"],
        "Cleanup": ["Clean Unused Assets", "Fix Broken References"]
    },
    "Quick Actions": ["Quick Build", "Refresh Content Browser"]
}

@unreal.uclass()
class HierarchicalMenuGenerator(unreal.ToolMenuSectionDynamic):

    def populate_menu_recursively(self, parent_menu, data, owner_name, section_name, parent_path, depth=0):
        """
        데이터를 재귀적으로 순회하며 하위 메뉴와 메뉴 항목을 생성합니다.
        """
        indent = "  " * depth
        unreal.log(f"{indent}populate_menu_recursively called - depth: {depth}, parent_path: '{parent_path}'")
        unreal.log(f"{indent}parent_menu: {parent_menu.get_name() if parent_menu else 'None'}")
        
        for name, content in data.items():
            # 메뉴 이름을 간단하고 깔끔하게 생성
            clean_name = name.replace(' ', '').replace('-', '').replace('_', '')
            current_path = f"DynamicTools.{clean_name}" if not parent_path else f"{parent_path}.{clean_name}"
            
            unreal.log(f"{indent}Processing: {name} -> {current_path}")

            if isinstance(content, dict):
                # 값이 딕셔너리이면, 새로운 하위 메뉴를 생성하고 재귀 호출
                unreal.log(f"{indent}Creating submenu: {name} with path: {current_path}")
                
                sub_menu = parent_menu.add_sub_menu(
                    owner=owner_name,
                    section_name=section_name,
                    name=unreal.Name(current_path),
                    label=unreal.Text(name),
                    tool_tip=unreal.Text(f"Options related to {name}")
                )
                
                unreal.log(f"{indent}Submenu created: {sub_menu.get_name() if sub_menu else 'None'}")
                unreal.log(f"{indent}Submenu type: {type(sub_menu)}")
                
                # 서브메뉴가 실제로 메뉴 시스템에 등록되었는지 확인
                menu_system = unreal.ToolMenus.get()
                registered_menu = menu_system.find_menu(sub_menu.get_name())
                unreal.log(f"{indent}Registered submenu found: {registered_menu is not None}")
                
                # 재귀적으로 하위 메뉴를 채웁니다.
                if sub_menu:
                    self.populate_menu_recursively(sub_menu, content, owner_name, unreal.Name(""), current_path, depth + 1)

            elif isinstance(content, list):
                # 값이 리스트이면, 메뉴 항목들을 생성
                unreal.log(f"{indent}Creating menu items for: {name}, count: {len(content)}")
                for i, item_label in enumerate(content):
                    clean_item_name = item_label.replace(' ', '').replace('-', '').replace('_', '')
                    entry_name = f"{current_path}.{clean_item_name}"
                    
                    unreal.log(f"{indent}  Creating item: {item_label} -> {entry_name}")
                    
                    entry = unreal.ToolMenuEntry(
                        name=unreal.Name(entry_name),
                        type=unreal.MultiBlockType.MENU_ENTRY
                    )
                    entry.set_label(unreal.Text(item_label))
                    
                    # 간단한 예제를 위해 실행 시 로그를 출력하는 command string 사용
                    entry.set_string_command(
                        unreal.ToolMenuStringCommandType.PYTHON,
                        custom_type=unreal.Name(''),
                        string=f'unreal.log("✅ Executed: {item_label}")'
                    )
                    parent_menu.add_menu_entry(section_name, entry)
            
            else:
                # 값이 문자열이거나 다른 타입이면 단일 메뉴 항목 생성
                entry_name = f"{current_path}.Action"
                unreal.log(f"{indent}Creating single item: {name} -> {entry_name}")
                
                entry = unreal.ToolMenuEntry(
                    name=unreal.Name(entry_name),
                    type=unreal.MultiBlockType.MENU_ENTRY
                )
                entry.set_label(unreal.Text(name))
                entry.set_string_command(
                    unreal.ToolMenuStringCommandType.PYTHON,
                    custom_type=unreal.Name(''),
                    string=f'unreal.log("✅ Executed: {name}")'
                )
                parent_menu.add_menu_entry(section_name, entry)

    @unreal.ufunction(override=True)
    def construct_sections(self, menu, context):
        # 동적 섹션에서는 find_section을 사용하지 않고 직접 메뉴를 구성합니다.
        section_name = unreal.Name("MyHierarchicalDynamicSection")
        
        # 동적 섹션이 실행될 때마다 메뉴를 구성합니다.
        # 재귀적 메뉴 생성을 시작합니다.
        self.populate_menu_recursively(
            parent_menu=menu,
            data=HIERARCHICAL_DATA,
            owner_name=menu.get_name(),
            section_name=section_name,
            parent_path=""  # 빈 문자열로 시작하여 깔끔한 경로 생성
        )

def register_hierarchical_dynamic_menu():
    """메인 메뉴에 계층적 동적 메뉴를 등록하는 함수"""
    menus = unreal.ToolMenus.get()

    # 1. 레벨 에디터의 메인 메뉴를 찾습니다.
    main_menu = menus.find_menu(unreal.Name("LevelEditor.MainMenu"))
    if not main_menu:
        return

    # 2. "Dynamic Tools" 라는 새로운 최상위 메뉴를 추가합니다.
    tools_menu = main_menu.add_sub_menu(
        owner=main_menu.get_name(),
        section_name=unreal.Name("Tools"), # 'Window' 메뉴 옆에 위치
        name=unreal.Name("MyDynamicToolsMenu"),
        label=unreal.Text("Dynamic Tools")
    )

    # 3. 이 메뉴 안에 동적 섹션을 추가할 준비를 합니다.
    #    add_dynamic_section이 호출될 때 이 섹션이 생성됩니다.
    section_name = unreal.Name("MyHierarchicalDynamicSection")
    tools_menu.add_section(section_name, unreal.Text("Tools"))

    # 4. 동적 섹션 생성자 클래스의 인스턴스를 생성하고 등록합니다.
    generator = HierarchicalMenuGenerator()
    tools_menu.add_dynamic_section(section_name, generator)

    # 5. UI를 새로고침하여 변경 사항을 적용합니다.
    menus.refresh_all_widgets()


if __name__ == "__main__":
    # 에디터 시작 시 등록 함수 호출
    register_hierarchical_dynamic_menu()