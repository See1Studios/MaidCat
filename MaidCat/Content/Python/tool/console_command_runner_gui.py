"""
Unreal Engine 콘솔 명령어 실행기 - GUI 버전

에디터 유틸리티 위젯과 함께 사용하기 위한 백엔드 로직
"""

import unreal
import json
import os


# ============================================================================
# 설정
# ============================================================================

DATA_DIRECTORY = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandData/"


# ============================================================================
# GUI 콘솔 명령어 매니저
# ============================================================================

@unreal.uclass()
class ConsoleCommandRunnerLibrary(unreal.BlueprintFunctionLibrary):
    """블루프린트에서 호출 가능한 함수 라이브러리"""
    
    @unreal.ufunction(
        static=True,
        ret=unreal.Array(str),
        params=[],
        meta=dict(Category="Console Commands")
    )
    def load_command_list():
        """모든 콘솔 명령어 목록 로드 (명령어 이름만)"""
        commands = []
        
        if not os.path.exists(DATA_DIRECTORY):
            unreal.log_warning(f"데이터 디렉토리를 찾을 수 없습니다: {DATA_DIRECTORY}")
            return commands
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    commands.append(cmd_data.get('command', ''))
                    
            except Exception as e:
                unreal.log_error(f"파일 로드 실패 ({json_file}): {e}")
        
        return sorted(commands)
    
    @unreal.ufunction(
        static=True,
        ret=unreal.Array(str),
        params=[str],
        meta=dict(Category="Console Commands")
    )
    def search_commands(query):
        """명령어 검색"""
        all_commands = []
        
        if not os.path.exists(DATA_DIRECTORY):
            return all_commands
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        query_lower = query.lower()
        
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    command_name = cmd_data.get('command', '')
                    help_en = cmd_data.get('help_en', '')
                    help_kr = cmd_data.get('help_kr', '')
                    
                    # 검색 조건
                    if (query_lower in command_name.lower() or 
                        query_lower in help_en.lower() or 
                        query_lower in help_kr.lower()):
                        all_commands.append(command_name)
                    
            except Exception as e:
                unreal.log_error(f"파일 로드 실패 ({json_file}): {e}")
        
        return sorted(all_commands)
    
    @unreal.ufunction(
        static=True,
        ret=str,
        params=[str],
        meta=dict(Category="Console Commands")
    )
    def get_command_description_kr(command_name):
        """명령어의 한국어 설명 가져오기"""
        if not os.path.exists(DATA_DIRECTORY):
            return "설명을 찾을 수 없습니다."
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    if cmd_data.get('command') == command_name:
                        return cmd_data.get('help_kr', '설명 없음')
                    
            except Exception as e:
                continue
        
        return "설명을 찾을 수 없습니다."
    
    @unreal.ufunction(
        static=True,
        ret=str,
        params=[str],
        meta=dict(Category="Console Commands")
    )
    def get_command_description_en(command_name):
        """명령어의 영어 설명 가져오기"""
        if not os.path.exists(DATA_DIRECTORY):
            return "Description not found."
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    if cmd_data.get('command') == command_name:
                        return cmd_data.get('help_en', 'No description')
                    
            except Exception as e:
                continue
        
        return "Description not found."
    
    @unreal.ufunction(
        static=True,
        ret=bool,
        params=[str, str],
        meta=dict(Category="Console Commands")
    )
    def execute_console_command(command_name, args=""):
        """콘솔 명령어 실행"""
        full_command = f"{command_name} {args}".strip()
        
        try:
            unreal.log(f"명령어 실행: {full_command}")
            unreal.SystemLibrary.execute_console_command(None, full_command)
            return True
        except Exception as e:
            unreal.log_error(f"명령어 실행 실패: {e}")
            return False
    
    @unreal.ufunction(
        static=True,
        ret=unreal.Array(str),
        params=[],
        meta=dict(Category="Console Commands")
    )
    def get_available_scopes():
        """사용 가능한 스코프 목록 가져오기"""
        scopes = []
        
        if not os.path.exists(DATA_DIRECTORY):
            return scopes
        
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        for json_file in json_files:
            scope = json_file.replace('_commands_kr.json', '').replace('_TEST', '')
            if scope not in scopes:
                scopes.append(scope)
        
        return sorted(scopes)
    
    @unreal.ufunction(
        static=True,
        ret=unreal.Array(str),
        params=[str],
        meta=dict(Category="Console Commands")
    )
    def get_commands_by_scope(scope):
        """특정 스코프의 명령어 목록 가져오기"""
        commands = []
        
        if not os.path.exists(DATA_DIRECTORY):
            return commands
        
        # 스코프에 해당하는 파일 찾기
        target_files = [f for f in os.listdir(DATA_DIRECTORY) 
                       if f.startswith(f"{scope}_") and f.endswith('.json')]
        
        for json_file in target_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    commands.append(cmd_data.get('command', ''))
                    
            except Exception as e:
                unreal.log_error(f"파일 로드 실패 ({json_file}): {e}")
        
        return sorted(commands)


