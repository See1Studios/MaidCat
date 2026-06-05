import os

base_dir = r"C:\Users\parkj\Documents\GitHub\VibeUE"

# 1. Fix UAssetDiscoveryService.cpp
path_asset = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UAssetDiscoveryService.cpp")
if os.path.exists(path_asset):
    with open(path_asset, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_code = 'TArray<IAssetEditorInstance*> OpenEditors = AssetEditorSubsystem->GetAllOpenEditors();'
    new_code = '''TArray<IAssetEditorInstance*> OpenEditors;
	TArray<UObject*> EditedAssets = AssetEditorSubsystem->GetAllEditedAssets();
	for (UObject* Asset : EditedAssets)
	{
		if (Asset)
		{
			OpenEditors.Append(AssetEditorSubsystem->FindEditorsForAsset(Asset));
		}
	}'''
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(path_asset, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed UAssetDiscoveryService.cpp")
    else:
        print("UAssetDiscoveryService.cpp already fixed or old_code not found")
else:
    print("UAssetDiscoveryService.cpp not found")

# 2. Fix UViewportService.cpp
path_view = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UViewportService.cpp")
if os.path.exists(path_view):
    with open(path_view, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('else if (Lower == TEXT("clay"))                 NewMode = VMI_Clay;', '// else if (Lower == TEXT("clay"))                 NewMode = VMI_Clay;')
    content = content.replace('case VMI_Clay:                 return TEXT("clay");', '// case VMI_Clay:                 return TEXT("clay");')
    
    with open(path_view, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed UViewportService.cpp")
else:
    print("UViewportService.cpp not found")

# 3. Fix UWidgetService.cpp
path_widget = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UWidgetService.cpp")
if os.path.exists(path_widget):
    with open(path_widget, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_widget_code = """	const FName WidgetFName = NewWidget->GetFName();
	if (!WidgetBP->WidgetVariableNameToGuidMap.Contains(WidgetFName))
	{
		WidgetBP->WidgetVariableNameToGuidMap.Add(WidgetFName, FGuid::NewGuid());
	}"""
    
    new_widget_code = """	// const FName WidgetFName = NewWidget->GetFName();
	// if (!WidgetBP->WidgetVariableNameToGuidMap.Contains(WidgetFName))
	// {
	// 	WidgetBP->WidgetVariableNameToGuidMap.Add(WidgetFName, FGuid::NewGuid());
	// }"""
    
    if old_widget_code in content:
        content = content.replace(old_widget_code, new_widget_code)
        print("Fixed UWidgetService.cpp via block replace")
    else:
        # Fallback simple replace
        content = content.replace('WidgetBP->WidgetVariableNameToGuidMap', '// WidgetBP->WidgetVariableNameToGuidMap')
        print("Fixed UWidgetService.cpp via fallback replace")
        
    with open(path_widget, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("UWidgetService.cpp not found")

# 4. Fix UStateTreeService.cpp by disabling WITH_EDITORONLY_DATA
path_state = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UStateTreeService.cpp")
if os.path.exists(path_state):
    with open(path_state, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace('#if WITH_EDITORONLY_DATA', '#if 0 // WITH_EDITORONLY_DATA (Disabled for UE 5.5 compatibility)')
    
    with open(path_state, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed UStateTreeService.cpp")
else:
    print("UStateTreeService.cpp not found")
