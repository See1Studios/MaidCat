---
name: unreal-python
description: A skill for writing and debugging Unreal Engine Python scripts. Use this skill when writing Unreal editor scripts, using unreal.py stubs, configuring VS Code Remote Execution, reading See1Unreal.log for Python logs, or interfacing with unreal.* API classes.
---

# Unreal Engine Python Development Playbook

This playbook establishes coding standards, codebase file structures, and Unreal Editor API reference guidelines for Python scripting and debugging inside Unreal Engine.

## Instructions

### 0. Project Discovery & Zero Assumptions (Inspired by DSTN2000)

- **Zero Assumptions**: Never assume the project structure or naming conventions. Always discover them dynamically.
- **Inspect `.uproject`**: At the start of tasks, inspect the host project's `.uproject` file (path defined in `dev.local.json`) to confirm:
  - Exact Unreal Engine version.
  - Enabled plugins (e.g., check if `TAPython` or other dependencies are explicitly enabled).
- **Scan Conventions**: Scan existing files in `Content/Python/` or `TA/TAPython/` to match naming, class design, and module import conventions. Do not introduce raw scripts that break project style.

### 1. Python Codebase Structure


The root directory of the Python codebase is `MaidCat/Content/Python/`.

**Important**: This workspace is configured as a standalone plugin development environment. During execution, it runs under the host project directory `{Project}/Plugins/MaidCat/`.

#### Dependencies:
This project depends on the **TAPython** plugin.
- TAPython enables native Slate UI creation in Python.
- Docs: https://www.tacolor.xyz/tapython/welcome_to_tapython.html
- GitHub: https://github.com/cgerchenhp/UE_TAPython_Plugin_Release

