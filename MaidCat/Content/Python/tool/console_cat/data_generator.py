"""
Unreal Engine 콘솔 명령어 리스트 생성 및 번역 도구

이 스크립트는 Unreal Engine의 ConsoleHelp.html 파일을 파싱하여
콘솔 명령어와 설명을 추출하고, Google Translate API를 사용하여
한국어로 번역한 후 JSON 파일로 저장합니다.
"""

import unreal
import json
import os
import urllib.request
import urllib.parse
import time
import re

# ============================================================================
# 설정 (Configuration)
# ============================================================================

# 처리할 명령어 스코프 (명령어의 '.' 앞부분)
# 예시: SCOPES_TO_PROCESS = ["r", "a", "sg"]
# 비워두면 모든 명령어를 하나의 파일로 처리
SCOPES_TO_PROCESS = ["r", "a"]

# 테스트 모드 설정 (빠른 테스트를 위해 소수의 명령어만 처리)
TEST_MODE_ENABLED = True
TEST_MODE_COMMAND_LIMIT = 5  # 테스트 모드에서 스코프당 처리할 명령어 수

# 출력 디렉토리 및 파일 경로
# ConsoleHelp.html과 같은 위치(Saved 디렉토리)에 JSON 파일 저장
HELP_HTML_FILE = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleHelp.html"
OUTPUT_DIRECTORY = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandData/"

# 번역 사전 파일 경로 (스크립트와 같은 폴더)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSLATION_DICT_FILE = os.path.join(SCRIPT_DIR, "translation_dictionary.json")

# API 요청 딜레이 (공개 API 사용 시 예의를 지키기 위한 대기 시간)
REQUEST_DELAY_SECONDS = 0.05

# ============================================================================
# 유틸리티 함수들 (Utility Functions)
# ============================================================================

def load_translation_dictionary():
    """
    외부 JSON 파일에서 번역 사전을 로드
    파일이 없으면 기본 빈 사전 생성
    
    Returns:
        dict: 영어-한국어 번역 사전
    """
    if not os.path.exists(TRANSLATION_DICT_FILE):
        unreal.log_warning(f"번역 사전 파일을 찾을 수 없습니다: {TRANSLATION_DICT_FILE}")
        unreal.log("기본 빈 사전을 생성합니다.")
        
        # 기본 사전 생성
        default_dict = {
            "Landscape": "랜드스케이프",
            "Render": "렌더",
            "Texture": "텍스처",
            "Material": "머티리얼",
            "Shader": "셰이더",
            "Component": "컴포넌트",
            "Actor": "액터",
            "Light": "라이트",
            "Build": "빌드",
            "Cache": "캐시"
        }
        
        try:
            with open(TRANSLATION_DICT_FILE, "w", encoding="utf-8") as f:
                json.dump(default_dict, f, indent=4, ensure_ascii=False)
            unreal.log(f"기본 번역 사전 파일 생성 완료: {TRANSLATION_DICT_FILE}")
            return default_dict
        except Exception as e:
            unreal.log_error(f"번역 사전 파일 생성 실패: {e}")
            return default_dict
    
    try:
        with open(TRANSLATION_DICT_FILE, "r", encoding="utf-8") as f:
            translation_dict = json.load(f)
        unreal.log(f"번역 사전 로드 완료: {len(translation_dict)}개 항목")
        return translation_dict
    except Exception as e:
        unreal.log_error(f"번역 사전 파일 읽기 실패: {e}")
        return {}


def translate_text_google(text):
    """
    Google Translate 공개 API를 사용하여 텍스트를 한국어로 번역
    
    Args:
        text (str): 번역할 영어 텍스트
        
    Returns:
        str: 번역된 한국어 텍스트, 실패 시 None 또는 빈 문자열
    """
    if not text or text.isspace():
        return ""
    
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ko&dt=t&q={encoded_text}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                unreal.log_error(f"Google Translate 요청 실패 (상태 코드: {response.status})")
                return None
            
            response_body = response.read().decode("utf-8")
            result = json.loads(response_body)
            
            # 번역 결과는 여러 세그먼트로 나뉠 수 있으므로 모두 결합
            full_translation = "".join([segment[0] for segment in result[0] if segment[0]])
            
            if full_translation:
                return full_translation
            else:
                unreal.log_warning(f"Google Translate: 번역 결과를 찾을 수 없음 - {text}")
                return ""
                
    except Exception as e:
        unreal.log_error(f"번역 중 오류 발생: {e}")
        return None

