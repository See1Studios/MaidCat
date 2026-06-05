import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
factory = unreal.NiagaraSystemFactoryNew()
# Set edit_after_new to False to avoid opening editor UI automatically
factory.set_editor_property("edit_after_new", False)

package_path = "/Game"
asset_name = "NS_FireEffect_Test"

print("Creating Niagara System...")
try:
    new_asset = asset_tools.create_asset(asset_name, package_path, unreal.NiagaraSystem, factory)
    print(f"Created Niagara System: {new_asset}")
except Exception as e:
    print(f"Error: {e}")
