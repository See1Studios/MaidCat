"""
ToolMenus 연습용 파일 - 단계별 학습
Context를 활용한 동적 메뉴 구성 연습
"""
import unreal

# =============================================================================
# 1단계: 기본 메뉴 요소들 이해
# =============================================================================

def practice_1_basic_menu_elements():
    """1단계: 기본 메뉴 요소들과 구조 이해"""
    print("🎯 1단계: 기본 메뉴 요소들 연습")
    
    tool_menus = unreal.ToolMenus.get()
    
    # 사용 가능한 메뉴들 찾아보기
    print("\n📋 사용 가능한 주요 메뉴들:")
    important_menus = [
        "ContentBrowser.AssetContextMenu",  # 콘텐츠 브라우저 우클릭
        "LevelEditor.ActorContextMenu",     # 뷰포트 액터 우클릭
        "LevelEditor.LevelEditorToolBar",   # 메인 툴바
        "MainFrame.MainMenu",               # 메인 메뉴바
        "ContentBrowser.FolderContextMenu", # 폴더 우클릭
    ]
    
    for menu_name in important_menus:
        menu = tool_menus.find_menu(unreal.Name(menu_name))
        if menu:
            print(f"✅ {menu_name} - 발견됨")
        else:
            print(f"❌ {menu_name} - 찾을 수 없음")
    
    print("\n💡 메뉴 요소 타입들:")
    print("- MENU_ENTRY: 일반 메뉴 항목")
    print("- SEPARATOR: 구분선")
    print("- MENU_BAR: 메뉴바")
    print("- TOOLBAR_BUTTON: 툴바 버튼")

def practice_2_menu_sections():
    """2단계: 메뉴 섹션 관리 연습"""
    print("\n🎯 2단계: 메뉴 섹션 관리 연습")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    if not menu:
        print("❌ 메뉴를 찾을 수 없습니다.")
        return
    
    # 기존 섹션들 확인
    print("\n📂 기존 섹션들:")
    # Unreal에서는 섹션 목록을 직접 가져올 수 없어서 알려진 섹션들 확인
    known_sections = [
        "GetAssetActions",
        "CommonAssetActions", 
        "ExploreAssetActions",
        "AssetContextAdvancedActions",
        "MaidCat_Practice"  # 우리가 만들 섹션
    ]
    
    for section_name in known_sections:
        print(f"- {section_name}")
    
    # 연습용 섹션 추가
    practice_section = unreal.Name("MaidCat_Practice")
    menu.add_section(practice_section, unreal.Text("🧪 Practice Section"))
    
    # 기본 메뉴 엔트리 추가
    entry = unreal.ToolMenuEntry(
        name=unreal.Name("practice_basic"),
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    entry.set_label(unreal.Text("📝 Basic Practice Entry"))
    entry.set_tool_tip(unreal.Text("기본 메뉴 항목 연습"))
    entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name(""),
        string="print('🎉 Basic Entry 클릭됨!')"
    )
    
    menu.add_menu_entry(practice_section, entry)
    tool_menus.refresh_all_widgets()
    print("✅ 기본 섹션과 엔트리 추가 완료")

def practice_3_context_detection():
    """3단계: Context 감지 연습"""
    print("\n🎯 3단계: Context 감지 연습")
    
    # Context 정보를 가져오는 다양한 방법들
    print("\n📍 Context 감지 방법들:")
    
    # 1. ContentBrowser에서 선택된 애셋들
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        print(f"✅ 선택된 애셋 수: {len(selected_assets)}")
        for i, asset in enumerate(selected_assets[:3]):  # 처음 3개만
            print(f"   {i+1}. {asset.get_name()} ({asset.get_class().get_name()})")
    except Exception as e:
        print(f"❌ 선택된 애셋 가져오기 실패: {e}")
    
    # 2. 선택된 폴더들
    try:
        content_browser_selections = unreal.EditorUtilityLibrary.get_selected_folder_paths()
        print(f"✅ 선택된 폴더 수: {len(content_browser_selections)}")
        for folder in content_browser_selections:
            print(f"   📁 {folder}")
    except Exception as e:
        print(f"❌ 선택된 폴더 가져오기 실패: {e}")
    
    # 3. 현재 레벨의 선택된 액터들
    try:
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        print(f"✅ 선택된 액터 수: {len(selected_actors)}")
        for i, actor in enumerate(selected_actors[:3]):
            print(f"   {i+1}. {actor.get_name()} ({actor.get_class().get_name()})")
    except Exception as e:
        print(f"❌ 선택된 액터 가져오기 실패: {e}")

