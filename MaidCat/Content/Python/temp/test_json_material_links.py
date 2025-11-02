"""
JSON 기반 머티리얼-웹링크 시스템 테스트
"""
import sys
import os

# Python 경로에 MaidCat 모듈 추가
sys.path.append(r'd:\GitHub\MaidCat\MaidCat\Content\Python')

try:
    from editor.mi_editor import (
        load_material_web_links, 
        add_material_to_json, 
        remove_material_from_json, 
        list_materials_in_json
    )
    
    def test_json_operations():
        """JSON 작업 테스트"""
        print("=== JSON 기반 머티리얼-웹링크 시스템 테스트 ===\n")
        
        # 1. 기존 데이터 로드 테스트
        print("1. 기존 JSON 데이터 로드 테스트:")
        materials = load_material_web_links()
        print(f"   로드된 머티리얼 수: {len(materials)}")
        for path in materials.keys():
            print(f"   - {path}")
        print()
        
        # 2. 기존 목록 출력
        print("2. 등록된 머티리얼 목록:")
        list_materials_in_json()
        
        # 3. 새 머티리얼 추가 테스트
        print("3. 새 머티리얼 추가 테스트:")
        test_material_path = "/Game/TestMaterials/M_TestMaterial"
        test_description = "테스트용 머티리얼 - 머티리얼 노드 시스템 가이드"
        test_url = "https://docs.unrealengine.com/5.3/en-US/material-nodes-in-unreal-engine/"
        
        add_material_to_json(test_material_path, test_description, test_url)
        print()
        
        # 4. 추가 후 목록 확인
        print("4. 추가 후 목록 확인:")
        list_materials_in_json()
        
        # 5. 머티리얼 제거 테스트
        print("5. 머티리얼 제거 테스트:")
        remove_material_from_json(test_material_path)
        print()
        
        # 6. 제거 후 목록 확인
        print("6. 제거 후 최종 목록:")
        list_materials_in_json()
        
        print("=== 테스트 완료 ===")
    
    if __name__ == "__main__":
        test_json_operations()
        
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("언리얼 에디터에서 실행해주세요.")
    
except Exception as e:
    print(f"❌ 테스트 실행 실패: {e}")
    import traceback
    traceback.print_exc()