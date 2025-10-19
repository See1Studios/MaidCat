"""
Unreal Engine VSCode Settings Generator
언리얼 엔진 프로젝트의 Python 경로를 자동으로 감지하여 VSCode settings.json 생성
"""

import json
from pathlib import Path
import sys

# 언리얼 엔진 모듈 import (에디터 내에서 실행 시)
try:
    import unreal
    RUNNING_IN_UNREAL = True
except ImportError:
    RUNNING_IN_UNREAL = False


def find_unreal_project_root():
    """현재 디렉토리에서 .uproject 파일을 찾아 프로젝트 루트 반환"""
    
    # 언리얼 에디터 내에서 실행 중이면 프로젝트 경로 직접 가져오기
    if RUNNING_IN_UNREAL:
        try:
            project_dir = unreal.Paths.project_dir()
            project_path = Path(project_dir)
            uproject_files = list(project_path.glob("*.uproject"))
            if uproject_files:
                return project_path, uproject_files[0]
        except Exception as e:
            print(f"⚠️  언리얼 API로 프로젝트 경로 가져오기 실패: {e}")
    
    # 일반 Python 환경에서 실행 시 현재 디렉토리부터 탐색
    current = Path.cwd()
    
    # 현재 디렉토리부터 상위로 올라가며 .uproject 파일 찾기
    # Content/Python 폴더에서 실행해도 프로젝트 루트까지 올라감
    search_paths = [current] + list(current.parents)
    
    for path in search_paths:
        uproject_files = list(path.glob("*.uproject"))
        if uproject_files:
            return path, uproject_files[0]
    
    return None, None


def find_python_paths(project_root):
    """프로젝트 내 Python 관련 경로 찾기"""
    paths = []
    
    # Intermediate/PythonStub 폴더 찾기 (언리얼 엔진 스텁)
    python_stub = project_root / "Intermediate" / "PythonStub"
    if python_stub.exists():
        paths.append(str(python_stub))
        print(f"   ✅ 언리얼 스텁 발견: {python_stub}")
    
    # Content/Python 폴더 찾기
    content_python = project_root / "Content" / "Python"
    if content_python.exists():
        paths.append(str(content_python))
        
        # Content/Python 하위 폴더들도 추가 (패키지들)
        for subdir in content_python.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                # __pycache__ 등 제외
                if subdir.name != "__pycache__":
                    paths.append(str(subdir))
    
    # Intermediate/PipInstall/Lib/site-packages 찾기 (pip으로 설치한 패키지)
    pip_site_packages = project_root / "Intermediate" / "PipInstall" / "Lib" / "site-packages"
    if pip_site_packages.exists():
        paths.append(str(pip_site_packages))
        print(f"   ✅ PipInstall Site-packages 발견: {pip_site_packages}")
    
    # Python/Lib/site-packages 찾기 (프로젝트 루트 레벨)
    python_site_packages = project_root / "Python" / "Lib" / "site-packages"
    if python_site_packages.exists():
        paths.append(str(python_site_packages))
        print(f"   ✅ Site-packages 발견: {python_site_packages}")
    
    # Content/Python/Lib/site-packages 찾기
    content_site_packages = project_root / "Content" / "Python" / "Lib" / "site-packages"
    if content_site_packages.exists():
        paths.append(str(content_site_packages))
        print(f"   ✅ Content Site-packages 발견: {content_site_packages}")
    
    # TA/TAPython/Python 찾기 (TA 툴 루트)
    ta_python = project_root / "TA" / "TAPython" / "Python"
    if ta_python.exists():
        paths.append(str(ta_python))
        print(f"   ✅ TA Python 발견: {ta_python}")
    
    # TA/TAPython/Lib/site-packages 찾기
    ta_site_packages = project_root / "TA" / "TAPython" / "Lib" / "site-packages"
    if ta_site_packages.exists():
        paths.append(str(ta_site_packages))
        print(f"   ✅ TA Site-packages 발견: {ta_site_packages}")
    
    # Plugins 폴더 내 Python 경로들 찾기
    plugins_dir = project_root / "Plugins"
    if plugins_dir.exists():
        for plugin in plugins_dir.iterdir():
            if plugin.is_dir():
                plugin_python = plugin / "Content" / "Python"
                if plugin_python.exists():
                    paths.append(str(plugin_python))
    
    return paths


def find_unreal_engine_paths():
    """언리얼 엔진 설치 경로에서 Python 경로 찾기 (선택사항)"""
    paths = []
    
    # 일반적인 언리얼 엔진 설치 경로들
    common_paths = [
        Path("C:/Program Files/Epic Games"),
        Path.home() / "Program Files/Epic Games",
        Path("/Applications/Epic Games") if sys.platform == "darwin" else None,
    ]
    
    for base_path in common_paths:
        if base_path and base_path.exists():
            for ue_dir in base_path.glob("UE_*"):
                engine_python = ue_dir / "Engine" / "Content" / "Python"
                if engine_python.exists():
                    paths.append(str(engine_python))
                    break  # 첫 번째만 추가
    
    return paths


