# ============================================================================
# dev_env_setup - 언리얼 엔진 파이썬 개발 환경 통합 설정 모듈
# ============================================================================
"""
언리얼 엔진 파이썬 개발 환경을 자동으로 설정하는 통합 모듈
- VSCode 설정 자동화 (Python 경로, Pylance 설정, 인터프리터)
- PyCharm 설정 자동화 (Python 경로, 인터프리터, 코드 스타일)
- 플러그인 및 프로젝트 환경 자동 감지
- 개발 도구별 최적화된 설정 제공

사용법:
    # 기본 설정 (모든 IDE 설정)
    import dev_env_setup
    dev_env_setup.setup_all()
    
    # 특정 IDE만 설정
    dev_env_setup.setup_vscode()           # VSCode만
    dev_env_setup.setup_pycharm()          # PyCharm만
    
    # Pylance 타입 설정 변경
    dev_env_setup.pylance_permissive()     # 추천: 외부 라이브러리 사용 시
    dev_env_setup.pylance_strict()         # 엄격한 타입 체크
    dev_env_setup.pylance_off()            # 타입 체크 완전 비활성화
    
    # 편의 함수들
    dev_env_setup.ignore_types()           # = pylance_permissive()
    dev_env_setup.no_typecheck()           # = pylance_off()
    dev_env_setup.strict_types()           # = pylance_strict()
"""

import json
import xml.etree.ElementTree as ET
import unreal
from pathlib import Path
import sys
import platform


# ============================================================================
# 공통 유틸리티 함수들
# ============================================================================

def _get_paths():
    """필요한 경로들 수집"""
    project_path = Path(unreal.Paths.project_dir())
    current_file = Path(__file__)
    current_plugin_path = current_file.parent.parent.parent.parent.parent  # MaidCat 폴더
    resolved_plugin_path = current_plugin_path.resolve()
    
    return project_path, current_plugin_path, resolved_plugin_path


def _is_plugin_in_project(resolved_plugin_path, project_path):
    """플러그인이 프로젝트 내부에 있는지 확인"""
    return resolved_plugin_path.is_relative_to(project_path.resolve())


def _print_debug_info(project_path, current_plugin_path, resolved_plugin_path):
    """디버그 정보 출력"""
    print(f"   🔍 프로젝트: {project_path}")
    print(f"   🔍 플러그인: {current_plugin_path}")
    print(f"   🔍 실제 경로: {resolved_plugin_path}")
    print(f"   🔍 심볼릭 링크: {current_plugin_path.is_symlink()}")


# ============================================================================
# Python 경로 생성 함수들
# ============================================================================

def _get_standard_python_paths():
    """표준 언리얼 Python 경로들 반환"""
    return [
        ("./Intermediate/PythonStub", "Unreal Python stub"),
        ("./TA/TAPython/Python", "TA Python scripts"),
        ("./TA/TAPython/Lib/site-packages", "TA Python libraries"),
        ("./Content/Python", "Project Content Python"),
        ("./Content/Python/Lib/site-packages", "Project Content Python libraries"),
        ("./Intermediate/PipInstall/Lib/site-packages", "Pip installed packages"),
        ("./Python/Lib/site-packages", "Project Python libraries")
    ]


def get_project_python_paths(plugin_path, project_path):
    """프로젝트용 Python 경로 리스트 생성"""
    python_paths = []
    
    # 표준 프로젝트 경로들 (상대 경로)
    for rel_path, description in _get_standard_python_paths():
        python_paths.append(rel_path)
        abs_path = project_path / rel_path.replace("./", "")
        exists = abs_path.exists()
        print(f"   {'✅' if exists else '⚠️'} {description}: {rel_path}")
    
    # 플러그인 경로 추가
    _add_plugin_paths_to_list(python_paths, plugin_path, project_path)
    
    # Plugins 폴더 내 다른 플러그인들도 검색
    _add_other_plugins_paths(python_paths, project_path)
    
    return python_paths


def get_plugin_python_paths(project_path):
    """플러그인용 Python 경로 리스트 생성 (플러그인: 상대, 프로젝트: 절대)"""
    python_paths = []
    
    # 플러그인 자체 경로 (상대 경로)
    plugin_paths = [
        "./MaidCat/Content/Python",
        "./MaidCat/Content/Python/Lib/site-packages"
    ]
    python_paths.extend(plugin_paths)
    print(f"   ✅ 플러그인 경로들: {plugin_paths}")
    
    # 프로젝트 경로들 (절대 경로)
    for rel_path, description in _get_standard_python_paths():
        abs_path = project_path / rel_path.replace("./", "")
        path_str = str(abs_path).replace("\\", "/")
        python_paths.append(path_str)
        exists = abs_path.exists()
        print(f"   {'✅' if exists else '⚠️'} {description}: {path_str}")
    
    return python_paths


