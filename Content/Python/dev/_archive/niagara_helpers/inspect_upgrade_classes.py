import unreal

def inspect_cls(cls_name):
    cls = getattr(unreal, cls_name)
    print(f"\n==================== {cls_name} ====================")
    print(cls.__doc__)
    methods = [x for x in dir(cls) if not x.startswith('_')]
    for m in sorted(methods):
        try:
            attr = getattr(cls, m)
            print(f"  {m}: {attr.__doc__ or 'No doc'}")
        except Exception as e:
            print(f"  {m}: {e}")

inspect_cls("UpgradeNiagaraEmitterContext")
inspect_cls("UpgradeNiagaraScriptResults")
