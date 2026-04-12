"""
Unreal Engine Python API 바로가기 모음
주요 유틸리티, 서브시스템, 라이브러리를 쉽게 접근할 수 있도록 정리

Usage:
    from developer.Template import *
    
    # 또는 네임스페이스로
    import developer.Template as ue
    
    actors = ue.get_selected_actors()
    assets = ue.get_selected_assets()

Compatible: UE 4.27 - 5.5+
"""

import unreal
from typing import List, Optional, Any


# ============================================================================
# 📦 Asset Management (에셋 관리)
# ============================================================================

# Asset Library - Content Browser 에셋 작업
EAL = unreal.EditorAssetLibrary
"""EditorAssetLibrary: Content Browser에서 에셋 로드, 저장, 삭제 등"""

# Asset Registry - 에셋 검색 및 쿼리
AR = unreal.AssetRegistryHelpers
"""AssetRegistryHelpers: 에셋 레지스트리 접근 및 복잡한 에셋 쿼리"""

# Asset Tools - 에셋 생성 및 Import
AT = unreal.AssetToolsHelpers
"""AssetToolsHelpers: 에셋 생성, Import, 타입 관리"""


# ============================================================================
# 🎬 Level & Actor Management (레벨 & 액터 관리)
# ============================================================================

# Level Library - 레벨 작업
ELL = unreal.EditorLevelLibrary
"""EditorLevelLibrary: 레벨 로드, 저장, 액터 스폰 등"""

# Actor Subsystem - 액터 관리 (UE5+)
try:
    EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    """EditorActorSubsystem: 액터 선택, 생성, 삭제, 검색 등 (UE5+)"""
except:
    # Fallback: UE4에서는 EditorLevelLibrary 사용
    EAS = None

# Filter Library - 액터 필터링
EFL = unreal.EditorFilterLibrary
"""EditorFilterLibrary: 액터 리스트 필터링 (클래스, 이름 등)"""


# ============================================================================
# 🎨 Material & Texture (머티리얼 & 텍스처)
# ============================================================================

# Material Editing - 머티리얼 생성/편집
MEL = unreal.MaterialEditingLibrary
"""MaterialEditingLibrary: 머티리얼 노드 생성 및 편집"""

# Rendering Library - 렌더타겟 작업
RL = unreal.RenderingLibrary
"""RenderingLibrary: 렌더타겟, 캡처 등"""

# Texture - 텍스처 관련 (UE5.4+에서 사용 가능)
try:
    TEX = unreal.get_editor_subsystem(unreal.EditorSubsystem)  # 실제로는 서브시스템으로 접근
    """EditorTextureSubsystem: 텍스처 편집 (UE5.4+)"""
except:
    TEX = None


# ============================================================================
# 🎭 Mesh & Animation (메시 & 애니메이션)
# ============================================================================

# Static Mesh Library - 스태틱 메시
SML = unreal.EditorStaticMeshLibrary
"""EditorStaticMeshLibrary: StaticMesh 편집 및 분석"""

# Skeletal Mesh Library - 스켈레탈 메시
SKL = unreal.EditorSkeletalMeshLibrary
"""EditorSkeletalMeshLibrary: SkeletalMesh 편집 및 분석"""

# Animation Subsystem - 애니메이션 (UE5.3+)
try:
    ANI = unreal.get_editor_subsystem(unreal.EditorSubsystem)  # 실제로는 서브시스템으로 접근
    """EditorAnimationSubsystem: 애니메이션 시퀀스 편집 (UE5.3+)"""
except:
    ANI = None


# ============================================================================
# 🎯 Editor Utilities (에디터 유틸리티)
# ============================================================================

# Editor Utility - Blutility 기능
EUL = unreal.EditorUtilityLibrary
"""EditorUtilityLibrary: 에디터 유틸리티 기능 (선택, 다이얼로그 등)"""

# System Library - 시스템 정보
SYS = unreal.SystemLibrary
"""SystemLibrary: 엔진 버전, 플랫폼 정보 등"""

# String Library - 문자열 처리
STR = unreal.StringLibrary
"""StringLibrary: 문자열 유틸리티"""

# Math Library - 수학 함수
MATH = unreal.MathLibrary
"""MathLibrary: 벡터, 회전, 수학 연산"""

# File Utilities - 파일 작업
FILE = unreal.BlueprintFileUtilsBPLibrary
"""BlueprintFileUtilsBPLibrary: 파일 시스템 작업"""


