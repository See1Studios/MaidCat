import unreal
import os
import configparser
from pathlib import Path
import json


class TAPythonConfigEditor:
    """TAPython config.ini 파일을 편집하는 유틸리티"""
    
    def __init__(self):
        self.project_dir = Path(unreal.Paths.project_dir())
        self.config_path = self.project_dir / "TA" / "TAPython" / "Config" / "config.ini"
        self.config = configparser.ConfigParser()
        self.ui_data = None  # Chameleon UI 데이터
        
    def find_config_file(self):
        """config.ini 파일을 찾습니다"""
        if self.config_path.exists():
            unreal.log(f"✅ Config 파일 발견: {self.config_path}")
            return True
        else:
            unreal.log_error(f"❌ Config 파일 없음: {self.config_path}")
            return False
    
    def load_config(self):
        """config.ini 파일을 로드합니다"""
        if not self.find_config_file():
            # Config 파일이 없으면 기본값으로 생성
            self.create_default_config()
            
        try:
            self.config.read(self.config_path, encoding='utf-8')
            unreal.log(f"📖 Config 파일 로드 완료")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Config 로드 실패: {e}")
            return False
    
    def save_config(self):
        """config.ini 파일을 저장합니다"""
        try:
            # 디렉토리가 없으면 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
            unreal.log(f"💾 Config 파일 저장 완료: {self.config_path}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Config 저장 실패: {e}")
            return False
    
    def create_default_config(self):
        """기본 config.ini 파일을 생성합니다"""
        self.config['General'] = {
            'debug': 'false',
            'log_level': 'info',
            'version': '1.0.0'
        }
        self.config['Paths'] = {
            'python_path': 'Content/Python',
            'scripts_path': 'Content/Python/Scripts'
        }
        self.config['Editor'] = {
            'auto_reload': 'true',
            'show_tooltips': 'true',
            'theme': 'default'
        }
        self.save_config()
    
    def get_value(self, section, key, default=None):
        """특정 값을 가져옵니다"""
        return self.config.get(section, key, fallback=default)
    
    def set_value(self, section, key, value):
        """값을 설정합니다"""
        if section not in self.config:
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        unreal.log(f"🔧 설정 변경: [{section}] {key} = {value}")


