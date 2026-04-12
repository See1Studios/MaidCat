"""
Unreal Engine Python API 바로가기 모음 (검증된 버전)
실제 Unreal Engine에서 확인된 API만 포함

Usage:
    from developer.UnrealShortcuts import *
    
    # 선택된 것들 가져오기
    assets = get_selected_assets()
    actors = get_selected_actors()
    
    # 정보 출력
    print_selected_info()

Compatible: UE 4.27 - 5.5+
"""

import unreal
from typing import List, Optional


# ============================================================================
# 📦 검증된 에셋 관리 API
# ============================================================================

# ✅ Asset Library (가장 많이 사용)
EAL = unreal.EditorAssetLibrary
"""Content Browser 에셋 작업: 로드, 저장, 삭제, 이름변경 등"""

# ✅ Asset Registry
AR = unreal.AssetRegistryHelpers
"""에셋 검색 및 쿼리"""

# ✅ Asset Tools
AT = unreal.AssetToolsHelpers
"""에셋 생성 및 Import"""


# ============================================================================
# 🎬 검증된 레벨 & 액터 API
# ============================================================================

# ✅ Level Library
ELL = unreal.EditorLevelLibrary
"""레벨 작업: 액터 스폰, 레벨 로드/저장 등"""

# ✅ Filter Library
EFL = unreal.EditorFilterLibrary
"""액터 필터링"""

# ✅ Actor Subsystem (UE5+, 있으면 사용)
def _get_actor_subsystem():
    """EditorActorSubsystem 가져오기 (UE5+)"""
    try:
        return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    except:
        return None

EAS = _get_actor_subsystem()


# ============================================================================
# 🎨 검증된 머티리얼 & 렌더링 API
# ============================================================================

# ✅ Material Editing
MEL = unreal.MaterialEditingLibrary
"""머티리얼 생성 및 편집"""

# ✅ Rendering
RL = unreal.RenderingLibrary
"""렌더타겟 및 캡처"""


# ============================================================================
# 🎭 검증된 메시 API
# ============================================================================

# ✅ Static Mesh
SML = unreal.EditorStaticMeshLibrary
"""StaticMesh 편집 및 분석"""

# ✅ Skeletal Mesh
SKL = unreal.EditorSkeletalMeshLibrary
"""SkeletalMesh 편집 및 분석"""


# ============================================================================
# 🔧 검증된 유틸리티 API
# ============================================================================

# ✅ Editor Utility
EUL = unreal.EditorUtilityLibrary
"""에디터 유틸리티: 선택, 다이얼로그 등"""

# ✅ System
SYS = unreal.SystemLibrary
"""시스템 정보: 엔진 버전, 플랫폼 등"""

# ✅ String
STR = unreal.StringLibrary
"""문자열 유틸리티"""

# ✅ Math
MATH = unreal.MathLibrary
"""수학 함수: 벡터, 회전 등"""

# ✅ File
FILE = unreal.BlueprintFileUtilsBPLibrary
"""파일 시스템 작업"""

# ✅ Paths
PATHS = unreal.Paths
"""프로젝트 경로 정보"""


# ============================================================================
# 🎬 시퀀서 (있으면 사용)
# ============================================================================

try:
    SEQ = unreal.SequencerTools
    """시퀀서 편집"""
except AttributeError:
    SEQ = None


# ============================================================================
# 🚀 편의 함수들
# ============================================================================

def get_selected_assets() -> List:
    """Content Browser에서 선택된 에셋"""
    return EUL.get_selected_assets()


def get_selected_actors() -> List:
    """레벨에서 선택된 액터"""
    if EAS:
        return EAS.get_selected_level_actors()
    else:
        # UE4 Fallback
        return ELL.get_selected_level_actors()


def get_all_actors(actor_class=None) -> List:
    """
    레벨의 모든 액터 (옵션: 특정 클래스만)
    
    Args:
        actor_class: 필터링할 액터 클래스 (예: unreal.Light)
    """
    if EAS:
        # UE5 방식
        if actor_class:
            return EAS.get_all_level_actors_of_class(actor_class)
        return EAS.get_all_level_actors()
    else:
        # UE4 Fallback
        all_actors = ELL.get_all_level_actors()
        if actor_class:
            return [a for a in all_actors if isinstance(a, actor_class)]
        return all_actors


def list_assets(directory="/Game", recursive=True) -> List[str]:
    """에셋 경로 리스트"""
    return EAL.list_assets(directory, recursive=recursive)


def load_asset(asset_path: str):
    """에셋 로드"""
    return EAL.load_asset(asset_path)


def save_asset(asset, only_if_dirty=True) -> bool:
    """에셋 저장"""
    return EAL.save_asset(asset.get_path_name(), only_if_dirty)


def delete_asset(asset_path: str) -> bool:
    """에셋 삭제"""
    return EAL.delete_asset(asset_path)


def rename_asset(source: str, destination: str) -> bool:
    """에셋 이름 변경"""
    return EAL.rename_asset(source, destination)


def duplicate_asset(source: str, destination: str):
    """에셋 복제"""
    return EAL.duplicate_asset(source, destination)


def spawn_actor(actor_class, location=None, rotation=None):
    """
    액터 스폰
    
    Args:
        actor_class: 스폰할 액터 클래스
        location: 위치 (기본: 원점)
        rotation: 회전 (기본: 0)
    """
    if location is None:
        location = unreal.Vector(0, 0, 0)
    if rotation is None:
        rotation = unreal.Rotator(0, 0, 0)
    
    return ELL.spawn_actor_from_class(actor_class, location, rotation)


