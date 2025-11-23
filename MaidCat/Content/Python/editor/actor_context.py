import unreal
import util.name as const
import tool.pp_preset as pp_preset
import importlib

TARGET_MENU = const.ACTOR_CONTEXT

def register():
    importlib.reload(pp_preset)
    pp_preset.register_to(const.ACTOR_CONTEXT)

def unregister():
    pp_preset.unregister()

if __name__ == "__main__":
    register()