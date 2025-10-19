# ============================================================================
# init_unreal.py - MaidCat 플러그인 초기화 스크립트
# ============================================================================
"""
MaidCat 플러그인 시작 시 실행되는 메인 초기화 스크립트
- 의존성 패키지 설치
- Python 경로 설정
- Startup 폴더의 모든 초기화 모듈 자동 실행
- 메뉴 및 툴바 아이템 추가
- VSCode 설정 자동 업데이트 (프로젝트 + 플러그인)
"""

import sys
import os
import unreal
from pathlib import Path
import importlib

# 의존성 설치
try:
    from tool import dependencies_installer
    dependencies_installer.install_dependencies()
except ImportError as e:
    print(f"⚠️  dependencies_installer를 찾을 수 없습니다: {e}")
except Exception as e:
    print(f"❌ 의존성 설치 중 오류 발생: {e}")

# VSCode 설정 모듈
try:
    from tool import vscode_setup
    # 개발 중이므로 모듈 리로드
    importlib.reload(vscode_setup)
    print("🔄 vscode_setup 모듈 리로드됨")
except ImportError as e:
    print(f"⚠️  vscode_setup 모듈을 찾을 수 없습니다: {e}")
    vscode_setup = None

# util 모듈 리로드 (개발 중 변경사항 반영)
try:
    import util.editor as editor_util
    import util.material as material_util
    importlib.reload(editor_util)
    print(f"🔄 util.editor 모듈 리로드됨")
    print(editor_util.UINames.LEVEL_EDITOR_MAIN_MENU)
except ImportError:
    print("⚠️  util 모듈을 찾을 수 없습니다.")


def get_plugin_path():
    """플러그인 경로 반환"""
    # 플러그인 경로는 이 스크립트의 위치를 기준으로 계산
    current_file = Path(__file__)
    # init_unreal.py -> Python -> Content -> MaidCat (플러그인 루트)
    plugin_root = current_file.parent.parent.parent
    return plugin_root


def add_to_sys_path(path_str, description=""):
    """sys.path에 경로 추가 (중복 방지)"""
    if path_str not in sys.path:
        sys.path.append(path_str)
        print(f"✅ Added to sys.path: {path_str}")
        if description:
            print(f"   ({description})")
    return path_str


def setup_python_paths():
    """플러그인 및 프로젝트 Python 경로 설정"""
    plugin_path = get_plugin_path()
    project_path = Path(unreal.Paths.project_dir())
    
    print("\n📂 Setting up Python paths...")
    print(f"   Plugin Path: {plugin_path}")
    print(f"   Project Path: {project_path}")
    
    # === 플러그인 경로 설정 ===
    # 플러그인 Content/Python 경로
    plugin_content_python_path = plugin_path / "Content" / "Python"
    if plugin_content_python_path.exists():
        add_to_sys_path(str(plugin_content_python_path), "Plugin Python scripts")
    
    # 플러그인 Python 라이브러리 경로 (Lib/site-packages)
    plugin_lib_path = plugin_content_python_path / "Lib" / "site-packages"
    if plugin_lib_path.exists():
        add_to_sys_path(str(plugin_lib_path), "Plugin Python libraries")
    
    # === 프로젝트 경로 설정 ===
    # 프로젝트 TA Python 경로
    ta_python_path = project_path / "TA" / "TAPython" / "Python"
    if ta_python_path.exists():
        add_to_sys_path(str(ta_python_path), "Project TA Python scripts")
    
    # 프로젝트 TA Python 라이브러리 경로 (TAPython/Lib/site-packages)
    ta_lib_path = project_path / "TA" / "TAPython" / "Lib" / "site-packages"
    if ta_lib_path.exists():
        add_to_sys_path(str(ta_lib_path), "Project TA Python libraries")
    
    # 프로젝트 Content/Python 경로
    project_content_python_path = project_path / "Content" / "Python"
    if project_content_python_path.exists():
        add_to_sys_path(str(project_content_python_path), "Project Content Python scripts")
    
    return plugin_content_python_path


