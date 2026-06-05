import unreal
import importlib
import util.name as const
import tool.level_loader as level_loader

def register():
    importlib.reload(level_loader)
    level_loader.register_to(const.WORLDBROWSER_CONTEXT)

def unregister():
    level_loader.unregister()

if __name__ == "__main__":
    register()