"""
Material Instance Migration Toolkit

머티리얼 인스턴스 마이그레이션을 위한 종합 툴킷

주요 기능:
1. 배치 마이그레이션 워크플로우: 폴더 단위 대량 마이그레이션
2. 마이그레이션 테이블 생성/관리: 파라미터 매핑 테이블 
3. 블루프린트 노출 함수들: UI 툴 개발용 API
4. 유틸리티 함수들: 애셋 에디터 새로고침, 검증 등
5. 테스트 및 디버깅 도구들

사용 예시:
- batch_migrate_materials(): 전체 배치 마이그레이션
- bp_*() 함수들: 블루프린트에서 호출 가능
- create_*_migration_table(): 다양한 테스트 테이블 생성
"""

import unreal
from tool.mi_migrator import MigrationTable, MaterialInstanceMigrator
from tool.mi_serializer import MaterialInstanceSerializer
import os
import json
from typing import List, Optional

# =============================================================================
# 상수 정의
# =============================================================================

# 테스트용 머티리얼 경로
TEST_FOLDER_PATH = "/MaidCat/MigrationTest/Test"
OLD_PARENT_MATERIAL = "/MaidCat/MigrationTest/Material/OldMat" 
NEW_PARENT_MATERIAL = "/MaidCat/MigrationTest/Material/NewMat"

# 기본 테이블 이름들
DEFAULT_TABLE_NAME = "test_migration_table"
REVERSE_TABLE_NAME = "reverse_test_migration_table"
TEMP_TABLE_NAME = "temp_migration_table"

# UI 상수들
SEPARATOR_WIDTH = 80


class MaterialPathManager:
    """머티리얼 마이그레이션 경로 관리 통합 클래스"""
    
    def __init__(self):
        self._project_dir = None
        self._base_paths = {
            "migration_table": "Saved/Material/MigrationTable",
            "batch_migration": "Saved/Material/BatchMigration", 
            "original": "01_Original",
            "migrated": "02_Migrated"
        }
    
    @property
    def project_dir(self) -> str:
        """프로젝트 디렉토리 (캐시됨)"""
        if self._project_dir is None:
            self._project_dir = unreal.SystemLibrary.get_project_directory()
        return self._project_dir
    
    def get_migration_table_folder(self) -> str:
        """마이그레이션 테이블 폴더 경로"""
        return os.path.join(self.project_dir, self._base_paths["migration_table"])
    
    def get_migration_table_path(self, table_name: str) -> str:
        """마이그레이션 테이블 파일 경로"""
        if not table_name.endswith('.json'):
            table_name += '.json'
        return os.path.join(self.get_migration_table_folder(), table_name)
    
    def get_batch_migration_folder(self) -> str:
        """배치 마이그레이션 작업 폴더 경로"""
        return os.path.join(self.project_dir, self._base_paths["batch_migration"])
    
    def get_original_folder(self, work_folder: str = None) -> str: # type: ignore
        """원본 JSON 저장 폴더"""
        base = work_folder or self.get_batch_migration_folder()
        return os.path.join(base, self._base_paths["original"])
    
    def get_migrated_folder(self, work_folder: str = None) -> str: # type: ignore
        """마이그레이션된 JSON 저장 폴더"""
        base = work_folder or self.get_batch_migration_folder()
        return os.path.join(base, self._base_paths["migrated"])
    
    @staticmethod
    def convert_to_package_path(object_path: str) -> str:
        """오브젝트 경로를 패키지 경로로 변환"""
        if not object_path:
            return ""
        
        # 이미 패키지 경로인 경우 (. 이 없는 경우)
        if '.' not in object_path:
            return object_path
        
        # /Game/Path/Asset.Asset -> /Game/Path/Asset
        if object_path.startswith('/'):
            parts = object_path.split('.')
            return parts[0]
        
        return object_path
    
    def resolve_migration_table(self, migration_table_or_path) -> MigrationTable:
        """마이그레이션 테이블 해석 (객체, 경로, 이름 모두 지원)"""
        if isinstance(migration_table_or_path, str):
            # 테이블 이름인지 확인 (경로 구분자가 없으면 테이블 이름)
            if '/' not in migration_table_or_path and '\\' not in migration_table_or_path:
                # 테이블 이름 -> 전체 경로 구성
                table_file_path = self.get_migration_table_path(migration_table_or_path)
                unreal.log(f"📄 테이블 이름 -> 경로: '{migration_table_or_path}' -> '{table_file_path}'")
                return MigrationTable.from_file(table_file_path)
            else:
                # 전체 파일 경로
                unreal.log(f"📄 마이그레이션 테이블 로드: {migration_table_or_path}")
                return MigrationTable.from_file(migration_table_or_path)
        else:
            # MigrationTable 객체
            unreal.log("📄 MigrationTable 객체 사용")
            return migration_table_or_path
    
    def ensure_folders(self, *folder_paths):
        """폴더들 생성 보장"""
        for folder in folder_paths:
            os.makedirs(folder, exist_ok=True)


