import os

base_dir = r"C:\Users\parkj\Documents\GitHub\VibeUE"

# 1. Update UStateTreeService.cpp helper wrapping
path_state = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UStateTreeService.cpp")
if os.path.exists(path_state):
    with open(path_state, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalize line endings to LF for easier replacement
    content_lf = content.replace('\r\n', '\n')
    
    old_helper1 = """static FString TasksCompletionTypeToString(EStateTreeTaskCompletionType Type)
{
	switch (Type)
	{
	case EStateTreeTaskCompletionType::Any: return TEXT("Any");
	case EStateTreeTaskCompletionType::All: return TEXT("All");
	default:                                return TEXT("Any");
	}
}"""
    old_helper1_lf = old_helper1.replace('\r\n', '\n')
    
    new_helper1 = """#if 0
static FString TasksCompletionTypeToString(EStateTreeTaskCompletionType Type)
{
	switch (Type)
	{
	case EStateTreeTaskCompletionType::Any: return TEXT("Any");
	case EStateTreeTaskCompletionType::All: return TEXT("All");
	default:                                return TEXT("Any");
	}
}
#endif"""
    new_helper1_lf = new_helper1.replace('\r\n', '\n')

    old_helper2 = """static EStateTreeTaskCompletionType StringToTasksCompletionType(const FString& Str)
{
	if (Str == TEXT("All")) return EStateTreeTaskCompletionType::All;
	return EStateTreeTaskCompletionType::Any;
}"""
    old_helper2_lf = old_helper2.replace('\r\n', '\n')
    
    new_helper2 = """#if 0
static EStateTreeTaskCompletionType StringToTasksCompletionType(const FString& Str)
{
	if (Str == TEXT("All")) return EStateTreeTaskCompletionType::All;
	return EStateTreeTaskCompletionType::Any;
}
#endif"""
    new_helper2_lf = new_helper2.replace('\r\n', '\n')
    
    if old_helper1_lf in content_lf:
        content_lf = content_lf.replace(old_helper1_lf, new_helper1_lf)
        print("TasksCompletionTypeToString replaced")
    else:
        print("TasksCompletionTypeToString NOT found")
        
    if old_helper2_lf in content_lf:
        content_lf = content_lf.replace(old_helper2_lf, new_helper2_lf)
        print("StringToTasksCompletionType replaced")
    else:
        print("StringToTasksCompletionType NOT found")
        
    # Restore CRLF
    content = content_lf.replace('\n', '\r\n')
    
    with open(path_state, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("UStateTreeService.cpp not found")

# 2. Fix UNiagaraService.cpp GetParameterData calls
path_ns = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UNiagaraService.cpp")
if os.path.exists(path_ns):
    with open(path_ns, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('GetParameterData(Offset, TypeDef)', 'GetParameterData(Offset)')
    
    with open(path_ns, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched UNiagaraService.cpp")
else:
    print("UNiagaraService.cpp not found")

# 3. Fix UNiagaraEmitterService.cpp GetParameterData calls
path_nes = os.path.join(base_dir, "Source", "VibeUE", "Private", "PythonAPI", "UNiagaraEmitterService.cpp")
if os.path.exists(path_nes):
    with open(path_nes, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace('GetParameterData(Offset, TypeDef)', 'GetParameterData(Offset)')
    
    with open(path_nes, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched UNiagaraEmitterService.cpp")
else:
    print("UNiagaraEmitterService.cpp not found")
