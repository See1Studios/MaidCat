import unreal

# Tkinter 텍스트 입력 함수
def get_text_input(title="Input", prompt="Enter text:", default_value=""):
    """Tkinter를 사용한 텍스트 입력 다이얼로그"""
    try:
        import tkinter as tk
        from tkinter import simpledialog
        
        # 루트 윈도우 생성 (숨김)
        root = tk.Tk()
        root.withdraw()  # 메인 창 숨기기
        root.lift()      # 다이얼로그를 맨 앞으로
        root.attributes('-topmost', True)  # 항상 위에 표시
        
        # 텍스트 입력 다이얼로그 표시
        result = simpledialog.askstring(
            title, 
            prompt, 
            initialvalue=default_value
        )
        
        root.destroy()  # 루트 윈도우 정리
        return result
        
    except ImportError:
        print("❌ Tkinter를 사용할 수 없습니다. 기본 이름을 사용합니다.")
        return default_value
    except Exception as e:
        print(f"❌ 텍스트 입력 다이얼로그 오류: {e}")
        return default_value

# === 메뉴 액션 함수들 ===

def action_save_root_preset():
    """Root 프리셋 저장 액션"""
    try:
        from tool.mi_context import MaterialInstanceContextMenu
        from tool.mi_preset import MaterialInstancePresetManager
        
        material = MaterialInstanceContextMenu._get_selected_material_instance()
        if material:
            preset_name = get_text_input(
                title="Save Root Preset",
                prompt="Root 프리셋 이름을 입력하세요:",
                default_value="NewRootPreset"
            )
            
            if preset_name and preset_name.strip():
                preset_manager = MaterialInstancePresetManager()
                success = preset_manager.save_root_preset(material, preset_name.strip())
                if success:
                    print(f'✅ Root 프리셋 저장됨: {preset_name}')
                    print(f'📁 경로: {material.get_name()} → Root Presets → {preset_name}')
                else:
                    print(f'❌ Root 프리셋 저장 실패: {preset_name}')
            else:
                print('❌ 저장 취소됨 (빈 이름)')
        else:
            print('❌ Material Instance를 먼저 선택해주세요.')
    except Exception as e:
        print(f'❌ Error saving root preset: {e}')
        import traceback
        traceback.print_exc()

def action_save_parent_preset():
    """Parent 프리셋 저장 액션"""
    try:
        from tool.mi_context import MaterialInstanceContextMenu
        from tool.mi_preset import MaterialInstancePresetManager
        
        material = MaterialInstanceContextMenu._get_selected_material_instance()
        if material:
            preset_name = get_text_input(
                title="Save Parent Preset",
                prompt="Parent 프리셋 이름을 입력하세요:",
                default_value="NewParentPreset"
            )
            
            if preset_name and preset_name.strip():
                preset_manager = MaterialInstancePresetManager()
                success = preset_manager.save_parent_preset(material, preset_name.strip())
                if success:
                    print(f'✅ Parent 프리셋 저장됨: {preset_name}')
                    print(f'📁 경로: {material.get_name()} → Parent Presets → {preset_name}')
                else:
                    print(f'❌ Parent 프리셋 저장 실패: {preset_name}')
            else:
                print('❌ 저장 취소됨 (빈 이름)')
        else:
            print('❌ Material Instance를 먼저 선택해주세요.')
    except Exception as e:
        print(f'❌ Error saving parent preset: {e}')
        import traceback
        traceback.print_exc()

def action_load_root_preset():
    """Root 프리셋 로드 액션"""
    try:
        from tool.mi_context import MaterialInstanceContextMenu
        from tool.mi_preset import MaterialInstancePresetManager
        
        material = MaterialInstanceContextMenu._get_selected_material_instance()
        if material:
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_root_presets(material)
            
            if presets:
                print(f'\n=== 사용 가능한 Root Presets ===')
                for i, preset in enumerate(presets, 1):
                    print(f'{i}. {preset}')
                
                selected_preset = get_text_input(
                    title="Load Root Preset",
                    prompt="로드할 Root 프리셋 이름을 입력하세요:",
                    default_value=presets[0] if presets else ""
                )
                
                if selected_preset and selected_preset in presets:
                    print(f'🎯 Root 프리셋 "{selected_preset}" 로딩 중...')
                    success = preset_manager.load_root_preset(material, selected_preset)
                    if success:
                        print(f'✅ 프리셋 "{selected_preset}" 로드 완료!')
                        unreal.EditorAssetLibrary.save_asset(material.get_path_name())
                    else:
                        print(f'❌ 프리셋 "{selected_preset}" 로드 실패')
                elif selected_preset:
                    print(f'❌ 프리셋 "{selected_preset}"을 찾을 수 없습니다.')
                    print(f'사용 가능한 프리셋: {", ".join(presets)}')
            else:
                print('⚠️  저장된 Root 프리셋이 없습니다.')
                print('💡 먼저 "💾 Save Root Preset" 메뉴를 사용해서 프리셋을 저장해주세요.')
        else:
            print('❌ Material Instance를 먼저 선택해주세요.')
    except Exception as e:
        print(f'❌ Error loading root presets: {e}')
        import traceback
        traceback.print_exc()

