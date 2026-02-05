# 빠른 시작 가이드

비개발자도 5분 안에 프로젝트를 시작할 수 있는 가이드입니다.

---

## 1. 사전 준비

### 1.1 필수 도구 설치

#### macOS

```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Node.js 설치
brew install node

# Python 설치
brew install python@3.11

# Git 설치 (보통 기본 설치됨)
brew install git
```

#### Windows

**방법 1: 공식 사이트에서 다운로드 (권장)**
1. Node.js: https://nodejs.org (LTS 버전 다운로드)
2. Python: https://python.org (설치 시 "Add Python to PATH" 체크 필수!)
3. Git: https://git-scm.com

**방법 2: winget 사용 (Windows 11)**
```powershell
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.11
winget install Git.Git
```

**방법 3: Chocolatey 사용**
```powershell
choco install nodejs-lts python git
```

### 1.2 Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code
```

### 1.3 Git 초기 설정 (필수)

Git을 처음 사용한다면 아래 설정을 해주세요:

```bash
# 사용자 이름 설정 (GitHub 계정 이름 권장)
git config --global user.name "홍길동"

# 이메일 설정 (GitHub 계정 이메일 권장)
git config --global user.email "your-email@example.com"

# 기본 브랜치 이름 설정
git config --global init.defaultBranch main

# 설정 확인
git config --list
```

---

## 2. 환경별 실행 방법

### macOS / Linux

```bash
# 의존성 설치
./install.sh

# 개발 서버 실행
./dev.sh

# 테스트 실행
./test.sh
```

### Windows (PowerShell)

```powershell
# 의존성 설치
.\install.ps1

# 개발 서버 실행
.\dev.ps1

# 테스트 실행
.\test.ps1
```

### Windows (Git Bash / WSL)

Git Bash나 WSL을 사용하면 macOS와 동일한 명령어 사용 가능:

```bash
./install.sh
./dev.sh
./test.sh
```

---

## 3. 프로젝트 시작하기

### Step 1: Claude Code 실행

프로젝트 폴더에서 터미널을 열고:

```bash
claude
```

### Step 2: 프로젝트 생성 요청

Claude Code에게 말하기:
```
"SPEC.md를 기반으로 프로젝트를 생성해줘"
```

Claude Code가 자동으로:
- frontend/ 폴더 생성 (React 앱)
- backend/ 폴더 생성 (FastAPI 앱)
- 필요한 설정 파일들 생성

### Step 3: 의존성 설치

```
"의존성 설치해줘"
```

### Step 4: 개발 서버 실행

```
"개발 서버 실행해줘"
```

브라우저에서 확인:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 4. 나만의 프로젝트 만들기

### SPEC.md 수정하기

`SPEC.md` 파일을 열어서 다음을 변경하세요:

1. **프로젝트 이름**: "Stock Portfolio Tracker" → 원하는 이름
2. **프로젝트 설명**: 1.1 Purpose 섹션
3. **데이터베이스 테이블**: 6. Database Schema 섹션
4. **API 엔드포인트**: 5. API Design 섹션

### 예시: 할 일 관리 앱으로 변경

SPEC.md에서 Database Schema 섹션을 다음과 같이 변경:

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

그리고 Claude Code에게:
```
"SPEC.md를 기반으로 프로젝트를 새로 생성해줘"
```

---

## 5. Railway 배포

### 사전 준비 (최초 1회)

1. Railway 계정 생성: https://railway.app

2. Railway CLI 설치:
```bash
npm install -g @railway/cli
```

3. Railway 로그인:
```bash
railway login
```

### 배포하기

Claude Code에게:
```
"Railway에 배포해줘"
```

Claude Code가 자동으로:
1. 테스트 실행
2. Git 커밋
3. Docker 이미지 빌드
4. Railway에 배포
5. 배포 URL 제공

---

## 6. 자주 사용하는 명령어

| 작업 | Claude Code에게 말하기 |
|------|----------------------|
| 프로젝트 생성 | "SPEC.md를 기반으로 프로젝트를 생성해줘" |
| 의존성 설치 | "의존성 설치해줘" |
| 개발 서버 실행 | "개발 서버 실행해줘" |
| 테스트 실행 | "테스트 실행해줘" |
| Railway 배포 | "Railway에 배포해줘" |
| 배포 로그 확인 | "배포 로그 확인해줘" |
| 에러 해결 | "에러 원인 분석해줘" |

---

## 7. 스크립트 명령어 정리

### macOS / Linux

| 스크립트 | 설명 | 옵션 |
|---------|------|------|
| `./install.sh` | 의존성 설치 | - |
| `./dev.sh` | 개발 서버 실행 | `backend`, `frontend`, `all` |
| `./test.sh` | 테스트 실행 | `lint`, `unit`, `frontend`, `all`, `--coverage` |
| `./easystart.sh` | 대화형 가이드 | - |

### Windows (PowerShell)

| 스크립트 | 설명 | 옵션 |
|---------|------|------|
| `.\install.ps1` | 의존성 설치 | - |
| `.\dev.ps1` | 개발 서버 실행 | `backend`, `frontend`, `all` |
| `.\test.ps1` | 테스트 실행 | `lint`, `unit`, `frontend`, `all`, `--coverage` |

---

## 8. 문제 해결

### "command not found" 에러

Node.js나 Python이 설치되지 않았습니다:
```bash
# 설치 확인
node --version
python3 --version  # 또는 python --version (Windows)
```

### "실행 권한 없음" 에러 (macOS/Linux)

```bash
chmod +x install.sh dev.sh test.sh easystart.sh
```

### "스크립트 실행 정책" 에러 (Windows PowerShell)

```powershell
# 관리자 권한으로 PowerShell 실행 후:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Railway 배포 실패

```
"배포 로그 확인해줘"
```

로그를 보고 Claude Code에게:
```
"이 에러 해결해줘: [에러 메시지]"
```

### 개발 서버가 실행되지 않음

```
"에러 로그 확인해줘"
```

### 포트가 이미 사용 중

```bash
# macOS/Linux
lsof -ti :8000 | xargs kill -9
lsof -ti :3000 | xargs kill -9

# Windows PowerShell
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 3000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

---

## 9. VS Code 추천 설정

이 템플릿에는 `.vscode/` 폴더에 VS Code 설정이 포함되어 있습니다.

### 추천 확장 설치

VS Code에서 프로젝트를 열면 추천 확장 설치 알림이 표시됩니다.
또는 수동 설치:

```
Ctrl+Shift+P (Windows) / Cmd+Shift+P (Mac)
→ "Extensions: Show Recommended Extensions"
→ 모두 설치
```

---

## 도움이 필요하면?

Claude Code에게 물어보세요:
```
"[문제 상황] 어떻게 해결해?"
```

예시:
- "API 엔드포인트 추가하는 방법 알려줘"
- "데이터베이스 테이블 추가하고 싶어"
- "로그인 기능 추가해줘"
