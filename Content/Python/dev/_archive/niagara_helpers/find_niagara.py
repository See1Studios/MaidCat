import unreal
niagara_classes = [x for x in dir(unreal) if 'Niagara' in x]
print("FOUND NIAGARA CLASSES:")
for cls_name in sorted(niagara_classes):
    print("  ", cls_name)
