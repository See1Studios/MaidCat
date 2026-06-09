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
import time
import platform


# ============================================================================
# 전역 캐시 변수들
# ============================================================================

_cached_unreal_python_path = None
_cached_engine_path = None
_cached_engine_association = None
_cached_project_data = None
_cached_cspell_words = None
_cached_pylance_permissive = None
_cached_pylance_strict = None
_cached_pylance_disabled = None


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
    """디버그 정보 출력 (비활성화)"""
    pass


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
    existing_count = 0
    
    # 표준 프로젝트 경로들 (상대 경로)
    for rel_path, description in _get_standard_python_paths():
        python_paths.append(rel_path)
        abs_path = project_path / rel_path.replace("./", "")
        if abs_path.exists():
            existing_count += 1
    
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
    
    # 프로젝트 경로들 (절대 경로)
    for rel_path, description in _get_standard_python_paths():
        abs_path = project_path / rel_path.replace("./", "")
        path_str = str(abs_path).replace("\\", "/")
        python_paths.append(path_str)
    
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
    except ValueError:
        # 프로젝트 외부인 경우 절대 경로 사용
        plugin_paths = [
            str(plugin_path / "Content" / "Python"),
            str(plugin_path / "Content" / "Python" / "Lib" / "site-packages")
        ]
        python_paths.extend(plugin_paths)


def _add_other_plugins_paths(python_paths, project_path):
    """다른 플러그인들의 Python 경로도 추가"""
    plugins_dir = project_path / "Plugins"
    if not plugins_dir.exists():
        return
    
    other_count = 0
    try:
        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name == "MaidCat":
                continue
            
            plugin_python = plugin_dir / "Content" / "Python"
            if plugin_python.exists():
                try:
                    plugin_relative = plugin_python.relative_to(project_path)
                    rel_path = f"./{plugin_relative}".replace("\\", "/")
                    python_paths.append(rel_path)
                    other_count += 1
                except ValueError:
                    pass
    except Exception:
        pass
        return
    
    try:
        for plugin_dir in plugins_dir.iterdir():
            if not plugin_dir.is_dir() or plugin_dir.name == "MaidCat":
                continue
            
            plugin_python = plugin_dir / "Content" / "Python"
            if plugin_python.exists():
                try:
                    plugin_relative = plugin_python.relative_to(project_path)
                    rel_path = f"./{plugin_relative}".replace("\\", "/")
                    python_paths.append(rel_path)
                    print(f"   ✅ 다른 플러그인: {rel_path}")
                except ValueError:
                    pass
    except Exception:
        pass


# ============================================================================
# 언리얼 Python 인터프리터 감지
# ============================================================================

def _get_engine_association():
    """엔진 연결 정보 가져오기 (캐싱)"""
    global _cached_engine_association, _cached_project_data
    
    if _cached_engine_association is not None:
        return _cached_engine_association
    
    try:
        project_path = Path(unreal.Paths.project_dir())
        uproject_files = list(project_path.glob("*.uproject"))
        
        if uproject_files:
            with open(uproject_files[0], 'r', encoding='utf-8') as f:
                _cached_project_data = json.load(f)
                _cached_engine_association = _cached_project_data.get("EngineAssociation", "")
                return _cached_engine_association
    except Exception:
        pass
    
    return None


