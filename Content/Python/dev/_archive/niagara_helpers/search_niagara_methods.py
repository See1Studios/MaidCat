import unreal

def search_methods(cls):
    print(f"=== Methods of {cls.__name__} ===")
    methods = [x for x in dir(cls) if not x.startswith('_')]
    for m in sorted(methods):
        print("  ", m)

search_methods(unreal.NiagaraSystem)
search_methods(unreal.NiagaraEmitter)
