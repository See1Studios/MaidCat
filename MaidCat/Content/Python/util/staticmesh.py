import unreal

# @unreal.uclass()
# class GetEditorAssetLibrary(unreal.EditorAssetLibrary):
#     pass

# editorAssetLib = GetEditorAssetLibrary()

def find_uv_channel_count(threshold, path_to_find="/Game/"):
    """
    Finds all Static Mesh assets in the specified working path that have more than 2 UV channels.
    Tags these assets in a collection named "StaticMeshes2+UV".
    """

    editorAssetLib = unreal.EditorAssetLibrary

    allAssets = editorAssetLib.list_assets(path_to_find, True, False)
    allAssetsCount = len(allAssets)
    #materialAssetDataList = []
    meshList = []

    if (allAssetsCount > 0):
        with unreal.ScopedSlowTask(allAssetsCount, path_to_find) as slowTask:
            slowTask.make_dialog(True)
            for asset in allAssets:
                assetData = editorAssetLib.find_asset_data(asset)
                path_to_find = assetData.asset_name
                if(assetData.asset_class_path.asset_name == "StaticMesh"):
                    mesh = assetData.get_asset()
                    num_uv_channels = unreal.EditorStaticMeshLibrary.get_num_uv_channels(mesh,0)
                    if(num_uv_channels > threshold):
                        meshList.append(mesh)

                    if slowTask.should_cancel():
                        break
                    slowTask.enter_progress_frame(1, asset)

    tagSystem = unreal.get_engine_subsystem(unreal.AssetTagsSubsystem)
    collectionName = "StaticMeshes2+UV" #Unreal Name 은 공백 특수문자 불가
    tagSystem.create_collection(collectionName, share_type=unreal.CollectionShareType.LOCAL)
    #tagSystem.add_asset_datas_to_collection(unreal.Name("TwoSided"),materialAssetDataList)
    tagSystem.add_asset_ptrs_to_collection(collectionName, meshList)