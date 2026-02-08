# Instagram-Style MVP (Lite) - Technical Specification (SPEC.md)

> **이 문서의 용도**: 프로젝트 초기 구현 시 Claude가 참고하는 **설계 청사진**입니다.
> 구현 완료 후에는 **코드와 테스트가 Source of Truth**입니다.
>
> **참고**: 이 프로젝트는 **학습/샘플용** 웹 애플리케이션 예시입니다.
> React + FastAPI 풀스택 개발의 구조, 패턴, 베스트 프랙티스를 보여줍니다.

---

## 1. Project Overview

### 1.1 Purpose
사용자가 사진을 업로드하고, 좋아요/댓글로 상호작용하는 **소셜 사진 앱 MVP**입니다.

### 1.2 MVP Goals (경량 버전)

- 회원가입/로그인/로그아웃 (Access Token만)
- 프로필(사진/소개/게시글 그리드) + 프로필 편집
- 게시글 업로드(**단일 이미지**), 캡션
- 홈 피드(**전체 최신 게시글**), 게시글 상세
- 좋아요/댓글(작성/삭제)

> **범위 제외(Non-goals)**: 팔로우, 해시태그, 검색, 탐색(Explore), 알림(Notifications), 다중 이미지, Reels/Stories/DM, Refresh Token, 이미지 리사이즈/썸네일

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
│  │  Auth  │ │  Posts  │ │     Social       │  │
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
- **주요 테이블**: users, posts, likes, comments

---

## 3. Core Features & User Stories

### 3.1 Auth & Account
- 사용자는 이메일/비밀번호로 가입하고 로그인한다.
- 사용자는 username으로 프로필 URL을 가진다(`/:username`).

### 3.2 Profile
- 사용자는 프로필 사진, 표시 이름, bio를 설정한다.
- 프로필 페이지에서 게시글 그리드를 본다.

### 3.3 Post (Feed)
- 사용자는 **1장의 이미지**를 업로드하고 캡션을 입력한다.
- 사용자는 홈 피드에서 **전체 최신 게시글**을 본다(커서 페이지네이션).
- 사용자는 게시글 상세에서 댓글을 보고 작성한다.

### 3.4 Social
- 사용자는 게시글에 좋아요/좋아요 취소를 한다.
- 사용자는 댓글을 작성/삭제한다(본인 댓글만 삭제).

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
PATCH /api/v1/users/me
- Body: { display_name?, bio? }

POST /api/v1/users/me/avatar
- multipart/form-data: file
- Response: { avatar_url }

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
- Response: { post, author, like_count, comment_count, is_liked }

DELETE /api/v1/posts/{post_id}
- 본인 게시글만 삭제

GET  /api/v1/feed?cursor=&limit=
- 전체 최신 게시글 피드
- Response: { items: [post...], next_cursor }

GET  /api/v1/users/{username}/posts?cursor=&limit=
- 프로필 그리드용
```

### 4.4 Likes
```
POST   /api/v1/posts/{post_id}/like
DELETE /api/v1/posts/{post_id}/like
```

### 4.5 Comments
```
GET  /api/v1/posts/{post_id}/comments?cursor=&limit=
POST /api/v1/posts/{post_id}/comments
- Body: { content }
DELETE /api/v1/comments/{comment_id}
```

### 4.6 System
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
    bio = Column(Text)
    avatar_url = Column(String)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

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

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)  # uuid str
    post_id = Column(String, ForeignKey("posts.id"), index=True)
    author_id = Column(String, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)
```

---

## 6. Business Rules

### 6.1 권한
- 게시글/댓글 삭제: 작성자만 가능

### 6.2 삭제
- 게시글 삭제(hard delete) → 연관 좋아요/댓글도 cascade 삭제
- 댓글 삭제(hard delete)

### 6.3 피드 페이지네이션
- Cursor 기반: `cursor = created_at + id` 조합
- limit 기본 20, 최대 50

### 6.4 업로드 제한
- 1게시글 1장
- 이미지 파일: jpg/png/webp, 최대 10MB

---

## 7. Frontend Routes & UX

### 7.1 Routes

| URL | 페이지 | 설명 |
|-----|--------|------|
| `/` | Feed | 홈 피드 (전체 최신) |
| `/p/:postId` | Post Detail | 게시글 상세 |
| `/:username` | Profile | 프로필 |
| `/upload` | Upload | 업로드 |
| `/login` | Login | 로그인 |
| `/register` | Register | 회원가입 |

### 7.2 UI/UX Guidelines
- Mobile-first, 하단 탭(Feed/Upload/Profile)
- 피드 카드: 상단(작성자) + 이미지 + 액션(Like/Comment) + 캡션 + 댓글 일부
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

### Phase 1: Foundation
- [ ] FastAPI + React(Vite) 프로젝트 스캐폴딩
- [ ] Auth(JWT) + User 모델 + 마이그레이션
- [ ] 기본 레이아웃/라우팅/탭바

### Phase 2: Posts + Social
- [ ] Upload API + 로컬 스토리지 연동
- [ ] Post CRUD + 프로필 그리드
- [ ] Feed(전체 최신) + Post Detail
- [ ] Like/Unlike + Comment CRUD

### Phase 3: Polish
- [ ] UI 다듬기 + 반응형
- [ ] 프로필 편집 + 아바타 업로드

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
- Comment: 작성/삭제 권한

### Frontend 테스트
- 로그인 폼 검증
- 피드 로딩/무한스크롤
- 좋아요 optimistic UI
- 댓글 작성/삭제

---

**Document Version**: 1.0-lite
**Template Type**: Instagram-Style MVP (경량 버전)
**용도**: 초기 구현 청사진 (구현 후에는 코드가 Source of Truth)
