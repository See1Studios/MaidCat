# 🎮 Unreal Engine 콘솔 명령어 실행기

언리얼 엔진의 모든 콘솔 명령어를 검색하고 실행할 수 있는 완전한 Python 기반 도구입니다.

## ✨ 특징

- 🔍 **스마트 검색**: 명령어 이름, 한글/영문 설명 모두 검색
- 📊 **스코프 필터링**: r (렌더링), a (오디오) 등 카테고리별 분류
- ⭐ **즐겨찾기**: 자주 쓰는 명령어 저장
- 📝 **히스토리**: 실행 기록 자동 저장
- 🎯 **프리셋**: 미리 정의된 유용한 명령어 모음
- 🌐 **한글 번역**: Google Translate로 자동 번역된 설명
- 🎨 **다양한 UI**: CLI, Qt GUI, 에디터 위젯 지원

## 📦 구성 요소

### 1. 데이터 생성 도구
- `generate_console_command_list.py` - 콘솔 명령어 추출 및 번역
- `translation_dictionary.json` - 엔진 용어 번역 사전

### 2. 실행기
- `console_command_runner.py` - CLI 버전 (Python 콘솔)
- `console_command_runner_qt.py` - Qt GUI 버전 (독립 창)
- `console_command_runner_gui.py` - 에디터 위젯 백엔드

### 3. 문서
- `README_ConsoleCommandRunner.md` - 상세 사용 가이드
- `GUI_GUIDE.md` - GUI 구현 가이드
- `QUICK_START.md` - 이 문서!

## 🚀 5분 빠른 시작

### 1️⃣ 데이터 생성 (처음 한 번만)

Unreal Editor → Python 콘솔:

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
exec(open("D:/GitHub/See1Unreal5/Content/Python/tool/generate_console_command_list.py").read())
```

⏱️ 약 1-2분 소요 (명령어 번역 중...)

### 2️⃣ 실행기 사용

#### 옵션 A: CLI 버전 (즉시 사용!)

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner as runner

# 명령어 검색
runner.search_commands("fps")

# 즉시 실행
runner.quick_fps()      # FPS 표시
runner.quick_unit()     # 프레임 시간
runner.quick_gpu()      # GPU 통계
```

#### 옵션 B: Qt GUI 버전 (완전한 GUI!)

```python
# PySide2 설치 (처음 한 번만)
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "PySide2"])

# GUI 실행
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import console_command_runner_qt as gui
window = gui.show_gui()
```

## 💡 주요 기능 사용법

### 검색

```python
import console_command_runner as runner

# 키워드 검색
runner.search_commands("landscape")

# 스코프별 검색
runner.search_commands("shadow", scope="r")

# 명령어 상세 정보
runner.show_command_info("r.SetRes")
```

### 실행

```python
# 간단한 명령어
runner.execute_command("stat fps")

# 인자가 있는 명령어
runner.execute_command("r.SetRes", "1920x1080w")

# 빠른 실행 함수
runner.quick_fps()                          # stat fps
runner.quick_unit()                         # stat unit
runner.quick_gpu()                          # stat gpu
runner.set_resolution(1920, 1080, True)     # 해상도 설정
```

### 즐겨찾기 & 히스토리 (GUI 버전)

```python
import console_command_runner_gui as gui

# 즐겨찾기 추가
gui.add_to_favorites("stat fps")
gui.add_to_favorites("r.SetRes")

# 즐겨찾기 목록
favorites = gui.get_favorites()

# 히스토리 확인
history = gui.get_history()

# 프리셋 실행
gui.execute_preset("Performance", "FPS 표시")
gui.execute_preset("Rendering", "1080p 창모드")
```

## 📊 데이터 파일 위치

생성된 파일들:

```
프로젝트/Saved/
├── ConsoleHelp.html                    # 원본 HTML (자동 생성)
├── ConsoleCommandData/                 # JSON 데이터
│   ├── r_commands_kr.json             # 렌더링 명령어
│   └── a_commands_kr.json             # 오디오 명령어
├── ConsoleCommandFavorites.json       # 즐겨찾기
└── ConsoleCommandHistory.json         # 히스토리
```

## 🎯 사용 예시

### 시나리오 1: 퍼포먼스 체크

