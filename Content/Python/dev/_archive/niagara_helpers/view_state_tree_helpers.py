import re

path = r"C:\Users\parkj\Documents\GitHub\VibeUE\Source\VibeUE\Private\PythonAPI\UStateTreeService.cpp"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Static functions between 1300 and 1800:")
for idx in range(1299, 1800):
    if idx < len(lines):
        line = lines[idx]
        if line.strip().startswith('static '):
            print(f"Line {idx+1}: {line.strip()}")
