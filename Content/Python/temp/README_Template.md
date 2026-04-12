# 🚀 Unreal Engine Python API 바로가기 가이드

Unreal Engine의 주요 유틸리티, 서브시스템, 라이브러리를 쉽게 접근할 수 있는 바로가기 모음입니다.

## 📦 설치 및 사용

### 기본 사용

```python
# Unreal Editor Python 콘솔에서
from developer.Template import *

# 또는 네임스페이스로
import developer.Template as ue

# 선택된 에셋 가져오기
assets = get_selected_assets()
# 또는
assets = ue.get_selected_assets()
```

### 도움말

```python
# 사용 가능한 모든 바로가기 보기
help()

# 특정 라이브러리 도움말
help(EAL)  # EditorAssetLibrary 도움말
```

## 📚 바로가기 레퍼런스

### 📦 Asset Management (에셋 관리)

#### EAL - EditorAssetLibrary
Content Browser 에셋 작업의 핵심

```python
# 에셋 로드
asset = EAL.load_asset("/Game/MyFolder/MyAsset")

# 에셋 저장
EAL.save_asset("/Game/MyFolder/MyAsset")

# 에셋 삭제
EAL.delete_asset("/Game/MyFolder/OldAsset")

# 에셋 이름 변경
EAL.rename_asset("/Game/Old", "/Game/New")

# 에셋 복제
EAL.duplicate_asset("/Game/Original", "/Game/Copy")

# 에셋 리스트
assets = EAL.list_assets("/Game", recursive=True)

# 에셋 존재 확인
exists = EAL.does_asset_exist("/Game/MyAsset")
```

#### AR - AssetRegistryHelpers
복잡한 에셋 검색 및 쿼리

```python
# Asset Registry 가져오기
registry = AR.get_asset_registry()

# 에셋 데이터 가져오기
asset_data = registry.get_asset_by_object_path("/Game/MyAsset")

# 클래스별 에셋 검색
static_meshes = registry.get_assets_by_class("StaticMesh")
```

#### AT - AssetToolsHelpers
에셋 생성 및 Import

```python
# Asset Tools 가져오기
tools = AT.get_asset_tools()

# 에셋 Import
```

---

### 🎬 Level & Actor Management (레벨 & 액터)

#### ELL - EditorLevelLibrary
레벨 작업의 기본

```python
# 액터 스폰
actor = ELL.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(0, 0, 0),
    unreal.Rotator(0, 0, 0)
)

# 액터 삭제
ELL.destroy_actor(actor)

# 레벨 저장
ELL.save_current_level()

# 레벨 로드
ELL.load_level("/Game/Maps/MyLevel")

# 모든 액터 가져오기 (deprecated in UE5, use EAS)
actors = ELL.get_all_level_actors()
```

#### EAS - EditorActorSubsystem (UE5+)
액터 관리의 최신 방법

```python
# 서브시스템 가져오기
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# 또는 바로가기 사용
EAS = unreal.EditorActorSubsystem

# 선택된 액터
selected = EAS.get_selected_level_actors()

# 모든 액터
all_actors = EAS.get_all_level_actors()

# 특정 클래스 액터
lights = EAS.get_all_level_actors_of_class(unreal.Light)

# 액터 선택
EAS.set_selected_level_actors([actor1, actor2])

# 액터 스폰
actor = EAS.spawn_actor_from_class(unreal.StaticMeshActor, location)
```

#### EFL - EditorFilterLibrary
액터 필터링

```python
# 클래스로 필터링
static_mesh_actors = EFL.by_actor_class_exact(
    actors,
    unreal.StaticMeshActor
)

# 이름으로 필터링
named_actors = EFL.by_name(actors, "MyActor")

# 태그로 필터링
tagged_actors = EFL.by_actor_tag(actors, "Important")
```

---

### 🎨 Material & Texture (머티리얼 & 텍스처)

#### MEL - MaterialEditingLibrary
머티리얼 생성 및 편집

```python
# 머티리얼 생성
material = MEL.create_material_in_path("/Game/Materials/MyMaterial")

# 텍스처 노드 생성
texture_node = MEL.create_material_expression_texture_2d_parameter(
    material,
    "BaseColor",
    texture_asset
)

# 노드 연결
MEL.connect_material_property(texture_node, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
```

#### RL - RenderingLibrary
렌더타겟 및 캡처

```python
# 스크린샷 캡처
RL.export_render_target(render_target, "D:/Screenshots/shot.png")

# 렌더타겟 클리어
RL.clear_render_target_2d(world_context, render_target)
```

---

### 🎭 Mesh & Animation (메시 & 애니메이션)

#### SML - EditorStaticMeshLibrary
스태틱 메시 편집

