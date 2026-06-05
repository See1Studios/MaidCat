---
name: unreal-material
description: Playbook for Unreal Engine Material and Shader development. Covers material graph optimizations, parameter grouping, HLSL custom nodes, texture sampler limits, and shader permutation control.
---

# Unreal Material & Shader Playbook

This playbook outlines best practices, optimization rules, and common pitfalls for material and shader development in Unreal Engine 5.x.

---

## Instructions

### 1. Shader Permutations (Static Switches)
- **Do**: Limit `Static Switch Parameter` usage. Keep switches under 3-4 per master material.
- **Do**: Use dynamic branching (dynamic switch / lerp with scalar) if pixel shader instruction difference is minimal.
- **Don't**: Use static switches for simple runtime toggles (e.g., toggling a tint color).
- **Why**: Static switches compile new shader permutations ($2^N$). High permutations explode shader compile times, disk cache size, and cause runtime hitches.

### 2. Texture Sampler Limits
- **Do**: Set `Sampler Source` to `Shared: Wrap` or `Shared: Clamp` for all texture sample nodes in master materials.
- **Don't**: Leave `Sampler Source` as `From texture asset` (default).
- **Why**: Hardware samplers are limited to 16. Shared samplers bypass this limit, allowing up to 128 textures per material.

### 3. HLSL Custom Nodes
- **Do**: Use native Material Graph nodes whenever possible.
- **Do**: Use `#include` in Custom nodes to load external `.usf`/`.ush` shader files for complex logic.
- **Don't**: Write large inline HLSL code blocks directly in the Custom node text box.
- **Don't**: Use custom HLSL for simple mathematical operations that native nodes handle.
- **Why**: Custom HLSL blocks compiler optimizations (constant folding, loop unrolling) and often break cross-platform translation (Metal/Vulkan).

### 4. LWC / Large World Coordinates (UE 5.4+)
- **Do**: Feed world-space values (WorldPosition, CameraPosition, ObjectPosition) into Custom nodes via **Input pins**, not by referencing `Parameters.*` directly inside the HLSL body. The graph auto-demotes them to plain `float3` at the pin boundary.
- **Don't**: Assign `Parameters.WorldPosition_NoOffsets` (or any world-space `Parameters.*`) directly to a `float3` inside a Custom node.
- **Why**: Since UE 5.4, world coordinates are no longer plain `float3`. They are `FDFVector3` (Double-Float / DF type, the backend for Large World Coordinates). Direct assignment fails shader compilation with `cannot initialize a variable of type 'float3' with an lvalue of type 'FDFVector3'`, and the material silently falls back to the Default Material.
- **Fallback**: If you must reference it inside HLSL, demote explicitly: `float3 P = DFDemote(Parameters.WorldPosition_NoOffsets);` (legacy LWC macro: `LWCToFloat(...)`). `DFDemote` is a no-op on plain `float`, so it is always safe to wrap.

### 5. Vector Math & Clamping
- **Do**: Clamp `Dot Product` output using a `Saturate` node (free on GPU) when calculating diffuse or specular lighting.
- **Don't**: Pass unclamped dot products to exponential functions (like `Power`) or division nodes.
- **Why**: Negative dot products (faces pointing away from light) cause math instability, NaN pixels (black/white spots), or visual artifacts.

### 6. Overdraw & Translucency
- **Do**: Use `Masked` blend mode with `DitherTemporalAA` for transparent effects (hair, foliage) when rendering performance is critical.
- **Do**: Keep translucent pixel shader instruction count as low as possible.
- **Don't**: Use expensive translucent materials on large screen-space objects.
- **Why**: Translucency does not write depth, causing massive overdraw and pixel fill-rate bottlenecks.

### 7. UE5 Nanite & Substrate (Strata)
- **Do**: Keep `World Position Offset` (WPO) minimal on Nanite meshes and clamp max displacement distance.
- **Don't**: Use `Pixel Depth Offset` (PDO) or `Masked` blend mode on Nanite meshes unless essential.
- **Why**: PDO and Masked break Nanite's fast rasterization pipeline. Excessive WPO causes cluster tearing.
- **Do**: If Substrate is enabled, use `Substrate Slab` nodes efficiently. Do not over-layer material slabs as it increases shading cost.
- **Enforce Left-to-Right Layout**: Always arrange material graph nodes from left to right matching the data flow. Place source input nodes (e.g., UV, Time, Parameters) on the far left, custom HLSL/calculation nodes in the middle, and connect to the final material property input pins on the right (target material node is usually centered around X=0). Avoid placing calculation nodes to the right (X > 0) of the target node to prevent backward/crossed wire spaghetti.


---

## Gotchas & Pitfalls

