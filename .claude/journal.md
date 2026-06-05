# Antigravity Developer Journal

This journal tracks the self-evolution milestones, trials, and learnings of the Antigravity AI assistant during the MaidCat project development.

---

## [2026-06-05] Self-Evolution Framework and First Skill Deployment

### 1. What I Did Today
- **Language & Communication Policy**: Configured Korean for user interaction and English for internal skills/guidelines to optimize context token usage.
- **User Self-Restraint Instruction**: Registered the user's explicit request to block them from building degraded clones or reinventing wheels. Updated [AGENTS.md](file:///C:/Users/parkj/Documents/GitHub/MaidCat/AGENTS.md) to guarantee future enforcement.
- **Auto-Activation Registry**: Created an `--active` flag mechanism in `requirements.txt` to instantly load critical skills (e.g., `caveman` mode) upon project entry.
- **Orchestrated Verification**: Integrated a multi-agent peer review step into the Self-Improvement Loop. The agent now spawns a `self` subagent as an `Auditor` to review code/guidelines draft against `unreal.py` API syntax and Karpathy guidelines before finalizing.
- **External Benchmarking**: Enforced searching and comparing external solutions (e.g., DSTN2000, Quodsoler repos) before writing playbooks.
- **Skill Deployments**:
  - Created and registered the `unreal-material` playbook covering shader permutation safety, shared samplers, and NaN pixel fixes.
  - Updated the `unreal-python` playbook with the "Zero Assumptions Project Discovery" rule to inspect `.uproject` dynamically instead of assuming directory structures.
- **Unreal Remote MCP Integration**:
  - Implemented a custom Python-based MCP server (`unreal_mcp.py`) that utilizes Unreal Engine's native TCP `Remote Execution` protocol.
  - Configured `mcp_config.json` to register this server under the name `unreal-remote`.
  - Installed Python `mcp` SDK to enable server-client handshake.
  - This allows the agent to run arbitrary Python code inside a running Unreal Editor instance with zero plugin installations.
  - Verified connection via `test_remote.py`: Successfully auto-discovered UE 5.5 instance (`PlayGround` project on `ROG-ALLY-X`), established command connection, executed `unreal.log()`, and captured success output.



