# 마이그레이션 가이드

기존 Template.py, template2.py, UnrealShortcuts.py에서 새로운 통합 유틸리티로 마이그레이션하는 가이드입니다.

## 🚀 빠른 마이그레이션

### 1단계: Import 변경

```python
# ❌ 기존 코드
from developer.Template import *
# 또는
from developer.template2 import *
# 또는
from developer.UnrealShortcuts import *

# ✅ 새 코드
from util.helper import *
```

**그게 전부입니다!** 나머지 코드는 변경 없이 그대로 작동합니다.

## 📋 변경 사항 없는 항목들

### API 바로가기 (그대로 사용 가능)

```python
# 모두 동일하게 작동
EAL   # EditorAssetLibrary
AR    # AssetRegistryHelpers
AT    # AssetToolsHelpers
ELL   # EditorLevelLibrary
EAS   # EditorActorSubsystem
EFL   # EditorFilterLibrary
MEL   # MaterialEditingLibrary
ML    # MaterialLibrary
RL    # RenderingLibrary
SML   # EditorStaticMeshLibrary
SKL   # EditorSkeletalMeshLibrary
EUL   # EditorUtilityLibrary
SYS   # SystemLibrary
STR   # StringLibrary
MATH  # MathLibrary
FILE  # BlueprintFileUtilsBPLibrary
PATHS # Paths
```

### 주요 함수 (그대로 사용 가능)

```python
# 선택
get_selected_assets()
get_selected_actors()
get_all_actors()

# 에셋
load_asset()
save_asset()
delete_asset()
rename_asset()
duplicate_asset()
list_assets()

# 액터
spawn_actor()

# 로깅
log()

# 정보
get_engine_version()
get_project_dir()
get_content_dir()
```

### 레거시 함수 (하위 호환성)

```python
# 구버전 함수들도 계속 작동
listAssetPaths()
getSelectionContentBrowser()
getAllActors()
getSelectedActors()

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

## ✨ 새로 추가된 기능

마이그레이션 시 활용할 수 있는 새 기능들:

### 1. 향상된 검색

```python
# 이름으로 액터 찾기
cameras = get_actors_by_name("Camera")

# 태그로 액터 찾기
tagged = get_actors_by_tag("Important")

# 클래스로 에셋 찾기
materials = get_assets_by_class(unreal.Material, "/Game")
```

### 2. 일괄 처리

```python
# 에셋 일괄 이름 변경
assets = get_selected_assets()
batch_rename_assets(assets, prefix="NEW_")
batch_rename_assets(assets, search="Old", replace="New")

# 프로퍼티 일괄 설정
actors = get_selected_actors()
batch_set_actor_property(actors, "mobility", unreal.ComponentMobility.MOVABLE)
```

### 3. 정보 출력

```python
# 선택 정보 상세 출력
print_selected_info()

# 액터 계층 구조
print_actor_hierarchy(root_actor)
```

### 4. 추가 경로 함수

```python
get_saved_dir()      # Saved 폴더
get_plugins_dir()    # Plugins 폴더
```

## 📝 실제 마이그레이션 예제

### 예제 1: 간단한 스크립트

**기존 코드:**
```python
from developer.Template import *

actors = get_selected_actors()
for actor in actors:
    log(actor.get_name())
```

**새 코드:**
```python
from util.helper import *

actors = get_selected_actors()
for actor in actors:
    log(actor.get_name())
```

### 예제 2: 에셋 일괄 처리

**기존 코드:**
```python
from developer.template2 import *

assets = EUL.get_selected_assets()
for asset in assets:
    old_path = asset.get_path_name()
    old_name = asset.get_name()
    new_name = "NEW_" + old_name
    directory = old_path.rsplit('/', 1)[0]
    new_path = f"{directory}/{new_name}"
    EAL.rename_asset(old_path, new_path)
```

**새 코드 (더 간단):**
```python
from util.helper import *

assets = get_selected_assets()
batch_rename_assets(assets, prefix="NEW_")
```

### 예제 3: 액터 검색 및 수정

**기존 코드:**
```python
from developer.Template import *

all_actors = get_all_actors()
lights = []
for actor in all_actors:
    if isinstance(actor, unreal.Light):
        lights.append(actor)

for light in lights:
    light.set_editor_property("intensity", 1000)
```

**새 코드 (더 간단):**
```python
from util.helper import *

lights = get_all_actors(unreal.Light)
batch_set_actor_property(lights, "intensity", 1000)
```

## ⚠️ 주의사항

### 1. 파일 경로

기존 파일들은 `developer/_deprecated/`로 이동되었습니다:

```
developer/_deprecated/Template.py         (백업)
developer/_deprecated/template2.py        (백업)
developer/_deprecated/UnrealShortcuts.py  (백업)
```

### 2. 동시 Import 금지

```python
# ❌ 하지 마세요
from developer.Template import *
from util.helper import *  # 충돌 가능

# ✅ 하나만 사용
from util.helper import *
```

### 3. 기존 스크립트 파일

프로젝트 내 다른 Python 파일들에서 기존 모듈을 import하고 있다면:

```bash
# 프로젝트 전체에서 찾기 (VS Code)
Ctrl+Shift+F
검색: "from developer.Template"
```

모두 `from util.helper`로 변경하세요.

## 🔧 트러블슈팅

### Q: "ModuleNotFoundError: No module named 'developer.Template'" 에러

**A**: 이미 마이그레이션 완료! import를 변경하세요:
```python
from util.helper import *
```

### Q: 기존 함수가 작동하지 않음

**A**: 모든 레거시 함수는 지원됩니다. 확인사항:
1. Import가 올바른지 확인
2. `help()` 함수로 사용 가능한 함수 목록 확인
3. Unreal Editor 재시작

### Q: EAS (EditorActorSubsystem)가 None

**A**: UE4를 사용 중이거나 UE5에서 해당 기능 미지원:
- `get_selected_actors()`, `get_all_actors()` 함수는 자동으로 Fallback
- 직접 `EAS` 사용 시 None 체크 필요

```python
if EAS:
    # UE5 방식
    actors = EAS.get_all_level_actors()
else:
    # UE4 Fallback
    actors = ELL.get_all_level_actors()

# 또는 편의 함수 사용 (자동 처리)
actors = get_all_actors()
```

## ✅ 마이그레이션 체크리스트

- [ ] 모든 `from developer.Template import *`를 찾아서 변경
- [ ] 모든 `from developer.template2 import *`를 찾아서 변경
- [ ] 모든 `from developer.UnrealShortcuts import *`를 찾아서 변경
- [ ] `from util.helper import *`로 변경
- [ ] Unreal Editor에서 테스트
- [ ] `help()` 함수로 기능 확인
- [ ] 새로운 편의 함수 활용 검토

## 📞 도움이 필요하면

1. **도움말**: `from util.helper import *; help()`
2. **README**: `Content/Python/util/README.md` 참고
3. **기존 파일**: `developer/_deprecated/` 폴더에서 참고

---

**마이그레이션 완료!** 🎉

이제 더 깔끔하고 강력한 통합 유틸리티를 사용할 수 있습니다.