```python
# LOD 개수 설정
SML.set_lod_count(static_mesh, 4)

# 콜리전 생성
SML.add_simple_collisions(static_mesh, unreal.ScriptingCollisionShapeType.BOX)

# 라이트맵 해상도 설정
SML.set_lightmap_resolution(static_mesh, 256)

# 버텍스 개수 가져오기
vertex_count = SML.get_number_of_vertices(static_mesh, 0)
```

#### SKL - EditorSkeletalMeshLibrary
스켈레탈 메시 편집

```python
# 본 개수
bone_count = SKL.get_num_bones(skeletal_mesh)

# LOD 개수
lod_count = SKL.get_lod_count(skeletal_mesh)
```

---

### 🔧 Utilities (유틸리티)

#### EUL - EditorUtilityLibrary
에디터 유틸리티 기능

```python
# 선택된 에셋
selected_assets = EUL.get_selected_assets()

# 선택된 에셋 클래스
selected_class = EUL.get_selected_asset_classes()

# 메시지 다이얼로그
result = EUL.show_message("Title", "Message", unreal.AppMsgType.OK_CANCEL)
```

#### SYS - SystemLibrary
시스템 정보

```python
# 엔진 버전
version = SYS.get_engine_version()

# 플랫폼 이름
platform = SYS.get_platform_name()

# 게임 이름
game_name = SYS.get_game_name()

# 콘솔 명령 실행
SYS.execute_console_command(world, "stat fps")
```

#### STR - StringLibrary
문자열 유틸리티

```python
# 문자열 포함 확인
contains = STR.contains(text, search)

# 대소문자 변환
upper = STR.to_upper(text)
lower = STR.to_lower(text)

# 문자열 분리
parts = STR.parse_into_array(text, ",")
```

#### MATH - MathLibrary
수학 함수

```python
# 벡터 연산
distance = MATH.vector_distance(vec1, vec2)
dot = MATH.dot_product_3d(vec1, vec2)

# 회전 연산
rotator = MATH.make_rotator(roll, pitch, yaw)

# 보간
lerp_value = MATH.lerp(a, b, alpha)
```

---

## 🚀 편의 함수 예제

### 에셋 관련

```python
# 선택된 에셋 가져오기
assets = get_selected_assets()

# 에셋 리스트
all_assets = list_assets("/Game/MyFolder")

# 에셋 로드
asset = load_asset("/Game/MyAsset")

# 에셋 저장
save_asset(asset)

# 에셋 삭제
delete_asset("/Game/OldAsset")

# 에셋 이름 변경
rename_asset("/Game/Old", "/Game/New")

# 에셋 복제
duplicate_asset("/Game/Original", "/Game/Copy")

# 특정 클래스 에셋만 가져오기
meshes = get_assets_by_class(unreal.StaticMesh, "/Game")

# 선택된 에셋 정보 출력
print_selected_assets_info()
```

### 액터 관련

```python
# 선택된 액터
actors = get_selected_actors()

# 모든 액터
all_actors = get_all_actors()

# 특정 클래스 액터
lights = get_all_actors(unreal.Light)

# 액터 스폰
actor = spawn_actor(
    unreal.StaticMeshActor,
    location=unreal.Vector(0, 0, 100),
    rotation=unreal.Rotator(0, 45, 0)
)

# 태그로 액터 찾기
tagged = get_actors_by_tag("Important")

# 이름으로 액터 찾기
named = get_actors_by_name("Player")

# 선택된 액터 정보 출력
print_selected_actors_info()
```

### 일괄 작업

```python
# 에셋 일괄 이름 변경
selected = get_selected_assets()
batch_rename_assets(
    selected,
    prefix="NEW_",
    suffix="_v2",
    search="old",
    replace="new"
)
```

### 로깅

```python
# 일반 로그
log("Hello Unreal!")

# 경고
log("Warning message", warning=True)

# 에러
log("Error message", error=True)
```

---

## 💡 실전 예제

### 예제 1: 모든 스태틱 메시에 콜리전 추가

```python
from developer.Template import *

# Content Browser에서 스태틱 메시 선택
meshes = get_selected_assets()

for mesh in meshes:
    if isinstance(mesh, unreal.StaticMesh):
        # 기존 콜리전 제거
        SML.remove_collisions(mesh)
        
        # 박스 콜리전 추가
        SML.add_simple_collisions(
            mesh,
            unreal.ScriptingCollisionShapeType.BOX
        )
        
        log(f"Added collision to {mesh.get_name()}")
```

### 예제 2: 레벨의 모든 라이트 밝기 조정

