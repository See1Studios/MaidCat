import unreal

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
materials = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Engine", asset_name="Material"))
material_instances = asset_registry.get_assets_by_class(unreal.TopLevelAssetPath(package_name="/Script/Engine", asset_name="MaterialInstanceConstant"))

print(f"Total Materials: {len(materials)}, Total Instances: {len(material_instances)}")

print("\nMatching Materials:")
for m in materials:
    name = str(m.asset_name).lower()
    path = str(m.package_name).lower()
    if any(k in name or k in path for k in ['fire', 'flame', 'smoke', 'particle', 'm_fx', 'glow']):
        print(f"  Material: {m.package_name} ({m.asset_class_path.asset_name})")

print("\nMatching Material Instances:")
for m in material_instances:
    name = str(m.asset_name).lower()
    path = str(m.package_name).lower()
    if any(k in name or k in path for k in ['fire', 'flame', 'smoke', 'particle', 'm_fx', 'glow']):
        print(f"  Instance: {m.package_name} ({m.asset_class_path.asset_name})")
