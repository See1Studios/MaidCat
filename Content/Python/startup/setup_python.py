"""
Unreal Engine Development Environment Setup
언리얼 엔진 Python 개발 환경 통합 설정 스크립트
- VSCode + PyCharm 설정 자동화
- dev_env_setup 통합 모듈의 래퍼

이 모듈은 dev_env_setup 통합 모듈의 래퍼입니다.
"""

import unreal
from pathlib import Path
import sys
import importlib

# 통합 개발 환경 설정 모듈 import (강제 리로드)
import tool.dev_env_setup
if 'tool.dev_env_setup' in sys.modules:
    importlib.reload(tool.dev_env_setup)

def copy_copilot_instructions():
    """플러그인의 GitHub Copilot 지침 파일을 프로젝트 루트로 복사"""
    try:
        import shutil
        
        # __file__을 resolve하여 실제 경로 획득 (심볼릭 링크 환경 대응)
        current_file_path = Path(__file__).resolve()
        
        # .github/copilot-instructions.md 파일을 상위 디렉토리에서 검색
        search_path = current_file_path
        repo_root = None
        
        for _ in range(10):  # 최대 10단계까지 상위로 검색
            search_path = search_path.parent
            candidate = search_path / ".github" / "copilot-instructions.md"
            
            if candidate.exists():
                repo_root = search_path
                break
            
            # 루트 디렉토리에 도달하면 중단
            if search_path.parent == search_path:
                break
        
        if repo_root is None:
            return  # 조용히 실패 (필수 기능 아님)
        
        project_path = Path(unreal.Paths.project_dir())
        source_file = repo_root / ".github" / "copilot-instructions.md"
        target_dir = project_path / ".github"
        target_file = target_dir / "copilot-instructions.md"
        
        # .github 폴더가 없으면 생성
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일 복사 (이미 있으면 덮어쓰기)
        shutil.copy2(source_file, target_file)
        print(f"   ✅ Copilot 지침 복사: {target_file}")
        
    except Exception:
        pass  # 조용히 실패 (필수 기능 아님)

def main(setup_mode="all"):
    """
    언리얼 엔진 개발 환경 설정 (통합 버전)
    
    Parameters:
    - setup_mode: 설정 모드 - "all"(VSCode+PyCharm), "vscode", "pycharm" (기본: "all")
    """
    print("=" * 60)
    print("Unreal Engine Development Environment Setup")
    print("언리얼 엔진 Python 개발 환경 통합 설정")
    print("=" * 60)
    
    print("\n🎮 언리얼 엔진 에디터에서 실행 중")
    print(f"\n⚙️  통합 개발 환경 설정 모드: {setup_mode}")
    
    # GitHub Copilot 지침 파일 복사 (프로젝트 작업 공간 지원)
    print("\n📋 GitHub Copilot 지침 파일 복사 중...")
    copy_copilot_instructions()
    
    try:
        if setup_mode == "all":
            tool.dev_env_setup.setup_all()  # VSCode + PyCharm 전체 설정
        elif setup_mode == "vscode":
            tool.dev_env_setup.setup_vscode()  # VSCode만
        elif setup_mode == "pycharm":
            tool.dev_env_setup.setup_pycharm()  # PyCharm만
        else:
            print(f"   ❌ 알 수 없는 모드: {setup_mode}")
            print("   💡 사용 가능한 모드: all, vscode, pycharm")
            return
        
        print("\n✅ 통합 개발 환경 설정 완료!")
        print("   📝 VSCode와 PyCharm에서 언리얼 엔진 Python 개발이 가능합니다.")
        print("   💡 IDE를 재시작하면 새 설정이 적용됩니다.")
        print("=" * 60)
        
    except Exception as e:
        print(f"   ❌ 설정 실패: {e}")
        import traceback
        traceback.print_exc()


# 편의 함수들 (직접 호출용)
def setup_all_dev_env():
    """VSCode + PyCharm 전체 개발 환경 설정"""
    tool.dev_env_setup.setup_all()


def setup_vscode_only():
    """VSCode만 설정"""
    tool.dev_env_setup.setup_vscode()


def setup_pycharm_only():
    """PyCharm만 설정"""
    tool.dev_env_setup.setup_pycharm()


def setup_with_strict_types():
    """엄격한 타입 체크 모드로 설정"""
    tool.dev_env_setup.setup_all_with_mode("strict")
    print("   ✅ 엄격한 타입 체크 모드로 설정됨")


def disable_type_checking():
    """타입 체크 완전 비활성화"""
    tool.dev_env_setup.pylance_off()
    print("   ✅ 타입 체크가 비활성화됨")


# 사용법 안내
def show_usage():
    """사용법 안내"""
    print("=" * 60)
    print("언리얼 엔진 Python 개발 환경 설정 사용법")
    print("=" * 60)
    print("\n📋 기본 사용법:")
    print("   import setup_python")
    print("   setup_python.setup_all_dev_env()      # VSCode + PyCharm 전체 설정")
    print("   setup_python.setup_vscode_only()      # VSCode만 설정")
    print("   setup_python.setup_pycharm_only()     # PyCharm만 설정")
    print("\n🔧 고급 설정:")
    print("   setup_python.setup_with_strict_types() # 엄격한 타입 체크")
    print("   setup_python.disable_type_checking()   # 타입 체크 비활성화")
    print("\n📋 통합 모듈 직접 사용:")
    print("   from tool.dev_env_setup import *")
    print("   setup_all()                            # VSCode + PyCharm 전체")
    print("   setup_vscode()                         # VSCode만")
    print("   setup_pycharm()                        # PyCharm만") 
    print("   ignore_types()                         # 타입 에러 무시")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # 언리얼 에디터에서 실행 시 통합 모드 (VSCode + PyCharm)
        import sys
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            if mode in ["all", "vscode", "pycharm"]:
                main(setup_mode=mode)
            else:
                print("사용법: python setup_python.py [all|vscode|pycharm]")
        else:
            main(setup_mode="all")  # 기본값: 전체 설정
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()