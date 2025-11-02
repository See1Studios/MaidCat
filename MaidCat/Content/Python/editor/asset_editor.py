import unreal

# ================================
# 버튼 엔트리를 주입할 메뉴
# ================================

TARGET_MENUS = [
    # ("AssetEditor.MaterialInstanceEditor.ToolBar", "머티리얼 인스턴스 에디터"),
    # ("AssetEditor.MaterialEditor.ToolBar", "머티리얼 에디터"),
    # ("AssetEditor.StaticMeshEditor.ToolBar", "스태틱 메시 에디터"),
    # ("AssetEditor.SkeletalMeshEditor.ToolBar", "스켈레탈 메시 에디터"),
    # ("AssetEditor.TextureEditor.ToolBar", "텍스처 에디터"),
    # ("AssetEditor.BlueprintEditor.ToolBar", "블루프린트 에디터"),
    # ("AssetEditor.DataTableEditor.ToolBar", "데이터 테이블 에디터"),
    ("AssetEditorToolBar.CommonActions", "애셋 에디터 공통 툴바")
]


# ================================
# 메인 툴바 버튼 클래스
# ================================

@unreal.uclass()
class AssetManualButton(unreal.ToolMenuEntryScript):
    """에셋 에디터 툴바 버튼 클래스"""

    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """버튼 실행 가능 여부 확인"""
        return True
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """버튼 클릭 시 실행 - 다른 모듈로 위임"""
        try:
            # 실제 기능은 다른 모듈에서 구현
            from tool.asset_link import handle_asset_button_click
            handle_asset_button_click(context)
        except ImportError:
            print("❌ asset_link 모듈을 찾을 수 없습니다.")
        except Exception as e:
            print(f"❌ 버튼 실행 실패: {e}")


# ================================
# 메뉴 등록/해제 함수들
# ================================

def register_manual_button(target_menu="AssetEditor.MaterialInstanceEditor.ToolBar"):
    """에디터 툴바에 MaidCat 버튼 등록"""
    try:
        tool_menus = unreal.ToolMenus.get()
        menu_name = unreal.Name(target_menu)
        
        # 기존 버튼 제거 (재등록을 위해)
        _remove_existing_section(tool_menus, menu_name, "MaidCat")
        
        # 툴바 확장
        toolbar = tool_menus.extend_menu(menu_name)
        if not toolbar:
            print(f"❌ {target_menu} 메뉴를 찾을 수 없습니다.")
            return
        
        # MaidCat 섹션 추가
        section_name = unreal.Name("MaidCat")
        toolbar.add_section(section_name, unreal.Text("MaidCat"))
        
        # 버튼 엔트리 등록
        _register_button_entry(toolbar, section_name, target_menu)
        
        # UI 새로고침
        tool_menus.refresh_all_widgets()
        print(f"✅ {target_menu} 툴바 버튼이 등록되었습니다.")
        
    except Exception as e:
        print(f"❌ {target_menu} 툴바 버튼 등록 실패: {e}")


def _register_button_entry(toolbar, section_name, editor_toolbar_name):
    """버튼 엔트리를 툴바에 등록"""
    owner_name = unreal.Name("MaidCat")
    menu_name = unreal.Name("AssetManual")
    menu = unreal.Name(editor_toolbar_name)
    label = unreal.Text("매뉴얼")
    tool_tip = unreal.Text("이 애셋에 대한 매뉴얼 열기")
    
    entry = AssetManualButton()
    entry.data = unreal.ToolMenuEntryScriptData()
    entry.data.icon = unreal.ScriptSlateIcon("CoreStyle","Icons.Info")
    entry.init_entry(owner_name, menu, section_name, menu_name, label, tool_tip)

    entry.register_menu_entry()


def _remove_existing_section(tool_menus, menu_name, section_name):
    """기존 섹션 제거 (재등록을 위해)"""
    try:
        menu = tool_menus.find_menu(menu_name)
        if menu:
            menu.remove_section(unreal.Name(section_name))
    except:
        pass  # 기존 섹션이 없어도 문제없음


