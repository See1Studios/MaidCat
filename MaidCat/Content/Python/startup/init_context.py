import sys
import importlib
import unreal
from tool import copier
from tool import replacer


@unreal.uclass()
class ReloadPythonModules(unreal.ToolMenuEntryScript):
    """Python 폴더의 모듈 리로드"""
    
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """Python 폴더가 선택된 경우에만 활성화"""
        try:
            folder_menu_class = unreal.load_class(None, '/Script/ContentBrowserData.ContentBrowserDataMenuContext_FolderMenu')
            menu_context = context.find_by_class(folder_menu_class)
            if menu_context:
                selected_items = menu_context.selected_items
                for item in selected_items:
                    virtual_path = str(item.get_virtual_path())
                    if "/Game/Python" in virtual_path or "/All/Game/Python" in virtual_path:
                        return True
            return False
        except:
            return False
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        folder_menu_class = unreal.load_class(None, '/Script/ContentBrowserData.ContentBrowserDataMenuContext_FolderMenu')
        menu_context = context.find_by_class(folder_menu_class)
        if not menu_context:
            return
        
        selected_items = menu_context.selected_items
        if not selected_items:
            return
        
        # 첫 번째 선택된 폴더 경로 가져오기
        virtual_path = str(selected_items[0].get_virtual_path())
        
        # /All/Game/Python/util -> util 추출
        folder_name = None
        if "/Game/Python/" in virtual_path:
            folder_name = virtual_path.split("/Game/Python/")[1].split("/")[0]
        elif "/All/Game/Python/" in virtual_path:
            folder_name = virtual_path.split("/All/Game/Python/")[1].split("/")[0]
        elif virtual_path.endswith("/Game/Python") or virtual_path.endswith("/All/Game/Python"):
            folder_name = None  # Python 폴더 자체
        else:
            return
        
        unreal.log("=" * 60)
        if folder_name:
            unreal.log(f"🔄 '{folder_name}' 폴더 모듈 리로드 시작...")
        else:
            unreal.log("🔄 Python 전체 모듈 리로드 시작...")
        unreal.log("=" * 60)
        
        # sys.modules에서 해당 폴더의 모듈만 찾기
        python_modules = []
        for module_name in list(sys.modules.keys()):
            if folder_name:
                # 특정 폴더의 모듈만 (예: util, util.helper 등)
                if module_name == folder_name or module_name.startswith(folder_name + '.'):
                    python_modules.append(module_name)
            else:
                # Python 폴더 전체 (util, developer, startup, tool 등)
                if module_name.startswith(('util', 'developer', 'startup', 'tool')) or module_name in ['util', 'developer', 'startup', 'tool']:
                    python_modules.append(module_name)
        
        if not python_modules:
            if folder_name:
                unreal.log_warning(f"⚠️ '{folder_name}' 폴더에 로드된 모듈이 없습니다.")
            else:
                unreal.log_warning("⚠️ 리로드할 Python 모듈이 없습니다.")
            return
        
        unreal.log(f"📦 로드된 모듈: {len(python_modules)}개")
        
        # 모듈 리로드
        success_count = 0
        fail_count = 0
        
        for module_name in sorted(python_modules):
            try:
                module = sys.modules[module_name]
                importlib.reload(module)
                unreal.log(f"  ✅ {module_name}")
                success_count += 1
            except Exception as e:
                unreal.log_error(f"  ❌ {module_name}: {e}")
                fail_count += 1
        
        # 결과 요약
        unreal.log("=" * 60)
        unreal.log(f"✅ 성공: {success_count}개")
        if fail_count > 0:
            unreal.log(f"❌ 실패: {fail_count}개")
        unreal.log("🎉 모듈 리로드 완료!")
        unreal.log("=" * 60)


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
            import importlib
            import sys
            
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
        """replacer.py 실행"""
        try:
            unreal.log("🔄 레퍼런스 교체 도구 실행...")
            
            # replacer 모듈 동적 import 및 실행
            import importlib
            import sys
            
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


def setup_python_reload_menu():
    """Python 폴더 컨텍스트 메뉴에 리로드 기능 추가"""
    tool_menus = unreal.ToolMenus.get()
    menu_owner = "pythonReloadMenu"
    
    # 폴더 컨텍스트 메뉴에만 추가
    folder_menu_names = [
        "ContentBrowser.FolderContextMenu",
        "ContentBrowser.PathViewContextMenu",
    ]
    
    for menu_name in folder_menu_names:
        menu = tool_menus.extend_menu(menu_name)
        menu_suffix = menu_name.split('.')[-1]
        python_section = f"PythonSection_{menu_suffix}"
        
        reload_entry = ReloadPythonModules()
        reload_entry.init_entry(
            menu_owner,
            f"reloadPythonModules_{menu_suffix}",
            python_section,
            "Python Reload",
            "Reload Python Modules"
        )
        
        menu.add_section(python_section, "Python")
        menu.add_menu_entry_object(reload_entry)
    
    tool_menus.refresh_all_widgets()
    unreal.log("✅ Python reload menu initialized")


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


# 스크립트 로드 시 자동 실행
importlib.reload(copier)
importlib.reload(replacer)
setup_python_reload_menu()
setup_asset_copier_menu()
setup_reference_replacer_menu()
