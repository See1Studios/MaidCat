import unreal
import inspect

def print_details(cls_name):
    cls = getattr(unreal, cls_name)
    print(f"=== {cls_name} ===")
    print(cls.__doc__)
    print("Methods & Properties:")
    for name in dir(cls):
        attr = getattr(cls, name)
        if callable(attr):
            print(f"  Method: {name}")
        else:
            print(f"  Property/Attr: {name}")

print_details("NiagaraPythonEmitter")
print_details("NiagaraClipboardEditorScriptingUtilities")
