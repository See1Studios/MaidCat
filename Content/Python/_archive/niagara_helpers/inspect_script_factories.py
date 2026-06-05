import unreal

def inspect_factory_cls(cls_name):
    cls = getattr(unreal, cls_name)
    print(f"\n==================== {cls_name} ====================")
    print(cls.__doc__)
    methods = [x for x in dir(cls) if not x.startswith('_')]
    for m in sorted(methods):
        try:
            attr = getattr(cls, m)
            print(f"  {m}: {attr.__doc__ or 'No doc'}")
        except Exception as e:
            pass

inspect_factory_cls("NiagaraScriptFactoryNew")
inspect_factory_cls("NiagaraModuleScriptFactory")
inspect_factory_cls("NiagaraFunctionScriptFactory")
inspect_factory_cls("NiagaraDynamicInputScriptFactory")
