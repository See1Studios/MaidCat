"""
Post Process Settings Serializer

PostProcessSettings 구조체를 Python dict로 직렬화/역직렬화하는 모듈입니다.

Key Features:
- PostProcessSettings 구조체 속성을 딕셔너리로 변환 (JSON 호환)
- 딕셔너리를 PostProcessSettings 구조체로 복원
- Post Process Volume 및 Camera Component 지원
- 타입별 직렬화 (Vector, LinearColor, Texture 등)

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
from typing import Optional, Dict, Any, List


class PostProcessSerializer:
    """Post Process 설정 직렬화/역직렬화 클래스"""
    
    # PostProcessSettings의 모든 editor property 이름들
    # (unreal.py 스텁 파일에서 확인 가능)
    # 
    # 주의: 일부 속성은 특정 언리얼 엔진 버전에서만 사용 가능합니다.
    # 직렬화/역직렬화 시 존재하지 않는 속성은 자동으로 건너뜁니다.
    PP_PROPERTIES: List[str] = [
        # Ambient Cubemap (UE 4.x+)
        "ambient_cubemap", "ambient_cubemap_intensity", "ambient_cubemap_tint",
        
        # Ambient Occlusion (UE 4.x+)
        "ambient_occlusion_bias", "ambient_occlusion_fade_distance", "ambient_occlusion_fade_radius",
        "ambient_occlusion_intensity", "ambient_occlusion_mip_blend", "ambient_occlusion_mip_scale",
        "ambient_occlusion_mip_threshold", "ambient_occlusion_power", "ambient_occlusion_quality",
        "ambient_occlusion_radius", "ambient_occlusion_radius_in_ws", "ambient_occlusion_static_fraction",
        "ambient_occlusion_temporal_blend_weight",
        
        # Auto Exposure (UE 4.x+)
        "auto_exposure_apply_physical_camera_exposure", "auto_exposure_bias", "auto_exposure_bias_curve",
        "auto_exposure_high_percent", "auto_exposure_low_percent", "auto_exposure_max_brightness",
        "auto_exposure_meter_mask", "auto_exposure_method", "auto_exposure_min_brightness",
        "auto_exposure_speed_down", "auto_exposure_speed_up",
        
        # Bloom (UE 4.x+)
        "bloom1_size", "bloom1_tint", "bloom2_size", "bloom2_tint", "bloom3_size", "bloom3_tint",
        "bloom4_size", "bloom4_tint", "bloom5_size", "bloom5_tint", "bloom6_size", "bloom6_tint",
        "bloom_convolution_buffer_scale", "bloom_convolution_center_uv", "bloom_convolution_intensity",
        "bloom_convolution_pre_filter_max", "bloom_convolution_pre_filter_min", "bloom_convolution_pre_filter_mult",
        "bloom_convolution_scatter_dispersion", "bloom_convolution_size", "bloom_convolution_texture",
        "bloom_dirt_mask", "bloom_dirt_mask_intensity", "bloom_dirt_mask_tint",
        "bloom_gaussian_intensity", "bloom_intensity", "bloom_method", "bloom_size_scale", "bloom_threshold",
        
        # Color Grading (UE 4.x+)
        "blue_correction", "color_contrast", "color_contrast_highlights", "color_contrast_midtones",
        "color_contrast_shadows", "color_correction_highlights_max", "color_correction_highlights_min",
        "color_correction_shadows_max", "color_gain", "color_gain_highlights", "color_gain_midtones",
        "color_gain_shadows", "color_gamma", "color_gamma_highlights", "color_gamma_midtones",
        "color_gamma_shadows", "color_grading_intensity", "color_grading_lut", "color_offset",
        "color_offset_highlights", "color_offset_midtones", "color_offset_shadows", "color_saturation",
        "color_saturation_highlights", "color_saturation_midtones", "color_saturation_shadows",
        
        # Camera (UE 4.x+)
        "camera_iso", "camera_shutter_speed", "chromatic_aberration_start_offset",
        
        # Depth of Field (UE 4.x+)
        "depth_of_field_aspect_ratio_scalar", "depth_of_field_barrel_length", "depth_of_field_barrel_radius",
        "depth_of_field_blade_count", "depth_of_field_depth_blur_amount", "depth_of_field_depth_blur_radius",
        "depth_of_field_far_blur_size", "depth_of_field_far_transition_region", "depth_of_field_focal_distance",
        "depth_of_field_focal_region", "depth_of_field_fstop", "depth_of_field_min_fstop",
        "depth_of_field_near_blur_size", "depth_of_field_near_transition_region", "depth_of_field_occlusion",
        "depth_of_field_petzval_bokeh", "depth_of_field_petzval_bokeh_falloff",
        "depth_of_field_petzval_exclusion_box_extents", "depth_of_field_petzval_exclusion_box_radius",
        "depth_of_field_scale", "depth_of_field_sensor_width", "depth_of_field_sky_focus_distance",
        "depth_of_field_squeeze_factor", "depth_of_field_use_hair_depth", "depth_of_field_vignette_size",
        
        # Dynamic Global Illumination (UE 5.0+)
        "dynamic_global_illumination_method", "expand_gamut",
        
        # Film (UE 4.x+)
        "film_black_clip", "film_grain_highlights_max", "film_grain_highlights_min", "film_grain_intensity",
        "film_grain_intensity_highlights", "film_grain_intensity_midtones", "film_grain_intensity_shadows",
        "film_grain_shadows_max", "film_grain_texel_size", "film_grain_texture", "film_shoulder",
        "film_slope", "film_toe", "film_white_clip",
        
        # Histogram (UE 4.x+)
        "histogram_log_max", "histogram_log_min",
        
        # Indirect Lighting (UE 4.x+)
        "indirect_lighting_color", "indirect_lighting_intensity",
        
        # Lens Flare (UE 4.x+)
        "lens_flare_bokeh_shape", "lens_flare_bokeh_size", "lens_flare_intensity", "lens_flare_threshold",
        "lens_flare_tint", "lens_flare_tints",
        
        # Local Exposure (UE 5.0+)
        "local_exposure_blurred_luminance_blend", "local_exposure_blurred_luminance_kernel_size_percent",
        "local_exposure_detail_strength", "local_exposure_highlight_contrast_curve",
        "local_exposure_highlight_contrast_scale", "local_exposure_highlight_threshold",
        "local_exposure_highlight_threshold_strength", "local_exposure_method", "local_exposure_middle_grey_bias",
        "local_exposure_shadow_contrast_curve", "local_exposure_shadow_contrast_scale",
        "local_exposure_shadow_threshold", "local_exposure_shadow_threshold_strength",
        
        # Lumen (UE 5.0+)
        "lumen_diffuse_color_boost", "lumen_final_gather_lighting_update_speed", "lumen_final_gather_quality",
        "lumen_final_gather_screen_traces", "lumen_front_layer_translucency_reflections",
        "lumen_full_skylight_leaking_distance", "lumen_max_reflection_bounces", "lumen_max_refraction_bounces",
        "lumen_max_roughness_to_trace_reflections", "lumen_max_trace_distance", "lumen_ray_lighting_mode",
        "lumen_reflection_quality", "lumen_reflections_screen_traces", "lumen_scene_detail",
        "lumen_scene_lighting_quality", "lumen_scene_lighting_update_speed", "lumen_scene_view_distance",
        "lumen_skylight_leaking", "lumen_skylight_leaking_tint", "lumen_surface_cache_resolution",
        
        # Motion Blur (UE 4.x+)
        "motion_blur_amount", "motion_blur_max", "motion_blur_per_object_size", "motion_blur_target_fps",
        
        # Path Tracing (UE 5.0+)
        "path_tracing_enable_denoiser", "path_tracing_enable_emissive_materials",
        "path_tracing_enable_reference_atmosphere", "path_tracing_enable_reference_dof",
        "path_tracing_include_diffuse", "path_tracing_include_emissive", "path_tracing_include_indirect_diffuse",
        "path_tracing_include_indirect_specular", "path_tracing_include_indirect_volume",
        "path_tracing_include_specular", "path_tracing_include_volume", "path_tracing_max_bounces",
        "path_tracing_max_path_intensity", "path_tracing_samples_per_pixel",
        
        # Ray Tracing (UE 4.22+)
        "ray_tracing_ao", "ray_tracing_ao_intensity", "ray_tracing_ao_radius", "ray_tracing_ao_samples_per_pixel",
        "ray_tracing_gi", "ray_tracing_gi_max_bounces", "ray_tracing_gi_samples_per_pixel",
        "ray_tracing_translucency_max_roughness", "ray_tracing_translucency_refraction",
        "ray_tracing_translucency_refraction_rays", "ray_tracing_translucency_samples_per_pixel",
        "ray_tracing_translucency_shadows",
        
        # Reflection (UE 4.x+)
        "reflection_method", "screen_space_reflection_intensity", "screen_space_reflection_max_roughness",
        "screen_space_reflection_quality",
        
        # Scene (UE 4.x+)
        "scene_color_tint", "scene_fringe_intensity",
        
        # Tone Mapping (UE 4.x+)
        "sharpen", "temperature_type", "tone_curve_amount", "white_temp", "white_tint",
        
        # Translucency (UE 4.x+)
        "translucency_type",
        
        # Vignette (UE 4.x+)
        "vignette_intensity",
        
        # Weighted Blendables (UE 4.x+)
        "weighted_blendables",
    ]
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """
        값을 JSON 직렬화 가능한 형태로 변환
        
        Args:
            value: 변환할 값
            
        Returns:
            직렬화된 값
        """
        # None
        if value is None:
            return None
        
        # Linear Color
        if isinstance(value, unreal.LinearColor):
            return {
                "type": "LinearColor",
                "r": value.r,
                "g": value.g,
                "b": value.b,
                "a": value.a
            }
        
        # Vector
        if isinstance(value, unreal.Vector):
            return {
                "type": "Vector",
                "x": value.x,
                "y": value.y,
                "z": value.z
            }
        
        # Vector2D
        if isinstance(value, unreal.Vector2D):
            return {
                "type": "Vector2D",
                "x": value.x,
                "y": value.y
            }
        
        # Vector4
        if isinstance(value, unreal.Vector4):
            return {
                "type": "Vector4",
                "x": value.x,
                "y": value.y,
                "z": value.z,
                "w": value.w
            }
        
        # Texture (애셋 참조는 경로로 저장)
        if isinstance(value, unreal.Texture):
            return {
                "type": "Texture",
                "path": value.get_path_name()
            }
        
        # CurveFloat (애셋 참조는 경로로 저장)
        if isinstance(value, unreal.CurveFloat):
            return {
                "type": "CurveFloat",
                "path": value.get_path_name()
            }
        
        # Enum
        if isinstance(value, unreal.EnumBase):
            return {
                "type": "Enum",
                "value": value.value
            }
        
        # WeightedBlendables (블렌더블 머티리얼 배열)
        # 복잡한 구조이므로 메타데이터만 저장
        if hasattr(value, '__class__') and value.__class__.__name__ == 'WeightedBlendables':
            return {
                "type": "WeightedBlendables",
                "note": "WeightedBlendables는 복잡하여 저장하지 않음"
            }
        
        # Array 타입 (list, tuple, FixedArray 등)
        if isinstance(value, (list, tuple)):
            return {
                "type": "Array",
                "items": [PostProcessSerializer._serialize_value(item) for item in value]
            }
        
        # FixedArray (언리얼 고정 크기 배열)
        # hasattr로 체크하여 FixedArray 여부 확인
        if hasattr(value, '__iter__') and hasattr(value, '__len__'):
            try:
                # FixedArray는 iterable이므로 리스트로 변환
                items = [PostProcessSerializer._serialize_value(item) for item in value]
                return {
                    "type": "Array",
                    "items": items
                }
            except:
                pass
        
        # 기본 타입 (int, float, bool, str)
        return value
    
    @staticmethod
    def _deserialize_value(data: Any) -> Any:
        """
        직렬화된 값을 원래 타입으로 복원
        
        Args:
            data: 직렬화된 데이터
            
        Returns:
            복원된 값
        """
        if data is None:
            return None
        
        # 딕셔너리 타입 체크
        if not isinstance(data, dict):
            return data
        
        value_type = data.get("type")
        
        if value_type == "LinearColor":
            return unreal.LinearColor(data["r"], data["g"], data["b"], data["a"])
        
        if value_type == "Vector":
            return unreal.Vector(data["x"], data["y"], data["z"])
        
        if value_type == "Vector2D":
            return unreal.Vector2D(data["x"], data["y"])
        
        if value_type == "Vector4":
            return unreal.Vector4(data["x"], data["y"], data["z"], data["w"])
        
        if value_type == "Texture":
            # 애셋 로드
            path = data.get("path")
            if path:
                return unreal.load_asset(path)
            return None
        
        if value_type == "CurveFloat":
            # 애셋 로드
            path = data.get("path")
            if path:
                return unreal.load_asset(path)
            return None
        
        if value_type == "Enum":
            # Enum 값 반환 (타입 정보가 없으므로 int로 반환)
            return data.get("value")
        
        if value_type == "Array":
            # Array 복원
            items = data.get("items", [])
            return [PostProcessSerializer._deserialize_value(item) for item in items]
        
        if value_type == "WeightedBlendables":
            # WeightedBlendables는 복원하지 않음 (블렌더블 머티리얼은 복잡함)
            # 빈 WeightedBlendables 반환
            return None
        
        return data
    
    @staticmethod
    def get_camera_component(actor: unreal.Actor) -> Optional[unreal.CameraComponent]:
        """
        Actor에서 Camera Component 찾기
        
        Args:
            actor: 검색할 Actor
            
        Returns:
            Camera Component (없으면 None)
        """
        if not actor:
            return None
        
        # CameraActor의 경우
        if isinstance(actor, unreal.CameraActor):
            return actor.get_editor_property("camera_component")
        
        # 일반 Actor의 경우 컴포넌트 검색
        components = actor.get_components_by_class(unreal.CameraComponent.static_class())
        if components and len(components) > 0:
            return components[0]
        
        return None
    
    @staticmethod
    def serialize_post_process_settings(
        settings: unreal.PostProcessSettings
    ) -> Optional[Dict[str, Any]]:
        """
        PostProcessSettings 구조체를 딕셔너리로 직렬화
        
        Args:
            settings: PostProcessSettings 구조체
            
        Returns:
            딕셔너리 (실패시 None)
        """
        try:
            data = {}
            success_count = 0
            skip_count = 0
            
            # 모든 속성 직렬화
            for prop_name in PostProcessSerializer.PP_PROPERTIES:
                try:
                    value = settings.get_editor_property(prop_name)
                    data[prop_name] = PostProcessSerializer._serialize_value(value)
                    success_count += 1
                except Exception as e:
                    # 속성이 없거나 접근할 수 없는 경우 (버전 차이 등)
                    # 디버그 모드에서만 경고 출력
                    skip_count += 1
                    # unreal.log_warning(f"속성 '{prop_name}' 직렬화 건너뜀: {e}")
                    continue
            
            unreal.log(f"✅ PostProcessSettings 직렬화 성공: {success_count}개 속성, {skip_count}개 건너뜀")
            return data
                
        except Exception as e:
            unreal.log_error(f"PostProcessSettings 직렬화 중 예외 발생: {e}")
            return None
    
    @staticmethod
    def deserialize_post_process_settings(
        data: Dict[str, Any]
    ) -> Optional[unreal.PostProcessSettings]:
        """
        딕셔너리를 PostProcessSettings 구조체로 역직렬화
        
        Args:
            data: 직렬화된 딕셔너리
            
        Returns:
            PostProcessSettings 구조체 (실패시 None)
        """
        try:
            settings = unreal.PostProcessSettings()
            success_count = 0
            skip_count = 0
            
            # 모든 속성 복원
            for prop_name, value_data in data.items():
                try:
                    value = PostProcessSerializer._deserialize_value(value_data)
                    settings.set_editor_property(prop_name, value)
                    success_count += 1
                except Exception as e:
                    # 속성이 없거나 설정할 수 없는 경우 (버전 차이 등)
                    # 디버그 모드에서만 경고 출력
                    skip_count += 1
                    # unreal.log_warning(f"속성 '{prop_name}' 역직렬화 건너뜀: {e}")
                    continue
            
            unreal.log(f"✅ PostProcessSettings 역직렬화 성공: {success_count}개 속성, {skip_count}개 건너뜀")
            return settings
                
        except Exception as e:
            unreal.log_error(f"PostProcessSettings 역직렬화 중 예외 발생: {e}")
            return None
    
    @staticmethod
    def serialize_post_process_volume(
        volume: unreal.PostProcessVolume
    ) -> Optional[Dict[str, Any]]:
        """
        Post Process Volume을 JSON 직렬화 가능한 딕셔너리로 변환
        
        Args:
            volume: Post Process Volume
            
        Returns:
            직렬화된 데이터 딕셔너리 (실패시 None)
        """
        try:
            settings = volume.get_editor_property("settings")
            if not settings:
                unreal.log_error("Volume의 PostProcessSettings를 가져올 수 없음")
                return None
            
            # PostProcessSettings 직렬화
            settings_dict = PostProcessSerializer.serialize_post_process_settings(settings)
            if not settings_dict:
                return None
            
            # 메타데이터 추가
            data = {
                "type": "volume",
                "name": volume.get_name(),
                "settings": settings_dict,
                "metadata": {
                    "priority": volume.get_editor_property("priority"),
                    "blend_radius": volume.get_editor_property("blend_radius"),
                    "blend_weight": volume.get_editor_property("blend_weight"),
                    "enabled": volume.get_editor_property("enabled")
                }
            }
            
            return data
            
        except Exception as e:
            unreal.log_error(f"Post Process Volume 직렬화 실패: {e}")
            return None
    
    @staticmethod
    def deserialize_post_process_volume(
        volume: unreal.PostProcessVolume,
        data: Dict[str, Any]
    ) -> bool:
        """
        직렬화된 데이터를 Post Process Volume에 적용
        
        Args:
            volume: 대상 Post Process Volume
            data: 직렬화된 데이터 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            # 딕셔너리에서 PostProcessSettings 복원
            settings_dict = data.get("settings")
            if not settings_dict:
                unreal.log_error("settings 필드를 찾을 수 없음")
                return False
            
            settings = PostProcessSerializer.deserialize_post_process_settings(settings_dict)
            if not settings:
                return False
            
            # Volume에 설정 적용
            volume.set_editor_property("settings", settings)
            
            # 메타데이터 적용 (선택사항)
            metadata = data.get("metadata", {})
            if metadata:
                if "priority" in metadata:
                    volume.set_editor_property("priority", metadata["priority"])
                if "blend_radius" in metadata:
                    volume.set_editor_property("blend_radius", metadata["blend_radius"])
                if "blend_weight" in metadata:
                    volume.set_editor_property("blend_weight", metadata["blend_weight"])
                if "enabled" in metadata:
                    volume.set_editor_property("enabled", metadata["enabled"])
            
            unreal.log(f"✅ Post Process Volume 역직렬화 성공: {volume.get_name()}")
            return True
            
        except Exception as e:
            unreal.log_error(f"Post Process Volume 역직렬화 실패: {e}")
            return False
    
    @staticmethod
    def serialize_camera_post_process(
        camera: unreal.CameraComponent
    ) -> Optional[Dict[str, Any]]:
        """
        Camera Component의 Post Process 설정을 직렬화
        
        Args:
            camera: Camera Component
            
        Returns:
            직렬화된 데이터 딕셔너리 (실패시 None)
        """
        try:
            settings = camera.get_editor_property("post_process_settings")
            if not settings:
                unreal.log_error("Camera의 PostProcessSettings를 가져올 수 없음")
                return None
            
            # PostProcessSettings 직렬화
            settings_dict = PostProcessSerializer.serialize_post_process_settings(settings)
            if not settings_dict:
                return None
            
            # 메타데이터 추가
            actor = camera.get_owner()
            data = {
                "type": "camera",
                "camera_name": camera.get_name(),
                "actor_name": actor.get_name() if actor else "UnknownActor",
                "settings": settings_dict,
                "metadata": {
                    "post_process_blend_weight": camera.get_editor_property("post_process_blend_weight")
                }
            }
            
            return data
            
        except Exception as e:
            unreal.log_error(f"Camera Post Process 직렬화 실패: {e}")
            return None
    
    @staticmethod
    def deserialize_camera_post_process(
        camera: unreal.CameraComponent,
        data: Dict[str, Any]
    ) -> bool:
        """
        직렬화된 데이터를 Camera Component에 적용
        
        Args:
            camera: 대상 Camera Component
            data: 직렬화된 데이터 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            # 딕셔너리에서 PostProcessSettings 복원
            settings_dict = data.get("settings")
            if not settings_dict:
                unreal.log_error("settings 필드를 찾을 수 없음")
                return False
            
            settings = PostProcessSerializer.deserialize_post_process_settings(settings_dict)
            if not settings:
                return False
            
            # Camera에 설정 적용
            camera.set_editor_property("post_process_settings", settings)
            
            # 메타데이터 적용 (선택사항)
            metadata = data.get("metadata", {})
            if metadata and "post_process_blend_weight" in metadata:
                camera.set_editor_property("post_process_blend_weight", metadata["post_process_blend_weight"])
            
            actor = camera.get_owner()
            actor_name = actor.get_name() if actor else "UnknownActor"
            unreal.log(f"✅ Camera Post Process 역직렬화 성공: {actor_name}.{camera.get_name()}")
            return True
            
        except Exception as e:
            unreal.log_error(f"Camera Post Process 역직렬화 실패: {e}")
            return False


# 사용 예제
if __name__ == "__main__":
    """
    예제: 선택된 Post Process Volume 또는 Camera Actor 처리
    """
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    
    if not selected_actors:
        print("⚠️  Post Process Volume 또는 Camera Actor를 선택하고 실행하세요.")
    
    for actor in selected_actors:
        print(f"\n{'='*60}")
        print(f"Actor: {actor.get_name()} ({actor.__class__.__name__})")
        print(f"{'='*60}")
        
        # Post Process Volume 처리
        if isinstance(actor, unreal.PostProcessVolume):
            print("🔍 Post Process Volume 감지")
            
            # 직렬화
            data = PostProcessSerializer.serialize_post_process_volume(actor)
            if data:
                print(f"✅ 직렬화 성공")
                print(f"   - Type: {data['type']}")
                print(f"   - Name: {data['name']}")
                print(f"   - Settings Count: {len(data['settings'])} 속성")
                print(f"   - Metadata: {data['metadata']}")
                
                # 역직렬화 테스트 (동일한 Volume에 다시 적용)
                success = PostProcessSerializer.deserialize_post_process_volume(actor, data)
                if success:
                    print(f"✅ 역직렬화 테스트 성공")
            
        # Camera Component 찾기 및 처리
        camera = PostProcessSerializer.get_camera_component(actor)
        if camera:
            print(f"🔍 Camera Component 감지: {camera.get_name()}")
            
            # 직렬화
            data = PostProcessSerializer.serialize_camera_post_process(camera)
            if data:
                print(f"✅ 직렬화 성공")
                print(f"   - Type: {data['type']}")
                print(f"   - Actor: {data['actor_name']}")
                print(f"   - Camera: {data['camera_name']}")
                print(f"   - Settings Count: {len(data['settings'])} 속성")
                print(f"   - Metadata: {data['metadata']}")
                
                # 역직렬화 테스트 (동일한 Camera에 다시 적용)
                success = PostProcessSerializer.deserialize_camera_post_process(camera, data)
                if success:
                    print(f"✅ 역직렬화 테스트 성공")
        
        # 다른 타입의 Actor인 경우
        if not isinstance(actor, unreal.PostProcessVolume) and not camera:
            print(f"⚠️  {actor.__class__.__name__}은 Post Process 설정을 지원하지 않습니다.")
    
    print(f"\n{'='*80}")
    print(f"📘 PostProcessSerializer API 사용법")
    print(f"{'='*80}")
    print(f"1. PostProcessSettings 직렬화:")
    print(f"   data_dict = PostProcessSerializer.serialize_post_process_settings(settings)")
    print(f"")
    print(f"2. PostProcessSettings 역직렬화:")
    print(f"   settings = PostProcessSerializer.deserialize_post_process_settings(data_dict)")
    print(f"")
    print(f"3. Post Process Volume 직렬화:")
    print(f"   data = PostProcessSerializer.serialize_post_process_volume(volume)")
    print(f"")
    print(f"4. Post Process Volume 역직렬화:")
    print(f"   success = PostProcessSerializer.deserialize_post_process_volume(volume, data)")
    print(f"")
    print(f"5. Camera Post Process 직렬화:")
    print(f"   data = PostProcessSerializer.serialize_camera_post_process(camera)")
    print(f"")
    print(f"6. Camera Post Process 역직렬화:")
    print(f"   success = PostProcessSerializer.deserialize_camera_post_process(camera, data)")
    print(f"")
    print(f"7. Camera Component 찾기:")
    print(f"   camera = PostProcessSerializer.get_camera_component(actor)")
    print(f"")
    print(f"💡 직렬화 방식:")
    print(f"   - PostProcessSettings 구조체의 모든 속성을 Python dict로 변환")
    print(f"   - Vector, LinearColor, Texture 등 복합 타입은 딕셔너리로 변환")
    print(f"   - JSON으로 저장 가능한 형태로 직렬화")
    print(f"   - 역직렬화 시 원래 타입으로 복원")
    print(f"{'='*80}")