def get_context_info():
    """현재 Context 정보 반환"""
    context = {
        'selected_assets': [],
        'selected_folders': [],
        'selected_actors': [],
        'asset_types': set(),
        'has_material_instances': False,
        'has_materials': False,
        'has_textures': False,
        'has_meshes': False
    }
    
    # 선택된 애셋들 분석
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        context['selected_assets'] = selected_assets
        
        for asset in selected_assets:
            asset_class = asset.get_class().get_name()
            context['asset_types'].add(asset_class)
            
            # 특정 타입들 체크
            if asset_class == 'MaterialInstanceConstant':
                context['has_material_instances'] = True
            elif asset_class == 'Material':
                context['has_materials'] = True
            elif 'Texture' in asset_class:
                context['has_textures'] = True
            elif 'Mesh' in asset_class:
                context['has_meshes'] = True
                
    except Exception as e:
        print(f"Context 분석 오류: {e}")
    
    # 선택된 폴더들
    try:
        context['selected_folders'] = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    except:
        pass
    
    # 선택된 액터들
    try:
        context['selected_actors'] = unreal.EditorLevelLibrary.get_selected_level_actors()
    except:
        pass
    
    return context

def practice_4_dynamic_menu_creation():
    """4단계: 동적 메뉴 생성 연습"""
    print("\n🎯 4단계: 동적 메뉴 생성 연습")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    if not menu:
        print("❌ 메뉴를 찾을 수 없습니다.")
        return
    
    # 기존 동적 섹션 제거
    try:
        menu.remove_section(unreal.Name("MaidCat_Dynamic"))
    except:
        pass
    
    # Context 정보 가져오기
    context = get_context_info()
    
    # Context에 따라 동적 섹션 생성
    if context['selected_assets']:
        dynamic_section = unreal.Name("MaidCat_Dynamic")
        menu.add_section(dynamic_section, unreal.Text("🔄 Dynamic Menu"))
        
        # 기본 정보 표시 엔트리
        info_entry = unreal.ToolMenuEntry(
            name=unreal.Name("context_info"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        
        asset_count = len(context['selected_assets'])
        asset_types = ', '.join(list(context['asset_types'])[:3])
        if len(context['asset_types']) > 3:
            asset_types += "..."
            
        info_entry.set_label(unreal.Text(f"📊 {asset_count}개 선택됨"))
        info_entry.set_tool_tip(unreal.Text(f"타입: {asset_types}"))
        info_entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string=f"from tool.toolmenus_practice import show_context_details; show_context_details()"
        )
        menu.add_menu_entry(dynamic_section, info_entry)
        
        # Material Instance가 있으면 특별 메뉴 추가
        if context['has_material_instances']:
            mi_entry = unreal.ToolMenuEntry(
                name=unreal.Name("material_instance_tools"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            mi_entry.set_label(unreal.Text("🎨 Material Instance Tools"))
            mi_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string="print('🎨 Material Instance 도구들 활성화!')"
            )
            menu.add_menu_entry(dynamic_section, mi_entry)
        
        # 텍스처가 있으면 텍스처 도구 추가
        if context['has_textures']:
            texture_entry = unreal.ToolMenuEntry(
                name=unreal.Name("texture_tools"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            texture_entry.set_label(unreal.Text("🖼️ Texture Tools"))
            texture_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string="print('🖼️ 텍스처 도구들 활성화!')"
            )
            menu.add_menu_entry(dynamic_section, texture_entry)
        
        # 메시가 있으면 메시 도구 추가
        if context['has_meshes']:
            mesh_entry = unreal.ToolMenuEntry(
                name=unreal.Name("mesh_tools"),
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            mesh_entry.set_label(unreal.Text("🗿 Mesh Tools"))
            mesh_entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string="print('🗿 메시 도구들 활성화!')"
            )
            menu.add_menu_entry(dynamic_section, mesh_entry)
        
        tool_menus.refresh_all_widgets()
        print("✅ 동적 메뉴 생성 완료")
    else:
        print("⚠️ 선택된 애셋이 없어서 동적 메뉴를 생성하지 않았습니다.")

def show_context_details():
    """Context 상세 정보 표시"""
    context = get_context_info()
    
    print("\n📋 현재 Context 상세 정보:")
    print(f"선택된 애셋: {len(context['selected_assets'])}개")
    print(f"선택된 폴더: {len(context['selected_folders'])}개") 
    print(f"선택된 액터: {len(context['selected_actors'])}개")
    print(f"애셋 타입들: {list(context['asset_types'])}")
    print(f"Material Instance 포함: {context['has_material_instances']}")
    print(f"Material 포함: {context['has_materials']}")
    print(f"Texture 포함: {context['has_textures']}")
    print(f"Mesh 포함: {context['has_meshes']}")
    
    if context['selected_assets']:
        print("\n📄 선택된 애셋 목록:")
        for i, asset in enumerate(context['selected_assets'][:5]):
            print(f"  {i+1}. {asset.get_name()} ({asset.get_class().get_name()})")
        if len(context['selected_assets']) > 5:
            print(f"  ... 그외 {len(context['selected_assets']) - 5}개 더")

def practice_5_submenu_creation():
    """5단계: 서브메뉴 생성 연습"""
    print("\n🎯 5단계: 서브메뉴 생성 연습")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    if not menu:
        print("❌ 메뉴를 찾을 수 없습니다.")
        return
    
    # 기존 서브메뉴 섹션 제거
    try:
        menu.remove_section(unreal.Name("MaidCat_Submenu_Practice"))
    except:
        pass
    
    # 서브메뉴 섹션 생성
    submenu_section = unreal.Name("MaidCat_Submenu_Practice")
    menu.add_section(submenu_section, unreal.Text("🌳 Submenu Practice"))
    
    # Context 기반 서브메뉴 생성
    context = get_context_info()
    
    # 1. Asset Type별 서브메뉴
    if context['asset_types']:
        type_submenu = menu.add_sub_menu(
            owner=unreal.Name(""),
            section_name=submenu_section,
            name=unreal.Name("asset_type_submenu"),
            label=unreal.Text("📂 Asset Type Tools"),
            tool_tip=unreal.Text("선택된 애셋 타입별 도구들")
        )
        
        if type_submenu:
            type_section = unreal.Name("type_tools")
            type_submenu.add_section(type_section, unreal.Text("Asset Types"))
            
            for asset_type in list(context['asset_types'])[:5]:  # 최대 5개
                type_entry = unreal.ToolMenuEntry(
                    name=unreal.Name(f"tool_{asset_type.lower()}"),
                    type=unreal.MultiBlockType.MENU_ENTRY
                )
                type_entry.set_label(unreal.Text(f"🔧 {asset_type} Tools"))
                type_entry.set_string_command(
                    unreal.ToolMenuStringCommandType.PYTHON,
                    custom_type=unreal.Name(""),
                    string=f"print('🔧 {asset_type} 도구 실행!')"
                )
                type_submenu.add_menu_entry(type_section, type_entry)
    
    # 2. 조건부 서브메뉴들
    if context['has_material_instances'] or context['has_materials']:
        material_submenu = menu.add_sub_menu(
            owner=unreal.Name(""),
            section_name=submenu_section,
            name=unreal.Name("material_submenu"),
            label=unreal.Text("🎨 Material Operations"),
            tool_tip=unreal.Text("머티리얼 관련 작업들")
        )
        
        if material_submenu:
            mat_section = unreal.Name("material_ops")
            material_submenu.add_section(mat_section, unreal.Text("Operations"))
            
            # Material Instance 관련 메뉴
            if context['has_material_instances']:
                mi_copy = unreal.ToolMenuEntry(
                    name=unreal.Name("mi_copy_params"),
                    type=unreal.MultiBlockType.MENU_ENTRY
                )
                mi_copy.set_label(unreal.Text("📋 Copy Parameters"))
                mi_copy.set_string_command(
                    unreal.ToolMenuStringCommandType.PYTHON,
                    custom_type=unreal.Name(""),
                    string="print('📋 Material Instance 파라미터 복사!')"
                )
                material_submenu.add_menu_entry(mat_section, mi_copy)
                
                mi_preset = unreal.ToolMenuEntry(
                    name=unreal.Name("mi_save_preset"),
                    type=unreal.MultiBlockType.MENU_ENTRY
                )
                mi_preset.set_label(unreal.Text("💾 Save as Preset"))
                mi_preset.set_string_command(
                    unreal.ToolMenuStringCommandType.PYTHON,
                    custom_type=unreal.Name(""),
                    string="print('💾 Material Instance 프리셋 저장!')"
                )
                material_submenu.add_menu_entry(mat_section, mi_preset)
    
    tool_menus.refresh_all_widgets()
    print("✅ 서브메뉴 생성 완료")

def practice_6_advanced_context():
    """6단계: 고급 Context 활용 연습"""
    print("\n🎯 6단계: 고급 Context 활용 연습")
    
    context = get_context_info()
    
    # 선택된 애셋들의 상세 분석
    if context['selected_assets']:
        print("\n🔍 선택된 애셋 상세 분석:")
        
        # 패키지 경로 분석
        package_paths = {}
        for asset in context['selected_assets']:
            package_path = asset.get_path_name()
            folder = '/'.join(package_path.split('/')[:-1])
            if folder not in package_paths:
                package_paths[folder] = []
            package_paths[folder].append(asset.get_name())
        
        print(f"📁 폴더별 분포: {len(package_paths)}개 폴더")
        for folder, assets in package_paths.items():
            print(f"  {folder}: {len(assets)}개")
        
        # Material Instance 특별 분석
        if context['has_material_instances']:
            print("\n🎨 Material Instance 분석:")
            for asset in context['selected_assets']:
                if asset.get_class().get_name() == 'MaterialInstanceConstant':
                    # 부모 머티리얼 확인
                    try:
                        parent = asset.get_editor_property('parent')
                        if parent:
                            print(f"  {asset.get_name()} → {parent.get_name()}")
                        else:
                            print(f"  {asset.get_name()} → 부모 없음")
                    except:
                        print(f"  {asset.get_name()} → 부모 정보 확인 불가")

def practice_7_menu_refresh_and_cleanup():
    """7단계: 메뉴 새로고침과 정리 연습"""
    print("\n🎯 7단계: 메뉴 새로고침과 정리 연습")
    
    tool_menus = unreal.ToolMenus.get()
    menu = tool_menus.find_menu(unreal.Name("ContentBrowser.AssetContextMenu"))
    
    if not menu:
        print("❌ 메뉴를 찾을 수 없습니다.")
        return
    
    # 모든 연습용 섹션들 제거
    practice_sections = [
        "MaidCat_Practice",
        "MaidCat_Dynamic", 
        "MaidCat_Submenu_Practice"
    ]
    
    print("🧹 연습용 섹션들 정리 중...")
    for section_name in practice_sections:
        try:
            menu.remove_section(unreal.Name(section_name))
            print(f"  ✅ {section_name} 제거됨")
        except Exception as e:
            print(f"  ⚠️  {section_name} 제거 실패: {e}")
    
    # 메뉴 새로고침
    tool_menus.refresh_all_widgets()
    print("✅ 메뉴 정리 및 새로고침 완료")

# =============================================================================
# 통합 연습 함수들
# =============================================================================

def run_all_practices():
    """모든 연습 단계 실행"""
    print("🚀 ToolMenus 연습 시작!\n")
    
    practice_1_basic_menu_elements()
    practice_2_menu_sections()
    practice_3_context_detection()
    practice_4_dynamic_menu_creation()
    practice_5_submenu_creation()
    practice_6_advanced_context()
    
    print("\n🎉 모든 연습 완료!")
    print("💡 콘텐츠 브라우저에서 애셋을 선택하고 우클릭해보세요!")

def run_context_practice():
    """Context 관련 연습만 실행"""
    print("🎯 Context 연습 모드\n")
    
    practice_3_context_detection()
    practice_4_dynamic_menu_creation()
    practice_6_advanced_context()
    
    print("\n✅ Context 연습 완료!")

def cleanup_all():
    """모든 연습용 메뉴 정리"""
    practice_7_menu_refresh_and_cleanup()

# =============================================================================
# 메인 실행부
# =============================================================================

if __name__ == "__main__":
    # 기본적으로 모든 연습 실행
    run_all_practices()