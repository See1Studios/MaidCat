import os

base_dir = r"C:\Users\parkj\Documents\GitHub\VibeUE"

# Helper to read and write files with universal newlines
def patch_file(path, replacements):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return False
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  Replaced code in {os.path.basename(path)}")
        else:
            print(f"  Warning: Code block not found in {os.path.basename(path)}")
            
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# 1. Patch UStateTreeService.cpp
path_state = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UStateTreeService.cpp")
state_replacements = [
    # Replace WITH_EDITORONLY_DATA
    ('#if WITH_EDITORONLY_DATA', '#if 0 // WITH_EDITORONLY_DATA (Disabled for UE 5.5 compatibility)'),
    
    # Replace namespace declaration to wrap helpers in #if 0 and define LoadStateTree
    ('namespace UStateTreeServiceHelpers\n{', 
     '''static UStateTree* LoadStateTree(const FString& AssetPath)
{
	if (AssetPath.IsEmpty())
	{
		return nullptr;
	}
	return Cast<UStateTree>(UEditorAssetLibrary::LoadAsset(AssetPath));
}

#if 0
namespace UStateTreeServiceHelpers
{'''),

    # Replace closing namespace
    ('} // namespace UStateTreeServiceHelpers\n\nusing namespace UStateTreeServiceHelpers;',
     '''} // namespace UStateTreeServiceHelpers
#endif

using namespace UStateTreeServiceHelpers;''')
]
print("Patching UStateTreeService.cpp...")
patch_file(path_state, state_replacements)

# 2. Patch UNiagaraService.cpp
path_ns = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UNiagaraService.cpp")
ns_replacements = [
    ('#include "PythonAPI/UNiagaraService.h"', 
     '''#include "PythonAPI/UNiagaraService.h"

// Define macro to bridge UE 5.5 Niagara GetParameterData signature
#define GetParameterData(a, b) GetParameterData(a)''')
]
print("Patching UNiagaraService.cpp...")
patch_file(path_ns, ns_replacements)

# 3. Patch UNiagaraEmitterService.cpp
path_nes = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UNiagaraEmitterService.cpp")
nes_replacements = [
    ('#include "PythonAPI/UNiagaraEmitterService.h"', 
     '''#include "PythonAPI/UNiagaraEmitterService.h"

// Define macro to bridge UE 5.5 Niagara GetParameterData signature
#define GetParameterData(a, b) GetParameterData(a)''')
]
print("Patching UNiagaraEmitterService.cpp...")
patch_file(path_nes, nes_replacements)

# 4. Patch UViewportService.cpp
path_view = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UViewportService.cpp")
view_replacements = [
    ('else if (Lower == TEXT("clay"))                 NewMode = VMI_Clay;', '// else if (Lower == TEXT("clay"))                 NewMode = VMI_Clay;'),
    ('case VMI_Clay:                 return TEXT("clay");', '// case VMI_Clay:                 return TEXT("clay");')
]
print("Patching UViewportService.cpp...")
patch_file(path_view, view_replacements)

# 5. Patch UWidgetService.cpp
path_widget = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UWidgetService.cpp")
widget_replacements = [
    ('WidgetBP->WidgetVariableNameToGuidMap', '// WidgetBP->WidgetVariableNameToGuidMap')
]
print("Patching UWidgetService.cpp...")
patch_file(path_widget, widget_replacements)

# 6. Patch UAssetDiscoveryService.cpp
path_asset = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UAssetDiscoveryService.cpp")
asset_replacements = [
    ('TArray<IAssetEditorInstance*> OpenEditors = AssetEditorSubsystem->GetAllOpenEditors();',
     '''TArray<IAssetEditorInstance*> OpenEditors;
	TArray<UObject*> EditedAssets = AssetEditorSubsystem->GetAllEditedAssets();
	for (UObject* Asset : EditedAssets)
	{
		if (Asset)
		{
			OpenEditors.Append(AssetEditorSubsystem->FindEditorsForAsset(Asset));
		}
	}''')
]
print("Patching UAssetDiscoveryService.cpp...")
patch_file(path_asset, asset_replacements)

print("All patches applied!")
