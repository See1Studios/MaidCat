#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run Script for TA Python Tool
TA Python Tool 실행 스크립트 - 기존 버전과 리팩토링된 버전을 선택적으로 실행
"""

import sys
import os

def main():
    """메인 함수"""
    print("🐍 TA Python Tool 실행 스크립트")
    print("=" * 50)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 사용자에게 선택지 제공
    while True:
        print("\n실행할 버전을 선택하세요:")
        print("1. 기존 버전 (ta_python_tool.py)")
        print("2. 리팩토링된 버전 (refactored_main.py)")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            print("\n🔄 기존 버전을 실행합니다...")
            try:
                original_path = os.path.join(current_dir, "ta_python_tool.py")
                if os.path.exists(original_path):
                    import subprocess
                    subprocess.run([sys.executable, original_path])
                else:
                    print(f"❌ 파일을 찾을 수 없습니다: {original_path}")
            except Exception as e:
                print(f"❌ 실행 중 오류: {e}")
            break
            
        elif choice == "2":
            print("\n🔄 리팩토링된 버전을 실행합니다...")
            try:
                refactored_path = os.path.join(current_dir, "refactored_main.py")
                if os.path.exists(refactored_path):
                    import subprocess
                    subprocess.run([sys.executable, refactored_path])
                else:
                    print(f"❌ 파일을 찾을 수 없습니다: {refactored_path}")
            except Exception as e:
                print(f"❌ 실행 중 오류: {e}")
            break
            
        elif choice == "3":
            print("\n👋 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1, 2, 또는 3을 입력하세요.")

if __name__ == "__main__":
    main()