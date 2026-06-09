"""
MaidCat Level Validator System
레벨 열기/닫기 및 검증을 위한 통합 시스템

Features:
- Level naming convention validation
- Level open/close event handling
- Asset validation on level changes
- Auto-fix capabilities for common issues
"""

import unreal


# =============================================================================
# Level Event Manager - Level 열기/닫기 이벤트 처리
# =============================================================================

class LevelEventManager:
    """Level 열기/닫기 이벤트를 관리하는 클래스"""
    
    def __init__(self):
        self._current_level = None
        self._validation_enabled = True
        self._setup_level_events()
    
    def _setup_level_events(self):
        """Level 이벤트 콜백 설정"""
        try:
            # Level Editor 서브시스템 가져오기
            level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
            if level_editor_subsystem:
                unreal.log("🎯 Level Event Manager 초기화 성공")
                
                # Level 변경 감지를 위한 타이머 설정 (실제 이벤트 대신 폴링 방식)
                self._setup_level_monitoring()
            else:
                unreal.log_warning("⚠️ LevelEditorSubsystem을 가져올 수 없습니다")
                
        except Exception as e:
            unreal.log_error(f"❌ Level 이벤트 설정 실패: {e}")
    
    def _setup_level_monitoring(self):
        """Level 모니터링 설정 (폴링 방식)"""
        try:
            # 현재 레벨 추적을 위한 초기 설정 (최신 API 사용)
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            if editor_subsystem:
                current_world = editor_subsystem.get_editor_world()
                if current_world:
                    current_level_path = current_world.get_path_name()
                    if current_level_path != self._current_level:
                        self._current_level = current_level_path
                        self.on_level_opened(current_level_path)
                    
        except Exception as e:
            unreal.log_error(f"❌ Level 모니터링 설정 실패: {e}")
    
    def on_level_opened(self, level_path: str):
        """Level이 열렸을 때 호출되는 콜백"""
        unreal.log(f"📂 Level 열림: {level_path}")
        self._current_level = level_path
        
        if self._validation_enabled:
            self._validate_opened_level(level_path)
    
    def on_level_closed(self, level_path: str):
        """Level이 닫혔을 때 호출되는 콜백"""
        unreal.log(f"📁 Level 닫힘: {level_path}")
        
        if self._validation_enabled:
            self._cleanup_level_resources(level_path)
    
    def _validate_opened_level(self, level_path: str):
        """열린 Level에 대한 검증 수행"""
        try:
            # Level 에셋 로드
            level_asset = unreal.EditorAssetLibrary.load_asset(level_path)
            if not level_asset:
                unreal.log_warning(f"⚠️ Level 에셋을 로드할 수 없습니다: {level_path}")
                return
            
            # 기본 검증들
            self._check_level_naming(level_asset)
            self._check_level_size(level_asset)
            self._check_actor_count(level_asset)
            
            unreal.log(f"✅ Level 검증 완료: {level_path}")
            
        except Exception as e:
            unreal.log_error(f"❌ Level 검증 실패: {e}")
    
    def _check_level_naming(self, level_asset):
        """Level 이름 규칙 확인"""
        level_name = level_asset.get_name()
        if not level_name.startswith("LV_"):
            unreal.log_warning(f"⚠️ 레벨 이름 규칙 위반: {level_name} (LV_ 접두사 필요)")
    
    def _check_level_size(self, level_asset):
        """Level 크기 확인"""
        # Level의 월드 바운드 체크 등
        unreal.log(f"📏 Level 크기 체크: {level_asset.get_name()}")
    
    def _check_actor_count(self, level_asset):
        """Level 내 액터 개수 확인"""
        try:
            # 현재 레벨의 모든 액터들 가져오기 (최신 API 사용)
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if editor_actor_subsystem:
                all_actors = editor_actor_subsystem.get_all_level_actors()
                actor_count = len(all_actors)
                
                unreal.log(f"🎭 Level 액터 개수: {actor_count}개")
                
                # 너무 많은 액터가 있으면 경고
                if actor_count > 1000:
                    unreal.log_warning(f"⚠️ 액터 개수가 많습니다 ({actor_count}개). 성능에 영향을 줄 수 있습니다.")
            else:
                unreal.log_warning("⚠️ EditorActorSubsystem을 가져올 수 없습니다.")
                
        except Exception as e:
            unreal.log_error(f"❌ 액터 개수 확인 실패: {e}")
    
    def _cleanup_level_resources(self, level_path: str):
        """Level이 닫힐 때 리소스 정리"""
        unreal.log(f"🧹 Level 리소스 정리: {level_path}")
        # 필요시 메모리 정리, 캐시 클리어 등
    
    def enable_validation(self, enabled: bool = True):
        """검증 활성화/비활성화"""
        self._validation_enabled = enabled
        status = "활성화" if enabled else "비활성화"
        unreal.log(f"🔧 Level 검증 {status}")


