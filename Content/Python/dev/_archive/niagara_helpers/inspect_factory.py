import unreal
factory = unreal.NiagaraSystemFactoryNew()
print("Factory properties:")
for prop in dir(factory):
    try:
        val = getattr(factory, prop)
        if not callable(val):
            print(f"  {prop}: {val}")
    except Exception as e:
        print(f"  {prop}: Error getting: {e}")
