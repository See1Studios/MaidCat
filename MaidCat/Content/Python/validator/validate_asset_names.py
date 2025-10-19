# import unreal

# # This script uses a hybrid approach:
# # 1. An EditorValidatorBase class to define the validation logic and UI.
# # 2. Event listeners for legacy and Interchange imports to trigger the validation automatically.
# # This provides immediate feedback on import without requiring "Validate on Save".

# ASSET_PREFIX_MAP = {
#     "Blueprint": "BP_",
#     "Material": "M_",
#     "MaterialInstanceConstant": "MI_",
#     "Texture2D": "T_",
#     "StaticMesh": "SM_",
#     "SkeletalMesh": "SK_",
#     "NiagaraSystem": "NS_",
#     "AnimBlueprint": "ABP_",
#     "LevelSequence": "LS_",
#     "MediaPlayer": "MP_",
#     "MediaTexture": "MT_",
#     "SubstanceGraphInstance": "S_",
#     "SubstanceInstanceFactory": "SI_",
#     "SoundCue": "SC_",
#     "SoundWave": "SW_",
#     "WidgetBlueprint": "WBP_",
#     "BehaviorTree": "BT_",
#     "BlackboardData": "BB_",
#     "DataAsset": "DA_",
# }

# @unreal.uclass()
# class AssetNamingValidator(unreal.EditorValidatorBase):
#     """
#     This class defines the actual validation logic. The subsystem finds this automatically.
#     """
#     def can_validate_asset(self, asset):
#         if not asset:
#             return False
#         asset_class = str(asset.get_class().get_name())
#         return asset_class in ASSET_PREFIX_MAP

#     def validate_loaded_asset(self, asset, validation_context):
#         if not self.can_validate_asset(asset):
#             return unreal.DataValidationResult.NOT_APPLICABLE

#         asset_class = str(asset.get_class().get_name())
#         asset_name = str(asset.get_name())
#         prefix = ASSET_PREFIX_MAP[asset_class]

#         if asset_name.startswith(prefix):
#             self.asset_passes(asset)
#             return unreal.DataValidationResult.VALID
#         else:
#             error_message = f"Naming convention failed. Name should start with '{prefix}'."
#             fix = unreal.AssetValidationFix("Rename Asset", lambda: self.apply_rename_fix(asset, prefix))
#             self.asset_fails(asset, unreal.Text(error_message), fix)
#             return unreal.DataValidationResult.INVALID

#     def apply_rename_fix(self, asset, prefix):
#         old_name = str(asset.get_name())
#         base_name = old_name
#         for p in ASSET_PREFIX_MAP.values():
#             if base_name.startswith(p):
#                 base_name = base_name[len(p):]
#                 break
#         new_name = f"{prefix}{base_name}"
#         try:
#             unreal.EditorAssetLibrary.rename_asset(asset.get_path_name(), new_name)
#             self.asset_passes(asset, unreal.Text(f"Successfully renamed to {new_name}."))
#         except Exception as e:
#             self.asset_fails(asset, unreal.Text(f"Failed to rename asset: {e}"))

# # --- Event Handling to Trigger Validation Manually ---

# def trigger_validation_for_asset(asset_path):
#     """Programmatically runs the validation subsystem on a specific asset."""
#     if not asset_path:
#         return
#     asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
#     if not asset_data or not asset_data.is_valid():
#         return
    
#     validator_subsystem = unreal.get_editor_subsystem(unreal.EditorValidatorSubsystem)
#     validator_subsystem.validate_assets_with_message([asset_data])

# def on_asset_post_import(factory, asset):
#     """Called after an asset is imported via the legacy pipeline."""
#     if asset:
#         trigger_validation_for_asset(asset.get_path_name())

# def on_interchange_import_done(results_container):
#     """Called after an asset is imported via the modern Interchange pipeline."""
#     try:
#         for result in results_container.get_results():
#             if isinstance(result, unreal.InterchangeImportResultSuccess) and result.get_asset():
#                 trigger_validation_for_asset(result.get_asset().get_path_name())
#     except Exception as e:
#         print(f"VALIDATOR: Error in on_interchange_import_done: {e}", file=sys.stderr)

# # --- Registration Logic ---

# post_import_handle = None
# interchange_handle = None

# def register_event_listeners():
#     global post_import_handle, interchange_handle
#     unregister_event_listeners()
#     import_subsystem = unreal.get_editor_subsystem(unreal.ImportSubsystem)
#     post_import_handle = import_subsystem.on_asset_post_import.add_callable(on_asset_post_import)
#     interchange_manager = unreal.get_editor_subsystem(unreal.interc)
#     interchange_handle = interchange_manager.on_interchange_import_done_py.add_callable(on_interchange_import_done)
#     print("VALIDATOR: Import-triggered validation is active.")

# def unregister_event_listeners():
#     global post_import_handle, interchange_handle
#     if post_import_handle:
#         import_subsystem = unreal.get_editor_subsystem(unreal.ImportSubsystem)
#         if import_subsystem: import_subsystem.on_asset_post_import.remove(post_import_handle)
#         post_import_handle = None
#     if interchange_handle:
#         interchange_manager = unreal.get_editor_subsystem(unreal.InterchangeManager)
#         if interchange_manager: interchange_manager.on_interchange_import_done_py.remove(interchange_handle)
#         interchange_handle = None

# # --- Main Execution ---
# register_event_listeners()
# unreal.register_script_exit_callback(unregister_event_listeners)
# print("VALIDATOR: Asset Naming Validator with import trigger loaded.")