# 전역 경로 관리자 인스턴스
_path_manager = MaterialPathManager()

# =============================================================================
# 테스트 테이블 생성 함수들
# =============================================================================

def create_test_migration_table() -> MigrationTable:
    """기본 테스트용 마이그레이션 테이블 생성 (OldMat -> NewMat)"""
    table = MigrationTable()
    table.set_new_parent_material(NEW_PARENT_MATERIAL)
    
    table.add_parameter_mapping(
        new_param_name="NewScalar",
        expression="a * 0.5", 
        param_type="scalar",
        old_param_aliases={"a": "OldScalar"}
    )
    
    table.add_parameter_mapping(
        new_param_name="NewColor",
        expression="float4(a.x * 0.5, a.y * 0.5, a.z * 0.5, a.w * 0.5)",
        param_type="vector",
        old_param_aliases={"a": "OldColor"}
    )
    
    table.add_parameter_mapping(
        new_param_name="NewTex",
        expression="a",
        param_type="texture",
        old_param_aliases={"a": "OldTex"}
    )
    
    table.add_parameter_mapping(
        new_param_name="NewSwitch",
        expression="!a",
        param_type="static_switch",
        old_param_aliases={"a": "OldSwitch"}
    )
    
    # 자동 저장
    table_folder = _path_manager.get_migration_table_folder()
    _path_manager.ensure_folders(table_folder)
    file_path = _path_manager.get_migration_table_path(DEFAULT_TABLE_NAME)
    table.save_to_file(file_path)
    unreal.log(f"✅ 기본 테스트 테이블 저장: {file_path}")
    
    return table


def create_reverse_test_migration_table() -> MigrationTable:
    """역방향 테스트용 마이그레이션 테이블 생성 (NewMat -> OldMat)"""
    table = MigrationTable()
    table.set_new_parent_material(OLD_PARENT_MATERIAL)
    
    # 역방향 파라미터 매핑 (NewMat의 파라미터들 -> OldMat의 파라미터들)
    table.add_parameter_mapping(
        new_param_name="OldScalar",
        expression="a * 2.0",  # 역변환: 0.5에서 1.0으로 (원래가 a * 0.5였으므로)
        param_type="scalar",
        old_param_aliases={"a": "NewScalar"}
    )
    
    table.add_parameter_mapping(
        new_param_name="OldColor", 
        expression="float4(a.x * 2.0, a.y * 2.0, a.z * 2.0, a.w)",  # RGB 2배, Alpha 유지
        param_type="vector",
        old_param_aliases={"a": "NewColor"}
    )
    
    table.add_parameter_mapping(
        new_param_name="OldTex",
        expression="a",  # 텍스처는 동일하게 유지
        param_type="texture",
        old_param_aliases={"a": "NewTex"}
    )
    
    table.add_parameter_mapping(
        new_param_name="OldSwitch",
        expression="!a",  # 스위치 반전
        param_type="static_switch",
        old_param_aliases={"a": "NewSwitch"}
    )
    
    # 테이블 저장
    table_folder = _path_manager.get_migration_table_folder()
    _path_manager.ensure_folders(table_folder)
    table_file = _path_manager.get_migration_table_path(REVERSE_TABLE_NAME)
    table.save_to_file(table_file)
    unreal.log(f"✅ 역방향 테이블 저장: {table_file}")
    
    return table


