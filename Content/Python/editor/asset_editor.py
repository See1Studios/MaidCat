import unreal
import tool.asset_link

# 상수 정의
OWNER_NAME = unreal.Name("MaidCat")
TOOLBAR_NAME = unreal.Name("AssetEditorToolBar.CommonActions")
CONTEXT_MENU_NAME = unreal.Name("PropertyEditor.RowContextMenu")
ASSET_MANUAL_NAME = unreal.Name("AssetManual")
CORE_STYLE_NAME = unreal.Name("CoreStyle")
ICONS_INFO_NAME = unreal.Name("Icons.Info")
EMPTY_NAME = unreal.Name("")

SECTION_TEXT = unreal.Text("MaidCat")
CONTEXT_SECTION_TEXT = unreal.Text("🐱 MaidCat")
MANUAL_LABEL_TEXT = unreal.Text("매뉴얼")
MANUAL_TOOLTIP_TEXT = unreal.Text("이 애셋에 대한 매뉴얼 열기")

# 프리셋 메뉴 관련 상수
SAVE_PRESET_NAME = unreal.Name("maidcat_save_preset")
LOAD_PRESET_NAME = unreal.Name("maidcat_load_preset")
SAVE_PRESET_LABEL = unreal.Text("💾 Save as Preset")
LOAD_PRESET_LABEL = unreal.Text("📂 Load Preset")
SAVE_PRESET_TOOLTIP = unreal.Text("현재 머티리얼 인스턴스를 프리셋으로 저장")
LOAD_PRESET_TOOLTIP = unreal.Text("저장된 프리셋 로드")

@unreal.uclass()
class AssetManualButton(unreal.ToolMenuEntryScript):
    """에셋 에디터 툴바의 매뉴얼 버튼"""
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        return True
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        tool.asset_link.handle_asset_button_click(context)


def register_manual_button():
    """공통 툴바에 매뉴얼 버튼 등록"""
    try:
        tool_menus = unreal.ToolMenus.get()
        
        toolbar = tool_menus.extend_menu(TOOLBAR_NAME)
        if not toolbar:
            return
        
        toolbar.add_section(OWNER_NAME, SECTION_TEXT)
        
        entry = AssetManualButton()
        entry.data = unreal.ToolMenuEntryScriptData()
        entry.data.icon = unreal.ScriptSlateIcon(CORE_STYLE_NAME, ICONS_INFO_NAME)
        entry.init_entry(
            OWNER_NAME,
            TOOLBAR_NAME, 
            OWNER_NAME,
            ASSET_MANUAL_NAME,
            MANUAL_LABEL_TEXT,
            MANUAL_TOOLTIP_TEXT
        )
        entry.register_menu_entry()
        tool_menus.refresh_all_widgets()
        
    except Exception as e:
        print(f"❌ 매뉴얼 버튼 등록 실패: {e}")


def register_preset_menu():
    """머티리얼 인스턴스 에디터에 프리셋 메뉴 등록"""
    try:
        tool_menus = unreal.ToolMenus.get()
        
        context_menu = tool_menus.extend_menu(CONTEXT_MENU_NAME)
        if not context_menu:
            return
        
        context_menu.add_section(OWNER_NAME, CONTEXT_SECTION_TEXT)
        
        # 저장 메뉴
        save_entry = unreal.ToolMenuEntry(
            name=SAVE_PRESET_NAME,
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        save_entry.set_label(SAVE_PRESET_LABEL)
        save_entry.set_tool_tip(SAVE_PRESET_TOOLTIP)
        save_entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=EMPTY_NAME,
            string="from tool.material_preset import save_material_instance_preset; save_material_instance_preset()"
        )
        
        # 로드 메뉴
        load_entry = unreal.ToolMenuEntry(
            name=LOAD_PRESET_NAME,
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        load_entry.set_label(LOAD_PRESET_LABEL)
        load_entry.set_tool_tip(LOAD_PRESET_TOOLTIP)
        load_entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=EMPTY_NAME,
            string="from tool.material_preset import load_material_instance_preset; load_material_instance_preset()"
        )
        
        context_menu.add_menu_entry(OWNER_NAME, save_entry)
        context_menu.add_menu_entry(OWNER_NAME, load_entry)
        tool_menus.refresh_all_widgets()
        
    except Exception as e:
        print(f"❌ 프리셋 메뉴 등록 실패: {e}")


def unregister():
    """모든 MaidCat 메뉴 항목 제거"""
    tool_menus = unreal.ToolMenus.get()
    tool_menus.unregister_owner_by_name(OWNER_NAME)
    tool_menus.refresh_all_widgets()


def register():
    """MaidCat 에디터 기능 초기화"""
    register_manual_button()
    register_preset_menu()


if __name__ == "__main__":
    register()