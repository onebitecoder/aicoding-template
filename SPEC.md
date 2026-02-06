# Instagram-Style MVP - Technical Specification (SPEC.md)

> **이 문서의 용도**: 프로젝트 초기 구현 시 Claude가 참고하는 **설계 청사진**입니다.  
> 구현 완료 후에는 **코드와 테스트가 Source of Truth**입니다.  
> 큰 아키텍처 변경이 있을 때만 이 문서를 업데이트합니다.
>
> **참고**: 이 프로젝트는 **학습/샘플용** 웹 애플리케이션 예시입니다.  
> React + FastAPI 풀스택 개발의 구조, 패턴, 베스트 프랙티스를 보여줍니다.

---

## 0. Data Flow Definition (필수 - 프로젝트 시작 전 정의)

> **IMPORTANT**: 데이터 소스와 흐름을 먼저 정의하지 않으면 업로드/피드/권한/캐시에서 큰 삽질이 발생합니다.

### 0.1 Data Source (데이터 소스)

| 항목 | 내용 |
|------|------|
| **소스 타입** | User-Generated Content + Storage + DB |
| **소스 이름** | (1) 사용자 업로드 이미지 (2) 관계형 DB |
| **접근 방법** | Backend 업로드 API → Object Storage(S3 호환) → CDN URL 제공 |
| **인증 필요** | Yes (JWT 기반) |
| **비용** | 로컬 개발: 무료 / 운영: 스토리지+대역폭 비용 |
| **Rate Limit** | 업로드/로그인/검색 등은 제한 필요 (IP/User 기반) |

#### 스토리지 권장
- **개발**: 로컬 파일 시스템(./storage) 또는 MinIO
- **운영**: S3 호환(Object Storage) + CDN  
  (예: AWS S3, Cloudflare R2, Supabase Storage, Backblaze B2 등)

---

### 0.2 Input (사용자 입력)

| 입력 항목 | 타입 | 예시 | 필수 |
|-----------|------|------|------|
| 회원가입 이메일 | String | user@example.com | 필수 |
| 비밀번호 | String | ******** | 필수 |
| 사용자명(username) | String | sangwoo | 필수 (유니크) |
| 프로필 이름 | String | Sangwoo | 선택 |
| 프로필 소개(bio) | String | “Hello” | 선택 |
| 프로필 사진 | File | jpg/png/webp | 선택 |
| 게시글 이미지 | File[] | 최대 10장 | 필수(최소 1장) |
| 캡션 | String | “오늘의 기록” | 선택 |
| 해시태그 | String[] | #travel #coffee | 선택 |
| 댓글 | String | “멋져요!” | 선택 |
| 좋아요 | Action | like/unlike | 필수(액션) |
| 팔로우 | Action | follow/unfollow | 필수(액션) |

---

### 0.3 Output (결과 출력)

| 출력 항목 | 형태 | 설명 |
|----------|------|------|
| 홈 피드 | 무한 스크롤 | 팔로우 기반 최신 게시글 |
| 게시글 상세 | 상세 페이지 | 이미지 캐러셀, 캡션, 댓글 |
| 프로필 | 프로필 페이지 | 게시글 그리드, 팔로워/팔로잉 |
| 검색/탐색 | 리스트/그리드 | 유저/해시태그/게시글 탐색 |
| 알림 | 리스트 | 좋아요/댓글/팔로우 이벤트 |

---

### 0.4 Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │     │  Frontend   │     │   Backend   │
│ (Web/Mobile)│────▶│   (React)   │────▶│  (FastAPI)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                             ┌──────────────────┼──────────────────┐
                             ▼                  ▼                  ▼
                        ┌─────────┐        ┌──────────┐       ┌──────────┐
                        │   DB    │        │  Storage │       │   Cache  │
                        │Postgres │        │  (S3)    │       │ (Redis*) │
                        └─────────┘        └──────────┘       └──────────┘
                             ▲                  │                  ▲
                             └─────── Feed/Graph ┴── CDN URL ──────┘

