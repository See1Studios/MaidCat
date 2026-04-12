"""
Unreal Engine 프로젝트 Python 패키지 관리 도구

프로젝트의 Python/Lib/site-packages에 패키지를 설치하고 관리합니다.
"""

import subprocess
import sys
import os
import unreal


# ============================================================================
# 설정
# ============================================================================

# 프로젝트 Python site-packages 경로
PROJECT_DIR = unreal.SystemLibrary.get_project_directory()
SITE_PACKAGES_DIR = os.path.join(PROJECT_DIR, "Python", "Lib", "site-packages")

# Python 실행 파일 경로
PYTHON_EXE = sys.executable


# ============================================================================
# 패키지 관리 함수
# ============================================================================

def ensure_site_packages_dir():
    """site-packages 디렉토리 생성"""
    if not os.path.exists(SITE_PACKAGES_DIR):
        try:
            os.makedirs(SITE_PACKAGES_DIR)
            unreal.log(f"✓ site-packages 디렉토리 생성: {SITE_PACKAGES_DIR}")
        except Exception as e:
            unreal.log_error(f"디렉토리 생성 실패: {e}")
            return False
    return True


def install_package(package_name, upgrade=False):
    """
    패키지 설치
    
    Args:
        package_name (str): 설치할 패키지 이름 (예: "PySide2", "requests==2.28.0")
        upgrade (bool): 업그레이드 여부
        
    Returns:
        bool: 성공 여부
    """
    if not ensure_site_packages_dir():
        return False
    
    unreal.log(f"패키지 설치 중: {package_name}")
    unreal.log(f"대상 경로: {SITE_PACKAGES_DIR}")
    
    cmd = [
        PYTHON_EXE, "-m", "pip", "install",
        "--target", SITE_PACKAGES_DIR,
        "--no-warn-script-location"
    ]
    
    if upgrade:
        cmd.append("--upgrade")
    
    cmd.append(package_name)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            unreal.log(f"✓ {package_name} 설치 완료!")
            if result.stdout:
                unreal.log(result.stdout)
            return True
        else:
            unreal.log_error(f"✗ {package_name} 설치 실패!")
            if result.stderr:
                unreal.log_error(result.stderr)
            return False
            
    except Exception as e:
        unreal.log_error(f"설치 중 오류 발생: {e}")
        return False