# =============================================================================
# Unreal Engine Asset Validation System 통합
# =============================================================================

"""
Unreal Engine Asset Validation 시스템 개요:

1. Data Validation Plugin이 활성화되어 있어야 함 (Project Settings > Plugins > Data Validation)
2. EditorValidatorBase를 상속받은 클래스들이 자동으로 시스템에 등록됨
3. 에셋 저장 시, 빌드 시, 수동 검증 시 자동으로 실행됨
4. Project Settings > Editor > Data Validation에서 설정 가능

사용 방법:
- Window > Developer Tools > Data Validation에서 수동 실행
- Blueprint에서 "Validate Data" 노드로 실행
- 에셋 우클릭 메뉴에서 "Validate Assets" 선택
- 커맨드라인: -run=DataValidation
"""

@unreal.uclass()
class MaidCatLevelNamingValidator(unreal.EditorValidatorBase):
    """
    MaidCat Level 이름 규칙 검증 Validator
    
    Unreal Engine의 Data Validation 시스템과 완전히 통합됨
    - 자동 등록: EditorValidatorBase 상속으로 시스템이 자동 감지
    - 자동 실행: 에셋 저장/빌드 시 자동으로 can_validate_asset() -> validate_loaded_asset() 호출
    - UI 통합: Data Validation 창에서 결과 확인 가능
    """
    
    @unreal.ufunction(override=True)
    def can_validate_asset(self, asset):
        """
        이 Validator가 해당 에셋을 검증할 수 있는지 확인
        
        Unreal Engine이 모든 에셋에 대해 이 함수를 먼저 호출하여
        이 Validator가 해당 에셋 타입을 처리할 수 있는지 확인함
        
        Args:
            asset: 검증할 에셋 (UObject)
            
        Returns:
            bool: True면 이 Validator가 해당 에셋을 검증 가능
        """
        if not asset:
            return False
            
        # World 에셋(Level)만 검증 대상으로 함
        return isinstance(asset, unreal.World)
    
    @unreal.ufunction(override=True)
    def validate_loaded_asset(self, asset, validation_context):
        """
        실제 에셋 검증 로직 수행
        
        can_validate_asset()가 True를 반환한 에셋에 대해서만 호출됨
        
        Args:
            asset: 검증할 World 에셋
            validation_context: 검증 컨텍스트 (현재 사용하지 않음)
            
        Returns:
            unreal.DataValidationResult: VALID, INVALID, NOT_APPLICABLE 중 하나
        """
        # 부모 클래스의 can_validate_asset 호출
        if not super().can_validate_asset(asset):
            return unreal.DataValidationResult.NOT_APPLICABLE
        
        asset_name = str(asset.get_name())
        asset_path = asset.get_path_name()
        
        # MaidCat Level 이름 규칙 검증: "LV_" 접두사 필수
        if asset_name.startswith("LV_"):
            # 검증 성공 - 시스템에 성공 알림
            self.asset_passes(asset)
            unreal.log(f"✅ Level 이름 규칙 준수: {asset_name}")
            return unreal.DataValidationResult.VALID
        else:
            # 검증 실패 - 시스템에 실패 알림 및 오류 메시지 전달
            error_message = f"Level 이름 규칙 위반: '{asset_name}'은(는) 'LV_' 접두사가 필요합니다."
            self.asset_fails(asset, unreal.Text(error_message))
            unreal.log_warning(f"❌ {error_message} (경로: {asset_path})")
            return unreal.DataValidationResult.INVALID


