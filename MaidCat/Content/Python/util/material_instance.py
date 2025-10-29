"""
Material Instance JSON Serialization/Deserialization Utility

머티리얼 인스턴스의 파라미터를 JSON으로 직렬화하고 역직렬화하는 유틸리티입니다.

지원하는 파라미터:
- Scalar Parameters (Float)
- Vector Parameters (Color/Linear Color)
- Texture Parameters
- Static Switch Parameters

저장 위치:
- 프리셋: Project/Saved/Material/{ParentMaterialPath}/{MaterialName}_preset.json
- 백업: Project/Saved/Material/{MaterialPath}/{MaterialName}_backup.json

Author: MaidCat Team
Version: 1.0.0
"""

import unreal
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class MaterialInstanceSerializer:
    """머티리얼 인스턴스 직렬화/역직렬화 클래스"""
    
    # 저장 경로 설정
    BASE_SAVE_DIR = "Saved/Material"
    PRESET_SUFFIX = "_preset.json"
    BACKUP_SUFFIX = "_backup.json"
    
    @staticmethod
    def _get_project_dir() -> str:
        """프로젝트 디렉토리 경로 가져오기"""
        return unreal.Paths.project_dir()
    
    @staticmethod
    def _convert_game_path_to_file_path(game_path: str) -> str:
        """
        /Game 경로를 Saved/Material 경로로 변환
        
        Args:
            game_path: /Game/Path/To/Asset 형태의 경로
            
        Returns:
            Saved/Material/Path/To/Asset 형태의 경로
        """
        if game_path.startswith("/Game/"):
            return game_path.replace("/Game/", "Saved/Material/", 1)
        elif game_path.startswith("/Game"):
            return game_path.replace("/Game", "Saved/Material", 1)
        return f"Saved/Material/{game_path}"
    
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
    def _get_parent_material_path(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """머티리얼 인스턴스의 최상위 부모 머티리얼 경로 가져오기"""
        try:
            # MaterialInstance의 parent 속성 직접 접근
            parent = material_instance.get_editor_property("parent")
            
            if not parent:
                return None
            
            # 부모가 또 다른 MaterialInstance인 경우 재귀적으로 추적
            while parent and isinstance(parent, unreal.MaterialInstance):
                next_parent = parent.get_editor_property("parent")
                if next_parent:
                    parent = next_parent
                else:
                    break
            
            if parent:
                return parent.get_path_name()
            return None
            
        except Exception as e:
            unreal.log_warning(f"부모 머티리얼 경로 가져오기 실패: {e}")
            return None
    
    @staticmethod
    def serialize_material_instance(material_instance: unreal.MaterialInstance) -> Dict[str, Any]:
        """
        머티리얼 인스턴스를 딕셔너리로 직렬화
        
        Args:
            material_instance: 직렬화할 머티리얼 인스턴스
            
        Returns:
            직렬화된 데이터 딕셔너리
        """
        data = {
            "metadata": {
                "asset_path": material_instance.get_path_name(),
                "asset_name": material_instance.get_name(),
                "parent_material": None,
                "serialized_date": datetime.now().isoformat(),
                "unreal_version": unreal.SystemLibrary.get_engine_version()
            },
            "parameters": {
                "scalar": {},
                "vector": {},
                "texture": {},
                "static_switch": {}
            }
        }
        
        # 부모 머티리얼 경로 저장
        parent_path = MaterialInstanceSerializer._get_parent_material_path(material_instance)
        if parent_path:
            data["metadata"]["parent_material"] = parent_path
        
        # Scalar Parameters 수집
        scalar_params = unreal.MaterialEditingLibrary.get_scalar_parameter_names(material_instance)
        for param_name in scalar_params:
            value = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(
                material_instance, param_name
            )
            # Override 상태 확인 (Python API에서는 직접 확인 불가능하므로 항상 저장)
            data["parameters"]["scalar"][str(param_name)] = {
                "value": value,
                "override": True  # 파라미터 목록에 있다는 것은 override 되어 있다는 의미
            }
        
        # Vector Parameters 수집
        vector_params = unreal.MaterialEditingLibrary.get_vector_parameter_names(material_instance)
        for param_name in vector_params:
            value = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(
                material_instance, param_name
            )
            # LinearColor를 딕셔너리로 변환
            data["parameters"]["vector"][str(param_name)] = {
                "value": {
                    "r": value.r,
                    "g": value.g,
                    "b": value.b,
                    "a": value.a
                },
                "override": True
            }
        
        # Texture Parameters 수집
        texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(material_instance)
        for param_name in texture_params:
            texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                material_instance, param_name
            )
            # 텍스처 경로 저장 (None이면 null)
            texture_path = texture.get_path_name() if texture else None
            data["parameters"]["texture"][str(param_name)] = {
                "value": texture_path,
                "override": True
            }
        
        # Static Switch Parameters 수집
        static_switch_params = unreal.MaterialEditingLibrary.get_static_switch_parameter_names(
            material_instance
        )
        for param_name in static_switch_params:
            value = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value(
                material_instance, param_name
            )
            data["parameters"]["static_switch"][str(param_name)] = {
                "value": value,
                "override": True
            }
        
        return data
    
    @staticmethod
    def deserialize_material_instance(
        material_instance: unreal.MaterialInstance,
        data: Dict[str, Any]
    ) -> bool:
        """
        딕셔너리 데이터를 머티리얼 인스턴스에 적용
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            data: 직렬화된 데이터 딕셔너리
            
        Returns:
            성공 여부
        """
        try:
            parameters = data.get("parameters", {})
            
            # Scalar Parameters 적용
            scalar_params = parameters.get("scalar", {})
            for param_name, param_data in scalar_params.items():
                # 이전 버전 호환성: 값이 딕셔너리가 아니면 직접 값으로 간주
                if isinstance(param_data, dict):
                    value = param_data.get("value", 0.0)
                    override = param_data.get("override", True)
                else:
                    value = param_data
                    override = True
                
                if override:
                    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                        material_instance,
                        unreal.Name(param_name),
                        float(value)
                    )
            
            # Vector Parameters 적용
            vector_params = parameters.get("vector", {})
            for param_name, param_data in vector_params.items():
                # 이전 버전 호환성
                if isinstance(param_data, dict) and "value" in param_data:
                    color_data = param_data["value"]
                    override = param_data.get("override", True)
                else:
                    color_data = param_data
                    override = True
                
                if override:
                    color = unreal.LinearColor(
                        r=color_data["r"],
                        g=color_data["g"],
                        b=color_data["b"],
                        a=color_data["a"]
                    )
                    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                        material_instance,
                        unreal.Name(param_name),
                        color
                    )
            
            # Texture Parameters 적용
            texture_params = parameters.get("texture", {})
            for param_name, param_data in texture_params.items():
                # 이전 버전 호환성
                if isinstance(param_data, dict):
                    texture_path = param_data.get("value")
                    override = param_data.get("override", True)
                else:
                    texture_path = param_data
                    override = True
                
                if override and texture_path:
                    # 여러 방법으로 텍스처 로드 시도
                    texture = None
                    
                    # 방법 1: EditorAssetLibrary.load_asset
                    try:
                        texture = unreal.EditorAssetLibrary.load_asset(texture_path)
                    except:
                        pass
                    
                    # 방법 2: load_asset (전역 함수)
                    if not texture:
                        try:
                            texture = unreal.load_asset(texture_path)
                        except:
                            pass
                    
                    # 방법 3: load_object (type 지정)
                    if not texture:
                        try:
                            texture = unreal.load_object(None, texture_path)
                        except:
                            pass
                    
                    if texture:
                        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                            material_instance,
                            unreal.Name(param_name),
                            texture
                        )
                    else:
                        unreal.log_warning(f"⚠️  텍스처를 찾을 수 없음: {texture_path} (파라미터: {param_name})")
            
            # Static Switch Parameters 적용
            static_switch_params = parameters.get("static_switch", {})
            for param_name, param_data in static_switch_params.items():
                # 이전 버전 호환성
                if isinstance(param_data, dict):
                    value = param_data.get("value", False)
                    override = param_data.get("override", True)
                else:
                    value = param_data
                    override = True
                
                if override:
                    unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(
                        material_instance,
                        unreal.Name(param_name),
                        bool(value)
                    )
            
            # 변경사항 저장
            unreal.EditorAssetLibrary.save_asset(material_instance.get_path_name())
            
            return True
            
        except Exception as e:
            unreal.log_error(f"머티리얼 인스턴스 역직렬화 실패: {e}")
            return False
    
    @staticmethod
    def save_as_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: Optional[str] = None
    ) -> Optional[str]:
        """
        머티리얼 인스턴스를 프리셋으로 저장
        
        프리셋은 부모 머티리얼 폴더에 저장되어 같은 부모를 가진 인스턴스들이 공유
        
        Args:
            material_instance: 저장할 머티리얼 인스턴스
            preset_name: 프리셋 이름 (None이면 인스턴스 이름 사용)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 직렬화
            data = MaterialInstanceSerializer.serialize_material_instance(material_instance)
            
            # 부모 머티리얼 경로 가져오기
            parent_path = data["metadata"].get("parent_material")
            if not parent_path:
                unreal.log_error("부모 머티리얼을 찾을 수 없습니다.")
                return None
            
            # 파일 경로 생성
            parent_folder = MaterialInstanceSerializer._convert_game_path_to_file_path(parent_path)
            parent_folder = os.path.dirname(parent_folder)  # 파일명 제거
            
            if not preset_name:
                preset_name = material_instance.get_name()
            
            file_name = f"{preset_name}{MaterialInstanceSerializer.PRESET_SUFFIX}"
            file_path = os.path.join(
                MaterialInstanceSerializer._get_project_dir(),
                parent_folder,
                file_name
            )
            
            # 디렉토리 생성
            if not MaterialInstanceSerializer._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ 프리셋 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def save_as_backup(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """
        머티리얼 인스턴스를 백업으로 저장
        
        백업은 자기 자신의 폴더에 저장되어 개별 인스턴스 전용
        
        Args:
            material_instance: 백업할 머티리얼 인스턴스
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 직렬화
            data = MaterialInstanceSerializer.serialize_material_instance(material_instance)
            
            # 파일 경로 생성
            asset_path = material_instance.get_path_name()
            material_folder = MaterialInstanceSerializer._convert_game_path_to_file_path(asset_path)
            material_folder = os.path.dirname(material_folder)  # 파일명 제거
            
            file_name = f"{material_instance.get_name()}{MaterialInstanceSerializer.BACKUP_SUFFIX}"
            file_path = os.path.join(
                MaterialInstanceSerializer._get_project_dir(),
                material_folder,
                file_name
            )
            
            # 디렉토리 생성
            if not MaterialInstanceSerializer._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ 백업 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"백업 저장 실패: {e}")
            return None
    
    @staticmethod
    def load_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: str
    ) -> bool:
        """
        프리셋을 로드하여 머티리얼 인스턴스에 적용
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            preset_name: 로드할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            # 부모 머티리얼 경로 가져오기
            parent_path = MaterialInstanceSerializer._get_parent_material_path(material_instance)
            if not parent_path:
                unreal.log_error("부모 머티리얼을 찾을 수 없습니다.")
                return False
            
            # 파일 경로 생성
            parent_folder = MaterialInstanceSerializer._convert_game_path_to_file_path(parent_path)
            parent_folder = os.path.dirname(parent_folder)
            
            file_name = f"{preset_name}{MaterialInstanceSerializer.PRESET_SUFFIX}"
            file_path = os.path.join(
                MaterialInstanceSerializer._get_project_dir(),
                parent_folder,
                file_name
            )
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = MaterialInstanceSerializer.deserialize_material_instance(
                material_instance, data
            )
            
            if success:
                unreal.log(f"✅ 프리셋 로드 완료: {preset_name}")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def load_backup(material_instance: unreal.MaterialInstance) -> bool:
        """
        백업을 로드하여 머티리얼 인스턴스에 적용
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            
        Returns:
            성공 여부
        """
        try:
            # 파일 경로 생성
            asset_path = material_instance.get_path_name()
            material_folder = MaterialInstanceSerializer._convert_game_path_to_file_path(asset_path)
            material_folder = os.path.dirname(material_folder)
            
            file_name = f"{material_instance.get_name()}{MaterialInstanceSerializer.BACKUP_SUFFIX}"
            file_path = os.path.join(
                MaterialInstanceSerializer._get_project_dir(),
                material_folder,
                file_name
            )
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"백업 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = MaterialInstanceSerializer.deserialize_material_instance(
                material_instance, data
            )
            
            if success:
                unreal.log(f"✅ 백업 로드 완료")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"백업 로드 실패: {e}")
            return False
    
    @staticmethod
    def list_presets(material_instance: unreal.MaterialInstance) -> List[str]:
        """
        사용 가능한 프리셋 목록 가져오기
        
        Args:
            material_instance: 머티리얼 인스턴스
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            # 부모 머티리얼 경로 가져오기
            parent_path = MaterialInstanceSerializer._get_parent_material_path(material_instance)
            if not parent_path:
                return []
            
            # 폴더 경로
            parent_folder = MaterialInstanceSerializer._convert_game_path_to_file_path(parent_path)
            parent_folder = os.path.dirname(parent_folder)
            full_path = os.path.join(
                MaterialInstanceSerializer._get_project_dir(),
                parent_folder
            )
            
            if not os.path.exists(full_path):
                return []
            
            # 프리셋 파일 찾기
            presets = []
            for file in os.listdir(full_path):
                if file.endswith(MaterialInstanceSerializer.PRESET_SUFFIX):
                    preset_name = file.replace(MaterialInstanceSerializer.PRESET_SUFFIX, "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"프리셋 목록 가져오기 실패: {e}")
            return []


# 편의 함수들
def save_material_preset(
    material_instance: unreal.MaterialInstance,
    preset_name: Optional[str] = None
) -> Optional[str]:
    """머티리얼 인스턴스 프리셋 저장 편의 함수"""
    return MaterialInstanceSerializer.save_as_preset(material_instance, preset_name)


def save_material_backup(material_instance: unreal.MaterialInstance) -> Optional[str]:
    """머티리얼 인스턴스 백업 저장 편의 함수"""
    return MaterialInstanceSerializer.save_as_backup(material_instance)


def load_material_preset(
    material_instance: unreal.MaterialInstance,
    preset_name: str
) -> bool:
    """머티리얼 인스턴스 프리셋 로드 편의 함수"""
    return MaterialInstanceSerializer.load_preset(material_instance, preset_name)


def load_material_backup(material_instance: unreal.MaterialInstance) -> bool:
    """머티리얼 인스턴스 백업 로드 편의 함수"""
    return MaterialInstanceSerializer.load_backup(material_instance)


def list_material_presets(material_instance: unreal.MaterialInstance) -> List[str]:
    """사용 가능한 프리셋 목록 가져오기 편의 함수"""
    return MaterialInstanceSerializer.list_presets(material_instance)


# 사용 예제
if __name__ == "__main__":
    """
    테스트: 머티리얼 인스턴스 백업 및 파라미터 이전
    
    1. 기존 머티리얼 인스턴스 백업
    2. 부모 머티리얼에서 새 인스턴스 생성
    3. 백업한 파라미터를 새 인스턴스에 적용
    """
    
    TEST_MATERIAL_PATH = "/Game/See1/AOE/AOE_Test"
    NEW_MATERIAL_NAME = "AOE_Test_New"
    NEW_MATERIAL_PATH = "/Game/See1/AOE/AOE_Test_New"
    
    try:
        print("\n" + "="*80)
        print("🔧 머티리얼 인스턴스 백업 및 파라미터 이전 테스트 시작")
        print("="*80 + "\n")
        
        # Step 1: 원본 머티리얼 인스턴스 로드
        print(f"📂 Step 1: 원본 머티리얼 인스턴스 로드")
        print(f"   경로: {TEST_MATERIAL_PATH}")
        
        original_material = unreal.load_asset(TEST_MATERIAL_PATH)
        
        if not original_material:
            print(f"❌ 머티리얼을 찾을 수 없습니다: {TEST_MATERIAL_PATH}")
            print("   먼저 /Game/See1/AOE/AOE_Test 머티리얼 인스턴스를 생성해주세요.")
            exit(1)
        
        if not isinstance(original_material, unreal.MaterialInstance):
            print(f"❌ 해당 에셋은 MaterialInstance가 아닙니다: {type(original_material)}")
            exit(1)
        
        print(f"✅ 원본 머티리얼 로드 완료: {original_material.get_name()}\n")
        
        # Step 2: 부모 머티리얼 확인
        print(f"📂 Step 2: 부모 머티리얼 확인")
        
        parent_material = original_material.get_editor_property("parent")
        
        if not parent_material:
            print(f"❌ 부모 머티리얼을 찾을 수 없습니다.")
            exit(1)
        
        parent_path = parent_material.get_path_name()
        print(f"   부모 머티리얼: {parent_path}")
        print(f"✅ 부모 머티리얼 확인 완료\n")
        
        # Step 3: 원본 파라미터 직렬화 (백업)
        print(f"💾 Step 3: 원본 파라미터 백업")
        
        backup_data = MaterialInstanceSerializer.serialize_material_instance(original_material)
        
        # 백업된 파라미터 정보 출력
        params = backup_data.get("parameters", {})
        scalar_count = len(params.get("scalar", {}))
        vector_count = len(params.get("vector", {}))
        texture_count = len(params.get("texture", {}))
        switch_count = len(params.get("static_switch", {}))
        
        print(f"   📊 백업된 파라미터:")
        print(f"      - Scalar Parameters: {scalar_count}개")
        print(f"      - Vector Parameters: {vector_count}개")
        print(f"      - Texture Parameters: {texture_count}개")
        print(f"      - Static Switch Parameters: {switch_count}개")
        
        if scalar_count > 0:
            print(f"\n   🔢 Scalar Parameters:")
            for name, param_data in params["scalar"].items():
                value = param_data.get("value", param_data) if isinstance(param_data, dict) else param_data
                print(f"      • {name}: {value}")
        
        if vector_count > 0:
            print(f"\n   🎨 Vector Parameters:")
            for name, param_data in params["vector"].items():
                color = param_data.get("value", param_data) if isinstance(param_data, dict) else param_data
                print(f"      • {name}: R={color['r']:.3f}, G={color['g']:.3f}, B={color['b']:.3f}, A={color['a']:.3f}")
        
        if texture_count > 0:
            print(f"\n   🖼️  Texture Parameters:")
            for name, param_data in params["texture"].items():
                tex_path = param_data.get("value", param_data) if isinstance(param_data, dict) else param_data
                tex_name = tex_path.split("/")[-1] if tex_path else "None"
                print(f"      • {name}: {tex_name}")
        
        if switch_count > 0:
            print(f"\n   🔀 Static Switch Parameters:")
            for name, param_data in params["static_switch"].items():
                value = param_data.get("value", param_data) if isinstance(param_data, dict) else param_data
                print(f"      • {name}: {value}")
        
        # 백업 파일로도 저장
        backup_path = MaterialInstanceSerializer.save_as_backup(original_material)
        print(f"\n   💾 백업 파일 저장됨: {backup_path}")
        print(f"✅ 백업 완료\n")
        
        # Step 4: 새 머티리얼 인스턴스 생성
        print(f"🆕 Step 4: 새 머티리얼 인스턴스 생성")
        print(f"   이름: {NEW_MATERIAL_NAME}")
        print(f"   경로: {NEW_MATERIAL_PATH}")
        
        # 기존 에셋이 있으면 삭제
        if unreal.EditorAssetLibrary.does_asset_exist(NEW_MATERIAL_PATH):
            print(f"   ⚠️  기존 에셋 발견, 삭제 중...")
            unreal.EditorAssetLibrary.delete_asset(NEW_MATERIAL_PATH)
        
        # 새 머티리얼 인스턴스 생성 (Factory 없이 직접 생성)
        new_material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name=NEW_MATERIAL_NAME,
            package_path="/Game/See1/AOE",
            asset_class=unreal.MaterialInstanceConstant,
            factory=unreal.MaterialInstanceConstantFactoryNew()
        )
        
        if not new_material:
            print(f"❌ 새 머티리얼 인스턴스 생성 실패")
            exit(1)
        
        # 부모 머티리얼 설정
        new_material.set_editor_property("parent", parent_material)
        unreal.EditorAssetLibrary.save_loaded_asset(new_material)
        
        print(f"✅ 새 머티리얼 인스턴스 생성 완료: {new_material.get_name()}\n")
        
        # Step 5: 백업 데이터를 새 인스턴스에 적용
        print(f"📥 Step 5: 백업 파라미터를 새 인스턴스에 적용")
        
        success = MaterialInstanceSerializer.deserialize_material_instance(new_material, backup_data)
        
        if not success:
            print(f"❌ 파라미터 적용 실패")
            exit(1)
        
        print(f"✅ 파라미터 적용 완료\n")
        
        # Step 6: 결과 확인
        print(f"✨ Step 6: 결과 확인")
        print(f"   원본: {TEST_MATERIAL_PATH}")
        print(f"   새 인스턴스: {NEW_MATERIAL_PATH}")
        print(f"   부모 머티리얼: {parent_path}")
        
        # 새 인스턴스의 파라미터 직렬화하여 비교
        new_data = MaterialInstanceSerializer.serialize_material_instance(new_material)
        new_params = new_data.get("parameters", {})
        
        print(f"\n   📊 새 인스턴스 파라미터:")
        print(f"      - Scalar Parameters: {len(new_params.get('scalar', {}))}개")
        print(f"      - Vector Parameters: {len(new_params.get('vector', {}))}개")
        print(f"      - Texture Parameters: {len(new_params.get('texture', {}))}개")
        print(f"      - Static Switch Parameters: {len(new_params.get('static_switch', {}))}개")
        
        # 텍스처 파라미터 상세 비교
        print(f"\n   🖼️  텍스처 파라미터 비교:")
        original_textures = backup_data["parameters"].get("texture", {})
        new_textures = new_params.get("texture", {})
        
        for param_name in original_textures.keys():
            original_data = original_textures[param_name]
            new_data = new_textures.get(param_name, {})
            
            # 이전 버전 호환성
            original_path = original_data.get("value", original_data) if isinstance(original_data, dict) else original_data
            new_path = new_data.get("value", new_data) if isinstance(new_data, dict) else new_data
            
            if original_path == new_path:
                print(f"      ✅ {param_name}: {original_path}")
            else:
                print(f"      ❌ {param_name}:")
                print(f"         원본: {original_path}")
                print(f"         복원: {new_path}")
        
        # 에셋 저장
        unreal.EditorAssetLibrary.save_asset(new_material.get_path_name())
        
        print("\n" + "="*80)
        print("✅ 테스트 완료!")
        print("="*80)
        print(f"\n💡 팁: Content Browser에서 다음 에셋들을 확인해보세요:")
        print(f"   • 원본: {TEST_MATERIAL_PATH}")
        print(f"   • 새 인스턴스: {NEW_MATERIAL_PATH}")
        print(f"   • 두 인스턴스의 파라미터가 동일한지 확인하세요!\n")
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 기존 예제 코드 (주석 처리)
    """
    # 예제: 선택된 머티리얼 인스턴스로 테스트
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    for asset in selected_assets:
        if isinstance(asset, unreal.MaterialInstance):
            print(f"\n=== 머티리얼 인스턴스: {asset.get_name()} ===")
            
            # 백업 저장
            backup_path = save_material_backup(asset)
            if backup_path:
                print(f"백업 저장됨: {backup_path}")
            
            # 프리셋 저장
            preset_path = save_material_preset(asset, "default")
            if preset_path:
                print(f"프리셋 저장됨: {preset_path}")
            
            # 사용 가능한 프리셋 목록
            presets = list_material_presets(asset)
            print(f"사용 가능한 프리셋: {presets}")
            
            # 프리셋 로드 예제 (주석 처리)
            # if "default" in presets:
            #     load_material_preset(asset, "default")
            #     print("프리셋 'default' 로드됨")
            
            # 백업 로드 예제 (주석 처리)
            # load_material_backup(asset)
            # print("백업 로드됨")
    """