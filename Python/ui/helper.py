import unreal
import ui.name_window
import ui.option_window
from pathlib import Path

class NameDialog:
	JSON_FILENAME = "name_window.json"
	name: str = ""
	
	@staticmethod
	def on_submit(text: str) -> None:
		NameDialog.name = text

	@staticmethod
	def on_cancel() -> None:
		NameDialog.name = ""
	
	@staticmethod
	def open_dialog(
		message: str = "이름을 입력하세요.",
		title_text: str = "",
	) -> str:
		"""이름 입력 다이얼로그를 열고 결과를 반환"""
		NameDialog.name = ""
		
		# JSON 파일 경로 찾기
		current_dir = Path(__file__).parent
		json_path = current_dir / NameDialog.JSON_FILENAME
		if not json_path.exists():
			unreal.log_warning(f"JSON file not found: {json_path}")
			return ""		

		# 다이얼로그 설정
		ui.name_window.NameDialog._message = message
		ui.name_window.NameDialog._on_submit_callback = NameDialog.on_submit
		ui.name_window.NameDialog._on_cancel_callback = NameDialog.on_cancel

		unreal.ChameleonData.modal_window(str(json_path).replace("\\", "/"))
		return NameDialog.name
	
class OptionDialog:
	JSON_FILENAME = "option_window.json"
	selected_option: str = ""
	option_list: list[str] = []

	@staticmethod
	def on_submit(text: str) -> None:
		OptionDialog.selected_option = text

	@staticmethod
	def on_cancel() -> None:
		OptionDialog.selected_option = ""
	
	@staticmethod
	def open_dialog(
		options: list[str],
		message: str = "옵션을 선택하세요.",
		label: str = "Option :",
		submit_text: str = "Submit",
		cancel_text: str = "Cancel",
	) -> str:

		OptionDialog.selected_option = ""
		# JSON 파일 경로 찾기
		current_dir = Path(__file__).parent
		json_path = current_dir / OptionDialog.JSON_FILENAME
		if not json_path.exists():
			unreal.log_warning(f"JSON file not found: {json_path}")
			return ""		

		# 다이얼로그 설정
		ui.option_window.OptionDialog._message = message
		ui.option_window.OptionDialog._label = label
		ui.option_window.OptionDialog._submit_text = submit_text
		ui.option_window.OptionDialog._cancel_text = cancel_text
		ui.option_window.OptionDialog._items = options
		ui.option_window.OptionDialog._on_submit_callback = OptionDialog.on_submit
		ui.option_window.OptionDialog._on_cancel_callback = OptionDialog.on_cancel
		
		# 다이얼로그 열기
		unreal.ChameleonData.modal_window(str(json_path).replace("\\", "/"))

		return OptionDialog.selected_option	

def open_name_dialog_test():
	result = NameDialog.open_dialog()
	unreal.log(f"User input: {result}")	
	
def open_option_dialog_test():
	result = OptionDialog.open_dialog(["Option 1", "Option 2", "Option 3"])
	unreal.log(f"User input: {result}")

if __name__ == "__main__":
	open_option_dialog_test()