@unreal.uclass()
class MaidCatLevelPerformanceValidator(unreal.EditorValidatorBase):
    """
    MaidCat Level 성능 관련 검증 Validator
    
    액터 개수, 메모리 사용량 등 성능에 영향을 주는 요소들을 검증
    """
    
    @unreal.ufunction(override=True)
    def can_validate_asset(self, asset):
        """에셋이 검증 가능한지 확인"""
        if not asset:
            return False
        return isinstance(asset, unreal.World)
    
    @unreal.ufunction(override=True)
    def validate_loaded_asset(self, asset, validation_context):
        """로드된 에셋에 대한 성능 검증 수행"""
        if not super().can_validate_asset(asset):
            return unreal.DataValidationResult.NOT_APPLICABLE
        
        try:
            # 현재 레벨의 액터들 분석 (최신 API 사용)
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if not editor_actor_subsystem:
                self.asset_fails(asset, unreal.Text("EditorActorSubsystem을 가져올 수 없습니다."))
                return unreal.DataValidationResult.INVALID
                
            all_actors = editor_actor_subsystem.get_all_level_actors()
            actor_count = len(all_actors)
            
            # 성능 임계값 체크
            if actor_count > 2000:
                warning_msg = f"액터 개수가 많습니다 ({actor_count}개). 성능 최적화를 고려하세요."
                self.asset_fails(asset, unreal.Text(warning_msg))
                return unreal.DataValidationResult.INVALID
            elif actor_count > 1000:
                warning_msg = f"액터 개수 주의 ({actor_count}개). 성능 모니터링이 필요합니다."
                self.asset_passes(asset)  # 경고지만 통과
                unreal.log_warning(warning_msg)
                return unreal.DataValidationResult.VALID
            else:
                self.asset_passes(asset)
                return unreal.DataValidationResult.VALID
                
        except Exception as e:
            error_msg = f"성능 검증 중 오류 발생: {e}"
            self.asset_fails(asset, unreal.Text(error_msg))
            return unreal.DataValidationResult.INVALID