def action_load_parent_preset():
    """Parent 프리셋 로드 액션"""
    try:
        from tool.mi_context import MaterialInstanceContextMenu
        from tool.mi_preset import MaterialInstancePresetManager
        
        material = MaterialInstanceContextMenu._get_selected_material_instance()
        if material:
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_parent_presets(material)
            
            if presets:
                print(f'\n=== 사용 가능한 Parent Presets ===')
                for i, preset in enumerate(presets, 1):
                    print(f'{i}. {preset}')
                
                selected_preset = get_text_input(
                    title="Load Parent Preset",
                    prompt="로드할 Parent 프리셋 이름을 입력하세요:",
                    default_value=presets[0] if presets else ""
                )
                
                if selected_preset and selected_preset in presets:
                    print(f'🎯 Parent 프리셋 "{selected_preset}" 로딩 중...')
                    success = preset_manager.load_parent_preset(material, selected_preset)
                    if success:
                        print(f'✅ 프리셋 "{selected_preset}" 로드 완료!')
                        unreal.EditorAssetLibrary.save_asset(material.get_path_name())
                    else:
                        print(f'❌ 프리셋 "{selected_preset}" 로드 실패')
                elif selected_preset:
                    print(f'❌ 프리셋 "{selected_preset}"을 찾을 수 없습니다.')
                    print(f'사용 가능한 프리셋: {", ".join(presets)}')
            else:
                print('⚠️  저장된 Parent 프리셋이 없습니다.')
                print('💡 먼저 "💾 Save Parent Preset" 메뉴를 사용해서 프리셋을 저장해주세요.')
        else:
            print('❌ Material Instance를 먼저 선택해주세요.')
    except Exception as e:
        print(f'❌ Error loading parent presets: {e}')
        import traceback
        traceback.print_exc()

def action_list_all_presets():
    """모든 프리셋 목록 보기 액션"""
    try:
        from tool.mi_context import MaterialInstanceContextMenu
        from tool.mi_preset import MaterialInstancePresetManager
        
        material = MaterialInstanceContextMenu._get_selected_material_instance()
        if material:
            preset_manager = MaterialInstancePresetManager()
            
            print(f'\n=== {material.get_name()}의 모든 프리셋 ===')
            
            root_presets = preset_manager.list_root_presets(material)
            parent_presets = preset_manager.list_parent_presets(material)
            
            print(f'📁 Root Presets ({len(root_presets)}개):')
            for i, preset in enumerate(root_presets, 1):
                print(f'   {i}. {preset}')
            
            print(f'👨‍👩‍👧‍👦 Parent Presets ({len(parent_presets)}개):')
            for i, preset in enumerate(parent_presets, 1):
                print(f'   {i}. {preset}')
            
            if not root_presets and not parent_presets:
                print('⚠️  저장된 프리셋이 없습니다.')
                print('💡 "💾 Save Root Preset" 또는 "💾 Save Parent Preset"을 사용해서 프리셋을 저장해보세요.')
        else:
            print('❌ Material Instance를 먼저 선택해주세요.')
    except Exception as e:
        print(f'❌ Error listing presets: {e}')
        import traceback
        traceback.print_exc()

# === 메뉴 등록 함수 ===

