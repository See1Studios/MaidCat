"""
Python Context Menu System
파이썬 컨텍스트 메뉴 시스템

주요 기능:
1. Python 파일 함수 실행: 파이썬 파일의 함수들을 컨텍스트 메뉴에서 직접 실행
2. Python 폴더 모듈 리로드: Python 폴더의 모든 모듈을 동적으로 리로드
3. 동적 메뉴 생성: 선택된 파일/폴더에 따라 메뉴 항목 자동 생성

클래스:
- PythonFunctionScript: 함수 실행 메뉴 항목
- PythonFunctionsDynamicSection: 동적 함수 메뉴 섹션  
- PythonReloadScript: 모듈 리로드 메뉴 항목

함수:
- analyze_python_file(): Python 파일 AST 분석
- convert_virtual_path_to_real_path(): 가상 경로를 실제 경로로 변환
- get_selected_python_file_from_context(): 선택된 Python 파일 경로 가져오기
- register_python_menu_entry(): Python 파일용 메뉴 등록
- register_python_folder_menu(): Python 폴더용 메뉴 등록
"""
import ast
import os
import sys
import importlib
import unreal


def analyze_python_file(file_path):
    """Python 파일을 AST로 분석하여 함수 정보 추출
    
    Args:
        file_path (str): 분석할 Python 파일 경로
        
    Returns:
        list: 함수 정보 딕셔너리 리스트
            - name: 함수명
            - line: 함수 정의 라인 번호
            - args: 함수 인자 목록
            - docstring: 함수 docstring
            - is_private: private 함수 여부
    """
    if not os.path.exists(file_path) or not file_path.endswith('.py'):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node),
                    'is_private': node.name.startswith('_')
                }
                functions.append(func_info)
        
        return functions
        
    except (SyntaxError, Exception):
        return []


def convert_virtual_path_to_real_path(virtual_path, is_file=True):
    """Unreal Engine의 가상 경로를 실제 파일 시스템 경로로 변환
    
    지원 경로 패턴:
    - /Game/Python/util → Content/Python/util(.py)
    - /All/Game/Python/util → Content/Python/util(.py)  
    - /All/Plugins/MaidCat/Content/Python/util → Plugins/MaidCat/Content/Python/util(.py)
    
    Args:
        virtual_path (str): Unreal Engine 가상 경로
        is_file (bool): True면 파일용(.py 확장자 추가), False면 폴더용
        
    Returns:
        str: 실제 파일 시스템 경로, 변환 실패 시 None
    """
    if virtual_path.startswith('/All/Plugins/'):
        # 플러그인 경로 처리
        plugin_path = virtual_path.replace('/All/Plugins/', '')
        path_parts = plugin_path.split('/')
        
        if len(path_parts) >= 1:
            plugin_name = path_parts[0]
            relative_path = '/'.join(path_parts[1:])
            
            plugin_dir = unreal.Paths.project_plugins_dir()
            plugin_root = os.path.join(plugin_dir, plugin_name)
            
            # 파일인 경우에만 .py 확장자 추가
            if is_file and not relative_path.endswith('.py'):
                relative_path += '.py'
            
            return os.path.join(plugin_root, "Content", relative_path.replace('/', os.sep))
    
    elif virtual_path.startswith('/All/Game/'):
        # /All/Game/Python/util -> Content/Python/util
        relative_path = virtual_path.replace('/All/Game/', '')
        content_dir = unreal.Paths.project_content_dir()
        
        # 파일인 경우에만 .py 확장자 추가
        if is_file and not relative_path.endswith('.py'):
            relative_path += '.py'
        
        return os.path.join(content_dir, relative_path.replace('/', os.sep))
    
    elif virtual_path.startswith('/Game/'):
        # 프로젝트 콘텐츠 경로 처리
        relative_path = virtual_path.replace('/Game/', '')
        content_dir = unreal.Paths.project_content_dir()
        
        # 파일인 경우에만 .py 확장자 추가
        if is_file and not relative_path.endswith('.py'):
            relative_path += '.py'
        
        return os.path.join(content_dir, relative_path.replace('/', os.sep))
    
    return None


