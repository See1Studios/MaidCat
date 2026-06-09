import unreal
from Utilities.Utils import Singleton
from typing import Callable, Optional, ClassVar

MESSAGE_TEXT = unreal.Name("MessageText")
COMBO_BOX = unreal.Name("ComboBoxInput")
LABEL_TEXT = unreal.Name("LabelText")
BTN_SUBMIT = unreal.Name("BtnSubmit")
BTN_CANCEL = unreal.Name("BtnCancel")

class OptionDialog(metaclass=Singleton):
	"""옵션 선택 다이얼로그 클래스 (싱글톤)"""
	_on_selection_changed: ClassVar[Optional[Callable[[str], None]]] = None
	_on_submit_callback: ClassVar[Optional[Callable[[str], None]]] = None
	_on_cancel_callback: ClassVar[Optional[Callable[[], None]]] = None
	_items: ClassVar[list[str]] = []
	_message: ClassVar[str] = "Enter Option"
	_label: ClassVar[str] = "Option :"
	_submit_text: ClassVar[str] = "Submit"
	_cancel_text: ClassVar[str] = "Cancel"


	def __init__(self, json_path: str):
		self.json_path = json_path
		self.data: unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(self.json_path)

	def init(self) -> None:
		"""초기화 처리"""
		self.data.set_text(MESSAGE_TEXT, OptionDialog._message)  # type: ignore
		self.data.set_text(LABEL_TEXT, OptionDialog._label)  # type: ignore
		self.data.set_text(BTN_SUBMIT, OptionDialog._submit_text)  # type: ignore
		self.data.set_text(BTN_CANCEL, OptionDialog._cancel_text)  # type: ignore
		if(len(OptionDialog._items) > 0):
			self.data.set_combo_box_items(COMBO_BOX, OptionDialog._items)  # type: ignore
			self.data.set_combo_box_selected_item(COMBO_BOX, 0)  # type: ignore

	def submit(self) -> None:
		"""제출 버튼 처리"""
		selected_item = self.data.get_combo_box_selected_item(COMBO_BOX) or ""
		if OptionDialog._on_submit_callback:  # type: ignore
			OptionDialog._on_submit_callback(selected_item.strip())  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)
			
	def cancel(self) -> None:
		"""취소 버튼 처리"""
		if OptionDialog._on_cancel_callback:  # type: ignore
			OptionDialog._on_cancel_callback()  # type: ignore
		unreal.ChameleonData.request_close_modal_window(self.json_path)

	def selection_changed(self, selected_item: str) -> None:
		"""콤보박스 선택 변경 처리"""
		# self.data.set_text(OptionDialog.message_text, selected_item)  # type: ignore
		if OptionDialog._on_selection_changed:  # type: ignore
			OptionDialog._on_selection_changed(selected_item)  # type: ignore