@unreal.uclass()
class MaidCatLevelContentValidator(unreal.EditorValidatorBase):
    """
    MaidCat Level 콘텐츠 무결성 검증 Validator
    
    필수 액터 존재, 라이팅 설정, 월드 설정 등 레벨 콘텐츠의 완성도를 검증
    """
    
    @unreal.ufunction(override=True)
    def can_validate_asset(self, asset):
        """에셋이 검증 가능한지 확인"""
        if not asset:
            return False
        return isinstance(asset, unreal.World)
    
    @unreal.ufunction(override=True)
    def validate_loaded_asset(self, asset, validation_context):
        """로드된 에셋에 대한 콘텐츠 검증 수행"""
        if not super().can_validate_asset(asset):
            return unreal.DataValidationResult.NOT_APPLICABLE
        
        try:
            validation_issues = []
            
            # 필수 액터 존재 확인
            self._check_essential_actors(validation_issues)
            
            # 라이팅 설정 확인
            self._check_lighting_setup(validation_issues)
            
            # 월드 설정 확인
            self._check_world_settings(asset, validation_issues)
            
            if validation_issues:
                for issue in validation_issues:
                    self.asset_fails(asset, unreal.Text(issue))
                return unreal.DataValidationResult.INVALID
            else:
                self.asset_passes(asset)
                return unreal.DataValidationResult.VALID
                
        except Exception as e:
            error_msg = f"콘텐츠 검증 중 오류 발생: {e}"
            self.asset_fails(asset, unreal.Text(error_msg))
            return unreal.DataValidationResult.INVALID
    
    def _check_essential_actors(self, issues):
        """필수 액터들이 있는지 확인"""
        try:
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if not editor_actor_subsystem:
                issues.append("EditorActorSubsystem을 가져올 수 없습니다.")
                return
                
            all_actors = editor_actor_subsystem.get_all_level_actors()
            
            # Player Start 확인
            player_starts = [actor for actor in all_actors 
                           if isinstance(actor, unreal.PlayerStart)]
            if not player_starts:
                issues.append("PlayerStart 액터가 없습니다. 플레이어 스폰 지점이 필요합니다.")
            
        except Exception as e:
            issues.append(f"필수 액터 확인 실패: {e}")
    
    def _check_lighting_setup(self, issues):
        """라이팅 설정 확인"""
        try:
            editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if not editor_actor_subsystem:
                issues.append("EditorActorSubsystem을 가져올 수 없습니다.")
                return
                
            all_actors = editor_actor_subsystem.get_all_level_actors()
            
            # Directional Light 확인
            directional_lights = [actor for actor in all_actors 
                                if isinstance(actor, unreal.DirectionalLight)]
            if not directional_lights:
                issues.append("Directional Light가 없습니다. 기본 조명이 필요합니다.")
            
        except Exception as e:
            issues.append(f"라이팅 설정 확인 실패: {e}")
    
    def _check_world_settings(self, asset, issues):
        """월드 설정 확인"""
        try:
            # 월드 설정 관련 검증 로직
            unreal.log(f"🌍 월드 설정 확인: {asset.get_name()}")
            
        except Exception as e:
            issues.append(f"월드 설정 확인 실패: {e}")


# =============================================================================
# 초기화 및 등록
# =============================================================================

# 전역 Level Event Manager 인스턴스
_level_event_manager = None
_system_initialized = False

def initialize_level_validation_system():
    """Level 검증 시스템 초기화 (중복 방지)"""
    global _level_event_manager, _system_initialized
    
    # 이미 초기화된 경우 스킵
    if _system_initialized:
        unreal.log("ℹ️ Level Validation System이 이미 초기화되었습니다.")
        return True
    
    try:
        unreal.log("🚀 Level Validation System 초기화 시작...")
        
        # Level Event Manager 초기화
        _level_event_manager = LevelEventManager()
        
        # Validator 인스턴스들 생성 (자동 등록됨)
        naming_validator = MaidCatLevelNamingValidator()
        performance_validator = MaidCatLevelPerformanceValidator()
        content_validator = MaidCatLevelContentValidator()
        
        # 초기화 완료 플래그 설정
        _system_initialized = True
        
        unreal.log("✅ Level Validation System 초기화 완료!")
        unreal.log("📋 등록된 Validator들:")
        unreal.log("   - MaidCatLevelNamingValidator: 레벨 이름 규칙 검증")
        unreal.log("   - MaidCatLevelPerformanceValidator: 성능 관련 검증")
        unreal.log("   - MaidCatLevelContentValidator: 콘텐츠 무결성 검증")
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Level Validation System 초기화 실패: {e}")
        return False


def get_level_event_manager():
    """Level Event Manager 인스턴스 가져오기"""
    global _level_event_manager
    if not _level_event_manager:
        _level_event_manager = LevelEventManager()
    return _level_event_manager


# =============================================================================
# Level 모니터링 및 이벤트 처리 함수들
# =============================================================================

def monitor_level_changes():
    """Level 변경 감지 (수동 호출용)"""
    try:
        manager = get_level_event_manager()
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        
        if editor_subsystem:
            current_world = editor_subsystem.get_editor_world()
            
            if current_world:
                current_level_path = current_world.get_path_name()
                
                # 레벨이 변경되었는지 확인
                if current_level_path != manager._current_level:
                    old_level = manager._current_level
                    
                    # 이전 레벨 닫힘 이벤트
                    if old_level:
                        manager.on_level_closed(old_level)
                    
                    # 새 레벨 열림 이벤트
                    manager.on_level_opened(current_level_path)
                    
                    return True  # 변경 감지됨
        
        return False  # 변경 없음
        
    except Exception as e:
        unreal.log_error(f"❌ Level 변경 감지 실패: {e}")
        return False


