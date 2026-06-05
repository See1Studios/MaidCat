import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
systems = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraSystem"))
emitters = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraEmitter"))

print("All Niagara Systems with fire/smoke/flame/explosion:")
for s in systems:
    path = str(s.package_name).lower()
    if any(k in path for k in ['fire', 'smoke', 'flame', 'explosion', 'vfx', 'effect']):
        print(f"  System: {s.package_name}")

print("\nAll Niagara Emitters with fire/smoke/flame/explosion:")
for e in emitters:
    path = str(e.package_name).lower()
    if any(k in path for k in ['fire', 'smoke', 'flame', 'explosion', 'vfx', 'effect']):
        print(f"  Emitter: {e.package_name}")
