# GUI 구현 가이드

## 🎨 GUI 옵션

콘솔 명령어 실행기는 두 가지 GUI 방식으로 사용할 수 있습니다.

---

## 방법 1: Qt GUI (Python만 사용) ⚡

### 장점
- Python만으로 완전한 GUI 구현
- 독립적인 창으로 실행
- 코드만으로 모든 것 제어 가능

### 설치 방법

**1. PySide2 설치**

Windows PowerShell에서:
```powershell
# Unreal Engine Python 경로 찾기
$UnrealPython = "C:\Program Files\Epic Games\UE_5.X\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

# PySide2 설치
& $UnrealPython -m pip install PySide2
```

또는 Unreal Editor Python 콘솔에서:
```python
import subprocess
import sys

# pip 업그레이드
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

# PySide2 설치
subprocess.run([sys.executable, "-m", "pip", "install", "PySide2"])
```

**2. GUI 실행**

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")

import console_command_runner_qt as qt_gui

# GUI 창 열기
window = qt_gui.show_gui()
```

### 주요 기능

- ✅ 명령어 검색 & 필터링
- ✅ 스코프별 분류
- ✅ 즐겨찾기 관리
- ✅ 실행 히스토리
- ✅ 프리셋 버튼
- ✅ 한/영 설명 표시
- ✅ 더블클릭으로 즉시 실행
- ✅ 명령어 인자 입력

### 스크린샷 구조

```
┌─────────────────────────────────────────────────────┐
│ 언리얼 콘솔 명령어 실행기                              │
├─────────────────────────────────────────────────────┤
│ 검색: [___________] 스코프: [전체▼]                   │
├─────────────────────────────────────────────────────┤
│ [명령어] [즐겨찾기] [히스토리] [프리셋]                │
│ ┌─────────────────────────────────────────────┐     │
│ │ [r] r.SetRes                                │     │
│ │ [r] r.VSync                                 │     │
│ │ [r] r.Shadow.MaxResolution                  │     │
│ │ ...                                         │     │
│ └─────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────┤
│ 명령어 상세 정보                                      │
│ 명령어: r.SetRes                                     │
│ 설명 (한국어): [_________________________]           │
│ 설명 (영어):   [_________________________]           │
│ 인자: [________] [실행] [⭐]                         │
└─────────────────────────────────────────────────────┘
```

---

## 방법 2: 에디터 유틸리티 위젯 (블루프린트) 🎯

### 장점
- Unreal 에디터에 완벽히 통합
- UMG 디자이너로 UI 디자인
- 에디터 툴바에 추가 가능
- 추가 패키지 설치 불필요

### 구현 방법

#### Step 1: Python 함수 준비 (이미 완료!)

`console_command_runner_gui.py`에 블루프린트용 함수들이 준비되어 있습니다:

```python
# 이미 구현된 함수들
ConsoleCommandRunnerLibrary.load_command_list()
ConsoleCommandRunnerLibrary.search_commands(query)
ConsoleCommandRunnerLibrary.get_command_description_kr(command_name)
ConsoleCommandRunnerLibrary.execute_console_command(command_name, args)
# ... 등등
```

#### Step 2: 에디터 유틸리티 위젯 블루프린트 생성

1. **Content Browser에서**:
   - 우클릭 → `Editor Utilities` → `Editor Utility Widget`
   - 이름: `EUW_ConsoleCommandRunner`

2. **위젯 디자이너에서 UI 구성**:

**기본 레이아웃:**
```
Canvas Panel
├─ Vertical Box (메인 컨테이너)
│  ├─ Horizontal Box (상단 검색)
│  │  ├─ Text Block: "검색:"
│  │  ├─ Editable Text Box (검색 입력)
│  │  ├─ Text Block: "스코프:"
│  │  └─ Combo Box String (스코프 선택)
│  │
│  ├─ Widget Switcher (탭)
│  │  ├─ Scroll Box (명령어 리스트)
│  │  │  └─ List View (명령어 목록)
│  │  ├─ Scroll Box (즐겨찾기)
│  │  └─ Scroll Box (히스토리)
│  │
│  └─ Vertical Box (하단 정보)
│     ├─ Text Block (명령어 이름)
│     ├─ Multi-line Text Box (한국어 설명)
│     ├─ Multi-line Text Box (영어 설명)
│     └─ Horizontal Box (실행 영역)
│        ├─ Editable Text Box (인자 입력)
│        ├─ Button: "실행"
│        └─ Button: "⭐"
```

#### Step 3: 블루프린트 이벤트 그래프

**1. Event Construct (초기화)**

```
Event Construct
└─> Python.Execute Python Script
    Script: 
    """
    import sys
    sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
    import console_command_runner_gui as gui
    
    # 명령어 로드
    commands = gui.ConsoleCommandRunnerLibrary.load_command_list()
    """
    └─> For Each Loop
        └─> Add Item to List View
