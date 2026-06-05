import unreal
import sys
import time

# Try to find selected Material or MaterialFunction in Content Browser
selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

target_asset = None
for asset in selected_assets:
    if isinstance(asset, (unreal.Material, unreal.MaterialFunction)):
        target_asset = asset
        break

if not target_asset:
    print("ERROR: No Material or MaterialFunction selected in the Content Browser!")
    print("Please select your target Material or Material Function in the Content Browser first, then try again.")
    sys.exit(1)

print(f"Target asset found: {target_asset.get_name()} ({target_asset.__class__.__name__})")

# HLSL code to inject
hlsl_code = """struct SDFHelper
{
    float hash(uint n) {
        n = (n << 13u) ^ n;
        n = n * (n * n * 15731u + 789221u) + 1376312589u;
        return float(n & 0x7fffffffu) / 2147483647.0;
    }
    float smin(float a, float b, float k, out float h) {
        h = saturate(0.5 + 0.5 * (b - a) / k);
        return lerp(b, a, h) - k * h * (1.0 - h);
    }
    float EvaluateEllipse(float2 localPos, float size, float2 aspectScale,
                          float speed, float invSpeedStretch, float speedStretch,
                          out float3 normal)
    {
        float absSpeed = abs(speed);
        float normalizedSpeed = saturate((absSpeed - 0.1) * invSpeedStretch);
        float stretchFactor = lerp(1.0, speedStretch, normalizedSpeed);

        float2 scale = float2(1.0 / stretchFactor, stretchFactor) * aspectScale;

        float2 scaledPos = localPos * scale;
        float dist = length(scaledPos) - size;

        float corrSize = size + 0.01;
        float z_sq = corrSize * corrSize - dot(scaledPos, scaledPos);
        normal = float3(scaledPos / scale, sqrt(max(0.0, z_sq)));

        return dist;
    }
};

SDFHelper Helper;

// ========== Stage 1: Viewport → flowPos ==========
float2 worldPos = UV - 0.5;
worldPos.x *= AspectRatio;

float2 flowDir = normalize(FlowDirection);
float2 flowPos = float2(
     worldPos.x * flowDir.x + worldPos.y * flowDir.y,
    -worldPos.x * flowDir.y + worldPos.y * flowDir.x
);

// ========== Pre-compute ==========
int num_particles = clamp(int(NumParticles), 0, 100);
if (num_particles <= 0) {
    return float4(0, 0, 1, 0);
}

float sizeMin = 1.0 - SizeVariation;
float sizeMax = 1.0 + SizeVariation;
float speedMin = 1.0 - SpeedVariation;
float speedMax = 1.0 + SpeedVariation;

float halfDomainX  = max(0.001, DomainWidth)  * 0.5;
float halfDomainY  = max(0.001, DomainHeight) * 0.5;
float domainX      = halfDomainX * 2.0;
float domainY      = halfDomainY * 2.0;
float invDomainX   = 1.0 / domainX;
float invDomainY   = 1.0 / domainY;

float smoothnessK     = max(0.001, Smoothness);
float gameTime        = ResolvedView.GameTime + TimeOffset;
float invSpeedStretch = 1.0 / max(0.001, SpeedStretch);
float2 aspectScale    = ParticleAspect >= 1.0
    ? float2(1.0, 1.0 / ParticleAspect)
    : float2(ParticleAspect, 1.0);

// ========== flowPos → 도메인 래핑 ==========
float2 tiledPos = float2(
    frac(flowPos.x * invDomainX) * domainX - halfDomainX,
    frac(flowPos.y * invDomainY) * domainY - halfDomainY
);

float finalDist    = 1e6;
float3 finalNormal = float3(0, 0, 1);

for (int i = 1; i <= num_particles; i++) {
    uint ui = uint(i);

    // ========== Spawn ==========
    float h_pos_x = Helper.hash(ui * 2u);
    float h_pos_y = Helper.hash(ui * 3u);
    float h_speed = Helper.hash(ui * 5u);
    float h_size  = Helper.hash(ui * 17u);
    float h_time  = Helper.hash(ui * 23u);

    float speed = FlowSpeed * lerp(speedMin, speedMax, h_speed);
    float size  = ParticleSize * lerp(sizeMin, sizeMax, h_size);

    // 스폰 위치: 도메인 기준
    float spawnX = lerp(-halfDomainX, halfDomainX, h_pos_x);
    float spawnY = lerp(-halfDomainY, halfDomainY, h_pos_y);

    // ========== Animate ==========
    float animX    = spawnX + (gameTime + h_time * TimeOffset) * speed;
    float wrappedX = frac(animX * invDomainX) * domainX - halfDomainX;

    float2 localPos = tiledPos - float2(wrappedX, spawnY);

    // 경계 처리
    localPos.x += localPos.x > halfDomainX ? -domainX :
                  (localPos.x < -halfDomainX ? domainX : 0.0);
    localPos.y += localPos.y > halfDomainY ? -domainY :
                  (localPos.y < -halfDomainY ? domainY : 0.0);

    // ========== Shape ==========
    float3 normal;
    float dist = Helper.EvaluateEllipse(localPos, size, aspectScale,
                                        speed, invSpeedStretch, SpeedStretch, normal);

    // ========== Blend ==========
    float h;
    finalDist   = Helper.smin(finalDist, dist, smoothnessK, h);
    finalNormal = lerp(normal, finalNormal, h);
}

// ========== Stage 3: Output ==========
finalNormal = normalize(finalNormal);
float2 restoredNormal = float2(
    finalNormal.x * flowDir.x - finalNormal.y * flowDir.y,
    finalNormal.x * flowDir.y + finalNormal.x * flowDir.x
);
return float4(restoredNormal, finalNormal.z, finalDist);"""

# Create custom node
if isinstance(target_asset, unreal.Material):
    custom_node = unreal.MaterialEditingLibrary.create_material_expression(target_asset, unreal.MaterialExpressionCustom, node_pos_x=-400, node_pos_y=-100)
else:
    custom_node = unreal.MaterialEditingLibrary.create_material_expression_in_function(target_asset, unreal.MaterialExpressionCustom, node_pos_x=-400, node_pos_y=-100)

custom_node.set_editor_property('code', hlsl_code)
custom_node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT4)
custom_node.set_editor_property('description', 'FlowSDFParticles')
custom_node.set_editor_property('desc', 'SDF-based Flowing Particle system')

# Set inputs
inputs = []
input_names = [
    "UV", "AspectRatio", "FlowDirection", "NumParticles",
    "DomainWidth", "DomainHeight", "FlowSpeed", "SizeVariation",
    "SpeedVariation", "TimeOffset", "ParticleSize", "ParticleAspect",
    "SpeedStretch", "Smoothness"
]
for name in input_names:
    ci = unreal.CustomInput()
    ci.set_editor_property('input_name', name)
    inputs.append(ci)
custom_node.set_editor_property('inputs', inputs)

if isinstance(target_asset, unreal.Material):
    unreal.MaterialEditingLibrary.layout_material_expressions(target_asset)
else:
    unreal.MaterialEditingLibrary.update_material_function(target_asset)

# Programmatically close and reopen editor to force UI repaint
editor_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
editor_subsystem.close_all_editors_for_asset(target_asset)
time.sleep(0.1)
editor_subsystem.open_editor_for_assets([target_asset])

print("SUCCESS: Custom node added and editor refreshed successfully!")
