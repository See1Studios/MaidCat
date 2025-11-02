"""
UStruct 및 데이터 테이블 테스트 스크립트
"""
import unreal
import importlib
import sys
import os

# 디버깅을 위해 startup 모듈 재로드
if 'startup.bp_struct' in sys.modules:
    importlib.reload(sys.modules['startup.bp_struct'])

from startup.bp_struct import MaterialWebLinkRow, MaterialWebLinkRowSafe, MaterialSoftObj

def test_ustruct_creation():
    """UStruct가 제대로 생성되는지 테스트"""
    print("=== UStruct 생성 테스트 ===")
    
    try:
        # MaterialSoftObj 테스트
        print("MaterialSoftObj 테스트 중...")
        soft_obj = MaterialSoftObj()
        print(f"MaterialSoftObj 생성 성공: {type(soft_obj)}")
        
        # MaterialWebLinkRow 테스트
        print("MaterialWebLinkRow 테스트 중...")
        row = MaterialWebLinkRow()
        print(f"MaterialWebLinkRow 생성 성공: {type(row)}")
        print(f"속성들: {dir(row)}")
        
        # 안전한 버전 테스트
        print("MaterialWebLinkRowSafe 테스트 중...")
        safe_row = MaterialWebLinkRowSafe()
        print(f"MaterialWebLinkRowSafe 생성 성공: {type(safe_row)}")
        
        return True
        
    except Exception as e:
        print(f"UStruct 생성 실패: {e}")
        return False

def test_data_table_creation():
    """데이터 테이블 생성 테스트"""
    print("\n=== 데이터 테이블 생성 테스트 ===")
    
    try:
        # 에셋 도구 가져오기
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        
        # 데이터 테이블 팩토리 생성
        factory = unreal.DataTableFactory()
        
        # UStruct 설정
        factory.struct = MaterialWebLinkRowSafe  # 먼저 안전한 버전부터 테스트
        
        # 데이터 테이블 생성
        package_path = "/Game/MaidCat/Data/TestMaterialWebLinks"
        asset_name = "DT_TestMaterialWebLinks"
        
        data_table = asset_tools.create_asset(
            asset_name=asset_name,
            package_path=package_path,
            asset_class=unreal.DataTable,
            factory=factory
        )
        
        if data_table:
            print(f"데이터 테이블 생성 성공: {data_table.get_path_name()}")
            return data_table
        else:
            print("데이터 테이블 생성 실패")
            return None
            
    except Exception as e:
        print(f"데이터 테이블 생성 중 오류: {e}")
        return None

def main():
    """메인 테스트 함수"""
    print("UStruct 및 데이터 테이블 테스트 시작\n")
    
    # UStruct 생성 테스트
    if test_ustruct_creation():
        print("✓ UStruct 생성 테스트 통과")
        
        # 데이터 테이블 생성 테스트
        data_table = test_data_table_creation()
        if data_table:
            print("✓ 데이터 테이블 생성 테스트 통과")
        else:
            print("✗ 데이터 테이블 생성 테스트 실패")
    else:
        print("✗ UStruct 생성 테스트 실패")
    
    print("\n테스트 완료")

if __name__ == "__main__":
    main()