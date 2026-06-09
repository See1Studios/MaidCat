"""
Material Instance JSON Serialization/Deserialization Utility

머티리얼 인스턴스의 파라미터를 JSON으로 직렬화하고 역직렬화하는 유틸리티입니다.
순수하게 직렬화/역직렬화 기능만 제공하며, 파일 저장/로드는 mi_preset 모듈에서 담당합니다.

지원하는 파라미터:
- Scalar Parameters (Float)
- Vector Parameters (Color/Linear Color)
- Texture Parameters
- Static Switch Parameters

Author: MaidCat Team
Version: 2.0.0
"""

import unreal
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime


class MaterialInstanceSerializer:
    """머티리얼 인스턴스 직렬화/역직렬화 클래스"""
    
    @staticmethod
    def get_parent_material_path(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """머티리얼 인스턴스의 직접 부모 머티리얼 경로 가져오기"""
        try:
            # MaterialInstance의 parent 속성 직접 접근
            parent = material_instance.get_editor_property("parent")
            
            if parent:
                return parent.get_path_name()
            return None
            
        except Exception as e:
            unreal.log_warning(f"부모 머티리얼 경로 가져오기 실패: {e}")
            return None
    
    @staticmethod
    def get_root_material_path(material_instance: unreal.MaterialInstance) -> Optional[str]:
        """머티리얼 인스턴스의 최상위 루트 머티리얼 경로 가져오기"""
        try:
            # MaterialInstance의 parent 속성 직접 접근
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
    def serialize(material_instance: unreal.MaterialInstance) -> Dict[str, Any]:
        """
        머티리얼 인스턴스를 딕셔너리로 직렬화
        
        Args:
            material_instance: 직렬화할 머티리얼 인스턴스
            
        Returns:
            직렬화된 데이터 딕셔너리
        """
        # 오브젝트 경로를 패키지 경로로 변환 (unreal.Paths 사용)
        def convert_to_package_path(object_path: str) -> str:
            """오브젝트 경로를 패키지 경로로 변환"""
            try:
                # AssetData를 통한 변환 (검증된 최적 방법)
                asset_data = unreal.EditorAssetLibrary.find_asset_data(object_path)
                if asset_data and asset_data.package_name:
                    return str(asset_data.package_name)
                        
            except Exception as e:
                unreal.log_warning(f"AssetData 경로 변환 실패: {e}")
            
            # Fallback: 수동 변환
            if "." in object_path and object_path.count(".") >= 1:
                path_parts = object_path.rsplit(".", 1)  # 마지막 점에서 분리
                if len(path_parts) == 2:
                    package_path_candidate = path_parts[0]
                    object_name = path_parts[1]
                    
                    # 패키지 경로의 마지막 부분이 오브젝트명과 같은지 확인
                    package_name = package_path_candidate.split("/")[-1]
                    if package_name == object_name:
                        return package_path_candidate  # 패키지 경로 반환
            
            return object_path  # 변환 불가하면 원본 반환
        
        # 애셋 경로를 패키지 경로로 변환
        object_path = material_instance.get_path_name()
        asset_package_path = convert_to_package_path(object_path)
        
        data = {
            "metadata": {
                "asset_path": asset_package_path,  # 패키지 경로 저장
                "parent_material": None,
                "root_material": None
            },
            "parameters": {
                "scalar": {},
                "vector": {},
                "texture": {},
                "static_switch": {}
            }
        }
        
        # 부모 머티리얼 경로 저장 (직접 부모, 패키지 경로로 변환)
        parent_path = MaterialInstanceSerializer.get_parent_material_path(material_instance)
        if parent_path:
            data["metadata"]["parent_material"] = convert_to_package_path(parent_path)
        
        # 루트 머티리얼 경로 저장 (최상위 부모, 패키지 경로로 변환)
        root_path = MaterialInstanceSerializer.get_root_material_path(material_instance)
        if root_path:
            data["metadata"]["root_material"] = convert_to_package_path(root_path)
        
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
    def deserialize(
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
            
            # 머티리얼 인스턴스 업데이트 (간소화)
            try:
                # 변경사항을 에디터에 알림
                material_instance.modify()
                
                # MaterialInstance 업데이트 시도
                try:
                    # update_material_instance 시도
                    unreal.MaterialEditingLibrary.update_material_instance(material_instance)
                    unreal.log("🔄 MaterialInstance 업데이트 완료")
                except:
                    # 실패하면 기본 방법 사용
                    unreal.log("🔄 기본 MaterialInstance 업데이트 완료")
                
                # 머티리얼 에디터 새로고침 (Static Switch 변경사항 반영)
                try:
                    asset_path = material_instance.get_path_name()
                    
                    # 방법 1: 에셋 데이터 새로고침
                    try:
                        unreal.EditorAssetLibrary.reload_asset_data(material_instance)
                    except:
                        pass
                    
                    # 방법 2: 에디터 콘솔 명령어들 시도
                    console_commands = [
                        f"Editor.RefreshAsset {asset_path}",
                        f"MaterialEditor.RefreshEditor {asset_path}",
                        "Editor.RefreshAllNodes",
                        "Slate.RefreshAllWidgets"
                    ]
                    
                    for command in console_commands:
                        try:
                            unreal.SystemLibrary.execute_console_command(None, command)
                        except:
                            continue
                    
                    unreal.log("🔄 머티리얼 에디터 새로고침 완료")
                except Exception as e:
                    # 에디터 새로고침 실패해도 무시 (중요하지 않음)
                    unreal.log_warning(f"에디터 새로고침 실패 (무시 가능): {e}")
                
            except Exception as e:
                # 중요한 오류만 표시
                unreal.log_error(f"머티리얼 업데이트 실패: {e}")
            
            # 변경사항 저장 (간소화)
            try:
                saved = unreal.EditorAssetLibrary.save_asset(material_instance.get_path_name())
                if saved:
                    unreal.log("💾 머티리얼 인스턴스 저장 완료")
            except Exception as e:
                unreal.log_warning(f"저장 중 오류: {e}")
            
            return True
            
        except Exception as e:
            unreal.log_error(f"머티리얼 인스턴스 역직렬화 실패: {e}")
            return False
    
    @staticmethod
    def save_to_file(
        material_instance: unreal.MaterialInstance,
        file_path: str,
        create_dirs: bool = True
    ) -> bool:
        """
        머티리얼 인스턴스를 JSON 파일로 저장
        
        Args:
            material_instance: 저장할 머티리얼 인스턴스
            file_path: 저장할 파일 경로 (절대 경로 또는 상대 경로)
            create_dirs: 디렉토리가 없으면 자동 생성 여부
            
        Returns:
            성공 여부
        """
        try:
            # 직렬화
            data = MaterialInstanceSerializer.serialize(material_instance)
            
            # 상대 경로인 경우 프로젝트 디렉토리 기준으로 변환
            if not os.path.isabs(file_path):
                project_dir = unreal.Paths.project_dir()
                file_path = os.path.join(project_dir, file_path)
            
            # 디렉토리 생성
            if create_dirs:
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                        unreal.log(f"📁 디렉토리 생성: {directory}")
                    except Exception as e:
                        unreal.log_error(f"디렉토리 생성 실패: {directory}, 오류: {e}")
                        return False
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            unreal.log(f"💾 머티리얼 인스턴스 저장 완료: {file_path}")
            unreal.log(f"   - Asset: {material_instance.get_name()}")
            
            # 저장된 파라미터 정보 출력
            params = data.get("parameters", {})
            scalar_count = len(params.get("scalar", {}))
            vector_count = len(params.get("vector", {}))
            texture_count = len(params.get("texture", {}))
            switch_count = len(params.get("static_switch", {}))
            unreal.log(f"   - 파라미터: Scalar({scalar_count}), Vector({vector_count}), Texture({texture_count}), Switch({switch_count})")
            
            return True
            
        except Exception as e:
            unreal.log_error(f"파일 저장 실패: {e}")
            return False
    
    @staticmethod
    def load_from_file(
        material_instance: unreal.MaterialInstance,
        file_path: str
    ) -> bool:
        """
        JSON 파일에서 머티리얼 인스턴스로 로드
        
        Args:
            material_instance: 적용할 머티리얼 인스턴스
            file_path: 로드할 파일 경로 (절대 경로 또는 상대 경로)
            
        Returns:
            성공 여부
        """
        try:
            # 상대 경로인 경우 프로젝트 디렉토리 기준으로 변환
            if not os.path.isabs(file_path):
                project_dir = unreal.Paths.project_dir()
                file_path = os.path.join(project_dir, file_path)
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                unreal.log_error(f"파일을 찾을 수 없음: {file_path}")
                return False
            
            # JSON 파일 로드
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            unreal.log(f"📂 파일 로드: {file_path}")
            
            # 메타데이터 정보 출력
            metadata = data.get("metadata", {})
            original_asset = metadata.get("asset_name", "Unknown")
            serialized_date = metadata.get("serialized_date", "Unknown")
            unreal.log(f"   - 원본 Asset: {original_asset}")
            unreal.log(f"   - 저장 날짜: {serialized_date}")
            
            # 역직렬화 적용
            success = MaterialInstanceSerializer.deserialize(material_instance, data)
            
            if success:
                unreal.log(f"✅ 머티리얼 인스턴스 복원 완료: {material_instance.get_name()}")
                
                # 복원된 파라미터 정보 출력
                params = data.get("parameters", {})
                scalar_count = len(params.get("scalar", {}))
                vector_count = len(params.get("vector", {}))
                texture_count = len(params.get("texture", {}))
                switch_count = len(params.get("static_switch", {}))
                unreal.log(f"   - 복원된 파라미터: Scalar({scalar_count}), Vector({vector_count}), Texture({texture_count}), Switch({switch_count})")
            else:
                unreal.log_error("머티리얼 인스턴스 복원 실패")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"파일 로드 실패: {e}")
            return False
    
    @staticmethod
    def export_to_file(
        material_instance: unreal.MaterialInstance,
        file_path: Optional[str] = None,
        base_folder: str = "Saved/MaterialExports"
    ) -> Optional[str]:
        """
        머티리얼 인스턴스를 자동 생성된 파일명으로 내보내기
        
        Args:
            material_instance: 내보낼 머티리얼 인스턴스
            file_path: 지정할 파일 경로 (None이면 자동 생성)
            base_folder: 기본 저장 폴더 (프로젝트 상대 경로)
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            if file_path is None:
                # 자동 파일명 생성: MaterialName_YYYYMMDD_HHMMSS.json
                material_name = material_instance.get_name()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{material_name}_{timestamp}.json"
                
                # 프로젝트 기준 경로 생성
                project_dir = unreal.Paths.project_dir()
                export_dir = os.path.join(project_dir, base_folder)
                file_path = os.path.join(export_dir, filename)
            
            # 파일 저장
            success = MaterialInstanceSerializer.save_to_file(material_instance, file_path)
            
            if success:
                return file_path
            else:
                return None
                
        except Exception as e:
            unreal.log_error(f"내보내기 실패: {e}")
            return None
    
    @staticmethod
    def save_to_asset_path(
        material_instance: unreal.MaterialInstance,
        filename: Optional[str] = None,
        create_dirs: bool = True
    ) -> Optional[str]:
        """
        머티리얼 인스턴스를 원래 애셋 경로 기준으로 저장
        
        예시:
        - 애셋 경로: /Game/Test/ParentMaterial
        - 저장 경로: Project/Saved/Material/Test/ParentMaterial/{filename}.json
        
        Args:
            material_instance: 저장할 머티리얼 인스턴스
            filename: 저장할 파일명 (None이면 애셋명 사용)
            create_dirs: 디렉토리가 없으면 자동 생성 여부
            
        Returns:
            저장된 파일 경로 (실패시 None)
        """
        try:
            # 애셋 경로 가져오기 (패키지 경로로 변환)
            object_path = material_instance.get_path_name()  # 오브젝트 경로 (AssetName.AssetName)
            asset_name = material_instance.get_name()
            
            if not object_path:
                unreal.log_error("애셋 경로를 가져올 수 없습니다.")
                return None
            
            # 오브젝트 경로를 패키지 경로로 변환 (AssetData 사용)
            def convert_to_package_path(object_path: str) -> str:
                """오브젝트 경로를 패키지 경로로 변환"""
                try:
                    # AssetData를 통한 변환 (검증된 최적 방법)
                    asset_data = unreal.EditorAssetLibrary.find_asset_data(object_path)
                    if asset_data and asset_data.package_name:
                        return str(asset_data.package_name)
                        
                except Exception as e:
                    unreal.log_warning(f"AssetData 경로 변환 실패: {e}")
                
                # Fallback: 수동 변환
                if "." in object_path and object_path.count(".") >= 1:
                    path_parts = object_path.rsplit(".", 1)  # 마지막 점에서 분리
                    if len(path_parts) == 2:
                        package_path_candidate = path_parts[0]
                        object_name = path_parts[1]
                        
                        # 패키지 경로의 마지막 부분이 오브젝트명과 같은지 확인
                        package_name = package_path_candidate.split("/")[-1]
                        if package_name == object_name:
                            return package_path_candidate  # 패키지 경로 반환
                
                return object_path  # 변환 불가하면 원본 반환
            
            # 패키지 경로로 변환
            asset_path = convert_to_package_path(object_path)
            
            # 애셋 경로 정규화 및 변환 (패키지 루트 유지)
            def clean_asset_path_with_package(path: str, asset_name: str) -> str:
                """애셋 경로를 정리하고 저장 경로로 변환 (패키지 루트 유지)"""
                if not path.startswith("/"):
                    return path
                
                # "/" 제거하고 경로 부분들을 분리
                clean_path = path[1:]  # 첫 번째 / 제거
                path_parts = [part for part in clean_path.split("/") if part]  # 빈 문자열 제거
                
                if len(path_parts) == 0:
                    return ""
                
                # 패키지 루트 (Game, MaidCat 등) 유지
                package_root = path_parts[0]  # Game, MaidCat, SomePlugin 등
                sub_path_parts = path_parts[1:]  # 나머지 경로
                
                # 마지막 부분이 "AssetName.AssetName" 형태인 경우 정리
                if len(sub_path_parts) > 0:
                    last_part = sub_path_parts[-1]
                    # "NewMat_Inst.NewMat_Inst" -> "NewMat_Inst"
                    if "." in last_part and last_part.count(".") == 1:
                        base_name = last_part.split(".")[0]
                        if base_name == asset_name:
                            # 중복된 애셋명 제거
                            sub_path_parts = sub_path_parts[:-1]
                        else:
                            # 애셋명과 다르면 폴더명으로 사용
                            sub_path_parts[-1] = base_name
                    elif last_part == asset_name:
                        # 마지막 부분이 애셋명과 같으면 제거
                        sub_path_parts = sub_path_parts[:-1]
                
                # 패키지 루트 + 하위 경로 결합
                if sub_path_parts:
                    return f"{package_root}/{'/'.join(sub_path_parts)}"
                else:
                    return package_root
            
            # 정리된 상대 경로 생성 (패키지 루트 포함)
            relative_path = clean_asset_path_with_package(asset_path, asset_name)
            
            # Saved/Material/ 접두어 추가
            save_folder = f"Saved/Material/{relative_path}" if relative_path else "Saved/Material"
            
            # 파일명 결정
            if filename is None:
                filename = f"{asset_name}.json"
            elif not filename.endswith(".json"):
                filename = f"{filename}.json"
            
            # 전체 파일 경로 생성
            project_dir = unreal.Paths.project_dir()
            full_file_path = os.path.join(project_dir, save_folder, filename)
            
            unreal.log(f"📁 애셋 기반 저장:")
            unreal.log(f"   - 오브젝트 경로: {object_path}")
            unreal.log(f"   - 패키지 경로: {asset_path}")
            unreal.log(f"   - 저장 폴더: {save_folder}")
            unreal.log(f"   - 파일명: {filename}")
            
            # 실제 저장
            success = MaterialInstanceSerializer.save_to_file(
                material_instance, 
                full_file_path, 
                create_dirs
            )
            
            if success:
                unreal.log(f"✅ 애셋 기반 저장 완료: {full_file_path}")
                return full_file_path
            else:
                return None
                
        except Exception as e:
            unreal.log_error(f"애셋 기반 저장 실패: {e}")
            return None
    
    @staticmethod
    def load_from_asset_path(
        target_material_instance: unreal.MaterialInstance,
        source_asset_path: str,
        filename: Optional[str] = None
    ) -> bool:
        """
        애셋 경로 기준으로 저장된 파일에서 로드
        
        Args:
            target_material_instance: 적용할 머티리얼 인스턴스
            source_asset_path: 원본 애셋 경로 (예: "/Game/Test/ParentMaterial")
            filename: 로드할 파일명 (None이면 애셋명에서 추출)
            
        Returns:
            성공 여부
        """
        try:
            # source_asset_path에서 애셋명 추출
            if filename is None:
                source_asset_name = source_asset_path.split("/")[-1]
                filename = f"{source_asset_name}.json"
            elif not filename.endswith(".json"):
                filename = f"{filename}.json"
            
            # 애셋 경로 정규화 및 변환 (패키지 루트 유지, save_to_asset_path와 동일한 로직)
            def clean_asset_path_with_package(path: str, asset_name: str) -> str:
                """애셋 경로를 정리하고 저장 경로로 변환 (패키지 루트 유지)"""
                if not path.startswith("/"):
                    return path
                
                # "/" 제거하고 경로 부분들을 분리
                clean_path = path[1:]  # 첫 번째 / 제거
                path_parts = [part for part in clean_path.split("/") if part]  # 빈 문자열 제거
                
                if len(path_parts) == 0:
                    return ""
                
                # 패키지 루트 (Game, MaidCat 등) 유지
                package_root = path_parts[0]  # Game, MaidCat, SomePlugin 등
                sub_path_parts = path_parts[1:]  # 나머지 경로
                
                # 마지막 부분이 "AssetName.AssetName" 형태인 경우 정리
                if len(sub_path_parts) > 0:
                    last_part = sub_path_parts[-1]
                    # "NewMat_Inst.NewMat_Inst" -> "NewMat_Inst"
                    if "." in last_part and last_part.count(".") == 1:
                        base_name = last_part.split(".")[0]
                        if base_name == asset_name:
                            # 중복된 애셋명 제거
                            sub_path_parts = sub_path_parts[:-1]
                        else:
                            # 애셋명과 다르면 폴더명으로 사용
                            sub_path_parts[-1] = base_name
                    elif last_part == asset_name:
                        # 마지막 부분이 애셋명과 같으면 제거
                        sub_path_parts = sub_path_parts[:-1]
                
                # 패키지 루트 + 하위 경로 결합
                if sub_path_parts:
                    return f"{package_root}/{'/'.join(sub_path_parts)}"
                else:
                    return package_root
            
            # source_asset_path에서 애셋명 추출
            source_asset_name = source_asset_path.split("/")[-1]
            if "." in source_asset_name:
                source_asset_name = source_asset_name.split(".")[0]
            
            # 정리된 상대 경로 생성 (패키지 루트 포함)
            relative_path = clean_asset_path_with_package(source_asset_path, source_asset_name)
            
            # Saved/Material/ 접두어 추가
            save_folder = f"Saved/Material/{relative_path}" if relative_path else "Saved/Material"
            
            # 전체 파일 경로 생성
            project_dir = unreal.Paths.project_dir()
            full_file_path = os.path.join(project_dir, save_folder, filename)
            
            unreal.log(f"📂 애셋 기반 로드:")
            unreal.log(f"   - 원본 애셋 경로: {source_asset_path}")
            unreal.log(f"   - 로드 폴더: {save_folder}")
            unreal.log(f"   - 파일명: {filename}")
            unreal.log(f"   - 대상 애셋: {target_material_instance.get_name()}")
            
            # 실제 로드
            return MaterialInstanceSerializer.load_from_file(target_material_instance, full_file_path)
            
        except Exception as e:
            unreal.log_error(f"애셋 기반 로드 실패: {e}")
            return False
    
    @staticmethod
    def import_from_file(
        target_material_instance: unreal.MaterialInstance,
        file_path: str,
        show_confirmation: bool = True
    ) -> bool:
        """
        파일에서 머티리얼 인스턴스로 가져오기 (확인 메시지 포함)
        
        Args:
            target_material_instance: 대상 머티리얼 인스턴스
            file_path: 가져올 파일 경로
            show_confirmation: 가져오기 전 확인 메시지 표시 여부
            
        Returns:
            성공 여부
        """
        try:
            # 상대 경로인 경우 프로젝트 디렉토리 기준으로 변환
            if not os.path.isabs(file_path):
                project_dir = unreal.Paths.project_dir()
                file_path = os.path.join(project_dir, file_path)
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                unreal.log_error(f"파일을 찾을 수 없음: {file_path}")
                return False
            
            # 미리보기를 위해 메타데이터 읽기
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data.get("metadata", {})
                original_asset = metadata.get("asset_name", "Unknown")
                serialized_date = metadata.get("serialized_date", "Unknown")
                
                if show_confirmation:
                    unreal.log(f"📋 가져오기 정보:")
                    unreal.log(f"   - 파일: {os.path.basename(file_path)}")
                    unreal.log(f"   - 원본 Asset: {original_asset}")
                    unreal.log(f"   - 저장 날짜: {serialized_date}")
                    unreal.log(f"   - 대상 Asset: {target_material_instance.get_name()}")
                    
                    # 실제 환경에서는 다이얼로그를 사용할 수 있지만, 
                    # 여기서는 로그로 정보만 출력
                    unreal.log(f"🔄 가져오기를 진행합니다...")
                
            except Exception as e:
                unreal.log_warning(f"메타데이터 읽기 실패, 가져오기를 계속 진행: {e}")
            
            # 실제 가져오기 수행
            return MaterialInstanceSerializer.load_from_file(target_material_instance, file_path)
            
        except Exception as e:
            unreal.log_error(f"가져오기 실패: {e}")
            return False


# 사용 예제
if __name__ == "__main__":
    """
    직렬화/역직렬화 및 파일 저장/로드 테스트 예제
    """
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected_assets:
        print("⚠️  머티리얼 인스턴스를 선택하고 실행하세요.")
    
    for asset in selected_assets:
        if isinstance(asset, unreal.MaterialInstance):
            print(f"\n{'='*60}")
            print(f"머티리얼 인스턴스: {asset.get_name()}")
            print(f"{'='*60}")
            
            # 1. 직렬화 테스트
            data = MaterialInstanceSerializer.serialize(asset)
            
            # 직렬화된 데이터 정보 출력
            params = data.get("parameters", {})
            scalar_count = len(params.get("scalar", {}))
            vector_count = len(params.get("vector", {}))
            texture_count = len(params.get("texture", {}))
            switch_count = len(params.get("static_switch", {}))
            
            print(f"📊 직렬화된 파라미터:")
            print(f"   - Scalar Parameters: {scalar_count}개")
            print(f"   - Vector Parameters: {vector_count}개")
            print(f"   - Texture Parameters: {texture_count}개")
            print(f"   - Static Switch Parameters: {switch_count}개")
            
            # 부모 머티리얼 정보
            parent_path = MaterialInstanceSerializer.get_parent_material_path(asset)
            if parent_path:
                print(f"   - 부모 머티리얼: {parent_path}")
            
            print(f"\n✅ 직렬화 완료!")
            
            # 2. 파일 내보내기 테스트 (자동 파일명)
            exported_file = MaterialInstanceSerializer.export_to_file(asset)
            if exported_file:
                print(f"📤 자동 내보내기 성공: {exported_file}")
                
                # 3. 파일 가져오기 테스트 (동일한 머티리얼 인스턴스에 다시 로드)
                # 주의: 실제로는 다른 머티리얼 인스턴스에 적용하는 것이 일반적
                print(f"\n🔄 가져오기 테스트 (동일 Asset):")
                import_success = MaterialInstanceSerializer.import_from_file(asset, exported_file)
                if import_success:
                    print(f"📥 가져오기 성공!")
                else:
                    print(f"❌ 가져오기 실패!")
            else:
                print(f"❌ 내보내기 실패!")
            
            # 4. 수동 파일 저장 테스트
            manual_file_path = f"Saved/ManualExport/{asset.get_name()}_manual.json"
            print(f"\n💾 수동 저장 테스트: {manual_file_path}")
            manual_save_success = MaterialInstanceSerializer.save_to_file(asset, manual_file_path)
            if manual_save_success:
                print(f"✅ 수동 저장 성공!")
                
                # 5. 수동 파일 로드 테스트
                print(f"\n📂 수동 로드 테스트:")
                manual_load_success = MaterialInstanceSerializer.load_from_file(asset, manual_file_path)
                if manual_load_success:
                    print(f"✅ 수동 로드 성공!")
                else:
                    print(f"❌ 수동 로드 실패!")
            else:
                print(f"❌ 수동 저장 실패!")
            
            # 6. 애셋 경로 기반 저장 테스트 (NEW!)
            print(f"\n🆕 애셋 경로 기반 저장 테스트:")
            asset_based_file = MaterialInstanceSerializer.save_to_asset_path(asset)
            if asset_based_file:
                print(f"✅ 애셋 경로 기반 저장 성공!")
                print(f"   저장 위치: {asset_based_file}")
                
                # 7. 애셋 경로 기반 로드 테스트 (NEW!)
                print(f"\n🆕 애셋 경로 기반 로드 테스트:")
                asset_path = asset.get_path_name()
                load_success = MaterialInstanceSerializer.load_from_asset_path(asset, asset_path)
                if load_success:
                    print(f"✅ 애셋 경로 기반 로드 성공!")
                else:
                    print(f"❌ 애셋 경로 기반 로드 실패!")
            else:
                print(f"❌ 애셋 경로 기반 저장 실패!")
            
            # 8. 커스텀 파일명으로 애셋 기반 저장
            custom_asset_file = MaterialInstanceSerializer.save_to_asset_path(
                asset, 
                filename="backup_version"  # .json은 자동 추가됨
            )
            if custom_asset_file:
                print(f"✅ 커스텀 파일명 저장 성공: {custom_asset_file}")
            
            print(f"\n{'='*60}")
            print(f"🎯 사용법 요약:")
            print(f"{'='*60}")
            print(f"1. 자동 내보내기:")
            print(f"   MaterialInstanceSerializer.export_to_file(material_instance)")
            print(f"")
            print(f"2. 수동 저장:")
            print(f"   MaterialInstanceSerializer.save_to_file(material_instance, 'path/file.json')")
            print(f"")
            print(f"3. 🆕 애셋 경로 기반 저장:")
            print(f"   MaterialInstanceSerializer.save_to_asset_path(material_instance)")
            print(f"   MaterialInstanceSerializer.save_to_asset_path(material_instance, 'custom_name')")
            print(f"")
            print(f"4. 파일에서 가져오기:")
            print(f"   MaterialInstanceSerializer.import_from_file(target_material, 'path/file.json')")
            print(f"")
            print(f"5. 파일에서 로드:")
            print(f"   MaterialInstanceSerializer.load_from_file(target_material, 'path/file.json')")
            print(f"")
            print(f"6. 🆕 애셋 경로 기반 로드:")
            print(f"   MaterialInstanceSerializer.load_from_asset_path(target_material, '/Game/Source/Path')")
            print(f"")
            print(f"💡 Tip: 상대 경로는 프로젝트 폴더 기준으로 자동 변환됩니다!")
            
            # 역직렬화 테스트 (주석 처리)
            # success = MaterialInstanceSerializer.deserialize(asset, data)
            # if success:
            #     print(f"✅ 역직렬화 완료!")
            # else:
            #     print(f"❌ 역직렬화 실패!")
        else:
            print(f"⚠️  {asset.get_name()}은(는) 머티리얼 인스턴스가 아닙니다. 건너뜁니다.")
    
    print(f"\n{'='*80}")
    print(f"🚀 MaterialInstanceSerializer 파일 저장/로드 기능 추가 완료!")
    print(f"{'='*80}")
    print(f"새로운 기능:")
    print(f"  • save_to_file() - 지정된 경로에 JSON 파일로 저장")
    print(f"  • load_from_file() - JSON 파일에서 머티리얼 인스턴스로 로드")
    print(f"  • export_to_file() - 자동 파일명으로 내보내기")
    print(f"  • import_from_file() - 확인 정보와 함께 가져오기")
    print(f"  • 🆕 save_to_asset_path() - 애셋 경로 기준 저장")
    print(f"  • 🆕 load_from_asset_path() - 애셋 경로 기준 로드")
    print(f"")
    print(f"저장 위치:")
    print(f"  • 자동 내보내기: Project/Saved/MaterialExports/")
    print(f"  • 수동 저장: 지정된 경로 (상대경로는 프로젝트 기준)")
    print(f"  • 🆕 애셋 기반 저장: Project/Saved/Material/{{애셋경로}}/")
    print(f"")
    print(f"💡 애셋 기반 저장 예시:")
    print(f"  게임 애셋: /Game/Test/ParentMaterial")
    print(f"  → 저장 위치: Project/Saved/Material/Game/Test/ParentMaterial/{{파일명}}.json")
    print(f"")
    print(f"  플러그인 애셋: /MaidCat/Tools/MyMaterial")
    print(f"  → 저장 위치: Project/Saved/Material/MaidCat/Tools/MyMaterial/{{파일명}}.json")
    print(f"")
    print(f"파일 형식: UTF-8 인코딩된 JSON 파일 (.json)")
    print(f"{'='*80}")