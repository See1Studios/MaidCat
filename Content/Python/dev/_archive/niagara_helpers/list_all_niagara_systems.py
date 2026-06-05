import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
systems = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraSystem"))

print("All Niagara Systems:")
for s in systems:
    print(f"  {s.package_name}")
