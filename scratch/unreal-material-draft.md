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

### 4. Vector Math & Clamping
- **Do**: Clamp `Dot Product` output using a `Saturate` node (free on GPU) when calculating diffuse or specular lighting.
- **Don't**: Pass unclamped dot products to exponential functions (like `Power`) or division nodes.
- **Why**: Negative dot products (faces pointing away from light) cause math instability, NaN pixels (black/white spots), or visual artifacts.

### 5. Overdraw & Translucency
- **Do**: Use `Masked` blend mode with `DitherTemporalAA` for transparent effects (hair, foliage) when rendering performance is critical.
- **Do**: Keep translucent pixel shader instruction count as low as possible.
- **Don't**: Use expensive translucent materials on large screen-space objects.
- **Why**: Translucency does not write depth, causing massive overdraw and pixel fill-rate bottlenecks.

### 6. UE5 Nanite & Substrate (Strata)
- **Do**: Keep `World Position Offset` (WPO) minimal on Nanite meshes and clamp max displacement distance.
- **Don't**: Use `Pixel Depth Offset` (PDO) or `Masked` blend mode on Nanite meshes unless essential.
- **Why**: PDO and Masked break Nanite's fast rasterization pipeline. Excessive WPO causes cluster tearing.
- **Do**: If Substrate is enabled, use `Substrate Slab` nodes efficiently. Do not over-layer material slabs as it increases shading cost.

---

## Gotchas & Pitfalls

### The $2^N$ Permutation Explosion
Adding static switches to a master material might seem convenient, but each switch doubles the permutations.
- 1 Master Material with 12 static switches = 4,096 shaders compiled per quality level/platform.
- **Fix**: Group common options into separate master materials rather than one "do-it-all" master material.

### Custom Node Compiler Failure on Consoles/Mobile
Custom HLSL nodes that compile fine on DX12 (Windows) often fail on Metal (iOS/macOS) or PlayStation/Switch due to strict compiler syntax or namespace differences.
- **Fix**: Always verify custom nodes on target non-Windows platforms. Keep code strictly conforming to standard HLSL.

### NaN (Not a Number) Black Pixels
Passing negative values into a `Power` node or taking `Square Root` of negative numbers results in `NaN`. These display as bright white or pitch black pixels that can corrupt post-processing.
- **Fix**: Always `Saturate` or `Clamp` the base input of any exponential/power calculations.

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
