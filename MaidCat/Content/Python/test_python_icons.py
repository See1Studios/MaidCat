#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이미지를 Base64로 인코딩하여 코드에 포함시키고,
런타임에 디코딩해서 아이콘으로 사용하는 도구
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import base64
import io
from typing import Dict, Optional, Tuple

class ImageToBase64Tool:
    """이미지를 Base64로 변환하고 코드에 포함시키는 도구"""
    
    # 파일 크기 제한 (바이트)
    MAX_FILE_SIZE = 100 * 1024  # 100KB
    RECOMMENDED_SIZE = 32 * 1024  # 32KB (권장)
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖼️ 이미지 → Base64 → 아이콘 변환 도구")
        self.root.geometry("800x900")
        
        # 변수들
        self.selected_image_path = tk.StringVar()
        self.base64_data = ""
        self.variable_name = tk.StringVar(value="icon_data")
        
        self.setup_ui()
    
    def _check_pil_availability(self) -> str:
        """PIL/Pillow 사용 가능 여부 확인"""
        try:
            from PIL import Image, ImageTk
            return "📦 PIL/Pillow 사용 가능 - PNG, BMP, JPEG 등 모든 형식 지원"
        except ImportError:
            return "⚠️ PIL/Pillow 없음 - ICO 파일만 지원 (pip install Pillow로 설치 권장)"
    
    def setup_ui(self):
        """UI 구성"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제목
        title_label = ttk.Label(main_frame, text="🖼️ 이미지 → Base64 → 아이콘 변환 도구", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 1단계: 이미지 선택
        self.create_step1_frame(main_frame)
        
        # 2단계: Base64 변환
        self.create_step2_frame(main_frame)
        
        # 3단계: 코드 생성
        self.create_step3_frame(main_frame)
        
        # 4단계: 테스트
        self.create_step4_frame(main_frame)
    
    def create_step1_frame(self, parent):
        """1단계: 이미지 선택"""
        step1_frame = ttk.LabelFrame(parent, text="1단계: 이미지 파일 선택")
        step1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 파일 선택
        file_frame = ttk.Frame(step1_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="선택된 파일:").pack(side=tk.LEFT)
        path_label = ttk.Label(file_frame, textvariable=self.selected_image_path, 
                              foreground="blue", cursor="hand2")
        path_label.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        ttk.Button(file_frame, text="📁 파일 선택", 
                  command=self.select_image_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 지원 형식 안내
        support_label = ttk.Label(step1_frame, 
                                 text="💡 지원 형식: .ico (권장), .png, .bmp, .gif, .jpg, .jpeg",
                                 font=("Arial", 8), foreground="gray")
        support_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
        
        # PIL 의존성 안내
        pil_info = self._check_pil_availability()
        pil_label = ttk.Label(step1_frame, 
                             text=pil_info,
                             font=("Arial", 8), foreground="blue")
        pil_label.pack(anchor=tk.W, padx=5, pady=(0, 2))
        
        # 파일 크기 제한 안내
        size_warning = ttk.Label(step1_frame, 
                                text=f"⚠️ 권장 크기: {self.RECOMMENDED_SIZE//1024}KB 이하, 최대: {self.MAX_FILE_SIZE//1024}KB",
                                font=("Arial", 8), foreground="orange")
        size_warning.pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    def create_step2_frame(self, parent):
        """2단계: Base64 변환"""
        step2_frame = ttk.LabelFrame(parent, text="2단계: Base64 변환")
        step2_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(step2_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="🔄 Base64로 변환", 
                  command=self.convert_to_base64).pack(side=tk.LEFT)
        
        self.base64_status = ttk.Label(button_frame, text="변환 대기 중...", 
                                      foreground="gray")
        self.base64_status.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_step3_frame(self, parent):
        """3단계: 코드 생성"""
        step3_frame = ttk.LabelFrame(parent, text="3단계: 파이썬 코드 생성")
        step3_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 변수명 입력
        var_frame = ttk.Frame(step3_frame)
        var_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(var_frame, text="변수명:").pack(side=tk.LEFT)
        var_entry = ttk.Entry(var_frame, textvariable=self.variable_name, width=20)
        var_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(var_frame, text="📝 코드 생성", 
                  command=self.generate_code).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(var_frame, text="📋 복사", 
                  command=self.copy_code).pack(side=tk.LEFT, padx=(5, 0))
        
        # 생성된 코드
        code_frame = ttk.Frame(step3_frame)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 5))
        
        self.code_text = tk.Text(code_frame, wrap=tk.WORD, height=15, font=("Consolas", 9))
        code_scroll = ttk.Scrollbar(code_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=code_scroll.set)
        
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_step4_frame(self, parent):
        """4단계: 테스트"""
        step4_frame = ttk.LabelFrame(parent, text="4단계: 아이콘 테스트")
        step4_frame.pack(fill=tk.X)
        
        test_frame = ttk.Frame(step4_frame)
        test_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(test_frame, text="🧪 아이콘 테스트", 
                  command=self.test_icon).pack(side=tk.LEFT)
        
        self.test_status = ttk.Label(test_frame, text="테스트 대기 중...", 
                                    foreground="gray")
        self.test_status.pack(side=tk.LEFT, padx=(10, 0))
    
    def select_image_file(self):
        """이미지 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="아이콘 이미지 선택",
            filetypes=[
                ("ICO 파일 (권장)", "*.ico"),
                ("PNG 파일 (PIL 필요)", "*.png"),
                ("이미지 파일", "*.ico *.png *.bmp *.gif *.jpg *.jpeg"),
                ("BMP 파일", "*.bmp"),
                ("GIF 파일", "*.gif"),
                ("JPEG 파일", "*.jpg *.jpeg"),
                ("모든 파일", "*.*")
            ]
        )
        
        if file_path:
            # 파일 크기 체크
            try:
                file_size = os.path.getsize(file_path)
                file_size_kb = file_size / 1024
                
                if file_size > self.MAX_FILE_SIZE:
                    messagebox.showerror(
                        "파일 크기 초과", 
                        f"선택한 파일이 너무 큽니다.\n\n"
                        f"파일 크기: {file_size_kb:.1f}KB\n"
                        f"최대 허용: {self.MAX_FILE_SIZE//1024}KB\n\n"
                        f"더 작은 이미지를 선택하거나 이미지를 압축해주세요."
                    )
                    return
                
                elif file_size > self.RECOMMENDED_SIZE:
                    result = messagebox.askquestion(
                        "큰 파일 경고",
                        f"선택한 파일이 권장 크기보다 큽니다.\n\n"
                        f"파일 크기: {file_size_kb:.1f}KB\n"
                        f"권장 크기: {self.RECOMMENDED_SIZE//1024}KB\n\n"
                        f"큰 파일은 생성되는 코드가 매우 길어집니다.\n"
                        f"계속 진행하시겠습니까?",
                        icon="warning"
                    )
                    if result != 'yes':
                        return
                
                self.selected_image_path.set(file_path)
                self.base64_data = ""  # 기존 변환 데이터 초기화
                self.base64_status.configure(
                    text=f"변환 대기 중... (파일 크기: {file_size_kb:.1f}KB)", 
                    foreground="gray"
                )
                self.test_status.configure(text="테스트 대기 중...", foreground="gray")
                
            except OSError as e:
                messagebox.showerror("오류", f"파일 정보를 읽을 수 없습니다:\n{str(e)}")
    
    def convert_to_base64(self):
        """이미지를 Base64로 변환"""
        if not self.selected_image_path.get():
            messagebox.showwarning("경고", "먼저 이미지 파일을 선택해주세요.")
            return
        
        try:
            with open(self.selected_image_path.get(), 'rb') as f:
                image_data = f.read()
            
            self.base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # 파일 정보
            file_size = len(image_data)
            base64_size = len(self.base64_data)
            size_increase = (base64_size / file_size - 1) * 100
            
            # 예상 코드 라인 수 계산 (76자 기준)
            estimated_lines = base64_size // 76 + 1
            
            status_text = (f"✅ 변환 완료 - 원본: {file_size:,}B → Base64: {base64_size:,}자 "
                          f"({size_increase:.0f}% 증가, 약 {estimated_lines}줄)")
            
            if base64_size > 50000:  # 50,000자 이상이면 경고
                self.base64_status.configure(text=status_text, foreground="orange")
                messagebox.showwarning(
                    "큰 데이터 경고",
                    f"Base64 데이터가 매우 큽니다!\n\n"
                    f"문자 수: {base64_size:,}자\n"
                    f"예상 코드 줄 수: {estimated_lines:,}줄\n\n"
                    f"이런 큰 데이터는 코드 관리가 어려울 수 있습니다.\n"
                    f"더 작은 이미지 사용을 권장합니다."
                )
            else:
                self.base64_status.configure(text=status_text, foreground="green")
            
            # 자동으로 코드 생성
            self.generate_code()
            
        except Exception as e:
            error_text = f"❌ 변환 실패: {str(e)}"
            self.base64_status.configure(text=error_text, foreground="red")
            messagebox.showerror("오류", f"Base64 변환 실패:\n{str(e)}")
    
    def generate_code(self):
        """파이썬 코드 생성"""
        if not self.base64_data:
            messagebox.showwarning("경고", "먼저 Base64 변환을 수행해주세요.")
            return
        
        var_name = self.variable_name.get().strip()
        if not var_name:
            var_name = "icon_data"
        
        # 파일명에서 확장자 추출
        file_path = self.selected_image_path.get()
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 파일 크기 정보
        try:
            file_size = os.path.getsize(file_path)
            base64_size = len(self.base64_data)
            size_info = f"""
원본 파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)
Base64 크기: {base64_size:,} characters
압축 비율: {(base64_size/file_size):.1f}x (Base64는 약 33% 크기 증가)"""
        except:
            size_info = ""
        
        # 코드 템플릿 생성
        code_template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base64로 인코딩된 아이콘 데이터
