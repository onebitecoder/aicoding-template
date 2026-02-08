# Instagram-Style MVP (Lite) - Technical Specification (SPEC.md)

> **이 문서의 용도**: 프로젝트 초기 구현 시 Claude가 참고하는 **설계 청사진**입니다.
> 구현 완료 후에는 **코드와 테스트가 Source of Truth**입니다.
>
> **참고**: 이 프로젝트는 **학습/샘플용** 웹 애플리케이션 예시입니다.
> React + FastAPI 풀스택 개발의 구조, 패턴, 베스트 프랙티스를 보여줍니다.

---

## 1. Project Overview

### 1.1 Purpose
사용자가 사진을 업로드하고, 좋아요로 상호작용하는 **소셜 사진 앱 MVP**입니다.

### 1.2 MVP Goals (경량 버전)

- 회원가입/로그인/로그아웃 (Access Token만)
- 프로필(표시 이름/게시글 그리드) — 읽기 전용
- 게시글 업로드(**단일 이미지**), 캡션
- 홈 피드(**전체 최신 게시글**), 게시글 상세
- 좋아요/좋아요 취소

> **범위 제외(Non-goals)**: 팔로우, 해시태그, 검색, 탐색(Explore), 알림(Notifications), 다중 이미지, Reels/Stories/DM, Refresh Token, 이미지 리사이즈/썸네일, 댓글, 프로필 편집/아바타 업로드, 게시글 삭제

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌───────────────────────────────────────────────┐
│              Frontend (React)                   │
│  ┌────────┐ ┌─────────┐ ┌──────────────────┐  │
│  │  Feed  │ │ Profile │ │  Post Detail     │  │
│  └────────┘ └─────────┘ └──────────────────┘  │
│  ┌────────┐ ┌─────────┐                       │
│  │ Upload │ │  Auth   │                       │
│  └────────┘ └─────────┘                       │
└───────────────────────────────────────────────┘
                        ↕ HTTP/REST
┌───────────────────────────────────────────────┐
│              Backend (FastAPI)                   │
│  ┌────────┐ ┌─────────┐ ┌──────────────────┐  │
│  │  Auth  │ │  Posts  │ │     Likes        │  │
│  └────────┘ └─────────┘ └──────────────────┘  │
└───────────────────────────────────────────────┘
          ↕                       ↕
   ┌──────────────┐       ┌──────────────┐
   │ SQLite/Postgres│       │ Local Storage │
   │   (DB)         │       │  (./storage)  │
   └──────────────┘       └──────────────┘
```

### 2.2 Component Breakdown

#### Frontend (React)
- **기술**: React + Vite, TypeScript, TailwindCSS, React Router
- **상태/데이터**: TanStack Query(서버 상태) + Zustand(로컬 UI 상태)
- **주요 화면**: Home Feed / Profile / Post Detail / Upload / Login / Register

#### Backend (FastAPI)
- **기술**: FastAPI, Pydantic, SQLAlchemy 2.x, Alembic
- **인증**: JWT Access Token + bcrypt 해싱
- **스토리지**: 로컬 파일 시스템(./storage)

#### Database
- **개발**: SQLite
- **운영**: PostgreSQL
- **주요 테이블**: users, posts, likes

---

## 3. Core Features & User Stories

### 3.1 Auth & Account
- 사용자는 이메일/비밀번호로 가입하고 로그인한다.
- 사용자는 username으로 프로필 URL을 가진다(`/:username`).

### 3.2 Profile
- 프로필 페이지에서 표시 이름과 게시글 그리드를 본다.
- 프로필은 읽기 전용(회원가입 시 입력한 정보만 표시).

### 3.3 Post (Feed)
- 사용자는 **1장의 이미지**를 업로드하고 캡션을 입력한다.
- 사용자는 홈 피드에서 **전체 최신 게시글**을 본다(offset 페이지네이션).
- 사용자는 게시글 상세에서 이미지와 좋아요 수를 본다.

### 3.4 Social
- 사용자는 게시글에 좋아요/좋아요 취소를 한다.

---

## 4. API Design

> **규칙**: 모든 엔드포인트는 trailing slash 없이 통일 (`/api/v1/...`)

### 4.1 Auth Endpoints
```
POST /api/v1/auth/register
- Body: { email, password, username, display_name? }
- Response: { user, access_token }

POST /api/v1/auth/login
- Body: { email_or_username, password }
- Response: { user, access_token }

POST /api/v1/auth/logout
- Response: { message }
```

### 4.2 User/Profile Endpoints
```
GET  /api/v1/users/me
- Response: { user }

