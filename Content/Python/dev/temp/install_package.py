"""
범용 Python 패키지 설치 스크립트
Content/Python/Lib/site-packages에 패키지 설치

사용법 1 - Unreal Editor Python 콘솔에서 직접 실행:
    exec(open(r'D:/GitHub/See1Unreal5/Content/Python/install_package.py').read())

사용법 2 - 모듈로 import해서 사용:
    import sys
    sys.path.append(r'D:/GitHub/See1Unreal5/Content/Python')
    from install_package import install_to_project
    
    install_to_project("numpy")
    install_to_project(["requests", "pillow"])
"""

import sys
from pathlib import Path
import subprocess
import unreal


def install_to_project(package_names, upgrade=False):
    """
    프로젝트의 Content/Python/Lib/site-packages에 패키지 설치
    
    Args:
        package_names: str or list of package names
        upgrade: bool, upgrade existing packages
    
    Returns:
        int: return code (0 = success, non-zero = failure)
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
    
    print("=" * 80)
    print(f"📦 Installing: {', '.join(package_names)}")
    print(f"📁 Target: {target_path}")
    print(f"🐍 Python: {python_version}")
    print("=" * 80 + "\n")
    
    # Build command
    cmd = [str(interpreter_path), '-m', 'pip', 'install']
    
    if upgrade:
        cmd.append('--upgrade')
    
    cmd.extend(package_names)
    cmd.extend(['--target', str(target_path)])
    
    # Run pip install
    # Don't show window on Windows
    startupinfo = None
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    process = subprocess.Popen(
        cmd,
        startupinfo=startupinfo,
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
            # Just informational messages
            for line in stderr.split('\n'):
                if line.strip() and not line.startswith('[notice]'):
                    print(f"ℹ️  {line}")
    
    return_code = process.returncode
    print("\n" + "=" * 80)
    if return_code == 0:
        print(f"✅ Successfully installed to:")
        print(f"   {target_path}")
    else:
        print(f"❌ Installation failed with return code {return_code}")
    print("=" * 80)
    
    return return_code


def uninstall_from_project(package_names):
    """
    프로젝트의 site-packages에서 패키지 제거
    
    Args:
        package_names: str or list of package names
    
    Returns:
        int: return code (0 = success, non-zero = failure)
    """
    # Ensure package_names is a list
    if isinstance(package_names, str):
        package_names = [package_names]
    
    # Get Python interpreter path
    interpreter_path = Path(unreal.get_interpreter_executable_path())
    
    print("=" * 80)
    print(f"🗑️  Uninstalling: {', '.join(package_names)}")
    print("=" * 80 + "\n")
    
    # Build command
    cmd = [str(interpreter_path), '-m', 'pip', 'uninstall', '-y']
    cmd.extend(package_names)
    
    # Run pip uninstall
    startupinfo = None
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    process = subprocess.Popen(
        cmd,
        startupinfo=startupinfo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    
    # Wait for completion and get output
    stdout, stderr = process.communicate()
    
    # Print output
    if stdout:
        print(stdout)
    
    if stderr:
        print(f"ℹ️  {stderr}")
    
    return_code = process.returncode
    print("\n" + "=" * 80)
    if return_code == 0:
        print(f"✅ Successfully uninstalled")
    else:
        print(f"❌ Uninstallation failed with return code {return_code}")
    print("=" * 80)
    
    return return_code


def main():
    """
    대화형 패키지 설치
    """
    print("\n" + "=" * 80)
    print("Python Package Installer for Unreal Project")
    print("=" * 80)
    print("\nCommon packages for UE 5.5 (Python 3.11+):")
    print("  • PySide6     - Qt for Python (GUI)")
    print("  • numpy       - Numerical computing")
    print("  • pillow      - Image processing")
    print("  • requests    - HTTP library")
    print("  • pyyaml      - YAML parser")
    print("\n⚠️  NOTE: Use PySide6 (not PySide2) for Python 3.11+")
    print("=" * 80 + "\n")
    
    # Default packages to install
    packages = ["PySide6", "numpy", "pillow", "requests", "pyyaml"]
    
    print(f"Installing recommended packages: {', '.join(packages)}\n")
    
    install_to_project(packages)
    
    print("\n💡 Usage in Unreal Python:")
    print("   from PySide6 import QtWidgets, QtCore, QtGui")
    print("   import numpy as np")
    print("   from PIL import Image")
    print("   import requests")
    print("   import yaml")
    print("\n💡 Restart Unreal Editor to ensure all packages are loaded correctly\n")


if __name__ == "__main__":
    main()
