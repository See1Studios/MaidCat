# ============================================================================
# vscode_setup - VSCode 환경 설정 자동화 모듈
# ============================================================================
"""
VSCode Python 개발 환경 설정을 자동화하는 모듈
- 프로젝트 VSCode 설정 관리
- 플러그인 VSCode 설정 관리
- Python 경로 자동 계산 및 설정
- Pylance 타입 체크 설정 관리

사용법:
    # 기본 설정 (permissive 모드)
    import vscode_setup
    vscode_setup.setup_vscode()
    
    # Pylance 타입 설정만 변경
    vscode_setup.pylance_permissive()  # 추천: 외부 라이브러리 사용 시
    vscode_setup.pylance_strict()      # 엄격한 타입 체크
    vscode_setup.pylance_off()         # 타입 체크 완전 비활성화
    
    # 편의 함수들
    vscode_setup.ignore_types()        # = pylance_permissive()
    vscode_setup.no_typecheck()        # = pylance_off()
    vscode_setup.strict_types()        # = pylance_strict()
"""

import json
import unreal
from pathlib import Path


# ============================================================================
# 경로 생성 함수들
# ============================================================================


def _get_standard_python_paths():
    """표준 언리얼 Python 경로들 반환"""
    return [
        ("./Intermediate/PythonStub", "Unreal Python stub"),
        ("./TA/TAPython/Python", "TA Python scripts"),
        ("./TA/TAPython/Lib/site-packages", "TA Python libraries"),
        ("./Content/Python", "Project Content Python"),
        ("./Content/Python/Lib/site-packages", "Project Content Python libraries")
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


# ============================================================================
# Pylance 타입 설정 관리
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


def update_pylance_settings(mode="permissive"):
    """Pylance 타입 설정 업데이트
    
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
    existing_settings = _load_existing_settings(settings_path)
    
    # Pylance 설정만 업데이트
    existing_settings.update(pylance_settings)
    
    # 설정 저장
    _save_settings(settings_path, existing_settings)


# ============================================================================
# VSCode 설정 파일 관리
# ============================================================================

def _load_existing_settings(settings_path):
    """기존 VSCode 설정 로드"""
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"   ⚠️  기존 설정 읽기 실패: {e}")
        return {}


def _save_settings(settings_path, settings):
    """VSCode 설정 파일 저장"""
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def _get_unreal_python_interpreter():
    """언리얼 엔진 Python 인터프리터 경로 자동 감지 (레지스트리 기반)"""
    try:
        import winreg
        
        # 프로젝트 파일에서 엔진 연결 정보 읽기
        project_path = Path(unreal.Paths.project_dir())
        uproject_files = list(project_path.glob("*.uproject"))
        
        if uproject_files:
            with open(uproject_files[0], 'r', encoding='utf-8') as f:
                import json
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
        
    except Exception as e:
        print(f"   ❌ 언리얼 Python 인터프리터 감지 실패: {e}")
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


def _create_python_settings(python_paths, pylance_mode="permissive"):
    """Python 설정 딕셔너리 생성
    
    Args:
        python_paths: Python 경로 리스트
        pylance_mode: "strict", "permissive", "disabled" 중 하나
    """
    settings = {
        "python.analysis.extraPaths": python_paths,
        "python.autoComplete.extraPaths": python_paths,
        "python.envFile": "${workspaceFolder}/.env",
        "python.languageServer": "Pylance"
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


def update_vscode_settings_file(settings_path, python_paths):
    """VSCode 설정 파일 업데이트 (공통 함수)"""
    print(f"   📁 VSCode 설정: {settings_path}")
    
    # 기존 설정 로드 및 업데이트
    existing_settings = _load_existing_settings(settings_path)
    new_settings = _create_python_settings(python_paths)
    existing_settings.update(new_settings)
    
    # 설정 저장
    _save_settings(settings_path, existing_settings)
    print(f"   ✅ 설정 완료 ({len(python_paths)} paths)")


# ============================================================================
# 메인 설정 함수들
# ============================================================================

def update_project_vscode_settings(plugin_path, project_path):
    """프로젝트의 VSCode 설정 업데이트"""
    print(f"\n   📁 프로젝트 VSCode 설정 시작")
    
    python_paths = get_project_python_paths(plugin_path, project_path)
    settings_path = project_path / ".vscode" / "settings.json"
    update_vscode_settings_file(settings_path, python_paths)


def create_plugin_vscode_settings(settings_path, project_path):
    """플러그인 VSCode 설정 파일 생성"""
    print(f"\n   📁 플러그인 VSCode 설정 시작")
    
    python_paths = get_plugin_python_paths(project_path)
    update_vscode_settings_file(settings_path, python_paths)


def update_all_vscode_settings():
    """VSCode 설정 자동 업데이트 (프로젝트 + 플러그인)"""
    print("\n⚙️  VSCode 설정 업데이트 시작...")
    
    try:
        # 경로 정보 수집
        project_path, current_plugin_path, resolved_plugin_path = _get_paths()
        
        # 디버그 정보 출력
        _print_debug_info(project_path, current_plugin_path, resolved_plugin_path)
        
        # 플러그인 위치에 따른 설정 업데이트
        if _is_plugin_in_project(resolved_plugin_path, project_path):
            _update_project_only(current_plugin_path, project_path)
        else:
            _update_project_and_plugin(current_plugin_path, project_path, resolved_plugin_path)
            
    except Exception as e:
        print(f"   ❌ VSCode 설정 실패: {e}")
        import traceback
        traceback.print_exc()


def _get_paths():
    """필요한 경로들 수집"""
    project_path = Path(unreal.Paths.project_dir())
    current_file = Path(__file__)
    current_plugin_path = current_file.parent.parent.parent.parent.parent  # MaidCat 폴더
    resolved_plugin_path = current_plugin_path.resolve()
    
    return project_path, current_plugin_path, resolved_plugin_path


def _print_debug_info(project_path, current_plugin_path, resolved_plugin_path):
    """디버그 정보 출력"""
    print(f"   🔍 프로젝트: {project_path}")
    print(f"   🔍 플러그인: {current_plugin_path}")
    print(f"   🔍 실제 경로: {resolved_plugin_path}")
    print(f"   🔍 심볼릭 링크: {current_plugin_path.is_symlink()}")


def _is_plugin_in_project(resolved_plugin_path, project_path):
    """플러그인이 프로젝트 내부에 있는지 확인"""
    return resolved_plugin_path.is_relative_to(project_path.resolve())


def _update_project_only(current_plugin_path, project_path):
    """프로젝트 설정만 업데이트"""
    print(f"   📁 프로젝트 내부 플러그인 감지")
    update_project_vscode_settings(current_plugin_path, project_path)


def _update_project_and_plugin(current_plugin_path, project_path, resolved_plugin_path):
    """프로젝트 + 플러그인 설정 모두 업데이트"""
    plugin_dev_root = resolved_plugin_path.parent
    print(f"   🔧 독립 개발 폴더: {plugin_dev_root}")
    
    # 프로젝트 설정
    update_project_vscode_settings(current_plugin_path, project_path)
    
    # 플러그인 설정
    settings_path = plugin_dev_root / ".vscode" / "settings.json"
    create_plugin_vscode_settings(settings_path, project_path)


# ============================================================================
# 공개 API
# ============================================================================

def setup_vscode():
    """VSCode 환경 설정 메인 함수 (permissive 모드)"""
    update_all_vscode_settings()


def setup_vscode_strict():
    """VSCode 환경 설정 (strict 타입 체크 모드)"""
    print("\n⚙️  VSCode 설정 업데이트 (strict 모드)...")
    update_all_vscode_settings()
    update_pylance_settings("strict")


def setup_vscode_permissive():
    """VSCode 환경 설정 (permissive 타입 체크 모드) - 기본값"""
    print("\n⚙️  VSCode 설정 업데이트 (permissive 모드)...")
    update_all_vscode_settings()
    update_pylance_settings("permissive")


def setup_vscode_no_typecheck():
    """VSCode 환경 설정 (타입 체크 비활성화 모드)"""
    print("\n⚙️  VSCode 설정 업데이트 (타입 체크 비활성화)...")
    update_all_vscode_settings()
    update_pylance_settings("disabled")


def pylance_strict():
    """Pylance를 strict 모드로 설정"""
    update_pylance_settings("strict")


def pylance_permissive():
    """Pylance를 permissive 모드로 설정 (추천)"""
    update_pylance_settings("permissive")


def pylance_off():
    """Pylance 타입 체크 완전 비활성화"""
    update_pylance_settings("disabled")


# 편의 함수 별칭들
ignore_types = pylance_permissive
no_typecheck = pylance_off
strict_types = pylance_strict


print("🔧 VSCode setup module loaded with Pylance type control.")
print("   💡 사용법: vscode_setup.ignore_types() - 타입 에러 무시")