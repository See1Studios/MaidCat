# 📁 폴더 트리 컨텍스트 메뉴 지원

이제 Python 컨텍스트 메뉴가 **모든 위치**에서 작동하며, **서브메뉴 구조**로 깔끔하게 정리되었습니다!

## ✨ 메뉴 구조

### 우클릭 → Python (섹션) → 서브메뉴
```
📁 폴더 정보
🔄 모듈 리로드
▶️ 파일 실행
```

이전처럼 메뉴가 흩어지지 않고, **Python 섹션 아래에 정리**되어 나타납니다!

## 🎯 지원하는 위치

### 1. Content Browser - 에셋 영역
```
Content Browser 중앙의 에셋 목록에서 우클릭
├── Python 파일 (.py) 우클릭
└── Python 폴더 우클릭
    └── [Python] 섹션 표시
```

### 2. Content Browser - 폴더 영역
```
Content Browser에서 폴더 아이콘 우클릭
└── Python 폴더 우클릭
    └── [Python] 섹션 표시
```

### 3. 왼쪽 폴더 트리 ✨ (NEW!)
```
Content Browser 왼쪽의 폴더 트리에서 우클릭
├── Python 폴더
├── util 폴더
├── developer 폴더
└── startup 폴더
    └── [Python] 섹션 표시
```

## 🎨 UI 개선점

### Before (이전)
```
우클릭 메뉴:
├── Import...
├── Export...
├── Python 폴더 정보          ← 흩어져 있음
├── Create New Folder
├── 🔄 Python 모듈 리로드      ← 찾기 어려움
├── Show in Explorer
└── ▶️ Python 파일 실행        ← 멀리 떨어져 있음
```

### After (현재) ✨
```
우클릭 메뉴:
├── Import...
├── Export...
├── Create New Folder
├── Show in Explorer
└── ──────────────────
    Python                     ← 섹션 헤더
    ├── 📁 폴더 정보           ← 그룹화!
    ├── 🔄 모듈 리로드         ← 한눈에 보임
    └── ▶️ 파일 실행           ← 깔끔함
```

**찾기 쉽고, 보기 좋고, 사용하기 편해졌습니다!**

## 🎯 등록된 메뉴 위치

```python
menu_names = [
    "ContentBrowser.AssetContextMenu",      # 에셋 우클릭
    "ContentBrowser.FolderContextMenu",     # 폴더 우클릭
    "ContentBrowser.PathViewContextMenu",   # 왼쪽 트리 ✨
]
```

## 💡 사용 예제

### 시나리오 1: 왼쪽 트리에서 폴더 관리

```
1. Content Browser 왼쪽 트리에서 "Python" 폴더 우클릭
2. "Python" 섹션 확인 (접기 가능)
3. "📁 폴더 정보" 클릭
4. Output Log에서 경로 확인
```

### 시나리오 2: 서브메뉴로 빠른 접근

```
# 이전: 메뉴 전체를 스캔해야 함
우클릭 → 스크롤 → 찾기 → 클릭

# 현재: Python 섹션만 찾으면 끝!
우클릭 → "Python" 찾기 → 서브메뉴 선택 ✨
```

### 시나리오 3: util 폴더에서 모듈 리로드

```
1. 왼쪽 트리에서 "Python/util" 폴더 우클릭
   → Python 섹션 보임
2. Content Browser에서 helper.py 선택
3. helper.py 우클릭 → Python → 🔄 모듈 리로드
4. 즉시 반영!
```

## 🔧 기술 상세

### 서브메뉴 섹션 생성

각 메뉴 위치마다 고유한 Python 섹션 생성:

```python
for menu_name in menu_names:
    menu = tool_menus.extend_menu(menu_name)
    menu_suffix = menu_name.split('.')[-1]
    
    # 고유한 섹션 ID
    python_section = f"PythonSection_{menu_suffix}"
    
    # 섹션 추가 (여기서 "Python" 헤더 생성)
    menu.add_section(python_section, "Python")
```

### 메뉴 항목을 섹션에 추가

