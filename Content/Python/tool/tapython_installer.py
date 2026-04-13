# ============================================================================
# tapython_installer.py - TAPython 플러그인 자동 설치 도구
# ============================================================================
"""
TAPython 플러그인 자동 설치 도구
- GitHub에서 최신 릴리스 다운로드
- 사용자 동의 다이얼로그
- 자동 압축 해제 및 설치
- 언리얼 엔진 재시작 안내

사용법:
    from tool.tapython_installer import check_and_install_tapython
    check_and_install_tapython()  # 설치 확인 및 자동 설치
"""

import unreal
from pathlib import Path
import urllib.request
import json
import zipfile
import shutil
import tempfile
import subprocess


# ============================================================================
# 상수 정의
# ============================================================================

TAPYTHON_GITHUB_API_LATEST = "https://api.github.com/repos/cgerchenhp/UE_TAPython_Plugin_Release/releases/latest"
TAPYTHON_GITHUB_API_ALL = "https://api.github.com/repos/cgerchenhp/UE_TAPython_Plugin_Release/releases"
TAPYTHON_GITHUB_RELEASES = "https://github.com/cgerchenhp/UE_TAPython_Plugin_Release/releases"
TAPYTHON_WEBSITE = "https://www.tacolor.xyz/tapython/welcome_to_tapython.html"


# ============================================================================
# TAPython 설치 확인
# ============================================================================

def is_tapython_installed() -> bool:
    """TAPython 플러그인이 설치되어 있는지 확인 (.uplugin 파일 기준)"""
    project_path = Path(unreal.Paths.project_dir())
    
    # 플러그인 폴더에서 .uplugin 파일 확인
    # TA/TAPython은 Resources 설치 위치이므로 제외
    plugin_locations = [
        project_path / "Plugins" / "TAPython",
    ]
    
    for location in plugin_locations:
        if location.exists():
            # .uplugin 파일이 있는지 확인 (실제 플러그인 설치 여부)
            uplugin_files = list(location.glob("*.uplugin"))
            
            if uplugin_files:
                unreal.log(f"✅ TAPython 플러그인 발견: {location}")
                unreal.log(f"   플러그인 파일: {uplugin_files[0].name}")
                return True
            else:
                unreal.log(f"⚠️ {location} 폴더는 있지만 .uplugin 파일이 없음 (Resources 폴더로 추정)")
    
    return False


def get_tapython_install_path() -> Path:
    """TAPython 설치 경로 반환 (플러그인 폴더)"""
    project_path = Path(unreal.Paths.project_dir())
    return project_path / "Plugins" / "TAPython"


# ============================================================================
# GitHub API를 통한 릴리스 정보 가져오기
# ============================================================================

def get_engine_version_info():
    """현재 엔진 버전 정보 가져오기"""
    try:
        engine_version = unreal.SystemLibrary.get_engine_version()
        # "5.5.4-0+++UE5+Release-5.5" 형식에서 메이저.마이너.패치 추출
        version_parts = engine_version.split('.')
        if len(version_parts) >= 2:
            major = version_parts[0]
            minor = version_parts[1]
            patch = version_parts[2].split('-')[0] if len(version_parts) >= 3 else "0"
            return {
                'full': engine_version,
                'major_minor': f"{major}.{minor}",
                'major_minor_patch': f"{major}.{minor}.{patch}",
                'version_string': f"{major}_{minor}_{patch}",  # 파일명 형식
                'major': major,
                'minor': minor,
                'patch': patch
            }
    except Exception as e:
        unreal.log_warning(f"엔진 버전 가져오기 실패: {e}")
    
    return None


def _parse_release_data(data: dict) -> dict:
    """GitHub API 릴리스 데이터를 공통 포맷으로 변환"""
    release_info = {
        'tag_name': data.get('tag_name', 'Unknown'),
        'name': data.get('name', 'TAPython'),
        'published_at': data.get('published_at', ''),
        'html_url': data.get('html_url', TAPYTHON_GITHUB_RELEASES),
        'assets': []
    }
    for asset in data.get('assets', []):
        if asset['name'].endswith('.zip'):
            release_info['assets'].append({
                'name': asset['name'],
                'download_url': asset['browser_download_url'],
                'size': asset['size']
            })
    return release_info


