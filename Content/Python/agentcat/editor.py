import unreal
import time

def get_selected_assets(allowed_classes=None):
    """
    Retrieve currently selected assets in the Content Browser.
    
    Args:
        allowed_classes (tuple or list): Optional list of unreal classes to filter by.
        
    Returns:
        list: List of unreal.Object assets selected.
    """
    selected = unreal.EditorUtilityLibrary.get_selected_assets()
    if not allowed_classes:
        return list(selected)
        
    filtered = []
    for asset in selected:
        if isinstance(asset, tuple(allowed_classes)):
            filtered.append(asset)
    return filtered

def reopen_editor(asset):
    """
    Close and reopen the editor window for a specific asset to force UI repaint.
    
    Args:
        asset (unreal.Object): The asset to reopen.
        
    Returns:
        bool: True if closed and reopened, False otherwise.
    """
    if not asset:
        return False
        
    editor_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    
    # Close active editor for this asset
    editor_subsystem.close_all_editors_for_asset(asset)
    time.sleep(0.1)
    
    # Reopen editor
    return editor_subsystem.open_editor_for_assets([asset])