def _add_plugin_paths_to_list(python_paths, plugin_path, project_path):
    """플러그인 경로를 리스트에 추가 (상대/절대 경로 자동 판단)"""
    try:
        # 상대 경로로 변환 시도
        plugin_relative = plugin_path.resolve().relative_to(project_path.resolve())
        plugin_paths = [
            str(plugin_relative / "Content" / "Python").replace("\\", "/"),
            str(plugin_relative / "Content" / "Python" / "Lib" / "site-packages").replace("\\", "/")
        ]
        python_paths.extend(plugin_paths)
        print(f"   ✅ 플러그인 경로 (상대): {plugin_paths}")
    except ValueError:
        # 프로젝트 외부인 경우 절대 경로 사용
        plugin_paths = [
            str(plugin_path / "Content" / "Python"),
            str(plugin_path / "Content" / "Python" / "Lib" / "site-packages")
        ]
        python_paths.extend(plugin_paths)
        print(f"   ✅ 플러그인 경로 (절대): {plugin_paths}")


def _add_other_plugins_paths(python_paths, project_path):
    """다른 플러그인들의 Python 경로도 추가"""
    plugins_dir = project_path / "Plugins"
    if plugins_dir.exists():
        for plugin_dir in plugins_dir.iterdir():
            if plugin_dir.is_dir() and plugin_dir.name != "MaidCat":
                plugin_python = plugin_dir / "Content" / "Python"
                if plugin_python.exists():
                    try:
                        plugin_relative = plugin_python.relative_to(project_path)
                        rel_path = f"./{plugin_relative}".replace("\\", "/")
                        python_paths.append(rel_path)
                        print(f"   ✅ 다른 플러그인: {rel_path}")
                    except ValueError:
                        pass


# ============================================================================
# 언리얼 Python 인터프리터 감지
# ============================================================================

def _get_unreal_python_interpreter():
    """언리얼 엔진 Python 인터프리터 경로 자동 감지 (레지스트리 기반)"""
    try:
        if platform.system() != "Windows":
            return _get_unreal_python_non_windows()
        
        import winreg
        
        # 프로젝트 파일에서 엔진 연결 정보 읽기
        project_path = Path(unreal.Paths.project_dir())
        uproject_files = list(project_path.glob("*.uproject"))
        
        if uproject_files:
            with open(uproject_files[0], 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                engine_association = project_data.get("EngineAssociation", "")
                
                print(f"   🔍 엔진 연결: {engine_association}")
                
                if engine_association:
                    # 레지스트리에서 엔진 경로 찾기
                    engine_path = _get_engine_path_from_registry(engine_association)
                    if engine_path:
                        python_exe = Path(engine_path) / "Engine" / "Binaries" / "ThirdParty" / "Python3" / "Win64" / "python.exe"
                        if python_exe.exists():
                            python_path = str(python_exe).replace("\\", "/")
                            print(f"   ✅ 언리얼 Python 인터프리터 (레지스트리): {python_path}")
                            return python_path
        
        # 폴백: 일반적인 경로들 시도
        return _get_unreal_python_fallback()
        
    except Exception as e:
        print(f"   ❌ 언리얼 Python 인터프리터 감지 실패: {e}")
        return _get_unreal_python_fallback()


def _get_unreal_python_non_windows():
    """Windows가 아닌 시스템에서의 언리얼 Python 경로 찾기"""
    if platform.system() == "Darwin":  # macOS
        common_paths = [
            "/Applications/Epic Games/UE_5.5/Engine/Binaries/ThirdParty/Python3/Mac/bin/python3",
            "/Applications/Epic Games/UE_5.4/Engine/Binaries/ThirdParty/Python3/Mac/bin/python3"
        ]
    else:  # Linux
        common_paths = [
            "/opt/UnrealEngine/Engine/Binaries/ThirdParty/Python3/Linux/bin/python3",
            "/usr/local/UnrealEngine/Engine/Binaries/ThirdParty/Python3/Linux/bin/python3"
        ]
    
    for path_str in common_paths:
        path_obj = Path(path_str)
        if path_obj.exists():
            print(f"   ✅ 언리얼 Python 인터프리터: {path_str}")
            return path_str
    
    return None


def _get_unreal_python_fallback():
    """폴백 방식으로 언리얼 Python 인터프리터 찾기"""
    common_paths = [
        "C:/Program Files/Epic Games/UE_5.5/Engine/Binaries/ThirdParty/Python3/Win64/python.exe",
        "C:/Program Files/Epic Games/UE_5.4/Engine/Binaries/ThirdParty/Python3/Win64/python.exe",
        "C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/ThirdParty/Python3/Win64/python.exe"
    ]
    
    for path_str in common_paths:
        path_obj = Path(path_str)
        if path_obj.exists():
            python_path = path_str.replace("\\", "/")
            print(f"   ✅ 언리얼 Python 인터프리터 (일반 경로): {python_path}")
            return python_path
    
    print(f"   ⚠️  언리얼 Python 인터프리터를 찾을 수 없음")
    return None


def _get_engine_path_from_registry(engine_association):
    """Windows 레지스트리에서 언리얼 엔진 경로 찾기"""
    try:
        import winreg
        
        # 레지스트리 키 경로들
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Epic Games\Unreal Engine\Builds"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Epic Games\Unreal Engine\Builds"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Epic Games\Unreal Engine\Builds")
        ]
        
        for hkey, registry_path in registry_paths:
            try:
                with winreg.OpenKey(hkey, registry_path) as key:
                    engine_path, _ = winreg.QueryValueEx(key, engine_association)
                    if engine_path and Path(engine_path).exists():
                        print(f"   ✅ 레지스트리에서 엔진 경로 발견: {engine_path}")
                        return engine_path
            except (FileNotFoundError, OSError):
                continue
        
        # GUID 형태가 아닌 경우 버전 문자열로 Epic Games 경로 시도
        if not _is_guid(engine_association):
            epic_path = f"C:/Program Files/Epic Games/UE_{engine_association}"
            if Path(epic_path).exists():
                print(f"   ✅ Epic Games 표준 경로: {epic_path}")
                return epic_path
        
        print(f"   ⚠️  레지스트리에서 엔진 경로를 찾을 수 없음: {engine_association}")
        return None
        
    except Exception as e:
        print(f"   ❌ 레지스트리 읽기 실패: {e}")
        return None


