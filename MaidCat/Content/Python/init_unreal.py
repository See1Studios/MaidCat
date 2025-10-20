# ============================================================================
# init_unreal.py - MaidCat 플러그인 초기화 스크립트
# ============================================================================
"""
MaidCat 플러그인 시작 시 실행되는 메인 초기화 스크립트
- 의존성 패키지 설치
- Python 경로 설정 (sys.path)
- VSCode 설정 자동 업데이트
"""

import sys
import unreal
from pathlib import Path

print("\n🐱 MaidCat Plugin 초기화 시작...")

# ============================================================================
# 의존성 설치
# ============================================================================

try:
    from tool import dependencies_installer
    dependencies_installer.install_dependencies()
except ImportError as e:
    print(f"⚠️  dependencies_installer를 찾을 수 없습니다: {e}")
except Exception as e:
    print(f"❌ 의존성 설치 중 오류 발생: {e}")

# ============================================================================
# VSCode 설정
# ============================================================================

try:
    from tool import vscode_setup
    vscode_setup.setup_vscode()
except ImportError as e:
    print(f"⚠️  vscode_setup 모듈을 찾을 수 없습니다: {e}")
except Exception as e:
    print(f"❌ VSCode 설정 중 오류 발생: {e}")


# ============================================================================
# Python 경로 설정 (sys.path)
# ============================================================================

def get_plugin_path():
    """플러그인 경로 반환"""
    current_file = Path(__file__)
    # init_unreal.py -> Python -> Content -> MaidCat (플러그인 루트)
    return current_file.parent.parent.parent


def add_to_sys_path(path_str, description=""):
    """sys.path에 경로 추가 (중복 방지)"""
    if path_str not in sys.path:
        sys.path.append(path_str)
        print(f"✅ sys.path 추가: {path_str}")
        if description:
            print(f"   ({description})")


def setup_python_paths():
    """플러그인 및 프로젝트 Python 경로 설정"""
    plugin_path = get_plugin_path()
    project_path = Path(unreal.Paths.project_dir())
    
    print("\n📂 Python 경로 설정 중...")
    
    # 플러그인 Python 경로
    plugin_python_path = plugin_path / "Content" / "Python"
    if plugin_python_path.exists():
        add_to_sys_path(str(plugin_python_path), "플러그인 Python")
    
    # 플러그인 라이브러리 경로
    plugin_lib_path = plugin_python_path / "Lib" / "site-packages"
    if plugin_lib_path.exists():
        add_to_sys_path(str(plugin_lib_path), "플러그인 라이브러리")
    
    # 프로젝트 Python 경로들
    project_paths = [
        (project_path / "TA" / "TAPython" / "Python", "프로젝트 TA Python"),
        (project_path / "TA" / "TAPython" / "Lib" / "site-packages", "프로젝트 TA 라이브러리"),
        (project_path / "Content" / "Python", "프로젝트 Content Python")
    ]
    
    for path, description in project_paths:
        if path.exists():
            add_to_sys_path(str(path), description)


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    """메인 초기화 함수"""
    try:
        # Python 경로 설정
        setup_python_paths()
        
        print("\n✅ MaidCat 플러그인 초기화 완료!")
        
    except Exception as e:
        print(f"\n❌ 플러그인 초기화 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()