def get_selected_python_file_from_context(context):
    """컨텍스트 메뉴에서 선택된 Python 파일의 실제 경로 추출
    
    Args:
        context: Unreal Engine ToolMenuContext 객체
        
    Returns:
        str: 선택된 Python 파일의 실제 경로, 없으면 None
    """
    try:
        file_menu_context = context.find_by_class(unreal.ContentBrowserDataMenuContext_FileMenu)
        if not file_menu_context:
            return None
        
        selected_items = file_menu_context.selected_items
        if not selected_items:
            return None
        
        for item in selected_items:
            virtual_path = str(item.get_virtual_path())
            if virtual_path.endswith('.py'):
                return convert_virtual_path_to_real_path(virtual_path, is_file=True)
        
        return None
    except Exception as e:
        unreal.log_error(f"파일 가져오기 실패: {e}")
        return None


@unreal.uclass()
class PythonFunctionScript(unreal.ToolMenuEntryScript):
    """Python 함수 실행을 위한 동적 메뉴 항목 스크립트
    
    기능:
    - Python 파일의 함수를 컨텍스트 메뉴에서 직접 실행
    - 인자가 있는 함수는 비활성화 상태로 표시 (정보용)
    - 인자가 없는 함수는 직접 실행 가능
    - 함수 실행 결과를 상세 분석하여 로그 출력
    
    메서드:
    - can_execute(): 함수 실행 가능 여부 판단
    - execute(): 함수 실행 및 결과 분석
    """
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """실행 가능 여부 확인
        
        메뉴 항목 이름에 '_with_args' 접미사가 있으면 인자가 필요한 함수로 판단하여
        False를 반환하여 비활성화(회색)로 표시합니다.
        """
        if not self.data:
            return False
        
        name_str = str(self.data.name)
        return not name_str.endswith("_with_args")
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """함수 실행 또는 안내 메시지
        
        can_execute()가 True인 경우에만 호출되지만,
        비활성화된 항목을 클릭했을 때도 호출될 수 있으므로 안전하게 처리합니다.
        """
        if not self.data:
            return
        
        name_str = str(self.data.name)
        
        if name_str.endswith("_with_args"):
            unreal.log("이 함수는 인자가 필요하여 직접 실행할 수 없습니다")
        else:
            # 함수명 추출 (PythonFunction_ 접두사 제거)
            func_name = name_str.replace("PythonFunction_", "")
            
            # 선택된 파이썬 파일 경로 가져오기
            file_path = get_selected_python_file_from_context(context)
            
            if file_path and os.path.exists(file_path):
                self._execute_python_function(func_name, file_path)
            else:
                unreal.log_error("파이썬 파일을 찾을 수 없습니다")
    
    def _execute_python_function(self, func_name, file_path):
        """실제 파이썬 함수 실행"""
        exec_command = f"""
import sys
import os
sys.path.insert(0, os.path.dirname(r'{file_path}'))

try:
    module_name = os.path.splitext(os.path.basename(r'{file_path}'))[0]
    
    # 모듈을 다시 로드하여 최신 코드 반영
    import importlib
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        __import__(module_name)
    
    # 함수 실행 및 리턴 값 캡처
    module_obj = sys.modules[module_name]
    func_obj = getattr(module_obj, '{func_name}')
    result = func_obj()
    
    # 객체 깊이 분석 함수
    def analyze_object(obj, name="result", depth=0, max_depth=5):
        indent = "  " * depth
        analysis = []
        
        if depth > max_depth:
            return [f"{{indent}}{{name}}: [Max depth reached]"]
        
        # 기본 정보
        obj_type = type(obj).__name__
        obj_module = getattr(type(obj), '__module__', 'unknown')
        analysis.append(f"{{indent}}{{name}}: {{obj_type}} ({{obj_module}})")
        
        # 값 출력
        try:
            if hasattr(obj, '__dict__') and obj.__dict__:
                analysis.append(f"{{indent}}  Value: {{repr(obj)}}")
            else:
                analysis.append(f"{{indent}}  Value: {{str(obj)}}")
        except:
            analysis.append(f"{{indent}}  Value: [Cannot display]")
        
        # 언리얼 객체인 경우 추가 분석
        if hasattr(obj, '__class__') and 'unreal' in str(type(obj)):
            # 주요 속성들 확인
            if hasattr(obj, 'get_all_properties'):
                try:
                    properties = obj.get_all_properties()
                    if properties:
                        analysis.append(f"{{indent}}  Properties ({{len(properties)}}):")
                        for i, prop in enumerate(properties):  # 모든 프로퍼티 표시
                            analysis.append(f"{{indent}}    [{{i}}] {{prop}}")
                except:
                    pass
            
            # 에디터 속성들 확인
            common_props = ['name', 'class', 'outer', 'package', 'world']
            for prop in common_props:
                if hasattr(obj, prop) or hasattr(obj, f'get_{{prop}}'):
                    try:
                        if hasattr(obj, prop):
                            value = getattr(obj, prop)
                        else:
                            value = getattr(obj, f'get_{{prop}}')()
                        analysis.append(f"{{indent}}  {{prop}}: {{repr(value)}}")
                    except:
                        pass
        
        # dir() 정보 (메서드와 속성들) - 모든 것 표시
        try:
            attrs = [attr for attr in dir(obj) if not attr.startswith('_')]
            if attrs:
                analysis.append(f"{{indent}}  Public attributes ({{len(attrs)}}):")
                
                # 모든 속성 표시
                for attr in attrs:
                    try:
                        attr_obj = getattr(obj, attr)
                        attr_type = type(attr_obj).__name__
                        if callable(attr_obj):
                            analysis.append(f"{{indent}}    {{attr}}() -> {{attr_type}}")
                        else:
                            analysis.append(f"{{indent}}    {{attr}}: {{attr_type}} = {{repr(attr_obj)}}")
                    except:
                        analysis.append(f"{{indent}}    {{attr}}: [Cannot access]")
        except:
            pass
        
        # 딕셔너리나 리스트인 경우 내용 분석 - 모든 내용 표시
        if isinstance(obj, dict) and depth < max_depth:
            analysis.append(f"{{indent}}  Dictionary contents ({{len(obj)}} items):")
            for key, value in obj.items():  # 모든 아이템 표시
                sub_analysis = analyze_object(value, f"[{{repr(key)}}]", depth + 1, max_depth)
                analysis.extend(sub_analysis)
        
        elif isinstance(obj, (list, tuple)) and depth < max_depth and len(obj) > 0:
            analysis.append(f"{{indent}}  {{type(obj).__name__}} contents ({{len(obj)}} items):")
            for i in range(len(obj)):  # 모든 아이템 표시
                sub_analysis = analyze_object(obj[i], f"[{{i}}]", depth + 1, max_depth)
                analysis.extend(sub_analysis)
        
        return analysis
    
    # 리턴 값 로그 출력
    if result is not None:
        analysis_lines = analyze_object(result, "result")
        unreal.log("=" * 60)
        unreal.log(f"✅ 함수 {func_name}() 실행 완료")
        unreal.log("=" * 60)
        for line in analysis_lines:
            unreal.log(line)
        unreal.log("=" * 60)
    else:
        unreal.log(f"✅ 함수 {func_name}() 실행 완료 - 리턴 값: None")
        
except AttributeError as e:
    unreal.log_error(f"❌ 함수 {func_name}()를 찾을 수 없습니다: " + str(e))
except Exception as e:
    unreal.log_error(f"❌ 함수 {func_name}() 실행 오류: " + str(e))
"""
        
        try:
            exec(exec_command)
        except Exception as e:
            unreal.log_error(f"❌ 스크립트 실행 오류: {e}")