def register_preset_menu():
    """PropertyEditor 컨텍스트 메뉴에 MaidCat 메뉴 추가"""
    try:
        tool_menus = unreal.ToolMenus.get()
        menu_name = unreal.Name("PropertyEditor.RowContextMenu")
        
        # 기존 메뉴 제거
        _remove_existing_section(tool_menus, menu_name, "MaidCat")
        
        # 컨텍스트 메뉴 확장
        context_menu = tool_menus.extend_menu(menu_name)
        if not context_menu:
            print("❌ PropertyEditor 컨텍스트 메뉴를 찾을 수 없습니다.")
            return
        
        # MaidCat 섹션 및 메뉴 엔트리 추가
        section_name = unreal.Name("MaidCat")
        context_menu.add_section(section_name, unreal.Text("🐱 MaidCat"))
        
        _add_preset_menu_entries(context_menu, section_name)
        
        # UI 새로고침
        tool_menus.refresh_all_widgets()
        print("✅ MaidCat PropertyEditor 컨텍스트 메뉴가 등록되었습니다.")
        
    except Exception as e:
        print(f"❌ PropertyEditor 컨텍스트 메뉴 등록 실패: {e}")


def _add_preset_menu_entries(context_menu, section_name):
    """프리셋 메뉴 엔트리들을 컨텍스트 메뉴에 추가"""
    # 프리셋 저장 메뉴
    save_preset_entry = unreal.ToolMenuEntry(
        name=unreal.Name("maidcat_save_preset"),
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    save_preset_entry.set_label(unreal.Text("💾 Save as Preset"))
    save_preset_entry.set_tool_tip(unreal.Text("현재 머티리얼 인스턴스를 프리셋으로 저장"))
    save_preset_entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name(""),
        string="from tool.material_preset import save_material_instance_preset; save_material_instance_preset()"
    )
    
    # 프리셋 로드 메뉴
    load_preset_entry = unreal.ToolMenuEntry(
        name=unreal.Name("maidcat_load_preset"),
        type=unreal.MultiBlockType.MENU_ENTRY
    )
    load_preset_entry.set_label(unreal.Text("📂 Load Preset"))
    load_preset_entry.set_tool_tip(unreal.Text("저장된 프리셋 로드"))
    load_preset_entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        custom_type=unreal.Name(""),
        string="from tool.material_preset import load_material_instance_preset; load_material_instance_preset()"
    )
    
    # 컨텍스트 메뉴에 엔트리들 추가
    context_menu.add_menu_entry(section_name, save_preset_entry)
    context_menu.add_menu_entry(section_name, load_preset_entry)


def unregister_manual_button(editor_toolbar_name="AssetEditor.MaterialInstanceEditor.ToolBar", editor_display_name="머티리얼 인스턴스 에디터"):
    """에디터 툴바 버튼 제거"""
    try:
        tool_menus = unreal.ToolMenus.get()
        menu_name = unreal.Name(editor_toolbar_name)
        _remove_existing_section(tool_menus, menu_name, "MaidCat")
        tool_menus.refresh_all_widgets()
        print(f"✅ {editor_display_name} MaidCat 툴바 버튼이 제거되었습니다.")
    except Exception as e:
        print(f"❌ {editor_display_name} 툴바 버튼 제거 실패: {e}")


def unregister_preset_menu():
    """PropertyEditor 컨텍스트 메뉴 제거"""
    try:
        tool_menus = unreal.ToolMenus.get()
        menu_name = unreal.Name("PropertyEditor.RowContextMenu")
        _remove_existing_section(tool_menus, menu_name, "MaidCat")
        tool_menus.refresh_all_widgets()
        print("✅ MaidCat PropertyEditor 컨텍스트 메뉴가 제거되었습니다.")
    except Exception as e:
        print(f"❌ PropertyEditor 컨텍스트 메뉴 제거 실패: {e}")


def register_multiple_editors():
    """여러 에디터에 MaidCat 버튼 등록"""
    print("🚀 여러 에디터에 MaidCat 버튼 등록 중...")
    
    success_count = 0
    for toolbar_name, display_name in TARGET_MENUS:
        try:
            register_manual_button(toolbar_name)
            success_count += 1
        except Exception as e:
            print(f"⚠️ {toolbar_name} 등록 실패: {e}")

    print(f"📊 등록 완료: {success_count}/{len(TARGET_MENUS)}개 에디터")


def unregister_multiple_editors():
    """여러 에디터에서 MaidCat 버튼 제거"""
    print("🧹 여러 에디터에서 MaidCat 버튼 제거 중...")
    
    success_count = 0
    for toolbar_name, display_name in TARGET_MENUS:
        try:
            unregister_manual_button(toolbar_name, display_name)
            success_count += 1
        except Exception as e:
            print(f"⚠️ {display_name} 제거 실패: {e}")
    
    print(f"📊 제거 완료: {success_count}/{len(TARGET_MENUS)}개 에디터")


def unregister_all():
    unregister_multiple_editors()
    unregister_preset_menu()


def initialize():
    register_multiple_editors()
    register_preset_menu()

if __name__ == "__main__":
    initialize()