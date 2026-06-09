#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base64로 인코딩된 아이콘 데이터 - 샘플 테스트
원본 파일: python_icon_16x16.ico (가상)
생성 도구: 이미지 → Base64 → 아이콘 변환 도구
"""

import base64
import io
import tkinter as tk
from tkinter import messagebox

# 간단한 16x16 ICO 파일의 Base64 데이터 (Python 스타일 아이콘)
sample_icon_data = """
AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A3d3d/93d3f/d3d3/3d3d/93d3f/d3d3/3d3d/93d3f////8A////AP///wD///8A////AP///wD///8A3d3d/5mZmf+ZmZn/mZmZ/5mZmf+ZmZn/mZmZ/5mZmf/d3d3/////AP///wD///8A////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+ZmZn/3d3d/////wD///8A////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/mZmZ/93d3f////8A////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/5mZmf/d3d3/////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/1VVVf9VVVX/VVVV/1VVVf8AAAD/AAAA/wAAAP+ZmZn/3d3d/////wD///8A3d3d/5mZmf8AAAD/AAAA/1VVVf//////VVVV/////1VVVf8AAAD/AAAA/wAAAP+ZmZn/3d3d/////wD///8A3d3d/5mZmf8AAAD/AAAA/1VVVf9VVVX/VVVV/1VVVf9VVVX/AAAA/wAAAP8AAAD/mZmZ/93d3f////8A////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/mZmZ/93d3f////8A////AP///wD///8A3d3d/5mZmf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+ZmZn/3d3d/////wD///8A////AP///wD///8A3d3d/5mZmf+ZmZn/mZmZ/5mZmf+ZmZn/mZmZ/5mZmf/d3d3/////AP///wD///8A////AP///wD///8A3d3d/93d3f/d3d3/3d3d/93d3f/d3d3/3d3d/93d3f////8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
"""

def decode_icon_data(base64_string: str) -> bytes:
    """Base64 문자열을 바이너리 데이터로 디코딩"""
    try:
        # 개행 문자와 공백 제거
        clean_data = base64_string.strip().replace('\n', '').replace(' ', '')
        return base64.b64decode(clean_data)
    except Exception as e:
        raise ValueError(f"Base64 디코딩 실패: {e}")

def create_icon_from_data(root_window, base64_string: str) -> bool:
    """
    Base64 데이터에서 아이콘을 생성하여 윈도우에 설정
    
    Args:
        root_window: Tkinter 윈도우 객체
        base64_string: Base64로 인코딩된 이미지 데이터
    
    Returns:
        bool: 성공 여부
    """
    try:
        # Base64 데이터 디코딩
        image_data = decode_icon_data(base64_string)
        
        # ICO 파일: 임시 파일로 저장 후 사용
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ico", delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            root_window.iconbitmap(temp_path)
            return True
        finally:
            # 임시 파일 정리
            try:
                import os
                os.unlink(temp_path)
            except:
                pass
    
    except Exception as e:
        print(f"아이콘 설정 실패: {e}")
        return False

def test_icon():
    """아이콘 테스트 함수"""
    root = tk.Tk()
    root.title("🧪 샘플 아이콘 테스트")
    root.geometry("400x300")
    
    # 아이콘 설정 시도
    success = create_icon_from_data(root, sample_icon_data)
    
    # 결과 표시
    if success:
        status_text = "✅ 샘플 아이콘이 성공적으로 설정되었습니다!"
        status_color = "green"
    else:
        status_text = "❌ 샘플 아이콘 설정에 실패했습니다."
        status_color = "red"
    
    # UI 구성
    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    
    tk.Label(frame, text="🧪 샘플 아이콘 테스트", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(frame, text=status_text, font=("Arial", 12), fg=status_color).pack(pady=10)
    
    tk.Label(frame, text="원본 파일: 16x16 Python 스타일 ICO", font=("Arial", 10)).pack(pady=5)
    tk.Label(frame, text=f"데이터 크기: {len(sample_icon_data.strip()):,} 문자", font=("Arial", 10)).pack(pady=5)
    tk.Label(frame, text="파일 형식: ICO (Tkinter 기본 지원)", font=("Arial", 10)).pack(pady=5)
    
    if success:
        tk.Label(frame, text="창의 제목 표시줄 왼쪽에 아이콘이 보입니다!", 
                font=("Arial", 9), fg="blue").pack(pady=5)
    
    tk.Button(frame, text="❌ 닫기", command=root.quit, font=("Arial", 12)).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("🧪 샘플 아이콘 테스트 시작...")
    test_icon()