def _get_unreal_python_interpreter():
    """언리얼 엔진 Python 인터프리터 경로 자동 감지 (레지스트리 기반)"""
    global _cached_unreal_python_path
    
    # 캐시된 값 반환
    if _cached_unreal_python_path is not None:
        return _cached_unreal_python_path
    
    try:
        if platform.system() != "Windows":
            return _get_unreal_python_non_windows()
        
        import winreg
        
        # 캐시된 엔진 연결 정보 사용
        engine_association = _get_engine_association()
        
        if engine_association:
                
                    # 레지스트리에서 엔진 경로 찾기
            engine_path = _get_engine_path_from_registry(engine_association)
            if engine_path:
                python_exe = Path(engine_path) / "Engine" / "Binaries" / "ThirdParty" / "Python3" / "Win64" / "python.exe"
                if python_exe.exists():
                    python_path = str(python_exe).replace("\\", "/")
                    _cached_unreal_python_path = python_path
                    return python_path
        
        # 폴백: 일반적인 경로들 시도
        result = _get_unreal_python_fallback()
        _cached_unreal_python_path = result
        return result
        
    except Exception as e:
        print(f"   ❌ 언리얼 Python 인터프리터 감지 실패: {e}")
        result = _get_unreal_python_fallback()
        _cached_unreal_python_path = result
        return result


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
    """엄격한 Pylance 타입 설정 반환 (캐싱)"""
    global _cached_pylance_strict
    if _cached_pylance_strict is not None:
        return _cached_pylance_strict
    
    _cached_pylance_strict = {
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
    return _cached_pylance_strict


def get_pylance_permissive_settings():
    """관대한 Pylance 타입 설정 반환 (외부 라이브러리 작업용, 캐싱)"""
    global _cached_pylance_permissive
    if _cached_pylance_permissive is not None:
        return _cached_pylance_permissive
    
    _cached_pylance_permissive = {
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
    return _cached_pylance_permissive


def get_pylance_disabled_settings():
    """Pylance 타입 체크 완전 비활성화 설정 (캐싱)"""
    global _cached_pylance_disabled
    if _cached_pylance_disabled is not None:
        return _cached_pylance_disabled
    
    _cached_pylance_disabled = {
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
    return _cached_pylance_disabled


def get_vscode_cspell_words():
    """언리얼 엔진용 cSpell 단어 목록 (캐싱)"""
    global _cached_cspell_words
    if _cached_cspell_words is not None:
        return _cached_cspell_words
    
    _cached_cspell_words = [
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
    return _cached_cspell_words


def _create_vscode_python_settings(python_paths, pylance_mode="permissive"):
    """VSCode Python 설정 딕셔너리 생성"""
    t_start = time.time()
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
    print(f"            ⏱️  기본 설정: {(time.time() - t_start) * 1000:.1f}ms")
    
    # Pylance 타입 설정 추가
    t0 = time.time()
    if pylance_mode == "strict":
        pylance_settings = get_pylance_strict_settings()
    elif pylance_mode == "disabled":
        pylance_settings = get_pylance_disabled_settings()
    else:  # permissive (기본값)
        pylance_settings = get_pylance_permissive_settings()
    
    settings.update(pylance_settings)
    print(f"            ⏱️  Pylance 설정: {(time.time() - t0) * 1000:.1f}ms")
    
    # 언리얼 Python 인터프리터 경로 추가
    t1 = time.time()
    unreal_python = _get_unreal_python_interpreter()
    print(f"            ⏱️  Python 인터프리터: {(time.time() - t1) * 1000:.1f}ms")
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


def _save_vscode_settings(settings_path, settings, existing_settings=None):
    """VSCode 설정 파일 저장 (변경사항이 있을 때만)"""
    # 기존 설정과 비교하여 변경사항이 없으면 건너뛰기
    if existing_settings is not None:
        # Python 관련 키만 비교 (다른 설정은 무시)
        python_keys = {
            'python.analysis.extraPaths',
            'python.autoComplete.extraPaths', 
            'python.defaultInterpreterPath',
            'python.analysis.typeCheckingMode',
            'python.analysis.diagnosticSeverityOverrides'
        }
        
        has_changes = False
        for key in python_keys:
            if settings.get(key) != existing_settings.get(key):
                has_changes = True
                break
        
        if not has_changes:
            return False  # 변경사항 없음
    
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    return True  # 저장 완료


def update_vscode_settings_file(settings_path, python_paths, pylance_mode="permissive"):
    """VSCode 설정 파일 업데이트"""
    print(f"   📁 VSCode 설정: {settings_path}")
    
    # 기존 설정 로드
    t0 = time.time()
    existing_settings = _load_existing_vscode_settings(settings_path)
    print(f"         ⏱️  로드: {(time.time() - t0) * 1000:.1f}ms")
    
    # 새 설정 생성
    t1 = time.time()
    new_settings = _create_vscode_python_settings(python_paths, pylance_mode)
    print(f"         ⏱️  설정 생성: {(time.time() - t1) * 1000:.1f}ms")
    
    # 병합
    merged_settings = existing_settings.copy()
    merged_settings.update(new_settings)
    
    # 변경사항이 있을 때만 저장
    t2 = time.time()
    saved = _save_vscode_settings(settings_path, merged_settings, existing_settings)
    elapsed = (time.time() - t2) * 1000
    
    if saved:
        print(f"         ⏱️  저장: {elapsed:.1f}ms")
        print(f"   ✅ VSCode 설정 완료 ({len(python_paths)} paths)")
    else:
        print(f"         ⏱️  비교: {elapsed:.1f}ms")
        print(f"   ✅ VSCode 설정 최신 상태 (변경사항 없음)")


# ============================================================================
# PyCharm 설정 관리 (프로젝트 작업 공간만)
# ============================================================================

def create_pycharm_project_config(project_path, python_paths):
    """PyCharm 프로젝트 설정 파일들 생성"""
    idea_dir = project_path / ".idea"
    idea_dir.mkdir(exist_ok=True)
    
    # 1. misc.xml - 프로젝트 기본 설정
    _create_pycharm_misc_xml(idea_dir)
    
    # 2. modules.xml - 모듈 설정
    _create_pycharm_modules_xml(idea_dir, project_path)
    
    # 3. [프로젝트명].iml - 모듈 파일 (Python 경로가 달라지므로 항상 생성)
    _create_pycharm_iml_file(idea_dir, project_path, python_paths)
    
    # 4. workspace.xml - 워크스페이스 설정
    _create_pycharm_workspace_xml(idea_dir)


def _create_pycharm_misc_xml(idea_dir):
    """PyCharm misc.xml 파일 생성"""
    misc_path = idea_dir / "misc.xml"
    
    # 이미 존재하면 건너뛰기
    if misc_path.exists():
        return False
    
    misc_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Unreal Python" project-jdk-type="Python SDK" />
  <component name="PyCharmProfessionalAdvertiser">
    <option name="shown" value="true" />
  </component>
</project>'''
    
    with open(misc_path, 'w', encoding='utf-8') as f:
        f.write(misc_content)
    
    return True


def _create_pycharm_modules_xml(idea_dir, project_path):
    """PyCharm modules.xml 파일 생성"""
    modules_path = idea_dir / "modules.xml"
    
    # 이미 존재하면 건너뛰기
    if modules_path.exists():
        return False
    
    project_name = project_path.name
    modules_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/{project_name}.iml" filepath="$PROJECT_DIR$/.idea/{project_name}.iml" />
    </modules>
  </component>
</project>'''
    
    with open(modules_path, 'w', encoding='utf-8') as f:
        f.write(modules_content)
    
    return True


def _create_pycharm_iml_file(idea_dir, project_path, python_paths):
    """PyCharm .iml 모듈 파일 생성"""
    project_name = project_path.name
    
    # Python 경로들을 절대 경로로 변환 (존재하는 경로만)
    content_roots = []
    
    for path in python_paths:
        if path.startswith("./"):
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
    workspace_path = idea_dir / "workspace.xml"
    
    # 이미 존재하면 건너뛰기 (workspace는 사용자 설정 포함)
    if workspace_path.exists():
        return False
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
    
    with open(workspace_path, 'w', encoding='utf-8') as f:
        f.write(workspace_content)
    
    return True


# ============================================================================
# 메인 설정 함수들
# ============================================================================

def update_project_settings():
    """프로젝트의 개발 환경 설정 업데이트 (기본: permissive 모드)"""
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        
        # VSCode 설정
        vscode_settings_path = project_path / ".vscode" / "settings.json"
        update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
        
        # PyCharm 설정
        create_pycharm_project_config(project_path, python_paths)
        
    except Exception as e:
        print(f"❌ 프로젝트 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_plugin_settings():
    """플러그인의 개발 환경 설정 업데이트 (기본: permissive 모드)"""
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # 플러그인이 프로젝트 외부에 있는 경우에만 별도 설정
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            python_paths = get_plugin_python_paths(project_path)
            
            # VSCode 설정
            vscode_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            update_vscode_settings_file(vscode_settings_path, python_paths, "permissive")
            
            # PyCharm 설정  
            create_pycharm_project_config(plugin_dev_root, python_paths)
            
    except Exception as e:
        print(f"❌ 플러그인 설정 실패: {e}")
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
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        pylance_settings = get_pylance_permissive_settings()
        
        # 프로젝트 설정 업데이트
        project_settings_path = project_path / ".vscode" / "settings.json"
        _update_pylance_in_settings_file(project_settings_path, pylance_settings)
        
        # 플러그인이 프로젝트 외부에 있는 경우 플러그인 설정도 업데이트
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            plugin_settings_path = plugin_dev_root / ".vscode" / "settings.json"
            _update_pylance_in_settings_file(plugin_settings_path, pylance_settings)
        
        print("✅ Pylance 설정 완료")
        
    except Exception as e:
        print(f"❌ Pylance 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_pylance_settings_with_mode(mode="permissive"):
    """Pylance 타입 설정 업데이트 (모드 선택 가능)
    
    Args:
        mode: "strict", "permissive", "disabled" 중 하나
    """
    try:
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
        
        print(f"✅ Pylance {mode} 모드 적용")
        
    except Exception as e:
        print(f"❌ Pylance 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def _update_pylance_in_settings_file(settings_path, pylance_settings):
    """특정 설정 파일의 Pylance 설정만 업데이트"""
    existing_settings = _load_existing_vscode_settings(settings_path)
    existing_settings.update(pylance_settings)
    _save_vscode_settings(settings_path, existing_settings)


def _check_ini_key(ini_path: Path, section: str, key: str, expected_value: str) -> bool:
    """INI 파일에서 특정 섹션/키가 기대 값으로 설정되어 있는지 확인."""
    if not ini_path.exists():
        return False
    content = ini_path.read_text(encoding="utf-8-sig")
    section_header = f"[{section}]"
    if section_header not in content:
        return False
    section_start = content.index(section_header) + len(section_header)
    next_section = content.find("\n[", section_start)
    block = content[section_start: next_section if next_section != -1 else len(content)]
    return any(
        line.strip() == f"{key}={expected_value}"
        for line in block.splitlines()
    )


def notify_engine_python_settings():
    """필수 엔진 Python 설정이 구성되지 않은 경우 사용자에게 안내 메시지를 표시."""
    project_path = Path(unreal.Paths.project_dir())
    PYTHON_SECTION = "/Script/PythonScriptPlugin.PythonScriptPluginUserSettings"

    default_engine_ini = project_path / "Config" / "DefaultEngine.ini"
    # Saved/Config 폴더는 플랫폼별로 다르나 Windows 기준으로 확인
    user_settings_ini = project_path / "Saved" / "Config" / "WindowsEditor" / "EditorPerProjectUserSettings.ini"

    required_settings = [
        (default_engine_ini,  PYTHON_SECTION, "bEnableRemoteExecution",          "True"),
        (user_settings_ini,   PYTHON_SECTION, "bDeveloperMode",                  "True"),
        (user_settings_ini,   PYTHON_SECTION, "TypeHintingMode",                 "AutoCompletion"),
        (user_settings_ini,   PYTHON_SECTION, "bEnableContentBrowserIntegration","True"),
    ]

    missing = [
        (ini, key, val)
        for ini, section, key, val in required_settings
        if not _check_ini_key(ini, section, key, val)
    ]

    if not missing:
        print("   ✔  엔진 Python 설정이 이미 올바르게 구성되어 있습니다")
        return

    message = (
        "MaidCat 플러그인을 사용하려면 다음 Python 설정이 필요합니다.\n\n"
        "편집 > 프로젝트 설정 > Plugins > Python 에서 설정하세요:\n\n"
        "  • Enable Remote Execution  (bEnableRemoteExecution=True)\n"
        "  • Developer Mode           (bDeveloperMode=True)\n"
        "  • Type Hinting Mode        → AutoCompletion\n"
        "  • Enable Content Browser   (bEnableContentBrowserIntegration=True)\n\n"
        "설정 후 에디터를 재시작하면 적용됩니다."
    )

    unreal.EditorDialog.show_message(
        unreal.Text("Python 설정 안내"),
        unreal.Text(message),
        unreal.AppMsgType.OK
    )


def update_all_settings():
    """모든 개발 환경 설정 업데이트 (VSCode + PyCharm, 기본: permissive 모드)"""
    try:
        notify_engine_python_settings()
        update_project_settings()
        update_plugin_settings()
        print("✅ 개발 환경 설정 완료")

    except Exception as e:
        print(f"❌ 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def update_all_settings_with_mode(pylance_mode="permissive"):
    """모든 개발 환경 설정 업데이트 (VSCode + PyCharm, pylance 모드 선택 가능)"""
    try:
        notify_engine_python_settings()
        update_project_settings_with_mode(pylance_mode)
        update_plugin_settings_with_mode(pylance_mode)
        print("✅ 개발 환경 설정 완료")

    except Exception as e:
        print(f"❌ 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# 공개 API
# ============================================================================

def check_tapython():
    """TAPython 플러그인 설치 확인 및 자동 설치"""
    try:
        from tool.tapython_installer import check_and_install_tapython
        return check_and_install_tapython()
    except Exception as e:
        print(f"❌ TAPython 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def setup_all():
    """모든 개발 환경 설정 (VSCode + PyCharm) - 파라미터 없음"""
    update_all_settings()


def setup_vscode():
    """VSCode 환경 설정만 - 파라미터 없음"""
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
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
        
        print("✅ VSCode 설정 완료")
        
    except Exception as e:
        print(f"❌ VSCode 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def setup_pycharm():
    """PyCharm 환경 설정만 - 파라미터 없음"""
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # 프로젝트 PyCharm 설정
        python_paths = get_project_python_paths(current_plugin_path, project_path)
        create_pycharm_project_config(project_path, python_paths)
        
        # 플러그인 PyCharm 설정 (필요한 경우)
        if not _is_plugin_in_project(resolved_plugin_path, project_path):
            plugin_dev_root = resolved_plugin_path.parent
            python_paths = get_plugin_python_paths(project_path)
            create_pycharm_project_config(plugin_dev_root, python_paths)
        
        print("✅ PyCharm 설정 완료")
        
    except Exception as e:
        print(f"❌ PyCharm 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# 고급 설정 함수들 (파라미터 필요 시에만 사용)
def setup_all_with_mode(pylance_mode="permissive"):
    """모든 개발 환경 설정 (pylance 모드 선택 가능)"""
    update_all_settings_with_mode(pylance_mode)


def setup_vscode_with_mode(pylance_mode="permissive"):
    """VSCode 환경 설정 (pylance 모드 선택 가능)"""
    try:
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
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
        
        print("✅ VSCode 설정 완료")
        
    except Exception as e:
        print(f"❌ VSCode 설정 실패: {e}")
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