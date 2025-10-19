import unreal

def pre_import_callback(factory,class_type ,parent, name, type):
    print("="*50)
    print(f'Pre Import Callback: {name}')
    print("="*50)

def post_import_callback(factory, created_object):
    print("="*50)
    print(f'Post Import Callback: {created_object}')
    print("="*50)

def post_lod_import_callback(object, lod_index):
    print("="*50)
    print(f'Post LOD Import Callback: {object}, LOD Index: {lod_index}')
    print("="*50)

def reimport_callback(created_object):
    print("="*50)
    print(f'Reimport Callback: {created_object}')
    print("="*50)

iss = unreal.get_editor_subsystem(unreal.ImportSubsystem)
iss.on_asset_pre_import.clear()
iss.on_asset_post_import.clear()
iss.on_asset_post_lod_import.clear()
iss.on_asset_reimport.clear()
iss.on_asset_pre_import.add_callable(pre_import_callback)
iss.on_asset_post_import.add_callable(post_import_callback)
iss.on_asset_post_lod_import.add_callable(post_lod_import_callback)
iss.on_asset_reimport.add_callable(reimport_callback)

print('Import Callbacks Registered')