def run_startup_modules():
    """Startup 폴더의 모든 초기화 모듈 실행"""
    plugin_path = get_plugin_path()
    startup_path = plugin_path / "Content" / "Python" / "startup"
    
    if not startup_path.exists():
        print(f"⚠️  Startup 폴더가 없습니다: {startup_path}")
        print("   Startup 폴더를 생성하고 초기화 스크립트를 추가하세요.")
        return
    
    # Startup 폴더를 sys.path에 추가
    add_to_sys_path(str(startup_path), "Startup modules")
    
    print("\n" + "=" * 60)
    print("🚀 Running Startup Modules...")
    print("=" * 60)
    
    # Startup 폴더의 모든 .py 파일 찾기 (알파벳 순 정렬)
    startup_files = sorted(startup_path.glob("*.py"))
    
    if not startup_files:
        print("⚠️  Startup 폴더에 초기화 스크립트가 없습니다.")
        return
    
    success_count = 0
    fail_count = 0
    
    for startup_file in startup_files:
        # __init__.py나 test_ 파일은 건너뛰기
        if startup_file.name.startswith("_") or startup_file.name.startswith("test_"):
            continue
        
        module_name = startup_file.stem
        print(f"\n📦 Loading: {module_name}")
        
        try:
            # 모듈 동적 import
            module = __import__(module_name)
            
            # 모듈에 run() 함수가 있으면 실행
            if hasattr(module, "run"):
                module.run()
                print(f"   ✅ {module_name}.run() executed")
            else:
                print(f"   ℹ️  {module_name} loaded (no run() function)")
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Error loading {module_name}: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Startup Complete: {success_count} succeeded, {fail_count} failed")
    print("=" * 60)


def create_script_editor_button():
    """툴바에 스크립트 에디터 버튼 추가"""
    section_name = 'MaidCat_Plugins'
    se_command = 'import my_module;w = my_module.show()'  # TODO: 실제 명령으로 교체
    label = 'MaidCat Tools'
    tooltip = "MaidCat 플러그인 도구"
    
    try:
        menus = unreal.ToolMenus.get()
        level_menu_bar = menus.find_menu('LevelEditor.LevelEditorToolBar.PlayToolBar')
        level_menu_bar.add_section(section_name=section_name, label=section_name)

        entry = unreal.ToolMenuEntry(type=unreal.MultiBlockType.TOOL_BAR_BUTTON)
        entry.set_label(label)
        entry.set_tool_tip(tooltip)
        entry.set_icon('EditorStyle', 'DebugConsole.Icon')
        entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(''),
            string=se_command
        )
        level_menu_bar.add_menu_entry(section_name, entry)
        menus.refresh_all_widgets()
        print(f"✅ 툴바 버튼 추가됨: {label}")
    except Exception as e:
        print(f"❌ 툴바 버튼 추가 실패: {e}")


def add_cmd_to_menu(label=None, command=None, tooltip=None, icon=None):
    """메뉴에 명령어 추가"""
    try:
        unreal_menus = unreal.ToolMenus.get()
        parent_menu = unreal_menus.find_menu("LevelEditor.MainMenu.Tools")

        # name kwargs는 유니크해야 함! 설정하지 않으면 자동 생성됨
        entry = unreal.ToolMenuEntry(
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST),
        )
        
        if label:
            entry.set_label(label)
        if command:
            entry.set_string_command(
                type=unreal.ToolMenuStringCommandType.PYTHON,
                string=command,
                custom_type=unreal.Name("MaidCat_Plugin"),
            )
        if tooltip:
            entry.set_tool_tip(tooltip)
        if icon:
            entry.set_icon(icon)

        parent_menu.add_menu_entry("MaidCat", entry)
        print(f"✅ 메뉴 아이템 추가됨: {label}")
    except Exception as e:
        print(f"❌ 메뉴 아이템 추가 실패: {e}")


def setup_ui_elements():
    """UI 요소 설정 (메뉴, 툴바 등)"""
    print("\n🎨 Setting up UI elements...")
    
    # 기본 설정
    section_name = 'MaidCat_Plugins'
    se_command = 'import my_module;w = my_module.show()'  # TODO: 실제 명령으로 교체
    label = 'MaidCat Tools'
    tooltip = "MaidCat 플러그인 도구 모음"
    
    # 툴바 버튼 추가 (주석 해제하면 활성화)
    # create_script_editor_button()
    
    # 메뉴 아이템 추가
    add_cmd_to_menu(label=label, command=se_command, tooltip=tooltip)








def main():
    """메인 초기화 함수"""
    print("\n" + "=" * 60)
    print("🐱 MaidCat Plugin Initialization")
    print("=" * 60)
    
    plugin_path = get_plugin_path()
    project_path = Path(unreal.Paths.project_dir())
    print(f"📁 Plugin Path: {plugin_path}")
    print(f"📁 Project Path: {project_path}")
    
    try:
        # --- 1. Python 경로 설정 (플러그인 + 프로젝트) ---
        plugin_content_python_path = setup_python_paths()
        
        # --- 2. VSCode 설정 자동 업데이트 ---
        if vscode_setup:
            print("🔧 VSCode 설정 모듈을 실행합니다...")
            vscode_setup.setup_vscode()
        else:
            print("⚠️  VSCode 설정 모듈을 사용할 수 없습니다.")
        
        # --- 3. Startup 모듈 실행 ---
        run_startup_modules()
        
        # --- 4. UI 요소 설정 ---
        setup_ui_elements()
        
        print(f"\n🎉 MaidCat 플러그인이 성공적으로 활성화되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 플러그인 초기화 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error in init_unreal.py: {e}")
        import traceback
        traceback.print_exc()