# Python Context Menu Setup

Content Browser의 Python 폴더에서만 활성화되는 컨텍스트 메뉴 기능입니다.

## 🎯 기능

### 1. 📁 Python 폴더 정보
- Python 폴더 또는 그 하위 폴더/파일에서만 표시
- 선택된 항목 정보를 로그에 출력

### 2. 🔄 Python 모듈 리로드
- `.py` 파일을 선택했을 때만 활성화
- 선택된 Python 모듈을 리로드
- 코드 수정 후 Unreal 재시작 없이 테스트 가능

### 3. ▶️ Python 파일 실행
- `.py` 파일을 선택했을 때만 활성화
- 선택된 Python 파일을 즉시 실행
- 스크립트 빠른 테스트에 유용

## 📦 설치

### init_context.py 파일

`Content/Python/startup/init_context.py` 파일에 기능이 구현되어 있습니다.

### 자동 활성화

`startup` 폴더의 Python 파일은 Unreal Editor 시작 시 자동 실행됩니다.
`init_context.py`는 자동으로 로드되어 컨텍스트 메뉴를 설정합니다.

## 🚀 사용법

### 1. Unreal Editor 시작 시 자동 로드

`Content/Python/startup/` 폴더의 Python 파일은 Unreal Editor 시작 시 자동 실행됩니다.

`init_toolbar.py`의 마지막 줄 주석을 해제하세요:

```python
# 컨텍스트 메뉴 설정 실행
setup_python_context_menu()  # ← 주석 제거!
```

### 2. 수동 실행

Python Console에서:

```python
import startup.init_context as ctx
import importlib
importlib.reload(ctx)
ctx.setup_python_context_menu()
```

### 3. Content Browser에서 사용

1. Content Browser에서 `/Game/Python` 폴더로 이동
2. Python 파일(`.py`) 또는 폴더를 **오른쪽 클릭**
3. 컨텍스트 메뉴에서 **"Python"** 섹션 찾기:
   - 📁 **Python 폴더 정보**
   - 🔄 **Python 모듈 리로드** (`.py` 파일만)
   - ▶️ **Python 파일 실행** (`.py` 파일만)

## 💡 사용 예제

### 예제 1: 모듈 리로드

```
1. Content/Python/util/helper.py 수정
2. Content Browser에서 helper.py 우클릭
3. "Python" → "🔄 Python 모듈 리로드" 선택
4. Output Log 확인: "✅ 리로드 성공: util.helper"
```

### 예제 2: 스크립트 실행

```
1. Content/Python/developer/temp.py 작성
2. Content Browser에서 temp.py 우클릭
3. "Python" → "▶️ Python 파일 실행" 선택
4. 스크립트 즉시 실행
```

### 예제 3: 폴더 정보

```
1. Content Browser에서 Python 폴더 우클릭
2. "Python" → "📁 Python 폴더 정보" 선택
3. Output Log에서 선택된 경로 확인
```

## 🔧 고급 설정

### 메뉴 항목 추가

새로운 메뉴 항목을 추가하려면:

```python
@unreal.uclass()
class MyCustomMenu(unreal.ToolMenuEntryScript):
    
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """메뉴 활성화 조건"""
        # Python 폴더인지 체크
        selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
        return any("/Game/Python" in folder for folder in selected_folders)
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """메뉴 클릭 시 실행"""
        unreal.log("내 커스텀 메뉴 실행!")
        # 여기에 원하는 기능 구현

# setup_python_context_menu() 함수 안에서:
custom_entry = MyCustomMenu()
custom_entry.init_entry(
    menu_owner,
    "myCustomMenu",
    "Python",
    "내 커스텀 메뉴",
    "설명"
)
custom_entry.data.menu = menu_name
menu.add_menu_entry_object(custom_entry)
```

### 다른 폴더에도 적용

`can_execute` 메서드에서 경로 조건 변경:

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    # 다른 폴더 패턴
    return any("/Game/MyFolder" in folder for folder in selected_folders)
```

## 📝 주의사항

### 1. Python 파일 경로 매핑

Content Browser의 에셋 경로를 Python 모듈 경로로 변환:

```
/Game/Python/util/helper.py → util.helper
/Game/Python/developer/temp.py → developer.temp
```

### 2. 실행 vs 리로드

- **실행**: 파일을 읽고 `exec()`로 실행 (일회성 스크립트)
- **리로드**: `importlib.reload()`로 모듈 새로고침 (import된 모듈)

### 3. 에러 처리

- 모든 에러는 Output Log에 표시됩니다
- ✅ = 성공, ❌ = 실패

## 🐛 트러블슈팅

### Q: 메뉴가 보이지 않아요

**A**: 
1. `setup_python_context_menu()` 주석 해제 확인
2. Unreal Editor 재시작
3. Python Console에서 수동 실행

### Q: "리로드 성공"인데 변경사항이 반영 안 돼요

**A**:
1. 이미 import한 변수/함수는 재할당 필요:
```python
from util import helper as uh
importlib.reload(uh)  # 리로드 후
# 다시 사용
actors = uh.get_selected_actors()
```

2. 또는 Unreal Editor 재시작

### Q: 실행이 안 돼요

**A**:
1. 파일 경로 확인 (Content/Python 폴더 안에 있어야 함)
2. Python 문법 에러 확인
3. Output Log에서 에러 메시지 확인

## 🎨 커스터마이징 아이디어

### 1. Python 파일 포맷팅
```python
# Black 포맷터 실행
def format_python_file(file_path):
    import subprocess
    subprocess.run(['black', file_path])
```

### 2. 테스트 실행
```python
# pytest 실행
def run_tests(file_path):
    import pytest
    pytest.main([file_path])
```

### 3. 문서 생성
```python
# docstring에서 마크다운 생성
def generate_docs(module_path):
    import pydoc
    # 문서 생성 로직
```

## 📚 관련 문서

- [Unreal Engine Tool Menus](https://docs.unrealengine.com/5.0/en-US/PythonAPI/class/ToolMenus.html)
- [Editor Utility Library](https://docs.unrealengine.com/5.0/en-US/PythonAPI/class/EditorUtilityLibrary.html)
- [ToolMenuEntryScript](https://docs.unrealengine.com/5.0/en-US/PythonAPI/class/ToolMenuEntryScript.html)

---

**작성일**: 2025-10-18  
**호환성**: UE 5.0+