원본 파일: {file_name}{size_info}
생성 도구: 이미지 → Base64 → 아이콘 변환 도구
"""

import base64
import io
import tkinter as tk
from tkinter import messagebox

# Base64로 인코딩된 아이콘 데이터
{var_name} = """\\
{self._format_base64_data(self.base64_data)}"""

def decode_icon_data(base64_string: str) -> bytes:
    """Base64 문자열을 바이너리 데이터로 디코딩"""
    try:
        return base64.b64decode(base64_string)
    except Exception as e:
        raise ValueError(f"Base64 디코딩 실패: {{e}}")

def create_icon_from_data(root_window: tk.Tk, base64_string: str) -> bool:
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
        
        # 파일 형식에 따른 처리
        if "{file_ext}" == ".ico":
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
        
        else:
            # PNG, BMP, GIF 등: PIL 사용
            try:
                from PIL import Image, ImageTk
                
                # BytesIO로 이미지 로드
                image_stream = io.BytesIO(image_data)
                image = Image.open(image_stream)
                
                # PhotoImage로 변환
                photo = ImageTk.PhotoImage(image)
                root_window.iconphoto(True, photo)
                
                # 참조 유지를 위해 윈도우 객체에 저장
                root_window._icon_photo = photo
                
                return True
                
            except ImportError:
                raise ImportError("PNG/BMP/GIF 아이콘을 사용하려면 PIL/Pillow가 필요합니다.")
    
    except Exception as e:
        print(f"아이콘 설정 실패: {{e}}")
        return False

def test_icon():
    """아이콘 테스트 함수"""
    root = tk.Tk()
    root.title("🧪 아이콘 테스트")
    root.geometry("400x300")
    
    # 아이콘 설정 시도
    success = create_icon_from_data(root, {var_name})
    
    # 결과 표시
    if success:
        status_text = "✅ 아이콘이 성공적으로 설정되었습니다!"
        status_color = "green"
    else:
        status_text = "❌ 아이콘 설정에 실패했습니다."
        status_color = "red"
    
    # UI 구성
    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    
    tk.Label(frame, text="🧪 아이콘 테스트 결과", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(frame, text=status_text, font=("Arial", 12), fg=status_color).pack(pady=10)
    
    tk.Label(frame, text=f"원본 파일: {file_name}", font=("Arial", 10)).pack(pady=5)
    tk.Label(frame, text=f"데이터 크기: {{len({var_name}):,}} 문자", font=("Arial", 10)).pack(pady=5)
    
    tk.Button(frame, text="❌ 닫기", command=root.quit, font=("Arial", 12)).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_icon()
'''
        
        # 코드 텍스트 위젯에 표시
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, code_template)
        
        # 상태 업데이트
        lines = code_template.count('\\n') + 1
        chars = len(code_template)
        print(f"📝 코드 생성 완료: {lines}줄, {chars:,}자")
    
    def _format_base64_data(self, data: str, line_length: int = 76) -> str:
        """Base64 데이터를 여러 줄로 포맷팅"""
        lines = []
        for i in range(0, len(data), line_length):
            lines.append(data[i:i + line_length])
        return '\\n'.join(lines)
    
    def copy_code(self):
        """생성된 코드를 클립보드에 복사"""
        code = self.code_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("경고", "복사할 코드가 없습니다.")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("성공", "코드가 클립보드에 복사되었습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"클립보드 복사 실패:\\n{str(e)}")
    
    def test_icon(self):
        """생성된 아이콘 테스트"""
        if not self.base64_data:
            messagebox.showwarning("경고", "먼저 Base64 변환을 수행해주세요.")
            return
        
        try:
            # 파일 형식 확인
            file_path = self.selected_image_path.get()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # PIL 사용 가능 여부 확인
            pil_available = False
            try:
                from PIL import Image, ImageTk
                pil_available = True
            except ImportError:
                pass
            
            # ICO가 아닌 파일이고 PIL이 없으면 경고
            if file_ext != '.ico' and not pil_available:
                result = messagebox.askquestion(
                    "PIL/Pillow 없음",
                    f"선택한 파일 형식({file_ext.upper()})을 테스트하려면 PIL/Pillow가 필요합니다.\n\n"
                    f"설치 명령어: pip install Pillow\n\n"
                    f"그래도 테스트를 진행하시겠습니까? (실패할 가능성이 높습니다)",
                    icon="warning"
                )
                if result != 'yes':
                    return
            
            # 테스트 윈도우 생성
            test_window = tk.Toplevel(self.root)
            test_window.title("🧪 아이콘 테스트")
            test_window.geometry("450x350")
            
            # 아이콘 설정 시도
            success = self._apply_icon_to_window(test_window, self.base64_data)
            
            # 결과 표시
            frame = tk.Frame(test_window)
            frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            
            tk.Label(frame, text="🧪 아이콘 테스트 결과", 
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            if success:
                status_text = "✅ 아이콘이 성공적으로 설정되었습니다!"
                status_color = "green"
                self.test_status.configure(text="✅ 테스트 성공", foreground="green")
            else:
                status_text = "❌ 아이콘 설정에 실패했습니다."
                status_color = "red"
                self.test_status.configure(text="❌ 테스트 실패", foreground="red")
                
                # 실패 원인 추가 정보
                if file_ext != '.ico' and not pil_available:
                    status_text += f"\n\n💡 해결 방법:\n"
                    status_text += f"1. ICO 파일 사용 (권장)\n"
                    status_text += f"2. 'pip install Pillow' 실행 후 재시도"
            
            tk.Label(frame, text=status_text, font=("Arial", 11), 
                    fg=status_color, justify=tk.LEFT).pack(pady=10)
            
            file_name = os.path.basename(self.selected_image_path.get())
            tk.Label(frame, text=f"원본 파일: {file_name}", 
                    font=("Arial", 10)).pack(pady=5)
            tk.Label(frame, text=f"파일 형식: {file_ext.upper()}", 
                    font=("Arial", 10)).pack(pady=2)
            tk.Label(frame, text=f"PIL 사용 가능: {'✅ 예' if pil_available else '❌ 아니오'}", 
                    font=("Arial", 10)).pack(pady=2)
            tk.Label(frame, text=f"데이터 크기: {len(self.base64_data):,} 문자", 
                    font=("Arial", 10)).pack(pady=5)
            
            if not pil_available:
                tk.Label(frame, text="💡 'pip install Pillow'로 더 많은 형식 지원", 
                        font=("Arial", 9), fg="blue").pack(pady=5)
            
            tk.Button(frame, text="❌ 닫기", command=test_window.destroy, 
                     font=("Arial", 12)).pack(pady=15)
            
        except Exception as e:
            error_text = f"❌ 테스트 실패: {str(e)}"
            self.test_status.configure(text=error_text, foreground="red")
            messagebox.showerror("오류", f"아이콘 테스트 실패:\n{str(e)}")
    
    def _apply_icon_to_window(self, window, base64_data: str) -> bool:
        """윈도우에 Base64 아이콘 적용"""
        try:
            # Base64 디코딩
            image_data = base64.b64decode(base64_data)
            
            # 파일 확장자 확인
            file_path = self.selected_image_path.get()
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.ico':
                # ICO 파일: 임시 파일 생성
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".ico", delete=False) as temp_file:
                    temp_file.write(image_data)
                    temp_path = temp_file.name
                
                try:
                    window.iconbitmap(temp_path)
                    return True
                finally:
                    # 임시 파일 정리
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            else:
                # PNG, BMP 등: PIL 사용 (선택적)
                try:
                    from PIL import Image, ImageTk
                    
                    image_stream = io.BytesIO(image_data)
                    image = Image.open(image_stream)
                    photo = ImageTk.PhotoImage(image)
                    window.iconphoto(True, photo)
                    
                    # 참조 유지
                    setattr(window, '_icon_photo', photo)
                    return True
                    
                except ImportError:
                    # PIL이 없으면 기본 이미지 처리 시도
                    try:
                        # Tkinter의 기본 PhotoImage로 시도 (GIF, PPM, PGM만 지원)
                        if file_ext in ['.gif', '.ppm', '.pgm']:
                            image_stream = io.BytesIO(image_data)
                            photo = tk.PhotoImage(data=base64_data)
                            window.iconphoto(True, photo)
                            setattr(window, '_icon_photo', photo)
                            return True
                        else:
                            raise ImportError(f"{file_ext.upper()} 아이콘을 사용하려면 PIL/Pillow가 필요합니다.")
                    except Exception:
                        raise ImportError(f"{file_ext.upper()} 아이콘을 사용하려면 PIL/Pillow가 필요합니다.")
        
        except Exception as e:
            print(f"아이콘 적용 실패: {e}")
            return False
    
    def run(self):
        """도구 실행"""
        self.root.mainloop()

def main():
    """메인 함수"""
    print("🖼️ 이미지 → Base64 → 아이콘 변환 도구 시작")
    app = ImageToBase64Tool()
    app.run()

if __name__ == "__main__":
    main()