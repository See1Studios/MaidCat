from pathlib import Path
import unreal


def plugin_site_dir() -> Path:
    """
    Return the site-packages path for the current plugin
    Note: this folder might not exist
    """
    plugin_root = Path(__file__).parent.parent.parent.parent
    return plugin_root / r"Content\Python\Lib\site-packages"


def get_py_pip():
    try:
        import py_pip
    except ImportError:
        from .vendor import py_pip
    return py_pip
            

def install_dependencies():
    """Install dependencies from requirements.txt."""
    # Initialize
    py_pip = get_py_pip()
    py_pip.default_target_path = plugin_site_dir()
    py_pip.python_interpreter = unreal.get_interpreter_executable_path()
    
    # Find requirements.txt file
    current_file = Path(__file__)
    # dependencies_installer는 tool 폴더 안에 있으므로 경로 수정
    # tool/dependencies_installer/__init__.py -> tool/dependencies_installer -> tool -> Python -> requirements.txt
    requirements_path = current_file.parent.parent.parent / "requirements.txt"
    
    print(f"Looking for requirements.txt at: {requirements_path}")
    if not requirements_path.exists():
        print(f"⚠️  requirements.txt not found at {requirements_path}")
        return
    
    # Install requirements
    py_pip.install(requirements=requirements_path)


print("Installing dependencies...")