GET  /api/v1/users/{username}
- Response: { user, stats: { posts } }
```

### 4.3 Upload & Posts
```
POST /api/v1/posts
- multipart/form-data: image (1장), caption?
- 서버가 이미지 저장 후 게시글 생성
- Response: { post }

GET  /api/v1/posts/{post_id}
- Response: { post, author, like_count, is_liked }

GET  /api/v1/feed?offset=0&limit=20
- 전체 최신 게시글 피드
- Response: { items: [post...], total, has_next }

GET  /api/v1/users/{username}/posts?offset=0&limit=20
- 프로필 그리드용
```

### 4.4 Likes
```
POST   /api/v1/posts/{post_id}/like
DELETE /api/v1/posts/{post_id}/like
```

### 4.5 System
```
GET /health
- Response: { "status": "healthy" }
```

---

## 5. Database Schema (SQLAlchemy ORM)

> **규칙**: Raw SQL 금지. SQLAlchemy 모델이 스키마의 원천이며 Alembic으로 마이그레이션한다.

### 5.1 Models

```python
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # uuid str
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String)
    created_at = Column(DateTime, default=utcnow)

class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True)  # uuid str
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    image_url = Column(String, nullable=False)  # 단일 이미지
    caption = Column(Text)
    created_at = Column(DateTime, default=utcnow, index=True)

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime, default=utcnow)
```

---

## 6. Business Rules

### 6.1 피드 페이지네이션
- Offset 기반: `offset` + `limit`
- limit 기본 20, 최대 50

### 6.2 업로드 제한
- 1게시글 1장
- 이미지 파일: jpg/png/webp, 최대 10MB

### 6.3 좋아요
- 같은 게시글에 중복 좋아요 불가 (복합 PK로 보장)

---

## 7. Frontend Routes & UX

### 7.1 Routes

| URL | 페이지 | 설명 |
|-----|--------|------|
| `/` | Feed | 홈 피드 (전체 최신) |
| `/p/:postId` | Post Detail | 게시글 상세 |
| `/:username` | Profile | 프로필 (읽기 전용) |
| `/upload` | Upload | 업로드 |
| `/login` | Login | 로그인 |
| `/register` | Register | 회원가입 |

### 7.2 UI/UX Guidelines
- Mobile-first, 하단 탭(Feed/Upload/Profile)
- 피드 카드: 상단(작성자) + 이미지 + 액션(Like) + 캡션
- Optimistic UI: 좋아요는 즉시 반영 후 실패 시 롤백
- Skeleton loading + 빈 상태(empty state) 제공

---

## 8. Security

- 비밀번호: bcrypt 해싱, 최소 8자
- JWT Access Token: 24시간 (MVP 단순화)
- 업로드: MIME 타입 + 확장자 검사
- CORS: 개발 시 `*`, 운영 시 특정 도메인

---

## 9. Development Phases

### Phase 1: Foundation + Auth
- [ ] FastAPI + React(Vite) 프로젝트 스캐폴딩
- [ ] Auth(JWT) + User 모델 + 마이그레이션
- [ ] 기본 레이아웃/라우팅/탭바
- [ ] 로그인/회원가입 페이지

### Phase 2: Posts + Feed + Like
- [ ] Upload API + 로컬 스토리지 연동
- [ ] Post 생성 + 피드(offset 페이지네이션)
- [ ] Post Detail + 프로필 그리드
- [ ] Like/Unlike + Optimistic UI
- [ ] UI 다듬기 + 반응형

---

## 10. Project Structure

```
instagram-mvp/
├── frontend/
│   ├── src/
│   │   ├── api/                # API 클라이언트
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/                # routers
│   │   ├── core/               # config, security
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # business logic
│   │   ├── database.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── storage/                    # 업로드 이미지 저장 (로컬)
├── design/
├── scripts/
├── Dockerfile
├── railway.toml
├── SPEC.md
└── README.md
```

---

## 11. Environment Variables

```bash
# .env.example

# Backend
ENVIRONMENT=development
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=change-me
JWT_ACCESS_EXPIRES_HOURS=24

# Storage
LOCAL_STORAGE_PATH=./storage

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Instagram MVP
```

---

## 12. Testing Strategy

### Backend 테스트
- Auth: register/login, 토큰 검증
- Upload: 파일 타입/크기 제한
- Feed: 전체 최신 게시글 정렬/페이지네이션
- Like: 중복 좋아요 방지, 카운트 정확성

### Frontend 테스트
- 로그인 폼 검증
- 피드 로딩/페이지네이션
- 좋아요 optimistic UI

---

**Document Version**: 1.1-lite
**Template Type**: Instagram-Style MVP (초경량 버전)
**용도**: 초기 구현 청사진 (구현 후에는 코드가 Source of Truth)
