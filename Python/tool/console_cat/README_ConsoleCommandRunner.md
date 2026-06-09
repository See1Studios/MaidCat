# 콘솔 명령어 실행기 사용 가이드

## 📋 개요

Unreal Engine 콘솔 명령어를 쉽게 검색하고 실행할 수 있는 Python 기반 유틸리티입니다.

## 🗂️ 파일 구조

```
Content/Python/tool/
├── generate_console_command_list.py   # 콘솔 명령어 데이터 생성 도구
├── translation_dictionary.json        # 번역 사전
├── console_command_runner.py          # CLI 명령어 실행기
└── console_command_runner_gui.py      # GUI 백엔드 (블루프린트 연동)

Saved/
├── ConsoleHelp.html                   # 언리얼 생성 HTML (자동)
└── ConsoleCommandData/                # JSON 데이터 (자동 생성)
    ├── r_commands_kr.json
    └── a_commands_kr.json
```

## 🚀 사용 방법

### 1단계: 데이터 생성

먼저 콘솔 명령어 데이터를 생성해야 합니다.

**Unreal Editor의 Python 콘솔에서:**

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")

import generate_console_command_list
# 스크립트 실행 - 자동으로 HTML 생성 및 JSON 변환
```

또는:

```python
exec(open("D:/GitHub/See1Unreal5/Content/Python/tool/generate_console_command_list.py").read())
```

### 2단계: CLI 실행기 사용

**Python 콘솔에서:**

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")

import console_command_runner as runner

# 명령어 검색
runner.search_commands("landscape")

# 특정 스코프에서 검색
runner.search_commands("render", scope="r")

# 명령어 상세 정보 보기
runner.show_command_info("r.SetRes")

# 명령어 실행
runner.execute_command("stat fps")
runner.execute_command("r.SetRes", "1920x1080w")

# 스코프 목록 보기
runner.list_scopes()
```

### 빠른 실행 함수

```python
# FPS 표시
runner.quick_fps()

# 프레임 시간 표시
runner.quick_unit()

# GPU 통계
runner.quick_gpu()

# 해상도 설정
runner.set_resolution(1920, 1080, windowed=True)

# 뷰 거리 스케일 (0.0 ~ 1.0)
runner.set_view_distance(0.8)
```

## 📊 주요 기능

### CLI 실행기 (`console_command_runner.py`)

#### ConsoleCommandManager 클래스

```python
manager = runner.ConsoleCommandManager()

# 모든 명령어 로드
manager.load_all_commands()

# 명령어 검색
results = manager.search_commands("texture", scope_filter="r")

# 특정 명령어 정보 가져오기
cmd_info = manager.get_command_by_name("r.SetRes")

# 명령어 실행
manager.execute_command("stat fps")
manager.execute_command("r.SetRes", "1920x1080w")
```

#### 검색 함수

```python
# 키워드로 검색 (명령어 이름, 영어/한국어 설명 모두 검색)
results = runner.search_commands("shadow")

# 결과 예시:
# 1. [r] r.Shadow.MaxResolution              - 렌더링할 섀도우 깊이 텍스처의 최대 크기
# 2. [r] r.Shadow.Quality                    - 섀도우 필터링 퀄리티 설정
# ...
```

### GUI 백엔드 (`console_command_runner_gui.py`)

블루프린트에서 호출 가능한 함수들:

```python
# 명령어 목록 로드
commands = ConsoleCommandRunnerLibrary.load_command_list()

# 명령어 검색
results = ConsoleCommandRunnerLibrary.search_commands("landscape")

# 설명 가져오기
desc_kr = ConsoleCommandRunnerLibrary.get_command_description_kr("r.SetRes")
desc_en = ConsoleCommandRunnerLibrary.get_command_description_en("r.SetRes")

# 명령어 실행
success = ConsoleCommandRunnerLibrary.execute_console_command("stat fps", "")

# 스코프 목록
scopes = ConsoleCommandRunnerLibrary.get_available_scopes()

# 스코프별 명령어
commands = ConsoleCommandRunnerLibrary.get_commands_by_scope("r")
```

### 즐겨찾기 & 히스토리

```python
import console_command_runner_gui as gui

# 즐겨찾기 추가/제거
gui.add_to_favorites("stat fps")
gui.remove_from_favorites("stat fps")
favorites = gui.get_favorites()

# 히스토리 관리
history = gui.get_history()
gui.clear_history()

# 명령어 실행 (자동으로 히스토리에 추가)
gui.execute_and_log("r.SetRes", "1920x1080w")
```

### 프리셋

미리 정의된 유용한 명령어 모음:

```python
import console_command_runner_gui as gui

# 프리셋 목록
presets = gui.get_presets()

# 프리셋 실행
gui.execute_preset("Performance", "FPS 표시")
gui.execute_preset("Rendering", "1080p 창모드")
gui.execute_preset("Debug", "와이어프레임")
```

**사용 가능한 프리셋:**

- **Performance**: FPS 표시, 프레임 시간, GPU 통계, 렌더 통계, 메모리 통계
- **Rendering**: 해상도 설정, 안티앨리어싱 설정
- **Debug**: 뷰모드, 콜리전 표시, 네비메시 표시

## 🔧 설정 커스터마이징

### generate_console_command_list.py

```python
# 처리할 스코프 설정
SCOPES_TO_PROCESS = ["r", "a", "sg"]  # 렌더링, 오디오, 스케일러빌리티

# 테스트 모드 (빠른 테스트용)
TEST_MODE_ENABLED = True
TEST_MODE_COMMAND_LIMIT = 5

# 번역 사전 수정
# translation_dictionary.json 파일을 직접 편집
```

### 번역 사전 수정

`translation_dictionary.json` 파일에서 엔진 용어 번역을 추가/수정:

```json
{
    "Landscape": "랜드스케이프",
    "Render": "렌더",
    "YourTerm": "당신의_번역"
}
```

### 프리셋 추가

`console_command_runner_gui.py`의 `COMMAND_PRESETS` 딕셔너리에 추가:

```python
COMMAND_PRESETS = {
    "Your Category": {
        "명령어 이름": "console.command arg1 arg2",
    }
}
```

## 💡 유용한 팁

### 1. 자주 사용하는 명령어 검색

```python
# 퍼포먼스 관련
runner.search_commands("stat")
runner.search_commands("fps")

# 렌더링 관련
runner.search_commands("render", scope="r")
runner.search_commands("shadow", scope="r")

# 랜드스케이프 관련
runner.search_commands("landscape")
```

### 2. 스크립트 자동 로드 설정

`init_unreal.py`에 추가하여 에디터 시작 시 자동 로드:

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")

import console_command_runner as runner
print("콘솔 명령어 실행기가 로드되었습니다.")
```

### 3. 커스텀 단축키 함수

```python
def my_debug_mode():
    """내 디버그 설정"""
    runner.execute_command("stat fps")
    runner.execute_command("stat unit")
    runner.execute_command("show collision")
    
def my_performance_mode():
    """퍼포먼스 테스트 설정"""
    runner.execute_command("r.SetRes", "1920x1080f")
    runner.execute_command("r.VSync", "0")
    runner.execute_command("t.MaxFPS", "0")
```

## 🐛 문제 해결

### 데이터 파일이 없다고 나올 때

```python
# 데이터 재생성
import generate_console_command_list
generate_console_command_list.generate_command_list_for_scopes()
```

### 모듈을 찾을 수 없을 때

```python
import sys
# 경로 확인
print(sys.path)

# 경로 추가
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
```

### HTML 파일이 생성되지 않을 때

1. Unreal Editor 콘솔에서 직접 실행:
   ```
   helphtml
   ```

2. Saved 폴더 확인:
   - `Saved/ConsoleHelp.html` 파일 존재 여부 확인

## 📝 예제 워크플로우

### 시나리오 1: 처음 사용

```python
# 1. 데이터 생성
exec(open("D:/GitHub/See1Unreal5/Content/Python/tool/generate_console_command_list.py").read())

# 2. 실행기 로드
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner as runner

# 3. 명령어 검색 및 실행
runner.search_commands("fps")
runner.execute_command("stat fps")
```

### 시나리오 2: 렌더링 설정 변경

```python
import console_command_runner as runner

# 렌더 관련 명령어 찾기
runner.search_commands("shadow", scope="r")

# 상세 정보 확인
runner.show_command_info("r.Shadow.MaxResolution")

# 실행
runner.execute_command("r.Shadow.MaxResolution", "2048")
```

### 시나리오 3: 퍼포먼스 프로파일링

```python
import console_command_runner as runner

# 통계 표시
runner.quick_fps()
runner.quick_unit()
runner.quick_gpu()

# 추가 정보
runner.execute_command("stat rhi")
runner.execute_command("stat scenerendering")
```

## 🎯 다음 단계

1. **에디터 유틸리티 위젯 생성**: 블루프린트로 GUI 인터페이스 만들기
2. **툴바 버튼 추가**: 빠른 접근을 위한 커스텀 툴바 버튼
3. **명령어 프리셋 확장**: 프로젝트에 맞는 커스텀 프리셋 추가

---

**작성자**: GitHub Copilot  
**최종 업데이트**: 2025년 10월 18일
