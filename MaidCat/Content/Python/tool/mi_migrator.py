"""
Material Instance Parameter Migration Tool

머티리얼 인스턴스 파라미터를 새로운 머티리얼로 마이그레이션하는 도구
"""

import unreal
import tool.mi_serializer as serializer
from typing import Dict, Any, Optional
import json


class VectorWrapper:
    """HLSL 스타일 벡터 컴포넌트 접근을 위한 래퍼 클래스"""
    
    def __init__(self, linear_color: unreal.LinearColor):
        self._color = linear_color
        # HLSL 스타일 접근
        self.x = linear_color.r
        self.y = linear_color.g
        self.z = linear_color.b
        self.w = linear_color.a
        # 기존 스타일 유지
        self.r = linear_color.r
        self.g = linear_color.g
        self.b = linear_color.b
        self.a = linear_color.a
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y}, {self.z}, {self.w})"


class MigrationTable:
    """파라미터 마이그레이션 테이블"""
    
    def __init__(self):
        self.parameter_mappings = {}
        self.new_parent_material = None
    
    def set_new_parent_material(self, material_path: str):
        self.new_parent_material = material_path
    
    def add_parameter_mapping(self, new_param_name: str, expression: str, 
                            param_type: str = "scalar", old_param_aliases: Optional[Dict[str, str]] = None):
        self.parameter_mappings[new_param_name] = {
            "expression": expression,
            "type": param_type,
            "aliases": old_param_aliases or {}
        }
    
    def get_mapping(self, new_param_name: str) -> Optional[Dict[str, Any]]:
        return self.parameter_mappings.get(new_param_name)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "new_parent_material": self.new_parent_material,
            "parameter_mappings": self.parameter_mappings
        }
    
    def from_dict(self, data: Dict[str, Any]):
        self.new_parent_material = data.get("new_parent_material")
        self.parameter_mappings = data.get("parameter_mappings", {})
    
    def save_to_file(self, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.from_dict(json.load(f))
    
    @classmethod
    def from_file(cls, file_path: str) -> 'MigrationTable':
        """파일 경로에서 마이그레이션 테이블 생성"""
        table = cls()
        table.load_from_file(file_path)
        return table


class ParameterExpressionEvaluator:
    """파라미터 표현식 평가 클래스"""
    
    @staticmethod
    def evaluate_expression(expression: str, variables: Dict[str, Any]) -> Any:
        try:
            # HLSL/C 스타일 연산자를 Python 스타일로 변환
            processed_expression = expression
            processed_expression = processed_expression.replace('!', 'not ')
            processed_expression = processed_expression.replace('&&', ' and ')
            processed_expression = processed_expression.replace('||', ' or ')
            
            # 안전한 표현식 평가를 위한 허용된 함수들
            safe_dict = {
                "__builtins__": {},
                "min": min, "max": max, "abs": abs, "round": round, "pow": pow,
                "sqrt": lambda x: x ** 0.5,
                "clamp": lambda x, min_val, max_val: max(min_val, min(x, max_val)),
                # 언리얼 벡터 파라미터는 LinearColor (RGBA) 전용
                "float4": lambda x, y, z, w=1.0: unreal.LinearColor(r=x, g=y, b=z, a=w)
            }
            
            # 변수들을 safe_dict에 추가
            for var_name, var_value in variables.items():
                safe_dict[var_name] = var_value
            
            return eval(processed_expression, safe_dict)
            
        except Exception as e:
            unreal.log_error(f"표현식 평가 실패: {expression}, 오류: {e}")
            return None
    
    @staticmethod
    def prepare_variables(old_params: Dict[str, Any], aliases: Dict[str, str]) -> Dict[str, Any]:
        variables = {}
        
        for alias, param_name in aliases.items():
            if param_name in old_params.get("scalar", {}):
                param_data = old_params["scalar"][param_name]
                value = param_data.get("value", 0.0) if isinstance(param_data, dict) else param_data
                variables[alias] = float(value)
            
            elif param_name in old_params.get("vector", {}):
                param_data = old_params["vector"][param_name]
                if isinstance(param_data, dict) and "value" in param_data:
                    color_data = param_data["value"]
                else:
                    color_data = param_data
                
                color = unreal.LinearColor(r=color_data["r"], g=color_data["g"], b=color_data["b"], a=color_data["a"])
                variables[alias] = VectorWrapper(color)
            
            elif param_name in old_params.get("texture", {}):
                param_data = old_params["texture"][param_name]
                texture_path = param_data.get("value") if isinstance(param_data, dict) else param_data
                variables[alias] = texture_path
            
            elif param_name in old_params.get("static_switch", {}):
                param_data = old_params["static_switch"][param_name]
                value = param_data.get("value", False) if isinstance(param_data, dict) else param_data
                variables[alias] = bool(value)
            
            else:
                unreal.log_warning(f"파라미터 '{param_name}' (별칭: '{alias}')를 찾을 수 없습니다.")
                variables[alias] = None
        
        return variables


class MaterialInstanceMigrator:
    """머티리얼 인스턴스 마이그레이션 메인 클래스"""
    
    def __init__(self):
        self.serializer = serializer.MaterialInstanceSerializer()
    
    def migrate_material_instance(self, material_instance: unreal.MaterialInstance, migration_table: MigrationTable) -> bool:
        try:
            unreal.log(f"🔄 머티리얼 인스턴스 마이그레이션 시작: {material_instance.get_name()}")
            
            # 1. 기존 MI를 JSON으로 직렬화
            old_data = self.serializer.serialize(material_instance)
            unreal.log("✅ 기존 파라미터 직렬화 완료")
            
            # 2. 새로운 부모 머티리얼로 변경
            if migration_table.new_parent_material:
                success = self._change_parent_material(material_instance, migration_table.new_parent_material)
                if not success:
                    return False
                unreal.log("✅ 부모 머티리얼 변경 완료")
            
            # 3. 파라미터 매핑 및 값 변환
            new_params = self._transform_parameters(old_data["parameters"], migration_table)
            
            # 4. 새로운 파라미터 데이터 구성
            new_data = {
                "metadata": old_data["metadata"].copy(),
                "parameters": new_params
            }
            
            # 새 부모 머티리얼 정보 업데이트 (패키지 경로로 변환)
            if migration_table.new_parent_material:
                new_data["metadata"]["parent_material"] = serializer.convert_to_package_path(migration_table.new_parent_material)
            
            # 5. 변환된 파라미터를 MI에 적용
            success = self.serializer.deserialize(material_instance, new_data)
            
            if success:
                unreal.log("✅ 머티리얼 인스턴스 마이그레이션 완료")
            else:
                unreal.log_error("❌ 파라미터 적용 실패")
            
            return success
            
        except Exception as e:
            unreal.log_error(f"❌ 머티리얼 인스턴스 마이그레이션 실패: {e}")
            return False
    
    def _change_parent_material(self, material_instance: unreal.MaterialInstance, new_parent_path: str) -> bool:
        try:
            # 패키지 경로로 변환 (필요한 경우)
            package_path = serializer.convert_to_package_path(new_parent_path)
            
            # 새 부모 머티리얼 로드
            new_parent = unreal.EditorAssetLibrary.load_asset(package_path)
            if not new_parent:
                unreal.log_error(f"새 부모 머티리얼을 찾을 수 없습니다: {package_path}")
                return False
            
            # 부모 머티리얼 설정
            material_instance.set_editor_property("parent", new_parent)
            material_instance.modify()
            
            unreal.log(f"부모 머티리얼 변경 완료: {new_parent.get_name()}")
            return True
            
        except Exception as e:
            unreal.log_error(f"부모 머티리얼 변경 실패 ({new_parent_path}): {e}")
            return False
    
    def _transform_parameters(self, old_params: Dict[str, Any], migration_table: MigrationTable) -> Dict[str, Any]:
        new_params = {"scalar": {}, "vector": {}, "texture": {}, "static_switch": {}}
        evaluator = ParameterExpressionEvaluator()
        
        for new_param_name, mapping in migration_table.parameter_mappings.items():
            try:
                expression = mapping["expression"]
                param_type = mapping["type"]
                aliases = mapping["aliases"]
                
                # 변수 준비 및 표현식 평가
                variables = evaluator.prepare_variables(old_params, aliases)
                result = evaluator.evaluate_expression(expression, variables)
                
                if result is not None:
                    if param_type == "scalar":
                        new_params["scalar"][new_param_name] = {"value": float(result), "override": True}
                    
                    elif param_type == "vector":
                        if isinstance(result, unreal.LinearColor):
                            color = result
                        elif isinstance(result, VectorWrapper):
                            color = result._color
                        else:
                            unreal.log_warning(f"Vector 파라미터 '{new_param_name}'의 결과가 벡터가 아닙니다: {type(result)}")
                            continue
                        
                        new_params["vector"][new_param_name] = {
                            "value": {"r": color.r, "g": color.g, "b": color.b, "a": color.a},
                            "override": True
                        }
                    
                    elif param_type == "texture":
                        new_params["texture"][new_param_name] = {"value": str(result) if result else None, "override": True}
                    
                    elif param_type == "static_switch":
                        new_params["static_switch"][new_param_name] = {"value": bool(result), "override": True}
                    
                    unreal.log(f"✅ 파라미터 변환 완료: {new_param_name} = {result}")
                
            except Exception as e:
                unreal.log_error(f"파라미터 '{new_param_name}' 변환 실패: {e}")
        
        return new_params


def migrate_selected_materials(migration_table_or_path):
    """선택된 머티리얼 인스턴스들을 마이그레이션
    
    Args:
        migration_table_or_path: MigrationTable 객체 또는 JSON 파일 경로
    """
    # 파라미터가 문자열이면 파일 경로로 간주하여 로드
    if isinstance(migration_table_or_path, str):
        migration_table = MigrationTable.from_file(migration_table_or_path)
        unreal.log(f"📄 마이그레이션 테이블 로드: {migration_table_or_path}")
    else:
        migration_table = migration_table_or_path
    
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    migrator = MaterialInstanceMigrator()
    
    material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
    
    if not material_instances:
        unreal.log_warning("⚠️ 선택된 머티리얼 인스턴스가 없습니다.")
        return
    
    unreal.log(f"🎯 {len(material_instances)}개의 머티리얼 인스턴스 마이그레이션 시작")
    
    success_count = 0
    for mi in material_instances:
        unreal.log(f"🔄 마이그레이션 중: {mi.get_name()}")
        
        success = migrator.migrate_material_instance(mi, migration_table)
        if success:
            success_count += 1
    
    unreal.log(f"\n🎉 마이그레이션 완료: {success_count}/{len(material_instances)} 성공")