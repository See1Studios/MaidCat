#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool Launcher for Unreal Engine
언리얼 엔진에서 TA Python Tool을 별도 프로세스로 실행하는 런처
"""

import subprocess
import os
import warnings

def run():
    """TA Python Tool을 별도 프로세스로 실행"""
    # ResourceWarning 억제 - detached 프로세스는 의도적으로 실행 상태 유지
    warnings.filterwarnings("ignore", category=ResourceWarning, message=".*subprocess.*is still running")
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        editor_path = os.path.join(script_dir, "ta_python_tool.py")
        
        if not os.path.exists(editor_path):
            print(f"오류: {editor_path} 파일을 찾을 수 없습니다.")
            return
            
        if os.name == 'nt':  # Windows
            DETACHED_PROCESS = 0x00000008
            try:
                subprocess.Popen(
                    ['pythonw', editor_path],
                    cwd=script_dir,
                    creationflags=DETACHED_PROCESS,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                subprocess.Popen(
                    ['python', editor_path],
                    cwd=script_dir,
                    creationflags=DETACHED_PROCESS,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        else:  # Unix/Linux
            try:
                subprocess.Popen(
                    ['python3', editor_path],
                    cwd=script_dir,
                    start_new_session=True,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                subprocess.Popen(
                    ['python', editor_path],
                    cwd=script_dir,
                    start_new_session=True,
                    close_fds=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        
    except Exception as e:
        print(f"TA Python Tool 실행 중 오류: {e}")

if __name__ == "__main__":
    run()