*Redis는 MVP에서는 선택(로컬/SQLite로도 가능). 운영 권장.
```

---

### 0.5 Data Refresh (데이터 갱신 주기)

| 데이터 | 갱신 주기 | 방법 |
|------|----------|------|
| 홈 피드 | 사용자 스크롤 시 | Cursor Pagination |
| 좋아요/댓글 | 즉시 | Optimistic UI + 서버 반영 |
| 알림 | 10~30초 polling 또는 WebSocket | MVP: polling / 확장: WS |
| 썸네일/리사이즈 | 업로드 시 | 서버 동기 처리(MVP) / 확장: 큐 |

---

### 0.6 Data Access Checklist (개발 전 확인사항)

- [x] 스토리지 업로드 후 **공개 URL**로 서빙 가능한가?
- [x] 업로드 크기 제한(예: 10MB/장)과 타입 제한(jpg/png/webp)이 정의되었는가?
- [x] 권한 모델(내 피드=팔로우 기반, 비공개 계정 등)이 정의되었는가?
- [x] 피드/댓글/검색에 대한 페이지네이션 방식(cursor)이 정의되었는가?
- [x] 삭제(게시글/댓글) 시 연관 데이터(좋아요/알림) 처리 정책이 있는가?

---

## 1. Project Overview

### 1.1 Purpose
Instagram-Style MVP는 사용자가 사진을 업로드하고, 팔로우 기반 피드를 보고, 좋아요/댓글/알림을 통해 상호작용하는 **소셜 사진 앱**입니다.

### 1.2 MVP Goals (기본 기능 “풀셋”)
> “MVP”이지만 **인스타그램의 기본 경험**을 구성하는 핵심 기능을 모두 구현합니다.

- 회원가입/로그인/로그아웃, 토큰 갱신(Access/Refresh)
- 프로필(사진/소개/게시글 그리드) + 프로필 편집
- 게시글 업로드(복수 이미지), 캡션, 해시태그
- 홈 피드(팔로우 기반), 게시글 상세
- 좋아요/댓글(작성/삭제), 좋아요 목록
- 팔로우/언팔로우, 팔로워/팔로잉 목록
- 검색(유저, 해시태그) + 탐색(인기/최신)
- 알림(좋아요/댓글/팔로우)

> **범위 제외(Non-goals)**: Reels/Stories/Live/쇼핑/광고/고급 추천 알고리즘(ML)/DM
> 단, 탐색 탭은 "인기 점수(좋아요/댓글/시간)" 기반의 단순 랭킹으로 구현.

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                        Frontend (React)                        │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │   Feed    │ │  Explore  │ │  Profile  │ │  Post Detail  │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────────┘  │
│  ┌───────────┐ ┌───────────────┐                               │
│  │  Upload   │ │ Notifications │                               │
│  └───────────┘ └───────────────┘                               │
└───────────────────────────────────────────────────────────────┘
                               ↕ HTTP/REST
┌───────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │   Auth    │ │   Feed    │ │   Social  │ │    Search     │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────────┘  │
│  ┌───────────┐ ┌───────────────┐                               │
│  │  Upload   │ │ Notifications │                               │
│  └───────────┘ └───────────────┘                               │
└───────────────────────────────────────────────────────────────┘
             ↕                         ↕
      ┌───────────────┐        ┌────────────────┐
      │ Postgres/SQLite│        │ S3-Compatible  │
      │   (DB)         │        │ Storage + CDN  │
      └───────────────┘        └────────────────┘
```

### 2.2 Component Breakdown

#### Frontend (React)
- **기술**: React + Vite, TypeScript(권장), TailwindCSS, React Router
- **상태/데이터**: TanStack Query(서버 상태) + Zustand(로컬 UI 상태)
- **주요 화면**
  - Home Feed / Explore / Profile / Post Detail
  - Upload Flow(미리보기+캡션)
  - Notifications

#### Backend (FastAPI)
- **기술**: FastAPI, Pydantic, SQLAlchemy 2.x, Alembic
- **인증**: JWT Access/Refresh + bcrypt 해싱
- **스토리지**: S3 SDK(boto3) 또는 추상화 레이어(StorageService)

#### Database
- **개발**: SQLite(가능)  
- **운영**: Postgres(권장)
- **주요 테이블**: users, posts, media, follows, likes, comments, hashtags, post_hashtags, notifications

---

## 3. Core Features & User Stories

### 3.1 Auth & Account
- 사용자는 이메일/비밀번호로 가입하고 로그인한다.
- 사용자는 username으로 프로필 URL을 가진다(`/:username`).

### 3.2 Profile
- 사용자는 프로필 사진, 표시 이름, bio를 설정한다.
- 프로필 페이지에서 게시글 그리드/팔로워/팔로잉을 본다.

### 3.3 Post (Feed)
- 사용자는 1~10장의 이미지를 업로드하고 캡션/해시태그를 입력한다.
- 사용자는 홈 피드에서 팔로우한 계정의 최신 게시글을 본다(커서 페이지네이션).
- 사용자는 게시글 상세에서 댓글을 보고 작성한다.

