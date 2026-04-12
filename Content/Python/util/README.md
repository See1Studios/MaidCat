# Unreal Python Utilities

통합된 Unreal Engine Python 유틸리티 모듈입니다.

> **v3.0** - Template.py, template2.py, UnrealShortcuts.py 통합 버전  
> UE 4.27 - 5.5+ 호환

## 📦 설치 및 사용

### 기본 사용법

```python
# Unreal Editor의 Python Console에서

# 방법 1: 모든 바로가기 임포트 (권장)
from util.helper import *

help()  # 도움말 보기
print_selected_info()  # 선택된 것들 정보

# 방법 2: 네임스페이스로 사용
from util import helper as ue
actors = ue.get_selected_actors()

# 방법 3: 특정 함수만
from util.helper import get_selected_assets, spawn_actor
```

## 🎯 주요 기능

### 1. API 바로가기

빠른 접근을 위한 주요 API 바로가기:

```python
# 에셋 관리
EAL  # EditorAssetLibrary
AR   # AssetRegistryHelpers
AT   # AssetToolsHelpers

# 레벨 & 액터
ELL  # EditorLevelLibrary
EAS  # EditorActorSubsystem (UE5+)
EFL  # EditorFilterLibrary

# 머티리얼 & 렌더링
MEL  # MaterialEditingLibrary
ML   # MaterialLibrary
RL   # RenderingLibrary

# 메시
SML  # EditorStaticMeshLibrary
SKL  # EditorSkeletalMeshLibrary

# 유틸리티
EUL  # EditorUtilityLibrary
SYS  # SystemLibrary
STR  # StringLibrary
MATH # MathLibrary
FILE # BlueprintFileUtilsBPLibrary
PATHS# Paths
```

### 2. 편의 함수

#### 선택 관련

```python
# Content Browser 선택
assets = get_selected_assets()

# 레벨 액터 선택
actors = get_selected_actors()

# 모든 액터
all_actors = get_all_actors()
lights = get_all_actors(unreal.Light)  # 특정 클래스만

# 이름으로 검색
cameras = get_actors_by_name("Camera")

# 태그로 검색
tagged = get_actors_by_tag("Important")

# 선택 정보 출력
print_selected_info()
```

#### 에셋 관련

```python
# 에셋 로드/저장
asset = load_asset("/Game/MyAsset")
save_asset(asset)

# 에셋 리스트
paths = list_assets("/Game/Materials")

# 클래스로 필터링
materials = get_assets_by_class(unreal.Material, "/Game")

# 이름 변경 및 복제
rename_asset("/Game/Old", "/Game/New")
duplicate_asset("/Game/Asset", "/Game/Asset_Copy")

# 삭제
delete_asset("/Game/Unused")
```

#### 액터 관련

```python
# 액터 스폰
location = unreal.Vector(0, 0, 100)
rotation = unreal.Rotator(0, 0, 0)
light = spawn_actor(unreal.PointLight, location, rotation)

# 에셋에서 스폰
mesh = load_asset("/Game/MyMesh")
actor = spawn_actor_from_object(mesh, location)

# 계층 구조 출력
print_actor_hierarchy(actor)
```

#### 일괄 처리

```python
# 에셋 일괄 이름 변경
assets = get_selected_assets()
batch_rename_assets(assets, prefix="NEW_")
batch_rename_assets(assets, search="Old", replace="New")

# 프로퍼티 일괄 설정
actors = get_selected_actors()
batch_set_actor_property(actors, "mobility", unreal.ComponentMobility.MOVABLE)
```

#### 로깅

```python
log("일반 로그")
log("경고!", warning=True)
log("에러 발생!", error=True)
```

#### 시스템 정보

```python
version = get_engine_version()
proj_dir = get_project_dir()
content_dir = get_content_dir()
saved_dir = get_saved_dir()
plugins_dir = get_plugins_dir()

# 월드 컨텍스트 (Material Parameter Collection 등에 필요)
world = get_editor_world()
```

#### Material Parameter Collection 사용

