import unreal

# Load the ProjecterNS system
ns_path = "/MaidCat/See1/ProjecterNS"
ns_asset = unreal.EditorAssetLibrary.load_asset(ns_path)

if ns_asset:
    print(f"Loaded {ns_path} successfully!")
    print(f"Class: {ns_asset.get_class().get_name()}")
    # Let's inspect its properties
    for prop in dir(ns_asset):
        if not prop.startswith('_'):
            try:
                val = getattr(ns_asset, prop)
                if not callable(val):
                    print(f"  {prop}: {val}")
            except Exception as e:
                pass
else:
    print(f"Failed to load {ns_path}")
