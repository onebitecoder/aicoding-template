# AI Coding Template - Installation Script (Windows PowerShell)
# 비개발자도 사용할 수 있도록 모든 의존성을 자동 설치합니다

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI Coding Template - Installation"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }

# ============================================
# 1. Node.js 확인
# ============================================
Write-Host "1. Node.js 확인 중..."

if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node -v
    Write-Success "Node.js $nodeVersion 이미 설치됨"
} else {
    Write-Error "Node.js가 설치되어 있지 않습니다."
    Write-Host ""
    Write-Host "Node.js 설치 방법:" -ForegroundColor Yellow
    Write-Host "  1. https://nodejs.org 에서 LTS 버전 다운로드"
    Write-Host "  2. 또는 winget: winget install OpenJS.NodeJS.LTS"
    Write-Host "  3. 또는 Chocolatey: choco install nodejs-lts"
    Write-Host ""
    exit 1
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm이 설치되어 있지 않습니다."
    exit 1
}

Write-Host ""

# ============================================
# 2. Python 확인
# ============================================
Write-Host "2. Python 확인 중..."

$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        $pythonCmd = "python"
        Write-Success "$pythonVersion 이미 설치됨"
    }
}

if (-not $pythonCmd -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
    $pythonVersion = python3 --version 2>&1
    $pythonCmd = "python3"
    Write-Success "$pythonVersion 이미 설치됨"
}

if (-not $pythonCmd) {
    Write-Error "Python 3가 설치되어 있지 않습니다."
    Write-Host ""
    Write-Host "Python 설치 방법:" -ForegroundColor Yellow
    Write-Host "  1. https://python.org 에서 다운로드"
    Write-Host "  2. 또는 winget: winget install Python.Python.3.11"
    Write-Host "  3. 또는 Chocolatey: choco install python"
    Write-Host ""
    Write-Host "설치 시 'Add Python to PATH' 옵션을 꼭 체크하세요!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================
# 3. Git 확인
# ============================================
Write-Host "3. Git 확인 중..."

if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitVersion = git --version
    Write-Success "$gitVersion 이미 설치됨"
} else {
    Write-Warning "Git이 설치되어 있지 않습니다."
    Write-Host ""
    Write-Host "Git 설치 방법:" -ForegroundColor Yellow
    Write-Host "  1. https://git-scm.com 에서 다운로드"
    Write-Host "  2. 또는 winget: winget install Git.Git"
    Write-Host ""
}

Write-Host ""

# ============================================
# 4. Python 가상환경 생성
# ============================================
Write-Host "4. Python 가상환경 생성 중..."

if (-not (Test-Path "venv")) {
    & $pythonCmd -m venv venv
    Write-Success "가상환경 생성 완료"
} else {
    Write-Warning "가상환경이 이미 존재합니다. 건너뜁니다."
}

# 가상환경 활성화
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Success "가상환경 활성화 완료"
} else {
    Write-Error "가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
}

Write-Host ""

# ============================================
# 5. Backend 의존성 설치
# ============================================
Write-Host "5. Backend 의존성 설치 중..."

if (Test-Path "backend\requirements.txt") {
    Push-Location backend
    pip install --upgrade pip
    pip install -r requirements.txt
    Pop-Location
    Write-Success "Backend 패키지 설치 완료"
} else {
    Write-Warning "backend/requirements.txt가 없습니다."
    Write-Info "프로젝트 생성 후 다시 install.ps1을 실행하세요."
}

Write-Host ""

# ============================================
# 6. Frontend 의존성 설치
# ============================================
Write-Host "6. Frontend 의존성 설치 중..."

if (Test-Path "frontend\package.json") {
    Push-Location frontend
    npm install
    Pop-Location
    Write-Success "Frontend 패키지 설치 완료"
} else {
    Write-Warning "frontend/package.json이 없습니다."
    Write-Info "프로젝트 생성 후 다시 install.ps1을 실행하세요."
}

Write-Host ""

# ============================================
# 7. 환경 변수 파일 생성
# ============================================
Write-Host "7. 환경 변수 파일 확인 중..."

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success ".env 파일 생성 완료"
        Write-Warning ".env 파일을 열어서 필요한 값을 설정하세요!"
    } else {
        Write-Warning ".env.example 파일이 없습니다."
    }
} else {
    Write-Success ".env 파일이 이미 존재합니다."
}

Write-Host ""

# ============================================
# 8. 설치 완료
# ============================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "설치가 완료되었습니다!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "설치된 도구:"
Write-Host "  - Node.js: $(node -v 2>$null)"
Write-Host "  - npm: $(npm -v 2>$null)"
Write-Host "  - Python: $($pythonCmd --version 2>$null)"
Write-Host "  - pip: $(pip --version 2>$null | Select-String -Pattern '\d+\.\d+' | ForEach-Object { $_.Matches.Value })"
Write-Host "  - Git: $(git --version 2>$null | Select-String -Pattern '\d+\.\d+\.\d+' | ForEach-Object { $_.Matches.Value })"
Write-Host ""
Write-Host "다음 단계:"
Write-Host "  1. 개발 서버 실행: .\dev.ps1"
Write-Host "  2. 테스트 실행: .\test.ps1"
Write-Host ""
Write-Host "문제가 있으면 Claude Code에게 물어보세요:"
Write-Host '  "에러 해결해줘: [에러 메시지]"'
Write-Host ""