def _is_guid(text):
    """문자열이 GUID 형태인지 확인"""
    import re
    guid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return re.match(guid_pattern, text) is not None


# ============================================================================
# VSCode 설정 관리
# ============================================================================

def get_pylance_strict_settings():
    """엄격한 Pylance 타입 설정 반환"""
    return {
        "python.analysis.typeCheckingMode": "strict",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingImports": "error",
            "reportMissingTypeStubs": "warning", 
            "reportUnknownMemberType": "warning",
            "reportUnknownArgumentType": "warning",
            "reportUnknownVariableType": "warning",
            "reportAttributeAccessIssue": "error",
            "reportOptionalMemberAccess": "error",
            "reportOptionalCall": "error",
            "reportOptionalIterable": "error",
            "reportOptionalContextManager": "error",
            "reportOptionalOperand": "error"
        }
    }


def get_pylance_permissive_settings():
    """관대한 Pylance 타입 설정 반환 (외부 라이브러리 작업용)"""
    return {
        "python.analysis.typeCheckingMode": "basic",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingImports": "none",
            "reportMissingTypeStubs": "none", 
            "reportUnknownMemberType": "none",
            "reportUnknownArgumentType": "none",
            "reportUnknownVariableType": "none",
            "reportAttributeAccessIssue": "warning",
            "reportOptionalMemberAccess": "warning",
            "reportOptionalCall": "warning",
            "reportOptionalIterable": "warning",
            "reportOptionalContextManager": "warning",
            "reportOptionalOperand": "warning",
            "reportGeneralTypeIssues": "none",
            "reportUntypedFunctionDecorator": "none",
            "reportUntypedClassDecorator": "none",
            "reportUntypedBaseClass": "none",
            "reportUntypedNamedTuple": "none"
        }
    }


def get_pylance_disabled_settings():
    """Pylance 타입 체크 완전 비활성화 설정"""
    return {
        "python.analysis.typeCheckingMode": "off",
        "python.analysis.diagnosticSeverityOverrides": {
            "reportMissingImports": "none",
            "reportMissingTypeStubs": "none", 
            "reportUnknownMemberType": "none",
            "reportUnknownArgumentType": "none",
            "reportUnknownVariableType": "none",
            "reportAttributeAccessIssue": "none",
            "reportOptionalMemberAccess": "none",
            "reportOptionalCall": "none",
            "reportOptionalIterable": "none",
            "reportOptionalContextManager": "none",
            "reportOptionalOperand": "none",
            "reportGeneralTypeIssues": "none"
        }
    }