# ============================================================================
# 🎬 Sequencer & Cinematics (시퀀서 & 시네마틱)
# ============================================================================

# Sequencer Tools - 시퀀서 편집
SEQ = unreal.SequencerTools
"""SequencerTools: 레벨 시퀀스 편집"""

# Movie Scene - 무비 씬 관리
try:
    MS = unreal.MovieSceneToolsScriptingLibrary
    """MovieSceneToolsScriptingLibrary: 무비 씬 스크립팅"""
except AttributeError:
    MS = None


# ============================================================================
# 🔧 Scripting & Automation (스크립팅 & 자동화)
# ============================================================================

# Automation Library - 자동화 테스트
AUTO = unreal.AutomationLibrary
"""AutomationLibrary: 자동화 테스트 및 스크린샷"""

# Slate Application - UI 작업
try:
    SLATE = unreal.SlateWindowElementHelpers
    """SlateWindowElementHelpers: Slate UI 헬퍼"""
except AttributeError:
    SLATE = None


# ============================================================================
# 📁 Path & Directory Utilities (경로 & 디렉토리)
# ============================================================================

# Paths - 프로젝트 경로
PATHS = unreal.Paths
"""Paths: 프로젝트, 콘텐츠, 엔진 경로 정보"""


# ============================================================================
# 🎨 UI Subsystems (UE5+)
# ============================================================================

# UE5+ 전용 서브시스템들 (없으면 None)
try:
    INSIGHTS = unreal.get_editor_subsystem(unreal.EditorSubsystem)
    """EditorInsightsSubsystem: Unreal Insights 통합 (UE5.1+)"""
except:
    INSIGHTS = None

try:
    # Python 관련 유틸리티
    PYTHON = unreal.PythonScriptLibrary
    """PythonScriptLibrary: Python 스크립팅 헬퍼"""
except AttributeError:
    PYTHON = None

# Asset Subsystem (UE5+)
try:
    EASSET = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    """EditorAssetSubsystem: 에셋 서브시스템 (UE5+)"""
except:
    EASSET = None


# ============================================================================
# 🚀 편의 함수들 (Convenience Functions)
# ============================================================================

def get_selected_assets() -> List[unreal.Object]:
    """
    Content Browser에서 선택된 에셋 반환
    
    Returns:
        List[unreal.Object]: 선택된 에셋 리스트
    """
    return EUL.get_selected_assets()


def get_selected_actors() -> List[unreal.Actor]:
    """
    레벨에서 선택된 액터 반환
    
    Returns:
        List[unreal.Actor]: 선택된 액터 리스트
    """
    if EAS:
        return EAS.get_selected_level_actors()
    else:
        # Fallback: UE4 방식
        return ELL.get_selected_level_actors()