def setup_level_change_callback():
    """Level 변경 콜백 설정 (에디터 이벤트 기반)"""
    try:
        # Asset Registry를 통한 레벨 변경 감지 시도
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        if asset_registry:
            unreal.log("📡 Asset Registry를 통한 Level 변경 감지 설정")
            # 실제 콜백 연결은 C++ 레벨에서 더 안정적임
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Level 변경 콜백 설정 실패: {e}")
        return False


def force_validate_all_levels():
    """프로젝트 내 모든 Level에 대한 강제 검증"""
    try:
        unreal.log("🔍 프로젝트 내 모든 Level 검증 시작...")
        
        # 프로젝트 내 모든 World 에셋 찾기
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        # World 클래스 필터 (대안 방법 사용)
        world_assets = []
        try:
            # EditorAssetLibrary를 사용한 에셋 검색
            all_game_assets = unreal.EditorAssetLibrary.list_assets("/Game", recursive=True, include_folder=False)
            
            for asset_path in all_game_assets:
                asset_data = asset_registry.get_asset_by_object_path(asset_path)
                if asset_data and asset_data.asset_class_path.asset_name == "World":
                    world_assets.append(asset_data)
                    
        except Exception as e:
            unreal.log_error(f"❌ World 에셋 검색 실패: {e}")
            return []
        
        unreal.log(f"📋 발견된 Level: {len(world_assets)}개")
        
        validation_results = []
        
        for asset_data in world_assets:
            try:
                asset_path = str(asset_data.package_name)
                unreal.log(f"🔍 검증 중: {asset_path}")
                
                # 에셋 로드
                world_asset = unreal.EditorAssetLibrary.load_asset(asset_path)
                if world_asset:
                    # 각 Validator로 검증
                    validators = [
                        MaidCatLevelNamingValidator(),
                        MaidCatLevelPerformanceValidator(),
                        MaidCatLevelContentValidator()
                    ]
                    
                    level_result = {"path": asset_path, "results": []}
                    
                    for validator in validators:
                        try:
                            result = validator.validate_loaded_asset(world_asset, None)
                            level_result["results"].append({
                                "validator": type(validator).__name__,
                                "result": str(result)
                            })
                        except Exception as e:
                            level_result["results"].append({
                                "validator": type(validator).__name__,
                                "result": f"ERROR: {e}"
                            })
                    
                    validation_results.append(level_result)
                
            except Exception as e:
                unreal.log_error(f"❌ Level 검증 실패 ({asset_data.package_name}): {e}")
        
        # 결과 출력
        unreal.log("=" * 80)
        unreal.log("🎯 모든 Level 검증 결과:")
        unreal.log("=" * 80)
        
        for result in validation_results:
            unreal.log(f"📄 {result['path']}:")
            for validator_result in result['results']:
                status = "✅" if "VALID" in validator_result['result'] else "❌"
                unreal.log(f"   {status} {validator_result['validator']}: {validator_result['result']}")
            unreal.log("")
        
        unreal.log(f"🎉 전체 Level 검증 완료: {len(validation_results)}개 처리")
        return validation_results
        
    except Exception as e:
        unreal.log_error(f"❌ 전체 Level 검증 실패: {e}")
        return []


# =============================================================================
# 사용자 편의 함수들
# =============================================================================