def get_vscode_cspell_words():
    """언리얼 엔진용 cSpell 단어 목록"""
    return [
        # 언리얼 엔진 기본 매크로
        "uclass", "ufunction", "uproperty", "ustruct", "uenum",
        "uinterface", "umeta", "uparam", "udelegate", "umulticastdelegate",
        
        # 언리얼 엔진 타입들
        "fstring", "fname", "ftext", "fvector", "frotator", "ftransform",
        "fcolor", "flinearcolor", "tarray", "tmap", "tset", "tsharedptr",
        "tweakptr", "tuniqueptr", "tsoftobjectptr", "tsoftclassptr",
        
        # 언리얼 엔진 클래스들
        "aactor", "apawn", "acharacter", "acontroller", "aplayercontroller",
        "agamemode", "agamestate", "aplayerstate", "ahud", "uobject",
        "uactorcomponent", "uscenecomponent", "uprimitivecomponent",
        "ustaticmeshcomponent", "uskeletalmeshcomponent", "uwidget",
        
        # 언리얼 엔진 모듈들
        "unrealed", "blueprintgraph", "kismet", "sequencer", "leveleditor",
        "contentbrowser", "assettools", "editorstyle", "toolmenus",
        "workspacecontroller", "mainframe", "detailsview", "propertyeditor",
        
        # Python 관련
        "pygame", "numpy", "matplotlib", "scipy", "opencv", "tensorflow",
        "pytorch", "sklearn", "pandas", "seaborn", "plotly", "jupyter",
        
        # 개발 도구 관련
        "vscode", "pycharm", "intellij", "pylance", "autopep", "flake",
        "mypy", "pytest", "unittest", "docstring", "setuptools", "pip"
    ]


def _create_vscode_python_settings(python_paths, pylance_mode="permissive"):
    """VSCode Python 설정 딕셔너리 생성"""
    settings = {
        "python.analysis.extraPaths": python_paths,
        "python.autoComplete.extraPaths": python_paths,
        "python.envFile": "${workspaceFolder}/.env",
        "python.languageServer": "Pylance",
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit"
            }
        },
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/.pytest_cache": True
        },
        "cSpell.words": get_vscode_cspell_words()
    }
    
    # Pylance 타입 설정 추가
    if pylance_mode == "strict":
        pylance_settings = get_pylance_strict_settings()
    elif pylance_mode == "disabled":
        pylance_settings = get_pylance_disabled_settings()
    else:  # permissive (기본값)
        pylance_settings = get_pylance_permissive_settings()
    
    settings.update(pylance_settings)
    
    # 언리얼 Python 인터프리터 경로 추가
    unreal_python = _get_unreal_python_interpreter()
    if unreal_python:
        settings["python.defaultInterpreterPath"] = unreal_python
    
    return settings


def _load_existing_vscode_settings(settings_path):
    """기존 VSCode 설정 로드"""
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"   ⚠️  기존 설정 읽기 실패: {e}")
        return {}


def _save_vscode_settings(settings_path, settings):
    """VSCode 설정 파일 저장"""
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def update_vscode_settings_file(settings_path, python_paths, pylance_mode="permissive"):
    """VSCode 설정 파일 업데이트"""
    print(f"   📁 VSCode 설정: {settings_path}")
    
    # 기존 설정 로드 및 업데이트
    existing_settings = _load_existing_vscode_settings(settings_path)
    new_settings = _create_vscode_python_settings(python_paths, pylance_mode)
    existing_settings.update(new_settings)
    
    # 설정 저장
    _save_vscode_settings(settings_path, existing_settings)
    print(f"   ✅ VSCode 설정 완료 ({len(python_paths)} paths)")


# ============================================================================
# PyCharm 설정 관리
# ============================================================================

def get_pycharm_config_dir():
    """PyCharm 설정 디렉토리 찾기"""
    home = Path.home()
    
    # OS별 PyCharm 설정 경로
    if platform.system() == "Windows":
        config_dirs = [
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharm2024.3",
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharm2024.2",
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharm2024.1",
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharm2023.3",
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharmCE2024.3",
            home / "AppData" / "Roaming" / "JetBrains" / "PyCharmCE2024.2",
        ]
    elif platform.system() == "Darwin":  # macOS
        config_dirs = [
            home / "Library" / "Application Support" / "JetBrains" / "PyCharm2024.3",
            home / "Library" / "Application Support" / "JetBrains" / "PyCharm2024.2",
            home / "Library" / "Application Support" / "JetBrains" / "PyCharmCE2024.3",
        ]
    else:  # Linux
        config_dirs = [
            home / ".config" / "JetBrains" / "PyCharm2024.3",
            home / ".config" / "JetBrains" / "PyCharm2024.2",
            home / ".config" / "JetBrains" / "PyCharmCE2024.3",
        ]
    
    for config_dir in config_dirs:
        if config_dir.exists():
            return config_dir
    
    return None