### 3.4 Social
- 사용자는 다른 사용자를 팔로우/언팔로우한다.
- 사용자는 게시글에 좋아요/좋아요 취소를 한다.
- 사용자는 댓글을 작성/삭제한다(본인 댓글만 삭제).

### 3.5 Search & Explore
- 사용자는 username/표시이름으로 유저를 검색한다.
- 사용자는 해시태그로 게시글을 탐색한다.
- Explore는 최근 N일 게시글을 점수 기반으로 정렬하여 그리드로 보여준다.

### 3.6 Notifications
- 좋아요/댓글/팔로우 이벤트 발생 시 알림이 생성된다.
- 사용자는 알림 목록을 조회하고 읽음 처리한다.

---

## 4. API Design

> **규칙**: 모든 엔드포인트는 trailing slash 없이 통일 (`/api/v1/...`)

### 4.1 Response Envelope
```json
{
  "status": "success",
  "data": { },
  "error": null,
  "metadata": {
    "timestamp": "2026-02-06T00:00:00Z",
    "version": "1.0.0",
    "request_id": "uuid"
  }
}
```

### 4.2 Auth Endpoints
```
POST /api/v1/auth/register
- Body: { email, password, username, display_name? }
- Response: { user, access_token, refresh_token }

POST /api/v1/auth/login
- Body: { email_or_username, password }
- Response: { user, access_token, refresh_token }

POST /api/v1/auth/refresh
- Body: { refresh_token }
- Response: { access_token }

POST /api/v1/auth/logout
- Body: { refresh_token } (서버에서 revoke 처리)
- Response: { message }
```

### 4.3 User/Profile Endpoints
```
GET  /api/v1/users/me
PATCH /api/v1/users/me
- Body: { display_name?, bio?, website?, is_private? }

POST /api/v1/users/me/avatar
- multipart/form-data: file
- Response: { avatar_url }

GET  /api/v1/users/{username}
- Response: { user, stats: { posts, followers, following }, is_following }

POST /api/v1/users/{username}/follow
DELETE /api/v1/users/{username}/follow
- 팔로우/언팔로우

GET /api/v1/users/{username}/followers?cursor=&limit=
GET /api/v1/users/{username}/following?cursor=&limit=
```

### 4.4 Upload & Media
```
POST /api/v1/uploads
- multipart/form-data: files[]
- 서버가 리사이즈/썸네일 생성 후 저장
- Response: { media: [{ id, url, width, height, thumb_url }] }
```

### 4.5 Posts
```
POST /api/v1/posts
- Body: { media_ids: string[], caption?: string, hashtags?: string[] }
- Response: { post }

GET  /api/v1/posts/{post_id}
- Response: { post, media[], author, like_count, comment_count, is_liked }

DELETE /api/v1/posts/{post_id}
- 본인 게시글만 삭제

GET  /api/v1/feed?cursor=&limit=
- 팔로우 기반 피드 (최신순)
- Response: { items: [post_summary...], next_cursor }

GET  /api/v1/users/{username}/posts?cursor=&limit=
- 프로필 그리드용

GET  /api/v1/explore?cursor=&limit=
- 인기/탐색 그리드 (단순 랭킹)
```

### 4.6 Likes
```
POST   /api/v1/posts/{post_id}/like
DELETE /api/v1/posts/{post_id}/like

GET /api/v1/posts/{post_id}/likes?cursor=&limit=
```

### 4.7 Comments
```
GET  /api/v1/posts/{post_id}/comments?cursor=&limit=
POST /api/v1/posts/{post_id}/comments
- Body: { content }
DELETE /api/v1/comments/{comment_id}
```

### 4.8 Search
```
GET /api/v1/search/users?q=&cursor=&limit=
GET /api/v1/search/hashtags?q=&cursor=&limit=
GET /api/v1/hashtags/{tag}/posts?cursor=&limit=
```

### 4.9 Notifications
```
GET  /api/v1/notifications?cursor=&limit=
POST /api/v1/notifications/read
- Body: { ids: [] } or { all: true }
```

### 4.10 System
```
GET /health
- Response: { "status": "healthy" }
```

---

## 5. Database Schema (SQLAlchemy ORM)

> **규칙**: Raw SQL 금지. SQLAlchemy 모델이 스키마의 원천이며 Alembic으로 마이그레이션한다.

### 5.1 Models (핵심 테이블)

