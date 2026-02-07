# AI Coding Template

> **Claude Code와 함께 사용하는 풀스택 웹 애플리케이션 템플릿**

이 템플릿은 비개발자도 Claude Code를 통해 웹 애플리케이션을 쉽게 구축할 수 있도록 설계되었습니다.

---

## Quick Start

### 1. 템플릿 다운로드

```bash
git clone https://github.com/your-repo/aicoding-template.git
cd aicoding-template
```

### 2. 환경 설치

```bash
bash scripts/install.sh
```

Node.js, Python, Git 등 필요한 도구를 자동으로 설치합니다. 이미 설치된 도구는 건너뜁니다.

### 3. Claude Code로 프로젝트 구현

```bash
claude
# "프로젝트 구현해줘"
```

Claude Code가 자동으로 SPEC.md를 읽고 프로젝트를 구현합니다.

### 4. 개발 서버 확인

```bash
bash scripts/dev.sh
```

- http://localhost:3000 (Frontend)
- http://localhost:8000/docs (API 문서)

### 5. 테스트 및 배포

```bash
bash scripts/test.sh    # 테스트
railway up              # 배포
```

---

## 스크립트 명령어

| 작업 | 명령어 |
|------|--------|
| 의존성 설치 | `bash scripts/install.sh` |
| 개발 서버 (전체) | `bash scripts/dev.sh` |
| 개발 서버 (Backend만) | `bash scripts/dev.sh backend` |
| 개발 서버 (Frontend만) | `bash scripts/dev.sh frontend` |
| 테스트 (전체) | `bash scripts/test.sh` |
| 린트만 | `bash scripts/test.sh lint` |
| Backend 테스트만 | `bash scripts/test.sh backend` |
| Frontend 테스트만 | `bash scripts/test.sh frontend` |
| 커버리지 포함 | `bash scripts/test.sh --coverage` |

---

## 프로젝트 구조

```
aicoding-template/
├── .claude/
│   ├── CLAUDE.md          # Claude Code 규칙 (핵심!)
│   └── settings.local.json
│
├── design/
│   └── reference.png      # 디자인 레퍼런스 이미지
│
├── scripts/
│   ├── install.sh         # 의존성 설치
│   ├── dev.sh             # 개발 서버 실행
│   └── test.sh            # 테스트/린트 실행
│
├── SPEC.md                # 프로젝트 명세서 (수정하여 사용)
├── AGENTS.md              # AI Agent 개발 규칙
├── Dockerfile             # Docker 빌드 설정
├── railway.toml           # Railway 배포 설정
└── .env.example           # 환경 변수 예시
```

### 구현 후 생성되는 구조

```
├── frontend/              # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── pages/         # 페이지
│   │   └── api/           # API 클라이언트
│   └── package.json
│
├── backend/               # Python + FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/           # API 라우터
│   │   ├── models/        # DB 모델
│   │   └── services/      # 비즈니스 로직
│   └── requirements.txt
```

---

## 나만의 프로젝트 만들기

### 1. SPEC.md 수정

`SPEC.md` 파일을 열어 원하는 프로젝트로 수정합니다.

### 2. 디자인 레퍼런스 추가 (선택)

`design/reference.png`에 원하는 디자인 이미지를 추가하면 Claude Code가 해당 스타일을 참고합니다.

### 3. Claude Code에게 요청

```
"SPEC.md를 기반으로 프로젝트를 생성해줘"
```

---

## 배포 (Railway)

### 사전 준비

1. [Railway](https://railway.app) 계정 생성
2. Railway CLI 설치: `npm install -g @railway/cli`
3. 로그인: `railway login`

### 배포

```bash
railway up
```

---

## 문제 해결

### 에러 발생 시

Claude Code에게 요청:

```
"에러 로그 확인해줘"
```

### 포트가 이미 사용 중

dev.sh가 자동으로 포트를 해제하지만, 수동으로 하려면:

```bash
# macOS/Linux
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9
```

### 로그 확인

```bash
tail -f backend/debug.log
```

---

## 참고 자료

- [SPEC.md](./SPEC.md) - 프로젝트 명세서
- [.claude/CLAUDE.md](./.claude/CLAUDE.md) - Claude Code 규칙
- [AGENTS.md](./AGENTS.md) - AI Agent 개발 규칙
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)

---

## 라이선스

MIT License - 자유롭게 사용하세요.
