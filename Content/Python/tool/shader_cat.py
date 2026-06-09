import unreal
import ue

def launch(material):
    """셰이더캣 실행"""
    if not material:
        unreal.log_warning("⚠️ 머티리얼이 선택되지 않았습니다.")
        return
    hlsl_data = unreal.PythonMaterialLib.get_hlsl_code(material)
    unreal.log(material.get_name())
    unreal.log(hlsl_data)

if __name__ == "__main__":
    launch(ue.util_lib.get_selected_assets_of_class(unreal.Material)[0])