def apply_custom_dictionary(text, dictionary):
    """
    커스텀 사전을 사용하여 특정 단어를 치환
    대소문자 구분 없이 완전한 단어만 치환
    
    Args:
        text (str): 치환할 텍스트
        dictionary (dict): 영어-한국어 치환 사전
        
    Returns:
        str: 치환된 텍스트
    """
    for en_word, kr_word in dictionary.items():
        # 정규식의 단어 경계(\b)를 사용하여 완전한 단어만 치환
        # re.IGNORECASE로 대소문자 구분 없이 치환
        text = re.sub(r'\b' + re.escape(en_word) + r'\b', kr_word, text, flags=re.IGNORECASE)
    return text

def parse_console_help_html(html_content):
    """
    ConsoleHelp.html에서 JavaScript 배열 'cvars'를 찾아 명령어 데이터 추출
    
    Args:
        html_content (str): HTML 파일의 내용
        
    Returns:
        dict: {명령어명: 도움말} 형식의 딕셔너리
    """
    unreal.log("HTML에서 JavaScript 명령어 데이터 추출 중...")
    
    # 스크립트 태그에서 'var cvars = [...]' 배열 찾기
    match = re.search(r"var\s+cvars\s*=\s*(\[[\s\S]*?\]);", html_content)
    if not match:
        unreal.log_error("ConsoleHelp.html에서 'cvars' JavaScript 배열을 찾을 수 없습니다.")
        return {}

    js_array_string = match.group(1)

    # 데이터 구조: [{name:"...", help:"..."}, ... ]
    # 정규식으로 각 객체를 찾아서 name과 help 값을 추출
    commands = {}
    
    # name과 help 키를 찾고, type 같은 다른 키는 무시
    object_regex = re.compile(r'{\s*name:\s*"(?P<name>(?:\\.|[^"\\])*)"\s*,\s*help:\s*"(?P<help>(?:\\.|[^"\\])*)"[^}]*?}')

    for item_match in object_regex.finditer(js_array_string):
        # JavaScript 문자열 리터럴을 언이스케이프
        command_name = item_match.group("name").encode('utf-8').decode('unicode_escape')
        help_text = item_match.group("help").encode('utf-8').decode('unicode_escape')
        
        if command_name:
            commands[command_name] = help_text
            
    return commands

# ============================================================================
# 파일 및 디렉토리 관리 함수들
# ============================================================================

def generate_help_html_if_needed():
    """
    ConsoleHelp.html 파일 존재 여부 확인 및 자동 생성
    파일이 없으면 'help html' 콘솔 명령어를 실행하여 생성
    
    Returns:
        bool: 성공 여부
    """
    if os.path.exists(HELP_HTML_FILE):
        unreal.log(f"ConsoleHelp.html 파일이 이미 존재합니다: {HELP_HTML_FILE}")
        return True
    
    unreal.log("ConsoleHelp.html 파일이 없습니다. 'help html' 명령어로 생성 중...")
    
    # Saved 디렉토리가 없으면 생성
    saved_dir = os.path.dirname(HELP_HTML_FILE)
    if not os.path.exists(saved_dir):
        try:
            os.makedirs(saved_dir)
            unreal.log(f"디렉토리 생성 완료: {saved_dir}")
        except Exception as e:
            unreal.log_error(f"Saved 디렉토리 생성 실패: {e}")
            return False
    
    # helphtml 콘솔 명령어 실행
    try:
        unreal.SystemLibrary.execute_console_command(None, "help html")
        unreal.log("'help html' 콘솔 명령어 실행 완료")
        
        # 파일 생성 대기 (최대 10초)
        max_wait_time = 10
        wait_interval = 0.5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            if os.path.exists(HELP_HTML_FILE):
                unreal.log(f"ConsoleHelp.html 파일 생성 성공: {HELP_HTML_FILE}")
                return True
            time.sleep(wait_interval)
            elapsed_time += wait_interval
        
        unreal.log_error(f"{max_wait_time}초 대기 후에도 ConsoleHelp.html 파일이 생성되지 않았습니다.")
        return False
        
    except Exception as e:
        unreal.log_error(f"'help html' 명령어 실행 실패: {e}")
        return False

def ensure_output_directory():
    """
    출력 디렉토리 존재 여부 확인 및 자동 생성
    
    Returns:
        bool: 성공 여부
    """
    if not os.path.exists(OUTPUT_DIRECTORY):
        unreal.log(f"출력 디렉토리가 없습니다. 생성 중: {OUTPUT_DIRECTORY}")
        try:
            os.makedirs(OUTPUT_DIRECTORY)
            unreal.log(f"출력 디렉토리 생성 성공: {OUTPUT_DIRECTORY}")
            return True
        except Exception as e:
            unreal.log_error(f"출력 디렉토리 생성 실패: {e}")
            return False
    else:
        unreal.log(f"출력 디렉토리 존재 확인: {OUTPUT_DIRECTORY}")
        return True

# ============================================================================
# 메인 처리 함수
# ============================================================================

