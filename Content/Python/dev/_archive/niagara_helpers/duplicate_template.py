import unreal

original_path = "/Niagara/DefaultAssets/Templates/Systems/FountainLightweight"
original_asset = unreal.EditorAssetLibrary.load_asset(original_path)

if not original_asset:
    print(f"ERROR: Could not load original template at {original_path}")
    sys.exit(1)

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
duplicated = asset_tools.duplicate_asset("NS_Fire", "/Game", original_asset)

if duplicated:
    print(f"SUCCESS: Duplicated asset to {duplicated.get_path_name()}")
    unreal.EditorAssetLibrary.save_loaded_asset(duplicated)
else:
    print("ERROR: Failed to duplicate asset.")
