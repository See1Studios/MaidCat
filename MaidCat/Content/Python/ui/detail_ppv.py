import unreal
from Utilities.Utils import Singleton
import ui.helper
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
        list_items = ['None', 'Pretty Preset', 'Ugly Preset']
        self.data.set_combo_box_items('CombBoxA', list_items)
        self.data.set_combo_box_items('CombBoxB', list_items)
        unreal.log(f"✅ PPDetailWidget 초기화: {self.jsonPath}")

    def on_load_clicked(self, item_name):
        """Load Preset 버튼 클릭"""
        if( item_name != "None" ):
             unreal.log(f"✅ {item_name} 클릭됨 (Load)")
        # TODO: 실제 로드 로직
    
    def on_overwrite_clicked(self, item_name):
        """Save Preset 버튼 클릭"""
        if( item_name != "None" ):
             unreal.log(f"✅ {item_name} 클릭됨 (Overwrite)")
        # TODO: 실제 저장 로직
        
    def on_new_clicked(self):
        """Save Preset 버튼 클릭"""
        unreal.log("✅ New 클릭됨 (New Preset)")

        name = ui.helper.NameDialog.open_dialog()
        print(name)
    
        # TODO: 실제 저장 로직
    