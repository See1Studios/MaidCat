import unreal
import random


# 전역 상태 저장소 (언리얼 ufunction 호출 간 Python 인스턴스 변수가 유지되지 않으므로)
_g_spawned_actors = []  # 현재 드래그에서 생성된 액터들
_g_last_spawn_location = None  # 마지막 스폰 위치
_g_actors_to_ignore = set()  # 라인트레이스에서 무시할 액터들


# Tool 프로퍼티 세트
@unreal.uclass()
class MeshSpawnerSettings(unreal.ScriptableInteractiveToolPropertySet):
    # 메시 설정
    static_mesh = unreal.uproperty(unreal.StaticMesh, meta=dict(
        Category="Mesh",
        DisplayName="스태틱 메시",
        Tooltip="스폰할 스태틱 메시"
    ))
    
    # 배치 설정
    use_line_trace = unreal.uproperty(bool, meta=dict(
        Category="Placement",
        DisplayName="라인 트레이스 사용",
        Tooltip="활성화하면 바닥을 검출하여 높이를 자동 설정합니다"
    ))
    min_distance = unreal.uproperty(float, meta=dict(
        Category="Placement",
        DisplayName="최소 거리",
        Tooltip="액터 사이의 최소 거리 (단위: cm)",
        ClampMin="0.0",
        ClampMax="10000.0"
    ))
    
    # 회전 설정
    rotation_x_min = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="X축 회전 최소",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    rotation_x_max = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="X축 회전 최대",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    rotation_y_min = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="Y축 회전 최소",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    rotation_y_max = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="Y축 회전 최대",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    rotation_z_min = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="Z축 회전 최소",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    rotation_z_max = unreal.uproperty(float, meta=dict(
        Category="Rotation",
        DisplayName="Z축 회전 최대",
        ClampMin="-180.0",
        ClampMax="180.0"
    ))
    
    # 스케일 설정
    scale_min = unreal.uproperty(float, meta=dict(
        Category="Scale",
        DisplayName="최소 스케일",
        ClampMin="0.01",
        ClampMax="100.0"
    ))
    scale_max = unreal.uproperty(float, meta=dict(
        Category="Scale",
        DisplayName="최대 스케일",
        ClampMin="0.01",
        ClampMax="100.0"
    ))
    uniform_scale = unreal.uproperty(bool, meta=dict(
        Category="Scale",
        DisplayName="균일 스케일",
        Tooltip="활성화하면 모든 축에 동일한 스케일 적용"
    ))
    
    # 디버그
    show_debug = unreal.uproperty(bool, meta=dict(
        Category="Debug",
        DisplayName="디버그 표시"
    ))
    
    def _post_init(self):
        self.static_mesh = None
        self.use_line_trace = True
        self.min_distance = 300.0
        
        self.rotation_x_min = 0.0
        self.rotation_x_max = 0.0
        self.rotation_y_min = 0.0
        self.rotation_y_max = 0.0
        self.rotation_z_min = 0.0
        self.rotation_z_max = 360.0
        
        self.scale_min = 0.8
        self.scale_max = 1.2
        self.uniform_scale = True
        
        self.show_debug = False


