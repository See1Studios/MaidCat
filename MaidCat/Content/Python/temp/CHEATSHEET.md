# 🚀 Unreal Python 바로가기 치트시트

빠른 참조용 핵심 바로가기 모음

## 📋 Import

```python
from developer.Template import *
```

## 🎯 가장 많이 사용하는 것들

| 작업 | 코드 |
|-----|------|
| **선택된 에셋** | `assets = get_selected_assets()` |
| **선택된 액터** | `actors = get_selected_actors()` |
| **모든 액터** | `all_actors = get_all_actors()` |
| **에셋 로드** | `asset = load_asset("/Game/Path")` |
| **액터 스폰** | `spawn_actor(unreal.Actor, loc, rot)` |
| **로그** | `log("message")` |
| **정보 출력** | `print_selected_assets_info()` |

## 📦 바로가기 목록

### 에셋 (Asset)
- `EAL` - EditorAssetLibrary (로드/저장/삭제)
- `AR` - AssetRegistryHelpers (검색/쿼리)
- `AT` - AssetToolsHelpers (생성/Import)

### 액터 & 레벨 (Actor & Level)
- `ELL` - EditorLevelLibrary (레벨 작업)
- `EAS` - EditorActorSubsystem (액터 관리)
- `EFL` - EditorFilterLibrary (필터링)

### 머티리얼 & 텍스처 (Material & Texture)
- `MEL` - MaterialEditingLibrary (편집)
- `RL` - RenderingLibrary (렌더타겟)

### 메시 (Mesh)
- `SML` - EditorStaticMeshLibrary (스태틱)
- `SKL` - EditorSkeletalMeshLibrary (스켈레탈)

### 유틸리티 (Utility)
- `EUL` - EditorUtilityLibrary (에디터)
- `SYS` - SystemLibrary (시스템)
- `STR` - StringLibrary (문자열)
- `MATH` - MathLibrary (수학)
- `FILE` - BlueprintFileUtilsBPLibrary (파일)
- `PATHS` - Paths (경로)

## 💻 코드 스니펫

### 에셋 작업

```python
# 선택된 에셋에 접두사 추가
assets = get_selected_assets()
batch_rename_assets(assets, prefix="NEW_")

# 스태틱 메시만 필터
meshes = [a for a in assets if isinstance(a, unreal.StaticMesh)]

# 에셋 저장
for asset in assets:
    save_asset(asset)
```

### 액터 작업

```python
# 선택된 액터 이동
actors = get_selected_actors()
for actor in actors:
    loc = actor.get_actor_location()
    actor.set_actor_location(loc + unreal.Vector(0, 0, 100))

# 태그로 찾기
important = get_actors_by_tag("Important")

# 클래스로 찾기
lights = get_all_actors(unreal.Light)
```

### 머티리얼 작업

```python
# 선택된 스태틱 메시의 머티리얼 교체
meshes = get_selected_assets()
new_material = load_asset("/Game/Materials/NewMat")

for mesh in meshes:
    if isinstance(mesh, unreal.StaticMesh):
        mesh.set_material(0, new_material)
```

### 레벨 정리

```python
# 특정 이름 포함 액터 삭제
actors = get_all_actors()
for actor in actors:
    if "Temp" in actor.get_name():
        ELL.destroy_actor(actor)
```

## 🎨 Qt UI 빠른 시작

```python
# 간단한 다이얼로그
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_simple_example.py').read())

# UI 로더
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())
```

## 🔧 유용한 원라이너

```python
# 엔진 버전
log(SYS.get_engine_version())

# 선택 개수
log(f"Selected: {len(get_selected_assets())} assets, {len(get_selected_actors())} actors")

# 프로젝트 경로
log(PATHS.project_dir())

# 모든 액터 개수
log(f"Total actors: {len(get_all_actors())}")
```

## 📚 도움말

```python
# 전체 도움말
help()

# 특정 라이브러리
help(EAL)
```

## 🎯 일반적인 워크플로우

### 1. 에셋 일괄 처리

```python
from developer.Template import *

# 에셋 선택
assets = get_selected_assets()

# 작업 수행
with unreal.ScopedSlowTask(len(assets), "Processing") as task:
    task.make_dialog(True)
    for asset in assets:
        task.enter_progress_frame(1, asset.get_name())
        # 작업...
        save_asset(asset)
```

### 2. 레벨 정리

```python
from developer.Template import *

# 조건에 맞는 액터 찾기
actors = get_all_actors()
to_delete = [a for a in actors if "Temp" in a.get_name()]

# 삭제
for actor in to_delete:
    log(f"Deleting {actor.get_name()}")
    ELL.destroy_actor(actor)
```

### 3. 정보 수집

```python
from developer.Template import *

# 선택 정보
print_selected_assets_info()
print_selected_actors_info()

# 또는 커스텀
for actor in get_selected_actors():
    log(f"{actor.get_name()} at {actor.get_actor_location()}")
```

---

**더 많은 정보**: `README_Template.md` 참조
