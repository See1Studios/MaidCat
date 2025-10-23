#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TA Python Tool Launcher for Unreal Engine
언리얼 엔진에서 TA Python Tool을 별도 프로세스로 실행하는 런처
"""

import subprocess
import sys
import os

def launch_menu_editor():
    """TA Python Tool을 별도 프로세스로 실행"""
    try:
        # 현재 스크립트 디렉토리
        script_dir = os.path.dirname(os.path.abspath(__file__))
        editor_path = os.path.join(script_dir, "ta_python_tool.py")
        
        # 별도 프로세스로 실행 (언리얼 엔진과 완전 분리)
        # 완전히 독립된 프로세스로 실행하여 입력 이벤트 간섭 방지
        if os.name == 'nt':  # Windows
            creation_flags = subprocess.CREATE_NEW_CONSOLE
        else:  # Unix/Linux
            creation_flags = 0
            
        process = subprocess.Popen([
            sys.executable, 
            editor_path
        ], 
        creationflags=creation_flags,
        cwd=script_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
        
        print("TA Python Tool이 별도 창에서 실행되었습니다.")
        print("이제 언리얼 에디터와 독립적으로 작동합니다.")
        
    except Exception as e:
        print(f"TA Python Tool 실행 중 오류: {e}")

if __name__ == "__main__":
    launch_menu_editor()