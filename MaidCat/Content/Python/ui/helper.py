import unreal
import ui.name_window
from pathlib import Path

class NameDialog:
	name: str = ""
	JSON_FILENAME = "name_window.json"
	
	@staticmethod
	def on_submit(text: str) -> None:
		NameDialog.name = text

	@staticmethod
	def on_cancel() -> None:
		NameDialog.name = ""
	
	@staticmethod
	def open_dialog() -> str:
		"""이름 입력 다이얼로그를 열고 결과를 반환"""
		NameDialog.name = ""
		
		# JSON 파일 경로 찾기
		current_dir = Path(__file__).parent
		json_path = current_dir / NameDialog.JSON_FILENAME
		
		if not json_path.exists():
			unreal.log_warning(f"JSON file not found: {json_path}")
			return ""
		
		try:
			# 다이얼로그 콜백 설정
			ui.name_window.Dialog._on_submit_callback = NameDialog.on_submit
			ui.name_window.Dialog._on_cancel_callback = NameDialog.on_cancel
			
			# 다이얼로그 열기
			unreal.ChameleonData.modal_window(str(json_path).replace("\\", "/"))
			
		except Exception as e:
			unreal.log_error(f"Failed to open dialog: {e}")
			return ""
		
		return NameDialog.name
		