# ⚠️ DEPRECATED

이 폴더의 파일들은 더 이상 사용되지 않습니다.

## 새 위치

모든 기능이 통합되어 이동되었습니다:

```
Content/Python/util/helper.py
```

## 마이그레이션

기존 코드를 업데이트하세요:

```python
# ❌ 기존
from developer.Template import *
from developer.template2 import *
from developer.UnrealShortcuts import *

# ✅ 새로운
from util.helper import *
```

**모든 변수명과 함수명이 동일하므로 import만 변경하면 됩니다!**

## 자세한 가이드

- 📚 README: `Content/Python/util/README.md`
- 🔄 마이그레이션 가이드: `Content/Python/util/MIGRATION.md`

## 레거시 파일 목록

- `Template.py` - v2.0, 30+ API 바로가기
- `template2.py` - v1.0, 기본 바로가기
- `UnrealShortcuts.py` - 검증된 버전

이 파일들은 참고용으로만 보관되며, 새 프로젝트에서는 **util.unreal_api를 사용**하세요.

---

**Deprecated Date**: 2025-10-18