# ============================================================================
# 즐겨찾기 관리
# ============================================================================

FAVORITES_FILE = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandFavorites.json"


def load_favorites():
    """즐겨찾기 로드"""
    if not os.path.exists(FAVORITES_FILE):
        return []
    
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        unreal.log_error(f"즐겨찾기 로드 실패: {e}")
        return []


def save_favorites(favorites):
    """즐겨찾기 저장"""
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        unreal.log_error(f"즐겨찾기 저장 실패: {e}")
        return False


def add_to_favorites(command_name):
    """즐겨찾기에 추가"""
    favorites = load_favorites()
    
    if command_name not in favorites:
        favorites.append(command_name)
        save_favorites(favorites)
        unreal.log(f"즐겨찾기 추가: {command_name}")
        return True
    else:
        unreal.log_warning(f"이미 즐겨찾기에 있음: {command_name}")
        return False


def remove_from_favorites(command_name):
    """즐겨찾기에서 제거"""
    favorites = load_favorites()
    
    if command_name in favorites:
        favorites.remove(command_name)
        save_favorites(favorites)
        unreal.log(f"즐겨찾기 제거: {command_name}")
        return True
    else:
        unreal.log_warning(f"즐겨찾기에 없음: {command_name}")
        return False


def get_favorites():
    """즐겨찾기 목록 가져오기"""
    return load_favorites()


# ============================================================================
# 명령어 히스토리 관리
# ============================================================================

HISTORY_FILE = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandHistory.json"
MAX_HISTORY = 50


def load_history():
    """히스토리 로드"""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        unreal.log_error(f"히스토리 로드 실패: {e}")
        return []


def save_history(history):
    """히스토리 저장"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history[:MAX_HISTORY], f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        unreal.log_error(f"히스토리 저장 실패: {e}")
        return False


def add_to_history(command_with_args):
    """히스토리에 추가"""
    history = load_history()
    
    # 이미 있으면 제거하고 맨 앞에 추가 (최근 사용순)
    if command_with_args in history:
        history.remove(command_with_args)
    
    history.insert(0, command_with_args)
    save_history(history)


def get_history():
    """히스토리 목록 가져오기"""
    return load_history()


def clear_history():
    """히스토리 초기화"""
    save_history([])
    unreal.log("히스토리가 초기화되었습니다.")


# ============================================================================
# 편의 함수들
# ============================================================================

def execute_and_log(command_name, args=""):
    """명령어 실행 및 히스토리 저장"""
    full_command = f"{command_name} {args}".strip()
    
    success = ConsoleCommandRunnerLibrary.execute_console_command(command_name, args)
    
    if success:
        add_to_history(full_command)
    
    return success


# ============================================================================
# 사전 정의된 명령어 프리셋
# ============================================================================

COMMAND_PRESETS = {
    "Performance": {
        "FPS 표시": "stat fps",
        "프레임 시간": "stat unit",
        "GPU 통계": "stat gpu",
        "렌더 통계": "stat rhi",
        "메모리 통계": "stat memory",
    },
    "Rendering": {
        "1080p 창모드": "r.SetRes 1920x1080w",
        "1080p 전체화면": "r.SetRes 1920x1080f",
        "4K 창모드": "r.SetRes 3840x2160w",
        "안티앨리어싱 끄기": "r.PostProcessAAQuality 0",
        "안티앨리어싱 최고": "r.PostProcessAAQuality 6",
    },
    "Debug": {
        "와이어프레임": "viewmode wireframe",
        "라이팅만": "viewmode lit",
        "언릿": "viewmode unlit",
        "콜리전 표시": "show collision",
        "네비메시 표시": "show navigation",
    },
}


def get_presets():
    """프리셋 목록 가져오기"""
    return COMMAND_PRESETS


def execute_preset(category, preset_name):
    """프리셋 실행"""
    if category in COMMAND_PRESETS:
        if preset_name in COMMAND_PRESETS[category]:
            command = COMMAND_PRESETS[category][preset_name]
            parts = command.split(' ', 1)
            cmd_name = parts[0]
            cmd_args = parts[1] if len(parts) > 1 else ""
            
            return execute_and_log(cmd_name, cmd_args)
    
    return False


if __name__ == "__main__":
    unreal.log("콘솔 명령어 실행기 GUI 백엔드가 로드되었습니다.")
