#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파이썬 아이콘 테스트 스크립트
로컬 파이썬 설치본에서 사용 가능한 아이콘들을 확인하고 테스트합니다.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

def find_python_icons():
    """파이썬 설치본에서 아이콘 파일들 찾기"""
    python_dir = os.path.dirname(sys.executable)
    print(f"🐍 파이썬 설치 디렉토리: {python_dir}")
    
    icon_info = {
        "python_dir": python_dir,
        "executable": sys.executable,
        "icons": []
    }
    
    # 검색할 디렉토리들
    search_dirs = [
        os.path.join(python_dir, "DLLs"),
        os.path.join(python_dir, "Lib", "idlelib", "Icons"),
        os.path.join(python_dir, "Lib", "tkinter"),
        os.path.join(python_dir, "tcl", "tk8.6", "images") if os.path.exists(os.path.join(python_dir, "tcl")) else None,
    ]
    
    # None 제거
    search_dirs = [d for d in search_dirs if d is not None]
    
    print("\n📁 검색 디렉토리들:")
    for search_dir in search_dirs:
        print(f"  - {search_dir}")
        
        if os.path.exists(search_dir):
            print(f"    ✅ 존재함")
            
            # 아이콘 파일들 찾기
            for ext in ['.ico', '.png', '.bmp', '.gif', '.xbm']:
                for file in os.listdir(search_dir):
                    if file.lower().endswith(ext):
                        full_path = os.path.join(search_dir, file)
                        try:
                            size = os.path.getsize(full_path)
                            icon_info["icons"].append({
                                "name": file,
                                "path": full_path,
                                "size": size,
                                "extension": ext,
                                "directory": os.path.basename(search_dir)
                            })
                        except OSError:
                            pass
        else:
            print(f"    ❌ 존재하지 않음")
    
    return icon_info

def test_icon_loading(icon_path):
    """아이콘 로딩 테스트"""
    try:
        if icon_path.lower().endswith('.ico'):
            # ICO 파일 테스트
            root = tk.Tk()
            root.withdraw()  # 윈도우 숨기기
            root.iconbitmap(icon_path)
            root.destroy()
            return True, "ICO 로딩 성공"
        
        elif icon_path.lower().endswith('.png'):
            # PNG 파일 테스트 (PIL 필요)
            try:
                from PIL import Image, ImageTk
                root = tk.Tk()
                root.withdraw()
                
                image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(image)
                root.iconphoto(True, photo)
                root.destroy()
                return True, "PNG 로딩 성공 (PIL 사용)"
            except ImportError:
                return False, "PNG 로딩 실패: PIL/Pillow 필요"
        
        else:
            return False, f"지원되지 않는 형식: {os.path.splitext(icon_path)[1]}"
            
    except Exception as e:
        return False, f"로딩 실패: {str(e)}"