def create_pycharm_project_config(project_path, python_paths):
    """PyCharm 프로젝트 설정 파일들 생성"""
    idea_dir = project_path / ".idea"
    idea_dir.mkdir(exist_ok=True)
    
    # 1. misc.xml - 프로젝트 기본 설정
    _create_pycharm_misc_xml(idea_dir)
    
    # 2. modules.xml - 모듈 설정
    _create_pycharm_modules_xml(idea_dir, project_path)
    
    # 3. [프로젝트명].iml - 모듈 파일
    _create_pycharm_iml_file(idea_dir, project_path, python_paths)
    
    # 4. workspace.xml - 워크스페이스 설정
    _create_pycharm_workspace_xml(idea_dir)
    
    print(f"   ✅ PyCharm 프로젝트 설정 완료: {idea_dir}")


def _create_pycharm_misc_xml(idea_dir):
    """PyCharm misc.xml 파일 생성"""
    misc_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Unreal Python" project-jdk-type="Python SDK" />
  <component name="PyCharmProfessionalAdvertiser">
    <option name="shown" value="true" />
  </component>
</project>'''
    
    misc_path = idea_dir / "misc.xml"
    with open(misc_path, 'w', encoding='utf-8') as f:
        f.write(misc_content)


def _create_pycharm_modules_xml(idea_dir, project_path):
    """PyCharm modules.xml 파일 생성"""
    project_name = project_path.name
    modules_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/{project_name}.iml" filepath="$PROJECT_DIR$/.idea/{project_name}.iml" />
    </modules>
  </component>
</project>'''
    
    modules_path = idea_dir / "modules.xml"
    with open(modules_path, 'w', encoding='utf-8') as f:
        f.write(modules_content)


def _create_pycharm_iml_file(idea_dir, project_path, python_paths):
    """PyCharm .iml 모듈 파일 생성"""
    project_name = project_path.name
    
    # Python 경로들을 절대 경로로 변환
    content_roots = []
    source_folders = []
    
    for path in python_paths:
        if path.startswith("./"):
            # 상대 경로를 절대 경로로 변환
            abs_path = project_path / path[2:]
        else:
            abs_path = Path(path)
        
        if abs_path.exists():
            path_url = f"file://{abs_path.as_posix()}"
            content_roots.append(f'    <content url="{path_url}">\n      <sourceFolder url="{path_url}" isTestSource="false" />\n    </content>')
    
    content_roots_xml = '\n'.join(content_roots)
    
    iml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <excludeFolder url="file://$MODULE_DIR$/Binaries" />
      <excludeFolder url="file://$MODULE_DIR$/Intermediate" />
      <excludeFolder url="file://$MODULE_DIR$/Saved" />
      <excludeFolder url="file://$MODULE_DIR$/.git" />
    </content>
{content_roots_xml}
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
  <component name="PyDocumentationSettings">
    <option name="format" value="GOOGLE" />
    <option name="myDocStringFormat" value="Google" />
  </component>
  <component name="TestRunnerService">
    <option name="PROJECT_TEST_RUNNER" value="pytest" />
  </component>
</module>'''
    
    iml_path = idea_dir / f"{project_name}.iml"
    with open(iml_path, 'w', encoding='utf-8') as f:
        f.write(iml_content)


def _create_pycharm_workspace_xml(idea_dir):
    """PyCharm workspace.xml 파일 생성"""
    workspace_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ChangeListManager">
    <list default="true" id="default" name="Changes" comment="" />
    <option name="SHOW_DIALOG" value="false" />
    <option name="HIGHLIGHT_CONFLICTS" value="true" />
    <option name="HIGHLIGHT_NON_ACTIVE_CHANGELIST" value="false" />
    <option name="LAST_RESOLUTION" value="IGNORE" />
  </component>
  <component name="Git.Settings">
    <option name="RECENT_GIT_ROOT_PATH" value="$PROJECT_DIR$" />
  </component>
  <component name="ProjectId" id="UnrealPython" />
  <component name="ProjectViewState">
    <option name="hideEmptyMiddlePackages" value="true" />
    <option name="showLibraryContents" value="true" />
  </component>
  <component name="PropertiesComponent"><![CDATA[{
  "keyToString": {
    "RunOnceActivity.OpenProjectViewOnStart": "true",
    "RunOnceActivity.ShowReadmeOnStart": "true",
    "last_opened_file_path": "$PROJECT_DIR$",
    "settings.editor.selected.configurable": "com.jetbrains.python.configuration.PyActiveSdkModuleConfigurable"
  }
}]]></component>
  <component name="SpellCheckerSettings" RuntimeDictionaries="0" Folders="0" CustomDictionaries="0" DefaultDictionary="application-level" UseSingleDictionary="true" transferred="true" />
  <component name="TaskManager">
    <task active="true" id="Default" summary="Default task">
      <changelist id="default" name="Changes" comment="" />
      <created>1699000000000</created>
      <option name="number" value="Default" />
      <option name="presentableId" value="Default" />
      <updated>1699000000000</updated>
    </task>
    <servers />
  </component>
</project>'''
    
    workspace_path = idea_dir / "workspace.xml"
    with open(workspace_path, 'w', encoding='utf-8') as f:
        f.write(workspace_content)