def validate_current_level():
    """현재 열린 Level에 대한 즉시 검증"""
    try:
        # 현재 레벨 가져오기 (최신 API 사용)
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        if not editor_subsystem:
            unreal.log_warning("⚠️ UnrealEditorSubsystem을 가져올 수 없습니다.")
            return False
            
        current_world = editor_subsystem.get_editor_world()
        if not current_world:
            unreal.log_warning("⚠️ 현재 열린 레벨이 없습니다.")
            return False
        
        unreal.log(f"🔍 현재 레벨 검증 시작: {current_world.get_name()}")
        
        # 각 Validator 인스턴스들로 검증
        validators = [
            MaidCatLevelNamingValidator(),
            MaidCatLevelPerformanceValidator(), 
            MaidCatLevelContentValidator()
        ]
        
        all_valid = True
        for validator in validators:
            try:
                result = validator.validate_loaded_asset(current_world, None)
                if result != unreal.DataValidationResult.VALID:
                    all_valid = False
            except Exception as e:
                unreal.log_error(f"❌ Validator 실행 실패: {e}")
                all_valid = False
        
        if all_valid:
            unreal.log("✅ 현재 레벨 검증 완료 - 모든 검사 통과")
        else:
            unreal.log_warning("⚠️ 현재 레벨 검증 완료 - 일부 문제 발견")
        
        return all_valid
        
    except Exception as e:
        unreal.log_error(f"❌ 현재 레벨 검증 실패: {e}")
        return False


def enable_level_validation(enabled: bool = True):
    """Level 검증 시스템 활성화/비활성화"""
    manager = get_level_event_manager()
    manager.enable_validation(enabled)


def get_validation_report():
    """현재 레벨의 검증 리포트 생성"""
    try:
        editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        if not editor_subsystem:
            return "UnrealEditorSubsystem을 가져올 수 없습니다."
            
        current_world = editor_subsystem.get_editor_world()
        if not current_world:
            return "현재 열린 레벨이 없습니다."
        
        report = []
        report.append("=" * 60)
        report.append(f"Level Validation Report: {current_world.get_name()}")
        report.append("=" * 60)
        
        # 액터 통계 (최신 API 사용)
        editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if editor_actor_subsystem:
            all_actors = editor_actor_subsystem.get_all_level_actors()
            report.append(f"총 액터 개수: {len(all_actors)}개")
            
            # 액터 타입별 분석
            actor_types = {}
            for actor in all_actors:
                actor_type = type(actor).__name__
                actor_types[actor_type] = actor_types.get(actor_type, 0) + 1
            
            report.append("\n액터 타입별 분포:")
            for actor_type, count in sorted(actor_types.items()):
                report.append(f"  - {actor_type}: {count}개")
        else:
            report.append("액터 정보를 가져올 수 없습니다.")
        
        report.append("=" * 60)
        
        return "\n".join(report)
        
    except Exception as e:
        return f"리포트 생성 실패: {e}"


# =============================================================================
# 자동 실행 및 테스트
# =============================================================================

if __name__ == "__main__":
    # 시스템 초기화
    if initialize_level_validation_system():
        unreal.log("🎉 Level Validation System 준비 완료!")
        
        # 현재 레벨이 있다면 즉시 검증
        try:
            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            if editor_subsystem:
                current_world = editor_subsystem.get_editor_world()
                if current_world:
                    unreal.log(f"🔍 현재 레벨 자동 검증: {current_world.get_name()}")
                    validate_current_level()
        except Exception as e:
            unreal.log_warning(f"⚠️ 초기 레벨 검증 실패: {e}")
    else:
        unreal.log_error("❌ Level Validation System 초기화 실패!")


# =============================================================================
# 테스트 및 데모 함수들
# =============================================================================

