---
name: ta-python
description: A skill for developing Tech Art Python scripts and native Slate-based Chameleon UIs in Unreal Engine using the TAPython framework. Use this skill when writing or debugging Python tools, JSON UI layout files, or handling menu/hotkey configs within the MaidCat plugin.
---

# TA Python & Chameleon Development Playbook

This playbook establishes coding standards and guidelines for developing editor utilities and UI tools in Unreal Engine using **TAPython** and the **Chameleon** UI framework.

> [!NOTE]
> Several patterns documented here reflect the current local conventions (including quick/rough implementations) in the MaidCat codebase. Maintain consistency with existing code when modifying them, but consult the official TAPython API documentation to choose the best standards for new tool development.

---

## Instructions

### 1. UI Layout Conversion Rules (Slate C++ to JSON)
TAPython renders Unreal Slate UIs dynamically from JSON layout files. Follow these mapping rules strictly:

- **Slate Type Name**: Omit the C++ `SNew` prefix and use the Slate class name directly as the JSON key (e.g., `SButton`, `SVerticalBox`).
- **Aka (Widget Bindings)**: Map `SAssignNew(MyButton, SButton)` to `"SButton": { "Aka": "MyButton" }`. Use this `aka_name` in Python to query or modify the widget.
- **Single Child Container (Content)**: Widgets that hold exactly one child (e.g., `SBorder`, `SWindow`, `SDPIScaler`, `SBox`) use the `"Content": { ... }` key.
- **Multiple Children Container (Slots)**: Layout widgets that hold multiple children (e.g., `SVerticalBox`, `SHorizontalBox`, `SScrollBox`, `SSplitter`) use a `"Slots": [ { ... }, { ... } ]` array.
- **Grid Layout (SGridPanel)**: Slots inside an `SGridPanel` must specify their coordinates using `"Column_Row": [X, Y]`.
- **Styles and Brushes**: Map style references like `FEditorStyle::Get().GetBrush("BrushName")` to:
  ```json
  "BorderImage": {
    "Style": "FEditorStyle",
    "Brush": "ToolPanel.DarkGroupBorder"
  }
  ```
- **Vectors and Padding**: Specify Vector2D/4D values or margins as JSON arrays: `[X, Y]` or `[X, Y, Z, W]`.

### 2. Advanced Chameleon UI Features

#### 2.1 Self-Declaring Menus (MenuEntries)
- Declare the menu entry directly within the tool's JSON configuration to avoid modifying the global `MenuConfig.json`:
  ```json
  "MenuEntries": ["Tools/MaidCat/My Custom Tool"],
  "Icon": { "style": "ChameleonStyle", "name": "Picture" }
  ```
- The menu tree is generated automatically using forward slashes (`/`).

#### 2.2 Aliases
- Simplify JSON event actions by defining short aliases for long Python call paths:
  ```json
  "Aliases": {
    "$tool": "MyModule.MyClass.MyInstance(%JsonPath)"
  },
  "OnClick": "$tool.on_click()"
  ```

#### 2.3 Dynamic Slate Widgets (Runtime Instantiation)
Modify the Slate layout dynamically at runtime using the `ChameleonData` instance:
- **Set Content (Single Child)**: `self.data.set_content_from_json("ParentAka", json_string)` (applicable to SBox, SBorder, SButton, etc.)
- **Append Slot**: `self.data.append_slot_from_json("ParentAka", json_string)` (applicable to SVerticalBox, SHorizontalBox, SScrollBox, SGridPanel, etc.)
- **Insert Slot**: `self.data.insert_slot_from_json("ParentAka", slot_index, json_string)` (applicable to SVerticalBox, SHorizontalBox)
- **Remove Widget**: `self.data.remove_widget_at("ParentAka", slot_index)`

#### 2.4 Tab Context Menu (OnTabContextMenu)
- Hook context menus to the tool tab. Use this to bind a **Reload Tool** option to quickly reload both Python and JSON without restarting the editor:
  ```json
  "OnTabContextMenu": {
    "items": [
      {
        "name": "Reload Tool",
        "command": "unreal.ChameleonData.request_close(%tool_path); unreal.ChameleonData.launch_chameleon_tool(%tool_path)"
      }
    ]
  }
  ```

### 3. MaidCat Local Code Conventions
These patterns are observed in [Content/Python/ui/](file:///C:/Users/parkj/Documents/GitHub/MaidCat/Content/Python/ui). Follow them when maintaining existing scripts:

- **Hot-Reloading Python Modules**: 
  - Call `importlib.reload(module)` inside the `InitPyCmd` declaration to force-reload changes on every launch of the tool:
    ```json
    "InitPyCmd": "import ui.detail_ppv, importlib; importlib.reload(ui.detail_ppv); detail_ppv = ui.detail_ppv.PPDetailWidget(%JsonPath)"
    ```
- **unreal.Name Casting**: 
  - When accessing UI widgets via `aka_name` in Python, cast strings to `unreal.Name` explicitly:
    ```python
    INPUT_FIELD = unreal.Name("NameInput")
    ```
- **Modal Dialog Setup and Callbacks**:
  - Before launching a modal dialog (e.g., `NameDialog`, `OptionDialog`), assign callback references and message parameters directly to the class variables of the dialog (e.g., `NameDialog._message = message`, `_on_submit_callback = callback`), then call `unreal.ChameleonData.modal_window(json_path_str)`.
  - Use `unreal.ChameleonData.request_close_modal_window(self.json_path)` to close.
- **UniqueID Object Bindings**:
  - When sync-binding a Chameleon utility to a selected actor (e.g., in a detail panel custom widget), extract the actor ID using `unreal.PythonBPLib.get_unique_id(selected_actor)` and instantiate with: `unreal.PythonBPLib.get_chameleon_data(self.json_path, unique_id)`.

---

## Examples

### 1. Chameleon UI JSON Definition (`MyTool.json`)
```json
{
  "TabLabel": "My Advanced Tool",
  "InitTabSize": [300, 200],
  "MenuEntries": ["Tools/MaidCat/My Advanced Tool"],
  "Icon": { "style": "ChameleonStyle", "name": "Default" },
  "InitPyCmd": "import MyTool, importlib; importlib.reload(MyTool); my_tool_inst = MyTool.MyToolClass(%JsonPath)",
  "Aliases": {
    "$tool": "my_tool_inst"
  },
  "OnTabContextMenu": {
    "items": [
      {
        "name": "Reload This Tool",
        "command": "unreal.ChameleonData.request_close(%tool_path); unreal.ChameleonData.launch_chameleon_tool(%tool_path)"
      }
    ]
  },
  "Root": {
    "SVerticalBox": {
      "Aka": "MainLayout",
      "Slots": [
        {
          "SButton": {
            "Text": "Add Dynamic Row",
            "OnClick": "$tool.add_new_row()"
          }
        }
      ]
    }
  }
}
```

### 2. Singleton Python Controller with Dynamic Widgets (`MyTool.py`)
```python
# -*- coding: utf-8 -*-
import unreal
from Utilities.Utils import Singleton

class MyToolClass(metaclass=Singleton):
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = unreal.PythonBPLib.get_chameleon_data(self.json_path)
        self.row_count = 0

    def add_new_row(self):
        self.row_count += 1
        new_slot_json = f"""
        {{
            "STextBlock": {{
                "Text": "Dynamic Row #{self.row_count}",
                "Margin": [5, 2]
            }}
        }}
        """
        self.data.append_slot_from_json("MainLayout", new_slot_json)
```
