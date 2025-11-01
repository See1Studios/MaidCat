# import unreal  

# # Define the owning menu where the button will be added
# menu_owner = "editorUtilities"  
# tool_menus = unreal.ToolMenus.get()  
# owning_menu_name = "LevelEditor.LevelEditorToolBar.AssetsToolBar"  

# # Define a custom Python class for the toolbar button
# @unreal.uclass()
# class CreateEntryExample(unreal.ToolMenuEntryScript):  

#     def __init__(self):
#         super().__init__()  # Properly initialize the class

#     @unreal.ufunction(override=True)  
#     def execute(self, context):  
#         """ Opens the custom UI widget when the button is clicked. """
#         registry = unreal.AssetRegistryHelpers.get_asset_registry()  
#         asset = unreal.EditorAssetLibrary.load_asset("/Game/MaidCat/MaidCat")  
        
#         # Get the EditorUtilitySubsystem
#         editor_utility = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)

#         # Try to find the utility widget
#         bp = editor_utility.find_utility_widget_from_blueprint(asset)

#         if bp is None:  
#             # Spawn the UI widget if it's not already open
#             bp = editor_utility.spawn_and_register_tab(asset)  
#         # else:
#             # If already open, bring it to the front
#             # editor_utility.invoke_tab(asset)

#     def init_as_toolbar_button(self):  
#         """ Initialize the button as a toolbar button. """
#         self.data.menu = owning_menu_name  
#         self.data.advanced.entry_type = unreal.MultiBlockType.TOOL_BAR_BUTTON  
#         self.data.icon = unreal.ScriptSlateIcon("EditorStyle", "Launcher.EditSettings")  # Play button

# def Run():  
#     """ Runs the script and adds the button to the UE5 toolbar. """
#     entry = CreateEntryExample()  
#     entry.init_as_toolbar_button()  

#     # Initialize the entry properly
#     entry.init_entry(
#         menu_owner, 
#         "maidCatButtonEntry",  # Unique ID
#         "",  # No section name
#         "MaidCat",  # Button text
#         "Nya"  # Tooltip
#     )

#     # Extend the toolbar and add the button
#     toolbar = tool_menus.extend_menu(owning_menu_name)  
#     toolbar.add_menu_entry_object(entry)  

#     # Refresh all UI elements to apply changes
#     tool_menus.refresh_all_widgets()

# # Run the script
# Run()
