import unreal
from Utilities.Utils import Singleton

class PPDetailWidget(metaclass=Singleton):
    """Post Process Volume 디테일 패널용 위젯"""
    
    def __init__(self, jsonPath):
        """
        Args:
            json_path: JSON 파일 경로 (%JsonPath로 전달됨)
        """
        self.jsonPath = jsonPath
        selection = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_selected_level_actors()[0]
        unique_id = unreal.PythonBPLib.get_unique_id(selection)
        self.data = unreal.PythonBPLib.get_chameleon_data(self.jsonPath,unique_id)
        self.data.set_combo_box_items('CombBoxA', ['1', '3', '5'])
        unreal.log(f"✅ PPDetailWidget 초기화: {self.jsonPath}")
    
    def on_save_clicked(self):
        """Save Preset 버튼 클릭"""
        unreal.log("✅ Save Preset 클릭됨 (디테일 패널)")
        # TODO: 실제 저장 로직
    
    def on_load_clicked(self):
        """Load Preset 버튼 클릭"""
        unreal.log("✅ Load Preset 클릭됨 (디테일 패널)")
        # TODO: 실제 로드 로직
