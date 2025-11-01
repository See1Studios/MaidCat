"""
Material Instance Context Menu

머티리얼 인스턴스에서 오른클릭 시 나타나는 컨텍스트 메뉴를 통해 
루트 프리셋과 부모 프리셋을 쉽게 관리할 수 있는 기능을 제공합니다.

컨텍스트 메뉴 기능:
- 루트 프리셋 저장/로드/삭제
- 부모 프리셋 저장/로드/삭제
- 프리셋 목록 보기
- 머티리얼 정보 표시

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
from typing import List, Optional

# 모듈 reload 및 import (개발 중 캐싱 문제 해결)
import importlib
try:
    import tool.mi_preset as mi_preset_module
    import tool.mi_serializer as mi_serializer_module
    importlib.reload(mi_preset_module)
    importlib.reload(mi_serializer_module)
    from tool.mi_preset import MaterialInstancePresetManager
    from tool.mi_serializer import MaterialInstanceSerializer
except ImportError as e:
    # 상대 경로로 다시 시도
    try:
        import mi_preset as mi_preset_module
        import mi_serializer as mi_serializer_module
        importlib.reload(mi_preset_module)
        importlib.reload(mi_serializer_module)
        from mi_preset import MaterialInstancePresetManager
        from mi_serializer import MaterialInstanceSerializer
    except ImportError:
        unreal.log_error(f"모듈 import 실패: {e}")
        raise

class MaterialInstanceContextMenu:
    """머티리얼 인스턴스 컨텍스트 메뉴 관리 클래스"""
    
    @staticmethod
    def register_context_menu():
        """컨텍스트 메뉴를 등록합니다."""
        try:
            # 툴 메뉴에 Material Instance Preset 항목 추가
            tool_menus = unreal.ToolMenus.get()
            if not tool_menus:
                unreal.log_error("❌ ToolMenus 인스턴스를 가져올 수 없습니다.")
                return False
            
            # Content Browser의 Asset Context Menu에 추가 (일반적인 Asset Context Menu 사용)
            menu_name = unreal.Name("ContentBrowser.AssetContextMenu")
            
            # 메뉴가 등록되어 있는지 확인
            if not tool_menus.is_menu_registered(menu_name):
                unreal.log_warning(f"⚠️  메뉴가 등록되지 않음: {menu_name}")
                return False
            
            menu = tool_menus.find_menu(menu_name)
            if not menu:
                unreal.log_error(f"❌ 메뉴를 찾을 수 없음: {menu_name}")
                return False
            
            # MaidCat 섹션 추가
            section_name = unreal.Name("MaidCat")
            # 섹션이 이미 있는지 확인하는 대신 바로 추가 (중복 추가는 무시됨)
            menu.add_section(section_name, unreal.Text("MaidCat"))
            
            # 루트 프리셋 서브메뉴 추가
            MaterialInstanceContextMenu._add_root_preset_menu(menu, section_name)
            
            # 부모 프리셋 서브메뉴 추가
            MaterialInstanceContextMenu._add_parent_preset_menu(menu, section_name)
            
            # 구분자 항목 추가 (separator entry)
            separator_entry = unreal.ToolMenuEntry(
                name=unreal.Name("MaidCatSeparator"),
                type=unreal.MultiBlockType.SEPARATOR
            )
            menu.add_menu_entry(section_name, separator_entry)
            
            # 머티리얼 정보 메뉴 추가
            MaterialInstanceContextMenu._add_info_menu(menu, section_name)
            
            # 메뉴 새로고침
            tool_menus.refresh_all_widgets()
            
            unreal.log("✅ Material Instance 컨텍스트 메뉴 등록 완료")
            return True
            
        except Exception as e:
            unreal.log_error(f"컨텍스트 메뉴 등록 실패: {e}")
            return False
    
    @staticmethod
    def try_register_with_delay():
        """지연된 컨텍스트 메뉴 등록 시도 (Material Instance 선택 후 사용)"""
        import unreal
        
        def delayed_register():
            success = MaterialInstanceContextMenu.register_context_menu()
            if success:
                unreal.log("✅ 지연된 컨텍스트 메뉴 등록 성공!")
            else:
                unreal.log("❌ 지연된 컨텍스트 메뉴 등록 실패")
        
        # 0.5초 후 등록 시도
        unreal.PythonBPLib.set_timer(delayed_register, 0.5, False)
    
    @staticmethod
    def _add_root_preset_menu(menu: unreal.ToolMenu, section_name: unreal.Name):
        """루트 프리셋 관련 메뉴 추가"""
        # 루트 프리셋 서브메뉴
        root_submenu = menu.add_sub_menu(
            owner=unreal.Name("MaidCat"),
            section_name=section_name,
            name=unreal.Name("RootPresets"),
            label=unreal.Text("Root Presets"),
            tool_tip=unreal.Text("루트 머티리얼 기반 프리셋 관리")
        )
        
        # 루트 프리셋 저장
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("SaveRootPreset"),
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(unreal.Name(""), unreal.ToolMenuInsertType.FIRST)
        )
        entry.set_label(unreal.Text("Save Root Preset..."))
        entry.set_tool_tip(unreal.Text("현재 머티리얼 인스턴스를 루트 프리셋으로 저장"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, 
                               custom_type=unreal.Name(""), 
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.save_root_preset_dialog()")
        root_submenu.add_menu_entry(unreal.Name("RootPresetOps"), entry)
        
        # 루트 프리셋 로드
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("LoadRootPreset"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry.set_label(unreal.Text("Load Root Preset..."))
        entry.set_tool_tip(unreal.Text("루트 프리셋을 선택하여 로드"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.load_root_preset_dialog()")
        root_submenu.add_menu_entry(unreal.Name("RootPresetOps"), entry)
        
        # 루트 프리셋 목록
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("ListRootPresets"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry.set_label(unreal.Text("List Root Presets"))
        entry.set_tool_tip(unreal.Text("사용 가능한 루트 프리셋 목록 표시"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.list_root_presets_dialog()")
        root_submenu.add_menu_entry(unreal.Name("RootPresetOps"), entry)
    
    @staticmethod
    def _add_parent_preset_menu(menu: unreal.ToolMenu, section_name: unreal.Name):
        """부모 프리셋 관련 메뉴 추가"""
        # 부모 프리셋 서브메뉴
        parent_submenu = menu.add_sub_menu(
            owner=unreal.Name("MaidCat"),
            section_name=section_name,
            name=unreal.Name("ParentPresets"),
            label=unreal.Text("Parent Presets"),
            tool_tip=unreal.Text("부모 머티리얼 기반 프리셋 관리")
        )
        
        # 부모 프리셋 저장
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("SaveParentPreset"),
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert(unreal.Name(""), unreal.ToolMenuInsertType.FIRST)
        )
        entry.set_label(unreal.Text("Save Parent Preset..."))
        entry.set_tool_tip(unreal.Text("현재 머티리얼 인스턴스를 부모 프리셋으로 저장"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.save_parent_preset_dialog()")
        parent_submenu.add_menu_entry(unreal.Name("ParentPresetOps"), entry)
        
        # 부모 프리셋 로드
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("LoadParentPreset"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry.set_label(unreal.Text("Load Parent Preset..."))
        entry.set_tool_tip(unreal.Text("부모 프리셋을 선택하여 로드"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.load_parent_preset_dialog()")
        parent_submenu.add_menu_entry(unreal.Name("ParentPresetOps"), entry)
        
        # 부모 프리셋 목록
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("ListParentPresets"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry.set_label(unreal.Text("List Parent Presets"))
        entry.set_tool_tip(unreal.Text("사용 가능한 부모 프리셋 목록 표시"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.list_parent_presets_dialog()")
        parent_submenu.add_menu_entry(unreal.Name("ParentPresetOps"), entry)
    
    @staticmethod
    def _add_info_menu(menu: unreal.ToolMenu, section_name: unreal.Name):
        """머티리얼 정보 메뉴 추가"""
        entry = unreal.ToolMenuEntry(
            name=unreal.Name("MaterialInfo"),
            type=unreal.MultiBlockType.MENU_ENTRY
        )
        entry.set_label(unreal.Text("Material Info"))
        entry.set_tool_tip(unreal.Text("선택된 머티리얼 인스턴스의 정보 표시"))
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,
                               custom_type=unreal.Name(""),
                               string="import tool.mi_context as mic; mic.MaterialInstanceContextMenu.show_material_info()")
        menu.add_menu_entry(section_name, entry)
    
    @staticmethod
    def _show_input_dialog(title: str, message: str, default_value: str = "") -> Optional[str]:
        """입력 다이얼로그 표시"""
        try:
            # EditorDialog를 사용하여 텍스트 입력 받기
            result = unreal.EditorDialog.show_message(
                title=unreal.Text(title),
                message=unreal.Text(f"{message}\n\n입력할 이름:"),
                message_type=unreal.AppMsgType.OK_CANCEL
            )
            
            if result == unreal.AppReturnType.OK:
                # 간단한 입력을 위해 기본값 사용 (실제로는 더 복잡한 UI 필요)
                return default_value if default_value else "default"
            
            return None
            
        except Exception as e:
            unreal.log_error(f"입력 다이얼로그 표시 실패: {e}")
            return None
    
    @staticmethod
    def _get_selected_material_instance() -> Optional['unreal.MaterialInstance']:
        """선택된 머티리얼 인스턴스 가져오기"""
        try:
            selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
            
            for asset in selected_assets:
                if isinstance(asset, unreal.MaterialInstance):
                    return asset
            
            unreal.log_warning("선택된 머티리얼 인스턴스가 없습니다.")
            return None
            
        except Exception as e:
            unreal.log_error(f"선택된 에셋 가져오기 실패: {e}")
            return None
    
    @staticmethod
    def _show_selection_dialog(title: str, message: str, options: List[str]) -> Optional[str]:
        """선택 다이얼로그 표시"""
        try:
            if not options:
                unreal.EditorDialog.show_message(
                    title=unreal.Text(title),
                    message=unreal.Text("사용 가능한 프리셋이 없습니다."),
                    message_type=unreal.AppMsgType.OK
                )
                return None
            
            # 옵션을 메시지에 포함
            options_text = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
            full_message = f"{message}\n\n사용 가능한 프리셋:\n{options_text}\n\n첫 번째 프리셋을 선택합니다."
            
            result = unreal.EditorDialog.show_message(
                title=unreal.Text(title),
                message=unreal.Text(full_message),
                message_type=unreal.AppMsgType.OK_CANCEL
            )
            
            if result == unreal.AppReturnType.OK and options:
                return options[0]  # 첫 번째 옵션 반환 (실제로는 더 복잡한 UI 필요)
            
            return None
            
        except Exception as e:
            unreal.log_error(f"선택 다이얼로그 표시 실패: {e}")
            return None
    
    # 루트 프리셋 관련 다이얼로그 함수들
    @staticmethod
    def save_root_preset_dialog():
        """루트 프리셋 저장 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_name = MaterialInstanceContextMenu._show_input_dialog(
                title="Save Root Preset",
                message="루트 프리셋 이름을 입력하세요:",
                default_value="new_root_preset"
            )
            
            if preset_name:
                preset_manager = MaterialInstancePresetManager()
                result = preset_manager.save_root_preset(material, preset_name)
                if result:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Success"),
                        message=unreal.Text(f"루트 프리셋 '{preset_name}' 저장 완료!\n\n저장 위치: {result}"),
                        message_type=unreal.AppMsgType.OK
                    )
                else:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Error"),
                        message=unreal.Text(f"루트 프리셋 '{preset_name}' 저장 실패!"),
                        message_type=unreal.AppMsgType.OK
                    )
        
        except Exception as e:
            unreal.log_error(f"루트 프리셋 저장 다이얼로그 오류: {e}")
    
    @staticmethod
    def load_root_preset_dialog():
        """루트 프리셋 로드 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_root_presets(material)
            
            preset_name = MaterialInstanceContextMenu._show_selection_dialog(
                title="Load Root Preset",
                message="로드할 루트 프리셋을 선택하세요:",
                options=presets
            )
            
            if preset_name:
                success = preset_manager.load_root_preset(material, preset_name)
                if success:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Success"),
                        message=unreal.Text(f"루트 프리셋 '{preset_name}' 로드 완료!"),
                        message_type=unreal.AppMsgType.OK
                    )
                else:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Error"),
                        message=unreal.Text(f"루트 프리셋 '{preset_name}' 로드 실패!"),
                        message_type=unreal.AppMsgType.OK
                    )
        
        except Exception as e:
            unreal.log_error(f"루트 프리셋 로드 다이얼로그 오류: {e}")
    
    @staticmethod
    def list_root_presets_dialog():
        """루트 프리셋 목록 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_root_presets(material)
            root_path = preset_manager._get_root_material_path(material)
            
            if presets:
                presets_text = "\n".join([f"• {preset}" for preset in presets])
                message = f"루트 머티리얼: {root_path}\n\n사용 가능한 루트 프리셋:\n{presets_text}"
            else:
                message = f"루트 머티리얼: {root_path}\n\n사용 가능한 루트 프리셋이 없습니다."
            
            unreal.EditorDialog.show_message(
                title=unreal.Text("Root Presets"),
                message=unreal.Text(message),
                message_type=unreal.AppMsgType.OK
            )
        
        except Exception as e:
            unreal.log_error(f"루트 프리셋 목록 다이얼로그 오류: {e}")
    
    # 부모 프리셋 관련 다이얼로그 함수들
    @staticmethod
    def save_parent_preset_dialog():
        """부모 프리셋 저장 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_name = MaterialInstanceContextMenu._show_input_dialog(
                title="Save Parent Preset",
                message="부모 프리셋 이름을 입력하세요:",
                default_value="new_parent_preset"
            )
            
            if preset_name:
                preset_manager = MaterialInstancePresetManager()
                result = preset_manager.save_parent_preset(material, preset_name)
                if result:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Success"),
                        message=unreal.Text(f"부모 프리셋 '{preset_name}' 저장 완료!\n\n저장 위치: {result}"),
                        message_type=unreal.AppMsgType.OK
                    )
                else:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Error"),
                        message=unreal.Text(f"부모 프리셋 '{preset_name}' 저장 실패!"),
                        message_type=unreal.AppMsgType.OK
                    )
        
        except Exception as e:
            unreal.log_error(f"부모 프리셋 저장 다이얼로그 오류: {e}")
    
    @staticmethod
    def load_parent_preset_dialog():
        """부모 프리셋 로드 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_parent_presets(material)
            
            preset_name = MaterialInstanceContextMenu._show_selection_dialog(
                title="Load Parent Preset",
                message="로드할 부모 프리셋을 선택하세요:",
                options=presets
            )
            
            if preset_name:
                success = preset_manager.load_parent_preset(material, preset_name)
                if success:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Success"),
                        message=unreal.Text(f"부모 프리셋 '{preset_name}' 로드 완료!"),
                        message_type=unreal.AppMsgType.OK
                    )
                else:
                    unreal.EditorDialog.show_message(
                        title=unreal.Text("Error"),
                        message=unreal.Text(f"부모 프리셋 '{preset_name}' 로드 실패!"),
                        message_type=unreal.AppMsgType.OK
                    )
        
        except Exception as e:
            unreal.log_error(f"부모 프리셋 로드 다이얼로그 오류: {e}")
    
    @staticmethod
    def list_parent_presets_dialog():
        """부모 프리셋 목록 다이얼로그"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            preset_manager = MaterialInstancePresetManager()
            presets = preset_manager.list_parent_presets(material)
            parent_path = preset_manager._get_parent_material_path(material)
            
            if presets:
                presets_text = "\n".join([f"• {preset}" for preset in presets])
                message = f"부모 머티리얼: {parent_path}\n\n사용 가능한 부모 프리셋:\n{presets_text}"
            else:
                message = f"부모 머티리얼: {parent_path}\n\n사용 가능한 부모 프리셋이 없습니다."
            
            unreal.EditorDialog.show_message(
                title=unreal.Text("Parent Presets"),
                message=unreal.Text(message),
                message_type=unreal.AppMsgType.OK
            )
        
        except Exception as e:
            unreal.log_error(f"부모 프리셋 목록 다이얼로그 오류: {e}")
    
    @staticmethod
    def show_material_info():
        """머티리얼 정보 표시"""
        try:
            material = MaterialInstanceContextMenu._get_selected_material_instance()
            if not material:
                return
            
            # 기본 정보
            asset_name = material.get_name()
            asset_path = material.get_path_name()
            
            # 부모/루트 머티리얼 정보
            preset_manager = MaterialInstancePresetManager()
            parent_path = preset_manager._get_parent_material_path(material)
            root_path = preset_manager._get_root_material_path(material)
            
            # 프리셋 개수
            root_presets_count = len(preset_manager.list_root_presets(material))
            parent_presets_count = len(preset_manager.list_parent_presets(material))
            
            # 정보 구성
            info_text = f"Material Instance: {asset_name}\n"
            info_text += f"Path: {asset_path}\n\n"
            info_text += f"Parent Material: {parent_path or 'None'}\n"
            info_text += f"Root Material: {root_path or 'None'}\n\n"
            info_text += f"Root Presets: {root_presets_count}개\n"
            info_text += f"Parent Presets: {parent_presets_count}개"
            
            unreal.EditorDialog.show_message(
                title=unreal.Text("Material Instance Info"),
                message=unreal.Text(info_text),
                message_type=unreal.AppMsgType.OK
            )
        
        except Exception as e:
            unreal.log_error(f"머티리얼 정보 표시 오류: {e}")


# 자동 등록
if __name__ == "__main__":
    """
    컨텍스트 메뉴 자동 등록
    """
    print("\n" + "="*80)
    print("🎛️  Material Instance Context Menu 등록")
    print("="*80)
    
    success = MaterialInstanceContextMenu.register_context_menu()
    
    if success:
        print("✅ 컨텍스트 메뉴 등록 완료!")
        print("\n💡 사용 방법:")
        print("   1. Content Browser에서 Material Instance를 선택")
        print("   2. 우클릭하여 컨텍스트 메뉴 열기")
        print("   3. 'MaidCat' 섹션에서 프리셋 관리 기능 사용")
        print("\n🎯 제공 기능:")
        print("   • Root Presets - 루트 머티리얼 기반 프리셋")
        print("   • Parent Presets - 부모 머티리얼 기반 프리셋")
        print("   • Material Info - 머티리얼 정보 표시")
    else:
        print("❌ 컨텍스트 메뉴 등록 실패!")
        print("   다음을 확인해주세요:")
        print("   • Unreal Editor에서 실행 중인지 확인")
        print("   • Play 모드가 아닌지 확인")
        print("   • Material Instance가 Content Browser에 있는지 확인")
        print("   • Material Instance를 선택한 상태에서 다시 시도")
        print("\n🔄 대안 방법:")
        print("   1. Material Instance를 Content Browser에서 선택")
        print("   2. 다음 명령어 실행:")
        print("      MaterialInstanceContextMenu.try_register_with_delay()")
    
    print("="*80 + "\n")


# 전역 편의 함수
def register_mi_context_menu():
    """전역 편의 함수 - 다른 스크립트에서 쉽게 사용할 수 있도록"""
    return MaterialInstanceContextMenu.register_context_menu()


def register_mi_context_menu_delayed():
    """지연된 등록 - Material Instance 선택 후 사용"""
    return MaterialInstanceContextMenu.try_register_with_delay()