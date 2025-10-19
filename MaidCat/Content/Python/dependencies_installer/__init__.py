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
        from dependencies_installer.vendor import py_pip
    return py_pip
            

def install_dependencies():
    """Install dependencies from requirements.txt."""
    # Initialize
    py_pip = get_py_pip()
    py_pip.default_target_path = plugin_site_dir()
    py_pip.python_interpreter = unreal.get_interpreter_executable_path()
    
    # Find requirements.txt file
    current_file = Path(__file__)
    requirements_path = current_file.parent.parent / "requirements.txt"
    
    # Install requirements
    py_pip.install(requirements=requirements_path)
