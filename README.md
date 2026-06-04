# MaidCat

언리얼 엔진 작업 도구상자 플러그인. 개인 작업에 쓰는 Python 도구, 머티리얼 함수, 에디터 확장을 한 곳에 모아 어떤 UE 프로젝트에서도 동일한 작업 환경을 재현하기 위한 것.

## 설치

다른 UE 프로젝트에 symlink로 통합한다.

1. 이 리포지토리를 원하는 위치에 git clone
2. 루트의 `InstallAsLink.bat` 실행 → 대상 UE 프로젝트 경로 입력
3. 대상 프로젝트의 `Plugins/MaidCat/`에 symlink가 생성되고 `dev.local.json`이 자동 생성됨

## 의존성

- **Unreal Engine 5.x**
- **[TAPython](https://github.com/cgerchenhp/UE_TAPython_Plugin_Release)** — Python으로 네이티브 Slate UI 작성

자세한 폴더 구조, Python 코드베이스, UE Python API 카탈로그는 [AGENTS.md](AGENTS.md)에 정리되어 있다.

## AI 작업 환경

이 리포지토리는 AI 코딩 어시스턴트(Claude Code / GitHub Copilot / Google Antigravity / OpenAI Codex)의 작업 환경이 함께 들어있다. 진입점은 2개로 최소화:

- [AGENTS.md](AGENTS.md) — 공통 진입점. Copilot, Antigravity, Codex가 자동 인식하는 SSOT
- [CLAUDE.md](CLAUDE.md) — Claude Code용. `@AGENTS.md` import + Claude 전용 추가 지시

## 문서

- [docs/See1Blur.md](docs/See1Blur.md) — Mipmap-assisted temporal dithering 기반 효율적 블러 기법