**TAPython Library Modules** ([PythonLib API](https://www.tacolor.xyz/tapython/pythonlib_api.html)):
- `unreal.PythonBPLib` - Editor interaction/viewports/assets API (103 functions)
- `unreal.PythonMaterialLib` - Material editing interface (34 functions)
- `unreal.PythonDataTableLib` - DataTable editing interface (19 functions)
- `unreal.PythonMeshLib` - Mesh/SkeletalMesh/ProceduralMesh API (15 functions)
- `unreal.PythonEnumLib` - Custom Enum API (12 functions)
- `unreal.PythonStructLib` - Custom Struct API (14 functions)
- `unreal.PythonLandscapeLib` - Landscape material API (12 functions)
- `unreal.PythonPhysicsAssetLib` - PhysicsAsset API (38 functions)
- `unreal.PythonTextureLib` - Texture2D/RenderTarget2D API (3 functions)
- `unreal.PythonControlRigLib` - ControlRig API
- `unreal.PythonLevelLib` - Level Editor API
- `unreal.PythonTestLib` - Testing interface API

**TAPython Folder Structure** (`{host_project_dir}/TA/TAPython/`):
- `Python/`: Read-only example code (e.g., `ChameleonGallery/`, `QueryTools/` for detail viewers).
- `Lib/site-packages/`: Pip-installed packages.
- `Config/`: TAPython config files.
- `UI/`: Chameleon JSON UI layouts.

#### Plugin Entry Point:
- **`init_unreal.py`**: Executes automatically on Unreal Editor startup. Configures `sys.path`, verifies versions/paths, and runs startup modules (`MaidCatInitializer`).

#### Major Python Modules:
- **`tool/`**: Core utilities (`console_cat/`, `dependencies_installer/`, `migrator.py`, `copier.py`, etc.).
- **`ue/`**: Unreal Engine API wrappers/shortcuts (`asset_*.py`, `level_*.py`, `mat_lib.py`, `mesh_lib.py`, etc.).
- **`util/`**: General helpers (`editor.py`, `static_mesh.py`, `file.py`, `path.py`, etc.).
- **`ui/`**: Chameleon UI controllers (`name_window.py`, `helper.py`, `option_window.py`).
- **`startup/`**: Startup scripts.
- **`validator/`**: Validation scripts.
- **`temp/`**: Git-ignored scratchpad directory for developer testing.

### 2. Python Coding Guidelines

1. **Module Import Order**:
   - Standard libraries ➡️ `unreal` ➡️ local modules.

2. **Native API Preference**:
   - Prefer using the native `unreal` module functions directly.
   - Use wrappers inside `ue/` only as convenient shortcuts.

3. **Temporary Test Code**:
   - Write experimental code inside the git-ignored `temp/` folder.

4. **Dependency Management**:
   - Declare python dependencies in `requirements.txt`.

5. **Error Handling & Logging**:
   - Log using `unreal.log()`, `unreal.log_warning()`, and `unreal.log_error()`.

6. **Type Safety & API Verification**:
   - Always verify API names, arguments, and return types in the generated `unreal.py` stub file (`{host_project_dir}/Intermediate/PythonStub/unreal.py`) before writing code.
   - Leverage Pylance type-checking and IntelliSense autocomplete.

7. **Execution Environment**:
   - Ensure `Enable Remote Execution` is enabled under `Project Settings > Plugins > Python`.
   - Use the VS Code extension `nilssoderman.ue-python` to execute code via `ue-python.execute` (Ctrl+Enter) or attach debuggers.

8. **Unreal Object Properties**:
   - Use `get_editor_property("PropName")` and `set_editor_property("PropName", Value)` for editor-only properties.
   - *Note*: Editor properties do not appear in `dir()`. Check `unreal.py` docstrings.

9. **Explicit Casts**:
   - Recommend explicit casts for Unreal types (e.g., `unreal.Name("name")`, `unreal.Vector(x, y, z)`) to avoid conversion ambiguities.

10. **Debugging & Logs**:
    - Project logs are saved in `{host_project_dir}/Saved/Logs/See1Unreal.log`.
    - Filter logs using the `LogPython:` prefix.
    - Attach debuggers via VS Code (`ue-python.attach`) and control breakpoints using VS Code UI.

11. **Path Resolution**:
    - Never use absolute file paths. Always use relative paths resolved via `unreal.Paths` API (e.g., `unreal.Paths.project_dir()`).

12. **Level & Asset API Verification**:
    - Do NOT guess Level-saving or World-getting methods. Many common legacy functions are either missing or deprecated.
    - **Incorrect**: `EditorLevelLibrary.save_current_level_as_asset()` or `LevelEditorSubsystem.get_context_world()`.
    - **Correct**: `LevelEditorSubsystem.save_current_level()` or `EditorLevelLibrary.get_editor_world()`.

---

## Gotchas & Pitfalls

### AttributeError: LevelEditorSubsystem / EditorLevelLibrary
- **Issue**: Attempting to call speculative methods like `get_context_world()` or `save_current_level_as_asset()` results in AttributeError.
- **Fix**: Use `unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()` for saving. Use `unreal.EditorLevelLibrary.get_editor_world()` to get the current editor world. Always verify methods by extracting them from the generated `unreal.py` stub.

---

## Examples


### 1. Common Unreal Engine API Usage

- **Core System**:
  - `unreal.SystemLibrary` - Tracing, overlap checks, debug drawing.
  - `unreal.GameplayStatics` - Spawners, audio, and gameplay events.
  - `unreal.KismetMathLibrary` - Rotators, vectors, transforms.

- **Editor Asset Management**:
  - `unreal.EditorAssetLibrary` - High-level asset operations (load, save, delete, rename).
  - `unreal.EditorAssetSubsystem` - Duplicate, merge, and metadata editing.
  - `unreal.AssetRegistry` - High-performance queries and tags filtering.
  - `unreal.AssetRegistryHelpers` - AssetData helper utilities.
  - **AssetData Best Practice**: Prefer processing assets using `unreal.AssetData` rather than loading full objects.
    - It is memory-efficient and fast.
    - Properties: `package_name`, `package_path`, `asset_name`, `asset_class_path`.
    - Methods: `get_asset()` (loads object), `is_valid()`, `to_soft_object_path()`.

- **Editor Level & Actor**:
  - `unreal.EditorLevelLibrary` - Spawn/delete/select actors in the world.
  - `unreal.EditorActorSubsystem` - Subsystem for actor selections and alignments.
  - `unreal.EditorFilterLibrary` - Filter actors by class, tags, or layers.

- **Editor Mesh Editing**:
  - `unreal.EditorStaticMeshLibrary` - LODs, UVs, collision generation.
  - `unreal.EditorSkeletalMeshLibrary` - Bones, morph targets, LOD configurations.

- **Subsystem Acquisition**:
  - `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)`