```python
from developer.Template import *

# 모든 라이트 액터 가져오기
lights = get_all_actors(unreal.Light)

for light in lights:
    # Light 컴포넌트 가져오기
    light_comp = light.get_editor_property('light_component')
    
    if light_comp:
        # 밝기 2배로
        current_intensity = light_comp.get_editor_property('intensity')
        light_comp.set_editor_property('intensity', current_intensity * 2)
        
        log(f"Updated {light.get_name()}: {current_intensity} -> {current_intensity * 2}")
```

### 예제 3: 텍스처 크기 리포트

```python
from developer.Template import *

# 모든 텍스처 가져오기
textures = get_assets_by_class(unreal.Texture2D, "/Game")

log("\n" + "="*60)
log("Texture Size Report")
log("="*60)

total_size = 0

for tex in textures:
    width = tex.get_editor_property('source_width')
    height = tex.get_editor_property('source_height')
    size_bytes = tex.get_resource_size_bytes()
    size_mb = size_bytes / (1024 * 1024)
    
    total_size += size_mb
    
    log(f"\n{tex.get_name()}")
    log(f"  Size: {width}x{height}")
    log(f"  Memory: {size_mb:.2f} MB")

log(f"\nTotal Texture Memory: {total_size:.2f} MB")
log("="*60)
```

### 예제 4: 머티리얼 인스턴스 일괄 생성

```python
from developer.Template import *

# 부모 머티리얼 선택
selected = get_selected_assets()
parent_material = selected[0] if selected else None

if not parent_material:
    log("Please select a parent material!", error=True)
else:
    # 색상 리스트
    colors = {
        'Red': (1, 0, 0),
        'Green': (0, 1, 0),
        'Blue': (0, 0, 1),
        'Yellow': (1, 1, 0),
    }
    
    for name, (r, g, b) in colors.items():
        # 머티리얼 인스턴스 생성
        instance_path = f"/Game/Materials/MI_{name}"
        
        # 인스턴스 생성 (AssetTools 사용)
        factory = unreal.MaterialInstanceConstantFactoryNew()
        factory.initial_parent = parent_material
        
        tools = AT.get_asset_tools()
        instance = tools.create_asset(
            f"MI_{name}",
            "/Game/Materials",
            unreal.MaterialInstanceConstant,
            factory
        )
        
        log(f"Created material instance: MI_{name}")
```

### 예제 5: 레벨 정리 (빈 액터 삭제)

```python
from developer.Template import *

# 모든 액터 가져오기
actors = get_all_actors()

deleted_count = 0

for actor in actors:
    # 이름이 "Empty" 포함하거나
    # 컴포넌트가 없는 액터 삭제
    if "Empty" in actor.get_name() or len(actor.get_components_by_class(unreal.ActorComponent)) == 0:
        ELL.destroy_actor(actor)
        log(f"Deleted: {actor.get_name()}")
        deleted_count += 1

log(f"\nTotal deleted: {deleted_count} actors")
```

---

## 🔧 고급 팁

### 1. 서브시스템 직접 접근

```python
# UE5 서브시스템 직접 가져오기
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
```

### 2. 트랜잭션 사용 (Undo/Redo)

```python
# Undo 가능한 작업
with unreal.ScopedEditorTransaction("My Operation") as trans:
    # 작업 수행
    actor.set_actor_location(new_location)
```

### 3. 프로그레스 바

```python
# 긴 작업에 프로그레스 표시
with unreal.ScopedSlowTask(len(assets), "Processing Assets") as slow_task:
    slow_task.make_dialog(True)
    
    for asset in assets:
        if slow_task.should_cancel():
            break
        
        slow_task.enter_progress_frame(1, f"Processing {asset.get_name()}")
        # 작업 수행
```

---

## 📚 추가 리소스

### 공식 문서
- [Unreal Python API](https://docs.unrealengine.com/5.5/en-US/PythonAPI/)
- [Python Scripting Guide](https://docs.unrealengine.com/5.5/en-US/scripting-the-unreal-editor-using-python/)

### 프로젝트 내 파일
- `Template.py` - 이 바로가기 모듈
- `QtTest.py` - Qt UI 로더
- `qt_template.py` - Qt 템플릿
- `qt_simple_example.py` - 간단한 Qt 예제

---

## 🎯 빠른 참조

### 자주 사용하는 패턴

```python
from developer.Template import *

# 1. 선택된 것들 가져오기
assets = get_selected_assets()
actors = get_selected_actors()

# 2. 정보 출력
print_selected_assets_info()
print_selected_actors_info()

# 3. 일괄 작업
for asset in assets:
    # 작업 수행
    pass

# 4. 로깅
log("작업 완료!")

# 5. 프로젝트 정보
log(f"Engine: {get_engine_version()}")
log(f"Project: {get_project_directory()}")
log(f"Content: {get_content_directory()}")
```

---

## 📝 라이선스

프로젝트 라이선스를 따릅니다.