def setup_pycharm_python_interpreter():
    """PyCharm에서 사용할 언리얼 Python 인터프리터 설정"""
    unreal_python = _get_unreal_python_interpreter()
    if not unreal_python:
        print("   ⚠️  언리얼 Python 인터프리터를 찾을 수 없음")
        return False
    
    # PyCharm 설정 디렉토리 찾기
    config_dir = get_pycharm_config_dir()
    if not config_dir:
        print("   ⚠️  PyCharm 설정 디렉토리를 찾을 수 없음")
        return False
    
    # jdk.table.xml 파일에 Python SDK 추가
    jdk_table_path = config_dir / "options" / "jdk.table.xml"
    if jdk_table_path.exists():
        _update_pycharm_jdk_table(jdk_table_path, unreal_python)
    else:
        _create_pycharm_jdk_table(jdk_table_path, unreal_python)
    
    print(f"   ✅ PyCharm Python 인터프리터 설정 완료: {unreal_python}")
    return True


def _update_pycharm_jdk_table(jdk_table_path, python_path):
    """기존 PyCharm jdk.table.xml 파일 업데이트"""
    try:
        tree = ET.parse(jdk_table_path)
        root = tree.getroot()
        
        # 기존 "Unreal Python" SDK가 있는지 확인
        for jdk in root.findall(".//jdk[@version='2']"):
            name_elem = jdk.find("name")
            if name_elem is not None and name_elem.get("value") == "Unreal Python":
                # 기존 SDK 업데이트
                homepath = jdk.find("homePath")
                if homepath is not None:
                    homepath.set("value", str(Path(python_path).parent))
                return
        
        # 기존 SDK가 없으면 추가
        _add_python_sdk_to_jdk_table(root, python_path)
        tree.write(jdk_table_path, encoding='utf-8', xml_declaration=True)
        
    except Exception as e:
        print(f"   ❌ PyCharm jdk.table.xml 업데이트 실패: {e}")


def _create_pycharm_jdk_table(jdk_table_path, python_path):
    """새로운 PyCharm jdk.table.xml 파일 생성"""
    jdk_table_path.parent.mkdir(parents=True, exist_ok=True)
    
    root = ET.Element("application")
    component = ET.SubElement(root, "component", name="ProjectJdkTable")
    
    _add_python_sdk_to_jdk_table(component, python_path)
    
    tree = ET.ElementTree(root)
    tree.write(jdk_table_path, encoding='utf-8', xml_declaration=True)


def _add_python_sdk_to_jdk_table(parent, python_path):
    """jdk.table.xml에 Python SDK 추가"""
    python_home = str(Path(python_path).parent)
    
    jdk = ET.SubElement(parent, "jdk", version="2")
    ET.SubElement(jdk, "name", value="Unreal Python")
    ET.SubElement(jdk, "type", value="Python SDK")
    ET.SubElement(jdk, "version", value="Python 3.11")
    ET.SubElement(jdk, "homePath", value=python_home)
    
    # 추가 설정들
    additional = ET.SubElement(jdk, "additional")
    ET.SubElement(additional, "option", name="interpreterType", value="Python SDK")
    ET.SubElement(additional, "option", name="sdkSeemsValid", value="true")


# ============================================================================
# 메인 설정 함수들
# ============================================================================