def log(message: str, warning=False, error=False):
    """로그 출력"""
    if error:
        unreal.log_error(message)
    elif warning:
        unreal.log_warning(message)
    else:
        unreal.log(message)


def get_engine_version() -> str:
    """엔진 버전"""
    return SYS.get_engine_version()


def get_project_dir() -> str:
    """프로젝트 디렉토리"""
    return PATHS.project_dir()


def get_content_dir() -> str:
    """Content 디렉토리"""
    return PATHS.project_content_dir()


# ============================================================================
# 🎯 고급 헬퍼
# ============================================================================

def get_assets_by_class(asset_class, directory="/Game") -> List:
    """특정 클래스의 에셋만 반환"""
    asset_paths = list_assets(directory)
    assets = []
    
    for path in asset_paths:
        asset = load_asset(path)
        if asset and isinstance(asset, asset_class):
            assets.append(asset)
    
    return assets


def get_actors_by_name(name_contains: str) -> List:
    """이름에 특정 문자열 포함하는 액터"""
    all_actors = get_all_actors()
    return [a for a in all_actors if name_contains.lower() in a.get_name().lower()]


def batch_rename_assets(assets: List, prefix="", suffix="", search="", replace=""):
    """에셋 일괄 이름 변경"""
    for asset in assets:
        old_path = asset.get_path_name()
        old_name = asset.get_name()
        
        new_name = old_name
        if search and replace:
            new_name = new_name.replace(search, replace)
        if prefix:
            new_name = prefix + new_name
        if suffix:
            new_name = new_name + suffix
        
        directory = old_path.rsplit('/', 1)[0]
        new_path = f"{directory}/{new_name}"
        
        if new_path != old_path:
            rename_asset(old_path, new_path)
            log(f"Renamed: {old_name} -> {new_name}")


def print_selected_info():
    """선택된 에셋 및 액터 정보 출력"""
    assets = get_selected_assets()
    actors = get_selected_actors()
    
    log(f"\n{'='*60}")
    log(f"선택 정보")
    log(f"{'='*60}")
    
    if assets:
        log(f"\n📦 에셋 ({len(assets)}개):")
        for asset in assets:
            log(f"  • {asset.get_name()} ({asset.get_class().get_name()})")
    
    if actors:
        log(f"\n🎭 액터 ({len(actors)}개):")
        for actor in actors:
            log(f"  • {actor.get_name()} ({actor.get_class().get_name()})")
    
    if not assets and not actors:
        log("선택된 것이 없습니다", warning=True)
    
    log(f"{'='*60}\n")


# ============================================================================
# 📚 도움말
# ============================================================================

def help():
    """사용 가능한 바로가기 출력"""
    ue_version = "UE5" if EAS else "UE4"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     Unreal Engine Python 바로가기 ({ue_version})              ║
╚══════════════════════════════════════════════════════════════╝

📦 에셋:
   EAL  - EditorAssetLibrary       (로드/저장/삭제)
   AR   - AssetRegistryHelpers     (검색/쿼리)
   AT   - AssetToolsHelpers        (생성/Import)

🎬 액터:
   ELL  - EditorLevelLibrary       (레벨 작업)
   {'EAS  - EditorActorSubsystem     (액터 관리) ✓' if EAS else 'EAS  - 사용 불가 (UE5+만 지원)'}
   EFL  - EditorFilterLibrary      (필터링)

🎨 머티리얼:
   MEL  - MaterialEditingLibrary   (편집)
   RL   - RenderingLibrary         (렌더타겟)

🎭 메시:
   SML  - EditorStaticMeshLibrary  (스태틱 메시)
   SKL  - EditorSkeletalMeshLibrary(스켈레탈 메시)

🔧 유틸리티:
   EUL  - EditorUtilityLibrary
   SYS  - SystemLibrary
   STR  - StringLibrary
   MATH - MathLibrary
   FILE - BlueprintFileUtilsBPLibrary
   PATHS- Paths

🚀 편의 함수:
   get_selected_assets()          - 선택된 에셋
   get_selected_actors()          - 선택된 액터
   get_all_actors()               - 모든 액터
   spawn_actor(class, loc, rot)   - 액터 스폰
   log(msg)                       - 로그
   print_selected_info()          - 선택 정보 출력

📚 예제:
   from developer.UnrealShortcuts import *
   
   assets = get_selected_assets()
   actors = get_selected_actors()
   print_selected_info()
   
   log(f"엔진: {get_engine_version()}")

엔진 버전: {get_engine_version()}
""")


# 모듈 로드 시 정보
if __name__ != "__main__":
    ue_version = "UE5" if EAS else "UE4"
    log(f"✅ Unreal 바로가기 로드 | {ue_version} | {get_engine_version()}")
    log(f"   도움말: help()")


# ============================================================================
# 레거시 호환성
# ============================================================================

listAssetPaths = lambda: [print(p) for p in list_assets()]
getSelectionContentBrowser = lambda: [print(a) for a in get_selected_assets()]
getAllActors = lambda: [print(a) for a in get_all_actors()]
getSelectedActors = lambda: [print(a) for a in get_selected_actors()]
