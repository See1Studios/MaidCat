import unreal

ns_path = "/Game/NS_Fire"
ns_asset = unreal.EditorAssetLibrary.load_asset(ns_path)

if ns_asset:
    subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    subsystem.open_editor_for_assets([ns_asset])
    print(f"SUCCESS: Opened editor for {ns_path}")
else:
    print(f"ERROR: Could not load asset {ns_path}")