def generate_vscode_settings(project_root, python_paths, include_engine=False):
    """VSCode settings.json 생성"""
    
    # 상대 경로로 변환 (workspace 기준)
    relative_paths = []
    for path in python_paths:
        try:
            rel_path = Path(path).relative_to(project_root)
            relative_paths.append(f"${{workspaceFolder}}/{rel_path.as_posix()}")
        except ValueError:
            # 프로젝트 외부 경로는 절대 경로 사용
            relative_paths.append(str(Path(path).as_posix()))
    
    # Intermediate/PythonStub을 stubPath로 설정
    stub_path = project_root / "Intermediate" / "PythonStub"
    stub_path_relative = None
    if stub_path.exists():
        try:
            rel_stub = stub_path.relative_to(project_root)
            stub_path_relative = f"${{workspaceFolder}}/{rel_stub.as_posix()}"
        except ValueError:
            stub_path_relative = str(stub_path.as_posix())
    
    settings = {
        "python.autoComplete.extraPaths": relative_paths,
        "python.analysis.extraPaths": relative_paths,
        "python.languageServer": "Pylance",
        "python.analysis.typeCheckingMode": "basic",
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit"
            }
        },
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True
        }
    }
    
    # stubPath 추가 (있는 경우)
    if stub_path_relative:
        settings["python.analysis.stubPath"] = stub_path_relative
    
    return settings


def create_vscode_directory(project_root):
    """프로젝트에 .vscode 디렉토리 생성"""
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    return vscode_dir


def save_settings(vscode_dir, settings):
    """settings.json 저장 (덮어쓰기)"""
    settings_file = vscode_dir / "settings.json"
    
    # 설정 저장
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    return settings_file


def main(include_engine=False, auto_create_folder=True):
    """
    VSCode 설정 자동 생성
    
    Parameters:
    - include_engine: 언리얼 엔진 Python 경로 포함 여부 (기본: False)
    - auto_create_folder: Content/Python 폴더 자동 생성 여부 (기본: True)
    """
    print("=" * 60)
    print("Unreal Engine VSCode Settings Generator")
    print("=" * 60)
    
    if RUNNING_IN_UNREAL:
        print("\n🎮 언리얼 엔진 에디터에서 실행 중")
    else:
        print("\n🐍 Python 환경에서 실행 중")
        print(f"📂 현재 위치: {Path.cwd()}")
    
    # 1. 프로젝트 루트 찾기
    project_root, uproject_file = find_unreal_project_root()
    
    if not project_root:
        print("\n❌ 언리얼 엔진 프로젝트를 찾을 수 없습니다.")
        if RUNNING_IN_UNREAL:
            print("   프로젝트가 제대로 로드되지 않았거나 API 오류가 발생했습니다.")
        else:
            print("   .uproject 파일이 있는 디렉토리 또는 하위 폴더에서 실행해주세요.")
        return
    
    print(f"\n📁 프로젝트 발견: {uproject_file.name}")
    print(f"   프로젝트 루트: {project_root}")
    
    # 2. Python 경로 찾기
    print("\n🔍 Python 경로 검색 중...")
    python_paths = find_python_paths(project_root)
    
    if not python_paths:
        print("   ⚠️  Content/Python 폴더를 찾을 수 없습니다.")
        
        if RUNNING_IN_UNREAL or auto_create_folder:
            # 언리얼 에디터에서 실행 중이거나 auto_create_folder=True면 자동 생성
            content_python = project_root / "Content" / "Python"
            content_python.mkdir(parents=True, exist_ok=True)
            python_paths.append(str(content_python))
            print(f"   ✅ 폴더 자동 생성: {content_python}")
        else:
            # 일반 Python 환경에서 실행 시 사용자에게 물어보기
            try:
                create = input("   Content/Python 폴더를 생성하시겠습니까? (y/n): ")
                if create.lower() == 'y':
                    content_python = project_root / "Content" / "Python"
                    content_python.mkdir(parents=True, exist_ok=True)
                    python_paths.append(str(content_python))
                    print(f"   ✅ 폴더 생성: {content_python}")
                else:
                    print("   설정을 생성하지 않고 종료합니다.")
                    return
            except (RuntimeError, EOFError):
                # input()을 사용할 수 없는 환경
                content_python = project_root / "Content" / "Python"
                content_python.mkdir(parents=True, exist_ok=True)
                python_paths.append(str(content_python))
                print(f"   ✅ 폴더 자동 생성: {content_python}")
    
    print("\n📍 발견된 Python 경로:")
    for path in python_paths:
        print(f"   • {path}")
    
    # 3. 엔진 경로 포함 여부
    if include_engine:
        print("\n🔍 언리얼 엔진 Python 경로 검색 중...")
        engine_paths = find_unreal_engine_paths()
        if engine_paths:
            print("📍 엔진 Python 경로:")
            for path in engine_paths:
                print(f"   • {path}")
            python_paths.extend(engine_paths)
        else:
            print("   ⚠️  엔진 Python 경로를 찾을 수 없습니다.")
    
    # 4. VSCode 설정 생성
    print("\n⚙️  VSCode 설정 생성 중...")
    settings = generate_vscode_settings(project_root, python_paths)
    
    # 5. .vscode 디렉토리 생성
    vscode_dir = create_vscode_directory(project_root)
    
    # 6. 설정 파일 저장
    settings_file = save_settings(vscode_dir, settings)
    
    print(f"\n✅ 설정 파일 생성 완료!")
    print(f"   📄 {settings_file}")
    print("\n💡 VSCode를 재시작하면 Python 인텔리센스가 활성화됩니다.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # 언리얼 에디터에서 실행 시 자동 모드
        if RUNNING_IN_UNREAL:
            main(include_engine=False, auto_create_folder=True)
        else:
            # 일반 Python 환경에서는 인터랙티브 모드 가능
            main()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()