@unreal.uclass()
class MeshSpawnerTool(unreal.ScriptableClickDragTool):
    settings = unreal.uproperty(unreal.ScriptableInteractiveToolPropertySet)
    
    def _post_init(self):
        self.tool_name = unreal.Text("Mesh Spawner")
        self.tool_category = unreal.Text("Python")
        self.tool_tooltip = unreal.Text("드래그하여 메시를 스폰합니다")
        self.show_tool_in_editor = True
        self.want_mouse_hover = True
        
    @unreal.ufunction(override=True)
    def on_script_setup(self):
        global _g_spawned_actors, _g_last_spawn_location, _g_actors_to_ignore
        unreal.log("MeshSpawnerTool 활성화됨")
        
        # 전역 변수 초기화
        _g_spawned_actors = []
        _g_last_spawn_location = None
        _g_actors_to_ignore = set()
        
        try:
            result, outcome = self.add_property_set_of_type(MeshSpawnerSettings, identifier="MeshSpawnerSettings")
            self.settings = result
            
            if self.settings:
                unreal.log("설정 로드됨")
            else:
                unreal.log_warning("설정을 불러오지 못했습니다")
        except Exception as e:
            unreal.log_error(f"설정 로드 에러: {e}")
    
    @unreal.ufunction(override=True)
    def test_if_can_begin_click_drag(self, click_pos: unreal.InputDeviceRay, modifiers: unreal.ScriptableToolModifierStates) -> unreal.InputRayHit:
        """드래그 시작 가능 여부 테스트"""
        hit = unreal.InputRayHit()
        hit.hit = True
        hit.hit_depth = 0.0
        return hit
    
    @unreal.ufunction(override=True)
    def on_drag_begin(self, start_position: unreal.InputDeviceRay, modifiers: unreal.ScriptableToolModifierStates):
        """드래그 시작"""
        global _g_spawned_actors, _g_last_spawn_location
        
        if self.settings and self.settings.show_debug:
            unreal.log("드래그 시작")
        
        # 새로운 드래그 세션 시작 - 리스트 초기화
        _g_spawned_actors = []
        _g_last_spawn_location = None
        
        # Undo 트랜잭션 시작
        unreal.SystemLibrary.begin_transaction("MeshSpawnerTool", unreal.Text("Spawn Meshes"), None)
        
        # 시작 위치에 첫 번째 메시 스폰
        self._try_spawn_mesh(start_position)
    
    @unreal.ufunction(override=True)
    def on_drag_update_position(self, new_position: unreal.InputDeviceRay, modifiers: unreal.ScriptableToolModifierStates):
        """드래그 업데이트 - 메시 스폰"""
        self._try_spawn_mesh(new_position)
    
    @unreal.ufunction(override=True)
    def on_drag_end(self, end_position: unreal.InputDeviceRay, modifiers: unreal.ScriptableToolModifierStates):
        """드래그 종료"""
        global _g_spawned_actors, _g_last_spawn_location, _g_actors_to_ignore
        
        if self.settings and self.settings.show_debug:
            unreal.log(f"드래그 종료 - 총 {len(_g_spawned_actors)}개 메시 스폰됨")
        
        # Undo 트랜잭션 종료
        unreal.SystemLibrary.end_transaction()
        
        # 이번 드래그에서 생성된 액터들을 영구 무시 목록에 추가
        for actor in _g_spawned_actors:
            if actor and unreal.SystemLibrary.is_valid(actor):
                _g_actors_to_ignore.add(actor)
        
        _g_spawned_actors = []
        _g_last_spawn_location = None
    
    @unreal.ufunction(override=True)
    def on_drag_sequence_cancelled(self):
        """드래그 취소됨"""
        global _g_spawned_actors, _g_last_spawn_location
        
        if self.settings and self.settings.show_debug:
            unreal.log("드래그 취소됨")
        
        # 취소 시 이번 드래그에서 생성된 액터들 삭제
        for actor in _g_spawned_actors:
            if actor and unreal.SystemLibrary.is_valid(actor):
                actor.destroy_actor()
        
        unreal.SystemLibrary.cancel_transaction(0)
        
        _g_spawned_actors = []
        _g_last_spawn_location = None
    
    def _try_spawn_mesh(self, device_ray: unreal.InputDeviceRay):
        """메시 스폰 시도"""
        if not self.settings or not self.settings.static_mesh:
            if self.settings and self.settings.show_debug:
                unreal.log_warning("스태틱 메시가 설정되지 않았습니다")
            return
        
        global _g_spawned_actors, _g_last_spawn_location
        
        # 스폰 위치 계산
        spawn_location = self._get_spawn_location(device_ray)
        if spawn_location is None:
            return
        
        # 최소 거리 체크 (수동으로 거리 계산)
        if _g_last_spawn_location is not None:
            dx = spawn_location.x - _g_last_spawn_location.x
            dy = spawn_location.y - _g_last_spawn_location.y
            dz = spawn_location.z - _g_last_spawn_location.z
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            if distance < self.settings.min_distance:
                return
        
        # 회전 계산
        rotation = self._get_random_rotation()
        
        # 스케일 계산
        scale = self._get_random_scale()
        
        # 액터 스폰
        actor = self._spawn_static_mesh_actor(spawn_location, rotation, scale)
        
        if actor:
            _g_spawned_actors.append(actor)
            _g_last_spawn_location = spawn_location
            
            if self.settings.show_debug:
                unreal.log(f"메시 스폰: ({spawn_location.x:.1f}, {spawn_location.y:.1f}, {spawn_location.z:.1f})")
    
    def _get_spawn_location(self, device_ray: unreal.InputDeviceRay) -> unreal.Vector:
        """스폰 위치 계산 (라인 트레이스 사용 시 바닥 검출)"""
        ray = device_ray.world_ray
        
        if not self.settings.use_line_trace:
            # 라인 트레이스 미사용 시 레이 원점에서 일정 거리
            return ray.origin + ray.direction * 1000.0
        
        # 라인 트레이스로 바닥 검출
        start = ray.origin
        end = ray.origin + ray.direction * 100000.0  # 1km 거리
        
        # 무시할 액터 목록 (현재 드래그에서 생성된 액터들 + 이전에 생성된 액터들)
        actors_to_ignore_list = list(_g_spawned_actors) + list(_g_actors_to_ignore)
        
        # 유효하지 않은 액터 필터링 후 Array로 변환
        actors_to_ignore = unreal.Array(unreal.Actor)
        for a in actors_to_ignore_list:
            if a and unreal.SystemLibrary.is_valid(a):
                actors_to_ignore.append(a)
        
        # 디버그: 무시 목록 확인
        if self.settings and self.settings.show_debug:
            unreal.log(f"[DEBUG] 무시할 액터 수: {len(actors_to_ignore)}, _g_spawned_actors: {len(_g_spawned_actors)}, _g_actors_to_ignore: {len(_g_actors_to_ignore)}")
        
        # WorldStatic, WorldDynamic 오브젝트 타입만 검출 (새로 스폰된 액터 제외)
        object_types = unreal.Array(unreal.ObjectTypeQuery)
        object_types.append(unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1)  # WorldStatic
        object_types.append(unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2)  # WorldDynamic
        
        # line_trace_single_for_objects: 특정 오브젝트 타입만 검출
        hit_result = unreal.SystemLibrary.line_trace_single_for_objects(
            unreal.EditorLevelLibrary.get_editor_world(),
            start,
            end,
            object_types,
            False,  # trace_complex
            actors_to_ignore,
            unreal.DrawDebugTrace.FOR_ONE_FRAME if self.settings.show_debug else unreal.DrawDebugTrace.NONE,
            True  # ignore_self
        )
        
        # hit_result가 None이 아니면 히트 성공
        # HitResult는 StructBase - to_tuple()로 접근
        # HitResult __init__ 순서: blocking_hit, initial_overlap, time, distance, location, impact_point, ...
        if hit_result is not None:
            # to_tuple()로 변환 후 impact_point(인덱스 5) 반환
            hit_tuple = hit_result.to_tuple()
            impact_point = hit_tuple[5]  # impact_point (Vector 또는 tuple)
            # Vector로 확실히 변환
            if isinstance(impact_point, unreal.Vector):
                return impact_point
            else:
                return unreal.Vector(impact_point[0], impact_point[1], impact_point[2])
        
        return None
    
    def _get_random_rotation(self) -> unreal.Rotator:
        """랜덤 회전 생성"""
        roll = random.uniform(self.settings.rotation_x_min, self.settings.rotation_x_max)
        pitch = random.uniform(self.settings.rotation_y_min, self.settings.rotation_y_max)
        yaw = random.uniform(self.settings.rotation_z_min, self.settings.rotation_z_max)
        return unreal.Rotator(pitch=pitch, yaw=yaw, roll=roll)
    
    def _get_random_scale(self) -> unreal.Vector:
        """랜덤 스케일 생성"""
        if self.settings.uniform_scale:
            s = random.uniform(self.settings.scale_min, self.settings.scale_max)
            return unreal.Vector(s, s, s)
        else:
            sx = random.uniform(self.settings.scale_min, self.settings.scale_max)
            sy = random.uniform(self.settings.scale_min, self.settings.scale_max)
            sz = random.uniform(self.settings.scale_min, self.settings.scale_max)
            return unreal.Vector(sx, sy, sz)
    
    def _spawn_static_mesh_actor(self, location: unreal.Vector, rotation: unreal.Rotator, scale: unreal.Vector) -> unreal.Actor:
        """스태틱 메시 액터 스폰"""
        world = unreal.EditorLevelLibrary.get_editor_world()
        if not world:
            unreal.log_error("에디터 월드를 가져올 수 없습니다")
            return None
        
        # StaticMeshActor 스폰
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location,
            rotation
        )
        
        if actor:
            # 스태틱 메시 컴포넌트에 메시 설정
            mesh_component = actor.static_mesh_component
            if mesh_component:
                mesh_component.set_static_mesh(self.settings.static_mesh)
            
            # 스케일 설정
            actor.set_actor_scale3d(scale)
            
            # Undo를 위해 트랜잭션에 등록
            actor.modify()
        
        return actor