def uninstall_package(package_name):
    """
    패키지 제거
    
    Args:
        package_name (str): 제거할 패키지 이름
        
    Returns:
        bool: 성공 여부
    """
    unreal.log(f"패키지 제거 중: {package_name}")
    
    cmd = [
        PYTHON_EXE, "-m", "pip", "uninstall",
        "-y",  # 확인 없이 제거
        package_name
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            unreal.log(f"✓ {package_name} 제거 완료!")
            return True
        else:
            unreal.log_error(f"✗ {package_name} 제거 실패!")
            if result.stderr:
                unreal.log_error(result.stderr)
            return False
            
    except Exception as e:
        unreal.log_error(f"제거 중 오류 발생: {e}")
        return False


def list_installed_packages():
    """
    설치된 패키지 목록 출력
    
    Returns:
        list: 설치된 패키지 목록 [(이름, 버전), ...]
    """
    cmd = [PYTHON_EXE, "-m", "pip", "list"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            packages = []
            
            # 헤더 건너뛰기
            for line in lines[2:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append((parts[0], parts[1]))
            
            unreal.log(f"\n{'='*60}")
            unreal.log("설치된 Python 패키지:")
            unreal.log(f"{'='*60}")
            for name, version in packages:
                unreal.log(f"  {name:30s} {version}")
            unreal.log(f"{'='*60}")
            unreal.log(f"총 {len(packages)}개 패키지")
            
            return packages
        else:
            unreal.log_error("패키지 목록 조회 실패!")
            return []
            
    except Exception as e:
        unreal.log_error(f"목록 조회 중 오류 발생: {e}")
        return []


def install_requirements(requirements_file):
    """
    requirements.txt 파일에서 패키지 설치
    
    Args:
        requirements_file (str): requirements.txt 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    if not os.path.exists(requirements_file):
        unreal.log_error(f"파일을 찾을 수 없습니다: {requirements_file}")
        return False
    
    if not ensure_site_packages_dir():
        return False
    
    unreal.log(f"requirements.txt에서 패키지 설치 중: {requirements_file}")
    
    cmd = [
        PYTHON_EXE, "-m", "pip", "install",
        "--target", SITE_PACKAGES_DIR,
        "--no-warn-script-location",
        "-r", requirements_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            unreal.log("✓ 모든 패키지 설치 완료!")
            if result.stdout:
                unreal.log(result.stdout)
            return True
        else:
            unreal.log_error("✗ 일부 패키지 설치 실패!")
            if result.stderr:
                unreal.log_error(result.stderr)
            return False
            
    except Exception as e:
        unreal.log_error(f"설치 중 오류 발생: {e}")
        return False


def check_package_installed(package_name):
    """
    패키지 설치 여부 확인
    
    Args:
        package_name (str): 확인할 패키지 이름
        
    Returns:
        bool: 설치 여부
    """
    cmd = [PYTHON_EXE, "-m", "pip", "show", package_name]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            unreal.log(f"✓ {package_name} 설치되어 있음")
            unreal.log(result.stdout)
            return True
        else:
            unreal.log(f"✗ {package_name} 설치되어 있지 않음")
            return False
            
    except Exception as e:
        unreal.log_error(f"확인 중 오류 발생: {e}")
        return False


def update_pip():
    """pip 자체를 최신 버전으로 업데이트"""
    unreal.log("pip 업데이트 중...")
    
    cmd = [PYTHON_EXE, "-m", "pip", "install", "--upgrade", "pip"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            unreal.log("✓ pip 업데이트 완료!")
            return True
        else:
            unreal.log_error("✗ pip 업데이트 실패!")
            if result.stderr:
                unreal.log_error(result.stderr)
            return False
            
    except Exception as e:
        unreal.log_error(f"업데이트 중 오류 발생: {e}")
        return False


def add_to_sys_path():
    """site-packages를 sys.path에 추가 (런타임에 즉시 사용 가능하도록)"""
    if SITE_PACKAGES_DIR not in sys.path:
        sys.path.insert(0, SITE_PACKAGES_DIR)
        unreal.log(f"✓ sys.path에 추가: {SITE_PACKAGES_DIR}")
        return True
    else:
        unreal.log("이미 sys.path에 포함되어 있음")
        return False


# ============================================================================
# 편의 함수들
# ============================================================================

def quick_install(package_name):
    """빠른 설치 (설치 + sys.path 추가)"""
    success = install_package(package_name)
    if success:
        add_to_sys_path()
    return success


def install_common_packages():
    """자주 사용하는 패키지 일괄 설치"""
    common_packages = [
        "requests",      # HTTP 라이브러리
        "pillow",        # 이미지 처리
        "numpy",         # 수치 계산
        "PySide2",       # Qt GUI
    ]
    
    unreal.log("일반적으로 많이 사용하는 패키지 설치 중...")
    unreal.log(f"패키지: {', '.join(common_packages)}")
    
    results = {}
    for package in common_packages:
        results[package] = install_package(package)
    
    # 결과 요약
    unreal.log("\n" + "="*60)
    unreal.log("설치 결과:")
    for package, success in results.items():
        status = "✓ 성공" if success else "✗ 실패"
        unreal.log(f"  {package:20s} {status}")
    unreal.log("="*60)
    
    add_to_sys_path()
    
    return results


# ============================================================================
# 사용 예시 및 도움말
# ============================================================================

def print_help():
    """사용법 출력"""
    help_text = """
╔═══════════════════════════════════════════════════════════════╗
║  Unreal Engine Python 패키지 관리 도구                          ║
╚═══════════════════════════════════════════════════════════════╝

📦 기본 사용법:
──────────────────────────────────────────────────────────────

# 패키지 설치
install_package("PySide2")
install_package("requests==2.28.0")  # 특정 버전

# 패키지 제거
uninstall_package("PySide2")

# 설치된 패키지 목록
list_installed_packages()

# 패키지 설치 확인
check_package_installed("PySide2")

# 빠른 설치 (설치 + sys.path 추가)
quick_install("requests")

# 일반 패키지 일괄 설치
install_common_packages()

──────────────────────────────────────────────────────────────
🔧 고급 기능:
──────────────────────────────────────────────────────────────

# requirements.txt에서 설치
install_requirements("D:/path/to/requirements.txt")

# pip 업데이트
update_pip()

# sys.path에 수동 추가
add_to_sys_path()

──────────────────────────────────────────────────────────────
📍 설치 경로:
──────────────────────────────────────────────────────────────
{SITE_PACKAGES_DIR}

Python 실행 파일:
{PYTHON_EXE}
──────────────────────────────────────────────────────────────
"""
    print(help_text)


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    unreal.log("Python 패키지 관리 도구가 로드되었습니다.")
    unreal.log("사용법을 보려면: print_help()")
    unreal.log(f"설치 경로: {SITE_PACKAGES_DIR}")
    
    # site-packages 디렉토리 자동 생성
    ensure_site_packages_dir()
    
    # sys.path에 자동 추가
    add_to_sys_path()
