"""dev_env_setup.py 성능 테스트 - 직접 실행"""

import sys
import importlib

# 모듈 강제 리로드
module_name = 'tool.dev_env_setup'
if module_name in sys.modules:
    del sys.modules[module_name]

print("=" * 60)
print("🔧 dev_env_setup.py 성능 테스트 (모듈 리로드)")
print("=" * 60)

# 새로 import
from tool.dev_env_setup import update_all_settings

# 함수 실행
update_all_settings()

print("=" * 60)
print("✅ 테스트 완료")
print("=" * 60)
