import unreal
import os

# DetailPanelCustomization 최종 테스트

# 1. 초기화
unreal.ChameleonData.clear_detail_customization()
unreal.log("=" * 50)

# 2. JSON 경로
json_path = os.path.abspath(r"d:\Projects\Unreal\PerforceTest\PerforceTest\TA\TAPython\Python\PPPreset\PPPreset.json")
json_path = json_path.replace("\\", "/")
unreal.log(f"JSON: {json_path}")

# 3. StaticMeshComponent 등록
mesh_comp = unreal.StaticMeshComponent.static_class()
result = unreal.ChameleonData.add_detail_customization(mesh_comp, json_path)
unreal.log(f"등록 결과: {result}")

# 4. 확인
unreal.ChameleonData.log_all_saved_detail_customization()

unreal.log("=" * 50)
unreal.log("Floor_0을 선택하세요")
unreal.log("LogCreateWidget=True로 상세 로그 확인")
unreal.log("=" * 50)
