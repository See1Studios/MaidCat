import unreal
from Utilities.Utils import Singleton
from typing import Callable, Optional, ClassVar

MESSAGE_TEXT = unreal.Name("MessageText")
INPUT_FIELD = unreal.Name("NameInput")
	
class NameDialog(metaclass=Singleton):
	"""이름 입력 다이얼로그 클래스 (싱글톤)"""
	_on_submit_callback: ClassVar[Optional[Callable[[str], None]]] = None
	_on_cancel_callback: ClassVar[Optional[Callable[[], None]]] = None
	_message: ClassVar[str] = "이름을 입력하세요."
	_hint_text: ClassVar[str] = ""
	_submit_text: ClassVar[str] = "Submit"
	_cancel_text: ClassVar[str] = "Cancel"
	
	def __init__(self, json_path: str):
		self.json_path = json_path
		self.data: unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(self.json_path)
		
	def init(self) -> None:
		"""초기화 처리"""
		self.data.set_text(INPUT_FIELD, "")  # type: ignore
		self.data.set_text(MESSAGE_TEXT, NameDialog._message)  # type: ignore

	def submit(self) -> None:
		"""제출 버튼 처리"""
		input_text = self.data.get_text(INPUT_FIELD) or ""
		if NameDialog._on_submit_callback:  # type: ignore
			NameDialog._on_submit_callback(input_text.strip())  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)
			
	def cancel(self) -> None:
		"""취소 버튼 처리"""
		if NameDialog._on_cancel_callback:  # type: ignore
			NameDialog._on_cancel_callback()  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)
		