"""
MaidCat Startup Module
MaidCat 프로젝트 시작 시 자동 로드되는 모듈들

이 패키지의 모든 모듈들은 Unreal Engine 시작 시 자동으로 로드됩니다.
"""

import unreal

def initialize_maidcat():
    """MaidCat 초기화"""
    unreal.log("🐱 MaidCat 프로젝트 초기화 시작...")
    
    # Blueprint Function Library 초기화
    try:
        from . import bp_func
        if hasattr(bp_func, 'initialize_maidcat_library'):
            bp_func.initialize_maidcat_library()
    except ImportError as e:
        unreal.log_warning(f"bp_func 모듈 로드 실패: {e}")
    
    # Material Migration Blueprint Library 초기화
    try:
        from . import bp_material_migration
        if hasattr(bp_material_migration, 'initialize_material_migration_library'):
            bp_material_migration.initialize_material_migration_library()
    except ImportError as e:
        unreal.log_warning(f"bp_material_migration 모듈 로드 실패: {e}")
    
    # Blueprint Struct 초기화
    try:
        from . import bp_struct
        unreal.log("✅ bp_struct 모듈 로드됨")
    except ImportError as e:
        unreal.log_warning(f"bp_struct 모듈 로드 실패: {e}")
    
    # Editor Extensions 초기화
    try:
        from . import extend_editor
        unreal.log("✅ extend_editor 모듈 로드됨")
    except ImportError as e:
        unreal.log_warning(f"extend_editor 모듈 로드 실패: {e}")
    
    unreal.log("🎉 MaidCat 프로젝트 초기화 완료!")


# 자동 초기화
if __name__ != "__main__":
    initialize_maidcat()