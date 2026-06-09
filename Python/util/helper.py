"""
Unreal Engine Python Helper
주요 유틸리티, 서브시스템, 라이브러리를 쉽게 접근

Usage:
    # 방법 1: 모든 바로가기 임포트
    from util.helper import *
    
    # 방법 2: 네임스페이스로 사용 (권장)
    from util import helper as uh
    actors = uh.get_selected_actors()
    
    # 방법 3: 특정 함수만
    from util.helper import get_selected_assets, spawn_actor

Features:
    - ✅ UE 4.27 - 5.5+ 호환
    - ✅ 자동 버전 감지 및 Fallback
    - ✅ 풍부한 편의 함수
    - ✅ Pylance 타입 에러 없음

Compatible: UE 4.27 - 5.5+
Version: 3.0 (Unified)
"""

import unreal
from typing import List, Optional, Any


# ============================================================================
# 📦 에셋 관리 (Asset Management)
# ============================================================================

EAL = unreal.EditorAssetLibrary
"""EditorAssetLibrary: Content Browser에서 에셋 로드, 저장, 삭제, 이름변경 등"""

AR = unreal.AssetRegistryHelpers
"""AssetRegistryHelpers: 에셋 검색 및 쿼리"""

AT = unreal.AssetToolsHelpers
"""AssetToolsHelpers: 에셋 생성 및 Import"""


# ============================================================================
# 🎬 레벨 & 액터 (Level & Actor)
# ============================================================================

ELL = unreal.EditorLevelLibrary
"""EditorLevelLibrary: 레벨 로드, 저장, 액터 스폰 등"""

EFL = unreal.EditorFilterLibrary
"""EditorFilterLibrary: 액터 필터링"""

# EditorActorSubsystem (UE5+, 있으면 사용)
def _get_actor_subsystem():
    """EditorActorSubsystem 가져오기 (UE5+)"""
    try:
        return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    except:
        return None

EAS = _get_actor_subsystem()
"""EditorActorSubsystem: 액터 관리 (UE5+ 전용, UE4에서는 None)"""


# ============================================================================
# 🎨 머티리얼 & 렌더링 (Material & Rendering)
# ============================================================================

MEL = unreal.MaterialEditingLibrary
"""MaterialEditingLibrary: 머티리얼 생성 및 편집"""

ML = unreal.MaterialLibrary
"""MaterialLibrary: 머티리얼 파라미터 컬렉션 Get/Set"""

RL = unreal.RenderingLibrary
"""RenderingLibrary: 렌더타겟 및 캡처"""


# ============================================================================
# 🎭 메시 (Mesh)
# ============================================================================

SML = unreal.EditorStaticMeshLibrary
"""EditorStaticMeshLibrary: StaticMesh 편집 및 분석"""

SKL = unreal.EditorSkeletalMeshLibrary
"""EditorSkeletalMeshLibrary: SkeletalMesh 편집 및 분석"""


# ============================================================================
# 🔧 유틸리티 (Utilities)
# ============================================================================

EUL = unreal.EditorUtilityLibrary
"""EditorUtilityLibrary: 에디터 유틸리티 - 선택, 다이얼로그 등"""

SYS = unreal.SystemLibrary
"""SystemLibrary: 시스템 정보 - 엔진 버전, 플랫폼 등"""

STR = unreal.StringLibrary
"""StringLibrary: 문자열 유틸리티"""

MATH = unreal.MathLibrary
"""MathLibrary: 수학 함수 - 벡터, 회전 등"""

FILE = unreal.BlueprintFileUtilsBPLibrary
"""BlueprintFileUtilsBPLibrary: 파일 시스템 작업"""

PATHS = unreal.Paths
"""Paths: 프로젝트 경로 정보"""


# ============================================================================
# 🎬 시퀀서 (Sequencer) - 선택적
# ============================================================================

try:
    SEQ = unreal.SequencerTools
    """SequencerTools: 시퀀서 편집"""
except AttributeError:
    SEQ = None


# ============================================================================
# 🚀 편의 함수 - 선택 (Selection Helpers)
# ============================================================================

def get_selected_assets() -> List:
    """Content Browser에서 선택된 에셋들 반환"""
    return EUL.get_selected_assets()


