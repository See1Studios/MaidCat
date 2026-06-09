// Interleaved Gradient Noise (Jimenez) - generates temporal noise pattern for TAA
// Returns a pseudo-random value [0,1] that varies per frame with 64-frame cycle
float IGN(float2 p) 
{
    p += float(View.FrameNumber % 64) * 5.588235;
    return frac(52.9829189 * frac(dot(p, float2(0.06711056, 0.00583715))));
}

// Temporal Dithered Blur - TAA friendly blur with golden angle sampling
float3 TemporalDitheredBlur(Texture2D Tex, float2 UV, float Radius, float2 Pos, int Samples)
{
    if (Samples <= 0) return Texture2DSample(Tex, View.MaterialTextureBilinearWrapedSampler, UV).rgb;
    
    float3 Color = 0;                                // Accumulated color
    float Dither = IGN(Pos);                         // Per-frame dither value (0~1)
    float Rot = Dither * 6.28318530718;              // Initial rotation offset (0~2π)
    float InvSamples = 1.0 / float(Samples);         // Inverse sample count (optimization)
    
    for (int i = 0; i < Samples; i++)
    {
        float t = (float(i) + Dither) * InvSamples;  // Dithered sample ratio (0~1)
        float a = float(i) * 2.39996323 + Rot;       // Sample angle (Golden angle)
        float r = Radius * sqrt(t);                  // Sample radius (uniform area distribution)
        Color += Texture2DSample(Tex, View.MaterialTextureBilinearWrapedSampler, UV + float2(cos(a), sin(a)) * r).rgb;
    }
    
    return Color * InvSamples;
}