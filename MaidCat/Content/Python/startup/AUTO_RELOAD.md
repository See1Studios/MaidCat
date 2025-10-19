# 🔄 자동 리로드 기능

`init_context.py`에 **자동 리로드 기능**이 추가되었습니다!

## ✨ 핵심 기능

### 파일 수정 감지

```python
# 메뉴를 우클릭할 때마다 자동으로 체크
def check_and_reload():
    """파일 변경 확인 및 자동 리로드"""
    current_mtime = os.path.getmtime(__file__)
    
    if current_mtime > _last_modified_time:
        # 파일이 변경됨!
        setup_python_context_menu()  # 메뉴 재설정
        unreal.log("✅ 자동 갱신 완료!")
```

### 동작 방식

1. **Unreal Editor 시작** → `init_context.py` 로드
2. **파일 수정 시간 저장** → `_last_modified_time` 변수에 저장
3. **우클릭할 때마다 체크** → `can_execute()` 메서드에서 자동 확인
4. **변경 감지 시** → 자동으로 메뉴 재설정

## 🚀 사용법

### 1. 평소처럼 사용

```
1. init_context.py 수정
2. 저장
3. Content Browser에서 Python 폴더 우클릭
4. 자동으로 변경사항 적용! ✨
```

**에디터 재시작 불필요!**

### 2. 로그 확인

Output Log에서 자동 갱신 메시지 확인:

```
🔄 init_context.py 변경 감지! 자동 리로드...
✅ 컨텍스트 메뉴 자동 갱신 완료!
```

## 💡 실전 예제

### 시나리오: 새 메뉴 항목 추가

```python
# 1. init_context.py 열기
# 2. 새로운 메뉴 클래스 추가

@unreal.uclass()
class MyNewMenu(unreal.ToolMenuEntryScript):
    def __init__(self):
        super().__init__()
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        # 자동 리로드 체크 포함!
        check_and_reload()
        return True
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        unreal.log("새 메뉴 실행!")

# 3. setup_python_context_menu() 함수에 추가
def setup_python_context_menu():
    # ... 기존 메뉴들 ...
    
    # 새 메뉴 추가
    new_entry = MyNewMenu()
    new_entry.init_entry(...)
    menu.add_menu_entry_object(new_entry)

# 4. 저장
# 5. Content Browser에서 우클릭
# 6. 새 메뉴가 바로 나타남! ✨
```

## 🔧 기술 상세

### 파일 변경 감지

```python
# 파일 수정 시간 비교
_last_modified_time = None  # 전역 변수

current_mtime = os.path.getmtime(__file__)

if current_mtime > _last_modified_time:
    # 변경됨!
    _last_modified_time = current_mtime
    setup_python_context_menu()
```

### 메뉴 체크 시점

```python
@unreal.ufunction(override=True)
def can_execute(self, context):
    # 메뉴 표시 전에 호출됨
    check_and_reload()  # 여기서 파일 변경 체크!
    
    # ... 나머지 로직 ...
```

### 자동 실행 (startup)

```python
if __name__ != "__main__":
    # startup 폴더에서 로드될 때
    _last_modified_time = os.path.getmtime(__file__)
    setup_python_context_menu()
    unreal.log("자동 리로드 활성화!")
```

## ⚡ 성능

- **오버헤드**: 거의 없음 (단순 파일 시간 체크)
- **체크 빈도**: 우클릭 시에만 (사용자 액션)
- **메모리**: 변수 1개 (`_last_modified_time`)

## 📋 장점

1. ✅ **개발 속도 향상**
   - 수정 → 저장 → 우클릭 → 즉시 반영
   - 에디터 재시작 불필요

2. ✅ **실시간 테스트**
   - 메뉴 로직 수정 후 바로 테스트
   - 빠른 반복 개발

3. ✅ **자동화**
   - 별도 리로드 명령 불필요
   - 자연스러운 워크플로우

4. ✅ **안전**
   - 에러 발생 시 조용히 실패
   - 메뉴 동작에 영향 없음

## 🐛 제한사항

### 1. uclass 클래스는 재로드 제한

```python
# @unreal.uclass() 데코레이터가 있는 클래스는
# Unreal Engine에 등록되므로 완전한 재로드 어려움

# 해결: 메뉴 로직만 변경 시 잘 작동
# 클래스 구조 변경 시 에디터 재시작 권장
```

### 2. import된 다른 모듈

```python
# init_context.py만 리로드됨
# 다른 모듈 변경 시 별도 리로드 필요

from util import helper  # 이건 자동 리로드 안 됨
```

### 3. 전역 변수 초기화

```python
# _last_modified_time은 유지됨
# 완전 리셋 원하면 에디터 재시작
```

## 🎯 모범 사례

### DO ✅

```python
# 메뉴 로직 수정
def execute(self, context):
    unreal.log("새로운 로직!")  # ← 이런 거 수정

# 조건 변경
def can_execute(self, context):
    return True  # ← 조건 변경

# 메뉴 텍스트 변경
entry.init_entry(..., "새 이름", ...)  # ← 텍스트 변경
```

### DON'T ❌

```python
# 클래스 이름 변경
class NewName(unreal.ToolMenuEntryScript):  # ← 재시작 필요
    pass

# 새 uclass 클래스 추가
@unreal.uclass()  # ← 재시작 권장
class BrandNewMenu(...):
    pass

# 클래스 구조 대폭 변경
# ← 재시작하는 게 안전
```

## 🎊 결론

**자동 리로드로 Python 개발이 훨씬 빠르고 편해집니다!**

```
수정 → 저장 → 우클릭 → 즉시 반영! ✨
```

---

**추가일**: 2025-10-18  
**파일**: `init_context.py`  
**호환**: UE 5.0+
