import unreal

def inspect_class(cls_name):
    try:
        cls = getattr(unreal, cls_name)
        print(f"\n==================== {cls_name} ====================")
        print(cls.__doc__)
        print("Methods:")
        methods = [x for x in dir(cls) if not x.startswith('_')]
        for m in sorted(methods):
            try:
                attr = getattr(cls, m)
                print(f"  {m}: {attr.__doc__ or 'No doc'}")
            except Exception as e:
                print(f"  {m}: Error getting doc: {e}")
    except Exception as e:
        print(f"Failed to inspect {cls_name}: {e}")

inspect_class("NiagaraPythonEmitter")
inspect_class("NiagaraPythonModule")
inspect_class("NiagaraPythonScriptModuleInput")
inspect_class("NiagaraClipboardEditorScriptingUtilities")
