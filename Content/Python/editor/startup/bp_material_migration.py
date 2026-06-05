"""
MaidCat Material Instance Migration Blueprint Functions
머티리얼 인스턴스 마이그레이션을 위한 블루프린트 함수들

이 모듈은 startup 폴더에 있어 Unreal Engine 시작 시 자동으로 로드됩니다.
블루프린트에서 'MaidCat Material|Migration' 카테고리로 함수들을 사용할 수 있습니다.
"""

import unreal
import os
from tool.mi_migrator import MigrationTable, MaterialInstanceMigrator

# 상수들
TEMP_TABLE_NAME = "temp_migration_table"

# 전역 경로 관리자 (mi_toolkit에서 가져오기)
def get_path_manager():
    """경로 관리자 인스턴스 가져오기"""
    from tool.mi_toolkit import _path_manager
    return _path_manager


# =============================================================================
# 블루프린트 노출 함수들
# =============================================================================

@unreal.uclass()
class MaidCatMaterialMigrationLibrary(unreal.BlueprintFunctionLibrary):
    """MaidCat Material Migration Blueprint Function Library"""

    @unreal.ufunction(static=True, ret=bool, params=[str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def create_empty_migration_table(new_parent_material_path: str) -> bool:
        """
        빈 마이그레이션 테이블 생성
        
        Args:
            new_parent_material_path: 새로운 부모 머티리얼 경로
            
        Returns:
            성공 여부
        """
        try:
            path_manager = get_path_manager()
            table = MigrationTable()
            table.set_new_parent_material(new_parent_material_path)
            
            # 임시 테이블로 저장
            table_file = path_manager.get_migration_table_path(TEMP_TABLE_NAME)
            path_manager.ensure_folders(path_manager.get_migration_table_folder())
            table.save_to_file(table_file)
            
            unreal.log(f"✅ 빈 마이그레이션 테이블 생성: {table_file}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ 빈 테이블 생성 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=bool, params=[str, str, str, str, str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def add_parameter_mapping(table_name: str, new_param_name: str, expression: str, 
                            param_type: str, old_param_name: str = "") -> bool:
        """
        마이그레이션 테이블에 파라미터 매핑 추가
        
        Args:
            table_name: 테이블 이름 (확장자 제외)
            new_param_name: 새 파라미터 이름
            expression: 변환 표현식
            param_type: 파라미터 타입 ("scalar", "vector", "texture", "static_switch")
            old_param_name: 기존 파라미터 이름 (비어있으면 new_param_name과 동일)
            
        Returns:
            성공 여부
        """
        try:
            path_manager = get_path_manager()
            
            # 테이블 로드
            table_file = path_manager.get_migration_table_path(table_name)
            table = MigrationTable.from_file(table_file)
            
            # 기존 파라미터 이름 설정
            if not old_param_name:
                old_param_name = new_param_name
            
            # 파라미터 매핑 추가
            table.add_parameter_mapping(
                new_param_name=new_param_name,
                expression=expression,
                param_type=param_type,
                old_param_aliases={"a": old_param_name}
            )
            
            # 테이블 저장
            table.save_to_file(table_file)
            
            unreal.log(f"✅ 파라미터 매핑 추가: {new_param_name} <- {old_param_name}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ 파라미터 매핑 추가 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=bool, params=[str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def save_migration_table(table_name: str) -> bool:
        """
        마이그레이션 테이블을 지정된 이름으로 저장
        
        Args:
            table_name: 저장할 테이블 이름 (확장자 제외)
            
        Returns:
            성공 여부
        """
        try:
            path_manager = get_path_manager()
            
            # 임시 테이블 로드
            temp_file = path_manager.get_migration_table_path(TEMP_TABLE_NAME)
            if not os.path.exists(temp_file):
                unreal.log_error("임시 테이블 파일이 없습니다. 먼저 테이블을 생성하세요.")
                return False
            
            # 새 이름으로 저장
            new_file = path_manager.get_migration_table_path(table_name)
            table = MigrationTable.from_file(temp_file)
            table.save_to_file(new_file)
            
            unreal.log(f"✅ 마이그레이션 테이블 저장: {new_file}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ 테이블 저장 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=bool, params=[str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def load_migration_table(table_name: str) -> bool:
        """
        저장된 마이그레이션 테이블을 임시 테이블로 로드
        
        Args:
            table_name: 로드할 테이블 이름 (확장자 제외)
            
        Returns:
            성공 여부
        """
        try:
            path_manager = get_path_manager()
            
            # 기존 테이블 로드
            source_file = path_manager.get_migration_table_path(table_name)
            if not os.path.exists(source_file):
                unreal.log_error(f"테이블 파일이 없습니다: {source_file}")
                return False
            
            # 임시 테이블로 복사
            temp_file = path_manager.get_migration_table_path(TEMP_TABLE_NAME)
            table = MigrationTable.from_file(source_file)
            table.save_to_file(temp_file)
            
            unreal.log(f"✅ 마이그레이션 테이블 로드: {table_name}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ 테이블 로드 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=str, params=[str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def get_table_info(table_name: str) -> str:
        """
        마이그레이션 테이블 정보 반환 (JSON 문자열)
        
        Args:
            table_name: 테이블 이름 (확장자 제외)
            
        Returns:
            테이블 정보 JSON 문자열 또는 빈 문자열
        """
        try:
            path_manager = get_path_manager()
            table_file = path_manager.get_migration_table_path(table_name)
            if not os.path.exists(table_file):
                return ""
            
            with open(table_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            unreal.log_error(f"❌ 테이블 정보 가져오기 실패: {e}")
            return ""

    @unreal.ufunction(static=True, ret=str, meta={"Category": "MaidCat Material|Migration", "CallInEditor": True}) 
    def list_migration_tables() -> str:
        """
        저장된 모든 마이그레이션 테이블 목록 반환 (쉼표로 구분된 문자열)
        
        Returns:
            테이블 이름들을 쉼표로 구분한 문자열
        """
        try:
            path_manager = get_path_manager()
            table_folder = path_manager.get_migration_table_folder()
            if not os.path.exists(table_folder):
                return ""
            
            table_files = []
            for file in os.listdir(table_folder):
                if file.endswith('.json'):
                    table_files.append(os.path.splitext(file)[0])
            
            return ",".join(table_files)
        except Exception as e:
            unreal.log_error(f"❌ 테이블 목록 가져오기 실패: {e}")
            return ""

    @unreal.ufunction(static=True, ret=bool, params=[str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def test_migration_with_table(table_name: str) -> bool:
        """
        선택된 머티리얼 인스턴스들로 마이그레이션 테스트
        
        Args:
            table_name: 테스트할 테이블 이름 (확장자 제외)
            
        Returns:
            성공 여부
        """
        try:
            path_manager = get_path_manager()
            
            # 선택된 머티리얼 인스턴스들 가져오기
            selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
            material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
            
            if not material_instances:
                unreal.log_error("선택된 머티리얼 인스턴스가 없습니다.")
                return False
            
            # 테이블 로드
            table_file = path_manager.get_migration_table_path(table_name)
            table = MigrationTable.from_file(table_file)
            
            # 마이그레이션 실행
            migrator = MaterialInstanceMigrator()
            success_count = 0
            
            for mi in material_instances:
                if migrator.migrate_material_instance(mi, table):
                    success_count += 1
                    unreal.log(f"✅ 마이그레이션 성공: {mi.get_name()}")
                else:
                    unreal.log_error(f"❌ 마이그레이션 실패: {mi.get_name()}")
            
            unreal.log(f"🎉 테스트 완료: {success_count}/{len(material_instances)}개 성공")
            return success_count > 0
        except Exception as e:
            unreal.log_error(f"❌ 마이그레이션 테스트 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=bool, params=[str, str, str, bool], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def batch_migrate_materials(folder_path: str, old_parent_material: str, 
                              table_name: str, refresh_editors: bool = True) -> bool:
        """
        배치 마이그레이션 실행 (블루프린트용)
        
        Args:
            folder_path: 검색할 폴더 경로
            old_parent_material: 기존 부모 머티리얼 경로  
            table_name: 사용할 테이블 이름 (확장자 제외)
            refresh_editors: 에디터 새로고침 여부
            
        Returns:
            성공 여부
        """
        try:
            from tool.mi_toolkit import batch_migrate_materials as batch_migrate
            return batch_migrate(
                folder_path=folder_path,
                old_parent_material=old_parent_material,
                migration_table_or_path=table_name,  # 테이블 이름으로 전달
                refresh_editors=refresh_editors
            )
        except Exception as e:
            unreal.log_error(f"❌ 배치 마이그레이션 실패: {e}")
            return False

    @unreal.ufunction(static=True, ret=str, meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def get_selected_material_instances() -> str:
        """
        선택된 머티리얼 인스턴스들의 경로 목록 반환 (쉼표로 구분된 문자열)
        
        Returns:
            머티리얼 인스턴스 경로들을 쉼표로 구분한 문자열
        """
        try:
            selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
            material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstance)]
            
            paths = [mi.get_path_name() for mi in material_instances]
            return ",".join(paths)
        except Exception as e:
            unreal.log_error(f"❌ 선택된 머티리얼 인스턴스 가져오기 실패: {e}")
            return ""

    @unreal.ufunction(static=True, ret=bool, params=[str, str], meta={"Category": "MaidCat Material|Migration", "CallInEditor": True})
    def validate_expression(expression: str, param_type: str) -> bool:
        """
        표현식 유효성 검사
        
        Args:
            expression: 검사할 표현식
            param_type: 파라미터 타입
            
        Returns:
            유효성 여부
        """
        try:
            from tool.mi_migrator import ParameterExpressionEvaluator
            evaluator = ParameterExpressionEvaluator()
            
            # 테스트용 변수 준비
            test_variables = {
                "a": 1.0 if param_type == "scalar" else unreal.LinearColor(1.0, 1.0, 1.0, 1.0)
            }
            
            # 표현식 평가 테스트
            result = evaluator.evaluate_expression(expression, test_variables)
            return result is not None
        except Exception as e:
            unreal.log_error(f"❌ 표현식 검증 실패: {e}")
            return False


def initialize_material_migration_library():
    """Material Migration 라이브러리 초기화"""
    unreal.log("🎨 MaidCat Material Migration Blueprint Library 초기화 완료!")
    unreal.log("사용 가능한 함수들:")
    unreal.log("  📋 MaidCat Material|Migration:")
    unreal.log("    - create_empty_migration_table: 빈 테이블 생성")
    unreal.log("    - add_parameter_mapping: 파라미터 매핑 추가")
    unreal.log("    - save_migration_table: 테이블 저장")
    unreal.log("    - load_migration_table: 테이블 로드")
    unreal.log("    - get_table_info: 테이블 정보 조회")
    unreal.log("    - list_migration_tables: 테이블 목록 조회")
    unreal.log("    - test_migration_with_table: 마이그레이션 테스트")
    unreal.log("    - batch_migrate_materials: 배치 마이그레이션")
    unreal.log("    - get_selected_material_instances: 선택된 머티리얼 조회")
    unreal.log("    - validate_expression: 표현식 유효성 검사")


if __name__ == "__main__":
    initialize_material_migration_library()