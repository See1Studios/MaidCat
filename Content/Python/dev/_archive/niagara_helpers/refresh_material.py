import unreal

selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
target_asset = None
for asset in selected_assets:
    if isinstance(asset, (unreal.Material, unreal.MaterialFunction)):
        target_asset = asset
        break

if target_asset:
    subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    subsystem.close_all_editors_for_asset(target_asset)
    unreal.System.delay(0.1) # Wait a tiny bit
    subsystem.open_editor_for_assets([target_asset])
    print("SUCCESS: Editor reopened to refresh UI")
else:
    print("ERROR: No Material selected")