def get_all_actors(actor_class: Optional[type] = None) -> List[unreal.Actor]:
    """
    레벨의 모든 액터 반환 (옵션: 특정 클래스만)
    
    Args:
        actor_class: 필터링할 액터 클래스 (None이면 모든 액터)
    
    Returns:
        List[unreal.Actor]: 액터 리스트
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


def list_assets(directory: str = "/Game", recursive: bool = True) -> List[str]:
    """
    디렉토리의 에셋 경로 리스트 반환
    
    Args:
        directory: 검색할 디렉토리 (기본: "/Game")
        recursive: 하위 디렉토리 포함 여부
    
    Returns:
        List[str]: 에셋 경로 리스트
    """
    return EAL.list_assets(directory, recursive=recursive)


def load_asset(asset_path: str) -> Optional[unreal.Object]:
    """
    에셋 경로로 에셋 로드
    
    Args:
        asset_path: 에셋 경로 (예: "/Game/MyFolder/MyAsset")
    
    Returns:
        Optional[unreal.Object]: 로드된 에셋 또는 None
    """
    return EAL.load_asset(asset_path)


def save_asset(asset: unreal.Object, only_if_dirty: bool = True) -> bool:
    """
    에셋 저장
    
    Args:
        asset: 저장할 에셋
        only_if_dirty: 변경된 경우만 저장
    
    Returns:
        bool: 저장 성공 여부
    """
    return EAL.save_asset(asset.get_path_name(), only_if_dirty)


def spawn_actor(actor_class: type, location: unreal.Vector = None, 
                rotation: unreal.Rotator = None) -> Optional[unreal.Actor]:
    """
    레벨에 액터 스폰
    
    Args:
        actor_class: 스폰할 액터 클래스
        location: 스폰 위치 (기본: 원점)
        rotation: 스폰 회전 (기본: 0)
    
    Returns:
        Optional[unreal.Actor]: 스폰된 액터 또는 None
    """
    if location is None:
        location = unreal.Vector(0, 0, 0)
    if rotation is None:
        rotation = unreal.Rotator(0, 0, 0)
    
    return ELL.spawn_actor_from_class(actor_class, location, rotation)


def delete_asset(asset_path: str) -> bool:
    """
    에셋 삭제
    
    Args:
        asset_path: 삭제할 에셋 경로
    
    Returns:
        bool: 삭제 성공 여부
    """
    return EAL.delete_asset(asset_path)


def rename_asset(source_path: str, destination_path: str) -> bool:
    """
    에셋 이름 변경 또는 이동
    
    Args:
        source_path: 원본 경로
        destination_path: 대상 경로
    
    Returns:
        bool: 성공 여부
    """
    return EAL.rename_asset(source_path, destination_path)


def duplicate_asset(source_path: str, destination_path: str) -> Optional[unreal.Object]:
    """
    에셋 복제
    
    Args:
        source_path: 원본 에셋 경로
        destination_path: 복제될 경로
    
    Returns:
        Optional[unreal.Object]: 복제된 에셋 또는 None
    """
    return EAL.duplicate_asset(source_path, destination_path)


def log(message: str, warning: bool = False, error: bool = False):
    """
    Unreal 콘솔에 로그 출력
    
    Args:
        message: 출력할 메시지
        warning: 경고로 출력
        error: 에러로 출력
    """
    if error:
        unreal.log_error(message)
    elif warning:
        unreal.log_warning(message)
    else:
        unreal.log(message)


def get_engine_version() -> str:
    """엔진 버전 반환"""
    return SYS.get_engine_version()


def get_project_directory() -> str:
    """프로젝트 디렉토리 반환"""
    return PATHS.project_dir()


def get_content_directory() -> str:
    """Content 디렉토리 반환"""
    return PATHS.project_content_dir()


# ============================================================================
# 🎯 고급 헬퍼 함수들
# ============================================================================

def get_assets_by_class(asset_class: type, directory: str = "/Game") -> List[unreal.Object]:
    """
    특정 클래스의 모든 에셋 반환
    
    Args:
        asset_class: 에셋 클래스 (예: unreal.StaticMesh)
        directory: 검색 디렉토리
    
    Returns:
        List[unreal.Object]: 에셋 리스트
    """
    asset_paths = list_assets(directory)
    assets = []
    
    for path in asset_paths:
        asset = load_asset(path)
        if asset and isinstance(asset, asset_class):
            assets.append(asset)
    
    return assets


def get_actors_by_tag(tag: str) -> List[unreal.Actor]:
    """
    특정 태그를 가진 액터 반환
    
    Args:
        tag: 검색할 태그
    
    Returns:
        List[unreal.Actor]: 액터 리스트
    """
    all_actors = get_all_actors()
    return [actor for actor in all_actors if tag in actor.tags]


def get_actors_by_name(name_contains: str) -> List[unreal.Actor]:
    """
    이름에 특정 문자열을 포함하는 액터 반환
    
    Args:
        name_contains: 검색할 문자열
    
    Returns:
        List[unreal.Actor]: 액터 리스트
    """
    all_actors = get_all_actors()
    return [actor for actor in all_actors if name_contains.lower() in actor.get_name().lower()]


def batch_rename_assets(assets: List[unreal.Object], prefix: str = "", 
                       suffix: str = "", search: str = "", replace: str = ""):
    """
    에셋 일괄 이름 변경
    
    Args:
        assets: 에셋 리스트
        prefix: 앞에 추가할 문자열
        suffix: 뒤에 추가할 문자열
        search: 검색할 문자열
        replace: 대체할 문자열
    """
    for asset in assets:
        old_path = asset.get_path_name()
        old_name = asset.get_name()
        
        # 이름 변경
        new_name = old_name
        if search and replace:
            new_name = new_name.replace(search, replace)
        if prefix:
            new_name = prefix + new_name
        if suffix:
            new_name = new_name + suffix
        
        # 경로 구성
        directory = old_path.rsplit('/', 1)[0]
        new_path = f"{directory}/{new_name}"
        
        # 이름 변경
        if new_path != old_path:
            rename_asset(old_path, new_path)
            log(f"Renamed: {old_name} -> {new_name}")


def print_selected_assets_info():
    """선택된 에셋 정보 출력"""
    assets = get_selected_assets()
    
    if not assets:
        log("No assets selected", warning=True)
        return
    
    log(f"\n{'='*60}")
    log(f"Selected Assets ({len(assets)}):")
    log(f"{'='*60}")
    
    for asset in assets:
        log(f"\n📦 {asset.get_name()}")
        log(f"   Type: {asset.get_class().get_name()}")
        log(f"   Path: {asset.get_path_name()}")


def print_selected_actors_info():
    """선택된 액터 정보 출력"""
    actors = get_selected_actors()
    
    if not actors:
        log("No actors selected", warning=True)
        return
    
    log(f"\n{'='*60}")
    log(f"Selected Actors ({len(actors)}):")
    log(f"{'='*60}")
    
    for actor in actors:
        loc = actor.get_actor_location()
        rot = actor.get_actor_rotation()
        
        log(f"\n🎭 {actor.get_name()}")
        log(f"   Type: {actor.get_class().get_name()}")
        log(f"   Location: ({loc.x:.2f}, {loc.y:.2f}, {loc.z:.2f})")
        log(f"   Rotation: ({rot.roll:.2f}, {rot.pitch:.2f}, {rot.yaw:.2f})")
        log(f"   Tags: {actor.tags}")


# ============================================================================
# 📚 도움말
# ============================================================================

def help():
    """사용 가능한 바로가기 및 함수 출력"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Unreal Engine Python API 바로가기 모음              ║
