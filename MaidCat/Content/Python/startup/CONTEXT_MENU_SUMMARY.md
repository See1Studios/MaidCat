# 🎉 Python Context Menu 추가 완료!

Content Browser의 Python 폴더에서만 활성화되는 컨텍스트 메뉴가 추가되었습니다.

## 📋 추가된 파일

```
Content/Python/startup/
├── init_context.py              ← 컨텍스트 메뉴 기능 ✨
├── init_toolbar.py              ← 툴바 버튼 (기존)
├── README_ContextMenu.md        ← 상세 사용 가이드
├── test_context_menu.py         ← 테스트 도구
└── CONTEXT_MENU_SUMMARY.md      ← 이 파일
```

## 🎯 주요 기능

### 1. 📁 Python 폴더 정보
- `/Game/Python` 폴더 또는 하위 항목에서만 표시
- 선택된 폴더/파일 정보를 Output Log에 출력

### 2. 🔄 Python 모듈 리로드
- `.py` 파일 선택 시에만 활성화
- `importlib.reload()` 사용하여 모듈 새로고침
- 코드 수정 후 에디터 재시작 불필요

### 3. ▶️ Python 파일 실행
- `.py` 파일 선택 시에만 활성화
- 선택된 Python 파일을 즉시 실행
- 빠른 스크립트 테스트에 유용

## 🚀 빠른 시작

### 1단계: 자동 활성화

`startup` 폴더의 `init_context.py`는 Unreal Editor 시작 시 **자동으로 실행**됩니다!

별도 설정 불필요 ✨

### 2단계: 수동 재로드 (선택사항)

변경 후 재로드가 필요하면 Python Console에서:

```python
import startup.init_context as ctx
import importlib
importlib.reload(ctx)
ctx.setup_python_context_menu()
```

### 3단계: 사용

1. Content Browser → `/Game/Python` 폴더
2. Python 파일 또는 폴더 **우클릭**
3. **"Python"** 섹션의 메뉴 확인

## 💡 사용 예제

### 예제 1: helper.py 수정 후 리로드

```
1. util/helper.py 파일 수정 (예: 함수 추가)
2. Content Browser에서 helper.py 우클릭
3. "Python" → "🔄 Python 모듈 리로드"
4. Output Log: "✅ 리로드 성공: util.helper"
5. 수정사항 즉시 반영!
```

### 예제 2: 테스트 스크립트 실행

```
1. developer/temp.py에 테스트 코드 작성
2. Content Browser에서 temp.py 우클릭
3. "Python" → "▶️ Python 파일 실행"
4. 즉시 실행 결과 확인
```

### 예제 3: 폴더 정보 확인

```
1. Content Browser에서 util 폴더 우클릭
2. "Python" → "📁 Python 폴더 정보"
3. Output Log에서 경로 정보 확인
```

## 🧪 테스트 도구

### 전체 테스트 실행

Python Console에서:

```python
import startup.test_context_menu as test
test.run_all_tests()
```

### 개별 테스트

```python
# 컨텍스트 메뉴 설정만 테스트
test.test_context_menu_setup()

# 모듈 리로드 테스트
test.test_module_reload()

# 파일 실행 테스트
test.test_file_execution()

# 현재 선택 항목 확인
test.show_selected_info()
```

## 🎨 워크플로우

### 개발 워크플로우

```
1. Python 파일 수정
   ↓
2. Content Browser에서 우클릭
   ↓
3. "🔄 Python 모듈 리로드"
   ↓
4. 즉시 테스트
   ↓
5. 반복 (에디터 재시작 불필요!)
```

### 스크립트 테스트 워크플로우

```
1. 간단한 스크립트 작성 (temp.py)
   ↓
2. Content Browser에서 우클릭
   ↓
3. "▶️ Python 파일 실행"
   ↓
4. 결과 확인
   ↓
5. 수정 후 다시 실행
```

## 🔧 기술 상세