@unreal.uclass()
class PythonFunctionsDynamicSection(unreal.ToolMenuSectionDynamic):
    """Python 파일의 함수들을 동적으로 표시하는 메뉴 섹션
    
    기능:
    - 선택된 Python 파일을 AST로 분석
    - 공개 함수들을 동적으로 메뉴에 추가
    - 함수 시그니처와 docstring을 툴팁으로 표시
    - 실행 가능/불가능 상태를 시각적으로 구분
    
    메서드:
    - construct_sections(): 동적 메뉴 구성
    - _add_function_entry(): 개별 함수 메뉴 항목 추가
    """
    
    @unreal.ufunction(override=True)
    def construct_sections(self, menu, context):
        """동적으로 파이썬 함수들을 메뉴에 추가"""
        # 선택된 파이썬 파일 가져오기
        file_path = get_selected_python_file_from_context(context)
        
        if not file_path or not os.path.exists(file_path):
            return  # 파이썬 파일이 없으면 메뉴를 비움
        
        # 파이썬 파일 분석
        functions = analyze_python_file(file_path)
        public_functions = [f for f in functions if not f['is_private']]
        
        if not public_functions:
            return  # 공개 함수가 없으면 메뉴를 비움
        
        # 모든 함수 추가
        for func in public_functions:
            self._add_function_entry(menu, func, file_path, context)
        
        # 통계 로그
        executable_count = len([f for f in public_functions if not f['args']])
        info_count = len(public_functions) - executable_count
        unreal.log(f"✅ {executable_count}개 실행가능 함수, {info_count}개 정보 함수를 동적 메뉴에 추가했습니다")
    
    def _add_function_entry(self, menu, func, file_path, context):
        """함수 엔트리 추가"""
        args_str = f"({', '.join(func['args'])})" if func['args'] else "()"
        label_text = f"{func['name']}{args_str}"
        
        # 툴팁 구성
        status_text = "실행 가능" if not func['args'] else "인자가 필요하여 직접 실행 불가"
        tooltip_text = (
            f"함수: {func['name']}\n"
            f"라인: {func['line']}\n"
            f"인자: {args_str}\n"
            f"상태: {status_text}\n"
            f"설명: {func['docstring'][:100] if func['docstring'] else '설명 없음'}"
        )
        
        # 스크립트 생성 및 데이터 설정
        script = PythonFunctionScript()
        name_suffix = "" if not func['args'] else "_with_args"
        
        script_data = unreal.ToolMenuEntryScriptData(
            menu=menu.menu_name,
            section=unreal.Name('Functions'),
            name=unreal.Name(f'PythonFunction_{func["name"]}{name_suffix}'),
            label=unreal.Text(label_text),
            tool_tip=unreal.Text(tooltip_text),
            icon=unreal.ScriptSlateIcon(),
            insert_position=unreal.ToolMenuInsert(unreal.Name(""), unreal.ToolMenuInsertType.DEFAULT)
        )
        
        script.data = script_data
        script.register_menu_entry()
        menu.add_menu_entry_object(script)

