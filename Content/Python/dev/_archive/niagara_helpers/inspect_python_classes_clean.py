import unreal

def inspect_clean(cls_name):
    cls = getattr(unreal, cls_name)
    print(f"\n==================== {cls_name} ====================")
    # Get methods of unreal.Object to filter them out
    obj_methods = set(dir(unreal.Object))
    methods = [x for x in dir(cls) if not x.startswith('_') and x not in obj_methods]
    for m in sorted(methods):
        attr = getattr(cls, m)
        print(f"  Method/Attr: {m}")
        if attr.__doc__:
            # Print only first few lines of docstring to keep it clean
            first_lines = "\n".join(attr.__doc__.strip().split("\n")[:3])
            print(f"    Doc: {first_lines}")

inspect_clean("NiagaraPythonEmitter")
inspect_clean("NiagaraPythonModule")
inspect_clean("NiagaraPythonScriptModuleInput")
