# CLAUDE.md

@AGENTS.md

## Claude Code 전용 추가 지시

- **Skill 시스템**: `.claude/skills/` 안의 Skill은 description 매칭으로 자동 트리거. 도메인 요청 시 references/ 자료를 읽고 정의된 출력 포맷을 따른다.
- **사용자 글로벌 원칙**: `~/.claude/CLAUDE.md`의 사용자 범용 코딩 원칙(DRY, 하드코딩 금지, 함수 분리 등)도 자동 로드되어 누적 적용된다. AGENTS.md와 충돌 시 더 구체적인 쪽을 우선.
- **메모리 시스템**: `~/.claude/projects/.../memory/`는 사용자 머신 한정. 플러그인 본문(`wiki/`)과 구분해서 관리한다 — 머신 간 동기화가 필요한 트러블슈팅/팁은 `wiki/`로.
- **코드 위치 참조**: `[file.py:42](file.py#L42)` markdown 링크 형식 사용 (VSCode 확장 클릭 이동 지원).