def register_material_preset_menu():
    """Material Instance 프리셋 메뉴 등록 (서브메뉴 방식)"""
    print("🚀 Material Preset 메뉴 등록 시작")
    
    tool_menus = unreal.ToolMenus.get()
    
    # 콘텐츠 브라우저 애셋 우클릭 메뉴 찾기
    menu_name = unreal.Name("ContentBrowser.AssetContextMenu")
    menu = tool_menus.find_menu(menu_name)
    if not menu:
        print(f"❌ Failed to find menu: {menu_name}")
        return
    
    print(f"✅ 메뉴 찾음: {menu_name}")
    
    # 기존 MaidCat 섹션들 제거 (새로 만들기 위해)
    try:
        menu.remove_section(unreal.Name("MaidCat"))
        menu.remove_section(unreal.Name("MaidCat_Flat"))
        menu.remove_section(unreal.Name("MaidCat_Submenu"))
        print("🧹 기존 섹션들 정리됨")
    except:
        pass
    
    # 새로운 MaidCat 섹션 추가
    main_section = unreal.Name("MaidCat_MaterialPresets")
    menu.add_section(main_section, unreal.Text("🐱 MaidCat Material Presets"))
    print(f"✅ 메인 섹션 '{main_section}' 추가됨")
    
    # === 💾 SAVE PRESETS 서브메뉴 ===
    save_submenu = menu.add_sub_menu(
        owner=unreal.Name(""),
        section_name=main_section,
        name=unreal.Name("maidcat_save"),
        label=unreal.Text("💾 Save Presets"),
        tool_tip=unreal.Text("Save Material Instance as preset")
    )
    
    if save_submenu:
        save_section = unreal.Name("save_options")
        save_submenu.add_section(save_section, unreal.Text("Save Options"))
        
        # Save Root Preset
        save_root = unreal.ToolMenuEntry(
            name=unreal.Name("save_root"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        save_root.set_label(unreal.Text("📁 Save as Root Preset"))
        save_root.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from tool.toolmenus_clean import action_save_root_preset; action_save_root_preset()"
        )
        save_submenu.add_menu_entry(save_section, save_root)
        
        # Save Parent Preset
        save_parent = unreal.ToolMenuEntry(
            name=unreal.Name("save_parent"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        save_parent.set_label(unreal.Text("👨‍👩‍👧‍👦 Save as Parent Preset"))
        save_parent.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from tool.toolmenus_clean import action_save_parent_preset; action_save_parent_preset()"
        )
        save_submenu.add_menu_entry(save_section, save_parent)
        print("✅ Save 서브메뉴 생성됨")
    
    # === 📂 LOAD PRESETS 서브메뉴 ===
    load_submenu = menu.add_sub_menu(
        owner=unreal.Name(""),
        section_name=main_section,
        name=unreal.Name("maidcat_load"),
        label=unreal.Text("📂 Load Presets"),
        tool_tip=unreal.Text("Load saved Material Instance presets")
    )
    
    if load_submenu:
        load_section = unreal.Name("load_options")
        load_submenu.add_section(load_section, unreal.Text("Load Options"))
        
        # Load Root Preset
        load_root = unreal.ToolMenuEntry(
            name=unreal.Name("load_root"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        load_root.set_label(unreal.Text("📁 Load Root Preset"))
        load_root.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from tool.toolmenus_clean import action_load_root_preset; action_load_root_preset()"
        )
        load_submenu.add_menu_entry(load_section, load_root)
        
        # Load Parent Preset
        load_parent = unreal.ToolMenuEntry(
            name=unreal.Name("load_parent"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        load_parent.set_label(unreal.Text("👨‍👩‍👧‍👦 Load Parent Preset"))
        load_parent.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from tool.toolmenus_clean import action_load_parent_preset; action_load_parent_preset()"
        )
        load_submenu.add_menu_entry(load_section, load_parent)
        
        # 구분자
        separator = unreal.ToolMenuEntry(
            name=unreal.Name("load_separator"),
            type=unreal.MultiBlockType.SEPARATOR
        )
        load_submenu.add_menu_entry(load_section, separator)
        
        # List All Presets
        list_all = unreal.ToolMenuEntry(
            name=unreal.Name("list_all"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        list_all.set_label(unreal.Text("📋 List All Presets"))
        list_all.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from tool.toolmenus_clean import action_list_all_presets; action_list_all_presets()"
        )
        load_submenu.add_menu_entry(load_section, list_all)
        print("✅ Load 서브메뉴 생성됨")
    
    # 메뉴 새로고침
    tool_menus.refresh_all_widgets()
    
    print("🎉 Material Preset 메뉴 등록 완료!")
    print("📂 콘텐츠 브라우저에서 Material Instance 우클릭 → '🐱 MaidCat Material Presets'")

# === 테스트 함수 ===

def test_preset_functions():
    """프리셋 함수들 개별 테스트"""
    print("🧪 프리셋 함수 테스트 시작")
    
    # Tkinter 테스트
    print("\n1. Tkinter 입력 테스트:")
    result = get_text_input("테스트", "테스트 텍스트를 입력하세요:", "TestValue")
    print(f"입력 결과: {result}")
    
    # 프리셋 목록 테스트
    print("\n2. 프리셋 목록 테스트:")
    action_list_all_presets()
    
    print("\n🧪 테스트 완료")

if __name__ == "__main__":
    # 스크립트가 직접 실행될 때 메뉴 등록
    register_material_preset_menu()