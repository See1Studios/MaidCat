import unreal

def find_heavy_materials(instruction_threshold, workingPath="/Game/"):
    editorAssetLib = unreal.EditorAssetLibrary
    materialEditingLib = unreal.MaterialEditingLibrary

    allAssets = editorAssetLib.list_assets(workingPath, True, False)
    allAssetsCount = len(allAssets)
    selectedAssetPath = workingPath

    materialObjectList = []

    if (allAssetsCount > 0):
        with unreal.ScopedSlowTask(allAssetsCount, selectedAssetPath) as slowTask:
            slowTask.make_dialog(True)
            for asset in allAssets:
                assetData = editorAssetLib.find_asset_data(asset)
                selectedAssetPath = assetData.asset_name
                if(assetData.asset_class_path.asset_name == "Material"):
                    mat = assetData.get_asset()
                    stat = materialEditingLib.get_statistics(mat)
                    if(stat.num_pixel_shader_instructions>instruction_threshold):
                        materialObjectList.append(mat)
                    if slowTask.should_cancel():
                        break
                    slowTask.enter_progress_frame(1, asset)

    tagSystem = unreal.get_engine_subsystem(unreal.AssetTagsSubsystem)
    collectionName = "HeavyMaterials"
    tagSystem.create_collection(collectionName, share_type=unreal.CollectionShareType.LOCAL)
    tagSystem.add_asset_ptrs_to_collection(collectionName, materialObjectList)

def find_two_sided(workingPath="/Game/"):
    
    editorAssetLib = unreal.EditorAssetLibrary

    allAssets = editorAssetLib.list_assets(workingPath, True, False)
    allAssetsCount = len(allAssets)
    selectedAssetPath = workingPath
    materialObjectList = []

    if (allAssetsCount > 0):
        with unreal.ScopedSlowTask(allAssetsCount, selectedAssetPath) as slowTask:
            slowTask.make_dialog(True)
            for asset in allAssets:
                assetData = editorAssetLib.find_asset_data(asset)
                selectedAssetPath = assetData.asset_name
                if(assetData.asset_class_path.asset_name == "Material"):
                    mat = assetData.get_asset()
                    if(mat.get_editor_property("two_sided") == True):
                    #materialAssetDataList.append(assetData)
                        materialObjectList.append(mat)

                elif (assetData.asset_class_path.asset_name == "MaterialInstance" or assetData.asset_class_path.asset_name == "MaterialInstanceConstant"):                
                    mat = assetData.get_asset()
                    baseOverrides = mat.get_editor_property("base_property_overrides")
                    if (baseOverrides.get_editor_property("override_two_sided") == True):
                    #materialAssetDataList.append(assetData)
                        materialObjectList.append(mat)

                    if slowTask.should_cancel():
                        break
                    slowTask.enter_progress_frame(1, asset)

    tagSystem = unreal.get_engine_subsystem(unreal.AssetTagsSubsystem)
    tagSystem.create_collection("TwoSided", share_type=unreal.CollectionShareType.LOCAL)
    #tagSystem.add_asset_datas_to_collection(unreal.Name("TwoSided"),materialAssetDataList)
    tagSystem.add_asset_ptrs_to_collection(unreal.Name("TwoSided"), materialObjectList)

def migrate_material_parameters():
    """
    Copies Scalar, Vector, and Texture parameter values from the first selected
    Material Instance to all other selected Material Instances.

    Usage:
    1. In the Content Browser, select the SOURCE Material Instance first.
    2. Ctrl+Click to select all DESTINATION Material Instances.
    3. Right-click on any selected asset and choose "Scripted Actions -> [Name of this script]".
    """
    editor_util = unreal.EditorUtilityLibrary()
    material_lib = unreal.MaterialEditingLibrary

    # Get the assets currently selected in the Content Browser
    selected_assets = editor_util.get_selected_assets()

    # --- Validation ---
    if len(selected_assets) < 2:
        unreal.log_error("Please select at least two Material Instances: one source and one or more destinations.")
        return

    # Ensure all selected assets are Material Instances
    material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstanceConstant)]
    if len(material_instances) != len(selected_assets):
        unreal.log_error("Aborted: All selected assets must be Material Instance Constants.")
        return

    # --- Identify Source and Destinations ---
    source_mi = material_instances[0]
    destination_mis = material_instances[1:]

    unreal.log(f"Source Material Instance: {source_mi.get_name()}")
    unreal.log(f"Found {len(destination_mis)} destination Material Instances.")

    # --- Migration Logic ---
    migrated_count = 0
    for dest_mi in destination_mis:
        # To ensure we are only copying to valid targets, we can check if they share the same parent.
        # This is a good safety check to prevent migrating parameters between unrelated materials.
        if material_lib.get_material_instance_parent(dest_mi) != material_lib.get_material_instance_parent(source_mi):
            unreal.log_warning(f"Skipping '{dest_mi.get_name()}': Parent material does not match source.")
            continue

        unreal.log(f"--- Migrating to: {dest_mi.get_name()} ---")

        # 1. Migrate Scalar Parameters
        scalar_values = material_lib.get_scalar_parameter_values(source_mi)
        for name, value in scalar_values.items():
            unreal.log(f"  - Setting Scalar '{name}' to {value}")
            material_lib.set_scalar_parameter_value(dest_mi, name, value)

        # 2. Migrate Vector Parameters
        vector_values = material_lib.get_vector_parameter_values(source_mi)
        for name, value in vector_values.items():
            unreal.log(f"  - Setting Vector '{name}' to {value}")
            material_lib.set_vector_parameter_value(dest_mi, name, value)

        # 3. Migrate Texture Parameters
        texture_values = material_lib.get_texture_parameter_values(source_mi)
        for name, value in texture_values.items():
            if value: # Ensure texture isn't None
                unreal.log(f"  - Setting Texture '{name}' to {value.get_name()}")
                material_lib.set_texture_parameter_value(dest_mi, name, value)

        # Mark the asset as dirty so the editor knows it has unsaved changes
        editor_util.save_asset(dest_mi.get_path_name(), only_if_is_dirty=False)
        migrated_count += 1

    unreal.log_warning(f"Migration complete. Successfully migrated parameters to {migrated_count} Material Instances. Remember to save your assets!")