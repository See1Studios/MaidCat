import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
# We want to find Niagara Systems and Emitters
systems = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraSystem"))
emitters = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraEmitter"))

print(f"Total Niagara Systems found: {len(systems)}")
for s in systems[:30]:
    print(f"  System: {s.package_name} | {s.asset_name} | {s.package_path}")

print(f"Total Niagara Emitters found: {len(emitters)}")
for e in emitters[:30]:
    print(f"  Emitter: {e.package_name} | {e.asset_name} | {e.package_path}")