def get_all_releases_info() -> list:
    """GitHub에서 전체 릴리스 목록 가져오기"""
    try:
        unreal.log("GitHub에서 TAPython 릴리스 목록 가져오는 중...")
        req = urllib.request.Request(TAPYTHON_GITHUB_API_ALL)
        req.add_header('User-Agent', 'Unreal-MaidCat-Plugin')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            releases = [_parse_release_data(r) for r in data]
            unreal.log(f"총 {len(releases)}개 릴리스 발견")
            return releases
    except Exception as e:
        unreal.log_warning(f"전체 릴리스 목록 가져오기 실패: {e}")
        return []


def get_latest_release_info() -> dict | None:
    """GitHub에서 최신 릴리스 정보 가져오기 (폴백용)"""
    try:
        req = urllib.request.Request(TAPYTHON_GITHUB_API_LATEST)
        req.add_header('User-Agent', 'Unreal-MaidCat-Plugin')
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            release_info = _parse_release_data(data)
            unreal.log(f"최신 릴리스: {release_info['name']} ({release_info['tag_name']})")
            return release_info
    except Exception as e:
        unreal.log_warning(f"최신 릴리스 정보 가져오기 실패: {e}")
        return None


def _find_matching_asset(assets: list, version_patterns: list) -> dict | None:
    """에셋 목록에서 버전 패턴과 일치하는 Win64 에셋 반환 (nopdb보다 pdb 우선)"""
    zip_assets = [a for a in assets if a['name'].endswith('.zip')]
    for pattern in version_patterns:
        for asset in zip_assets:
            name_lower = asset['name'].lower()
            if pattern.lower() in name_lower and 'win64' in name_lower and 'nopdb' not in name_lower:
                return asset
    for pattern in version_patterns:
        for asset in zip_assets:
            name_lower = asset['name'].lower()
            if pattern.lower() in name_lower and 'win64' in name_lower:
                return asset
    return None


def find_best_release_and_asset(releases: list, engine_info: dict) -> tuple[dict | None, dict | None]:
    """전체 릴리스에서 현재 엔진 버전에 맞는 릴리스와 에셋을 반환"""
    version_patterns = [
        engine_info['version_string'],                                          # "5_5_4"
        f"{engine_info['major']}_{engine_info['minor']}_{engine_info['patch']}",  # 동일
        f"{engine_info['major']}_{engine_info['minor']}",                       # "5_5"
    ]
    unreal.log(f"현재 엔진: {engine_info['full']} | 검색 패턴: {version_patterns}")

    for release in releases:
        asset = _find_matching_asset(release['assets'], version_patterns)
        if asset:
            unreal.log(f"✅ 매칭 릴리스: {release['name']} | 에셋: {asset['name']}")
            return release, asset

    unreal.log_warning("⚠️ 엔진 버전과 일치하는 릴리스를 찾지 못했습니다")
    return None, None


def select_release_and_asset() -> tuple[dict | None, dict | None]:
    """현재 엔진 버전에 맞는 릴리스와 에셋 선택 (버전 불일치 시 최신으로 폴백)"""
    engine_info = get_engine_version_info()

    # 전체 릴리스에서 버전 매칭 시도
    releases = get_all_releases_info()
    if releases and engine_info:
        release, asset = find_best_release_and_asset(releases, engine_info)
        if release and asset:
            return release, asset

    # 폴백: 최신 릴리스의 첫 번째 Win64 ZIP
    unreal.log_warning("최신 릴리스로 폴백합니다")
    latest = get_latest_release_info()
    if latest:
        zip_assets = [a for a in latest['assets'] if 'win64' in a['name'].lower()]
        fallback = zip_assets[0] if zip_assets else (latest['assets'][0] if latest['assets'] else None)
        if fallback:
            unreal.log_warning(f"⚠️ 폴백 에셋 사용: {fallback['name']}")
            return latest, fallback

    return None, None


# ============================================================================
# 다운로드 및 설치
# ============================================================================

