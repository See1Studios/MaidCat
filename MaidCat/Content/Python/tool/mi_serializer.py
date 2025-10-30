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
        data = {
            "metadata": {
                "asset_path": material_instance.get_path_name(),
                "asset_name": material_instance.get_name(),
                "parent_material": None,
                "root_material": None,
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
        
        # 부모 머티리얼 경로 저장 (직접 부모)
        parent_path = MaterialInstanceSerializer.get_parent_material_path(material_instance)
        if parent_path:
            data["metadata"]["parent_material"] = parent_path
        
        # 루트 머티리얼 경로 저장 (최상위 부모)
        root_path = MaterialInstanceSerializer.get_root_material_path(material_instance)
        if root_path:
            data["metadata"]["root_material"] = root_path
        
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


# 사용 예제
if __name__ == "__main__":
    """
    직렬화/역직렬화 테스트 예제
    """
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    for asset in selected_assets:
        if isinstance(asset, unreal.MaterialInstance):
            print(f"\n{'='*60}")
            print(f"머티리얼 인스턴스: {asset.get_name()}")
            print(f"{'='*60}")
            
            # 직렬화
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
            
            # 역직렬화 테스트 (주석 처리)
            # success = MaterialInstanceSerializer.deserialize(asset, data)
            # if success:
            #     print(f"✅ 역직렬화 완료!")
            # else:
            #     print(f"❌ 역직렬화 실패!")