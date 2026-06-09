"""
Material Instance Preset Manager

머티리얼 인스턴스의 파라미터를 루트 프리셋/부모 프리셋으로 저장하고 로드하는 관리 모듈입니다.

저장 위치:
- 루트 프리셋: Project/Saved/Material/{RootMaterialPath}/Preset/{PresetName}.json
- 부모 프리셋: Project/Saved/Material/{ParentMaterialPath}/Preset/{PresetName}.json

프리셋 개념:
- 루트 프리셋: 최상위 머티리얼이 같은 머티리얼 인스턴스들이 공유할 수 있는 프리셋
- 부모 프리셋: 직접 부모 머티리얼이 같은 머티리얼 인스턴스들이 공유할 수 있는 프리셋

Author: MaidCat Team
Version: 3.0.0
"""

import unreal
import json
import os
from typing import List, Optional, Literal

# mi_serializer 모듈 임포트 및 reload
import importlib
try:
    import tool.mi_serializer as mi_serializer_module
    importlib.reload(mi_serializer_module)
    from tool.mi_serializer import MaterialInstanceSerializer
except ImportError:
    try:
        import mi_serializer as mi_serializer_module
        importlib.reload(mi_serializer_module)
        from mi_serializer import MaterialInstanceSerializer
    except ImportError:
        unreal.log_error("MaterialInstanceSerializer import 실패")
        raise

PresetType = Literal["root", "parent"]


