"""
Post Process Preset Manager 테스트

PostProcessPresetManager의 모든 기능을 테스트합니다.
- Volume 프리셋 저장/로드
- Camera 프리셋 저장/로드
- 공통 프리셋 저장/로드
- 프리셋 목록 조회
- 프리셋 삭제

사용법:
1. 레벨에 Post Process Volume 또는 Camera Actor를 배치
2. Post Process Settings를 원하는 대로 설정
3. 해당 Actor를 선택
4. 이 스크립트를 실행 (Ctrl+Enter)

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
import importlib

# 모듈 리로드
try:
    import tool.pp_preset as pp_preset_module
    importlib.reload(pp_preset_module)
    from tool.pp_preset import PostProcessPresetManager
except ImportError:
    try:
        import pp_preset as pp_preset_module
        importlib.reload(pp_preset_module)
        from pp_preset import PostProcessPresetManager
    except ImportError:
        unreal.log_error("PostProcessPresetManager import 실패")
        raise


class PPPresetTester:
    """Post Process Preset Manager 테스트 클래스"""
    
    def __init__(self):
        self.editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """테스트 결과 로깅"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        unreal.log(f"{status} | {test_name} | {message}")
        
    def print_separator(self, title: str = ""):
        """구분선 출력"""
        if title:
            unreal.log(f"\n{'='*80}")
            unreal.log(f"  {title}")
            unreal.log(f"{'='*80}")
        else:
            unreal.log(f"{'='*80}")
    
    def test_volume_preset_save_load(self, volume: unreal.PostProcessVolume):
        """Post Process Volume 프리셋 저장/로드 테스트"""
        self.print_separator("Test: Volume 프리셋 저장/로드")
        
        preset_name = "test_volume_preset"
        
        # 저장 테스트
        unreal.log("📝 1단계: Volume 프리셋 저장...")
        file_path = PostProcessPresetManager.save_volume_preset(volume, preset_name)
        self.log_test(
            "Volume 프리셋 저장",
            file_path is not None,
            f"경로: {file_path}" if file_path else "저장 실패"
        )
        
        if not file_path:
            return False
        
        # 현재 설정 백업 (비교용)
        original_settings = volume.get_editor_property("settings")
        original_bloom_intensity = original_settings.get_editor_property("bloom_intensity")
        
        # 설정 변경 (로드 테스트 전에 값을 바꿔봄)
        unreal.log("🔄 2단계: Volume 설정 변경...")
        modified_settings = volume.get_editor_property("settings")
        modified_settings.set_editor_property("bloom_intensity", 99.0)
        volume.set_editor_property("settings", modified_settings)
        
        # 로드 테스트
        unreal.log("📂 3단계: Volume 프리셋 로드...")
        success = PostProcessPresetManager.load_volume_preset(volume, preset_name)
        self.log_test(
            "Volume 프리셋 로드",
            success,
            "로드 성공" if success else "로드 실패"
        )
        
        if not success:
            return False
        
        # 설정 복원 확인
        restored_settings = volume.get_editor_property("settings")
        restored_bloom_intensity = restored_settings.get_editor_property("bloom_intensity")
        
        restoration_success = abs(restored_bloom_intensity - original_bloom_intensity) < 0.01
        self.log_test(
            "Volume 설정 복원 검증",
            restoration_success,
            f"원본: {original_bloom_intensity:.2f}, 복원: {restored_bloom_intensity:.2f}"
        )
        
        # 프리셋 목록 테스트
        unreal.log("📋 4단계: Volume 프리셋 목록 조회...")
        presets = PostProcessPresetManager.list_volume_presets(volume)
        list_success = preset_name in presets
        self.log_test(
            "Volume 프리셋 목록 조회",
            list_success,
            f"목록: {presets}"
        )
        
        # 삭제 테스트
        unreal.log("🗑️  5단계: Volume 프리셋 삭제...")
        delete_success = PostProcessPresetManager.delete_volume_preset(volume, preset_name)
        self.log_test(
            "Volume 프리셋 삭제",
            delete_success,
            "삭제 성공" if delete_success else "삭제 실패"
        )
        
        return True
    
    def test_camera_preset_save_load(self, camera: unreal.CameraComponent):
        """Camera Component 프리셋 저장/로드 테스트"""
        self.print_separator("Test: Camera 프리셋 저장/로드")
        
        preset_name = "test_camera_preset"
        
        # 저장 테스트
        unreal.log("📝 1단계: Camera 프리셋 저장...")
        file_path = PostProcessPresetManager.save_camera_preset(camera, preset_name)
        self.log_test(
            "Camera 프리셋 저장",
            file_path is not None,
            f"경로: {file_path}" if file_path else "저장 실패"
        )
        
        if not file_path:
            return False
        
        # 현재 설정 백업
        original_settings = camera.get_editor_property("post_process_settings")
        original_vignette = original_settings.get_editor_property("vignette_intensity")
        
        # 설정 변경
        unreal.log("🔄 2단계: Camera 설정 변경...")
        modified_settings = camera.get_editor_property("post_process_settings")
        modified_settings.set_editor_property("vignette_intensity", 0.9)
        camera.set_editor_property("post_process_settings", modified_settings)
        
        # 로드 테스트
        unreal.log("📂 3단계: Camera 프리셋 로드...")
        success = PostProcessPresetManager.load_camera_preset(camera, preset_name)
        self.log_test(
            "Camera 프리셋 로드",
            success,
            "로드 성공" if success else "로드 실패"
        )
        
        if not success:
            return False
        
        # 설정 복원 확인
        restored_settings = camera.get_editor_property("post_process_settings")
        restored_vignette = restored_settings.get_editor_property("vignette_intensity")
        
        restoration_success = abs(restored_vignette - original_vignette) < 0.01
        self.log_test(
            "Camera 설정 복원 검증",
            restoration_success,
            f"원본: {original_vignette:.2f}, 복원: {restored_vignette:.2f}"
        )
        
        # 프리셋 목록 테스트
        unreal.log("📋 4단계: Camera 프리셋 목록 조회...")
        presets = PostProcessPresetManager.list_camera_presets(camera)
        list_success = preset_name in presets
        self.log_test(
            "Camera 프리셋 목록 조회",
            list_success,
            f"목록: {presets}"
        )
        
        # 삭제 테스트
        unreal.log("🗑️  5단계: Camera 프리셋 삭제...")
        delete_success = PostProcessPresetManager.delete_camera_preset(camera, preset_name)
        self.log_test(
            "Camera 프리셋 삭제",
            delete_success,
            "삭제 성공" if delete_success else "삭제 실패"
        )
        
        return True
    
    def test_common_preset_volume(self, volume: unreal.PostProcessVolume):
        """Volume → 공통 프리셋 저장/로드 테스트"""
        self.print_separator("Test: 공통 프리셋 (Volume 소스)")
        
        preset_name = "test_common_from_volume"
        category = "TestCategory"
        
        # 저장 테스트
        unreal.log("📝 1단계: Volume → 공통 프리셋 저장...")
        file_path = PostProcessPresetManager.save_common_preset(volume, preset_name, category)
        self.log_test(
            "공통 프리셋 저장 (Volume)",
            file_path is not None,
            f"경로: {file_path}" if file_path else "저장 실패"
        )
        
        if not file_path:
            return False
        
        # 현재 설정 백업
        original_settings = volume.get_editor_property("settings")
        original_temp = original_settings.get_editor_property("white_temp")
        
        # 설정 변경
        unreal.log("🔄 2단계: Volume 설정 변경...")
        modified_settings = volume.get_editor_property("settings")
        modified_settings.set_editor_property("white_temp", 10000.0)
        volume.set_editor_property("settings", modified_settings)
        
        # 로드 테스트
        unreal.log("📂 3단계: 공통 프리셋 → Volume 로드...")
        success = PostProcessPresetManager.load_common_preset(volume, preset_name, category)
        self.log_test(
            "공통 프리셋 로드 (Volume)",
            success,
            "로드 성공" if success else "로드 실패"
        )
        
        if not success:
            return False
        
        # 설정 복원 확인
        restored_settings = volume.get_editor_property("settings")
        restored_temp = restored_settings.get_editor_property("white_temp")
        
        restoration_success = abs(restored_temp - original_temp) < 0.01
        self.log_test(
            "공통 프리셋 복원 검증 (Volume)",
            restoration_success,
            f"원본: {original_temp:.2f}, 복원: {restored_temp:.2f}"
        )
        
        # 카테고리 목록 테스트
        unreal.log("📋 4단계: 공통 카테고리 목록 조회...")
        categories = PostProcessPresetManager.list_common_categories()
        category_success = category in categories
        self.log_test(
            "공통 카테고리 목록 조회",
            category_success,
            f"목록: {categories}"
        )
        
        # 프리셋 목록 테스트
        unreal.log("📋 5단계: 공통 프리셋 목록 조회...")
        presets = PostProcessPresetManager.list_common_presets(category)
        preset_success = preset_name in presets
        self.log_test(
            "공통 프리셋 목록 조회",
            preset_success,
            f"목록: {presets}"
        )
        
        # 삭제 테스트
        unreal.log("🗑️  6단계: 공통 프리셋 삭제...")
        delete_success = PostProcessPresetManager.delete_common_preset(preset_name, category)
        self.log_test(
            "공통 프리셋 삭제",
            delete_success,
            "삭제 성공" if delete_success else "삭제 실패"
        )
        
        return True
    
    def test_common_preset_camera(self, camera: unreal.CameraComponent):
        """Camera → 공통 프리셋 저장/로드 테스트"""
        self.print_separator("Test: 공통 프리셋 (Camera 소스)")
        
        preset_name = "test_common_from_camera"
        category = "CameraTest"
        
        # 저장 테스트
        unreal.log("📝 1단계: Camera → 공통 프리셋 저장...")
        file_path = PostProcessPresetManager.save_common_preset(camera, preset_name, category)
        self.log_test(
            "공통 프리셋 저장 (Camera)",
            file_path is not None,
            f"경로: {file_path}" if file_path else "저장 실패"
        )
        
        if not file_path:
            return False
        
        # 현재 설정 백업
        original_settings = camera.get_editor_property("post_process_settings")
        original_sharpen = original_settings.get_editor_property("sharpen")
        
        # 설정 변경
        unreal.log("🔄 2단계: Camera 설정 변경...")
        modified_settings = camera.get_editor_property("post_process_settings")
        modified_settings.set_editor_property("sharpen", 2.0)
        camera.set_editor_property("post_process_settings", modified_settings)
        
        # 로드 테스트
        unreal.log("📂 3단계: 공통 프리셋 → Camera 로드...")
        success = PostProcessPresetManager.load_common_preset(camera, preset_name, category)
        self.log_test(
            "공통 프리셋 로드 (Camera)",
            success,
            "로드 성공" if success else "로드 실패"
        )
        
        if not success:
            return False
        
        # 설정 복원 확인
        restored_settings = camera.get_editor_property("post_process_settings")
        restored_sharpen = restored_settings.get_editor_property("sharpen")
        
        restoration_success = abs(restored_sharpen - original_sharpen) < 0.01
        self.log_test(
            "공통 프리셋 복원 검증 (Camera)",
            restoration_success,
            f"원본: {original_sharpen:.2f}, 복원: {restored_sharpen:.2f}"
        )
        
        # 삭제 테스트
        unreal.log("🗑️  4단계: 공통 프리셋 삭제...")
        delete_success = PostProcessPresetManager.delete_common_preset(preset_name, category)
        self.log_test(
            "공통 프리셋 삭제",
            delete_success,
            "삭제 성공" if delete_success else "삭제 실패"
        )
        
        return True
    
    def test_cross_apply(self, volume: unreal.PostProcessVolume, camera: unreal.CameraComponent):
        """교차 적용 테스트: Volume 프리셋 → Camera, Camera 프리셋 → Volume"""
        self.print_separator("Test: 교차 적용 (Volume ↔ Camera)")
        
        # Volume → Camera 프리셋 교차 적용
        unreal.log("📝 1단계: Volume → 공통 프리셋 저장...")
        preset_v2c = "test_volume_to_camera"
        category = "CrossTest"
        
        path1 = PostProcessPresetManager.save_common_preset(volume, preset_v2c, category)
        save1_success = path1 is not None
        self.log_test(
            "Volume 프리셋 저장",
            save1_success,
            f"경로: {path1}" if path1 else "저장 실패"
        )
        
        if save1_success:
            unreal.log("📂 2단계: Volume 프리셋 → Camera 적용...")
            load1_success = PostProcessPresetManager.load_common_preset(camera, preset_v2c, category)
            self.log_test(
                "Volume 프리셋 → Camera 적용",
                load1_success,
                "적용 성공" if load1_success else "적용 실패"
            )
            
            # 삭제
            PostProcessPresetManager.delete_common_preset(preset_v2c, category)
        
        # Camera → Volume 프리셋 교차 적용
        unreal.log("📝 3단계: Camera → 공통 프리셋 저장...")
        preset_c2v = "test_camera_to_volume"
        
        path2 = PostProcessPresetManager.save_common_preset(camera, preset_c2v, category)
        save2_success = path2 is not None
        self.log_test(
            "Camera 프리셋 저장",
            save2_success,
            f"경로: {path2}" if path2 else "저장 실패"
        )
        
        if save2_success:
            unreal.log("📂 4단계: Camera 프리셋 → Volume 적용...")
            load2_success = PostProcessPresetManager.load_common_preset(volume, preset_c2v, category)
            self.log_test(
                "Camera 프리셋 → Volume 적용",
                load2_success,
                "적용 성공" if load2_success else "적용 실패"
            )
            
            # 삭제
            PostProcessPresetManager.delete_common_preset(preset_c2v, category)
        
        return True
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        self.print_separator("테스트 결과 요약")
        
        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed
        
        unreal.log(f"총 테스트: {total}개")
        unreal.log(f"성공: {passed}개 (✅)")
        unreal.log(f"실패: {failed}개 (❌)")
        unreal.log(f"성공률: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            unreal.log("\n❌ 실패한 테스트:")
            for name, success, message in self.test_results:
                if not success:
                    unreal.log(f"  - {name}: {message}")
        
        self.print_separator()
        
        if failed == 0:
            unreal.log("🎉 모든 테스트 통과!")
        else:
            unreal.log(f"⚠️  {failed}개 테스트 실패")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.print_separator("Post Process Preset Manager 종합 테스트 시작")
        
        # 선택된 Actor 가져오기
        selected_actors = self.editor_actor_subsystem.get_selected_level_actors()
        
        if not selected_actors:
            unreal.log_warning("⚠️  Post Process Volume 또는 Camera Actor를 선택하고 실행하세요.")
            return
        
        # Volume과 Camera 찾기
        volume = None
        camera = None
        
        for actor in selected_actors:
            if isinstance(actor, unreal.PostProcessVolume):
                volume = actor
                unreal.log(f"✅ Post Process Volume 감지: {volume.get_name()}")
            
            # Camera Component 찾기
            from tool.pp_serializer import PostProcessSerializer
            cam = PostProcessSerializer.get_camera_component(actor)
            if cam:
                camera = cam
                actor_name = actor.get_name()
                unreal.log(f"✅ Camera Component 감지: {actor_name}.{camera.get_name()}")
        
        if not volume and not camera:
            unreal.log_error("❌ Post Process Volume 또는 Camera Component를 찾을 수 없습니다.")
            return
        
        # 테스트 실행
        try:
            if volume:
                self.test_volume_preset_save_load(volume)
                self.test_common_preset_volume(volume)
            
            if camera:
                self.test_camera_preset_save_load(camera)
                self.test_common_preset_camera(camera)
            
            if volume and camera:
                self.test_cross_apply(volume, camera)
            
        except Exception as e:
            unreal.log_error(f"❌ 테스트 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()
        
        # 결과 요약
        self.print_summary()


def main():
    """메인 실행 함수"""
    tester = PPPresetTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