class TAPythonConfigGUI:
    """TAPython Config GUI Editor using Chameleon"""
    
    def __init__(self, json_path):
        self.json_path = json_path
        self.data = unreal.PythonBPLib.get_chameleon_data(self.json_path)
        self.config_editor = TAPythonConfigEditor()
        
        # UI 컨트롤 ID들
        self.ui_debug_checkbox = "debug_checkbox"
        self.ui_log_level_combo = "log_level_combo"
        self.ui_version_text = "version_text"
        self.ui_python_path_text = "python_path_text"
        self.ui_scripts_path_text = "scripts_path_text"
        self.ui_auto_reload_checkbox = "auto_reload_checkbox"
        self.ui_show_tooltips_checkbox = "show_tooltips_checkbox"
        self.ui_theme_combo = "theme_combo"
        self.ui_config_display = "config_display"
        
        # Config 로드 및 UI 초기화
        self.load_and_update_ui()
        
    def load_and_update_ui(self):
        """Config를 로드하고 UI를 업데이트합니다"""
        if self.config_editor.load_config():
            self.update_ui_from_config()
        
    def update_ui_from_config(self):
        """Config 값을 UI에 반영합니다"""
        # General 섹션
        debug = self.config_editor.get_value('General', 'debug', 'false') == 'true'
        self.data.set_is_checked(self.ui_debug_checkbox, debug)
        
        log_level = self.config_editor.get_value('General', 'log_level', 'info')
        self.data.set_combo_box_selected_item(self.ui_log_level_combo, log_level)
        
        version = self.config_editor.get_value('General', 'version', '1.0.0')
        self.data.set_text(self.ui_version_text, version)
        
        # Paths 섹션
        python_path = self.config_editor.get_value('Paths', 'python_path', 'Content/Python')
        self.data.set_text(self.ui_python_path_text, python_path)
        
        scripts_path = self.config_editor.get_value('Paths', 'scripts_path', 'Content/Python/Scripts')
        self.data.set_text(self.ui_scripts_path_text, scripts_path)
        
        # Editor 섹션
        auto_reload = self.config_editor.get_value('Editor', 'auto_reload', 'true') == 'true'
        self.data.set_is_checked(self.ui_auto_reload_checkbox, auto_reload)
        
        show_tooltips = self.config_editor.get_value('Editor', 'show_tooltips', 'true') == 'true'
        self.data.set_is_checked(self.ui_show_tooltips_checkbox, show_tooltips)
        
        theme = self.config_editor.get_value('Editor', 'theme', 'default')
        self.data.set_combo_box_selected_item(self.ui_theme_combo, theme)
        
        # Config 전체 내용 표시
        self.update_config_display()
    
    def update_config_display(self):
        """Config 내용을 텍스트로 표시합니다"""
        config_text = ""
        for section_name in self.config_editor.config.sections():
            config_text += f"[{section_name}]\\n"
            for key, value in self.config_editor.config[section_name].items():
                config_text += f"{key} = {value}\\n"
            config_text += "\\n"
        
        self.data.set_text(self.ui_config_display, config_text)
    
    def save_config(self):
        """현재 UI 설정을 Config에 저장합니다"""
        try:
            # UI에서 값 읽기 및 Config에 설정
            # General 섹션
            debug = self.data.get_is_checked(self.ui_debug_checkbox)
            self.config_editor.set_value('General', 'debug', 'true' if debug else 'false')
            
            log_level = self.data.get_combo_box_selected_item(self.ui_log_level_combo)
            self.config_editor.set_value('General', 'log_level', log_level)
            
            version = self.data.get_text(self.ui_version_text)
            self.config_editor.set_value('General', 'version', version)
            
            # Paths 섹션
            python_path = self.data.get_text(self.ui_python_path_text)
            self.config_editor.set_value('Paths', 'python_path', python_path)
            
            scripts_path = self.data.get_text(self.ui_scripts_path_text)
            self.config_editor.set_value('Paths', 'scripts_path', scripts_path)
            
            # Editor 섹션
            auto_reload = self.data.get_is_checked(self.ui_auto_reload_checkbox)
            self.config_editor.set_value('Editor', 'auto_reload', 'true' if auto_reload else 'false')
            
            show_tooltips = self.data.get_is_checked(self.ui_show_tooltips_checkbox)
            self.config_editor.set_value('Editor', 'show_tooltips', 'true' if show_tooltips else 'false')
            
            theme = self.data.get_combo_box_selected_item(self.ui_theme_combo)
            self.config_editor.set_value('Editor', 'theme', theme)
            
            # 저장
            if self.config_editor.save_config():
                unreal.PythonBPLib.notification("✅ Config 저장 완료!", info_level=0)
                self.update_config_display()
            else:
                unreal.PythonBPLib.notification("❌ Config 저장 실패!", info_level=2)
                
        except Exception as e:
            unreal.log_error(f"Config 저장 중 오류: {e}")
            unreal.PythonBPLib.notification(f"❌ 오류: {e}", info_level=2)
    
    def reset_to_defaults(self):
        """기본값으로 리셋"""
        self.config_editor.create_default_config()
        self.config_editor.load_config()
        self.update_ui_from_config()
        unreal.PythonBPLib.notification("🔄 기본값으로 리셋됨", info_level=0)
    
    def reload_config(self):
        """Config 파일 다시 로드"""
        self.load_and_update_ui()
        unreal.PythonBPLib.notification("📖 Config 다시 로드됨", info_level=0)
    
    def on_value_changed(self):
        """값이 변경될 때 호출 (실시간 미리보기)"""
        self.update_config_display()


