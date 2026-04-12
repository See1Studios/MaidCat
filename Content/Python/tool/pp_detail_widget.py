"""Post Process 디테일 패널 커스터마이징 위젯"""
import unreal


class PPDetailWidget:
    """Post Process Volume 디테일 패널용 위젯"""
    
    def __init__(self, json_path):
        """
        Args:
            json_path: JSON 파일 경로 (%JsonPath로 전달됨)
        """
        self.json_path = json_path
        unreal.log(f"✅ PPDetailWidget 초기화: {json_path}")
    
    def on_save_clicked(self):
        """Save Preset 버튼 클릭"""
        unreal.log("✅ Save Preset 클릭됨 (디테일 패널)")
        # TODO: 실제 저장 로직
    
    def on_load_clicked(self):
        """Load Preset 버튼 클릭"""
        unreal.log("✅ Load Preset 클릭됨 (디테일 패널)")
        # TODO: 실제 로드 로직
