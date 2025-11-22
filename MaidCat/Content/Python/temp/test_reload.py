import sys
import importlib
import unreal

unreal.log("=" * 60)
unreal.log("🔄 레벨 로더 모듈 리로드 시작")

# tool.level_loader 모듈 리로드
if 'tool.level_loader' in sys.modules:
    importlib.reload(sys.modules['tool.level_loader'])
    unreal.log("✅ 모듈 리로드 완료")
    
from tool import level_loader
level_loader.register()

unreal.log("🎉 완료!")
unreal.log("=" * 60)
