import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
emitters = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraEmitter"))

print("Matching emitters:")
for e in emitters:
    name = str(e.asset_name).lower()
    path = str(e.package_name).lower()
    if any(k in name or k in path for k in ['fire', 'flame', 'smoke', 'spark', 'explosion', 'burst']):
        print(f"  {e.package_name} ({e.asset_class_path.asset_name})")

systems = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraSystem"))
print("\nMatching systems:")
for s in systems:
    name = str(s.asset_name).lower()
    path = str(s.package_name).lower()
    if any(k in name or k in path for k in ['fire', 'flame', 'smoke', 'spark', 'explosion', 'burst']):
        print(f"  {s.package_name} ({s.asset_class_path.asset_name})")