```

**2. On Search Text Changed**

```
검색 Text Box → On Text Changed
└─> Python.Execute Python Script
    Script:
    """
    import console_command_runner_gui as gui
    results = gui.ConsoleCommandRunnerLibrary.search_commands("{SearchText}")
    """
    └─> Clear List View
    └─> For Each → Add to List View
```

**3. On Execute Button Clicked**

```
실행 Button → On Clicked
└─> Python.Execute Python Script
    Script:
    """
    import console_command_runner_gui as gui
    gui.ConsoleCommandRunnerLibrary.execute_console_command(
        "{SelectedCommand}",
        "{ArgsText}"
    )
    """
```

#### Step 4: 간단한 버전 (텍스트만)

더 간단하게 시작하고 싶다면:

**최소 UI:**
- Vertical Box
  - Editable Text (명령어 입력)
  - Button (실행)
  - Multi-line Text Box (결과 표시)

**블루프린트:**
```
Button Clicked
└─> Get Text (명령어 입력)
└─> Python Execute
    "import unreal; unreal.SystemLibrary.execute_console_command(None, '{입력된_명령어}')"
```

---

## 방법 3: 간단한 Python 스크립트 (GUI 없음)

GUI가 필요 없다면 CLI 버전만 사용:

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner as runner

# 즉시 사용 가능
runner.quick_fps()
runner.search_commands("landscape")
```

---

## 🚀 추천 사용 방법

### 초보자
1. **CLI 버전부터 시작** (`console_command_runner.py`)
   - Python 콘솔에서 직접 함수 호출
   - GUI 없이 빠르게 테스트

### 중급자
2. **Qt GUI 사용** (`console_command_runner_qt.py`)
   - PySide2 설치 후 완전한 GUI 사용
   - 독립적인 창으로 편리하게 사용

### 고급자
3. **에디터 유틸리티 위젯 제작**
   - 프로젝트에 맞게 커스터마이징
   - 에디터 툴바에 통합

---

## 📦 파일별 용도 정리

| 파일 | 용도 | GUI |
|------|------|-----|
| `console_command_runner.py` | CLI 기본 실행기 | ❌ |
| `console_command_runner_gui.py` | 블루프린트 백엔드 | 블루프린트로 구현 |
| `console_command_runner_qt.py` | Qt GUI 완성본 | ✅ Python |

---

## 💡 빠른 시작

### Qt GUI (가장 간단!)

```python
# 1. PySide2 설치 (한 번만)
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "PySide2"])

# 2. GUI 실행
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner_qt as gui
window = gui.show_gui()
```

### CLI (설치 없음!)

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner as runner

runner.quick_fps()
runner.search_commands("shadow")
```

---

## 🎯 다음 단계

선택한 방법에 따라:

- **Qt GUI**: `show_gui()` 호출만 하면 끝!
- **에디터 위젯**: 위의 Step 2-3 따라서 블루프린트 생성
- **CLI**: 바로 사용 가능!

---

**문의사항이나 추가 기능 요청은 이슈로 남겨주세요!** 🚀
