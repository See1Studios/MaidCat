"""
레벨 로더 모듈 리로드 스크립트
"""
import sys
import importlib
import unreal

unreal.log("=" * 60)
unreal.log("🔄 레벨 로더 모듈 리로드 시작")
unreal.log("=" * 60)

try:
    # tool.level_loader 모듈 리로드
    if 'tool.level_loader' in sys.modules:
        importlib.reload(sys.modules['tool.level_loader'])
        unreal.log("✅ tool.level_loader 모듈 리로드 완료")
    else:
        unreal.log_warning("⚠️ tool.level_loader 모듈이 로드되지 않았습니다. 새로 임포트합니다.")
        from tool import level_loader
    
    # 재등록
    from tool import level_loader
    level_loader.register()
    
    unreal.log("=" * 60)
    unreal.log("🎉 모듈 리로드 및 재등록 완료")
    unreal.log("=" * 60)
    
except Exception as e:
    unreal.log_error(f"❌ 리로드 실패: {e}")
    import traceback
    unreal.log_error(traceback.format_exc())
