# Qt UI Loader for Unreal Engine

개선된 Qt UI 로더 - .ui 파일 자동 검색 및 Fallback UI 지원

## 🚀 특징

### ✅ 자동 .ui 파일 검색
- 지정된 경로
- 스크립트와 같은 폴더
- 프로젝트 내 여러 표준 경로 자동 탐색

### ✅ Fallback UI
- .ui 파일이 없어도 작동
- 실용적인 기본 UI 제공
- Unreal Engine 정보 표시
- 선택된 에셋 확인

### ✅ 에러 처리
- 파일 없음 처리
- 로딩 실패 시 자동 Fallback
- 명확한 로그 메시지

### ✅ Unreal 통합
- Slate 윈도우 부모 지정
- 엔진 버전 조회
- 에셋 선택 상태 확인
- 프로젝트 경로 정보

## 📦 사용 방법

### 1. 기본 실행 (.ui 파일 자동 검색)

```python
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())
```

### 2. 특정 .ui 파일 지정

```python
import sys
sys.path.append(r'D:/GitHub/See1Unreal5/Content/Python/developer')
from QtTest import open_qt_window

# 특정 .ui 파일 로드
open_qt_window(r"D:/path/to/your/custom.ui")
```

### 3. Fallback UI 사용 (파일 없이)

```python
from QtTest import open_qt_window

# .ui 파일 없이 기본 UI 표시
open_qt_window()
```

## 📁 .ui 파일 검색 순서

1. **지정된 경로** (파라미터로 전달)
2. **스크립트 폴더**: `Content/Python/developer/QtTest.ui`
3. **표준 경로들**:
   - `Content/Python/developer/ui/`
   - `Content/Python/Test/`
   - `Content/Python/ui/`

## 🎨 Qt Designer로 .ui 파일 만들기

### 1. Qt Designer 실행

```bash
# Windows
designer
```

또는 직접 실행:
```bash
C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\ThirdParty\Python3\Win64\Scripts\pyside6-designer.exe
```

### 2. UI 디자인

1. 새 Widget 생성
2. 컴포넌트 배치 (버튼, 레이블 등)
3. 객체 이름 설정 (중요!)
   - 버튼: `pushButton`, `btnTest`, `btnExecute` 등

### 3. 저장

권장 위치:
```
Content/Python/developer/ui/YourUI.ui
```

### 4. 스크립트에서 로드

```python
from QtTest import open_qt_window

open_qt_window(r"D:/GitHub/See1Unreal5/Content/Python/developer/ui/YourUI.ui")
```

## 💡 .ui 파일 예제

### 기본 QtTest.ui

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>300</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Unreal Qt Tool</string>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QLabel" name="label">
     <property name="text">
      <string>Unreal Engine Qt Tool</string>
     </property>
     <property name="alignment">
      <set>Qt::AlignCenter</set>
     </property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="pushButton">
     <property name="text">
      <string>Show Engine Version</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
```

이 파일을 `Content/Python/developer/QtTest.ui`로 저장하세요.

## 🔧 커스터마이징

### 자신만의 UI 클래스 만들기

```python
from QtTest import UnrealQtWindow
from PySide6.QtWidgets import QVBoxLayout, QPushButton

class MyCustomUI(UnrealQtWindow):
    def __init__(self):
        super().__init__()
        self.setup_custom_ui()
    
    def setup_custom_ui(self):
        layout = QVBoxLayout(self)
        
        btn = QPushButton("My Custom Button")
        btn.clicked.connect(self.my_action)
        layout.addWidget(btn)
    
    def my_action(self):
        import unreal
        unreal.log("Custom action executed!")

# 사용
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MyCustomUI()
    window.show()
    
    import unreal
    unreal.parent_external_window_to_slate(window.winId())
```

### 버튼 연결 커스터마이징

```python
def connect_ui_elements(self):
    """
    로드된 UI의 요소들을 찾아서 연결
    """
    # 여러 버튼 찾기
    btn_save = self.loaded_widget.findChild(QPushButton, 'btnSave')
    if btn_save:
        btn_save.clicked.connect(self.on_save)
    
    btn_load = self.loaded_widget.findChild(QPushButton, 'btnLoad')
    if btn_load:
        btn_load.clicked.connect(self.on_load)
    
    # 입력 필드 찾기
    from PySide6.QtWidgets import QLineEdit
    text_input = self.loaded_widget.findChild(QLineEdit, 'lineEdit')
    if text_input:
        text_input.textChanged.connect(self.on_text_changed)
```

## 📊 Fallback UI 기능

### 제공되는 기능:

1. **📋 Show Engine Version**
   - Unreal Engine 버전 표시
   - 메시지 박스로 알림

2. **🎯 Show Selected Assets**
   - Content Browser에서 선택된 에셋 목록
   - 최대 10개까지 표시

3. **🔄 Refresh Info**
   - 엔진 정보 새로고침
   - 프로젝트 경로, Python 버전 등

4. **📂 Load .ui File**
   - 파일 선택 대화상자
   - 다른 .ui 파일 동적 로드

## 🐛 문제 해결

### .ui 파일을 찾을 수 없음

**해결책:**
1. 파일 경로 확인
2. 표준 경로에 복사:
   ```
   Content/Python/developer/ui/
   ```
3. 절대 경로로 직접 지정

### 윈도우가 표시되지 않음

**해결책:**
```python
# parent_external_window_to_slate 호출 확인
import unreal
unreal.parent_external_window_to_slate(window.winId())
```

### 버튼이 작동하지 않음

**해결책:**
1. Qt Designer에서 객체 이름 확인
2. 스크립트의 `button_names` 리스트에 추가:
   ```python
   button_names = ['pushButton', 'btnTest', 'btnExecute', 'yourButtonName']
   ```

### 이전 윈도우가 계속 표시됨

**해결책:**
```python
# 스크립트가 자동으로 처리하지만, 수동으로:
from QtTest import UnrealQtWindow

if UnrealQtWindow._instance:
    UnrealQtWindow._instance.close()
    UnrealQtWindow._instance.deleteLater()
```

## 📚 관련 파일

- `qt_template.py` - 더 복잡한 템플릿
- `qt_simple_example.py` - 간단한 예제들
- `README_PySide6.md` - PySide6 전체 가이드

## 🎯 사용 시나리오

### 시나리오 1: 빠른 테스트
```python
# .ui 파일 없이 바로 실행
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())
```

### 시나리오 2: 커스텀 UI
```python
# Qt Designer로 만든 UI 로드
from QtTest import open_qt_window
open_qt_window(r"D:/MyProject/ui/custom_tool.ui")
```

### 시나리오 3: 프로그래매틱 확장
```python
# 코드로 UI 확장
from QtTest import UnrealQtWindow

class MyTool(UnrealQtWindow):
    def __init__(self):
        super().__init__()
        # 추가 UI 요소 구현
```

## ⚡ 성능 팁

1. **인스턴스 재사용**: 클래스 변수로 참조 유지
2. **적절한 정리**: close()와 deleteLater() 사용
3. **QApplication 재사용**: 이미 존재하는 인스턴스 사용

## 📝 변경 이력

### v2.0 (현재)
- ✅ 자동 .ui 파일 검색
- ✅ Fallback UI 추가
- ✅ 에러 처리 개선
- ✅ Unreal 통합 기능 추가
- ✅ 재사용 가능한 클래스 구조

### v1.0 (이전)
- 기본 .ui 파일 로더
- 하드코딩된 경로
- 에러 처리 없음