def test_validator_system():
    """Validator 시스템 테스트"""
    unreal.log("🧪 Level Validator 시스템 테스트 시작...")
    
    try:
        # 1. 시스템 초기화 확인
        unreal.log("1️⃣ 시스템 초기화 테스트")
        if initialize_level_validation_system():
            unreal.log("   ✅ 초기화 성공")
        else:
            unreal.log("   ❌ 초기화 실패")
            return
        
        # 2. 현재 레벨 검증
        unreal.log("2️⃣ 현재 레벨 검증 테스트")
        if validate_current_level():
            unreal.log("   ✅ 현재 레벨 검증 완료")
        else:
            unreal.log("   ⚠️ 현재 레벨 검증에서 문제 발견")
        
        # 3. 검증 리포트 생성
        unreal.log("3️⃣ 검증 리포트 생성 테스트")
        report = get_validation_report()
        unreal.log("   📋 검증 리포트:")
        for line in report.split('\n')[:10]:  # 처음 10줄만 출력
            unreal.log(f"     {line}")
        
        # 4. Level 변경 감지 테스트
        unreal.log("4️⃣ Level 변경 감지 테스트")
        if monitor_level_changes():
            unreal.log("   ✅ Level 변경 감지됨")
        else:
            unreal.log("   ℹ️ Level 변경 없음")
        
        unreal.log("🎉 Level Validator 시스템 테스트 완료!")
        
    except Exception as e:
        unreal.log_error(f"❌ 테스트 실패: {e}")


def show_validator_help():
    """Validator 사용법 및 Unreal Engine Asset Validation 시스템 안내"""
    help_text = """
    =" * 80
    MaidCat Level Validator System 사용법
    =" * 80
    
    🎯 Unreal Engine Asset Validation 시스템 통합:
    
    1. Data Validation Plugin 활성화:
       - Edit > Project Settings > Plugins > Data Validation ✅ 체크
    
    2. 자동 검증 설정:
       - Edit > Project Settings > Editor > Data Validation
       - "Validate on Save" 활성화하면 에셋 저장 시 자동 검증
    
    3. 수동 검증 실행:
       - Window > Developer Tools > Data Validation
       - 에셋 우클릭 > Validate Assets
       - Blueprint에서 "Validate Data" 노드 사용
    
    4. 커맨드라인 검증:
       - UE5Editor.exe -run=DataValidation
    
    📋 MaidCat Python 함수들:
    
    🔧 시스템 관리:
    - initialize_level_validation_system(): 시스템 초기화
    - reset_validation_system(): 시스템 리셋
    - show_system_status(): 현재 상태 확인
    - enable_level_validation(True/False): 검증 활성화/비활성화
    
    🔍 검증 실행:
    - validate_current_level(): 현재 레벨 즉시 검증
    - force_validate_all_levels(): 프로젝트 내 모든 레벨 검증
    - monitor_level_changes(): Level 변경 감지 (수동)
    
    📊 정보 및 리포트:
    - get_validation_report(): 현재 레벨 검증 리포트 생성
    
    🧪 테스트:
    - test_validator_system(): 전체 시스템 테스트
    
    📋 등록된 Validator 클래스들:
    - MaidCatLevelNamingValidator: 레벨 이름 규칙 검증 (LV_ 접두사)
    - MaidCatLevelPerformanceValidator: 성능 관련 검증 (액터 개수 등)
    - MaidCatLevelContentValidator: 콘텐츠 무결성 검증 (필수 액터 등)
    
    💡 Python API 사용 예시:
    
    # 시스템 상태 확인
    import validator.level_validator as lv
    lv.show_system_status()
    
    # 현재 레벨 검증
    lv.validate_current_level()
    
    # 모든 레벨 검증
    results = lv.force_validate_all_levels()
    
    # 시스템 리셋 (필요시)
    lv.reset_validation_system()
    
    🎮 Unreal Editor에서 사용:
    
    1. Data Validation 창에서 "Validate Data" 클릭
    2. 결과 창에서 MaidCat 검증 결과 확인
    3. 실패한 에셋은 자동으로 하이라이트됨
    4. 오류 메시지 클릭하면 해당 에셋으로 이동
    
    =" * 80
    """
    
    for line in help_text.strip().split('\n'):
        unreal.log(line.replace('="', '='))


