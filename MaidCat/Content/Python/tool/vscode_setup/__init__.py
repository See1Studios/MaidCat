# ============================================================================
# vscode_setup - VSCode 환경 설정 자동화 모듈
# ============================================================================
"""
VSCode Python 개발 환경 설정을 자동화하는 모듈
- 프로젝트 VSCode 설정 관리
- 플러그인 VSCode 설정 관리
- Python 경로 자동 계산 및 설정
"""

import json
import unreal
from pathlib import Path


def get_plugin_path():
    """플러그인 경로 반환 (실제 개발 경로의 MaidCat 폴더)"""
    # 현재 파일 위치를 기준으로 플러그인 경로 계산
    current_file = Path(__file__)
    # vscode_setup/__init__.py -> vscode_setup -> tool -> Python -> Content -> MaidCat
    plugin_maidcat_path = current_file.parent.parent.parent.parent.parent
    
    # 실제 경로로 해결 (심볼릭 링크 추적)
    real_plugin_path = plugin_maidcat_path.resolve()
    
    return real_plugin_path  # 실제 MaidCat 폴더 반환


def update_project_vscode_settings(plugin_path, project_path):
    """프로젝트의 VSCode 설정 업데이트"""
    settings_path = project_path / ".vscode" / "settings.json"
    print(f"\n   📁 프로젝트 VSCode 설정 업데이트: {settings_path}")
    
    # .vscode 폴더 생성
    if not settings_path.parent.exists():
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"   📂 .vscode 폴더 생성됨: {settings_path.parent}")
    
    # 기존 설정 읽기
    settings = {}
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            print(f"   ⚠️  기존 설정 읽기 실패, 새로 생성: {e}")
            settings = {}
    
    # 프로젝트 기준 Python 경로들
    python_paths = []
    
    # Unreal Python Stub 경로
    stub_path = "./Intermediate/PythonStub"
    python_paths.append(stub_path)
    stub_exists = (project_path / "Intermediate" / "PythonStub").exists()
    print(f"   {'✅' if stub_exists else '⚠️'} Unreal Python stub: {stub_path}")
    
    # TA Python 경로들
    ta_paths = ["./TA/TAPython/Python", "./TA/TAPython/Lib/site-packages"]
    for ta_path in ta_paths:
        python_paths.append(ta_path)
        ta_exists = (project_path / ta_path.replace("./", "")).exists()
        print(f"   {'✅' if ta_exists else '⚠️'} TA Python: {ta_path}")
    
    # Content Python 경로
    content_path = "./Content/Python"
    python_paths.append(content_path)
    content_exists = (project_path / "Content" / "Python").exists()
    print(f"   {'✅' if content_exists else '⚠️'} Content Python: {content_path}")
    
    # Content Python 라이브러리 경로
    content_lib_path = "./Content/Python/Lib/site-packages"
    python_paths.append(content_lib_path)
    content_lib_exists = (project_path / "Content" / "Python" / "Lib" / "site-packages").exists()
    print(f"   {'✅' if content_lib_exists else '⚠️'} Content Python libraries: {content_lib_path}")
    
    # 플러그인 경로들 (상대 경로로 변환)
    try:
        plugin_relative = plugin_path.resolve().relative_to(project_path.resolve())
        plugin_paths = [
            str(plugin_relative / "Content" / "Python").replace("\\", "/"),
            str(plugin_relative / "Content" / "Python" / "Lib" / "site-packages").replace("\\", "/")
        ]
        python_paths.extend(plugin_paths)
        print(f"   ✅ Plugin paths (relative): {plugin_paths}")
    except ValueError:
        # 플러그인이 프로젝트 외부에 있는 경우
        plugin_paths = [
            str(plugin_path / "Content" / "Python"),
            str(plugin_path / "Content" / "Python" / "Lib" / "site-packages")
        ]
        python_paths.extend(plugin_paths)
        print(f"   ✅ Plugin paths (absolute): {plugin_paths}")
    
    # 설정 업데이트
    settings.update({
        "python.analysis.extraPaths": python_paths,
        "python.autoComplete.extraPaths": python_paths,
        "python.envFile": "${workspaceFolder}/.env"
    })
    
    # 파일 저장
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    print(f"   ✅ 프로젝트 VSCode 설정 업데이트 완료 ({len(python_paths)} paths)")