```python
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

def utcnow():
    return datetime.utcnow()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # uuid str
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    display_name = Column(String)
    bio = Column(Text)
    avatar_url = Column(String)
    website = Column(String)
    is_private = Column(Boolean, default=False)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True)  # uuid str
    author_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    caption = Column(Text)

    created_at = Column(DateTime, default=utcnow, index=True)
    deleted_at = Column(DateTime)

    author = relationship("User")
    media = relationship("Media", back_populates="post", cascade="all,delete-orphan")

class Media(Base):
    __tablename__ = "media"
    id = Column(String, primary_key=True)  # uuid str
    post_id = Column(String, ForeignKey("posts.id"), index=True)
    url = Column(String, nullable=False)
    thumb_url = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    mime_type = Column(String)
    order = Column(Integer, default=0)  # 이미지 순서 (0-based)
    created_at = Column(DateTime, default=utcnow)

    post = relationship("Post", back_populates="media")

class Follow(Base):
    __tablename__ = "follows"
    follower_id = Column(String, ForeignKey("users.id"), primary_key=True)
    followee_id = Column(String, ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("ix_followee", "followee_id"),
    )

class Like(Base):
    __tablename__ = "likes"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("ix_like_post", "post_id"),
    )

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)  # uuid str
    post_id = Column(String, ForeignKey("posts.id"), index=True)
    author_id = Column(String, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)
    deleted_at = Column(DateTime)

class Hashtag(Base):
    __tablename__ = "hashtags"
    tag = Column(String, primary_key=True)   # lowercased
    created_at = Column(DateTime, default=utcnow)

class PostHashtag(Base):
    __tablename__ = "post_hashtags"
    post_id = Column(String, ForeignKey("posts.id"), primary_key=True)
    tag = Column(String, ForeignKey("hashtags.tag"), primary_key=True)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (Index("ix_tag", "tag"),)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True)  # uuid str
    user_id = Column(String, ForeignKey("users.id"), index=True)  # receiver
    actor_id = Column(String, ForeignKey("users.id"))
    type = Column(String, nullable=False)  # FOLLOW, LIKE, COMMENT
    post_id = Column(String, ForeignKey("posts.id"))
    comment_id = Column(String, ForeignKey("comments.id"))

    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=utcnow, index=True)
```

---

## 6. Business Rules (정책/규칙)

### 6.1 권한
- 게시글/댓글 삭제: 작성자만 가능
- 피드: “내가 팔로우하는 사람 + 내 게시글”
- 비공개 계정(is_private):
  - 팔로우 요청/승인 기능은 MVP에서는 선택(기본은 공개 계정)
  - MVP 범위를 단순화하려면 is_private는 저장만 하고 동작은 Phase 4로 미룸

### 6.2 삭제 시 연관 데이터 처리
- 게시글 삭제(soft delete) → 연관 좋아요/댓글/해시태그 연결/알림은 조회에서 제외(deleted_at IS NULL 필터)
- 댓글 삭제(soft delete) → 연관 알림은 조회에서 제외
- 계정 삭제는 MVP 범위 외

### 6.3 피드 페이지네이션
- Cursor 기반: `cursor = created_at + id` 조합(중복 방지)
- limit 기본 20, 최대 50

### 6.4 Explore 랭킹(단순)
- score = (like_count * 3) + (comment_count * 5) - time_decay
- time_decay = hours_since_created
- 최근 7일 게시글만 대상으로 함

### 6.5 해시태그 파싱
- 캡션에서 `#tag` 정규식 추출 + API 입력 hashtags 병합
- 소문자 정규화, 길이 제한(예: 2~30)

### 6.6 업로드 제한
- 1게시글 최대 10장
- 이미지 파일: jpg/png/webp, 최대 10MB/장
- 서버에서 1080px 리사이즈 + 썸네일 생성

---

## 7. Caching & Performance (선택)

- 좋아요/댓글 카운트는 **집계 테이블** 또는 **캐시 컬럼**으로 최적화 가능
  - MVP: 조회 시 COUNT(인덱스 필수)
  - 확장: posts.like_count, posts.comment_count denormalization + 트랜잭션 업데이트
- Redis가 있으면:
  - feed cursor 캐시
  - notification badge 캐시
  - rate limit 저장소로 활용

---

## 8. Frontend Routes & UX

### 8.1 Routes

| URL | 페이지 | 설명 |
|-----|--------|------|
| `/` | Feed | 홈 피드 |
| `/explore` | Explore | 탐색 탭 |
| `/search` | Search | 유저/해시태그 검색 |
| `/p/:postId` | Post Detail | 게시글 상세 |
| `/:username` | Profile | 프로필 |
| `/upload` | Upload | 업로드 |
| `/notifications` | Notifications | 알림 |
| `/login` | Login | 로그인 |
| `/register` | Register | 회원가입 |

