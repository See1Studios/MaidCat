"""
PySide6를 프로젝트의 Content/Python/Lib/site-packages에 설치하는 스크립트

NOTE: UE 5.5는 Python 3.11을 사용하므로 PySide2가 아닌 PySide6를 사용해야 합니다!
- PySide2: Python 3.10까지만 지원 (구버전)
- PySide6: Python 3.11+ 지원 (최신 버전)

Unreal Editor Python 콘솔에서 실행:
exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_pyside2.py').read())
"""

import sys
from pathlib import Path
import subprocess
import unreal

def install_to_project(package_names):
    """
    프로젝트의 Content/Python/Lib/site-packages에 패키지 설치
    
    Args:
        package_names: str or list of package names
    """
    # Ensure package_names is a list
    if isinstance(package_names, str):
        package_names = [package_names]
    
    # Get project path
    relative_project_path = unreal.Paths.project_content_dir()
    project_path = unreal.Paths.convert_relative_path_to_full(relative_project_path)
    target_path = Path(project_path) / r"Python\Lib\site-packages"
    
    # Ensure target directory exists
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Get Python interpreter path
    interpreter_path = Path(unreal.get_interpreter_executable_path())
    
    # Check Python version
    version_check = subprocess.run(
        [str(interpreter_path), '--version'],
        capture_output=True,
        text=True
    )
    python_version = version_check.stdout.strip()
    
    print(f"📦 Installing: {package_names}")
    print(f"📁 Target: {target_path}")
    print(f"🐍 Python: {python_version}")
    print(f"   Path: {interpreter_path}\n")
    
    # Run pip install
    # Don't show window
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    process = subprocess.Popen(
        [str(interpreter_path), '-m', 'pip', 'install', *package_names, '--target', str(target_path)],
        startupinfo=info,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    
    # Wait for completion and get output
    stdout, stderr = process.communicate()
    
    # Print output
    if stdout:
        print(stdout)
    
    # Check for errors
    if stderr:
        # Separate warnings from errors
        if "ERROR" in stderr or process.returncode != 0:
            print(f"❌ Errors:\n{stderr}")
        else:
            print(f"ℹ️ Messages:\n{stderr}")
    
    return_code = process.returncode
    if return_code == 0:
        print(f"\n✅ Successfully installed to {target_path}")
    else:
        print(f"\n❌ Installation failed with return code {return_code}")
    
    return return_code


def main():
    """PySide6 설치 (Python 3.11+ 호환)"""
    
    print("=" * 80)
    print("PySide6 Installation to Project")
    print("=" * 80 + "\n")
    
    # PySide6 사용 (Python 3.11 호환)
    packages = ["PySide6"]
    
    print("ℹ️  NOTE: Installing PySide6 (not PySide2)")
    print("   - PySide2 is not compatible with Python 3.11+")
    print("   - PySide6 is the modern Qt for Python version\n")
    
    try:
        install_to_project(packages)
        
        print("\n" + "=" * 80)
        print("✅ Installation complete!")
        print("=" * 80)
        print("\n💡 Usage in Unreal:")
        print("   from PySide6 import QtWidgets, QtCore, QtGui")
        print("\n💡 You may need to restart Unreal Editor to use the new packages")
        
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