def create_icon_test_gui(icon_info):
    """아이콘 테스트 GUI 생성"""
    root = tk.Tk()
    root.title("🐍 파이썬 아이콘 테스트")
    root.geometry("900x700")
    
    # 첫 번째로 찾은 ICO 파일로 윈도우 아이콘 설정 시도
    for icon in icon_info["icons"]:
        if icon["extension"] == ".ico":
            try:
                root.iconbitmap(icon["path"])
                print(f"✅ 윈도우 아이콘 설정 성공: {icon['name']}")
                break
            except Exception as e:
                print(f"❌ 윈도우 아이콘 설정 실패: {icon['name']} - {e}")
    
    # 메인 프레임
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 제목
    title_label = ttk.Label(main_frame, text="🐍 파이썬 설치본 아이콘 테스트", 
                           font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 10))
    
    # 파이썬 정보
    info_frame = ttk.LabelFrame(main_frame, text="파이썬 정보")
    info_frame.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(info_frame, text=f"실행파일: {icon_info['executable']}").pack(anchor=tk.W, padx=5, pady=2)
    ttk.Label(info_frame, text=f"설치 디렉토리: {icon_info['python_dir']}").pack(anchor=tk.W, padx=5, pady=2)
    ttk.Label(info_frame, text=f"찾은 아이콘 수: {len(icon_info['icons'])}개").pack(anchor=tk.W, padx=5, pady=2)
    
    # 아이콘 목록
    list_frame = ttk.LabelFrame(main_frame, text="발견된 아이콘들")
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    # 트리뷰
    columns = ("name", "directory", "size", "status")
    tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=15)
    
    tree.heading("#0", text="형식", anchor=tk.W)
    tree.heading("name", text="파일명", anchor=tk.W)
    tree.heading("directory", text="디렉토리", anchor=tk.W)
    tree.heading("size", text="크기", anchor=tk.W)
    tree.heading("status", text="로딩 테스트", anchor=tk.W)
    
    tree.column("#0", width=80, minwidth=60)
    tree.column("name", width=200, minwidth=150)
    tree.column("directory", width=100, minwidth=80)
    tree.column("size", width=80, minwidth=60)
    tree.column("status", width=200, minwidth=150)
    
    # 스크롤바
    tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scroll.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    # 아이콘들을 트리뷰에 추가
    for icon in icon_info["icons"]:
        # 로딩 테스트
        success, message = test_icon_loading(icon["path"])
        status_text = message
        status_icon = "✅" if success else "❌"
        
        # 크기 포맷팅
        size_kb = icon["size"] / 1024
        size_text = f"{size_kb:.1f} KB"
        
        # 트리에 추가
        tree.insert("", tk.END, 
                   text=icon["extension"].upper(),
                   values=(icon["name"], icon["directory"], size_text, f"{status_icon} {status_text}"))
    
    # 버튼 프레임
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    def copy_selected_path():
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            name = item["values"][0]
            # 선택된 아이콘 찾기
            for icon in icon_info["icons"]:
                if icon["name"] == name:
                    root.clipboard_clear()
                    root.clipboard_append(icon["path"])
                    print(f"📋 클립보드에 복사됨: {icon['path']}")
                    break
    
    def open_directory():
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            name = item["values"][0]
            # 선택된 아이콘 찾기
            for icon in icon_info["icons"]:
                if icon["name"] == name:
                    import subprocess
                    subprocess.Popen(f'explorer /select,"{icon["path"]}"')
                    break
    
    ttk.Button(button_frame, text="📋 경로 복사", command=copy_selected_path).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="📁 폴더 열기", command=open_directory).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="❌ 종료", command=root.quit).pack(side=tk.RIGHT, padx=5)
    
    # 사용법 안내
    help_text = "💡 사용법: 아이콘을 선택하고 '경로 복사' 버튼을 클릭하여 전체 경로를 복사할 수 있습니다."
    ttk.Label(main_frame, text=help_text, font=("Arial", 8), foreground="gray").pack(pady=(5, 0))
    
    return root

def main():
    print("🔍 파이썬 설치본에서 아이콘 검색 중...")
    icon_info = find_python_icons()
    
    print(f"\n📊 검색 결과:")
    print(f"  - 총 {len(icon_info['icons'])}개의 아이콘 발견")
    
    if icon_info["icons"]:
        print("\n📋 발견된 아이콘들:")
        for icon in icon_info["icons"]:
            size_kb = icon["size"] / 1024
            print(f"  📄 {icon['name']} ({icon['extension'].upper()}) - {size_kb:.1f} KB")
            print(f"     📁 {icon['path']}")
            
            # 간단한 로딩 테스트
            success, message = test_icon_loading(icon["path"])
            print(f"     🧪 {message}")
            print()
        
        print("🖼️ GUI 테스트 창을 열어 자세한 정보를 확인하세요...")
        root = create_icon_test_gui(icon_info)
        root.mainloop()
    else:
        print("❌ 아이콘을 찾을 수 없습니다.")
        
        # 디렉토리 구조 출력 (디버깅용)
        python_dir = icon_info["python_dir"]
        print(f"\n🔍 디렉토리 구조 확인:")
        for dir_name in ["DLLs", "Lib", "tcl"]:
            full_path = os.path.join(python_dir, dir_name)
            if os.path.exists(full_path):
                print(f"  ✅ {dir_name}/ 존재")
                if dir_name == "Lib":
                    idlelib_path = os.path.join(full_path, "idlelib")
                    if os.path.exists(idlelib_path):
                        print(f"    ✅ idlelib/ 존재")
                        icons_path = os.path.join(idlelib_path, "Icons")
                        if os.path.exists(icons_path):
                            print(f"      ✅ Icons/ 존재")
                            files = os.listdir(icons_path)
                            print(f"      📁 파일들: {files}")
                        else:
                            print(f"      ❌ Icons/ 없음")
                    else:
                        print(f"    ❌ idlelib/ 없음")
            else:
                print(f"  ❌ {dir_name}/ 없음")

if __name__ == "__main__":
    main()