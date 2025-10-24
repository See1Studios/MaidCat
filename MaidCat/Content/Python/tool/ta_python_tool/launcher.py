#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool Launcher for Unreal Engine
언리얼 엔진에서 TA Python Tool을 별도 프로세스로 실행하는 런처
"""

import subprocess
import sys
import os

def run():
    """TA Python Tool을 별도 프로세스로 실행"""
    try:
        # 현재 스크립트 디렉토리
        script_dir = os.path.dirname(os.path.abspath(__file__))
        editor_path = os.path.join(script_dir, "ta_python_tool.py")
        
        print(f"스크립트 디렉토리: {script_dir}")
        print(f"실행할 파일: {editor_path}")
        
        # 파일 존재 확인
        if not os.path.exists(editor_path):
            print(f"오류: {editor_path} 파일을 찾을 수 없습니다.")
            return
            
        # 간단히 PATH에서 Python 실행파일로 실행
        if os.name == 'nt':  # Windows
            # pythonw 우선 시도 (백그라운드 실행)
            try:
                process = subprocess.Popen(
                    ['pythonw', editor_path],
                    cwd=script_dir
                )
                print(f"pythonw로 실행 성공 (PID: {process.pid})")
                
            except FileNotFoundError:
                # pythonw가 없으면 python으로 실행
                try:
                    process = subprocess.Popen(
                        ['python', editor_path],
                        cwd=script_dir
                    )
                    print(f"python으로 실행 성공 (PID: {process.pid})")
                except FileNotFoundError:
                    print("오류: python 또는 pythonw를 PATH에서 찾을 수 없습니다.")
                    return
            
        else:  # Unix/Linux
            try:
                process = subprocess.Popen(
                    ['python3', editor_path],
                    cwd=script_dir
                )
                print(f"python3로 실행 성공 (PID: {process.pid})")
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(
                        ['python', editor_path],
                        cwd=script_dir
                    )
                    print(f"python으로 실행 성공 (PID: {process.pid})")
                except FileNotFoundError:
                    print("오류: python3 또는 python을 PATH에서 찾을 수 없습니다.")
                    return
        
        print("TA Python Tool 실행 완료")
        print("잠시 후 GUI 창이 나타날 예정입니다.")
        
    except Exception as e:
        print(f"TA Python Tool 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()