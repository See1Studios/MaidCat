import unreal

ASSET_PREFIX_MAP = {
    "Blueprint": "BP_",
    "Material": "M_",
    "MaterialInstanceConstant": "MI_",
    "Texture2D": "T_",
    "StaticMesh": "SM_",
    "SkeletalMesh": "SK_",
    "NiagaraSystem": "NS_",
    "AnimBlueprint": "ABP_",
    "LevelSequence": "LS_",
    "SoundCue": "SC_",
    "SoundWave": "SW_",
    "WidgetBlueprint": "WBP_",
    "BehaviorTree": "BT_",
    "BlackboardData": "BB_",
    "DataAsset": "DA_",
}

@unreal.uclass()
class AssetNamingValidator(unreal.EditorValidatorBase):
    

     
    @unreal.ufunction(override=True)
    def k2_can_validate(self, usecase: unreal.DataValidationUsecase):
        return usecase == unreal.DataValidationUsecase.SAVE

    @unreal.ufunction(override=True)
    def k2_can_validate_asset(self, asset):
        return isinstance(asset, unreal.Object)

    @unreal.ufunction(override=True)
    def k2_validate_loaded_asset(self, asset):
        asset_class = str(asset.get_class().get_name())
        asset_name = str(asset.get_name())
        expected_prefix = ASSET_PREFIX_MAP[asset_class]

        if asset_name.startswith(expected_prefix):
            self.asset_passes(asset)
            return unreal.DataValidationResult.VALID
        else:
            error_message = f"Asset naming convention failed. '{asset_name}' should start with '{expected_prefix}'"
            self.asset_fails(asset, unreal.Text(error_message))
            return unreal.DataValidationResult.INVALID

    def asset_fails(self, asset: unreal.Object, message: unreal.Text) -> None:
        return super().asset_fails(asset, message)

    def asset_passes(self, asset: unreal.Object) -> None:
        return super().asset_passes(asset)

    def asset_warning(self, asset: unreal.Object, message: unreal.Text) -> None:
        return super().asset_warning(asset, message)

# Validator 등록
def register_validator():
    validator_subsystem = unreal.get_editor_subsystem(unreal.EditorValidatorSubsystem)
    if validator_subsystem:
        validator = AssetNamingValidator()
        validator_subsystem.add_validator(validator)
        unreal.log("Asset Naming Validator registered successfully")

if __name__ == "__main__":
    register_validator()