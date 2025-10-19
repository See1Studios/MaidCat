# Unreal Engine PySide6 UI Tools

UE 5.5 (Python 3.11)용 PySide6 UI 템플릿 및 예제

## 📋 요구사항

- **Unreal Engine 5.5** (Python 3.11)
- **PySide6** (PySide2는 Python 3.11과 호환되지 않음)

## 🚀 설치

### 1. PySide6 설치

Unreal Editor Python 콘솔에서:

```python
# 방법 1: PySide6만 설치
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_pyside2.py').read())

# 방법 2: 여러 패키지 함께 설치 (PySide6, numpy, pillow, requests, pyyaml)
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_package.py').read())
```

### 2. Unreal Editor 재시작 (권장)

패키지가 제대로 로드되도록 에디터를 재시작하세요.

## 📁 파일 설명

### `qt_template.py`
완전한 PySide6 템플릿으로 두 가지 방식 지원:
- **방법 1**: Qt Designer `.ui` 파일 로드
- **방법 2**: Python 코드로 UI 생성 (기본값)

**사용법:**
```python
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_template.py').read())
```

**주요 기능:**
- ✅ Programmatic UI creation (코드로 UI 생성)
- ✅ Qt Designer .ui 파일 로드 지원
- ✅ Unreal Slate에 자동 부모 지정
- ✅ 기존 윈도우 인스턴스 관리
- ✅ 예제 컨트롤들 (체크박스, 입력, 버튼)

### `qt_simple_example.py`
간단한 PySide6 사용 예제들

**사용법:**
```python
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_simple_example.py').read())
```

**포함된 예제:**
1. `show_simple_dialog()` - 메시지 박스
2. `show_input_dialog()` - 사용자 입력
3. `show_custom_window()` - Unreal 통합 윈도우

## 💡 사용 예제

### 기본 메시지 박스
```python
from PySide6 import QtWidgets
import unreal

app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])

msg = QtWidgets.QMessageBox()
msg.setText("Hello from Unreal!")
msg.exec()
```

### Unreal과 통합된 윈도우
```python
from PySide6 import QtWidgets, QtCore
import unreal

class MyTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Unreal Tool")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        btn = QtWidgets.QPushButton("Get Selected Assets")
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)
    
    def on_click(self):
        assets = unreal.EditorUtilityLibrary.get_selected_assets()
        unreal.log(f"Selected: {len(assets)} assets")

# 생성 및 표시
app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication([])

window = MyTool()
window.show()

# Unreal Slate에 부모 지정 (중요!)
unreal.parent_external_window_to_slate(window.winId())
```

### 선택된 에셋 작업
```python
from PySide6 import QtWidgets
import unreal

def process_selected_assets():
    selected = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected:
        QtWidgets.QMessageBox.warning(None, "Warning", "No assets selected!")
        return
    
    for asset in selected:
        unreal.log(f"Processing: {asset.get_name()}")
        # 여기에 작업 코드 추가
    
    QtWidgets.QMessageBox.information(
        None, 
        "Complete", 
        f"Processed {len(selected)} assets"
    )

# 실행
process_selected_assets()
```

## 🎨 Qt Designer 사용하기

### .ui 파일 생성

1. **Qt Designer 설치** (PySide6와 함께 설치됨)
   ```bash
   # Windows
   C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\ThirdParty\Python3\Win64\python.exe -m pip install pyside6-tools
   ```

2. **Qt Designer 실행**
   ```bash
   designer
   ```

3. **UI 생성 및 저장**
   - `Content/Python/developer/ui/` 폴더에 `.ui` 파일 저장

4. **코드에서 로드**
   ```python
   from PySide6 import QtUiTools, QtCore
   from pathlib import Path
   
   ui_file_path = Path(__file__).parent / "ui" / "mywindow.ui"
   ui_file = QtCore.QFile(str(ui_file_path))
   ui_file.open(QtCore.QFile.OpenModeFlag.ReadOnly)
   
   loader = QtUiTools.QUiLoader()
   widget = loader.load(ui_file)
   ui_file.close()
   ```

## 🔧 문제 해결

### PySide6 import 오류
```python
# PySide6가 설치되었는지 확인
import sys
print(sys.path)

# 설치 경로 확인
# Content/Python/Lib/site-packages 에 PySide6 폴더가 있어야 함
```

### 윈도우가 Unreal 뒤에 숨음
```python
# 반드시 parent_external_window_to_slate() 호출
unreal.parent_external_window_to_slate(window.winId())
```

### 윈도우가 닫히지 않음
```python
# close() 와 deleteLater() 모두 호출
window.close()
window.deleteLater()
```

### 가비지 컬렉션으로 윈도우가 사라짐
```python
# 클래스 변수로 참조 유지
class MyTool(QtWidgets.QWidget):
    window = None  # 클래스 변수

MyTool.window = MyTool()
MyTool.window.show()
```

## 📚 추가 리소스

- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt for Python Examples](https://doc.qt.io/qtforpython-6/examples/index.html)
- [Unreal Python API](https://docs.unrealengine.com/5.5/en-US/PythonAPI/)

## ⚠️ 중요 참고사항

### PySide2 vs PySide6

| 항목 | PySide2 | PySide6 |
|-----|---------|---------|
| Python 3.11 | ❌ 지원 안함 | ✅ 지원 |
| Qt 버전 | Qt 5 | Qt 6 |
| UE 5.5 | ❌ 사용 불가 | ✅ 사용 가능 |

**UE 5.5 = Python 3.11 → PySide6 필수!**

### Import 차이점
```python
# PySide2 (구버전)
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader

# PySide6 (신버전)
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
```

### Enum 차이점
```python
# PySide2
QtCore.Qt.AlignCenter
QtWidgets.QMessageBox.Information

# PySide6
QtCore.Qt.AlignmentFlag.AlignCenter
QtWidgets.QMessageBox.Icon.Information
```

## 🎯 VS Code 설정

Python autocomplete가 작동하도록 `.vscode/settings.json`에 다음 경로가 포함되어야 합니다:

```json
{
    "python.autoComplete.extraPaths": [
        "${workspaceFolder}/Content/Python/Lib/site-packages",
        "${workspaceFolder}/Intermediate/PythonStub"
    ],
    "python.analysis.extraPaths": [
        "${workspaceFolder}/Content/Python/Lib/site-packages",
        "${workspaceFolder}/Intermediate/PythonStub"
    ]
}
```

## 📝 라이선스

프로젝트 라이선스를 따릅니다.