def update_project_settings():
    """프로젝트의 개발 환경 설정 업데이트 (기본: permissive 모드)"""
    print(f"\n📁 프로젝트 개발 환경 설정 시작")
    
    try:
        # 경로 정보 수집
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        
        # VSCode 설정
        vscode_settings_path = project_path / ".vscode" / "settings.json"
        update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
        
        # PyCharm 설정
        create_pycharm_project_config(project_path, python_paths)
        
    except Exception as e:
        print(f"   ❌ 프로젝트 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_plugin_settings():
    """플러그인의 개발 환경 설정 업데이트 (기본: permissive 모드)"""
    print(f"\n📁 플러그인 개발 환경 설정 시작")
    
    try:
        # 경로 정보 수집
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # 플러그인이 프로젝트 외부에 있는 경우에만 별도 설정
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            print(f"   🔧 독립 개발 폴더: {plugin_dev_root}")
            
            python_paths = get_plugin_python_paths(project_path)
            
            # VSCode 설정
            vscode_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
            
            # PyCharm 설정  
            create_pycharm_project_config(plugin_dev_root, python_paths)
        else:
            print(f"   📁 프로젝트 내부 플러그인 - 별도 설정 불필요")
            
    except Exception as e:
        print(f"   ❌ 플러그인 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# 고급 설정 함수들 (파라미터가 필요한 경우)
def update_project_settings_with_mode(pylance_mode="permissive"):
    """프로젝트의 개발 환경 설정 업데이트 (pylance 모드 선택 가능)"""
    print(f"\n📁 프로젝트 개발 환경 설정 시작")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        
        vscode_settings_path = project_path / ".vscode" / "settings.json"
        update_vscode_settings_file(vscode_settings_path, python_paths, pylance_mode)
        
        create_pycharm_project_config(project_path, python_paths)
        
    except Exception as e:
        print(f"   ❌ 프로젝트 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_plugin_settings_with_mode(pylance_mode="permissive"):
    """플러그인의 개발 환경 설정 업데이트 (pylance 모드 선택 가능)"""
    print(f"\n📁 플러그인 개발 환경 설정 시작")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            print(f"   🔧 독립 개발 폴더: {plugin_dev_root}")
            
            python_paths = get_plugin_python_paths(project_path)
            
            vscode_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            update_vscode_settings_file(vscode_settings_path, python_paths, pylance_mode)
            
            create_pycharm_project_config(plugin_dev_root, python_paths)
        else:
            print(f"   📁 프로젝트 내부 플러그인 - 별도 설정 불필요")
            
    except Exception as e:
        print(f"   ❌ 플러그인 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_pylance_settings():
    """Pylance 타입 설정 업데이트 (기본: permissive 모드)"""
    print(f"\n⚙️  Pylance 타입 설정 업데이트 (permissive 모드)...")
    
    try:
        # 경로 정보 수집
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # permissive 설정 사용
        pylance_settings = get_pylance_permissive_settings()
        
        # 프로젝트 설정 업데이트
        project_settings_path = project_path / ".vscode" / "settings.json"
        _update_pylance_in_settings_file(project_settings_path, pylance_settings)
        
        # 플러그인이 프로젝트 외부에 있는 경우 플러그인 설정도 업데이트
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            plugin_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            _update_pylance_in_settings_file(plugin_settings_path, pylance_settings)
        
        print(f"   ✅ Pylance 설정 완료 (permissive 모드)")
        
    except Exception as e:
        print(f"   ❌ Pylance 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_pylance_settings_with_mode(mode="permissive"):
    """Pylance 타입 설정 업데이트 (모드 선택 가능)
    
    Args:
        mode: "strict", "permissive", "disabled" 중 하나
    """
    print(f"\n⚙️  Pylance 타입 설정 업데이트 ({mode} 모드)...")
    
    try:
        # 경로 정보 수집
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # 모드에 따른 설정 선택
        if mode == "strict":
            pylance_settings = get_pylance_strict_settings()
        elif mode == "disabled":
            pylance_settings = get_pylance_disabled_settings()
        else:  # permissive (기본값)
            pylance_settings = get_pylance_permissive_settings()
        
        # 프로젝트 설정 업데이트
        project_settings_path = project_path / ".vscode" / "settings.json"
        _update_pylance_in_settings_file(project_settings_path, pylance_settings)
        
        # 플러그인이 프로젝트 외부에 있는 경우 플러그인 설정도 업데이트
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            plugin_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            _update_pylance_in_settings_file(plugin_settings_path, pylance_settings)
        
        print(f"   ✅ Pylance 설정 완료 ({mode} 모드)")
        
    except Exception as e:
        print(f"   ❌ Pylance 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def _update_pylance_in_settings_file(settings_path, pylance_settings):
    """특정 설정 파일의 Pylance 설정만 업데이트"""
    print(f"   📁 Pylance 설정 업데이트: {settings_path}")
    
    # 기존 설정 로드
    existing_settings = _load_existing_vscode_settings(settings_path)
    
    # Pylance 설정만 업데이트
    existing_settings.update(pylance_settings)
    
    # 설정 저장
    _save_vscode_settings(settings_path, existing_settings)


def update_all_settings():
    """모든 개발 환경 설정 업데이트 (VSCode + PyCharm, 기본: permissive 모드)"""
    print("\n⚙️  통합 개발 환경 설정 시작...")
    
    try:
        # 경로 정보 수집 및 출력
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        # 프로젝트 설정
        update_project_settings()
        
        # 플러그인 설정 (필요한 경우)
        update_plugin_settings()
        
        # PyCharm Python 인터프리터 전역 설정
        setup_pycharm_python_interpreter()
        
        print(f"\n✅ 통합 개발 환경 설정 완료!")
        print("   📝 VSCode와 PyCharm에서 언리얼 엔진 Python 개발이 가능합니다.")
        print("   💡 IDE를 재시작하면 새 설정이 적용됩니다.")
            
    except Exception as e:
        print(f"   ❌ 통합 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_all_settings_with_mode(pylance_mode="permissive"):
    """모든 개발 환경 설정 업데이트 (VSCode + PyCharm, pylance 모드 선택 가능)"""
    print("\n⚙️  통합 개발 환경 설정 시작...")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        update_project_settings_with_mode(pylance_mode)
        update_plugin_settings_with_mode(pylance_mode)
        
        setup_pycharm_python_interpreter()
        
        print(f"\n✅ 통합 개발 환경 설정 완료!")
        print("   📝 VSCode와 PyCharm에서 언리얼 엔진 Python 개발이 가능합니다.")
        print("   💡 IDE를 재시작하면 새 설정이 적용됩니다.")
            
    except Exception as e:
        print(f"   ❌ 통합 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# 공개 API
# ============================================================================

def setup_all():
    """모든 개발 환경 설정 (VSCode + PyCharm) - 파라미터 없음"""
    update_all_settings()


def setup_vscode():
    """VSCode 환경 설정만 - 파라미터 없음"""
    print("\n⚙️  VSCode 개발 환경 설정...")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        # 프로젝트 VSCode 설정
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        vscode_settings_path = project_path / ".vscode" / "settings.json"
        update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
        
        # 플러그인 VSCode 설정 (필요한 경우)
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            python_paths = get_plugin_python_paths(project_path)
            vscode_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
        
        print(f"   ✅ VSCode 설정 완료!")
        
    except Exception as e:
        print(f"   ❌ VSCode 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def setup_pycharm():
    """PyCharm 환경 설정만 - 파라미터 없음"""
    print("\n⚙️  PyCharm 개발 환경 설정...")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        # 프로젝트 PyCharm 설정
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        create_pycharm_project_config(project_path, python_paths)
        
        # 플러그인 PyCharm 설정 (필요한 경우)
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            python_paths = get_plugin_python_paths(project_path)
            create_pycharm_project_config(plugin_dev_root, python_paths)
        
        # 전역 Python 인터프리터 설정
        setup_pycharm_python_interpreter()
        
        print(f"   ✅ PyCharm 설정 완료!")
        
    except Exception as e:
        print(f"   ❌ PyCharm 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# 고급 설정 함수들 (파라미터 필요 시에만 사용)
def setup_all_with_mode(pylance_mode="permissive"):
    """모든 개발 환경 설정 (pylance 모드 선택 가능)"""
    update_all_settings_with_mode(pylance_mode)


def setup_vscode_with_mode(pylance_mode="permissive"):
    """VSCode 환경 설정 (pylance 모드 선택 가능)"""
    print("\n⚙️  VSCode 개발 환경 설정...")
    
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        # 프로젝트 VSCode 설정
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        vscode_settings_path = project_path / ".vscode" / "settings.json"
        update_vscode_settings_file(vscode_settings_path, python_paths, pylance_mode)
        
        # 플러그인 VSCode 설정 (필요한 경우)
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            python_paths = get_plugin_python_paths(project_path)
            vscode_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            update_vscode_settings_file(vscode_settings_path, python_paths, pylance_mode)
        
        print(f"   ✅ VSCode 설정 완료!")
        
    except Exception as e:
        print(f"   ❌ VSCode 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def pylance_strict():
    """Pylance를 strict 모드로 설정"""
    update_pylance_settings_with_mode("strict")


def pylance_permissive():
    """Pylance를 permissive 모드로 설정 (추천)"""
    update_pylance_settings_with_mode("permissive")


def pylance_off():
    """Pylance 타입 체크 완전 비활성화"""
    update_pylance_settings_with_mode("disabled")


# 편의 함수 별칭들
ignore_types = pylance_permissive
no_typecheck = pylance_off
strict_types = pylance_strict


print("🔧 언리얼 엔진 Python 통합 개발환경 설정 모듈 로드됨")
print("   💡 사용법:")
print("     dev_env_setup.setup_all()        - VSCode + PyCharm 전체 설정")
print("     dev_env_setup.setup_vscode()     - VSCode만 설정")  
print("     dev_env_setup.setup_pycharm()    - PyCharm만 설정")
print("     dev_env_setup.ignore_types()     - 타입 에러 무시 (추천)")
print("     dev_env_setup.strict_types()     - 엄격한 타입 체크")
print("     dev_env_setup.no_typecheck()     - 타입 체크 완전 비활성화")