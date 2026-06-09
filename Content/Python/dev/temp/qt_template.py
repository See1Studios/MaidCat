"""
Unreal Engine PySide6 UI Template

Requirements:
- PySide6 (install using install_package.py)

Usage:
- Option 1: Use .ui file from Qt Designer
- Option 2: Create UI programmatically (see example below)

Note: UE 5.5 uses Python 3.11, which requires PySide6 (not PySide2)
"""

import unreal
import sys
from pathlib import Path
from functools import partial
from PySide6 import QtCore, QtWidgets, QtUiTools


class UnrealUITemplate(QtWidgets.QWidget):
    """
    Create a default tool window.
    
    This example shows both methods:
    1. Loading from .ui file (commented out)
    2. Creating UI programmatically (default)
    """
    # Store ref to window to prevent garbage collection
    window = None
    
    def __init__(self, parent=None):
        """
        Import UI and connect components
        """
        super(UnrealUITemplate, self).__init__(parent)
        
        # Method 1: Load from .ui file (uncomment if you have a .ui file)
        # self.load_ui_from_file()
        
        # Method 2: Create UI programmatically (default)
        self.create_ui_programmatically()
    
    def load_ui_from_file(self):
        """
        Load UI from Qt Designer .ui file
        """
        # Path to your .ui file
        ui_file_path = Path(__file__).parent / "ui" / "mainWidget.ui"
        
        if not ui_file_path.exists():
            unreal.log_warning(f"UI file not found: {ui_file_path}")
            unreal.log_warning("Falling back to programmatic UI creation")
            self.create_ui_programmatically()
            return
        
        # Load the UI file
        ui_file = QtCore.QFile(str(ui_file_path))
        ui_file.open(QtCore.QFile.ReadOnly)
        
        loader = QtUiTools.QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()
        
        # Attach the widget to this instance
        self.widget.setParent(self)
        
        # Find interactive elements
        self.btn_close = self.widget.findChild(QtWidgets.QPushButton, 'btn_close')
        
        # Connect signals
        if self.btn_close:
            self.btn_close.clicked.connect(self.close_window)
    
    def create_ui_programmatically(self):
        """
        Create UI using Python code (no .ui file needed)
        """
        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Title label
        title_label = QtWidgets.QLabel("Unreal Engine Tool")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Add some example content
        content_group = QtWidgets.QGroupBox("Tool Options")
        content_layout = QtWidgets.QVBoxLayout()
        
        # Example checkbox
        self.chk_option1 = QtWidgets.QCheckBox("Enable Feature 1")
        self.chk_option1.setChecked(True)
        content_layout.addWidget(self.chk_option1)
        
        # Example input
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(QtWidgets.QLabel("Input Value:"))
        self.txt_input = QtWidgets.QLineEdit()
        self.txt_input.setPlaceholderText("Enter value here...")
        input_layout.addWidget(self.txt_input)
        content_layout.addLayout(input_layout)
        
        # Example button
        self.btn_execute = QtWidgets.QPushButton("Execute")
        self.btn_execute.clicked.connect(self.on_execute)
        content_layout.addWidget(self.btn_execute)
        
        content_group.setLayout(content_layout)
        main_layout.addWidget(content_group)
        
        # Spacer
        main_layout.addStretch()
        
        # Bottom buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.close_window)
        button_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(button_layout)
        
        # Set window properties
        self.setMinimumSize(400, 300)
    
    def on_execute(self):
        """
        Example button handler
        """
        option_enabled = self.chk_option1.isChecked()
        input_value = self.txt_input.text()
        
        unreal.log(f"Execute clicked! Option: {option_enabled}, Input: {input_value}")
        
        # Show message box
        QtWidgets.QMessageBox.information(
            self,
            "Execute",
            f"Feature 1: {option_enabled}\nInput: {input_value}"
        )
    
    def resizeEvent(self, event):
        """
        Called on automatically generated resize event
        """
        # Only needed if using .ui file with separate widget
        if hasattr(self, 'widget') and self.widget:
            self.widget.resize(self.width(), self.height())
        super().resizeEvent(event)
    
    def close_window(self):
        """
        Close the window.
        """
        self.close()
        self.deleteLater()
 
def open_window():
    """
    Create and show tool window.
    
    This function:
    1. Creates or reuses QApplication
    2. Closes any existing instances of this tool
    3. Creates and shows the window
    4. Parents it to Unreal's Slate UI
    """
    # Get or create QApplication
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # Close any existing instances of this tool
    for win in QtWidgets.QApplication.allWindows():
        if win.objectName() == 'UnrealToolWindow':
            win.close()
            win.deleteLater()
    
    # Create and show new window
    UnrealUITemplate.window = UnrealUITemplate()
    UnrealUITemplate.window.setObjectName('UnrealToolWindow')
    UnrealUITemplate.window.setWindowTitle('Unreal Tool Template')
    UnrealUITemplate.window.show()
    
    # Parent to Unreal's Slate UI (keeps window on top)
    unreal.parent_external_window_to_slate(UnrealUITemplate.window.winId())
    
    unreal.log("Unreal Tool Window opened successfully")
    
    return UnrealUITemplate.window


# Main entry point
if __name__ == "__main__":
    open_window()
