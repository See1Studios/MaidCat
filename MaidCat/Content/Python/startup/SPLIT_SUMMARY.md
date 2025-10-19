# ✅ init_context.py 분리 완료!

컨텍스트 메뉴 기능이 별도 파일로 분리되었습니다.

## 📝 변경 사항

### Before
```
startup/
└── init_toolbar.py    ← 툴바 + 컨텍스트 메뉴 모두 포함
```

### After
```
startup/
├── init_toolbar.py    ← 툴바 버튼만
└── init_context.py    ← 컨텍스트 메뉴만 ✨
```

## 🎯 분리 이유

1. **관심사 분리**: 툴바와 컨텍스트 메뉴는 별도 기능
2. **유지보수 용이**: 각 파일의 역할이 명확
3. **모듈화**: 독립적으로 enable/disable 가능
4. **확장성**: 각각 독립적으로 확장 가능

## 📦 파일 구조

### init_toolbar.py
```python
# 툴바 버튼 관련
- CreateEntryExample    # MaidCat 버튼
- Run()                 # 툴바 설정 함수
```

### init_context.py ✨
```python
# 컨텍스트 메뉴 관련
- PythonFolderContextMenu   # 폴더 정보
- ReloadPythonModule         # 모듈 리로드
- RunPythonFile              # 파일 실행
- setup_python_context_menu() # 설정 함수
```

## 🚀 사용법

### 자동 로드 (권장)

`startup` 폴더의 모든 Python 파일은 Unreal Editor 시작 시 자동 실행됩니다.

- `init_toolbar.py` → 자동 로드 (현재 비활성화 상태)
- `init_context.py` → **자동 로드 및 실행** ✅

### 수동 로드

```python
# 툴바 버튼만 필요할 때
import startup.init_toolbar as toolbar
toolbar.Run()

# 컨텍스트 메뉴만 필요할 때
import startup.init_context as ctx
ctx.setup_python_context_menu()
```

### 선택적 비활성화

특정 기능을 비활성화하려면 파일 이름 변경:

```
init_context.py → init_context.py.disabled
```

## 🔧 커스터마이징

### 툴바 버튼 추가

`init_toolbar.py`에서:

```python
# 새 버튼 클래스 추가
@unreal.uclass()
class MyToolbarButton(unreal.ToolMenuEntryScript):
    # ...

# Run() 함수 수정
def Run():
    # 기존 버튼
    entry1 = CreateEntryExample()
    # ...
    
    # 새 버튼
    entry2 = MyToolbarButton()
    # ...
```

### 컨텍스트 메뉴 항목 추가

`init_context.py`에서:

```python
# 새 메뉴 클래스 추가
@unreal.uclass()
class MyContextMenu(unreal.ToolMenuEntryScript):
    # ...

# setup_python_context_menu() 함수 수정
def setup_python_context_menu():
    # 기존 메뉴들
    # ...
    
    # 새 메뉴
    my_entry = MyContextMenu()
    my_entry.init_entry(...)
    menu.add_menu_entry_object(my_entry)
```

## 📚 업데이트된 문서

- ✅ `README_ContextMenu.md` - `init_context` 참조로 변경
- ✅ `test_context_menu.py` - `init_context` 임포트로 변경
- ✅ `CONTEXT_MENU_SUMMARY.md` - 자동 로드 설명 추가

## 🧪 테스트

```python
# Python Console에서
import startup.test_context_menu as test
test.run_all_tests()
```

## 💡 활용 예시

### 시나리오 1: 툴바만 사용

```python
# init_context.py 비활성화
# startup/init_context.py → startup/init_context.py.disabled

# init_toolbar.py 활성화
# init_toolbar.py 마지막 줄 주석 해제
Run()
```

### 시나리오 2: 컨텍스트 메뉴만 사용 (현재 기본)

```python
# init_context.py: 자동 로드됨 ✅
# init_toolbar.py: Run() 주석 처리 상태
```

### 시나리오 3: 둘 다 사용

```python
# init_context.py: 자동 로드됨 ✅
# init_toolbar.py: Run() 주석 해제
```

## 🎊 완료!

이제 각 기능이 독립적으로 관리됩니다:

- ✅ **깔끔한 구조**: 툴바 vs 컨텍스트 메뉴 분리
- ✅ **유지보수 용이**: 파일별 역할 명확
- ✅ **자동 로드**: startup 폴더 활용
- ✅ **유연한 활성화**: 개별적으로 enable/disable

---

**분리 완료일**: 2025-10-18  
**파일**: `init_context.py` (컨텍스트 메뉴)  
**호환성**: UE 5.0+
