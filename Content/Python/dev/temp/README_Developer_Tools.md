# 🎮 Unreal Engine PySide6 개발 도구 모음

UE 5.5 (Python 3.11) 용 PySide6 UI 개발 템플릿 및 유틸리티

## 📦 파일 구조

```
Content/Python/developer/
├── QtTest.py                    # ⭐ 개선된 UI 로더 (권장)
├── qt_template.py               # 완전한 템플릿
├── qt_simple_example.py         # 간단한 예제들
├── ui/
│   └── QtTest.ui               # 샘플 UI 파일
├── README_PySide6.md           # PySide6 전체 가이드
├── README_QtTest.md            # QtTest 상세 가이드
└── README_Developer_Tools.md   # 이 파일
```

## 🚀 빠른 시작

### 1. PySide6 설치 (한 번만)

```python
# Unreal Editor Python 콘솔에서:
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_pyside2.py').read())

# 또는 여러 패키지 함께:
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_package.py').read())
```

### 2. 도구 실행

```python
# 가장 간단한 방법 - QtTest (자동 UI 검색)
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())

# 간단한 예제들
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_simple_example.py').read())

# 완전한 템플릿
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_template.py').read())
```

## 📋 파일별 비교

| 파일 | 난이도 | 용도 | 특징 |
|-----|-------|------|------|
| **qt_simple_example.py** | ⭐ 초급 | 학습, 빠른 테스트 | 3가지 간단한 예제 |
| **QtTest.py** | ⭐⭐ 중급 | 실용적인 도구 개발 | .ui 파일 + Fallback UI |
| **qt_template.py** | ⭐⭐⭐ 고급 | 완전한 프로젝트 | 모든 기능 포함 |

### 🎯 qt_simple_example.py
**언제 사용?**
- PySide6 처음 시작
- 간단한 대화상자 필요
- 빠른 프로토타입

**기능:**
- ✅ 메시지 박스
- ✅ 입력 대화상자
- ✅ 간단한 커스텀 윈도우

**예제:**
```python
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_simple_example.py').read())
```

### 🎯 QtTest.py (추천! ⭐)
**언제 사용?**
- Qt Designer로 UI 디자인
- 실용적인 툴 개발
- .ui 파일 없이도 작동

**기능:**
- ✅ .ui 파일 자동 검색
- ✅ Fallback UI (파일 없어도 OK)
- ✅ 버튼 자동 연결
- ✅ Unreal 통합 기능

**예제:**
```python
# 자동 UI 검색
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/QtTest.py').read())

# 또는 특정 .ui 파일
from QtTest import open_qt_window
open_qt_window(r"D:/path/to/custom.ui")
```

### 🎯 qt_template.py
**언제 사용?**
- 복잡한 프로젝트
- 완전한 커스터마이징
- 많은 기능 필요

**기능:**
- ✅ .ui 파일 로드
- ✅ 프로그래매틱 UI
- ✅ 완전한 예제 코드
- ✅ 확장 가능한 구조

**예제:**
```python
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/qt_template.py').read())
```

## 🛠️ 개발 워크플로우

### 방법 1: 코드로 UI 생성 (빠름)
```python
from PySide6 import QtWidgets
import unreal

class MyTool(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        
        btn = QtWidgets.QPushButton("Click Me")
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)
    
    def on_click(self):
        unreal.log("Clicked!")

# 실행
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
window = MyTool()
window.show()
unreal.parent_external_window_to_slate(window.winId())
```

### 방법 2: Qt Designer로 UI 디자인 (직관적)

1. **Qt Designer 실행**
   ```bash
   designer
   ```

2. **UI 디자인 및 저장**
   - `Content/Python/developer/ui/mytool.ui`

3. **QtTest.py로 로드**
   ```python
   from QtTest import open_qt_window
   open_qt_window(r"D:/GitHub/See1Unreal5/Content/Python/developer/ui/mytool.ui")
   ```

### 방법 3: 템플릿 커스터마이징 (완전한 제어)

1. **qt_template.py 복사**
   ```bash
   cp qt_template.py my_custom_tool.py
   ```

2. **클래스 수정**
   ```python
   class MyCustomTool(UnrealUITemplate):
       def __init__(self):
           super().__init__()
           # 커스터마이징
   ```

3. **실행**
   ```python
   exec(open(r'D:/GitHub/See1Unreal5/Content/Python/developer/my_custom_tool.py').read())
   ```

## 💡 실전 예제

### 예제 1: 선택된 에셋 이름 변경

```python
from PySide6 import QtWidgets
import unreal

class AssetRenamer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asset Renamer")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # 입력 필드
        self.prefix_input = QtWidgets.QLineEdit()
        self.prefix_input.setPlaceholderText("Prefix...")
        layout.addWidget(QtWidgets.QLabel("Add Prefix:"))
        layout.addWidget(self.prefix_input)
        
        # 실행 버튼
        btn = QtWidgets.QPushButton("Rename Selected Assets")
        btn.clicked.connect(self.rename_assets)
        layout.addWidget(btn)
    
    def rename_assets(self):
        prefix = self.prefix_input.text()
        if not prefix:
            QtWidgets.QMessageBox.warning(self, "Warning", "Enter a prefix!")
            return
        
        selected = unreal.EditorUtilityLibrary.get_selected_assets()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Warning", "No assets selected!")
            return
        
        for asset in selected:
            old_name = asset.get_name()
            new_name = f"{prefix}_{old_name}"
            
            # 에셋 이름 변경
            unreal.EditorAssetLibrary.rename_asset(
                asset.get_path_name(),
                f"{asset.get_path_name().rsplit('/', 1)[0]}/{new_name}"
            )
            
            unreal.log(f"Renamed: {old_name} -> {new_name}")
        
        QtWidgets.QMessageBox.information(
            self, "Success", f"Renamed {len(selected)} assets!"
        )

# 실행
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
window = AssetRenamer()
window.show()
unreal.parent_external_window_to_slate(window.winId())
```