### 2. Learnings & Pitfalls
- **The Blind Spot of Inside-Out Knowledge**: Realized that relying only on internal weights for drafting guidelines leads to missing modern best practices. Direct web-searching of existing GitHub playbooks (like DSTN2000's zero-assumption scanning) proved essential.
- **Orchestration Value**: Generating a peer agent to audit code blocks reduces the cognitive strain of single-context verification, yielding cleaner syntax and structured gotchas.
- **Level API Trial-and-Error**:
  - *Problem*: Guessed method names (`get_context_world`, `save_current_level_as_asset`) resulting in `AttributeError` during Remote Execution.
  - *Correction*: Inspected `unreal.py` stub dynamically via a parsing script. Replaced with valid methods: `unreal.LevelEditorSubsystem.save_current_level()` and `unreal.EditorLevelLibrary.get_editor_world()`.
  - *Prevention*: Updated `unreal-python` playbook with the explicit correct vs incorrect API patterns to prevent regression.
- **Autonomous Troubleshooting Guideline**:
  - *Policy*: Enforced self-contained execution testing and error recovery using subagents. Trivial debug choices/approvals will be resolved internally rather than prompting the user.
  - *Sandbox Constraint*: Dangerous commands like `python` cannot be pre-authorized via `ask_permission`. The agent will invoke `run_command` directly to trigger UI popups, skipping any textual asking in chat.
  - *Loop Prevention*: Established a strict maximum 3-retry limit for autonomous debugging. If a task fails 3 times, execution halts and escalates to the user.
  - *Action*: Updated `AGENTS.md` verification protocol.
- **ShaderToy Material Creation**:
  - *Task*: Convert multiple ShaderToy shaders (Neon Ring, Plasma Wave, Glowing Star) into Unreal Materials, then compile them into a single composite material.
  - *Implementation*: Created `/Game/M_ShaderToyTest`, `/Game/M_ShaderToyPlasma`, and `/Game/M_ShaderToyStar`. Subsequently built `/Game/M_ShaderToyComposite` using a single Custom Node containing all three HLSL algorithms, multiplexed via a `Mode` dynamic switch parameter.
  - *Layout & Parameter Rules*: Adhered to parameter grouping (placed `Mode` in "Controls" group) and Left-to-Right layout, ensuring 100% clean connection wires.
  - *Lock & API Constraints*: 
    - Attempted to read protected `expressions` property via `get_editor_property("expressions")` to manually delete nodes in a loop, resulting in a read error.
    - Verified that `delete_all_material_expressions()` is the only viable way to clear nodes. Re-established the fallback mechanism.
  - *Automation*: Ran remote editor compilation and saving successfully (`Save status: True` for all assets).
- **Blueprint API Discovery**:
  - *Research*: Verified capabilities of Blueprint asset scripting.
  - *Key Finding*: `unreal.BlueprintEditorLibrary` is fully functional for BP creation/compilation. `unreal.SubobjectDataSubsystem` handles component trees.
  - *Gotcha*: `SubobjectDataSubsystem` is an `EngineSubsystem`, meaning it must be fetched via `unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)` instead of `get_editor_subsystem()`.
  - *State Persistence Gotcha*: When adding subobjects to a Blueprint context, **`blueprint.modify()`** must be called to mark the asset dirty. Otherwise, compilation and file saving fail to write the new component tree to disk, keeping changes only in temporary memory.
  - *UObject Access*: Discovered that `SubobjectDataHandle` is an opaque struct wrapper. To retrieve the actual `UObject` component instance, **`unreal.SubobjectDataBlueprintFunctionLibrary.get_object(bp_lib.get_data(handle))`** must be called.
  - *Execution*: Successfully built `/Game/BP_MyTestActor`, dynamically attached a `StaticMeshComponent`, and assigned the engine basic shape `Cube` mesh to it persistently (`Save status: True`).
- **Landscape Creation & Sculpting**:
  - *Task*: Dynamically instantiate and sculpt a terrain.
  - *Implementation*: Used TAPython's `unreal.PythonLandscapeLib.create_landscape` with X=2, Y=2 components (resolution 127x127).
  - *Sculpting*:
    - Initial Trial: Generated simple mathematical sine-wave ripples.
    - Second Trial: Implemented Fractal Value Noise (5 octaves fBm). Jagged/spiky hills were detected.
    - Final Polish: Decreased gain to 0.32 and expanded frequency scale to flatten steep slopes. Implemented a 3x3 Box Blur filter (`smooth_heightmap`) with 2 iterations to simulate erosion, and drastically lowered the height scale factor from `24000.0` to `6500.0` to balance the aspect ratio, resulting in natural, rolling organic hills.
  - *Procedural Shading*:
    - Created a textureless, mathematical `/Game/M_LandscapeProcedural` material.
    - Inside a Custom HLSL Node, evaluated pixel `Parameters.WorldPosition_NoOffsets` (height) and `Parameters.WorldNormal` (slope).
    - Blended color targets dynamically: Flat areas = grass (dark green), steep cliffs = rock (slate gray), high-altitude peaks = snow.
    - Wired Custom Output to `Base Color`, set `Roughness` to a matte `0.85` constant, and mapped the material to the Landscape's `landscape_material` property.
  - *Shading*: Triggered `recalculate_normals()` to ensure standard engine shadow and light evaluation updated successfully.













### LWC Custom Node Compile Failure (UE 5.4+)
- *Problem*: `M_LandscapeProcedural` shader compile failed; log showed `Failed to compile Material for platform PCD3D_SM6` + `Material.ush: cannot initialize a variable of type 'float3' with an lvalue of type 'FDFVector3'`. Material silently fell back to Default Material (warning only, no hard error).
- *Root Cause*: Custom HLSL node assigned `Parameters.WorldPosition_NoOffsets` directly to `float3`. Since UE 5.4, Large World Coordinates promotes world positions to the `FDFVector3` double-float struct, so direct assignment is a type mismatch.
- *Verification*: Confirmed against engine shaders — `DoubleFloatOperations.ush:20` defines `DFDemote(FDFType) -> FFloatType` (and a no-op overload for plain `float`); `LargeWorldCoordinates.ush:249` defines legacy `LWCToFloat(FLWCVector3)`.
- *Prevention*: Best practice is to wire world-space values through a Custom node **Input pin** (auto-demotes to `float3`); inline fallback is `DFDemote(...)`. Recorded as `unreal-material` Instruction §4 (LWC), a new Gotcha, and Comparative Examples.

### Fab Plugin Workflow Knowledge (UE 5.5)
- *Goal*: Build durable knowledge of how the engine-bundled Fab plugin moves assets, rather than one-off level construction.
- *Source Investigation*: Read `Engine/Plugins/Fab` source directly — `FabSettings`, `FabAssetsCache`, `FabLocalAssets`, `FabConsoleCommands`, `FabBrowserApi`.
- *Key Findings*:
  - **Automation boundary**: Download/import is driven by the embedded web frontend (Chromium) via server-signed URLs → NOT scriptable. Post-import `/Game/Fab/<product>/` assets ARE freely scriptable with Python.
  - **Console surface**: Only 5 commands (`Fab.Login/Logout/ShowSettings/ClearCache/SetEnvironment`) — auth/cache/env management, no download/import command.
  - **`UFabBrowserApi::AddToProject`** is a real entry point but `UFUNCTION()` without `BlueprintCallable` → not exposed to Python/BP; `DownloadUrl` is a server-signed URL, uncforgeable.
  - **Cache layout**: `%TEMP%\FabLibrary\<listing-guid>\source_extracted\<name>_extracted\` (raw gltf/textures, 10-day expiry).
  - **Import layout**: `/Game/Fab/<ProductName-sanitized>/` flat (mesh+material+textures together).
  - **"alias" tracking**: `EditorPerProjectUserSettings.ini [/Script/Fab.FabLocalAssets] PathsListingID` maps `/Game` path ↔ Fab listing GUID.
- *Live Verification*: Confirmed with a real import — "FREE Desert Terrain / Landscape" landed in `Content/Fab/FREE_Desert_Terrain___Landscape_/` only after Save All (assets exist in Asset Registry but not on disk until saved).
- *Pitfall Recorded*: A Fab title containing "Terrain/Landscape" is usually a static-mesh model + PBR set, NOT a UE Landscape-actor layer material.
- *Action*: Created the `unreal-fab` skill capturing the automation boundary, cache/import paths, console commands, settings, and gotchas.

### Self-Improvement Loop Retro + Shell Fix
- *Self-eval*: Knowledge quality strong (1st-source + live verification, self-correction worked), but efficiency weak — repeated PowerShell command failures wasted tokens, and the Auditor-subagent + external-benchmarking steps were skipped on the `unreal-fab` skill (protocol gap to tighten).
- *Root cause of waste*: Bash tool = git-bash, so `powershell -Command "..."` lets bash pre-expand `$_`/`$env:`/`${}`. Retried the broken double-quoted form ~4x instead of switching strategy.
- *Fix verified*: Single-quote wrapping (`powershell -Command '...'`) stops bash expansion; dedicated `Glob`/`Grep`/`Read` avoid it entirely. Recorded in `AGENTS.md` Dev Environment as a Shell Gotcha (ref Claude Code issue #15471).

### 3. Next Evolution Focus
- Maintain this journal recursively at the end of each session or major milestone.
- Begin refactoring actual Unreal Python plugin script nodes using these newly established rules.

### 4. [Session 2] Python Codebase Bug Fixes and Root Directory Clean-up
- **Bug Fixes**:
  - Fixed a `NameError` in `tool/dev_env_setup.py` by adding the missing `import platform` standard library import.
  - Fixed a startup menu registration warning (`⚠️  메뉴가 등록되지 않음: ContentBrowser.AssetContextMenu`) in `editor/mi_context.py` by refactoring `is_menu_registered` + `find_menu` to use `extend_menu` directly. This allows registering extensions to lazy-loaded / deferred menus safely before their subsystems initialize them.
- **Root Clean-up**:
  - Verified and deleted `debug_struct_properties.py` (obsolete debug script).
  - Safely deleted `MaidCat_PythonTestObject.uasset` (unused test UObject Blueprint) using `unreal.EditorAssetLibrary.delete_asset` inside the editor, bypassing OS file locking.
- **Learnings**:
  - *Content Browser Sync gotcha*: Confirmed that newly created Python folders (like `agentcat`) do not dynamically update in the Content Browser via file watchers. They require an editor restart (or manual Asset Registry path scan) because Python script asset integration caches directories at editor startup.

### 5. [Session 3] Python Codebase Restructuring & Namespace Unification
- **Restructuring & Organization**:
  - Consolidated 16 fragmented Python root folders into a unified `maidcat/` package namespace (split into `core/`, `editor/`, `tools/`, `ui/`, `agentcat/`, `chameleon/`, `data/`) to prevent plugin namespace collisions in host Unreal projects.
  - Isolated test validator scripts under a new `tests/` directory.
  - Moved temporary developer sandboxes (`temp/`, `sample/`, `_archive/`) to a `dev/` directory at the Python Content root.
- **Import Redirection System**:
  - Developed a dynamic `sys.modules` pre-population and namespace binding algorithm in `init_unreal.py`.
  - The script dynamically crawls all subpackages and mounts them to the legacy module names (e.g., binding `maidcat.core.utils.name` to `util.name`) at editor startup. This ensures 100% backward compatibility for all dot-notation imports (`import util.name as const`) with zero manual file edits.
- **Verification**:
  - Successfully ran full initialization tests in the Unreal Engine editor with 0 errors and 0 module failures. All editor extensions, UI dialogs, and material preset libraries loaded cleanly.

### 6. [Session 4] Root-level Flat Restructuring & Metaclass Mock Verification
- **Root-level Flat Restructuring (No Top-Level Package)**:
  - Honored the user's design decision to NOT use a `maidcat/` top-level namespace, keeping packages directly under `Content/Python/`.
  - Moved subfolders out of `maidcat/` and established flat root packages: `api/` (unreal API), `util/` (general helpers), `tool/` (automation), `editor/` (UI/menus), `agentcat/` (pre-packaged library), `test/` (testing), `dev/` (development scratchpad).
  - Deleted the temporary `maidcat` top-level directory.
- **100% Singular Naming & Redirection Refinement**:
  - Unified all package folder names to be consistently singular (`api`, `util`, `tool`, `editor`, `test`, `dev`) to eliminate confusion and maintain complete consistency.
  - By using `util` and `tool` as folder names, legacy imports (`import util.file`, `import tool.mi_serializer`) now resolve **natively** via python's search path, completely bypassing redirection overhead for those packages.
  - Configured `init_unreal.py` redirects to only map the remaining renames: `api` ➡️ `ue`, `editor.ui` ➡️ `ui`, `editor.startup` ➡️ `startup`.
  - Preserved dual-alias registration (mapping `editor.menus.*` submodules to both `tool.{name}` and `editor.{name}`) for seamless context menu string delegate evaluation.
  - Refactored all internal startup imports inside `init_unreal.py` to use direct root package names (`tool.tapython_installer`, `tool.dependencies_installer`, `editor.startup.setup_python`).
- **Gotcha & Resolution (Package Walk discovery)**:
  - Created placeholder `__init__.py` files inside `tool/`, `editor/menus/`, and `editor/ui/` to ensure `pkgutil.walk_packages` recursively discovers and registers all submodules without ignoring them.
- **Local Metaclass Mock Verification**:
  - Implemented and verified a metaclass-based `MockUnreal` dummy engine class locally to test full module loading and dynamic redirection without requiring a running Unreal Editor instance. The local syntax and import checks completed with 0 errors.
  - Staged all changes cleanly in git (`git add -A`).


