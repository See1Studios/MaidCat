# 🎉 Python 유틸리티 통합 완료!

## 📋 변경 사항 요약

### ✅ 통합된 파일들
1. **Template.py** (v2.0) - 30+ API 바로가기, 많은 편의 함수
2. **template2.py** (v1.0) - 기본 바로가기
3. **UnrealShortcuts.py** - 검증된 API 버전

### 🎯 새로운 구조

```
Content/Python/
├── util/                          ← 새로운 통합 위치!
│   ├── __init__.py
│   ├── helper.py             ← 여기 사용!
│   ├── README.md                 ← 전체 문서
│   └── MIGRATION.md              ← 마이그레이션 가이드
│
├── developer/
│   └── _deprecated/              ← 백업 (참고용)
│       ├── Template.py
│       ├── template2.py
│       ├── UnrealShortcuts.py
│       └── README.md
│
└── MIGRATION_NOTICE.py           ← 이 공지
```

## 🚀 빠른 시작

### Unreal Editor에서 사용

```python
# 1. 임포트
from util.helper import *

# 2. 도움말 보기
help()

# 3. 바로 사용!
print_selected_info()
actors = get_selected_actors()
```

## 🔄 기존 코드 업데이트

### Import만 변경하면 됩니다!

```python
# ❌ 기존
from developer.Template import *

# ✅ 새로운
from util.helper import *
```

**그게 전부입니다!** 모든 변수명과 함수명이 동일합니다.

## 📚 주요 기능

### API 바로가기
```python
EAL   # EditorAssetLibrary - 에셋 관리
ELL   # EditorLevelLibrary - 레벨 관리
EAS   # EditorActorSubsystem (UE5+)
MEL   # MaterialEditingLibrary
SML   # StaticMeshLibrary
# ... 그 외 20+개
```

### 편의 함수 (40+개)
```python
# 선택
get_selected_assets()
get_selected_actors()
get_all_actors(class)
get_actors_by_name(str)
get_actors_by_tag(tag)

# 에셋
load_asset(path)
save_asset(asset)
list_assets(dir)
batch_rename_assets(...)

# 액터
spawn_actor(class, loc, rot)
batch_set_actor_property(...)

# 정보
print_selected_info()
print_actor_hierarchy()
get_engine_version()
```

## 🎁 새로 추가된 기능

### 1. 향상된 검색
```python
cameras = get_actors_by_name("Camera")
materials = get_assets_by_class(unreal.Material)
```

### 2. 일괄 처리
```python
batch_rename_assets(assets, prefix="NEW_")
batch_set_actor_property(actors, "mobility", value)
```

### 3. 상세 정보
```python
print_selected_info()      # 선택 정보 출력
print_actor_hierarchy()    # 계층 구조
```

## ✨ 장점

1. ✅ **단일 진입점**: 하나의 모듈로 모든 기능
2. ✅ **하위 호환성**: 기존 코드 그대로 작동
3. ✅ **버전 호환**: UE 4.27 - 5.5+ 자동 감지
4. ✅ **타입 안전**: Pylance 에러 없음
5. ✅ **풍부한 문서**: README + 마이그레이션 가이드
6. ✅ **레거시 지원**: 구버전 함수명도 사용 가능

## 📖 자세한 문서

### README.md
전체 API 문서, 사용 예제, 팁
```
Content/Python/util/README.md
```

### MIGRATION.md
단계별 마이그레이션 가이드, 예제, 트러블슈팅
```
Content/Python/util/MIGRATION.md
```

## 💡 실전 예제

### 예제 1: 선택된 액터 일괄 수정
```python
from util.helper import *

actors = get_selected_actors()
batch_set_actor_property(actors, "mobility", unreal.ComponentMobility.MOVABLE)
log(f"{len(actors)}개 액터 수정 완료!")
```

### 예제 2: 머티리얼 검색 및 수정
```python
from util.helper import *

materials = get_assets_by_class(unreal.Material, "/Game/Materials")
for mat in materials:
    log(f"Found: {mat.get_name()}")
```

### 예제 3: 라이트 배치
```python
from util.helper import *

for i in range(10):
    loc = unreal.Vector(i * 100, 0, 200)
    light = spawn_actor(unreal.PointLight, loc)
    log(f"Light created: {light.get_name()}")
```

## ⚠️ 중요 공지

### 1. 구 파일 위치
기존 파일들은 `developer/_deprecated/`로 이동:
- 삭제되지 않았습니다 (백업 유지)
- 새 코드에서는 사용하지 마세요
- 참고용으로만 보관

### 2. Import 업데이트 필요
프로젝트 내 모든 Python 파일에서:
```python
# 찾기 (Ctrl+Shift+F)
from developer.Template
from developer.template2
from developer.UnrealShortcuts

# 바꾸기
from util.helper
```

### 3. 동시 Import 금지
```python
# ❌ 충돌 가능
from developer.Template import *
from util.helper import *

# ✅ 하나만 사용
from util.helper import *
```

## 🎓 학습 경로

1. **시작**: `from util.helper import *; help()`
2. **문서**: `util/README.md` 읽기
3. **예제**: README의 예제 실행
4. **마이그레이션**: 기존 코드 업데이트
5. **활용**: 새 기능들 프로젝트에 적용

## 📞 도움말

### Unreal Editor에서
```python
from util.helper import *
help()  # 전체 API 목록
```

### 문서
- **README**: 전체 기능 설명
- **MIGRATION**: 단계별 가이드
- **_deprecated/README**: 구버전 정보

## ✅ 체크리스트

- [ ] `from util.helper import *` 테스트
- [ ] `help()` 실행해서 기능 확인
- [ ] `print_selected_info()` 테스트
- [ ] 기존 스크립트 import 업데이트
- [ ] README.md 읽기
- [ ] 새로운 편의 함수 활용

---

## 🎊 완료!

이제 **더 깔끔하고 강력한 통합 유틸리티**를 사용할 수 있습니다!

**Happy Coding in Unreal!** 🚀

---

**통합 완료일**: 2025년 10월 18일  
**버전**: v3.0 (Unified)  
**호환**: UE 4.27 - 5.5+

