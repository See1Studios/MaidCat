"""
언리얼 엔진 Python API 래퍼 패키지
=================================

이 패키지는 언리얼 엔진의 다양한 에디터 API들에 대한 편리한 래퍼를 제공합니다.
각 모듈은 특정 기능 영역에 특화되어 있습니다:

모듈 목록:

언리얼 엔진 내장 API:
- asset_lib: EditorAssetLibrary 래퍼들 (에셋 관리)
- util_lib: EditorUtilityLibrary 래퍼들 (유틸리티 함수)
- actor_sys: EditorActorSubsystem 래퍼들 (액터 관리)
- asset_sys: EditorAssetSubsystem 래퍼들 (에셋 서브시스템)
- util_sys: EditorUtilitySubsystem 래퍼들 (유틸리티 서브시스템)
- level_lib: EditorLevelLibrary + PythonLevelLib 래퍼들 (레벨 관리)
- asset_tool: AssetTools 래퍼들 (에셋 도구)
- asset_reg: AssetRegistry 래퍼들 (에셋 레지스트리)

TAPython 확장 라이브러리 (https://www.tacolor.xyz/):
- bp_lib: PythonBPLib 래퍼들 (Python BP 라이브러리)
- mat_lib: PythonMaterialLib 래퍼들 (머티리얼 라이브러리)
- mesh_lib: PythonMeshLib 래퍼들 (메시 라이브러리)
- tex_lib: PythonTextureLib 래퍼들 (텍스처 라이브러리)
- data_lib: PythonDataTableLib 래퍼들 (데이터테이블 라이브러리)
- phys_lib: PythonPhysicsAssetLib 래퍼들 (피지컬 에셋 라이브러리)
- enum_lib: PythonEnumLib 래퍼들 (열거형 라이브러리)
- struct_lib: PythonStructLib 래퍼들 (구조체 라이브러리)
- landscape_lib: PythonLandscapeLib 래퍼들 (랜드스케이프 라이브러리)

사용 예시:
    from ue import asset_lib, actor_sys, util_lib, bp_lib, mat_lib, mesh_lib, tex_lib, data_lib, phys_lib, enum_lib, struct_lib, landscape_lib
    
    # 언리얼 엔진 내장 API 사용
    asset = asset_lib.load_asset("/Game/MyAsset")  # EditorAssetLibrary
    actors = actor_sys.get_selected_level_actors()  # EditorActorSubsystem
    selected = util_lib.get_selected_assets()  # EditorUtilityLibrary
    
    # TAPython 확장 라이브러리 사용 (https://www.tacolor.xyz/)
    bp_lib.message_dialog("Hello", "Title")  # PythonBPLib
    connections = mat_lib.get_material_connections(material)  # PythonMaterialLib
    materials = mesh_lib.get_static_mesh_materials(static_mesh)  # PythonMeshLib
    texture = tex_lib.create_texture2d_from_raw(raw_data, 512, 512, 4)  # PythonTextureLib
    row_names = data_lib.get_row_names(data_table)  # PythonDataTableLib
    selected_bodies = phys_lib.get_selected_bodies_indexes(physics_asset)  # PythonPhysicsAssetLib
    enum_count = enum_lib.get_enum_len(user_enum)  # PythonEnumLib
    var_names = struct_lib.get_variable_names(user_struct)  # PythonStructLib
    landscape = landscape_lib.create_landscape(transform, 127, 1, 4, 4)  # PythonLandscapeLib

작성자: MaidCat Plugin
버전: 1.0
"""

# 주요 모듈들을 가져와서 패키지 레벨에서 접근 가능하게 함
from . import asset_lib
from . import util_lib
from . import actor_sys
from . import asset_sys
from . import util_sys
from . import level_lib
from . import asset_tool
from . import asset_reg
from . import bp_lib
from . import mat_lib
from . import mesh_lib
from . import tex_lib
from . import data_lib
from . import phys_lib
from . import enum_lib
from . import struct_lib
from . import landscape_lib

# 패키지 정보
__version__ = "1.0"
__author__ = "MaidCat Plugin"

# 모든 하위 모듈을 __all__에 명시
__all__ = [
    "asset_lib",
    "util_lib", 
    "actor_sys",
    "asset_sys",
    "util_sys",
    "level_lib",
    "asset_tool",
    "asset_reg",
    "bp_lib",
    "mat_lib",
    "mesh_lib",
    "tex_lib",
    "data_lib",
    "phys_lib",
    "enum_lib",
    "struct_lib",
    "landscape_lib"
]