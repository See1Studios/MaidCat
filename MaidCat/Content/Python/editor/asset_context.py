"""
Asset Context Menu Handler
애셋 컨텍스트 메뉴 관련 기능 모듈
- Asset Copier 도구
- Reference Replacer 도구
"""

import importlib
import sys
import unreal


@unreal.uclass()
class RunAssetCopier(unreal.ToolMenuEntryScript):
    """선택된 애셋들에 대해 copier.py 실행"""
    
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """애셋이 선택된 경우에만 활성화"""
        try:
            # 애셋 컨텍스트 메뉴인지 확인
            asset_menu_class = unreal.load_class(None, '/Script/ContentBrowserData.ContentBrowserDataMenuContext_FileMenu')
            menu_context = context.find_by_class(asset_menu_class)
            if menu_context:
                selected_items = menu_context.selected_items
                return len(selected_items) > 0
            return False
        except:
            return False
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """copier.py 실행"""
        try:
            unreal.log("🔧 고오급 복사 도구 실행...")
            
            # copier 모듈 동적 import 및 실행
            # tool.copier 모듈 리로드 (최신 코드 반영)
            if 'tool.copier' in sys.modules:
                importlib.reload(sys.modules['tool.copier'])
            
            # copier 함수 실행
            from tool import copier
            copier.run()
            
        except Exception as e:
            unreal.log_error(f"❌ 고오급 복사 실행 중 오류: {e}")
            # 폴백: 직접 선택된 애셋 정보 출력
            try:
                selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
                if selected_assets:
                    unreal.log("=" * 60)
                    unreal.log(f"📋 선택된 애셋 ({len(selected_assets)}개):")
                    for i, asset in enumerate(selected_assets, 1):
                        unreal.log(f"{i}. {asset.get_name()} ({asset.get_class().get_name()})")
                    unreal.log("=" * 60)
            except:
                pass


@unreal.uclass()
class RunReferenceReplacer(unreal.ToolMenuEntryScript):
    """선택된 애셋들에 대해 replacer.py 실행"""
    
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """애셋이 선택된 경우에만 활성화"""
        try:
            # 애셋 컨텍스트 메뉴인지 확인
            asset_menu_class = unreal.load_class(None, '/Script/ContentBrowserData.ContentBrowserData MenuContext_FileMenu')
            menu_context = context.find_by_class(asset_menu_class)
            if menu_context:
                selected_items = menu_context.selected_items
                return len(selected_items) > 0
            return False
        except:
            return False
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """replacer.py 실행"""
        try:
            unreal.log("🔄 레퍼런스 교체 도구 실행...")
            
            # replacer 모듈 동적 import 및 실행
            # tool.replacer 모듈 리로드 (최신 코드 반영)
            if 'tool.replacer' in sys.modules:
                importlib.reload(sys.modules['tool.replacer'])
            
            # replacer 함수 실행
            from tool import replacer
            replacer.run()
            
        except Exception as e:
            unreal.log_error(f"❌ 레퍼런스 교체 도구 실행 중 오류: {e}")
            # 폴백: 직접 선택된 애셋 정보 출력
            try:
                selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
                if selected_assets:
                    unreal.log("=" * 60)
                    unreal.log(f"📋 선택된 애셋 ({len(selected_assets)}개):")
                    for i, asset in enumerate(selected_assets, 1):
                        unreal.log(f"{i}. {asset.get_name()} ({asset.get_class().get_name()})")
                    unreal.log("=" * 60)
            except:
                pass


def setup_asset_copier_menu():
    """애셋 컨텍스트 메뉴에 copier 도구 추가"""
    tool_menus = unreal.ToolMenus.get()
    menu_owner = "assetCopierMenu"
    
    # 애셋 컨텍스트 메뉴에 추가
    asset_menu_names = [
        "ContentBrowser.AssetContextMenu",
        "ContentBrowser.AssetViewContextMenu",
    ]
    
    for menu_name in asset_menu_names:
        try:
            menu = tool_menus.extend_menu(menu_name)
            menu_suffix = menu_name.split('.')[-1]
            copier_section = f"CopierSection_{menu_suffix}"
            
            copier_entry = RunAssetCopier()
            copier_entry.init_entry(
                menu_owner,
                f"runAssetCopier_{menu_suffix}",
                copier_section,
                "Asset Copier",
                "Run Asset Copier Tool"
            )
            
            menu.add_section(copier_section, "Tools")
            menu.add_menu_entry_object(copier_entry)
            
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to add copier menu to {menu_name}: {e}")
    
    tool_menus.refresh_all_widgets()
    unreal.log("✅ Asset copier menu initialized")


def setup_reference_replacer_menu():
    """애셋 컨텍스트 메뉴에 reference replacer 도구 추가"""
    tool_menus = unreal.ToolMenus.get()
    menu_owner = "referenceReplacerMenu"
    
    # 애셋 컨텍스트 메뉴에 추가
    asset_menu_names = [
        "ContentBrowser.AssetContextMenu",
        "ContentBrowser.AssetViewContextMenu",
    ]
    
    for menu_name in asset_menu_names:
        try:
            menu = tool_menus.extend_menu(menu_name)
            menu_suffix = menu_name.split('.')[-1]
            replacer_section = f"ReplacerSection_{menu_suffix}"
            
            replacer_entry = RunReferenceReplacer()
            replacer_entry.init_entry(
                menu_owner,
                f"runReferenceReplacer_{menu_suffix}",
                replacer_section,
                "Reference Replacer",
                "Run Reference Replacer Tool"
            )
            
            menu.add_section(replacer_section, "Tools")
            menu.add_menu_entry_object(replacer_entry)
            
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to add replacer menu to {menu_name}: {e}")
    
    tool_menus.refresh_all_widgets()
    unreal.log("✅ Reference replacer menu initialized")


def register():
    """애셋 컨텍스트 메뉴 초기화"""
    # 의존 모듈들 미리 리로드
    try:
        from tool import copier, replacer
        importlib.reload(copier)
        importlib.reload(replacer)
    except Exception as e:
        unreal.log_warning(f"⚠️ Failed to reload tool modules: {e}")
    
    setup_asset_copier_menu()
    setup_reference_replacer_menu()