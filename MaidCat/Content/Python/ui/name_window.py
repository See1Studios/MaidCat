import unreal
from Utilities.Utils import Singleton
from typing import Callable, Optional, ClassVar

class Dialog(metaclass=Singleton):
	"""이름 입력 다이얼로그 클래스 (싱글톤)"""
	_on_submit_callback: ClassVar[Optional[Callable[[str], None]]] = None
	_on_cancel_callback: ClassVar[Optional[Callable[[], None]]] = None
	
	input_field = unreal.Name("NameInput")
	def __init__(self, json_path: str):
		self.json_path = json_path
		self.data: unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(self.json_path)
	
	def reset(self) -> None:
		"""입력 필드 초기화"""
		self.data.set_text(Dialog.input_field, "")
	
	def open_with_callbacks(self, on_submit: Callable[[str], None], on_cancel: Optional[Callable[[], None]] = None) -> None:
		"""콜백 함수를 설정하고 다이얼로그 열기"""
		Dialog._on_submit_callback = on_submit  # type: ignore
		Dialog._on_cancel_callback = on_cancel  # type: ignore
		self.reset()
		unreal.ChameleonData.modal_window(self.json_path)
		
	def get_input_text(self, field_name: str) -> str:
		"""지정된 필드의 텍스트 가져오기"""
		return self.data.get_text(Dialog.input_field) or ""
	
	def submit(self) -> None:
		"""제출 버튼 처리"""
		input_text = self.get_input_text(Dialog.input_field)
		if Dialog._on_submit_callback:  # type: ignore
			Dialog._on_submit_callback(input_text.strip())  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)
			
	def cancel(self) -> None:
		"""취소 버튼 처리"""
		if Dialog._on_cancel_callback:  # type: ignore
			Dialog._on_cancel_callback()  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)
		