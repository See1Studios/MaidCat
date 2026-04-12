import unreal

def getAssetClass():

    EAL = unreal.EditorAssetLibrary()
    
    assetPaths = EAL.list_assets('/Game')
    
    for assetPath in assetPaths:
        assetData = EAL.find_asset_data(assetPath)
        assetClass = assetData.asset_class_path.asset_name
        print (assetClass)

getAssetClass()