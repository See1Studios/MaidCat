#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Entry Point for Refactored TA Python Tool
리팩토링된 TA Python Tool의 메인 진입점
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# 현재 패키지 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 리팩토링된 모듈들 import
try:
    from ta_python_tool.utils.logging_utils import setup_logging, cleanup_logging
    from ta_python_tool.models.config_model import ConfigManager
    from ta_python_tool.core.guide import TAPythonGuide
    from ta_python_tool.config.constants import APP_TITLE, APP_GEOMETRY
    
    logger, file_handler = setup_logging()
    logger.info("리팩토링된 TA Python Tool 시작")
    
except ImportError as e:
    print(f"모듈 import 오류: {e}")
    print("기존 ta_python_tool.py를 사용하여 실행합니다.")
    
    # 기존 파일로 폴백
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("ta_python_tool", 
                                                    os.path.join(current_dir, "ta_python_tool.py"))
        if spec and spec.loader:
            ta_python_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ta_python_module)
            ta_python_module.main()
            sys.exit(0)
        else:
            raise ImportError("모듈 스펙 생성 실패")
    except Exception as fallback_e:
        print(f"기존 파일 실행도 실패: {fallback_e}")
        sys.exit(1)


class RefactoredTAPythonTool:
    """리팩토링된 TA Python Tool 메인 클래스"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        
        # 리소스 정리 상태 추적
        self._resources_cleaned = False
        
        # 모델 초기화
        self.config_manager = ConfigManager()
        
        # 인터페이스 상태 초기화
        self.guide_interface = None
        self.edit_interface = None
        
        # UI 설정
        self.setup_ui()
        
        # 가이드 클래스 초기화
        self.guide = TAPythonGuide(self.root, self.main_container, 
                                 self._clear_main_container, self)
        
        # 창 닫기 이벤트 핸들러 설정
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 지연된 초기화
        self.root.after(10, self._delayed_initialization)
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 상태바
        self.setup_status_bar()
    
    def setup_status_bar(self):
        """상태바 설정"""
        self.status_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))
        
        self.status_label = tk.Label(self.status_frame, text="리팩토링된 TA Python Tool 준비", 
                                   anchor=tk.W, font=("Arial", 9), 
                                   padx=8, pady=4)
        self.status_label.pack(fill=tk.BOTH, expand=True)
    
    def _clear_main_container(self):
        """메인 컨테이너의 모든 위젯 제거"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # 인터페이스 참조 초기화
        self.edit_interface = None
        self.guide_interface = None
    
    def _delayed_initialization(self):
        """지연된 초기화 작업들"""
        try:
            # TAPython 플러그인 설치 상태 확인
            tapython_available = self.config_manager.is_tapython_available()
            
            if tapython_available:
                # 기본 설정 파일 로드 시도
                if self.config_manager.default_config_path:
                    success = self.config_manager.load_file(self.config_manager.default_config_path)
                    if success:
                        self.show_edit_interface()
                        self.update_status("✅ 설정 파일 로드 완료")
                    else:
                        self.guide.show_guide_interface()
                        self.update_status("❌ 설정 파일 로드 실패")
                else:
                    self.guide.show_guide_interface()
                    self.update_status("❌ 설정 파일 경로를 찾을 수 없음")
            else:
                # TAPython 플러그인이 없으면 가이드 표시
                self.guide.show_guide_interface()
                self.update_status("❌ TAPython 플러그인이 필요합니다")
            
        except Exception as e:
            logger.error(f"지연된 초기화 중 오류: {e}")
            self.guide.show_guide_interface()
            self.update_status(f"❌ 초기화 오류: {str(e)}")
    
    def show_edit_interface(self):
        """편집 인터페이스 표시"""
        try:
            self._clear_main_container()
            
            # 간단한 편집 인터페이스 생성 (데모용)
            self.edit_interface = tk.Frame(self.main_container)
            self.edit_interface.pack(fill=tk.BOTH, expand=True)
            
            # 제목
            title_label = tk.Label(self.edit_interface, 
                                 text="🐍 리팩토링된 TA Python Tool", 
                                 font=("Arial", 16, "bold"))
            title_label.pack(pady=20)
            
            # 설명
            desc_text = """리팩토링이 성공적으로 완료되었습니다!

주요 개선사항:
• 모듈화된 구조 (4100줄 → 여러 작은 모듈들)
• 타입 힌트 추가
• 설정과 상수 분리
• 재사용 가능한 유틸리티 함수들
• 데이터 모델 클래스들
• 더 나은 에러 처리

현재는 데모 버전입니다. 전체 기능은 곧 구현됩니다."""
            
            desc_label = tk.Label(self.edit_interface, text=desc_text, 
                                justify=tk.LEFT, wraplength=600)
            desc_label.pack(pady=20)
            
            # 설정 정보
            info_frame = tk.LabelFrame(self.edit_interface, text="설정 정보")
            info_frame.pack(fill=tk.X, padx=20, pady=10)
            
            config_info = f"""설정 파일: {self.config_manager.file_path}
로드된 툴 메뉴: {len(self.config_manager.config_data)}개
변경사항: {'있음' if self.config_manager.has_unsaved_changes else '없음'}"""
            
            tk.Label(info_frame, text=config_info, justify=tk.LEFT).pack(anchor=tk.W)
            
            # 버튼들
            button_frame = tk.Frame(self.edit_interface)
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="🔄 가이드로 돌아가기", 
                     command=self.guide.show_guide_interface).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="📄 새 파일 생성", 
                     command=self.guide._create_new_config_file_guide).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"편집 인터페이스 표시 중 오류: {e}")
            messagebox.showerror("오류", f"편집 인터페이스를 표시할 수 없습니다:\n{e}")
    
    def load_config_file(self, file_path: str):
        """설정 파일 로드 (가이드에서 호출됨)"""
        try:
            success = self.config_manager.load_file(file_path)
            if success:
                self.show_edit_interface()
                self.update_status(f"✅ 파일 로드 성공: {os.path.basename(file_path)}")
            else:
                self.update_status(f"❌ 파일 로드 실패: {os.path.basename(file_path)}")
                messagebox.showerror("오류", f"설정 파일을 로드할 수 없습니다:\n{file_path}")
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류: {e}")
            messagebox.showerror("오류", f"파일 로드 중 오류가 발생했습니다:\n{e}")
    
    def update_status(self, message: str, auto_clear: bool = True, clear_delay: int = 3000):
        """상태바 메시지 업데이트"""
        self.status_label.configure(text=message)
        
        if auto_clear:
            self.root.after(clear_delay, lambda: self.status_label.configure(text="준비"))
    
    def _setup_guide_menubar(self):
        """가이드용 메뉴바 설정 (임시)"""
        pass
    
    def _setup_guide_info_frame(self):
        """가이드용 정보 프레임 설정 (임시)"""
        pass
    
    def on_closing(self):
        """창 닫기 시 리소스 정리"""
        try:
            if self.config_manager.has_unsaved_changes:
                result = messagebox.askyesnocancel(
                    "저장하지 않은 변경사항",
                    "저장하지 않은 변경사항이 있습니다.\n\n저장하고 종료하시겠습니까?",
                    icon="warning"
                )
                
                if result is True:  # 예 - 저장하고 종료
                    # 여기서 저장 로직 구현 필요
                    self.cleanup_resources()
                    self.root.destroy()
                elif result is False:  # 아니오 - 저장하지 않고 종료
                    if messagebox.askyesno("확인", "정말로 저장하지 않고 종료하시겠습니까?"):
                        self.cleanup_resources()
                        self.root.destroy()
                # None (취소) - 아무것도 하지 않음
            else:
                self.cleanup_resources()
                self.root.destroy()
        except Exception as e:
            logger.error(f"창 닫기 중 오류: {e}")
            self.cleanup_resources()
            self.root.destroy()
    
    def cleanup_resources(self):
        """리소스 정리"""
        if self._resources_cleaned:
            return
            
        try:
            cleanup_logging()
            self._resources_cleaned = True
        except Exception as e:
            logger.error(f"리소스 정리 중 오류: {e}")
            self._resources_cleaned = True
    
    def run(self):
        """메인 루프 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    app = None
    try:
        app = RefactoredTAPythonTool()
        app.run()
    except Exception as e:
        print(f"애플리케이션 실행 중 오류: {e}")
        traceback.print_exc()
        if 'logger' in globals():
            logger.error(f"애플리케이션 실행 중 오류: {e}")
    finally:
        # 최종 리소스 정리
        if app and not getattr(app, '_resources_cleaned', False):
            try:
                app.cleanup_resources()
            except:
                pass


if __name__ == "__main__":
    main()