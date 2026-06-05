import unreal

def get_textures_and_materials():

    editorAssetLib = unreal.EditorAssetLibrary()
    all_assets = unreal.AssetRegistryHelpers.get_asset_registry().get_all_assets()
    textures = [x for x in all_assets if x.asset_class_path.asset_name == 'Texture2D' and x.package_path.__str__().startswith('/Game/')]
    materials = [x for x in all_assets if x.asset_class_path.asset_name == 'Material' and x.package_path.__str__().startswith('/Game/')]
    return textures, materials

textures, materials = get_textures_and_materials()

for texture in textures:
    print(texture.get_asset().blueprint_get_size_x())
    print(texture.get_asset().blueprint_get_size_y())