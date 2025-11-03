import unreal
from Utilities.Utils import Singleton
from typing import Callable, Optional

class Dialog(metaclass=Singleton):
	_on_submit_callback:Optional[Callable[[str],None]] = None
	_on_cancel_callback:Optional[Callable[[],None]] = None
	
	def __init__(self, json_path:str):
		self.json_path = json_path
		self.data:unreal.ChameleonData = unreal.PythonBPLib.get_chameleon_data(self.json_path)
	
	def reset(self):
		self.data.set_text("NameInput","")
	
	def open_with_callbacks(self, on_submit, on_cancel):
		self.__class__._on_submit_callback = on_submit
		self.__class__._on_cancel_callback = on_cancel
		self.reset()
		unreal.ChameleonData.modal_window(self.json_path)
		
	def get_input_text(self, field_name:str) -> str :
		return self.data.get_text(field_name) or ""
	
	def submit(self):
		input_text = self.get_input_text("NameInput")
		if self.__class__._on_submit_callback:
			self.__class__._on_submit_callback(input_text.strip())
		unreal.ChameleonData.request_close_modal_window(self.json_path)
			
	def cancel(self):
		if self.__class__._on_cancel_callback:
			self.__class__._on_cancel_callback()
		unreal.ChameleonData.request_close_modal_window(self.json_path)
		