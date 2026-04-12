"""
Post Process Preset Manager

Post Process Volume과 Camera Component의 Post Process Settings를 프리셋으로 저장하고 로드하는 관리 모듈입니다.

저장 위치:
- Post Process Volume: Project/Saved/PostProcess/Volume/{VolumeName}/Preset/{PresetName}.json
- Camera Post Process: Project/Saved/PostProcess/Camera/{ActorName}/{CameraName}/Preset/{PresetName}.json

프리셋 개념:
- Volume 프리셋: Post Process Volume별로 개별 저장/로드
- Camera 프리셋: Camera Component별로 개별 저장/로드
- 범용 프리셋: 공통 폴더에서 여러 대상이 공유할 수 있는 프리셋

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
import json
import os
from typing import List, Optional, Literal, Union

# pp_serializer 모듈 임포트 및 reload
import importlib
try:
    import tool.pp_serializer as pp_serializer_module
    importlib.reload(pp_serializer_module)
    from tool.pp_serializer import PostProcessSerializer
except ImportError:
    try:
        import pp_serializer as pp_serializer_module
        importlib.reload(pp_serializer_module)
        from pp_serializer import PostProcessSerializer
    except ImportError:
        unreal.log_error("PostProcessSerializer import 실패")
        raise

PresetTarget = Union[unreal.PostProcessVolume, unreal.CameraComponent]


class PostProcessPresetManager:
    """Post Process 프리셋 관리 클래스"""
    
    # 프리셋 폴더명
    PRESET_FOLDER = "Preset"
    BASE_FOLDER = "Saved/PostProcess"
    VOLUME_FOLDER = "Volume"
    CAMERA_FOLDER = "Camera"
    COMMON_FOLDER = "Common"
    
    @staticmethod
    def _get_project_dir() -> str:
        """프로젝트 디렉토리 경로 가져오기"""
        return unreal.Paths.project_dir()
    
    @staticmethod
    def _ensure_directory_exists(file_path: str) -> bool:
        """디렉토리가 없으면 생성"""
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                return True
            except Exception as e:
                unreal.log_error(f"디렉토리 생성 실패: {directory}, 오류: {e}")
                return False
        return True
    
    @staticmethod
    def _get_volume_preset_path(volume: unreal.PostProcessVolume, preset_name: str) -> str:
        """Post Process Volume 프리셋 파일 경로 생성"""
        volume_name = volume.get_name()
        return os.path.join(
            PostProcessPresetManager._get_project_dir(),
            PostProcessPresetManager.BASE_FOLDER,
            PostProcessPresetManager.VOLUME_FOLDER,
            volume_name,
            PostProcessPresetManager.PRESET_FOLDER,
            f"{preset_name}.json"
        )
    
    @staticmethod
    def _get_camera_preset_path(camera: unreal.CameraComponent, preset_name: str) -> str:
        """Camera Component 프리셋 파일 경로 생성"""
        actor = camera.get_owner()
        actor_name = actor.get_name() if actor else "UnknownActor"
        camera_name = camera.get_name()
        
        return os.path.join(
            PostProcessPresetManager._get_project_dir(),
            PostProcessPresetManager.BASE_FOLDER,
            PostProcessPresetManager.CAMERA_FOLDER,
            actor_name,
            camera_name,
            PostProcessPresetManager.PRESET_FOLDER,
            f"{preset_name}.json"
        )
    
    @staticmethod
    def _get_common_preset_path(preset_name: str, category: str = "General") -> str:
        """공통 프리셋 파일 경로 생성"""
        return os.path.join(
            PostProcessPresetManager._get_project_dir(),
            PostProcessPresetManager.BASE_FOLDER,
            PostProcessPresetManager.COMMON_FOLDER,
            category,
            PostProcessPresetManager.PRESET_FOLDER,
            f"{preset_name}.json"
        )
    
    @staticmethod
    def save_volume_preset(
        volume: unreal.PostProcessVolume,
        preset_name: str
    ) -> Optional[str]:
        """
        Post Process Volume을 프리셋으로 저장
        
        Args:
            volume: 저장할 Post Process Volume
            preset_name: 프리셋 이름 (필수)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 직렬화
            data = PostProcessSerializer.serialize_post_process_volume(volume)
            if not data:
                unreal.log_error("Post Process Volume 직렬화 실패")
                return None
            
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_volume_preset_path(volume, preset_name)
            
            # 디렉토리 생성
            if not PostProcessPresetManager._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ Volume 프리셋 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"Volume 프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def save_camera_preset(
        camera: unreal.CameraComponent,
        preset_name: str
    ) -> Optional[str]:
        """
        Camera Component Post Process 설정을 프리셋으로 저장
        
        Args:
            camera: 저장할 Camera Component
            preset_name: 프리셋 이름 (필수)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 직렬화
            data = PostProcessSerializer.serialize_camera_post_process(camera)
            if not data:
                unreal.log_error("Camera Post Process 직렬화 실패")
                return None
            
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_camera_preset_path(camera, preset_name)
            
            # 디렉토리 생성
            if not PostProcessPresetManager._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            actor = camera.get_owner()
            actor_name = actor.get_name() if actor else "UnknownActor"
            unreal.log(f"✅ Camera 프리셋 저장 완료: {file_path}")
            unreal.log(f"   - Actor: {actor_name}, Camera: {camera.get_name()}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"Camera 프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def save_common_preset(
        target: PresetTarget,
        preset_name: str,
        category: str = "General"
    ) -> Optional[str]:
        """
        공통 프리셋으로 저장 (다른 Volume/Camera에서도 사용 가능)
        
        Args:
            target: Post Process Volume 또는 Camera Component
            preset_name: 프리셋 이름 (필수)
            category: 프리셋 카테고리 (선택사항, 기본값: "General")
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 타입에 따라 직렬화
            if isinstance(target, unreal.PostProcessVolume):
                data = PostProcessSerializer.serialize_post_process_volume(target)
                source_type = "Volume"
                source_name = target.get_name()
            elif isinstance(target, unreal.CameraComponent):
                data = PostProcessSerializer.serialize_camera_post_process(target)
                source_type = "Camera"
                actor = target.get_owner()
                actor_name = actor.get_name() if actor else "UnknownActor"
                source_name = f"{actor_name}.{target.get_name()}"
            else:
                unreal.log_error("지원하지 않는 타입입니다. Post Process Volume 또는 Camera Component만 지원합니다.")
                return None
            
            if not data:
                unreal.log_error(f"{source_type} 직렬화 실패")
                return None
            
            # 메타데이터에 공통 프리셋 정보 추가
            if "metadata" not in data:
                data["metadata"] = {}
            data["metadata"]["preset_type"] = "common"
            data["metadata"]["source_type"] = source_type.lower()
            data["metadata"]["source_name"] = source_name
            data["metadata"]["category"] = category
            
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_common_preset_path(preset_name, category)
            
            # 디렉토리 생성
            if not PostProcessPresetManager._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ 공통 프리셋 저장 완료: {file_path}")
            unreal.log(f"   - 카테고리: {category}, 소스: {source_type} ({source_name})")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"공통 프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def load_volume_preset(
        volume: unreal.PostProcessVolume,
        preset_name: str
    ) -> bool:
        """
        Volume 프리셋을 로드하여 Post Process Volume에 적용
        
        Args:
            volume: 적용할 Post Process Volume
            preset_name: 로드할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_volume_preset_path(volume, preset_name)
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"Volume 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = PostProcessSerializer.deserialize_post_process_volume(volume, data)
            
            if success:
                unreal.log(f"✅ Volume 프리셋 로드 완료: {preset_name}")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"Volume 프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def load_camera_preset(
        camera: unreal.CameraComponent,
        preset_name: str
    ) -> bool:
        """
        Camera 프리셋을 로드하여 Camera Component에 적용
        
        Args:
            camera: 적용할 Camera Component
            preset_name: 로드할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_camera_preset_path(camera, preset_name)
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"Camera 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = PostProcessSerializer.deserialize_camera_post_process(camera, data)
            
            if success:
                actor = camera.get_owner()
                actor_name = actor.get_name() if actor else "UnknownActor"
                unreal.log(f"✅ Camera 프리셋 로드 완료: {preset_name}")
                unreal.log(f"   - Actor: {actor_name}, Camera: {camera.get_name()}")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"Camera 프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def load_common_preset(
        target: PresetTarget,
        preset_name: str,
        category: str = "General"
    ) -> bool:
        """
        공통 프리셋을 로드하여 대상에 적용
        
        Args:
            target: Post Process Volume 또는 Camera Component
            preset_name: 로드할 프리셋 이름
            category: 프리셋 카테고리
            
        Returns:
            성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = PostProcessPresetManager._get_common_preset_path(preset_name, category)
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"공통 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 메타데이터 확인
            metadata = data.get("metadata", {})
            source_type = metadata.get("source_type", "unknown")
            
            # 타입에 따라 역직렬화
            if isinstance(target, unreal.PostProcessVolume):
                success = PostProcessSerializer.deserialize_post_process_volume(target, data)
                target_type = "Volume"
                target_name = target.get_name()
            elif isinstance(target, unreal.CameraComponent):
                success = PostProcessSerializer.deserialize_camera_post_process(target, data)
                target_type = "Camera"
                actor = target.get_owner()
                actor_name = actor.get_name() if actor else "UnknownActor"
                target_name = f"{actor_name}.{target.get_name()}"
            else:
                unreal.log_error("지원하지 않는 타입입니다.")
                return False
            
            if success:
                unreal.log(f"✅ 공통 프리셋 로드 완료: {preset_name}")
                unreal.log(f"   - 카테고리: {category}")
                unreal.log(f"   - 소스: {source_type} → 대상: {target_type} ({target_name})")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"공통 프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def list_volume_presets(volume: unreal.PostProcessVolume) -> List[str]:
        """
        사용 가능한 Volume 프리셋 목록 가져오기
        
        Args:
            volume: Post Process Volume
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            preset_folder = os.path.join(
                PostProcessPresetManager._get_project_dir(),
                PostProcessPresetManager.BASE_FOLDER,
                PostProcessPresetManager.VOLUME_FOLDER,
                volume.get_name(),
                PostProcessPresetManager.PRESET_FOLDER
            )
            
            if not os.path.exists(preset_folder):
                return []
            
            presets = []
            for file in os.listdir(preset_folder):
                if file.endswith(".json"):
                    preset_name = file.replace(".json", "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"Volume 프리셋 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def list_camera_presets(camera: unreal.CameraComponent) -> List[str]:
        """
        사용 가능한 Camera 프리셋 목록 가져오기
        
        Args:
            camera: Camera Component
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            actor = camera.get_owner()
            actor_name = actor.get_name() if actor else "UnknownActor"
            
            preset_folder = os.path.join(
                PostProcessPresetManager._get_project_dir(),
                PostProcessPresetManager.BASE_FOLDER,
                PostProcessPresetManager.CAMERA_FOLDER,
                actor_name,
                camera.get_name(),
                PostProcessPresetManager.PRESET_FOLDER
            )
            
            if not os.path.exists(preset_folder):
                return []
            
            presets = []
            for file in os.listdir(preset_folder):
                if file.endswith(".json"):
                    preset_name = file.replace(".json", "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"Camera 프리셋 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def list_common_presets(category: str = "General") -> List[str]:
        """
        사용 가능한 공통 프리셋 목록 가져오기
        
        Args:
            category: 프리셋 카테고리
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            preset_folder = os.path.join(
                PostProcessPresetManager._get_project_dir(),
                PostProcessPresetManager.BASE_FOLDER,
                PostProcessPresetManager.COMMON_FOLDER,
                category,
                PostProcessPresetManager.PRESET_FOLDER
            )
            
            if not os.path.exists(preset_folder):
                return []
            
            presets = []
            for file in os.listdir(preset_folder):
                if file.endswith(".json"):
                    preset_name = file.replace(".json", "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"공통 프리셋 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def list_common_categories() -> List[str]:
        """
        사용 가능한 공통 프리셋 카테고리 목록 가져오기
        
        Returns:
            카테고리 이름 리스트
        """
        try:
            common_folder = os.path.join(
                PostProcessPresetManager._get_project_dir(),
                PostProcessPresetManager.BASE_FOLDER,
                PostProcessPresetManager.COMMON_FOLDER
            )
            
            if not os.path.exists(common_folder):
                return []
            
            categories = []
            for item in os.listdir(common_folder):
                item_path = os.path.join(common_folder, item)
                if os.path.isdir(item_path):
                    categories.append(item)
            
            return sorted(categories)
            
        except Exception as e:
            unreal.log_error(f"공통 카테고리 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def delete_volume_preset(volume: unreal.PostProcessVolume, preset_name: str) -> bool:
        """Volume 프리셋 파일 삭제"""
        try:
            file_path = PostProcessPresetManager._get_volume_preset_path(volume, preset_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                unreal.log(f"✅ Volume 프리셋 삭제 완료: {preset_name}")
                return True
            else:
                unreal.log_warning(f"Volume 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
                
        except Exception as e:
            unreal.log_error(f"Volume 프리셋 삭제 실패: {e}")
            return False
    
    @staticmethod
    def delete_camera_preset(camera: unreal.CameraComponent, preset_name: str) -> bool:
        """Camera 프리셋 파일 삭제"""
        try:
            file_path = PostProcessPresetManager._get_camera_preset_path(camera, preset_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                unreal.log(f"✅ Camera 프리셋 삭제 완료: {preset_name}")
                return True
            else:
                unreal.log_warning(f"Camera 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
                
        except Exception as e:
            unreal.log_error(f"Camera 프리셋 삭제 실패: {e}")
            return False
    
    @staticmethod
    def delete_common_preset(preset_name: str, category: str = "General") -> bool:
        """공통 프리셋 파일 삭제"""
        try:
            file_path = PostProcessPresetManager._get_common_preset_path(preset_name, category)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                unreal.log(f"✅ 공통 프리셋 삭제 완료: {preset_name} (카테고리: {category})")
                return True
            else:
                unreal.log_warning(f"공통 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
                
        except Exception as e:
            unreal.log_error(f"공통 프리셋 삭제 실패: {e}")
            return False


# 사용 예제
if __name__ == "__main__":
    """
    예제: 선택된 Post Process Volume 또는 Camera로 프리셋 관리
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
            # Volume 프리셋 저장 (예제)
            volume_preset_path = PostProcessPresetManager.save_volume_preset(actor, "default_volume")
            if volume_preset_path:
                print(f"✅ Volume 프리셋 저장됨: {volume_preset_path}")
            
            # 공통 프리셋으로도 저장 (예제)
            common_preset_path = PostProcessPresetManager.save_common_preset(actor, "cinematic_look", "Cinematic")
            if common_preset_path:
                print(f"✅ 공통 프리셋 저장됨: {common_preset_path}")
            
            # 사용 가능한 프리셋 목록
            volume_presets = PostProcessPresetManager.list_volume_presets(actor)
            common_presets = PostProcessPresetManager.list_common_presets("Cinematic")
            print(f"📋 Volume 프리셋: {volume_presets}")
            print(f"📋 공통 프리셋 (Cinematic): {common_presets}")
        
        # Camera Component 찾기 및 처리
        camera = PostProcessSerializer.get_camera_component(actor)
        if camera:
            # Camera 프리셋 저장 (예제)
            camera_preset_path = PostProcessPresetManager.save_camera_preset(camera, "default_camera")
            if camera_preset_path:
                print(f"✅ Camera 프리셋 저장됨: {camera_preset_path}")
            
            # 공통 프리셋으로도 저장 (예제)
            common_camera_preset_path = PostProcessPresetManager.save_common_preset(camera, "handheld_camera", "Camera")
            if common_camera_preset_path:
                print(f"✅ 공통 Camera 프리셋 저장됨: {common_camera_preset_path}")
            
            # 사용 가능한 프리셋 목록
            camera_presets = PostProcessPresetManager.list_camera_presets(camera)
            common_camera_presets = PostProcessPresetManager.list_common_presets("Camera")
            print(f"📋 Camera 프리셋: {camera_presets}")
            print(f"📋 공통 프리셋 (Camera): {common_camera_presets}")
        
        # 다른 타입의 Actor인 경우
        if not isinstance(actor, unreal.PostProcessVolume) and not camera:
            print(f"⚠️  {actor.__class__.__name__}은 Post Process 설정을 지원하지 않습니다.")
    
    # 공통 카테고리 목록
    categories = PostProcessPresetManager.list_common_categories()
    print(f"\n📁 사용 가능한 공통 카테고리: {categories}")
    
    print(f"\n{'='*80}")
    print(f"📁 Post Process Preset 폴더 구조")
    print(f"{'='*80}")
    print(f"Project/")
    print(f"└── Saved/")
    print(f"    └── PostProcess/")
    print(f"        ├── Volume/")
    print(f"        │   └── {{VolumeName}}/")
    print(f"        │       └── Preset/")
    print(f"        │           ├── default_volume.json")
    print(f"        │           ├── night_scene.json")
    print(f"        │           └── day_scene.json")
    print(f"        ├── Camera/")
    print(f"        │   └── {{ActorName}}/")
    print(f"        │       └── {{CameraName}}/")
    print(f"        │           └── Preset/")
    print(f"        │               ├── default_camera.json")
    print(f"        │               ├── closeup_shot.json")
    print(f"        │               └── wide_shot.json")
    print(f"        └── Common/")
    print(f"            ├── General/")
    print(f"            │   └── Preset/")
    print(f"            │       ├── standard.json")
    print(f"            │       └── high_contrast.json")
    print(f"            ├── Cinematic/")
    print(f"            │   └── Preset/")
    print(f"            │       ├── film_look.json")
    print(f"            │       ├── noir_style.json")
    print(f"            │       └── vintage.json")
    print(f"            └── Camera/")
    print(f"                └── Preset/")
    print(f"                    ├── handheld.json")
    print(f"                    ├── static_shot.json")
    print(f"                    └── dolly_zoom.json")
    print(f"")
    print(f"💡 개념:")
    print(f"   • Volume 프리셋: 특정 Post Process Volume에서만 사용")
    print(f"   • Camera 프리셋: 특정 Camera Component에서만 사용")
    print(f"   • 공통 프리셋: 모든 Volume/Camera에서 공유 가능")
    print(f"   • 카테고리별로 프리셋 분류 관리 (General, Cinematic, Camera 등)")

    print(f"\n{'='*80}")
    print(f"🚀 Post Process Preset Manager 사용법")
    print(f"{'='*80}")
    print(f"1. Volume 프리셋:")
    print(f"   PostProcessPresetManager.save_volume_preset(volume, 'preset_name')")
    print(f"   PostProcessPresetManager.load_volume_preset(volume, 'preset_name')")
    print(f"")
    print(f"2. Camera 프리셋:")
    print(f"   PostProcessPresetManager.save_camera_preset(camera, 'preset_name')")
    print(f"   PostProcessPresetManager.load_camera_preset(camera, 'preset_name')")
    print(f"")
    print(f"3. 공통 프리셋:")
    print(f"   PostProcessPresetManager.save_common_preset(target, 'preset_name', 'Category')")
    print(f"   PostProcessPresetManager.load_common_preset(target, 'preset_name', 'Category')")
    print(f"")
    print(f"4. 프리셋 목록:")
    print(f"   PostProcessPresetManager.list_volume_presets(volume)")
    print(f"   PostProcessPresetManager.list_camera_presets(camera)")
    print(f"   PostProcessPresetManager.list_common_presets('Category')")
    print(f"   PostProcessPresetManager.list_common_categories()")
    print(f"{'='*80}")