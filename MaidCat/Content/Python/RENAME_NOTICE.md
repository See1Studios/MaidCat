# 이름 변경 완료!

## 변경 사항

`unreal_api.py` → `helper.py` ✨

## 새로운 사용법

```python
# 방법 1: 전체 임포트
from util.helper import *

# 방법 2: 네임스페이스 (권장) 
from util import helper as uh
actors = uh.get_selected_actors()

# 방법 3: 특정 함수만
from util.helper import get_selected_assets, spawn_actor
```

## 왜 helper?

- ✅ **더 짧고 간결**: `helper` vs `unreal_api`
- ✅ **직관적**: "헬퍼 함수들" 의미가 명확
- ✅ **타이핑 편함**: `uh` (unreal helper) 약어 사용 가능
- ✅ **관례적**: 다른 프로젝트에서도 `helper` 많이 사용

## 업데이트된 파일

- ✅ `util/helper.py` (이름 변경)
- ✅ `util/__init__.py`
- ✅ `util/README.md`
- ✅ `util/MIGRATION.md`
- ✅ `MIGRATION_NOTICE.py`
- ✅ `CONSOLIDATION_SUMMARY.md`
- ✅ `developer/_deprecated/README.md`
- ✅ `developer/temp.py`

## 테스트

```python
# Unreal Editor에서
from util.helper import *
help()
print_selected_info()
```

모든 기능은 동일하게 작동합니다! 🎉
