import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
def post_save_asset_check(asset_data):
    asset_path = asset_data.asset_name.to_string() # 에셋의 전체 경로 가져오기
    asset_name = unreal.Paths.get_base_filename(asset_path)
    asset_class = asset_data.asset_class.to_string() # 에셋의 클래스 이름 (예: "Blueprint", "Material")

    unreal.log(f"에셋이 저장되었습니다 (Post-Save): {asset_name} (Class: {asset_class})")

    # 여기에 유효성 검사 로직을 구현합니다.
    # 예시: 저장된 블루프린트 이름이 "BP_"로 시작하지 않으면 경고
    if asset_class == "Blueprint" and not asset_name.startswith("BP_"):
        unreal.log_warning(f"경고: 블루프린트 이름 '{asset_name}'은 'BP_'로 시작하는 것이 권장됩니다.")
        unreal.EditorDialog.show_message("저장 경고",
                                         f"블루프린트 이름 '{asset_name}'은 'BP_'로 시작해야 합니다.",
                                         unreal.AppMsgType.OK,
                                         unreal.AppReturnType.NONE)
    # 추가적인 검사 로직...

def setup_asset_post_save_validation():
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_registry.on_asset_saved.add_callable(post_save_asset_check)
    unreal.log("에셋 저장 후 유효성 검사 스크립트가 로드되었습니다.")