import unreal

ns_path = "/Game/NS_Fire"
ns_asset = unreal.EditorAssetLibrary.load_asset(ns_path)

if ns_asset:
    print(f"Loaded {ns_path} successfully.")
    # Let's see if there are user parameters or expose API
    # Normally, we can use NiagaraDataInterface or parameter definitions.
    # Let's list properties of the asset editor data if any.
    # Let's inspect variables.
    print("Variables or properties:")
    for attr in dir(ns_asset):
        if 'parameter' in attr.lower() or 'variable' in attr.lower():
            print("  ", attr)
else:
    print(f"Failed to load {ns_path}")
