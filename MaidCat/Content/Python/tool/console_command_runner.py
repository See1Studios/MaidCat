"""
Unreal Engine 콘솔 명령어 실행기

JSON 파일에서 콘솔 명령어 목록을 로드하고
검색, 필터링, 실행 기능을 제공하는 유틸리티
"""

import unreal
import json
import os


# ============================================================================
# 설정
# ============================================================================

# JSON 데이터 파일 경로
DATA_DIRECTORY = unreal.SystemLibrary.get_project_saved_directory() + "ConsoleCommandData/"


# ============================================================================
# 콘솔 명령어 관리자
# ============================================================================

class ConsoleCommandManager:
    """콘솔 명령어를 로드하고 관리하는 클래스"""
    
    def __init__(self):
        self.commands = []
        self.available_scopes = []
        self.load_all_commands()
    
    def load_all_commands(self):
        """모든 JSON 파일에서 명령어 로드"""
        self.commands = []
        self.available_scopes = []
        
        if not os.path.exists(DATA_DIRECTORY):
            unreal.log_warning(f"데이터 디렉토리를 찾을 수 없습니다: {DATA_DIRECTORY}")
            return
        
        # 디렉토리의 모든 JSON 파일 찾기
        json_files = [f for f in os.listdir(DATA_DIRECTORY) if f.endswith('.json')]
        
        if not json_files:
            unreal.log_warning(f"데이터 파일을 찾을 수 없습니다: {DATA_DIRECTORY}")
            unreal.log("generate_console_command_list.py를 먼저 실행해주세요.")
            return
        
        # 각 JSON 파일 로드
        for json_file in json_files:
            file_path = os.path.join(DATA_DIRECTORY, json_file)
            scope = json_file.replace('_commands_kr.json', '').replace('_TEST', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    
                for cmd_data in commands_data:
                    cmd_data['scope'] = scope
                    self.commands.append(cmd_data)
                
                if scope not in self.available_scopes:
                    self.available_scopes.append(scope)
                    
            except Exception as e:
                unreal.log_error(f"파일 로드 실패 ({json_file}): {e}")
        
        unreal.log(f"✓ {len(self.commands)}개의 명령어를 로드했습니다.")
        unreal.log(f"사용 가능한 스코프: {', '.join(self.available_scopes)}")
    
    def search_commands(self, query, scope_filter=None):
        """
        명령어 검색
        
        Args:
            query (str): 검색어 (명령어 이름 또는 설명)
            scope_filter (str): 스코프 필터 (None이면 모두 검색)
            
        Returns:
            list: 검색 결과 명령어 리스트
        """
        if not query:
            # 쿼리가 없으면 스코프 필터만 적용
            if scope_filter:
                return [cmd for cmd in self.commands if cmd.get('scope') == scope_filter]
            return self.commands
        
        query_lower = query.lower()
        results = []
        
        for cmd in self.commands:
            # 스코프 필터 체크
            if scope_filter and cmd.get('scope') != scope_filter:
                continue
            
            # 명령어 이름 검색
            if query_lower in cmd.get('command', '').lower():
                results.append(cmd)
                continue
            
            # 영어 설명 검색
            if query_lower in cmd.get('help_en', '').lower():
                results.append(cmd)
                continue
            
            # 한국어 설명 검색
            if query_lower in cmd.get('help_kr', '').lower():
                results.append(cmd)
                continue
        
        return results
    
    def get_command_by_name(self, command_name):
        """명령어 이름으로 명령어 정보 가져오기"""
        for cmd in self.commands:
            if cmd.get('command') == command_name:
                return cmd
        return None
    
    def execute_command(self, command_name, args=""):
        """
        콘솔 명령어 실행
        
        Args:
            command_name (str): 실행할 명령어
            args (str): 명령어 인자 (선택사항)
        """
        full_command = f"{command_name} {args}".strip()
        
        unreal.log(f"명령어 실행: {full_command}")
        
        try:
            unreal.SystemLibrary.execute_console_command(None, full_command)
            unreal.log(f"✓ 명령어 실행 완료: {full_command}")
            return True
        except Exception as e:
            unreal.log_error(f"명령어 실행 실패: {e}")
            return False


# ============================================================================
# 간단한 CLI 인터페이스
# ============================================================================

def print_command_info(cmd_data):
    """명령어 정보를 출력"""
    print("\n" + "="*80)
    print(f"명령어: {cmd_data.get('command')}")
    print(f"스코프: {cmd_data.get('scope')}")
    print("-"*80)
    print(f"설명 (EN): {cmd_data.get('help_en', 'N/A')}")
    print(f"설명 (KR): {cmd_data.get('help_kr', 'N/A')}")
    print("="*80)


def print_search_results(results, max_display=20):
    """검색 결과를 출력"""
    if not results:
        print("\n검색 결과가 없습니다.")
        return
    
    print(f"\n검색 결과: {len(results)}개")
    print("-"*80)
    
    for i, cmd in enumerate(results[:max_display], 1):
        kr_help = cmd.get('help_kr', '')
        if len(kr_help) > 60:
            kr_help = kr_help[:60] + "..."
        print(f"{i:2d}. [{cmd.get('scope')}] {cmd.get('command'):30s} - {kr_help}")
    
    if len(results) > max_display:
        print(f"\n... 외 {len(results) - max_display}개 더 있음")


def run_interactive_cli():
    """대화형 CLI 실행"""
    manager = ConsoleCommandManager()
    
    if not manager.commands:
        print("명령어 데이터를 로드할 수 없습니다.")
        return
    
    print("\n" + "="*80)
    print("Unreal Engine 콘솔 명령어 실행기")
    print("="*80)
    print("\n사용 가능한 명령:")
    print("  search <검색어>     - 명령어 검색")
    print("  scope <스코프>      - 스코프별 명령어 보기")
    print("  info <명령어>       - 명령어 상세 정보")
    print("  exec <명령어> [인자] - 명령어 실행")
    print("  list                - 모든 명령어 보기")
    print("  scopes              - 사용 가능한 스코프 보기")
    print("  help                - 도움말")
    print("  exit                - 종료")
    print("-"*80)


def search_commands(query="", scope=None):
    """
    명령어 검색 (외부에서 호출 가능)
    
    Args:
        query (str): 검색어
        scope (str): 스코프 필터
    
    Example:
        search_commands("landscape")
        search_commands("render", scope="r")
    """
    manager = ConsoleCommandManager()
    results = manager.search_commands(query, scope)
    print_search_results(results)
    return results


def execute_command(command_name, args=""):
    """
    콘솔 명령어 실행 (외부에서 호출 가능)
    
    Args:
        command_name (str): 명령어 이름
        args (str): 명령어 인자
        
    Example:
        execute_command("r.SetRes", "1920x1080")
        execute_command("stat fps")
    """
    manager = ConsoleCommandManager()
    return manager.execute_command(command_name, args)


def show_command_info(command_name):
    """
    명령어 상세 정보 표시 (외부에서 호출 가능)
    
    Args:
        command_name (str): 명령어 이름
        
    Example:
        show_command_info("r.SetRes")
    """
    manager = ConsoleCommandManager()
    cmd_data = manager.get_command_by_name(command_name)
    
    if cmd_data:
        print_command_info(cmd_data)
        return cmd_data
    else:
        print(f"\n명령어를 찾을 수 없습니다: {command_name}")
        return None


def list_scopes():
    """사용 가능한 스코프 목록 표시"""
    manager = ConsoleCommandManager()
    print("\n사용 가능한 스코프:")
    print("-"*80)
    for scope in manager.available_scopes:
        count = len([cmd for cmd in manager.commands if cmd.get('scope') == scope])
        print(f"  {scope:10s} - {count}개 명령어")


# ============================================================================
# 빠른 실행 함수들
# ============================================================================

def quick_fps():
    """FPS 표시 토글"""
    execute_command("stat fps")


def quick_unit():
    """프레임 시간 표시 토글"""
    execute_command("stat unit")


def quick_gpu():
    """GPU 통계 표시"""
    execute_command("stat gpu")


def set_resolution(width=1920, height=1080, windowed=True):
    """
    해상도 설정
    
    Args:
        width (int): 너비
        height (int): 높이
        windowed (bool): 창 모드 여부
    """
    mode = "w" if windowed else "f"
    execute_command("r.SetRes", f"{width}x{height}{mode}")


def set_view_distance(scale=1.0):
    """
    뷰 거리 스케일 설정
    
    Args:
        scale (float): 스케일 (0.0 ~ 1.0)
    """
    execute_command("r.ViewDistanceScale", str(scale))


# ============================================================================
# 메인 실행
# ============================================================================

if __name__ == "__main__":
    print("\n콘솔 명령어 실행기가 로드되었습니다.")
    print("\n사용 예시:")
    print("  search_commands('landscape')")
    print("  show_command_info('r.SetRes')")
    print("  execute_command('stat fps')")
    print("  list_scopes()")
    print("\n빠른 실행:")
    print("  quick_fps()  # FPS 표시")
    print("  quick_unit() # 프레임 시간 표시")
    print("  quick_gpu()  # GPU 통계")
    print("  set_resolution(1920, 1080, True)")