def update_all_vscode_settings():
    """VSCode 설정 자동 업데이트 (프로젝트 + 플러그인)"""
    print("\n⚙️  Updating VSCode settings...")
    
    try:
        # 현재 실행 중인 파일의 경로 분석
        current_file = Path(__file__)
        current_plugin_path = current_file.parent.parent.parent.parent.parent  # MaidCat 폴더
        
        # 경로 디버깅
        print(f"   🔍 Current file: {current_file}")
        print(f"   🔍 Current plugin path: {current_plugin_path}")
        print(f"   🔍 Is symlink: {current_plugin_path.is_symlink()}")
        print(f"   🔍 Resolved path: {current_plugin_path.resolve()}")
        
        project_path = Path(unreal.Paths.project_dir())
        
        # 실제 개발 폴더 경로 결정
        # 현재 경로가 프로젝트 내부(Plugins 폴더)에 있으면 심볼릭 링크로 간주
        if "Plugins" in str(current_plugin_path):
            # 심볼릭 링크 경로인 경우: 실제 개발 경로를 하드코딩으로 계산
            plugin_dev_root = Path("D:/GitHub/MaidCat")
            print(f"   🔗 프로젝트 내 플러그인 경로 감지, 개발 폴더로 변경: {plugin_dev_root}")
        else:
            # 이미 개발 폴더에서 실행 중인 경우
            plugin_dev_root = current_plugin_path.parent
            print(f"   📁 개발 폴더에서 직접 실행 중: {plugin_dev_root}")
        
        print(f"   🔧 Plugin Dev Root: {plugin_dev_root}")
        print(f"   🔧 Project Path: {project_path}")
        
        # === 1. 프로젝트 VSCode 설정 업데이트 ===
        update_project_vscode_settings(current_plugin_path, project_path)
        
        # === 2. 플러그인 VSCode 설정 업데이트 ===  
        # 실제 개발 폴더에 VSCode 설정 생성
        settings_path = plugin_dev_root / ".vscode" / "settings.json"
        print(f"   📁 플러그인 VSCode 설정 업데이트: {settings_path}")
        
        # .vscode 폴더 생성
        if not settings_path.parent.exists():
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"   📂 .vscode 폴더 생성됨: {settings_path.parent}")
        
        # 플러그인 VSCode 설정 생성
        create_plugin_vscode_settings(settings_path, project_path)
        
    except Exception as e:
        print(f"   ❌ VSCode 설정 업데이트 실패: {e}")
        import traceback
        traceback.print_exc()


def create_plugin_vscode_settings(settings_path, project_path):
    """플러그인 VSCode 설정 파일 생성 (플러그인은 상대, 프로젝트는 절대 경로)"""
    # Python 경로 리스트 생성
    python_paths = []
    
    # === 플러그인 자체 경로 (상대 경로) ===
    plugin_paths = [
        "./MaidCat/Content/Python",
        "./MaidCat/Content/Python/Lib/site-packages"
    ]
    python_paths.extend(plugin_paths)
    print(f"   ✅ 플러그인 경로들 (상대 경로): {plugin_paths}")
    
    # === 프로젝트 경로들 (절대 경로) ===
    project_paths_info = [
        (project_path / "Intermediate" / "PythonStub", "Unreal Python stub"),
        (project_path / "TA" / "TAPython" / "Python", "TA Python scripts"),
        (project_path / "TA" / "TAPython" / "Lib" / "site-packages", "TA Python libraries"),
        (project_path / "Content" / "Python", "Project Content Python"),
        (project_path / "Content" / "Python" / "Lib" / "site-packages", "Project Content Python libraries")
    ]
    
    project_paths = []
    for abs_path, description in project_paths_info:
        path_str = str(abs_path).replace("\\", "/")  # Windows 경로 정규화
        python_paths.append(path_str)
        project_paths.append(path_str)
        exists = abs_path.exists()
        print(f"   {'✅' if exists else '⚠️'} {description}: {path_str}")
    
    print(f"   ✅ Python 경로들 총 {len(python_paths)} paths (플러그인: 상대, 프로젝트: 절대)")
    
    # 기존 설정과 병합
    existing = {}
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception as e:
            print(f"   ⚠️  기존 플러그인 설정 읽기 실패: {e}")
    
    # 플러그인 전용 설정
    plugin_settings = {
        "python.analysis.extraPaths": python_paths,
        "python.autoComplete.extraPaths": python_paths,
        "python.envFile": "${workspaceFolder}/.env",
        "files.associations": {
            "*.uplugin": "jsonc",
            "*.uproject": "jsonc"
        }
    }
    
    # 기존 설정과 병합
    existing.update(plugin_settings)
    
    # 파일 저장
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)
    
    print(f"   ✅ 플러그인 VSCode 설정 업데이트 완료")


# 편의 함수들
def setup_vscode():
    """VSCode 환경 설정 메인 함수"""
    update_all_vscode_settings()


print("VSCode setup module loaded.")