import unreal

# List all subclasses of unreal.EditorSubsystem
subsystems = [x for x in dir(unreal) if 'Subsystem' in x]
print("All subsystems with Niagara:")
for s in subsystems:
    if 'Niagara' in s:
        print("  ", s)