class MaterialInstancePresetManager:
    """머티리얼 인스턴스 프리셋 관리 클래스"""
    
    # 프리셋 폴더명
    PRESET_FOLDER = "Preset"
    
    @staticmethod
    def _get_root_material_path(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """머티리얼 인스턴스의 최상위 루트 머티리얼 경로 가져오기 (백업용)"""
        try:
            parent = material_instance.get_editor_property("parent")
            if not parent:
                return None
            
            # 부모가 또 다른 MaterialInstance인 경우 재귀적으로 추적하여 최상위 찾기
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
            unreal.log_warning(f"루트 머티리얼 경로 가져오기 실패: {e}")
            return None
    
    @staticmethod
    def _get_parent_material_path(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """머티리얼 인스턴스의 직접 부모 머티리얼 경로 가져오기 (백업용)"""
        try:
            parent = material_instance.get_editor_property("parent")
            if parent:
                return parent.get_path_name()
            return None
        except Exception as e:
            unreal.log_warning(f"부모 머티리얼 경로 가져오기 실패: {e}")
            return None
    
    @staticmethod
    def _get_project_dir() -> str:
        """프로젝트 디렉토리 경로 가져오기"""
        return unreal.Paths.project_dir()
    
    @staticmethod
    def _convert_package_path_to_file_path(package_path: str) -> str:
        """
        Package 경로를 파일 시스템 경로로 변환
        
        Args:
            package_path: /Game/Path/To/Material 형태의 패키지 경로
            
        Returns:
            Saved/Material/Path/To/Material 형태의 파일 시스템 경로
        """
        if not package_path:
            return "Saved/Material"
        
        # /Game을 Saved/Material로 치환
        if package_path.startswith("/Game"):
            file_path = package_path.replace("/Game", "Saved/Material", 1)
            
            # Unreal Engine에서 때때로 Asset이 PackageName.AssetName 형태로 나타남
            # 예: /Game/NewMaterial.NewMaterial -> /Game/NewMaterial
            if '.' in file_path:
                path_parts = file_path.split('.')
                if len(path_parts) == 2:
                    # 마지막 부분이 폴더명과 같은지 확인
                    folder_name = path_parts[0].split('/')[-1]
                    asset_name = path_parts[1]
                    if folder_name == asset_name:
                        file_path = path_parts[0]
            
            return file_path
        else:
            # /Game으로 시작하지 않는 경우 그대로 Saved/Material에 추가
            return f"Saved/Material/{package_path.lstrip('/')}"
    
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
    def _get_preset_folder_path(material_path: str) -> str:
        """머티리얼 경로에서 프리셋 폴더 경로 생성"""
        if not material_path:
            return MaterialInstancePresetManager.PRESET_FOLDER
        
        # Package path를 파일 시스템 경로로 변환
        file_path = MaterialInstancePresetManager._convert_package_path_to_file_path(material_path)
        
        # Preset 폴더 추가
        return os.path.join(file_path, MaterialInstancePresetManager.PRESET_FOLDER)
    
    @staticmethod
    def save_root_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: str
    ) -> Optional[str]:
        """
        머티리얼 인스턴스를 루트 프리셋으로 저장
        
        루트 프리셋은 최상위 머티리얼 폴더의 Preset 폴더에 저장되어 
        같은 루트 머티리얼을 가진 인스턴스들이 공유
        
        Args:
            material_instance: 저장할 머티리얼 인스턴스
            preset_name: 프리셋 이름 (필수)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 루트 머티리얼 경로 가져오기 (백업 메서드 사용)
            root_path = MaterialInstancePresetManager._get_root_material_path(material_instance)
            if not root_path:
                unreal.log_error("루트 머티리얼을 찾을 수 없습니다.")
                return None
            
            # 직렬화
            data = MaterialInstanceSerializer.serialize(material_instance)
            
            # 파일 경로 생성: Saved/Material/{RootMaterialPath}/Preset/{PresetName}.json
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(root_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            # 디렉토리 생성
            if not MaterialInstancePresetManager._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ 루트 프리셋 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"루트 프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def save_parent_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: str
    ) -> Optional[str]:
        """
        머티리얼 인스턴스를 부모 프리셋으로 저장
        
        부모 프리셋은 직접 부모 머티리얼 폴더의 Preset 폴더에 저장되어 
        같은 부모 머티리얼을 가진 인스턴스들이 공유
        
        Args:
            material_instance: 저장할 머티리얼 인스턴스
            preset_name: 프리셋 이름 (필수)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 부모 머티리얼 경로 가져오기 (백업 메서드 사용)
            parent_path = MaterialInstancePresetManager._get_parent_material_path(material_instance)
            if not parent_path:
                unreal.log_error("부모 머티리얼을 찾을 수 없습니다.")
                return None
            
            # 직렬화
            data = MaterialInstanceSerializer.serialize(material_instance)
            
            # 파일 경로 생성: Saved/Material/{ParentMaterialPath}/Preset/{PresetName}.json
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(parent_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            # 디렉토리 생성
            if not MaterialInstancePresetManager._ensure_directory_exists(file_path):
                return None
            
            # JSON 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"✅ 부모 프리셋 저장 완료: {file_path}")
            return file_path
            
        except Exception as e:
            unreal.log_error(f"부모 프리셋 저장 실패: {e}")
            return None
    
    @staticmethod
    def load_root_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: str
    ) -> bool:
        """
        루트 프리셋을 로드하여 머티리얼 인스턴스에 적용
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            preset_name: 로드할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            # 루트 머티리얼 경로 가져오기 (백업 메서드 사용)
            root_path = MaterialInstancePresetManager._get_root_material_path(material_instance)
            if not root_path:
                unreal.log_error("루트 머티리얼을 찾을 수 없습니다.")
                return False
            
            # 파일 경로 생성
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(root_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"루트 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = MaterialInstanceSerializer.deserialize(material_instance, data)
            
            if success:
                unreal.log(f"✅ 루트 프리셋 로드 완료: {preset_name}")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"루트 프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def load_parent_preset(
        material_instance: unreal.MaterialInstance,
        preset_name: str
    ) -> bool:
        """
        부모 프리셋을 로드하여 머티리얼 인스턴스에 적용
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            preset_name: 로드할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            # 부모 머티리얼 경로 가져오기 (백업 메서드 사용)
            parent_path = MaterialInstancePresetManager._get_parent_material_path(material_instance)
            if not parent_path:
                unreal.log_error("부모 머티리얼을 찾을 수 없습니다.")
                return False
            
            # 파일 경로 생성
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(parent_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            # JSON 로드
            if not os.path.exists(file_path):
                unreal.log_error(f"부모 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 역직렬화
            success = MaterialInstanceSerializer.deserialize(material_instance, data)
            
            if success:
                unreal.log(f"✅ 부모 프리셋 로드 완료: {preset_name}")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"부모 프리셋 로드 실패: {e}")
            return False
    
    @staticmethod
    def list_root_presets(material_instance: unreal.MaterialInstance) -> List[str]:
        """
        사용 가능한 루트 프리셋 목록 가져오기
        
        Args:
            material_instance: 머티리얼 인스턴스
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            # 루트 머티리얼 경로 가져오기 (백업 메서드 사용)
            root_path = MaterialInstancePresetManager._get_root_material_path(material_instance)
            if not root_path:
                return []
            
            # 프리셋 폴더 경로
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(root_path)
            full_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder
            )
            
            if not os.path.exists(full_path):
                return []
            
            # 프리셋 파일 찾기
            presets = []
            for file in os.listdir(full_path):
                if file.endswith(".json"):
                    preset_name = file.replace(".json", "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"루트 프리셋 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def list_parent_presets(material_instance: unreal.MaterialInstance) -> List[str]:
        """
        사용 가능한 부모 프리셋 목록 가져오기
        
        Args:
            material_instance: 머티리얼 인스턴스
            
        Returns:
            프리셋 이름 리스트
        """
        try:
            # 부모 머티리얼 경로 가져오기 (백업 메서드 사용)
            parent_path = MaterialInstancePresetManager._get_parent_material_path(material_instance)
            if not parent_path:
                return []
            
            # 프리셋 폴더 경로
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(parent_path)
            full_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder
            )
            
            if not os.path.exists(full_path):
                return []
            
            # 프리셋 파일 찾기
            presets = []
            for file in os.listdir(full_path):
                if file.endswith(".json"):
                    preset_name = file.replace(".json", "")
                    presets.append(preset_name)
            
            return sorted(presets)
            
        except Exception as e:
            unreal.log_error(f"부모 프리셋 목록 가져오기 실패: {e}")
            return []
    
    @staticmethod
    def delete_root_preset(material_instance: unreal.MaterialInstance, preset_name: str) -> bool:
        """
        루트 프리셋 파일 삭제
        
        Args:
            material_instance: 머티리얼 인스턴스
            preset_name: 삭제할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            root_path = MaterialInstancePresetManager._get_root_material_path(material_instance)
            if not root_path:
                return False
            
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(root_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            if os.path.exists(file_path):
                os.remove(file_path)
                unreal.log(f"✅ 루트 프리셋 삭제 완료: {preset_name}")
                return True
            else:
                unreal.log_warning(f"루트 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
                
        except Exception as e:
            unreal.log_error(f"루트 프리셋 삭제 실패: {e}")
            return False
    
    @staticmethod
    def delete_parent_preset(material_instance: unreal.MaterialInstance, preset_name: str) -> bool:
        """
        부모 프리셋 파일 삭제
        
        Args:
            material_instance: 머티리얼 인스턴스
            preset_name: 삭제할 프리셋 이름
            
        Returns:
            성공 여부
        """
        try:
            parent_path = MaterialInstancePresetManager._get_parent_material_path(material_instance)
            if not parent_path:
                return False
            
            preset_folder = MaterialInstancePresetManager._get_preset_folder_path(parent_path)
            file_name = f"{preset_name}.json"
            file_path = os.path.join(
                MaterialInstancePresetManager._get_project_dir(),
                preset_folder,
                file_name
            )
            
            if os.path.exists(file_path):
                os.remove(file_path)
                unreal.log(f"✅ 부모 프리셋 삭제 완료: {preset_name}")
                return True
            else:
                unreal.log_warning(f"부모 프리셋 파일을 찾을 수 없음: {file_path}")
                return False
                
        except Exception as e:
            unreal.log_error(f"부모 프리셋 삭제 실패: {e}")
            return False


# 사용 예제
if __name__ == "__main__":
    """
    예제: 선택된 머티리얼 인스턴스로 루트/부모 프리셋 관리
    """
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    for asset in selected_assets:
        if isinstance(asset, unreal.MaterialInstance):
            print(f"\n{'='*60}")
            print(f"머티리얼 인스턴스: {asset.get_name()}")
            print(f"{'='*60}")
            
            # 루트 프리셋 저장 (예제)
            root_preset_path = MaterialInstancePresetManager.save_root_preset(asset, "default_root")
            if root_preset_path:
                print(f"✅ 루트 프리셋 저장됨: {root_preset_path}")
            
            # 부모 프리셋 저장 (예제)
            parent_preset_path = MaterialInstancePresetManager.save_parent_preset(asset, "default_parent")
            if parent_preset_path:
                print(f"✅ 부모 프리셋 저장됨: {parent_preset_path}")
            
            # 사용 가능한 프리셋 목록
            root_presets = MaterialInstancePresetManager.list_root_presets(asset)
            parent_presets = MaterialInstancePresetManager.list_parent_presets(asset)
            print(f"📋 루트 프리셋: {root_presets}")
            print(f"📋 부모 프리셋: {parent_presets}")
            
            # 프리셋 로드 예제 (주석 처리)
            # if "default_root" in root_presets:
            #     MaterialInstancePresetManager.load_root_preset(asset, "default_root")
            #     print("✅ 루트 프리셋 'default_root' 로드됨")
            # 
            # if "default_parent" in parent_presets:
            #     MaterialInstancePresetManager.load_parent_preset(asset, "default_parent")
            #     print("✅ 부모 프리셋 'default_parent' 로드됨")

    # 실제 사용 예제
    print("\n" + "="*80)
    print("📁 Material Instance Preset 폴더 구조 예제")
    print("="*80)
    print("예시: 구조")
    print("  - 루트 머티리얼: /Game/Materials/BaseMaterial")
    print("  - 부모 머티리얼: /Game/Materials/MetalMaterial (BaseMaterial의 인스턴스)")
    print("  - 자식 머티리얼: /Game/Materials/IronMaterial (MetalMaterial의 인스턴스)")
    print()
    print("루트 프리셋 저장 위치:")
    print("  Project/")
    print("  └── Saved/")
    print("      └── Material/")
    print("          └── Materials/")
    print("              └── BaseMaterial/")
    print("                  └── Preset/")
    print("                      ├── metal_base.json")
    print("                      ├── wood_base.json")
    print("                      └── glass_base.json")
    print()
    print("부모 프리셋 저장 위치:")
    print("  Project/")
    print("  └── Saved/")
    print("      └── Material/")
    print("          └── Materials/")
    print("              └── MetalMaterial/")
    print("                  └── Preset/")
    print("                      ├── iron.json")
    print("                      ├── copper.json")
    print("                      └── gold.json")
    print()
    print("💡 개념:")
    print("   • 루트 프리셋: 최상위 머티리얼을 기준으로 하는 프리셋")
    print("   • 부모 프리셋: 직접 부모 머티리얼을 기준으로 하는 프리셋")
    print("   • 같은 루트/부모를 가진 모든 인스턴스가 해당 프리셋을 공유")
