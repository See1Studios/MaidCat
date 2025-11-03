import unreal
import ui.name_window
import os

class NameDialog:
	name:str = ""
	
	@staticmethod
	def on_submit(text: str):
		NameDialog.name = text

	@staticmethod
	def on_cancel():
		NameDialog.name = ""
	
	@staticmethod
	def _get_json_path():
		"""
		현재 실행 컨텍스트가 프로젝트인지 플러그인인지 판단하여 적절한 경로를 반환
		"""
		# 현재 파일의 디렉토리에서 JSON 파일 경로 생성
		current_dir = os.path.dirname(os.path.abspath(__file__))
		json_file_path = os.path.join(current_dir, "name_window.json")
		
		# 디버깅 정보 출력
		print(f"PythonTA: Current directory: {current_dir}")
		print(f"PythonTA: Looking for JSON at: {json_file_path}")
		print(f"PythonTA: JSON file exists: {os.path.exists(json_file_path)}")
		
		# JSON 파일이 존재하는지 확인
		if os.path.exists(json_file_path):
			# 절대 경로를 언리얼 엔진 형식으로 변환 (백슬래시를 슬래시로)
			final_path = json_file_path.replace("\\", "/")
			print(f"PythonTA: Using JSON path: {final_path}")
			return final_path
		else:
			# 파일이 없으면 기본 상대 경로 반환
			print("PythonTA: JSON file not found, using relative path")
			return "./name_window.json"
	
	@staticmethod
	def open_dialog():
		NameDialog.name = ""
		ui.name_window.Dialog._on_submit_callback = NameDialog.on_submit
		ui.name_window.Dialog._on_cancel_callback = NameDialog.on_cancel
		
		json_path = NameDialog._get_json_path()
		unreal.ChameleonData.modal_window(json_path)
		
		return NameDialog.name
		