```python
# 월드 컨텍스트 가져오기
world = get_editor_world()

# Collection 로드
collection = load_asset("/Game/MyCollection")

# 값 가져오기
vector_val = ML.get_vector_parameter_value(world, collection, unreal.Name("MyVector"))
scalar_val = ML.get_scalar_parameter_value(world, collection, unreal.Name("MyScalar"))

# 값 설정
ML.set_vector_parameter_value(world, collection, unreal.Name("MyVector"), 
                               unreal.LinearColor(1, 0, 0, 1))
ML.set_scalar_parameter_value(world, collection, unreal.Name("MyScalar"), 1.0)
```

## 🔄 마이그레이션 가이드

기존 코드를 새 유틸리티로 마이그레이션:

### Template.py / template2.py / UnrealShortcuts.py에서

```python
# 기존 코드
from developer.Template import *
# 또는
from developer.template2 import *
# 또는
from developer.UnrealShortcuts import *

# 새 코드
from util.helper import *
```

모든 변수명과 함수명이 동일하므로 **임포트만 변경**하면 됩니다!

### 레거시 함수 지원

기존 함수들도 그대로 작동합니다:

```python
listAssetPaths()              # 에셋 경로 출력
getSelectionContentBrowser()  # 선택된 에셋 출력
getAllActors()                # 모든 액터 출력
getSelectedActors()           # 선택된 액터 출력

# 구버전 변수명
at          # = AT
atHelper    # = AT
arHelper    # = AR
matLib      # = ML
strLib      # = STR
sysLib      # = SYS
bpfuLib     # = FILE
engineVersion  # = get_engine_version()
```

## ✅ 호환성

- **UE 4.27** ✓
- **UE 5.0 - 5.5+** ✓
- 자동 버전 감지
- UE4/UE5 Fallback 지원
- Pylance 타입 에러 없음
- 최신 Unreal API 사용 (deprecated 함수 회피)

## 📚 도움말

Unreal Editor에서:

```python
from util.helper import *
help()  # 전체 도움말 출력
```

## 🗂️ 파일 구조

```
Content/Python/
├── util/
│   ├── __init__.py
│   └── helper.py      ← 통합 유틸리티 (여기 사용!)
│
└── developer/
    └── _deprecated/        ← 구버전 파일들 (참고용)
        ├── Template.py
        ├── template2.py
        └── UnrealShortcuts.py
```

## 🎯 빠른 시작 예제

```python
from util.helper import *

# 1. 선택된 것들 확인
print_selected_info()

# 2. 모든 라이트 찾기
lights = get_all_actors(unreal.Light)
log(f"라이트 {len(lights)}개 발견")

# 3. 선택된 에셋 이름 변경
assets = get_selected_assets()
batch_rename_assets(assets, prefix="NEW_")

# 4. 새 액터 스폰
loc = unreal.Vector(0, 0, 200)
light = spawn_actor(unreal.PointLight, loc)
log(f"라이트 생성: {light.get_name()}")

# 5. 머티리얼 찾기
materials = get_assets_by_class(unreal.Material, "/Game/Materials")
log(f"머티리얼 {len(materials)}개 발견")

# 6. Material Parameter Collection 사용
world = get_editor_world()
collection = load_asset("/Game/MyCollection")
value = ML.get_vector_parameter_value(world, collection, unreal.Name("MyParam"))
log(f"파라미터 값: {value}")
```

## 💡 팁

1. **도움말 항상 활용**: `help()` 함수로 전체 API 확인
2. **타입 힌트**: IDE에서 자동완성 지원
3. **에러 처리**: 모든 함수가 안전하게 예외 처리
4. **버전 호환**: UE4/UE5 자동 감지 및 Fallback
5. **월드 컨텍스트**: `get_editor_world()` 함수로 간편하게 가져오기
6. **Deprecated 회피**: 최신 Unreal API 사용 (예: UnrealEditorSubsystem)

## 📝 업데이트 로그

### v3.0.1 (2025-10-18)
- ✅ `get_editor_world()` 헬퍼 함수 추가
- ✅ Deprecated API 회피 (EditorLevelLibrary.get_editor_world → UnrealEditorSubsystem)
- ✅ Material Parameter Collection 사용 예제 추가

### v3.0 (2025-10-18)
- ✅ Template.py, template2.py, UnrealShortcuts.py 통합
- ✅ `util` 모듈로 재구성
- ✅ 레거시 호환성 유지
- ✅ 더 많은 편의 함수 추가
- ✅ 완전한 문서화

---

**문의사항**: 이슈 또는 PR로 제안해주세요!