```python
# 모든 메뉴 항목은 python_section에 속함
info_entry.init_entry(
    menu_owner,
    f"pythonFolderInfo_{menu_suffix}",
    python_section,  # ← 여기가 핵심!
    "📁 폴더 정보",
    "Python 폴더 관련 정보 표시"
)
```

### 섹션별 고유 ID

```python
# 섹션 ID:
# - PythonSection_AssetContextMenu
# - PythonSection_FolderContextMenu  
# - PythonSection_PathViewContextMenu

# 메뉴 ID:
# - pythonFolderInfo_AssetContextMenu
# - pythonFolderInfo_FolderContextMenu
# - pythonFolderInfo_PathViewContextMenu
```

이렇게 하면 **중복 없이** 모든 위치에 **동일한 구조**로 메뉴가 나타납니다!

## 📋 테스트

### 1. 왼쪽 트리
```
✅ Python 폴더 우클릭 → 메뉴 보임
✅ util 폴더 우클릭 → 메뉴 보임
✅ Materials 폴더 우클릭 → 메뉴 안 보임 (정상)
```

### 2. 폴더 영역
```
✅ Python 폴더 아이콘 우클릭 → 메뉴 보임
✅ startup 폴더 우클릭 → 메뉴 보임
```

### 3. 에셋 영역
```
✅ helper.py 우클릭 → 모든 메뉴 보임
✅ temp.py 우클릭 → 모든 메뉴 보임
✅ MyMaterial 우클릭 → 메뉴 안 보임 (정상)
```

## 🎨 UI 일관성

**모든 위치에서 동일한 메뉴:**

```
Python
├── Python 폴더 정보
├── 🔄 Python 모듈 리로드
└── ▶️ Python 파일 실행
```

**위치에 따른 가용성:**

| 메뉴 항목 | 왼쪽 트리 | 폴더 | 에셋 (.py) |
|----------|----------|------|-----------|
| 폴더 정보 | ✅ | ✅ | ✅ |
| 모듈 리로드 | ❌ | ❌ | ✅ |
| 파일 실행 | ❌ | ❌ | ✅ |

## 💡 워크플로우 개선

### Before
```
1. 왼쪽에서 폴더 클릭
2. 중앙 에셋 영역에서 파일 찾기
3. 파일 우클릭
4. 메뉴 선택
```

### After ✨
```
1. 왼쪽 트리에서 바로 우클릭!
2. 메뉴 선택
```

**단계 감소: 4단계 → 2단계**

## 🐛 알려진 동작

### 폴더에서 파일 메뉴 비활성화

```python
# 폴더 우클릭 시
✅ Python 폴더 정보     - 보임
❌ Python 모듈 리로드   - 흐리게 (비활성)
❌ Python 파일 실행     - 흐리게 (비활성)

# 이유: can_execute()에서 .py 파일 체크
```

### 다중 선택

```python
# 여러 파일 선택 시
✅ 모두 Python 파일이면 → 메뉴 활성
❌ 하나라도 다른 파일이면 → 메뉴 비활성
```

## 🎊 결론

**이제 Python 메뉴가 서브메뉴로 깔끔하게 정리되었습니다!**

### 장점

✅ **찾기 쉬움** - "Python" 섹션만 찾으면 모든 메뉴가 한곳에  
✅ **보기 좋음** - 메뉴가 흩어지지 않고 그룹화  
✅ **확장성** - 새 메뉴 추가 시 같은 섹션에 넣기만 하면 됨  
✅ **일관성** - 모든 위치에서 동일한 구조  

### 지원 위치

```
왼쪽 트리 ✅
폴더 영역 ✅
에셋 영역 ✅

모두 서브메뉴로! 🎉
```

### 메뉴 구조

```
[Python]  ← 섹션 헤더
├── 📁 폴더 정보
├── 🔄 모듈 리로드
└── ▶️ 파일 실행
```

**직관적이고 깔끔한 UX!**

---

**업데이트일**: 2025-10-18  
**파일**: `init_context.py`  
**주요 개선**: 서브메뉴 구조 (add_section) 도입  
**추가 지원**: PathViewContextMenu (폴더 트리)
