# ============================================================================
# test_tapython_installer.py - TAPython 설치 기능 테스트
# ============================================================================
"""
TAPython 자동 설치 기능 테스트 스크립트
"""

import unreal
from tool.tapython_installer import (
    is_tapython_installed,
    get_latest_release_info,
    check_and_install_tapython,
    test_installation_check,
    test_github_api
)


def main():
    """메인 테스트 함수"""
    print("\n" + "="*70)
    print("TAPython 자동 설치 기능 테스트")
    print("="*70)
    
    # 1. 설치 상태 확인
    print("\n[1] TAPython 설치 상태 확인")
    test_installation_check()
    
    # 2. GitHub API 테스트
    print("\n[2] GitHub API 테스트")
    test_github_api()
    
    # 3. 실제 설치 여부 확인 (실제 설치는 하지 않음)
    print("\n[3] 설치 확인 (자동 설치 테스트는 주석 처리)")
    print(f"현재 설치 여부: {is_tapython_installed()}")
    
    # 실제 설치를 원하면 아래 주석 해제
    # check_and_install_tapython()
    
    print("\n" + "="*70)
    print("테스트 완료!")
    print("실제 설치를 원하면 check_and_install_tapython() 함수를 호출하세요.")
    print("="*70)


if __name__ == "__main__":
    main()