def create_config_gui_json():
    """Config GUI용 JSON 파일을 생성합니다"""
    gui_json = {
        "TabLabel": "TAPython Config Editor",
        "InitTabSize": [800, 600],
        "InitTabPosition": [100, 100],
        "InitPyCmd": "import edit_config, importlib; importlib.reload(edit_config); config_gui = edit_config.TAPythonConfigGUI(%JsonPath);",
        "Root": {
            "SBorder": {
                "BorderImage": {
                    "Style": "FCoreStyle",
                    "Brush": "ToolPanel.GroupBorder"
                },
                "Content": {
                    "SScrollBox": {
                        "Aka": "ScrollBox",
                        "Slots": [
                            {
                                "Padding": 10,
                                "SVerticalBox": {
                                    "Slots": [
                                        # 헤더
                                        {
                                            "AutoHeight": True,
                                            "Padding": [0, 0, 0, 10],
                                            "STextBlock": {
                                                "Text": "TAPython Configuration Editor",
                                                "TextStyle": {
                                                    "Style": "FEditorStyle",
                                                    "StyleName": "LargeText"
                                                },
                                                "Justification": "Center"
                                            }
                                        },
                                        
                                        # General 섹션
                                        {
                                            "AutoHeight": True,
                                            "SExpandableArea": {
                                                "InitiallyCollapsed": False,
                                                "HeaderContent": {
                                                    "STextBlock": {
                                                        "Text": "📋 General Settings",
                                                        "Font": {
                                                            "Style": "FCoreStyle",
                                                            "StyleName": "DefaultFont.Bold.12"
                                                        }
                                                    }
                                                },
                                                "BodyContent": {
                                                    "SGridPanel": {
                                                        "FillColumn": [[0, 0.3], [1, 0.7]],
                                                        "Slots": [
                                                            {
                                                                "Column_Row": [0, 0],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Debug Mode:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 0],
                                                                "Padding": 5,
                                                                "SCheckBox": {
                                                                    "Aka": "debug_checkbox",
                                                                    "Content": {"STextBlock": {"Text": "Enable Debug"}},
                                                                    "OnCheckStateChanged": "config_gui.on_value_changed()"
                                                                }
                                                            },
                                                            {
                                                                "Column_Row": [0, 1],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Log Level:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 1],
                                                                "Padding": 5,
                                                                "SComboBox": {
                                                                    "Aka": "log_level_combo",
                                                                    "OptionsSource": ["debug", "info", "warning", "error"],
                                                                    "OnSelectionChanged": "config_gui.on_value_changed()"
                                                                }
                                                            },
                                                            {
                                                                "Column_Row": [0, 2],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Version:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 2],
                                                                "Padding": 5,
                                                                "SEditableTextBox": {
                                                                    "Aka": "version_text",
                                                                    "Text": "1.0.0",
                                                                    "OnTextChanged": "config_gui.on_value_changed()"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        
                                        # Paths 섹션
                                        {
                                            "AutoHeight": True,
                                            "SExpandableArea": {
                                                "InitiallyCollapsed": False,
                                                "HeaderContent": {
                                                    "STextBlock": {
                                                        "Text": "📁 Path Settings",
                                                        "Font": {
                                                            "Style": "FCoreStyle",
                                                            "StyleName": "DefaultFont.Bold.12"
                                                        }
                                                    }
                                                },
                                                "BodyContent": {
                                                    "SGridPanel": {
                                                        "FillColumn": [[0, 0.3], [1, 0.7]],
                                                        "Slots": [
                                                            {
                                                                "Column_Row": [0, 0],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Python Path:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 0],
                                                                "Padding": 5,
                                                                "SEditableTextBox": {
                                                                    "Aka": "python_path_text",
                                                                    "Text": "Content/Python",
                                                                    "OnTextChanged": "config_gui.on_value_changed()"
                                                                }
                                                            },
                                                            {
                                                                "Column_Row": [0, 1],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Scripts Path:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 1],
                                                                "Padding": 5,
                                                                "SEditableTextBox": {
                                                                    "Aka": "scripts_path_text",
                                                                    "Text": "Content/Python/Scripts",
                                                                    "OnTextChanged": "config_gui.on_value_changed()"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        
                                        # Editor 섹션
                                        {
                                            "AutoHeight": True,
                                            "SExpandableArea": {
                                                "InitiallyCollapsed": False,
                                                "HeaderContent": {
                                                    "STextBlock": {
                                                        "Text": "⚙️ Editor Settings",
                                                        "Font": {
                                                            "Style": "FCoreStyle",
                                                            "StyleName": "DefaultFont.Bold.12"
                                                        }
                                                    }
                                                },
                                                "BodyContent": {
                                                    "SGridPanel": {
                                                        "FillColumn": [[0, 0.3], [1, 0.7]],
                                                        "Slots": [
                                                            {
                                                                "Column_Row": [0, 0],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Auto Reload:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 0],
                                                                "Padding": 5,
                                                                "SCheckBox": {
                                                                    "Aka": "auto_reload_checkbox",
                                                                    "Content": {"STextBlock": {"Text": "Enable Auto Reload"}},
                                                                    "OnCheckStateChanged": "config_gui.on_value_changed()"
                                                                }
                                                            },
                                                            {
                                                                "Column_Row": [0, 1],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Show Tooltips:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 1],
                                                                "Padding": 5,
                                                                "SCheckBox": {
                                                                    "Aka": "show_tooltips_checkbox",
                                                                    "Content": {"STextBlock": {"Text": "Show Tooltips"}},
                                                                    "OnCheckStateChanged": "config_gui.on_value_changed()"
                                                                }
                                                            },
                                                            {
                                                                "Column_Row": [0, 2],
                                                                "Padding": 5,
                                                                "STextBlock": {"Text": "Theme:"}
                                                            },
                                                            {
                                                                "Column_Row": [1, 2],
                                                                "Padding": 5,
                                                                "SComboBox": {
                                                                    "Aka": "theme_combo",
                                                                    "OptionsSource": ["default", "dark", "light"],
                                                                    "OnSelectionChanged": "config_gui.on_value_changed()"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        
                                        # 버튼들
                                        {
                                            "AutoHeight": True,
                                            "Padding": [0, 20, 0, 10],
                                            "SHorizontalBox": {
                                                "Slots": [
                                                    {
                                                        "Padding": 5,
                                                        "SButton": {
                                                            "Text": "💾 Save Config",
                                                            "ContentPadding": 8,
                                                            "ButtonColorAndOpacity": [0, 0.7, 0, 1],
                                                            "OnClick": "config_gui.save_config()"
                                                        }
                                                    },
                                                    {
                                                        "Padding": 5,
                                                        "SButton": {
                                                            "Text": "🔄 Reload",
                                                            "ContentPadding": 8,
                                                            "ButtonColorAndOpacity": [0, 0.5, 1, 1],
                                                            "OnClick": "config_gui.reload_config()"
                                                        }
                                                    },
                                                    {
                                                        "Padding": 5,
                                                        "SButton": {
                                                            "Text": "⚠️ Reset to Defaults",
                                                            "ContentPadding": 8,
                                                            "ButtonColorAndOpacity": [1, 0.5, 0, 1],
                                                            "OnClick": "config_gui.reset_to_defaults()"
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                        
                                        # Config 미리보기
                                        {
                                            "AutoHeight": True,
                                            "SExpandableArea": {
                                                "InitiallyCollapsed": True,
                                                "HeaderContent": {
                                                    "STextBlock": {
                                                        "Text": "📄 Config Preview",
                                                        "Font": {
                                                            "Style": "FCoreStyle",
                                                            "StyleName": "DefaultFont.Bold.12"
                                                        }
                                                    }
                                                },
                                                "BodyContent": {
                                                    "SMultiLineEditableTextBox": {
                                                        "Aka": "config_display",
                                                        "Text": "",
                                                        "IsReadOnly": True,
                                                        "AutoWrapText": False,
                                                        "Font": {
                                                            "Style": "FCoreStyle",
                                                            "StyleName": "DefaultFont.Mono.10"
                                                        },
                                                        "MinDesiredHeight": 200
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
    # JSON 파일 저장
    json_path = Path(__file__).parent / "config_editor.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(gui_json, f, indent=2, ensure_ascii=False)
    
    unreal.log(f"✅ Config GUI JSON 생성됨: {json_path}")
    return str(json_path)


def launch_config_gui():
    """Config GUI를 실행합니다"""
    json_path = create_config_gui_json()
    unreal.ChameleonData.launch_chameleon_tool(json_path)
    unreal.log("🚀 TAPython Config Editor 실행됨")


# 기존 헬퍼 함수들 유지
def create_sample_config():
    """샘플 config.ini 파일을 생성합니다"""
    editor = TAPythonConfigEditor()
    editor.create_default_config()


def quick_config_edit(section, key, value):
    """빠른 설정 변경"""
    editor = TAPythonConfigEditor()
    if editor.load_config():
        old_value = editor.get_value(section, key)
        editor.set_value(section, key, value)
        if editor.save_config():
            unreal.log(f"✅ 설정 변경: [{section}] {key}: '{old_value}' → '{value}'")
        else:
            unreal.log_error("❌ 설정 저장 실패")
    else:
        unreal.log_error("❌ Config 파일 로드 실패")


unreal.log("✅ TAPython Config Editor 로드 완료")
unreal.log("사용법:")
unreal.log("  launch_config_gui() - GUI 에디터 실행")
unreal.log("  quick_config_edit('section', 'key', 'value') - 빠른 설정 변경")
unreal.log("  create_sample_config() - 샘플 config 생성")