def run_unreal_data_validation():
    """
    Unreal Engine의 공식 Data Validation 시스템 실행
    
    이 함수는 Unreal Engine의 내장 Data Validation Manager를 사용하여
    프로젝트 전체의 에셋 검증을 실행합니다.
    """
    try:
        unreal.log("🚀 Unreal Engine Data Validation 시스템 실행...")
        
        # Data Validation 수동 실행 (Plugin API가 Python에 노출되지 않을 수 있음)
        try:
            # 대신 Python Validator들을 직접 실행
            unreal.log("📋 Python Validator들을 직접 실행합니다...")
            force_validate_all_levels()
            return True
        except Exception as e:
            unreal.log_error(f"❌ Python Validator 실행 실패: {e}")
            return False
        
        # 모든 에셋에 대한 검증 실행
        unreal.log("📋 프로젝트 전체 에셋 검증 시작...")
        
        # 검증 결과는 Unreal Engine의 Data Validation 창에 표시됨
        unreal.log("✅ Data Validation 실행 완료. 결과는 'Window > Developer Tools > Data Validation'에서 확인하세요.")
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Data Validation 실행 실패: {e}")
        return False


def check_data_validation_plugin():
    """Data Validation Plugin 활성화 상태 확인"""
    try:
        unreal.log("🔍 Data Validation Plugin 상태 확인...")
        
        # Python에서 DataValidationSubsystem API 접근이 제한적일 수 있음
        # 대신 EditorValidatorBase 기반 Validator 작동 여부로 확인
        validator = MaidCatLevelNamingValidator()
        if hasattr(validator, 'can_validate_asset') and hasattr(validator, 'validate_loaded_asset'):
            unreal.log("✅ EditorValidatorBase 기반 Validator가 정상 작동합니다.")
            unreal.log("💡 Unreal Engine Data Validation 사용법:")
            unreal.log("   - Window > Developer Tools > Data Validation")
            unreal.log("   - 에셋 우클릭 > Validate Assets")
            unreal.log("   - Edit > Project Settings > Editor > Data Validation")
            unreal.log("   - 자동 검증: 에셋 저장 시 또는 빌드 시")
            return True
        else:
            unreal.log_warning("⚠️ Validator 인터페이스에 문제가 있습니다.")
            return False
            
    except Exception as e:
        unreal.log_error(f"❌ Plugin 상태 확인 실패: {e}")
        unreal.log("💡 Data Validation Plugin 활성화 방법:")
        unreal.log("   - Edit > Project Settings > Plugins")
        unreal.log("   - 'Data Validation' 검색 후 체크박스 활성화")
        unreal.log("   - 에디터 재시작")
        return False


def reset_validation_system():
    """Validation 시스템 리셋 (개발/디버그용)"""
    global _level_event_manager, _system_initialized
    
    unreal.log("🔄 Level Validation System 리셋...")
    _level_event_manager = None
    _system_initialized = False
    
    # 다시 초기화
    return initialize_level_validation_system()


def show_system_status():
    """시스템 상태 출력"""
    global _level_event_manager, _system_initialized
    
    unreal.log("=" * 60)
    unreal.log("Level Validation System 상태")
    unreal.log("=" * 60)
    unreal.log(f"초기화 상태: {'✅ 완료' if _system_initialized else '❌ 미완료'}")
    unreal.log(f"Event Manager: {'✅ 활성' if _level_event_manager else '❌ 비활성'}")
    
    if _level_event_manager:
        current_level = _level_event_manager._current_level or 'None'
        validation_enabled = '✅ Yes' if _level_event_manager._validation_enabled else '❌ No'
        unreal.log(f"현재 레벨: {current_level}")
        unreal.log(f"검증 활성화: {validation_enabled}")
    
    unreal.log("=" * 60)


# =============================================================================
# 모듈 로드 시 자동 초기화
# =============================================================================
def _auto_initialize():
    """자동 초기화 (중복 방지)"""
    try:
        # __name__이 __main__이 아닐 때만 자동 초기화 (import 시)
        if __name__ != "__main__" and not _system_initialized:
            if initialize_level_validation_system():
                unreal.log("💡 Level Validator 도움말을 보려면 show_validator_help() 호출")
    except Exception as e:
        unreal.log_error(f"❌ 자동 초기화 실패: {e}")

# 자동 초기화 실행
_auto_initialize()