@unreal.uclass()
class PythonReloadScript(unreal.ToolMenuEntryScript):
    """Python 폴더의 모든 모듈을 리로드하는 메뉴 항목 스크립트
    
    기능:
    - Python 폴더(/Python 포함 경로)에서만 활성화
    - 3단계 리로드 프로세스:
      1. 기존 sys.modules에서 관련 모듈 탐지 및 리로드
      2. 새로운 Python 파일들 동적 import
      3. import 실패 시 직접 exec() 실행
    - 하위 폴더까지 재귀적으로 처리
    - 상세한 처리 결과 로깅
    
    메서드:
    - can_execute(): Python 폴더 여부 확인
    - execute(): 3단계 모듈 리로드 실행
    """
    
    @unreal.ufunction(override=True)
    def can_execute(self, context):
        """Python 폴더가 선택된 경우에만 활성화"""
        try:
            context_item = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu) # type: ignore
            if context_item:
                selected_items = context_item.selected_items
                for item in selected_items:
                    virtual_path = str(item.get_virtual_path())
                    if "/Python" in virtual_path:
                        return True
            return False
        except:
            return False

    @unreal.ufunction(override=True)
    def execute(self, context):
        """선택된 Python 폴더의 모든 모듈 리로드"""
        import sys
        import importlib
        
        context_item = context.find_by_class(unreal.ContentBrowserDataMenuContext_FolderMenu) # type: ignore
        if not context_item:
            return
        
        selected_items = context_item.selected_items
        if not selected_items:
            return
        
        # 첫 번째 선택된 폴더 경로 가져오기
        virtual_path = str(selected_items[0].get_virtual_path())
        
        # Python 경로가 포함되지 않으면 실행하지 않음
        if "/Python" not in virtual_path:
            unreal.log_warning("⚠️ Python 폴더가 아닙니다.")
            return
        
        # 폴더명 추출
        folder_name = None
        if "/Game/Python/" in virtual_path:
            folder_name = virtual_path.split("/Game/Python/")[1].split("/")[0]
        elif "/All/Game/Python/" in virtual_path:
            folder_name = virtual_path.split("/All/Game/Python/")[1].split("/")[0]
        elif "/Plugins/" in virtual_path and "/Python/" in virtual_path:
            # 플러그인 내 Python 폴더 처리
            python_part = virtual_path.split("/Python/")[1]
            folder_name = python_part.split("/")[0] if python_part else None
        elif virtual_path.endswith("/Python") or "/Python" in virtual_path:
            folder_name = None  # Python 폴더 자체
        else:
            unreal.log_warning(f"⚠️ 지원하지 않는 Python 경로: {virtual_path}")
            return
        
        unreal.log("=" * 60)
        if folder_name:
            unreal.log(f"🔄 '{folder_name}' 폴더 모듈 리로드 시작...")
        else:
            unreal.log("🔄 Python 전체 모듈 리로드 시작...")
        unreal.log(f"📁 경로: {virtual_path}")
        unreal.log("=" * 60)
        
        # 실제 파일 시스템 경로로 변환
        real_path = convert_virtual_path_to_real_path(virtual_path, is_file=False)
        
        if not real_path or not os.path.exists(real_path):
            unreal.log_error(f"❌ 실제 경로를 찾을 수 없습니다: {virtual_path}")
            return
        
        unreal.log(f"📂 실제 경로: {real_path}")
        
        # 해당 폴더의 Python 파일들 찾기
        python_files = []
        if os.path.isdir(real_path):
            for root, dirs, files in os.walk(real_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        python_files.append(os.path.join(root, file))
        
        if not python_files:
            unreal.log_warning(f"⚠️ Python 파일이 없습니다: {real_path}")
            return
        
        unreal.log(f"📄 발견된 Python 파일: {len(python_files)}개")
        
        # 더 유연한 모듈 리로드 방식
        success_count = 0
        fail_count = 0
        loaded_modules = []
        
        # 1. 기존 sys.modules에서 해당 경로와 관련된 모듈들 찾기
        base_module_names = set()
        if folder_name:
            # 특정 폴더인 경우: folder_name으로 시작하는 모든 모듈
            for module_name in list(sys.modules.keys()):
                if (module_name == folder_name or 
                    module_name.startswith(folder_name + '.')):
                    base_module_names.add(module_name)
        else:
            # Python 폴더 전체인 경우: 알려진 Python 폴더들
            known_folders = ['util', 'tool', 'startup', 'editor', 'developer']
            for module_name in list(sys.modules.keys()):
                for known_folder in known_folders:
                    if (module_name == known_folder or 
                        module_name.startswith(known_folder + '.')):
                        base_module_names.add(module_name)
        
        # 2. 기존 모듈들 리로드
        for module_name in sorted(base_module_names):
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    unreal.log(f"  ✅ 리로드: {module_name}")
                    loaded_modules.append(module_name)
                    success_count += 1
            except Exception as e:
                unreal.log_error(f"  ❌ 리로드 실패 {module_name}: {e}")
                fail_count += 1
        
        # 3. 새로운 파일들 동적 import 시도
        for py_file in python_files:
            try:
                # 간단한 모듈명 생성 (파일 시스템 기반)
                rel_path = os.path.relpath(py_file, real_path)
                module_path = os.path.splitext(rel_path)[0]
                simple_module_name = module_path.replace(os.sep, '.')
                
                # 이미 처리된 모듈이면 스킵
                potential_names = [
                    simple_module_name,
                    f"{folder_name}.{simple_module_name}" if folder_name else simple_module_name,
                    os.path.splitext(os.path.basename(py_file))[0]  # 단순 파일명
                ]
                
                already_processed = any(name in loaded_modules for name in potential_names)
                if already_processed:
                    continue
                
                # 새로 import 시도
                module_dir = os.path.dirname(py_file)
                if module_dir not in sys.path:
                    sys.path.insert(0, module_dir)
                
                # 다양한 방식으로 import 시도
                import_success = False
                for attempt_name in potential_names:
                    try:
                        if attempt_name and attempt_name not in sys.modules:
                            __import__(attempt_name)
                            unreal.log(f"  ✅ 새로 로드: {attempt_name} ({os.path.basename(py_file)})")
                            loaded_modules.append(attempt_name)
                            success_count += 1
                            import_success = True
                            break
                    except:
                        continue
                
                if not import_success:
                    # 직접 파일 실행으로 폴백
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            code = f.read()
                        exec(code, {'__file__': py_file})
                        unreal.log(f"  ✅ 실행: {os.path.basename(py_file)}")
                        success_count += 1
                    except Exception as e:
                        unreal.log_error(f"  ❌ 실행 실패 {os.path.basename(py_file)}: {e}")
                        fail_count += 1
                        
            except Exception as e:
                unreal.log_error(f"  ❌ 처리 실패 {os.path.basename(py_file)}: {e}")
                fail_count += 1
        
        # 결과 요약
        unreal.log("=" * 60)
        unreal.log(f"✅ 성공: {success_count}개")
        if fail_count > 0:
            unreal.log(f"❌ 실패: {fail_count}개")
        
        if loaded_modules:
            unreal.log("📦 로드된 모듈들:")
            for module in loaded_modules:
                unreal.log(f"  - {module}")
        
        unreal.log("🎉 모듈 리로드 완료!")
        unreal.log("=" * 60)


def register_python_menu_entry():
    """Python 파일 컨텍스트 메뉴에 함수 실행 서브메뉴 등록
    
    기능:
    - Python 파일(.py) 우클릭 시 "함수 실행..." 서브메뉴 추가
    - 동적 섹션을 통해 파일의 함수들을 실시간 표시
    - 함수 실행 가능/불가능 상태를 시각적으로 구분
    
    Returns:
        bool: 등록 성공 여부
    """
    try:
        tool_menus = unreal.ToolMenus.get()
        menu = tool_menus.extend_menu(unreal.Name("ContentBrowser.ItemContextMenu.PythonData"))        
        section_name = unreal.Name("PythonScript")        
        # 함수 실행 서브메뉴 추가
        functions_submenu = menu.add_sub_menu(
            owner=section_name,
            section_name=section_name,
            name=unreal.Name("ContentBrowser.ItemContextMenu.PythonData.PythonFunctions"),
            label=unreal.Text("함수 실행..."),
            tool_tip=unreal.Text("파이썬 파일의 함수들을 바로 실행할 수 있습니다")
        )
        
        if functions_submenu:
            # 서브메뉴에 동적 섹션 추가
            dynamic_section = PythonFunctionsDynamicSection()
            functions_submenu.add_dynamic_section(unreal.Name("PythonFunctions"), dynamic_section)
            unreal.log("✅ 파이썬 함수 실행기 등록 완료!")
        else:
            unreal.log("❌ 함수 실행 서브메뉴 생성 실패")
            return False
        
        tool_menus.refresh_all_widgets()
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ 메뉴 등록 오류: {e}")
        return False


def register_python_folder_menu():
    """Python 폴더 컨텍스트 메뉴에 모듈 리로드 기능 추가
    
    기능:
    - Python 폴더(/Python 포함 경로) 우클릭 시 "파이썬 모듈 리로드" 메뉴 추가
    - Python 폴더가 아닌 경우 메뉴 항목 비활성화
    - 3단계 리로드 프로세스로 강력한 모듈 갱신
    - 하위 폴더까지 재귀적으로 처리
    """
    tool_menus = unreal.ToolMenus.get()    
    # 폴더 컨텍스트 메뉴에 추가
    menu_name = unreal.Name("ContentBrowser.FolderContextMenu")
    # 메뉴 확장
    menu = tool_menus.extend_menu(menu_name)
    # 섹션 추가
    python_section = unreal.Name("PythonFolderContext")
    menu.add_section(python_section, unreal.Text("Python Folder Context"))
    # 리로드 스크립트 항목 추가
    entry_name = unreal.Name("PythonReloadScript")
    entry_label = unreal.Text("파이썬 모듈 리로드")
    entry_tooltip = unreal.Text("선택된 Python 폴더의 모든 파이썬 모듈을 다시 로드합니다")
    # 리로드 스크립트 인스턴스 생성 및 초기화. init_entry 에서 자기가 들어갈 곳을 지정한 후 register.menu_entry() 호출 필요
    reload_entry = PythonReloadScript()
    reload_entry.init_entry(menu_name, menu_name, python_section, entry_name, entry_label, entry_tooltip)
    reload_entry.register_menu_entry()
    tool_menus.refresh_all_widgets()


def initialize():
    """Python 컨텍스트 메뉴 시스템 초기화"""
    register_python_menu_entry()
    register_python_folder_menu()


if __name__ == "__main__":
    initialize()


"""
=== Python Context Menu System 개발 가이드 ===

🎯 주요 컴포넌트:
1. PythonFunctionScript: 함수 실행 메뉴 (활성화/비활성화 제어)
2. PythonFunctionsDynamicSection: 동적 함수 목록 생성  
3. PythonReloadScript: 3단계 모듈 리로드 시스템

🔧 핵심 기술:
- AST 파싱: Python 파일 함수 분석
- 동적 메뉴: 선택 상태에 따른 실시간 메뉴 생성
- 유연한 리로드: sys.modules + 동적 import + exec 폴백
- 경로 변환: Unreal 가상 경로 ↔ 실제 파일 시스템

⚙️ 메뉴 등록 패턴:
1. ToolMenuEntryScript 클래스 정의 (@unreal.uclass)
2. can_execute() - 활성화 조건 
3. execute() - 실행 로직
4. register_menu_entry() + add_menu_entry_object()

🚀 확장 가능성:
- 새로운 파일 타입 지원 (Blueprint, Material 등)
- 고급 함수 분석 (타입 힌트, 데코레이터 등)  
- 배치 실행 기능
- 실행 결과 캐싱
"""