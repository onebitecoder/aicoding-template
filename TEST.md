# TEST.md

> 목적: `SPEC.md`의 요구사항을 **실행 가능한 테스트 시나리오**로 관리하는 검증 기준 문서

## 1) 운영 규칙

1. `SPEC.md` 변경 시 반드시 `TEST.md`를 동기화한다.
2. 구현 완료 조건은 아래 시나리오 전체 PASS다.
3. FAIL 항목이 있으면 구현 미완료로 간주한다.

## 2) 실행 명령

```bash
bash scripts/test.sh lint
bash scripts/test.sh
# 필요 시
bash scripts/test.sh --coverage
```

## 3) Backend API 시나리오 (SPEC 12.1)

| ID | 엔드포인트 | 시나리오 | 기대 결과 |
|---|---|---|---|
| BE-01 | `POST /api/v1/auth/register` | 정상 가입 | 201, `{ user, access_token }` |
| BE-02 | `POST /api/v1/auth/register` | 중복 이메일 | 400, `{ detail }` |
| BE-03 | `POST /api/v1/auth/register` | 비밀번호 8자 미만 | 422 |
| BE-04 | `POST /api/v1/auth/login` | 정상 로그인 | 200, `{ user, access_token }` |
| BE-05 | `POST /api/v1/auth/login` | 잘못된 비밀번호 | 401, `{ detail }` |
| BE-06 | `POST /api/v1/posts` | 정상 업로드 (jpg) | 201, `{ post }` |
| BE-07 | `POST /api/v1/posts` | 잘못된 파일 타입 (gif) | 400, `{ detail }` |
| BE-08 | `GET /api/v1/feed` | 피드 정상 조회 | 200, `{ items, total, has_next }` |
| BE-09 | `GET /api/v1/feed` | 페이지네이션 | 200, `has_next` 정확성 |
| BE-10 | `GET /api/v1/users/{username}` | 존재 유저 조회 | 200, `{ user, stats: { posts } }` |
| BE-11 | `GET /api/v1/users/{username}/posts` | 유저 게시글 조회 | 200, `{ items: Post[], total, has_next }` |
| BE-12 | `POST /api/v1/posts/{id}/like` | 좋아요 | 200 |
| BE-13 | `POST /api/v1/posts/{id}/like` | 중복 좋아요 | 400, `{ detail }` |
| BE-14 | `DELETE /api/v1/posts/{id}/like` | 좋아요 취소 | 200 |

## 4) Frontend 렌더 시나리오 (SPEC 12.2)

| ID | 컴포넌트/페이지 | 시나리오 | 기대 결과 |
|---|---|---|---|
| FE-01 | `LoginPage` | 입력/버튼 렌더 | 이메일/비밀번호/로그인 버튼 표시 |
| FE-02 | `RegisterPage` | 입력 필드 렌더 | 이메일/비밀번호/유저명 표시 |
| FE-03 | `FeedPage` | 목록 렌더 | 게시물 목록 표시 |
| FE-04 | `FeedPage` | 빈 상태 렌더 | empty state 표시 |
| FE-05 | `UploadPage` | 파일 선택 UI 렌더 | `label[for]` + `input` 연결 |
| FE-06 | `ProfilePage` | 프로필/그리드 렌더 | 프로필 정보 + 그리드 표시 |

## 5) 타입 일관성 시나리오 (SPEC 12.3)

| ID | 검증 대상 | 기대 결과 |
|---|---|---|
| TS-01 | `GET /feed` 응답 | Frontend에서 `PostDetail`로 사용 (`post` 중첩 구조) |
| TS-02 | `GET /users/{username}/posts` 응답 | Frontend에서 `Post`로 사용 (직접 필드 구조) |
| TS-03 | `GET /users/{username}` 응답 | Frontend에서 `UserProfile`로 사용 |
| TS-04 | `POST /auth/register`, `POST /auth/login` 응답 | Frontend에서 `AuthResponse`로 사용 |

## 6) 결과 기록 템플릿

| 구분 | 결과 | 상세 |
|------|------|------|
| Frontend Lint | PASS/FAIL | 에러 수 또는 OK |
| Backend Lint | PASS/FAIL | 에러 수 또는 OK |
| Frontend Test | PASS/FAIL | 통과/전체 |
| Backend Test | PASS/FAIL | 통과/전체 |
| 타입 일관성 | PASS/FAIL | 검증 파일/근거 |
| **최종 결과** | **PASS/FAIL** | - |