```python
import console_command_runner as runner

# 통계 표시
runner.quick_fps()
runner.quick_unit()
runner.quick_gpu()

# 추가 정보
runner.execute_command("stat rhi")
runner.execute_command("stat memory")
```

### 시나리오 2: 렌더링 설정

```python
import console_command_runner as runner

# 해상도 변경
runner.set_resolution(1920, 1080, windowed=True)

# 섀도우 품질
runner.execute_command("r.Shadow.MaxResolution", "2048")

# 안티앨리어싱
runner.execute_command("r.PostProcessAAQuality", "6")
```

### 시나리오 3: 디버그 뷰

```python
import console_command_runner as runner

# 와이어프레임
runner.execute_command("viewmode", "wireframe")

# 콜리전 표시
runner.execute_command("show", "collision")

# 네비메시 표시
runner.execute_command("show", "navigation")
```

## 🔧 커스터마이징

### 번역 사전 수정

`translation_dictionary.json`:

```json
{
    "Landscape": "랜드스케이프",
    "Render": "렌더",
    "YourTerm": "당신의_번역"
}
```

### 프리셋 추가

`console_command_runner_gui.py`:

```python
COMMAND_PRESETS = {
    "My Category": {
        "내 명령어": "my.command arg1 arg2",
    }
}
```

### 스코프 설정

`generate_console_command_list.py`:

```python
SCOPES_TO_PROCESS = ["r", "a", "sg"]  # 처리할 스코프
```

## 🐛 문제 해결

### "데이터 파일을 찾을 수 없습니다"

```python
# 데이터 재생성
import generate_console_command_list
generate_console_command_list.generate_command_list_for_scopes()
```

### "PySide2를 설치해주세요"

```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "PySide2"])
```

### "모듈을 찾을 수 없습니다"

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
```

## 📚 더 알아보기

- **상세 가이드**: `README_ConsoleCommandRunner.md`
- **GUI 구현**: `GUI_GUIDE.md`
- **소스 코드**: 각 `.py` 파일의 독스트링 참조

## 🎨 GUI 스크린샷

### Qt GUI 버전

```
┌─────────────────────────────────────────┐
│ 언리얼 콘솔 명령어 실행기                 │
├─────────────────────────────────────────┤
│ 검색: [___] 스코프: [전체▼]              │
├─────────────────────────────────────────┤
│ [명령어] [즐겨찾기] [히스토리] [프리셋]    │
│ ┌─────────────────────────────────┐     │
│ │ [r] r.SetRes                    │     │
│ │ [r] r.VSync                     │     │
│ │ [a] a.Volume                    │     │
│ └─────────────────────────────────┘     │
├─────────────────────────────────────────┤
│ 명령어: r.SetRes                         │
│ 설명: 해상도를 설정합니다                │
│ 인자: [1920x1080w] [실행] [⭐]          │
└─────────────────────────────────────────┘
```

## 🎯 주요 명령어 치트시트

### Performance
```python
runner.quick_fps()              # FPS 표시
runner.quick_unit()             # 프레임 시간
runner.quick_gpu()              # GPU 통계
runner.execute_command("stat rhi")      # 렌더 통계
runner.execute_command("stat memory")   # 메모리 통계
```

### Rendering
```python
runner.set_resolution(1920, 1080, True)
runner.execute_command("r.VSync", "0")
runner.execute_command("r.SetRes", "3840x2160f")
runner.execute_command("r.Shadow.MaxResolution", "2048")
```

### Debug
```python
runner.execute_command("viewmode", "wireframe")
runner.execute_command("viewmode", "lit")
runner.execute_command("show", "collision")
runner.execute_command("show", "navigation")
```

### Editor
```python
runner.execute_command("t.MaxFPS", "120")
runner.execute_command("r.Editor.Viewport.OverrideLOD", "0")
```

## 🚀 다음 단계

1. ✅ 데이터 생성 완료
2. ✅ CLI로 테스트
3. 🎨 Qt GUI 또는 에디터 위젯 선택
4. ⭐ 자주 쓰는 명령어 즐겨찾기 추가
5. 🎯 커스텀 프리셋 만들기

## 💬 피드백

개선 사항이나 버그 발견 시 이슈로 알려주세요!

---

**Happy Console Commanding! 🎮**

최종 업데이트: 2025년 10월 18일
