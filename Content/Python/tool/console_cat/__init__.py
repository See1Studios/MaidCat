"""
Console Cat - MaidCat 콘솔 명령어 도구 🐱

Unreal Engine 콘솔 명령어 관리 및 실행을 위한 패키지

사용법:
    import console_cat
    
    # 데이터 생성
    console_cat.generate_data()
    
    # GUI 실행
    window = console_cat.main()
"""

__version__ = "1.0.0"
__author__ = "MaidCat Team"

# 서브모듈 import
from . import data_generator
from . import console_cat as gui

# 패키지 레벨 함수
def main():
    """Console Cat GUI 실행"""
    return gui.main()

def generate_data():
    """콘솔 명령어 데이터 생성"""
    if hasattr(data_generator, 'main'):
        return data_generator.main()
    return False

def show():
    """GUI 표시 (main의 별칭)"""
    return main()

def run():
    """GUI 실행 (main의 별칭)"""  
    return main()

# 공개 API
__all__ = [
    'main',
    'generate_data', 
    'show',
    'run',
    'data_generator',
    'gui'
]