### The $2^N$ Permutation Explosion
Adding static switches to a master material might seem convenient, but each switch doubles the permutations.
- 1 Master Material with 12 static switches = 4,096 shaders compiled per quality level/platform.
- **Fix**: Group common options into separate master materials rather than one "do-it-all" master material.

### Custom Node Compiler Failure on Consoles/Mobile
Custom HLSL nodes that compile fine on DX12 (Windows) often fail on Metal (iOS/macOS) or PlayStation/Switch due to strict compiler syntax or namespace differences.
- **Fix**: Always verify custom nodes on target non-Windows platforms. Keep code strictly conforming to standard HLSL.

### Material Expressions Property is Protected
- **Issue**: Attempting to read `material.get_editor_property("expressions")` to inspect or clean up nodes results in a python error: `Property is protected and cannot be read`.
- **Fix**: Never access `expressions` directly. To clear all nodes inside a material, always use the built-in function `unreal.MaterialEditingLibrary.delete_all_material_expressions(material)`.

### NaN (Not a Number) Black Pixels

Passing negative values into a `Power` node or taking `Square Root` of negative numbers results in `NaN`. These display as bright white or pitch black pixels that can corrupt post-processing.
- **Fix**: Always `Saturate` or `Clamp` the base input of any exponential/power calculations.

### LWC Type Mismatch in Custom Nodes (`FDFVector3`)

Referencing world-space `Parameters.*` (e.g. `WorldPosition_NoOffsets`, `WorldNormal`'s position basis, `CameraPosition`) directly inside a Custom node fails to compile on UE 5.4+:
```
LogShaderCompilers: Warning: Failed to compile Material for platform PCD3D_SM6, Default Material will be used in game.
/Engine/Generated/Material.ush:XXXX:X: error: cannot initialize a variable of type 'float3' with an lvalue of type 'FDFVector3'
```
The material then silently renders as the gray Default Material — easy to miss because there is no hard error, only a warning.
- **Root cause**: Large World Coordinates promotes world positions to the `FDFVector3` double-float struct.
- **Fix (preferred)**: Wire a `WorldPosition` graph node into a Custom node **Input pin** — the pin demotes it to `float3` automatically.
- **Fix (inline)**: `float3 P = DFDemote(Parameters.WorldPosition_NoOffsets);` (legacy: `LWCToFloat(...)`).

---

## Comparative Examples

### Texture Sampler Setup
#### Correct (Shared Sampler)
```
[Texture Sample Node]
  ├── Sampler Source: Shared: Wrap (Details Panel)
  └── UVs: [Texture Coordinate]
```
#### Incorrect (Unique Sampler - consumes 1 of 16 slots)
```
[Texture Sample Node]
  ├── Sampler Source: From texture asset
  └── UVs: [Texture Coordinate]
```

### Safe Math Operations
#### Correct (Safe Clamped Dot Product)
```hlsl
// In HLSL Custom Node:
float NdotL = saturate(dot(Normal, LightDir));
float Specular = pow(NdotL, Shininess);
```
Or in Material Graph:
`Dot Product` -> `Saturate` -> `Power`

#### Incorrect (Unsafe Dot Product - causes NaNs if Dot < 0)
```hlsl
// In HLSL Custom Node:
float NdotL = dot(Normal, LightDir);
float Specular = pow(NdotL, Shininess); // pow of negative base is NaN!
```
Or in Material Graph:
`Dot Product` -> `Power`

### World Position in a Custom Node (LWC-safe)
#### Correct (Input pin auto-demotes to float3)
```
[WorldPosition node] ──> Custom node Input pin "WorldPos" (float3)
```
```hlsl
// Inside the Custom node body — WorldPos is already a plain float3:
float height = WorldPos.z;
return height;
```
#### Correct (explicit demote when referencing Parameters directly)
```hlsl
float3 WorldPos = DFDemote(Parameters.WorldPosition_NoOffsets);
float height = WorldPos.z;
return height;
```
#### Incorrect (direct assignment — fails with FDFVector3 mismatch on UE 5.4+)
```hlsl
float3 WorldPos = Parameters.WorldPosition_NoOffsets; // FDFVector3 != float3 -> compile fail
```

### Custom HLSL USF Include
#### Correct (External USF File)
1. Store USF in project: `/Shaders/MyShader.usf`
2. Add Virtual Shader Path map in C++ or plugin startup.
3. In Custom Node text box:
```hlsl
#include "/Project/MyShader.usf"
return MyCustomFunction(Input1, Input2);
```
#### Incorrect (Inline Mess)
In Custom Node text box:
```hlsl
float3 Color = Input1;
for(int i=0; i<10; i++) {
    Color += CustomLogic(Input2, i);
}
return Color;
```