def analyze_json_parameters(json_file_path: str):
    """JSON 파일의 파라미터들을 분석하여 출력"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        unreal.log(f"📊 JSON 파일 분석: {os.path.basename(json_file_path)}")
        
        # 파라미터 섹션 확인
        if "parameters" in data:
            params = data["parameters"]
            unreal.log(f"🔍 발견된 파라미터들:")
            
            for param_type in ["scalar", "vector", "texture", "switch"]:
                if param_type in params and params[param_type]:
                    unreal.log(f"  📋 {param_type.upper()} 파라미터:")
                    for param_name, param_value in params[param_type].items():
                        unreal.log(f"    - '{param_name}': {param_value}")
        
        # 메타데이터 확인
        if "metadata" in data:
            meta = data["metadata"]
            unreal.log(f"📄 메타데이터:")
            if "parent_material" in meta:
                unreal.log(f"  - 부모 머티리얼: {meta['parent_material']}")
                
    except Exception as e:
        unreal.log_error(f"❌ JSON 분석 실패: {e}")


def create_math_migration_table() -> MigrationTable:
    """수학 연산 테스트 테이블"""
    table = MigrationTable()
    table.set_new_parent_material(NEW_PARENT_MATERIAL)
    
    table.add_parameter_mapping("NewScalar", "pow(a, 2) * 0.5", "scalar", {"a": "OldScalar"})
    table.add_parameter_mapping("NewColor", "float4(sqrt(a.x), a.y * 0.5, abs(a.z), a.w)", "vector", {"a": "OldColor"})
    
    return table


def create_logic_migration_table() -> MigrationTable:
    """논리 연산 테스트 테이블"""
    table = MigrationTable()
    table.set_new_parent_material(NEW_PARENT_MATERIAL)
    
    table.add_parameter_mapping("NewSwitch", "!a", "static_switch", {"a": "OldSwitch"})
    table.add_parameter_mapping("ComplexLogic", "a > 0.5 && !b", "static_switch", {"a": "OldScalar", "b": "OldSwitch"})
    
    return table


def create_conditional_migration_table() -> MigrationTable:
    """조건부 표현식 테스트 테이블"""
    table = MigrationTable()
    table.set_new_parent_material(NEW_PARENT_MATERIAL)
    
    table.add_parameter_mapping("NewScalar", "a * 2.0 if b else a * 0.5", "scalar", {"a": "OldScalar", "b": "OldSwitch"})
    table.add_parameter_mapping("NewTex", "a if b else '/Engine/EngineResources/Gray.Gray'", "texture", {"a": "OldTex", "b": "OldSwitch"})
    
    return table


def create_component_migration_table() -> MigrationTable:
    """벡터 컴포넌트 조작 테스트 테이블"""
    table = MigrationTable()
    table.set_new_parent_material(NEW_PARENT_MATERIAL)
    
    table.add_parameter_mapping("SwappedColor", "float4(a.z, a.y, a.x, a.w)", "vector", {"a": "OldColor"})
    table.add_parameter_mapping("MixedColor", "float4(a, b.x, b.y, b.z)", "vector", {"a": "OldScalar", "b": "OldColor"})
    table.add_parameter_mapping("Brightness", "(a.x + a.y + a.z) / 3.0", "scalar", {"a": "OldColor"})
    
    return table


# =============================================================================
# 테스트 및 유틸리티 함수들
# =============================================================================

def test_migration():
    """선택된 머티리얼 인스턴스들로 간단한 마이그레이션 테스트"""
    test_table = create_test_migration_table()
    
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
    
    if not material_instances:
        unreal.log_warning("⚠️ 머티리얼 인스턴스를 선택하고 다시 실행하세요.")
        return
    
    unreal.log(f"🎯 {len(material_instances)}개 머티리얼 인스턴스로 테스트 시작")
    
    migrator = MaterialInstanceMigrator()
    success_count = 0
    for mi in material_instances:
        unreal.log(f"🔄 마이그레이션 중: {mi.get_name()}")
        if migrator.migrate_material_instance(mi, test_table):
            success_count += 1
    
    unreal.log(f"🎉 마이그레이션 완료: {success_count}/{len(material_instances)} 성공")


def save_all_example_tables():
    """모든 예제 테이블을 개별 파일로 저장"""
    table_folder = _path_manager.get_migration_table_folder()
    _path_manager.ensure_folders(table_folder)
    
    examples = {
        "math_operations": create_math_migration_table(), 
        "logic_operations": create_logic_migration_table(),
        "conditional_expressions": create_conditional_migration_table(),
        "component_manipulation": create_component_migration_table()
    }
    
    for name, table in examples.items():
        file_path = _path_manager.get_migration_table_path(f"{name}_migration_table")
        table.save_to_file(file_path)
        unreal.log(f"✅ {name} 테이블 저장: {file_path}")
    
    unreal.log(f"🎉 총 {len(examples)}개 예제 테이블 저장 완료!")


# =============================================================================
# 배치 마이그레이션 워크플로우 함수들
# =============================================================================
def find_material_instances_by_parent(folder_path: str, parent_material_path: str) -> list:
    """
    특정 폴더에서 지정한 부모 머티리얼을 가진 머티리얼 인스턴스들을 찾기
    
    Args:
        folder_path: 검색할 폴더 경로 (예: "/Game/Materials")
        parent_material_path: 부모 머티리얼 경로 (예: "/Game/Materials/OldMat")
        
    Returns:
        머티리얼 인스턴스 에셋 리스트
    """
    from tool.mi_migrator import VectorWrapper, ParameterExpressionEvaluator
    import tool.mi_serializer as serializer
    
    material_instances = []
    
    # 폴더의 모든 에셋 가져오기 (대안 방법 사용)
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # ARFilter 대신 EditorAssetLibrary 사용
    all_assets = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=True, include_folder=False)
    unreal.log(f"🔍 폴더 '{folder_path}'에서 총 {len(all_assets)}개 에셋 발견")
    
    assets = []
    
    for asset_path in all_assets:
        # MaterialInstance만 필터링
        asset_data = asset_registry.get_asset_by_object_path(asset_path)
        if asset_data:
            class_name = asset_data.asset_class_path.asset_name
            unreal.log(f"   - 에셋: {asset_path} (클래스: {class_name})")
            if class_name == "MaterialInstanceConstant":
                assets.append(asset_data)
                unreal.log(f"     ✅ MaterialInstance 추가!")
    
    unreal.log(f"📊 필터링된 MaterialInstance: {len(assets)}개")
    
    # 부모 머티리얼이 일치하는 인스턴스들만 필터링
    parent_package_path = _path_manager.convert_to_package_path(parent_material_path)
    unreal.log(f"🎯 찾는 부모 머티리얼: {parent_package_path}")
    
    for asset_data in assets:
        # 에셋 로드
        asset = unreal.EditorAssetLibrary.load_asset(asset_data.package_name)
        if asset and isinstance(asset, unreal.MaterialInstance):
            # 부모 머티리얼 확인
            parent = asset.get_editor_property("parent")
            unreal.log(f"🔍 {asset.get_name()} 부모 확인:")
            if parent:
                actual_parent_path = parent.get_path_name()
                # 오브젝트 경로를 패키지 경로로 변환
                actual_parent_package_path = _path_manager.convert_to_package_path(actual_parent_path)
                
                unreal.log(f"   - 실제 부모 (오브젝트): '{actual_parent_path}'")
                unreal.log(f"   - 실제 부모 (패키지): '{actual_parent_package_path}'")
                unreal.log(f"   - 찾는 부모: '{parent_package_path}'")
                unreal.log(f"   - 일치 여부: {actual_parent_package_path == parent_package_path}")
                
                if actual_parent_package_path == parent_package_path:
                    material_instances.append(asset)
                    unreal.log(f"✅ 매칭 성공: {asset.get_name()} -> {parent.get_name()}")
            else:
                unreal.log(f"   - 부모 없음 (None)")
    
    unreal.log(f"🎯 총 {len(material_instances)}개의 머티리얼 인스턴스 발견")
    return material_instances


def serialize_material_instances_to_json(material_instances: list, output_folder: str) -> list:
    """
    머티리얼 인스턴스들을 JSON 파일로 직렬화
    
    Args:
        material_instances: 머티리얼 인스턴스 리스트
        output_folder: JSON 파일 저장 폴더 경로
        
    Returns:
        생성된 JSON 파일 경로 리스트
    """
    import tool.mi_serializer as serializer
    
    os.makedirs(output_folder, exist_ok=True)
    json_files = []
    migrator_serializer = serializer.MaterialInstanceSerializer()
    
    for mi in material_instances:
        try:
            # JSON으로 직렬화
            data = migrator_serializer.serialize(mi)
            
            # 파일 이름 생성 (에셋 이름 기반)
            safe_name = mi.get_name().replace(' ', '_')
            json_file_path = os.path.join(output_folder, f"{safe_name}.json")
            
            # JSON 파일 저장
            migrator_serializer.save_to_asset_path(mi, json_file_path)
            json_files.append(json_file_path)
            
            unreal.log(f"✅ 직렬화 완료: {mi.get_name()} -> {json_file_path}")
            
        except Exception as e:
            unreal.log_error(f"❌ 직렬화 실패: {mi.get_name()} - {e}")
    
    unreal.log(f"🎉 총 {len(json_files)}개 JSON 파일 생성 완료")
    return json_files


def migrate_json_files_with_table(json_files: list, migration_table_or_path, output_folder: str) -> list:
    """
    JSON 파일들을 마이그레이션 테이블로 변환
    
    Args:
        json_files: 원본 JSON 파일 경로 리스트
        migration_table_or_path: MigrationTable 객체 또는 JSON 파일 경로
        output_folder: 변환된 JSON 파일 저장 폴더
        
    Returns:
        변환된 JSON 파일 경로 리스트
    """
    from tool.mi_migrator import VectorWrapper, ParameterExpressionEvaluator
    import tool.mi_serializer as serializer
    
    # 파라미터 처리: 통합 경로 관리 사용
    migration_table = _path_manager.resolve_migration_table(migration_table_or_path)
    
    os.makedirs(output_folder, exist_ok=True)
    migrated_files = []
    evaluator = ParameterExpressionEvaluator()
    
    for json_file in json_files:
        try:
            # 원본 JSON 로드
            with open(json_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 파라미터 변환
            new_params = {"scalar": {}, "vector": {}, "texture": {}, "static_switch": {}}
            
            for new_param_name, mapping in migration_table.parameter_mappings.items():
                expression = mapping["expression"]
                param_type = mapping["type"]
                aliases = mapping["aliases"]
                
                # 변수 준비 및 표현식 평가
                variables = evaluator.prepare_variables(old_data["parameters"], aliases)
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
                            continue
                        new_params["vector"][new_param_name] = {
                            "value": {"r": color.r, "g": color.g, "b": color.b, "a": color.a},
                            "override": True
                        }
                    elif param_type == "texture":
                        new_params["texture"][new_param_name] = {"value": str(result) if result else None, "override": True}
                    elif param_type == "static_switch":
                        new_params["static_switch"][new_param_name] = {"value": bool(result), "override": True}
            
            # 새로운 데이터 구성
            new_data = {
                "metadata": old_data["metadata"].copy(),
                "parameters": new_params
            }
            
            # 새 부모 머티리얼 정보 업데이트
            if migration_table.new_parent_material:
                new_data["metadata"]["parent_material"] = _path_manager.convert_to_package_path(migration_table.new_parent_material)
            
            # 변환된 JSON 파일 저장
            base_name = os.path.basename(json_file)
            name_without_ext = os.path.splitext(base_name)[0]
            migrated_file = os.path.join(output_folder, f"{name_without_ext}_migrated.json")
            
            with open(migrated_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            migrated_files.append(migrated_file)
            unreal.log(f"✅ 마이그레이션 완료: {base_name} -> {migrated_file}")
            
        except Exception as e:
            unreal.log_error(f"❌ 마이그레이션 실패: {json_file} - {e}")
    
    unreal.log(f"🎉 총 {len(migrated_files)}개 마이그레이션 완료")
    return migrated_files


def change_material_parent_batch(material_instances: list, new_parent_material_path: str) -> list:
    """
    머티리얼 인스턴스들의 부모 머티리얼을 일괄 변경
    
    Args:
        material_instances: 머티리얼 인스턴스 리스트
        new_parent_material_path: 새 부모 머티리얼 경로
        
    Returns:
        성공적으로 변경된 머티리얼 인스턴스 리스트
    """
    success_instances = []
    package_path = _path_manager.convert_to_package_path(new_parent_material_path)
    
    # 새 부모 머티리얼 로드
    new_parent = unreal.EditorAssetLibrary.load_asset(package_path)
    if not new_parent:
        unreal.log_error(f"새 부모 머티리얼을 찾을 수 없습니다: {package_path}")
        return success_instances
    
    for mi in material_instances:
        try:
            # 부모 머티리얼 설정
            mi.set_editor_property("parent", new_parent)
            mi.modify()
            success_instances.append(mi)
            unreal.log(f"✅ 부모 변경 완료: {mi.get_name()} -> {new_parent.get_name()}")
            
        except Exception as e:
            unreal.log_error(f"❌ 부모 변경 실패: {mi.get_name()} - {e}")
    
    unreal.log(f"🎉 총 {len(success_instances)}개 부모 변경 완료")
    return success_instances


def apply_migrated_json_to_materials(material_instances: list, migrated_json_files: list) -> list:
    """
    마이그레이션된 JSON 파일들을 머티리얼 인스턴스들에 적용
    
    Args:
        material_instances: 머티리얼 인스턴스 리스트
        migrated_json_files: 마이그레이션된 JSON 파일 경로 리스트
        
    Returns:
        성공적으로 적용된 머티리얼 인스턴스 리스트
    """
    import tool.mi_serializer as serializer
    
    success_instances = []
    migrator_serializer = serializer.MaterialInstanceSerializer()
    
    # 파일명과 머티리얼 인스턴스 매칭을 위한 딕셔너리 생성
    mi_dict = {mi.get_name(): mi for mi in material_instances}
    
    for json_file in migrated_json_files:
        try:
            # 파일명에서 머티리얼 이름 추출 (suffix 제거)
            base_name = os.path.basename(json_file)
            name_without_ext = os.path.splitext(base_name)[0]
            original_name = name_without_ext.replace('_migrated', '')
            
            # 해당하는 머티리얼 인스턴스 찾기
            if original_name in mi_dict:
                mi = mi_dict[original_name]
                
                # JSON 데이터 로드 및 적용
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if migrator_serializer.deserialize(mi, data):
                    success_instances.append(mi)
                    unreal.log(f"✅ 파라미터 적용 완료: {mi.get_name()}")
                else:
                    unreal.log_error(f"❌ 파라미터 적용 실패: {mi.get_name()}")
            else:
                unreal.log_warning(f"⚠️ 해당하는 머티리얼 인스턴스를 찾을 수 없음: {original_name}")
                
        except Exception as e:
            unreal.log_error(f"❌ JSON 적용 실패: {json_file} - {e}")
    
    unreal.log(f"🎉 총 {len(success_instances)}개 파라미터 적용 완료")
    return success_instances


def batch_migrate_materials(folder_path: str, old_parent_material: str, migration_table_or_path, 
                          work_folder: str = None, refresh_editors: bool = True) -> bool:
    """
    전체 배치 마이그레이션 워크플로우 실행
    
    Args:
        folder_path: 검색할 폴더 경로
        old_parent_material: 기존 부모 머티리얼 경로
        migration_table_or_path: MigrationTable 객체 또는 JSON 파일 경로
        work_folder: 작업 파일 저장 폴더 (None이면 자동 생성)
        refresh_editors: 마이그레이션 후 열린 에디터 새로고침 여부
        
    Returns:
        성공 여부
    """
    try:
        # 파라미터 처리: 통합 경로 관리 사용
        migration_table = _path_manager.resolve_migration_table(migration_table_or_path)
        
        # 작업 폴더 설정
        if not work_folder:
            work_folder = _path_manager.get_batch_migration_folder()
        
        # 폴더 구성 (통합 경로 관리 사용)
        original_folder = _path_manager.get_original_folder(work_folder)
        migrated_folder = _path_manager.get_migrated_folder(work_folder)
        _path_manager.ensure_folders(work_folder, original_folder, migrated_folder)
        
        unreal.log("🚀 배치 마이그레이션 시작")
        
        # 1단계: 머티리얼 인스턴스 찾기
        unreal.log("\n📋 1단계: 머티리얼 인스턴스 검색")
        material_instances = find_material_instances_by_parent(folder_path, old_parent_material)
        if not material_instances:
            unreal.log_warning("⚠️ 해당하는 머티리얼 인스턴스를 찾을 수 없습니다.")
            return False
        

        
        # 2단계: JSON 직렬화
        unreal.log("\n💾 2단계: JSON 직렬화")
        json_files = serialize_material_instances_to_json(material_instances, original_folder)
        
        # 3단계: 마이그레이션
        unreal.log("\n🔄 3단계: 마이그레이션")
        migrated_files = migrate_json_files_with_table(json_files, migration_table, migrated_folder)
        
        # 4단계: 부모 머티리얼 변경
        unreal.log("\n🔗 4단계: 부모 머티리얼 변경")
        success_instances = change_material_parent_batch(material_instances, migration_table.new_parent_material)
        
        # 5단계: 마이그레이션된 파라미터 적용
        unreal.log("\n⚙️ 5단계: 파라미터 적용")
        final_instances = apply_migrated_json_to_materials(success_instances, migrated_files)
        
        # 6단계: 애셋 에디터 새로고침 (옵션)
        if refresh_editors:
            unreal.log("\n🔄 6단계: 애셋 에디터 새로고침")
            asset_editor_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
            refreshed_count = 0
            
            for mi in final_instances:
                try:
                    # 닫았다가 다시 열기
                    asset_editor_subsystem.close_all_editors_for_asset(mi)
                    asset_editor_subsystem.open_editor_for_assets([mi])
                    refreshed_count += 1
                    unreal.log(f"✅ 에디터 새로고침: {mi.get_name()}")
                except Exception as e:
                    unreal.log_error(f"❌ 에디터 새로고침 실패 {mi.get_name()}: {e}")
            
            if refreshed_count > 0:
                unreal.log(f"✅ {refreshed_count}개 애셋 에디터 새로고침 완료")
        
        unreal.log(f"\n🎉 배치 마이그레이션 완료!")
        unreal.log(f"   📁 작업 폴더: {work_folder}")
        unreal.log(f"   ✅ 성공: {len(final_instances)}/{len(material_instances)}개")
        
        return len(final_instances) > 0
        
    except Exception as e:
        unreal.log_error(f"❌ 배치 마이그레이션 실패: {e}")
        return False


def load_migration_table(file_path: str) -> MigrationTable:
    """JSON 파일에서 마이그레이션 테이블 로드"""
    table = MigrationTable()
    table.load_from_file(file_path)
    unreal.log(f"📄 마이그레이션 테이블 로드 완료: {file_path}")
    return table

# 메인 실행 코드
if __name__ == "__main__":
    print("\n" + "=" * SEPARATOR_WIDTH)
    print("MATERIAL INSTANCE MIGRATION TOOLKIT")
    print("=" * SEPARATOR_WIDTH)
    
    print("🧪 사용 가능한 테스트들:")
    print("   test_migration()                    - 간단한 기본 테스트")
    print("   save_all_example_tables()          - 모든 예제 테이블 생성")
    print("")
    print("🚀 배치 마이그레이션 함수들:")
    print("   find_material_instances_by_parent() - 특정 부모의 인스턴스 검색")
    print("   serialize_material_instances_to_json() - JSON 직렬화")
    print("   migrate_json_files_with_table()    - JSON 파일 마이그레이션")
    print("   change_material_parent_batch()     - 부모 머티리얼 일괄 변경")
    print("   apply_migrated_json_to_materials() - 마이그레이션 결과 적용")
    print("   batch_migrate_materials()          - 전체 워크플로우 실행")
    
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
    
    if material_instances:
        print(f"\n🎯 {len(material_instances)}개 머티리얼 인스턴스 선택됨 - 테스트 준비 완료!")
    else:
        print(f"\n⚠️ 테스트할 머티리얼 인스턴스를 먼저 선택하세요")
    
    print("\n" + "=" * SEPARATOR_WIDTH)


# 배치 마이그레이션 예제 함수
def example_batch_migration():
    """배치 마이그레이션 예제 실행"""
    # 테스트 마이그레이션 테이블 생성
    create_test_migration_table()
    
    # 배치 마이그레이션 실행 (테이블 이름으로 전달)
    success = batch_migrate_materials(
        folder_path=TEST_FOLDER_PATH,
        old_parent_material=OLD_PARENT_MATERIAL,
        migration_table_or_path=DEFAULT_TABLE_NAME
    )
    
    if success:
        unreal.log("🎉 배치 마이그레이션 예제 완료!")
    else:
        unreal.log_warning("⚠️ 배치 마이그레이션 실패 또는 대상 없음")


# =============================================================================
# 블루프린트 함수들 (startup/bp_material_migration.py로 이동됨)
# =============================================================================

# 블루프린트 함수들은 startup/bp_material_migration.py 파일로 이동되었습니다.
# 블루프린트에서 사용하려면 해당 모듈을 import 하세요:
# from startup.bp_material_migration import MaidCatMaterialMigrationLibrary

def refresh_selected_material_editors():
    """선택된 머티리얼 인스턴스들의 에디터를 새로고침"""
    try:
        selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
        material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
        
        if not material_instances:
            unreal.log_warning("⚠️ 선택된 머티리얼 인스턴스가 없습니다.")
            return 0
        
        asset_editor_subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        refreshed_count = 0
        
        for mi in material_instances:
            try:
                asset_editor_subsystem.close_all_editors_for_asset(mi)
                asset_editor_subsystem.open_editor_for_assets([mi])
                refreshed_count += 1
                unreal.log(f"✅ 에디터 새로고침: {mi.get_name()}")
            except Exception as e:
                unreal.log_error(f"❌ 에디터 새로고침 실패 {mi.get_name()}: {e}")
        
        unreal.log(f"🎉 {refreshed_count}개 머티리얼 에디터 새로고침 완료")
        return refreshed_count
        
    except Exception as e:
        unreal.log_error(f"❌ 에디터 새로고침 실패: {e}")
        return 0


if __name__ == "__main__":
    print("\n💡 사용 예시:")
    print("   example_batch_migration()           - 배치 마이그레이션 예제 실행")
    print("   refresh_selected_material_editors() - 선택된 머티리얼 에디터 새로고침")
    print("\n🎨 블루프린트 함수들:")
    print("   📁 위치: startup/bp_material_migration.py")
    print("   📋 카테고리: MaidCat Material|Migration")
    print("   🔧 함수들: create_empty_migration_table, add_parameter_mapping,")
    print("            save_migration_table, load_migration_table, get_table_info,")
    print("            list_migration_tables, test_migration_with_table,")
    print("            batch_migrate_materials, get_selected_material_instances,")
    print("            validate_expression")
    print("\n💡 블루프린트 사용법:")
    print("   1. 블루프린트에서 MaidCatMaterialMigrationLibrary 클래스 사용")
    print("   2. 함수들은 'MaidCat Material|Migration' 카테고리에서 찾기")
    print("   3. Call in Editor로 설정되어 에디터에서 바로 실행 가능")