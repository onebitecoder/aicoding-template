---
description: 현재 프로젝트의 frontend(React)와 backend(FastAPI)를 대규모 설계 변경 없이 리팩터링
allowed-tools: Read, Grep, Glob, Edit, Bash(git status:*), Bash(git diff:*), Bash(find:*), Bash(ls:*), Bash(pnpm:*), Bash(npm:*), Bash(yarn:*), Bash(pytest:*), Bash(python:*), Bash(ruff:*), Bash(mypy:*), Bash(uv:*), Bash(poetry:*), Bash(make:*)
---

## 컨텍스트 (현재 저장소 스냅샷)
- Current directory listing: !`ls`
- Git status: !`git status`
- Git diff (working tree): !`git diff`

## 작업
당신은 현재 디렉토리에서 작업하는 Claude입니다.
이 저장소는 React 프론트엔드와 FastAPI 백엔드를 포함합니다. 목표는 두 코드베이스를 모두 리팩터링하는 것입니다.

## 강한 제약 (반드시 준수)
1) **대규모 디자인/UX 변경 금지**
   - 화면, 레이아웃, 시각 스타일, 상호작용 흐름을 재설계하지 않는다.
   - 사용자가 체감하는 UI 구조/동작을 바꾸지 않는다.
   - UI 변경은 전체 흐름을 바꾸지 않는 **버그 수정**, **접근성 개선**, **작은 일관성 정리**로 제한한다.
2) 명확한 버그 수정이 아닌 한 **외부 동작 변경 금지**.
3) 변경은 **점진적이고, 리뷰 가능하며, 저위험**하게 유지한다.
4) API 계약 변경을 피한다. 불가피할 경우 반드시 둘 다 업데이트:
   - Backend: routes + schemas(Pydantic) + service layer
   - Frontend: API client + types + usage sites

## 범위 탐색 (가장 먼저 수행)
1) 일반적인 폴더 패턴을 검색해 프론트엔드/백엔드 루트를 식별한다:
   - Frontend candidates: `frontend/`, `web/`, `client/`, `apps/web/`, `src/`
   - Backend candidates: `backend/`, `server/`, `api/`, `apps/api/`, `app/`
2) 도구와 실행 명령을 감지한다:
   - Frontend: `package.json`, lockfile (`pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`)
   - Backend: `pyproject.toml`, `requirements.txt`, `uv.lock`, `poetry.lock`, `Pipfile`
3) 양쪽을 모두 찾았는지 확인한다. 한쪽이 없으면 존재하는 쪽만 리팩터링하고 누락 사실을 보고한다.

## 리팩터링 목표 (우선순위)

### A) Frontend (React)
- 중복을 줄이고 가독성을 높이며 컴포넌트를 단순화
- 타입 안정성과 props/interface 일관성 강화
- 로딩/에러 처리 패턴 정규화
- **작고 안전한 이동만**으로 모듈 경계를 개선 (대규모 재구조화 금지)

### B) Backend (FastAPI)
- router/service 경계를 명확히 하고 dead code 제거
- Pydantic 스키마 일관성과 타이핑 개선
- 반복되는 검증/에러 처리 통합
- 엔드포인트/하위 호환성 유지

## 실행 계획 (필수)
1) 편집 전에 3~6개 항목의 짧은 계획을 작성한다.
2) 변경은 작은 배치(응집도 높은 diff)로 나눈다.
3) 각 배치 후, 가능한 가장 관련성 높은 검사를 실행한다:
   - Frontend (pick what exists): `pnpm lint`, `pnpm test`, `pnpm build` (or `npm/yarn`)
   - Backend (pick what exists): `ruff check`, `pytest`, `mypy`
   - `Makefile`이 있으면 `make test`/`make lint`를 우선 활용한다.
4) 명령이 실패하면 단순 이슈는 즉시 수정한다. 대규모 리팩터링이나 디자인 변경이 필요하면 중단 후 보고한다.

## 출력 형식 (필수)
- 탐색 결과 (frontend/backend 루트 + 툴링)
- 계획
- 변경 사항 (파일별 + 변경 이유)
- 실행 명령 + 결과 (또는 실행해야 할 정확한 명령)
- 리스크 / 후속 작업 (선택)
