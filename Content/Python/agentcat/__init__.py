"""
AgentCat - Unreal Engine Editor Automation & Scripting Library
Designed for AI agents and developer automation.
"""

# Check if we are running inside Unreal (where 'unreal' module exists)
unreal_available = False
try:
    import unreal
    unreal_available = True
except ImportError:
    pass

if unreal_available:
    from . import editor
    from . import material
    from . import niagara
    from . import remote

__all__ = []
if unreal_available:
    __all__.extend(['editor', 'material', 'niagara', 'remote'])