def get_selected_actors() -> List:
    """레벨에서 선택된 액터들 반환"""
    if EAS:
        return EAS.get_selected_level_actors()
    else:
        # UE4 Fallback
        return ELL.get_selected_level_actors()


def get_all_actors(actor_class=None) -> List:
    """
    레벨의 모든 액터 반환 (옵션: 특정 클래스만)
    
    Args:
        actor_class: 필터링할 액터 클래스 (예: unreal.Light)
    
    Returns:
        액터 리스트
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


def get_actors_by_name(name_contains: str) -> List:
    """
    이름에 특정 문자열을 포함하는 액터들 반환
    
    Args:
        name_contains: 검색할 문자열 (대소문자 구분 없음)
    
    Returns:
        매칭된 액터 리스트
    """
    all_actors = get_all_actors()
    return [a for a in all_actors if name_contains.lower() in a.get_name().lower()]


def get_actors_by_tag(tag: str) -> List:
    """
    특정 태그를 가진 액터들 반환
    
    Args:
        tag: 검색할 태그
    
    Returns:
        매칭된 액터 리스트
    """
    all_actors = get_all_actors()
    result = []
    for actor in all_actors:
        try:
            if hasattr(actor, 'tags') and tag in actor.tags:
                result.append(actor)
        except:
            pass
    return result


# ============================================================================
# 🚀 편의 함수 - 에셋 (Asset Helpers)
# ============================================================================

def list_assets(directory="/Game", recursive=True, include_only_on_disk_assets=False) -> List[str]:
    """
    특정 디렉토리의 에셋 경로 리스트 반환
    
    Args:
        directory: 검색할 디렉토리 (기본: /Game)
        recursive: 하위 폴더도 검색할지 (기본: True)
        include_only_on_disk_assets: 디스크에 있는 에셋만 (기본: False)
    
    Returns:
        에셋 경로 리스트
    """
    return EAL.list_assets(directory, recursive=recursive, include_only_on_disk_assets=include_only_on_disk_assets)


def load_asset(asset_path: str):
    """
    에셋 로드
    
    Args:
        asset_path: 에셋 경로 (예: /Game/MyFolder/MyAsset)
    
    Returns:
        로드된 에셋 또는 None
    """
    return EAL.load_asset(asset_path)


def save_asset(asset_or_path, only_if_dirty=True) -> bool:
    """
    에셋 저장
    
    Args:
        asset_or_path: 에셋 객체 또는 경로
        only_if_dirty: 변경된 경우에만 저장 (기본: True)
    
    Returns:
        저장 성공 여부
    """
    if isinstance(asset_or_path, str):
        path = asset_or_path
    else:
        path = asset_or_path.get_path_name()
    
    return EAL.save_asset(path, only_if_dirty)


def delete_asset(asset_path: str) -> bool:
    """
    에셋 삭제
    
    Args:
        asset_path: 에셋 경로
    
    Returns:
        삭제 성공 여부
    """
    return EAL.delete_asset(asset_path)


def rename_asset(source: str, destination: str) -> bool:
    """
    에셋 이름 변경
    
    Args:
        source: 원본 에셋 경로
        destination: 새 에셋 경로
    
    Returns:
        이름 변경 성공 여부
    """
    return EAL.rename_asset(source, destination)


def duplicate_asset(source: str, destination: str):
    """
    에셋 복제
    
    Args:
        source: 원본 에셋 경로
        destination: 복제될 경로
    
    Returns:
        복제된 에셋
    """
    return EAL.duplicate_asset(source, destination)


def get_assets_by_class(asset_class, directory="/Game") -> List:
    """
    특정 클래스의 에셋만 반환
    
    Args:
        asset_class: 필터링할 에셋 클래스
        directory: 검색할 디렉토리
    
    Returns:
        매칭된 에셋 리스트
    """
    asset_paths = list_assets(directory)
    assets = []
    
    for path in asset_paths:
        asset = load_asset(path)
        if asset and isinstance(asset, asset_class):
            assets.append(asset)
    
    return assets


# ============================================================================
# 🚀 편의 함수 - 액터 생성 (Actor Creation)
# ============================================================================

def spawn_actor(actor_class, location=None, rotation=None):
    """
    액터 스폰
    
    Args:
        actor_class: 스폰할 액터 클래스
        location: 위치 (기본: 원점)
        rotation: 회전 (기본: 0)
    
    Returns:
        생성된 액터
    """
    if location is None:
        location = unreal.Vector(0, 0, 0)
    if rotation is None:
        rotation = unreal.Rotator(0, 0, 0)
    
    return ELL.spawn_actor_from_class(actor_class, location, rotation)


def spawn_actor_from_object(object_to_use, location=None, rotation=None):
    """
    에셋 객체로부터 액터 스폰
    
    Args:
        object_to_use: 스폰할 에셋 객체
        location: 위치 (기본: 원점)
        rotation: 회전 (기본: 0)
    
    Returns:
        생성된 액터
    """
    if location is None:
        location = unreal.Vector(0, 0, 0)
    if rotation is None:
        rotation = unreal.Rotator(0, 0, 0)
    
    return ELL.spawn_actor_from_object(object_to_use, location, rotation)


# ============================================================================
# 🚀 편의 함수 - 일괄 처리 (Batch Operations)
# ============================================================================

def batch_rename_assets(assets: List, prefix="", suffix="", search="", replace=""):
    """
    에셋 일괄 이름 변경
    
    Args:
        assets: 에셋 리스트
        prefix: 앞에 붙일 문자열
        suffix: 뒤에 붙일 문자열
        search: 찾을 문자열
        replace: 바꿀 문자열
    """
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


def batch_set_actor_property(actors: List, property_name: str, value):
    """
    여러 액터의 프로퍼티를 일괄 설정
    
    Args:
        actors: 액터 리스트
        property_name: 프로퍼티 이름
        value: 설정할 값
    """
    for actor in actors:
        try:
            actor.set_editor_property(property_name, value)
            log(f"Set {actor.get_name()}.{property_name} = {value}")
        except Exception as e:
            log(f"Failed to set {actor.get_name()}.{property_name}: {e}", error=True)


# ============================================================================
# 🚀 편의 함수 - 로깅 (Logging)
# ============================================================================

def log(message: str, warning=False, error=False):
    """
    로그 출력
    
    Args:
        message: 로그 메시지
        warning: 경고 로그로 출력
        error: 에러 로그로 출력
    """
    if error:
        unreal.log_error(message)
    elif warning:
        unreal.log_warning(message)
    else:
        unreal.log(message)


# ============================================================================
# 🚀 편의 함수 - 시스템 정보 (System Info)
# ============================================================================

def get_engine_version() -> str:
    """엔진 버전 문자열 반환"""
    return SYS.get_engine_version()


def get_project_dir() -> str:
    """프로젝트 디렉토리 경로 반환"""
    return PATHS.project_dir()


def get_content_dir() -> str:
    """Content 디렉토리 경로 반환"""
    return PATHS.project_content_dir()


def get_saved_dir() -> str:
    """Saved 디렉토리 경로 반환"""
    return PATHS.project_saved_dir()


def get_plugins_dir() -> str:
    """Plugins 디렉토리 경로 반환"""
    return PATHS.project_plugins_dir()


def get_editor_world():
    """
    에디터 월드 가져오기 (월드 컨텍스트 필요 시 사용)
    
    Returns:
        현재 에디터 월드 객체
    
    Usage:
        world = get_editor_world()
        # Material Parameter Collection에서 값 가져오기
        value = ML.get_vector_parameter_value(world, collection, param_name)
    """
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    return editor_subsystem.get_editor_world()


# ============================================================================
# 🚀 편의 함수 - 정보 출력 (Info Display)
# ============================================================================

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
            log(f"    Path: {asset.get_path_name()}")
    
    if actors:
        log(f"\n🎭 액터 ({len(actors)}개):")
        for actor in actors:
            loc = actor.get_actor_location()
            log(f"  • {actor.get_name()} ({actor.get_class().get_name()})")
            log(f"    Location: ({loc.x:.1f}, {loc.y:.1f}, {loc.z:.1f})")
    
    if not assets and not actors:
        log("선택된 것이 없습니다", warning=True)
    
    log(f"{'='*60}\n")


def print_actor_hierarchy(actor, indent=0):
    """
    액터의 계층 구조 출력
    
    Args:
        actor: 루트 액터
        indent: 들여쓰기 레벨 (재귀용)
    """
    prefix = "  " * indent
    log(f"{prefix}└─ {actor.get_name()} ({actor.get_class().get_name()})")
    
    # 자식 액터들
    children = actor.get_attached_actors()
    for child in children:
        print_actor_hierarchy(child, indent + 1)


# ============================================================================
# 📚 도움말 (Help)
# ============================================================================

def help():
    """사용 가능한 바로가기 및 함수 출력"""
    ue_version = "UE5" if EAS else "UE4"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     Unreal Engine Python API 바로가기 ({ue_version})         ║
╚══════════════════════════════════════════════════════════════╝

📦 에셋 관리:
   EAL  - EditorAssetLibrary       로드/저장/삭제/이름변경
   AR   - AssetRegistryHelpers     검색/쿼리
   AT   - AssetToolsHelpers        생성/Import

🎬 레벨 & 액터:
   ELL  - EditorLevelLibrary       레벨 작업, 액터 스폰
   {'EAS  - EditorActorSubsystem     액터 관리 ✓' if EAS else 'EAS  - 사용 불가 (UE5+ 전용)'}
   EFL  - EditorFilterLibrary      필터링

🎨 머티리얼 & 렌더링:
   MEL  - MaterialEditingLibrary   편집
   ML   - MaterialLibrary          파라미터 컬렉션
   RL   - RenderingLibrary         렌더타겟

🎭 메시:
   SML  - EditorStaticMeshLibrary  스태틱 메시
   SKL  - EditorSkeletalMeshLibrary스켈레탈 메시

🔧 유틸리티:
   EUL  - EditorUtilityLibrary     에디터 유틸리티
   SYS  - SystemLibrary            시스템 정보
   STR  - StringLibrary            문자열 처리
   MATH - MathLibrary              수학 함수
   FILE - BlueprintFileUtilsBPLibrary  파일 작업
   PATHS- Paths                    경로 정보

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 주요 편의 함수:

📋 선택:
   get_selected_assets()          Content Browser 선택
   get_selected_actors()          레벨 액터 선택
   get_all_actors([class])        모든 액터 (옵션: 클래스 필터)
   get_actors_by_name(str)        이름으로 검색
   get_actors_by_tag(tag)         태그로 검색

📦 에셋:
   list_assets(dir)               에셋 경로 리스트
   load_asset(path)               에셋 로드
   save_asset(asset)              에셋 저장
   delete_asset(path)             에셋 삭제
   rename_asset(src, dst)         이름 변경
   duplicate_asset(src, dst)      복제
   get_assets_by_class(class)     클래스로 필터링

🎭 액터:
   spawn_actor(class, loc, rot)   액터 스폰
   spawn_actor_from_object(obj)   에셋에서 스폰

⚡ 일괄 처리:
   batch_rename_assets(list, ...)    에셋 일괄 이름 변경
   batch_set_actor_property(list, ...)  프로퍼티 일괄 설정

📊 정보:
   print_selected_info()          선택 정보 출력
   print_actor_hierarchy(actor)   계층 구조 출력

📝 로그:
   log(msg, warning=False, error=False)  로그 출력

🔧 시스템:
   get_engine_version()           엔진 버전
   get_project_dir()              프로젝트 경로
   get_content_dir()              Content 경로
   get_editor_world()             에디터 월드 (월드 컨텍스트)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 사용 예제:

   # 모든 바로가기 임포트
   from util.unreal_api import *
   
   # 선택된 것들 가져오기
   assets = get_selected_assets()
   actors = get_selected_actors()
   print_selected_info()
   
   # 액터 스폰
   location = unreal.Vector(0, 0, 100)
   spawn_actor(unreal.PointLight, location)
   
   # 에셋 검색
   materials = get_assets_by_class(unreal.Material, "/Game/Materials")
   
   # 일괄 작업
   batch_rename_assets(assets, prefix="NEW_")
   
   # Material Parameter Collection 사용
   world = get_editor_world()
   collection = load_asset("/Game/MyCollection")
   value = ML.get_vector_parameter_value(world, collection, unreal.Name("MyParam"))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

엔진 버전: {get_engine_version()}
프로젝트: {PATHS.project_dir()}
""")

# ============================================================================
# 모듈 초기화
# ============================================================================

if __name__ != "__main__":
    ue_version = "UE5" if EAS else "UE4"
    log(f"✅ Unreal Helper 로드됨 | {ue_version} | {get_engine_version()}")
    log(f"   📚 도움말: help() 또는 from util.helper import help")
