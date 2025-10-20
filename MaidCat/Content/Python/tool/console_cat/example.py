"""
Console Cat 사용 예제

이 파일은 console_cat 패키지를 어떻게 사용하는지 보여줍니다.
"""

def example_generate_data():
    """데이터 생성 예제"""
    print("=== 콘솔 명령어 데이터 생성 ===")
    
    try:
        import console_cat
        
        # 데이터 생성
        result = console_cat.generate_data()
        
        if result:
            print("✅ 데이터 생성 성공")
        else:
            print("❌ 데이터 생성 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def example_run_gui():
    """GUI 실행 예제"""
    print("\n=== Console Cat GUI 실행 ===")
    
    try:
        import console_cat
        
        # GUI 실행 (여러 방법)
        print("GUI 실행 방법들:")
        print("1. console_cat.main()")
        print("2. console_cat.run()")  
        print("3. console_cat.show()")
        
        # 실제 실행 (주석 해제하면 GUI가 열림)
        # window = console_cat.main()
        
        print("✅ GUI 실행 준비 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def example_direct_module_access():
    """서브모듈 직접 접근 예제"""
    print("\n=== 서브모듈 직접 접근 ===")
    
    try:
        import console_cat
        
        # 서브모듈 접근
        data_gen = console_cat.data_generator
        gui_module = console_cat.gui
        
        print(f"✅ data_generator 모듈: {data_gen}")
        print(f"✅ gui 모듈: {gui_module}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == '__main__':
    print("🐱 Console Cat 사용 예제")
    print("=" * 40)
    
    example_generate_data()
    example_run_gui()  
    example_direct_module_access()
    
    print("\n📚 더 많은 정보는 README를 참고하세요!")