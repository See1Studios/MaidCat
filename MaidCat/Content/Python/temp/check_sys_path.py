"""
Unreal Engine에서 sys.path 확인
언리얼 에디터의 Python 콘솔에서 실행하세요
"""

import sys
from pathlib import Path

print("=" * 80)
print("Current sys.path in Unreal Engine")
print("=" * 80)

# 프로젝트 루트 찾기
try:
    import unreal
    project_dir = Path(unreal.Paths.project_dir())
    print(f"\n📁 Project Root: {project_dir}\n")
except:
    project_dir = None
    print("\n⚠️  Not running in Unreal Editor\n")

print("📍 sys.path entries:\n")

for i, path in enumerate(sys.path, 1):
    path_obj = Path(path)
    
    # 프로젝트 관련 경로인지 확인
    is_project = False
    if project_dir:
        try:
            path_obj.relative_to(project_dir)
            is_project = True
        except ValueError:
            pass
    
    marker = "✅" if is_project else "  "
    print(f"{marker} {i:2d}. {path}")

if project_dir:
    print("\n" + "=" * 80)
    print("✅ = Project-related paths (should be in VS Code settings)")
    print("   = External/System paths (usually not needed)")
    print("=" * 80)

# 프로젝트 관련 경로만 필터링
if project_dir:
    print("\n" + "=" * 80)
    print("Recommended paths for VS Code settings:")
    print("=" * 80 + "\n")
    
    for path in sys.path:
        path_obj = Path(path)
        try:
            rel_path = path_obj.relative_to(project_dir)
            print(f"  • {rel_path}")
        except ValueError:
            pass
