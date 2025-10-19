# Python 패키지 설치 가이드

## 🎯 빠른 시작

### Unreal Editor Python 콘솔에서:

```python
import sys
sys.path.append("D:/GitHub/See1Unreal5/Content/Python/tool")
import package_manager as pm

# 도움말 보기
pm.print_help()

# 패키지 설치
pm.install_package("PySide2")

# 설치 확인
pm.list_installed_packages()
```

## 📦 설치 방법

### 방법 1: 패키지 매니저 사용 (추천)

```python
import package_manager as pm

# 단일 패키지 설치
pm.install_package("requests")
pm.install_package("pillow")
pm.install_package("numpy")

# 특정 버전 설치
pm.install_package("requests==2.28.0")

# 업그레이드
pm.install_package("requests", upgrade=True)

# 빠른 설치 (설치 + 즉시 사용 가능)
pm.quick_install("PySide2")
```

### 방법 2: 일반 패키지 일괄 설치

```python
import package_manager as pm

# 자주 쓰는 패키지 한 번에 설치
# requests, pillow, numpy, PySide2
pm.install_common_packages()
```

### 방법 3: requirements.txt 사용

**requirements.txt 만들기:**
```txt
requests>=2.28.0
pillow>=9.0.0
numpy>=1.23.0
PySide2>=5.15.0
```

**설치:**
```python
import package_manager as pm

pm.install_requirements("D:/GitHub/See1Unreal5/requirements.txt")
```

### 방법 4: PowerShell에서 직접

```powershell
# Python 경로
$Python = "C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

# 프로젝트 site-packages 경로
$Target = "D:\GitHub\See1Unreal5\Python\Lib\site-packages"

# 폴더 생성
New-Item -ItemType Directory -Force -Path $Target

# 패키지 설치
& $Python -m pip install --target $Target PySide2
```

## 🔍 패키지 관리

### 설치된 패키지 확인

```python
import package_manager as pm

# 전체 목록
pm.list_installed_packages()

# 특정 패키지 확인
pm.check_package_installed("PySide2")
```

### 패키지 제거

```python
import package_manager as pm

pm.uninstall_package("PySide2")
```

### pip 업데이트

```python
import package_manager as pm

pm.update_pip()
```

## 📍 설치 경로

패키지는 다음 위치에 설치됩니다:

```
프로젝트/Python/Lib/site-packages/
```

예시:
```
D:\GitHub\See1Unreal5\Python\Lib\site-packages\
├── requests/
├── PIL/
├── numpy/
└── PySide2/
```

## 💡 자주 사용하는 패키지

### GUI 개발
```python
pm.install_package("PySide2")     # Qt GUI
pm.install_package("PySide6")     # Qt6 GUI
```

### 데이터 처리
```python
pm.install_package("numpy")       # 수치 계산
pm.install_package("pandas")      # 데이터 분석
pm.install_package("openpyxl")    # Excel 파일
```

### 이미지 처리
```python
pm.install_package("pillow")      # 이미지 처리
pm.install_package("opencv-python") # 컴퓨터 비전
```

### 네트워크
```python
pm.install_package("requests")    # HTTP 클라이언트
pm.install_package("aiohttp")     # 비동기 HTTP
```

### 유틸리티
```python
pm.install_package("python-dotenv") # 환경 변수
pm.install_package("pyyaml")        # YAML 파서
pm.install_package("toml")          # TOML 파서
```

## 🚨 문제 해결

### "ModuleNotFoundError" 발생 시

```python
import package_manager as pm

# sys.path에 수동 추가
pm.add_to_sys_path()

# 또는 직접 추가
import sys
sys.path.insert(0, "D:/GitHub/See1Unreal5/Python/Lib/site-packages")
```

### 패키지 설치 실패 시

```python
import package_manager as pm

# pip 먼저 업데이트
pm.update_pip()

# 다시 설치 시도
pm.install_package("패키지이름")
```

### 권한 오류 시

- Unreal Editor를 관리자 권한으로 실행
- 또는 PowerShell을 관리자 권한으로 실행

### 의존성 충돌 시

```python
# 특정 버전 지정
pm.install_package("패키지이름==버전")

# 예시
pm.install_package("numpy==1.23.5")
```

## 🔄 자동 로드 설정

프로젝트에서 항상 site-packages를 사용하려면:

**InitUnreal.py 또는 startup 스크립트:**

```python
import sys
import unreal
import os

# site-packages를 sys.path에 추가
project_dir = unreal.SystemLibrary.get_project_directory()
site_packages = os.path.join(project_dir, "Python", "Lib", "site-packages")

if site_packages not in sys.path:
    sys.path.insert(0, site_packages)
    print(f"✓ site-packages 추가: {site_packages}")
```

## 📝 requirements.txt 생성

현재 설치된 패키지를 requirements.txt로 내보내기:

```python
import subprocess
import sys
import unreal

project_dir = unreal.SystemLibrary.get_project_directory()
requirements_file = f"{project_dir}requirements.txt"

# 패키지 목록 내보내기
result = subprocess.run(
    [sys.executable, "-m", "pip", "freeze"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    with open(requirements_file, 'w') as f:
        f.write(result.stdout)
    print(f"✓ requirements.txt 생성: {requirements_file}")
```

## 🎯 실전 예제

### 예제 1: PySide2로 GUI 만들기

```python
import package_manager as pm

# 1. PySide2 설치
pm.quick_install("PySide2")

# 2. 즉시 사용
from PySide2 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
window.setWindowTitle("Test")
window.show()
```

### 예제 2: HTTP 요청하기

```python
import package_manager as pm

# 1. requests 설치
pm.quick_install("requests")

# 2. 사용
import requests
response = requests.get("https://api.github.com")
print(response.json())
```

### 예제 3: 이미지 처리

```python
import package_manager as pm

# 1. Pillow 설치
pm.quick_install("pillow")

# 2. 사용
from PIL import Image
img = Image.open("texture.png")
img_resized = img.resize((512, 512))
img_resized.save("texture_512.png")
```

## 🔧 고급 설정

### 프록시 사용

```python
import subprocess
import sys
import os

# 프록시 설정
os.environ['HTTP_PROXY'] = 'http://proxy.example.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.example.com:8080'

# 설치
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "--target", site_packages,
    "--proxy", "http://proxy.example.com:8080",
    "패키지이름"
])
```

### 미러 서버 사용 (중국 등)

```python
import subprocess
import sys

subprocess.run([
    sys.executable, "-m", "pip", "install",
    "--target", site_packages,
    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
    "패키지이름"
])
```

---

## 📚 참고

- 패키지 매니저: `package_manager.py`
- 설치 경로: `프로젝트/Python/Lib/site-packages/`
- Python 버전 확인: `import sys; print(sys.version)`

**Happy Packaging! 📦**