def download_file(url: str, dest_path: Path, chunk_size: int = 8192) -> bool:
    """파일 다운로드 (진행률 표시)"""
    try:
        unreal.log(f"다운로드 시작: {url}")
        unreal.log(f"저장 경로: {dest_path}")
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Unreal-MaidCat-Plugin')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 진행률 출력 (10% 단위)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (chunk_size * 100) == 0:  # 간헐적 출력
                            unreal.log(f"다운로드 진행: {progress:.1f}% ({downloaded}/{total_size} bytes)")
        
        unreal.log(f"다운로드 완료: {dest_path}")
        return True
        
    except Exception as e:
        unreal.log_error(f"다운로드 실패: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """ZIP 파일 압축 해제"""
    try:
        unreal.log(f"압축 해제 시작: {zip_path}")
        unreal.log(f"대상 폴더: {extract_to}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        unreal.log(f"압축 해제 완료")
        return True
        
    except Exception as e:
        unreal.log_error(f"압축 해제 실패: {e}")
        return False


def organize_tapython_files(extract_path: Path, install_path: Path) -> bool:
    """압축 해제된 TAPython 파일들을 올바른 위치로 이동"""
    try:
        unreal.log(f"TAPython 파일 정리 중...")
        
        # 압축 해제된 폴더 구조 확인
        extracted_items = list(extract_path.iterdir())
        
        # 최상위에 단일 폴더가 있는 경우 (예: TAPython-1.0.0/)
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            source_folder = extracted_items[0]
        else:
            source_folder = extract_path
        
        # 설치 경로가 이미 존재하면 백업
        if install_path.exists():
            backup_path = install_path.parent / f"{install_path.name}_backup"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            unreal.log(f"기존 설치 백업: {backup_path}")
            shutil.move(str(install_path), str(backup_path))
        
        # 파일 이동
        install_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_folder), str(install_path))
        
        unreal.log(f"TAPython 설치 완료: {install_path}")
        return True
        
    except Exception as e:
        unreal.log_error(f"파일 정리 실패: {e}")
        return False


# ============================================================================
# 사용자 동의 다이얼로그
# ============================================================================

def show_install_dialog(release_info: dict, selected_asset: dict) -> bool:
    """TAPython 설치 동의 다이얼로그 표시"""
    if not release_info or not selected_asset:
        return False
    
    # 엔진 버전 정보
    engine_info = get_engine_version_info()
    engine_ver = engine_info['major_minor_patch'] if engine_info else "Unknown"
    
    # 파일 크기 (MB)
    size_mb = selected_asset['size'] / (1024 * 1024)
    
    # 메시지 구성
    message = f"""TAPython 플러그인을 설치하시겠습니까?

현재 엔진 버전: UE {engine_ver}
다운로드 파일: {selected_asset['name']} ({size_mb:.1f} MB)
릴리스: {release_info['tag_name']}
출처: GitHub - UE_TAPython_Plugin_Release

TAPython은 Python으로 Slate UI를 작성할 수 있게 해주는
언리얼 엔진 플러그인입니다.

설치 위치: {get_tapython_install_path()}

계속하시겠습니까?"""
    
    # 언리얼 엔진 다이얼로그 표시
    result = unreal.EditorDialog.show_message(
        unreal.Text("TAPython 플러그인 설치"),
        unreal.Text(message),
        unreal.AppMsgType.YES_NO
    )
    
    return result == unreal.AppReturnType.YES


def restart_editor():
    """에디터 새 프로세스로 재시작 후 현재 인스턴스 종료"""
    try:
        engine_dir = Path(unreal.Paths.engine_dir())
        editor_exe = engine_dir / "Binaries" / "Win64" / "UnrealEditor.exe"

        project_dir = Path(unreal.Paths.project_dir())
        uproject_files = list(project_dir.glob("*.uproject"))

        if not editor_exe.exists():
            unreal.log_error(f"에디터 실행 파일을 찾을 수 없습니다: {editor_exe}")
            unreal.SystemLibrary.quit_editor()
            return

        if not uproject_files:
            unreal.log_error(f"프로젝트 파일(.uproject)을 찾을 수 없습니다: {project_dir}")
            unreal.SystemLibrary.quit_editor()
            return

        unreal.log(f"에디터 재시작: {editor_exe} {uproject_files[0]}")
        subprocess.Popen([str(editor_exe), str(uproject_files[0])])
        unreal.SystemLibrary.quit_editor()

    except Exception as e:
        unreal.log_error(f"재시작 실패: {e}")
        unreal.SystemLibrary.quit_editor()


def show_restart_dialog():
    """엔진 재시작 안내 다이얼로그"""
    message = """TAPython 플러그인 설치가 완료되었습니다!

변경사항을 적용하려면 언리얼 엔진을 재시작해야 합니다.

지금 재시작하시겠습니까?"""

    result = unreal.EditorDialog.show_message(
        unreal.Text("설치 완료 - 재시작 필요"),
        unreal.Text(message),
        unreal.AppMsgType.YES_NO
    )

    if result == unreal.AppReturnType.YES:
        restart_editor()


# ============================================================================
# 메인 설치 함수
# ============================================================================

def install_tapython_from_github() -> bool:
    """GitHub에서 TAPython 다운로드 및 설치"""

    # 1. 엔진 버전에 맞는 릴리스와 에셋 선택
    release_info, asset = select_release_and_asset()
    if not release_info:
        unreal.log_error("릴리스 정보를 가져올 수 없습니다")
        return False

    if not asset:
        unreal.log_error("다운로드 가능한 파일을 찾을 수 없습니다")
        
        # 수동 다운로드 안내
        message = f"""자동 다운로드에 실패했습니다.

GitHub 릴리스 페이지에서 수동으로 다운로드하세요:
{release_info['html_url']}

다운로드 후 압축을 해제하여 다음 위치에 설치하세요:
{get_tapython_install_path()}"""
        
        unreal.EditorDialog.show_message(
            unreal.Text("수동 설치 필요"),
            unreal.Text(message),
            unreal.AppMsgType.OK
        )
        return False
    
    # 3. 사용자 동의 확인
    if not show_install_dialog(release_info, asset):
        unreal.log("사용자가 설치를 취소했습니다")
        return False
    
    # 4. 임시 폴더에 다운로드
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        download_path = temp_path / asset['name']
        
        # 다운로드
        unreal.log(f"다운로드 중: {asset['name']} ({asset['size']} bytes)")
        if not download_file(asset['download_url'], download_path):
            return False
        
        # 압축 해제
        extract_path = temp_path / "extracted"
        extract_path.mkdir(exist_ok=True)
        
        if not extract_zip(download_path, extract_path):
            return False
        
        # 설치 위치로 이동
        install_path = get_tapython_install_path()
        if not organize_tapython_files(extract_path, install_path):
            return False
    
    # 5. 설치 완료 및 재시작 안내
    unreal.log("✅ TAPython 플러그인 설치 완료!")
    show_restart_dialog()
    
    return True


def check_and_install_tapython() -> bool:
    """TAPython 설치 확인 및 자동 설치
    
    Returns:
        bool: TAPython이 설치되어 있거나 설치 완료된 경우 True
    """
    
    # 이미 설치되어 있는지 확인
    if is_tapython_installed():
        unreal.log("✅ TAPython 플러그인이 이미 설치되어 있습니다")
        return True
    
    # 설치 안내 메시지
    unreal.log("⚠️ TAPython 플러그인이 설치되어 있지 않습니다")
    unreal.log("GitHub에서 자동 설치를 시작합니다...")
    
    # 자동 설치 실행
    return install_tapython_from_github()


# ============================================================================
# 테스트/디버그용 함수
# ============================================================================

def test_github_api():
    """GitHub API 테스트"""
    print("\n=== GitHub API 테스트 ===")

    engine_info = get_engine_version_info()
    if engine_info:
        print(f"현재 엔진 버전: {engine_info['full']}")
        print(f"파일명 형식: {engine_info['version_string']}")

    releases = get_all_releases_info()
    if releases:
        print(f"\n✅ 전체 릴리스 수: {len(releases)}")
        for r in releases[:5]:  # 최근 5개만 출력
            print(f"   - {r['name']} ({r['tag_name']}) | 에셋: {len(r['assets'])}개")

    release_info, selected_asset = select_release_and_asset()
    if release_info and selected_asset:
        size_mb = selected_asset['size'] / (1024 * 1024)
        print(f"\n📥 선택된 릴리스: {release_info['name']} ({release_info['tag_name']})")
        print(f"   선택된 에셋: {selected_asset['name']} ({size_mb:.1f} MB)")
        print(f"   다운로드 URL: {selected_asset['download_url']}")
    else:
        print("❌ 적합한 릴리스/에셋을 찾지 못했습니다")


def test_installation_check():
    """설치 확인 테스트"""
    print("\n=== TAPython 설치 확인 ===")
    
    is_installed = is_tapython_installed()
    print(f"설치 여부: {'✅ 설치됨' if is_installed else '❌ 미설치'}")
    
    if not is_installed:
        print(f"설치 예정 경로: {get_tapython_install_path()}")


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    # 테스트 모드
    print("\n" + "="*70)
    print("TAPython Installer - 테스트 모드")
    print("="*70)
    
    # 1. 설치 확인
    test_installation_check()
    
    # 2. GitHub API 및 버전 매칭 테스트
    test_github_api()
    
    print("\n" + "="*70)
    print("테스트 완료! 실제 설치는 check_and_install_tapython() 호출")
    print("="*70)