def generate_command_list_for_scopes():
    """
    ConsoleHelp.html을 읽어서 스코프별로 필터링하고,
    번역하여 개별 JSON 파일로 저장하는 메인 함수
    """
    unreal.log("=== 콘솔 명령어 추출 및 번역 시작 ===")

    # HTML 파일 존재 확인 (없으면 자동 생성)
    if not generate_help_html_if_needed():
        unreal.log_error("ConsoleHelp.html 파일 확보 실패. 작업을 중단합니다.")
        return
    
    # 출력 디렉토리 존재 확인 (없으면 자동 생성)
    if not ensure_output_directory():
        unreal.log_error("출력 디렉토리 확보 실패. 작업을 중단합니다.")
        return
    
    # 번역 사전 로드
    translation_map = load_translation_dictionary()

    # HTML 파일 읽기
    try:
        with open(HELP_HTML_FILE, "r", encoding="utf-8") as f:
            html_content = f.read()
    except IOError as e:
        unreal.log_error(f"ConsoleHelp.html 파일 읽기 실패: {e}")
        return

    # HTML에서 모든 명령어 파싱
    unreal.log("HTML에서 모든 명령어 파싱 중...")
    all_parsed_commands = parse_console_help_html(html_content)
    unreal.log(f"총 {len(all_parsed_commands)}개의 명령어를 찾았습니다.")

    # 스코프별로 명령어 그룹화
    commands_by_scope = {}
    for command, help_text in all_parsed_commands.items():
        scope = command.split('.')[0]
        if scope not in commands_by_scope:
            commands_by_scope[scope] = {}
        commands_by_scope[scope][command] = help_text

    # 처리할 스코프 결정
    scopes_to_run = SCOPES_TO_PROCESS
    if not scopes_to_run:
        # 리스트가 비어있으면 모든 명령어를 하나의 파일로 처리
        scopes_to_run = ["all_commands"]
        commands_by_scope = {"all_commands": all_parsed_commands}

    # 각 스코프별로 처리
    for scope in scopes_to_run:
        commands_to_process = commands_by_scope.get(scope)
        if not commands_to_process:
            unreal.log_warning(f"스코프 '{scope}'에 해당하는 명령어가 없습니다. 건너뜁니다.")
            continue

        # 테스트 모드일 경우 제한된 수의 명령어만 처리
        if TEST_MODE_ENABLED:
            unreal.log(f"--- 테스트 모드: '{scope}' 스코프를 {TEST_MODE_COMMAND_LIMIT}개 명령어로 제한 ---")
            commands_to_process = {k: commands_to_process[k] for k in list(commands_to_process)[:TEST_MODE_COMMAND_LIMIT]}

        total_commands = len(commands_to_process)
        unreal.log(f"스코프 '{scope}'의 {total_commands}개 명령어 처리 중")

        # 명령어 번역 및 데이터 수집
        all_commands_data = []
        with unreal.ScopedSlowTask(total_commands, f"스코프 '{scope}' 명령어 번역 중") as slow_task:
            slow_task.make_dialog(True)
            
            for i, (command_name, help_text_en) in enumerate(commands_to_process.items(), 1):
                if slow_task.should_cancel():
                    unreal.log("사용자가 작업을 취소했습니다.")
                    return

                slow_task.enter_progress_frame(1, f"처리 중 {i}/{total_commands}: {command_name}")
                
                help_text_kr = ""
                if help_text_en:
                    # 먼저 커스텀 사전으로 엔진 용어 치환
                    processed_text_en = apply_custom_dictionary(help_text_en, translation_map)
                    
                    # Google Translate로 번역
                    translated_text = translate_text_google(processed_text_en)
                    if translated_text is None:
                        unreal.log_error(f"'{command_name}' 번역 실패. 건너뜁니다.")
                        help_text_kr = "TRANSLATION_FAILED"
                    else:
                        help_text_kr = translated_text
                    
                    # API 호출 간 대기
                    time.sleep(REQUEST_DELAY_SECONDS)

                all_commands_data.append({
                    "command": command_name,
                    "help_en": help_text_en,
                    "help_kr": help_text_kr,
                })
        
        # 스코프별 JSON 파일로 저장
        output_filename = f"{scope}_commands_kr.json"
        if TEST_MODE_ENABLED:
            output_filename = f"{scope}_commands_kr_TEST.json"
            
        output_path = os.path.join(OUTPUT_DIRECTORY, output_filename)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_commands_data, f, indent=4, ensure_ascii=False)
            unreal.log(f"✓ 스코프 '{scope}'의 {len(all_commands_data)}개 명령어를 저장했습니다: {output_path}")
        except IOError as e:
            unreal.log_error(f"파일 쓰기 실패 ({output_path}): {e}")

    unreal.log("=== 콘솔 명령어 추출 및 번역 완료 ===")


# ============================================================================
# 스크립트 실행
# ============================================================================

if __name__ == "__main__":
    generate_command_list_for_scopes()