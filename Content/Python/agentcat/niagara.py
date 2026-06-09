import unreal

def list_systems(package_path="/Game"):
    """
    List all Niagara Systems in the project under the specified path.
    
    Args:
        package_path (str): The folder path to filter assets.
        
    Returns:
        list: List of FAssetData objects representing Niagara Systems.
    """
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    systems = asset_registry.get_assets_by_class(
        unreal.TopLevelAssetPath(package_name="/Script/Niagara", asset_name="NiagaraSystem")
    )
    
    filtered_systems = []
    for asset_data in systems:
        path = str(asset_data.package_name)
        if path.startswith(package_path):
            filtered_systems.append(asset_data)
    return filtered_systems

def duplicate_system(source_path, target_package_path, new_name):
    """
    Duplicate an existing Niagara System (e.g. from templates).
    
    Args:
        source_path (str): The path to the source Niagara System.
        target_package_path (str): The package path where the duplicate will be created.
        new_name (str): The name for the new duplicate.
        
    Returns:
        unreal.NiagaraSystem: The duplicated Niagara System asset, or None.
    """
    source_asset = unreal.EditorAssetLibrary.load_asset(source_path)
    if not source_asset:
        unreal.log_error(f"Niagara duplicate: Could not load source asset at {source_path}")
        return None
        
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    duplicated = asset_tools.duplicate_asset(new_name, target_package_path, source_asset)
    
    if duplicated:
        unreal.EditorAssetLibrary.save_loaded_asset(duplicated)
        return unreal.NiagaraSystem.cast(duplicated)
    return None

def create_blank_system(name, package_path="/Game"):
    """
    Create a blank new Niagara System.
    
    Args:
        name (str): The name of the new system.
        package_path (str): The package path where it should be created.
        
    Returns:
        unreal.NiagaraSystem: The created Niagara System, or None.
    """
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.NiagaraSystemFactoryNew()
    factory.set_editor_property("edit_after_new", False)
    
    try:
        new_asset = asset_tools.create_asset(name, package_path, unreal.NiagaraSystem, factory)
        if new_asset:
            unreal.EditorAssetLibrary.save_loaded_asset(new_asset)
            return unreal.NiagaraSystem.cast(new_asset)
    except Exception as e:
        unreal.log_error(f"Niagara create failed: {e}")
        
    return None