### 컨텍스트 메뉴 활성화 조건

```python
# Python 폴더 체크
@unreal.ufunction(override=True)
def can_execute(self, context):
    selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    # 폴더가 Python 경로 포함하는지 확인
    for folder in selected_folders:
        if "/Game/Python" in folder:
            return True
    
    # 에셋 경로가 Python 경로 포함하는지 확인
    for asset in selected_assets:
        if "/Game/Python" in asset.get_path_name():
            return True
    
    return False
```

### 경로 변환

```python
# Content Browser 경로 → Python 모듈 경로
"/Game/Python/util/helper.py" → "util.helper"
"/Game/Python/developer/temp.py" → "developer.temp"
```

### 파일 시스템 경로

```python
# Content Browser 경로 → 실제 파일 경로
content_dir = unreal.Paths.project_content_dir()
# D:/GitHub/See1Unreal5/Content/

file_path = asset_path.replace("/Game/", "")
# Python/util/helper.py

full_path = os.path.join(content_dir, file_path)
# D:/GitHub/See1Unreal5/Content/Python/util/helper.py
```

## ⚙️ 커스터마이징

### 새로운 메뉴 항목 추가

```python
@unreal.uclass()
class MyCustomAction(unreal.ToolMenuEntryScript):
    
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        # 활성화 조건
        return True
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        # 실행 로직
        unreal.log("Custom action executed!")

# setup_python_context_menu()에서:
custom = MyCustomAction()
custom.init_entry(menu_owner, "myAction", "Python", "My Action", "Description")
custom.data.menu = menu_name
menu.add_menu_entry_object(custom)
```

### 다른 폴더에도 적용

```python
# can_execute에서 경로 조건 변경
if "/Game/Materials" in folder:  # Materials 폴더
    return True
```

## 📚 상세 문서

- **전체 가이드**: `README_ContextMenu.md`
- **테스트 도구**: `test_context_menu.py`

## 🐛 알려진 이슈

### 1. 리로드 후 변수 재할당 필요

```python
# 문제: 리로드 후에도 이전 값 유지
from util import helper as uh
# ... helper.py 수정 ...
# 우클릭 → 리로드
print(uh.some_function())  # 여전히 이전 값!

# 해결: 다시 import
from util import helper as uh  # 재할당
print(uh.some_function())  # 새로운 값!
```

### 2. 실행 vs 리로드

- **실행** (`exec`): 독립 스크립트, 일회성
- **리로드** (`importlib`): 모듈, 지속적 사용

## 💡 팁

1. **빠른 개발**: 수정 → 리로드 → 테스트 사이클로 빠른 개발
2. **로그 확인**: Output Log를 항상 열어두기
3. **테스트 도구**: `test_context_menu.py` 활용
4. **단축키**: Content Browser에서 우클릭 단축키 사용

## 📝 체크리스트

실행 전:
- [ ] `init_toolbar.py`에서 `setup_python_context_menu()` 주석 해제
- [ ] Unreal Editor 재시작 (또는 Python Console에서 수동 로드)

사용 중:
- [ ] Content Browser에서 `/Game/Python` 폴더로 이동
- [ ] Python 파일 우클릭하여 메뉴 확인
- [ ] Output Log 열어두기

문제 발생 시:
- [ ] Output Log에서 에러 메시지 확인
- [ ] `test_context_menu.py` 실행
- [ ] Unreal Editor 재시작

## 🎊 완료!

이제 Python 개발이 훨씬 편해집니다:

- ✅ 코드 수정 후 **즉시 리로드**
- ✅ 스크립트 **빠른 실행**
- ✅ 에디터 재시작 **불필요**
- ✅ 워크플로우 **최적화**

**Happy Python Coding in Unreal!** 🚀

---

**추가일**: 2025-10-18  
**위치**: `Content/Python/startup/init_toolbar.py`  
**호환성**: UE 5.0+