### 예제 2: 배치된 액터 목록

```python
from PySide6 import QtWidgets
import unreal

class ActorLister(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Actor Lister")
        self.setMinimumSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # 리스트 위젯
        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)
        
        # 새로고침 버튼
        btn = QtWidgets.QPushButton("🔄 Refresh Actor List")
        btn.clicked.connect(self.refresh_list)
        layout.addWidget(btn)
        
        # 초기 로드
        self.refresh_list()
    
    def refresh_list(self):
        self.list_widget.clear()
        
        # 현재 레벨의 모든 액터 가져오기
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        
        for actor in actors:
            actor_name = actor.get_name()
            actor_class = actor.get_class().get_name()
            self.list_widget.addItem(f"{actor_name} ({actor_class})")
        
        unreal.log(f"Found {len(actors)} actors in level")

# 실행
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
window = ActorLister()
window.show()
unreal.parent_external_window_to_slate(window.winId())
```

### 예제 3: 텍스처 크기 체커

```python
from PySide6 import QtWidgets
import unreal

class TextureSizeChecker(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texture Size Checker")
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # 결과 표시
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # 체크 버튼
        btn = QtWidgets.QPushButton("Check Selected Textures")
        btn.clicked.connect(self.check_textures)
        layout.addWidget(btn)
    
    def check_textures(self):
        selected = unreal.EditorUtilityLibrary.get_selected_assets()
        
        results = []
        for asset in selected:
            if isinstance(asset, unreal.Texture2D):
                width = asset.get_editor_property('source_width')
                height = asset.get_editor_property('source_height')
                size_mb = asset.get_resource_size_bytes() / (1024 * 1024)
                
                results.append(
                    f"{asset.get_name()}:\n"
                    f"  Size: {width}x{height}\n"
                    f"  Memory: {size_mb:.2f} MB\n"
                )
        
        if results:
            self.result_text.setPlainText("\n".join(results))
        else:
            self.result_text.setPlainText("No textures selected!")

# 실행
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
window = TextureSizeChecker()
window.show()
unreal.parent_external_window_to_slate(window.winId())
```

## 🔧 디버깅 팁

### PySide6가 import 안 됨
```python
# 설치 확인
import sys
print(sys.path)

# 설치 경로에 있는지 확인
# Content/Python/Lib/site-packages/PySide6/
```

### 윈도우가 Unreal 뒤에 숨음
```python
# 반드시 호출!
import unreal
unreal.parent_external_window_to_slate(window.winId())
```

### 스크립트 수정이 반영 안 됨
```python
# 모듈 리로드
import importlib
import your_module
importlib.reload(your_module)

# 또는 Unreal Editor 재시작
```

### 윈도우가 사라짐 (가비지 컬렉션)
```python
# 클래스 변수로 참조 유지
class MyTool(QtWidgets.QWidget):
    _instance = None

MyTool._instance = MyTool()
MyTool._instance.show()
```

## 📚 추가 학습 자료

### 공식 문서
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Qt for Python Examples](https://doc.qt.io/qtforpython-6/examples/index.html)
- [Unreal Python API](https://docs.unrealengine.com/5.5/en-US/PythonAPI/)

### 프로젝트 내 문서
- `README_PySide6.md` - PySide6 완벽 가이드
- `README_QtTest.md` - QtTest 상세 설명
- `install_package.py` - 패키지 설치 도구

## 🎯 권장 학습 순서

1. **초급**: `qt_simple_example.py` 실행 및 수정
2. **중급**: `QtTest.py`로 실용적인 툴 만들기
3. **고급**: `qt_template.py` 커스터마이징
4. **마스터**: Qt Designer + Python 조합

## ⚡ 프로덕션 체크리스트

도구를 배포하기 전 확인사항:

- [ ] PySide6 의존성 문서화
- [ ] 에러 처리 추가 (try-except)
- [ ] 사용자 입력 검증
- [ ] 실행 취소 기능 (위험한 작업)
- [ ] 진행 상황 표시 (긴 작업)
- [ ] 로그 메시지 추가
- [ ] parent_external_window_to_slate() 호출
- [ ] 윈도우 인스턴스 관리

## 🎨 UI 디자인 팁

### 색상 스킴 (Unreal 스타일)
```python
# 다크 테마
style = """
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
}
QPushButton {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    padding: 5px;
    border-radius: 3px;
}
QPushButton:hover {
    background-color: #3e3e42;
}
"""
widget.setStyleSheet(style)
```

### 아이콘 사용
```python
# 유니코드 이모지 활용
btn = QPushButton("🎮 Play")
btn = QPushButton("💾 Save")
btn = QPushButton("🔍 Search")
```

## 📝 라이선스

프로젝트 라이선스를 따릅니다.