╚══════════════════════════════════════════════════════════════╝

📦 Asset Management (에셋 관리):
   EAL  - EditorAssetLibrary       (에셋 로드/저장/삭제)
   AR   - AssetRegistryHelpers     (에셋 검색/쿼리)
   AT   - AssetToolsHelpers        (에셋 생성/Import)

🎬 Level & Actor (레벨 & 액터):
   ELL  - EditorLevelLibrary       (레벨 작업)
   EAS  - EditorActorSubsystem     (액터 관리)
   EFL  - EditorFilterLibrary      (액터 필터링)

🎨 Material & Texture (머티리얼 & 텍스처):
   MEL  - MaterialEditingLibrary   (머티리얼 편집)
   RL   - RenderingLibrary         (렌더타겟)
   TEX  - EditorTextureSubsystem   (텍스처 편집)

🎭 Mesh & Animation (메시 & 애니메이션):
   SML  - EditorStaticMeshLibrary  (스태틱 메시)
   SKL  - EditorSkeletalMeshLibrary(스켈레탈 메시)
   ANI  - EditorAnimationSubsystem (애니메이션)

🔧 Utilities (유틸리티):
   EUL  - EditorUtilityLibrary     (에디터 유틸리티)
   SYS  - SystemLibrary             (시스템 정보)
   STR  - StringLibrary             (문자열)
   MATH - MathLibrary               (수학)
   FILE - BlueprintFileUtilsBPLibrary (파일)

🚀 편의 함수들:
   get_selected_assets()            - 선택된 에셋
   get_selected_actors()            - 선택된 액터
   get_all_actors()                 - 모든 액터
   list_assets(dir)                 - 에셋 리스트
   spawn_actor(class, loc, rot)     - 액터 스폰
   log(msg)                         - 로그 출력
   
   print_selected_assets_info()     - 선택된 에셋 정보 출력
   print_selected_actors_info()     - 선택된 액터 정보 출력

📚 사용 예제:
   from developer.Template import *
   
   # 선택된 에셋 가져오기
   assets = get_selected_assets()
   
   # 액터 스폰
   actor = spawn_actor(unreal.StaticMeshActor)
   
   # 로그 출력
   log(f"엔진 버전: {get_engine_version()}")

상세 정보: help() 또는 개별 객체의 help(EAL) 등
""")


# 모듈 로드 시 간단한 정보 출력
if __name__ != "__main__":
    log(f"✅ Unreal Template 로드 완료 | Engine: {get_engine_version()}")
    log(f"   사용 가능한 바로가기 확인: help()")


# ============================================================================
# 레거시 호환성 (기존 함수명 유지)
# ============================================================================

# 기존 함수명도 유지
listAssetPaths = lambda: [print(p) for p in list_assets()]
getSelectionContentBrowser = lambda: [print(a) for a in get_selected_assets()]
getAllActors = lambda: [print(a) for a in get_all_actors()]
getSelectedActors = lambda: [print(a) for a in get_selected_actors()]