### 8.2 UI/UX Guidelines
- Mobile-first, 하단 탭(Feed/Explore/Upload/Notifications/Profile)
- 피드 카드 구성: 상단(작성자) + 이미지 + 액션(Like/Comment/Share) + 캡션 + 댓글 일부
- Optimistic UI: 좋아요/팔로우/댓글은 즉시 반영 후 실패 시 롤백
- Skeleton loading + 빈 상태(empty state) 제공

---

## 9. Security Considerations

- 비밀번호: bcrypt 해싱, 최소 8자, rate limit 적용
- JWT:
  - Access token: 15분
  - Refresh token: 14~30일, 서버 저장 및 revoke 지원
- 업로드 보안:
  - MIME sniffing + 확장자 검사
  - 이미지 디코딩(Pillow)으로 유효성 확인
  - EXIF 제거(선택)
- CORS: 프론트 도메인만 허용(운영)
- Rate Limit: `slowapi` 사용 (로그인/검색/댓글/업로드에 적용)

---

## 10. Development Phases

### Phase 1: Foundation
- [ ] FastAPI + React(Vite) 프로젝트 스캐폴딩
- [ ] Auth(JWT) + User 모델 + 마이그레이션
- [ ] 기본 레이아웃/라우팅/탭바

### Phase 2: Posts (핵심)
- [ ] Upload API + 스토리지 연동(S3/로컬)
- [ ] Post CRUD + 프로필 그리드
- [ ] Feed(팔로우 기반) + Post Detail

### Phase 3: Social
- [ ] Follow/Unfollow
- [ ] Like/Unlike
- [ ] Comment CRUD
- [ ] Search(Users/Hashtags) + Hashtag Page

### Phase 4: Notifications + Polish
- [ ] Notification 생성/조회/읽음 처리
- [ ] Explore 랭킹 및 성능 개선

---

## 11. Project Structure

```
instagram-mvp/
├── frontend/
│   ├── src/
│   │   ├── api/                # fetch/axios clients
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── styles/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/                # routers
│   │   ├── core/               # config, security, logging
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # business logic
│   │   ├── repositories/       # db access layer
│   │   ├── storage/            # S3/local storage service
│   │   ├── database.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
│
├── design/
│   ├── reference/
│   └── README.md
├── scripts/
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── SPEC.md
└── README.md
```

---

## 12. Environment Variables

```bash
# .env.example

# Backend
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./app.db   # dev
# DATABASE_URL=postgresql+psycopg://...  # prod

JWT_SECRET_KEY=change-me
JWT_ACCESS_EXPIRES_MIN=15
JWT_REFRESH_EXPIRES_DAYS=30

# Storage (choose one)
STORAGE_DRIVER=local           # local | s3
LOCAL_STORAGE_PATH=./storage

S3_ENDPOINT_URL=               # for R2/MinIO optional
S3_REGION=auto
S3_BUCKET=instagram-mvp
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
CDN_BASE_URL=                  # public base url for media

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Instagram-Style MVP
```

---

## 13. Testing Strategy

### 13.1 Backend 테스트
- Auth: register/login/refresh, 토큰 만료/리프레시
- Upload: 파일 타입/크기 제한, 썸네일 생성 여부
- Feed: 팔로우 관계에 따른 피드 포함/제외
- Like: 중복 좋아요 방지(uq_like), 카운트 정확성
- Comment: 작성/삭제 권한
- Search: 유저/해시태그 검색 정확성
- Notifications: 이벤트 발생 시 생성, 읽음 처리

### 13.2 Frontend 테스트
- 로그인 폼 검증
- 피드 로딩/무한스크롤
- 좋아요 optimistic UI
- 댓글 작성/삭제
- 프로필 팔로우 버튼 상태 전환
- 업로드 흐름(파일 선택→미리보기→등록)

---

## 14. Success Metrics

- [ ] 피드 API p95 응답시간 < 500ms
- [ ] 업로드 성공률 > 99%
- [ ] 좋아요/댓글 액션 실패율 < 1%
- [ ] 모바일 기본 UX(탭/스크롤/터치) 문제 없음
- [ ] 권한/보안(타인 삭제/비인가 접근) 0건

---

**Document Version**: 1.0  
**Template Type**: Instagram-Style MVP  
**용도**: 초기 구현 청사진 (구현 후에는 코드가 Source of Truth)
