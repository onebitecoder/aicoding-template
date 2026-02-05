# AI Coding Template - Test Runner (Windows PowerShell)
# 유닛 테스트, 통합 테스트, 린트를 실행합니다

$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI Coding Template - Test Runner"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }

# 가상환경 확인 및 활성화
if (-not (Test-Path "venv")) {
    Write-Error "가상환경이 없습니다. 먼저 .\install.ps1을 실행하세요."
    exit 1
}

& ".\venv\Scripts\Activate.ps1"

# .env 파일 로드
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

# 파라미터 파싱
$mode = "all"
$coverage = $false

foreach ($arg in $args) {
    switch ($arg) {
        "--coverage" { $coverage = $true }
        "unit" { $mode = "unit" }
        "integration" { $mode = "integration" }
        "frontend" { $mode = "frontend" }
        "lint" { $mode = "lint" }
        "all" { $mode = "all" }
    }
}

$failed = $false

# 린트 검사
function Run-Lint {
    Write-Info "코드 린트 검사 중..."

    $lintFailed = $false

    # Backend: Ruff
    if (Test-Path "backend") {
        Push-Location backend
        if (Get-Command ruff -ErrorAction SilentlyContinue) {
            ruff check .
            if ($LASTEXITCODE -ne 0) { $lintFailed = $true }
        } elseif (Get-Command flake8 -ErrorAction SilentlyContinue) {
            flake8 app tests
            if ($LASTEXITCODE -ne 0) { $lintFailed = $true }
        } else {
            Write-Warning "Backend 린터(ruff/flake8)가 설치되어 있지 않습니다."
        }
        Pop-Location
    }

    # Frontend: ESLint
    if (Test-Path "frontend") {
        Push-Location frontend
        npm run lint 2>$null
        if ($LASTEXITCODE -ne 0) { $lintFailed = $true }
        Pop-Location
    }

    if ($lintFailed) {
        Write-Error "린트 검사 실패"
        return $false
    } else {
        Write-Success "린트 검사 통과"
        return $true
    }
}

# Backend 유닛 테스트
function Run-BackendUnitTests {
    Write-Info "백엔드 유닛 테스트 실행 중..."

    # tests/backend 또는 backend/tests/unit 둘 다 지원
    $testPath = $null
    if (Test-Path "tests\backend") {
        $testPath = "tests\backend"
    } elseif (Test-Path "backend\tests\unit") {
        $testPath = "backend\tests\unit"
    }

    if (-not $testPath) {
        Write-Warning "백엔드 테스트 디렉토리가 없습니다."
        return $true
    }

    Push-Location backend
    if ($coverage) {
        pytest ..\$testPath -v --cov=app --cov-report=html --cov-report=term
    } else {
        pytest ..\$testPath -v
    }
    $exitCode = $LASTEXITCODE
    Pop-Location

    if ($exitCode -eq 0) {
        Write-Success "백엔드 유닛 테스트 통과"
        return $true
    } else {
        Write-Error "백엔드 유닛 테스트 실패"
        return $false
    }
}

# Backend 통합 테스트
function Run-BackendIntegrationTests {
    Write-Info "백엔드 통합 테스트 실행 중..."

    if (-not (Test-Path "backend\tests\integration")) {
        Write-Warning "backend/tests/integration/ 디렉토리가 없습니다."
        return $true
    }

    Push-Location backend
    pytest tests\integration\ -v
    $exitCode = $LASTEXITCODE
    Pop-Location

    if ($exitCode -eq 0) {
        Write-Success "백엔드 통합 테스트 통과"
        return $true
    } else {
        Write-Error "백엔드 통합 테스트 실패"
        return $false
    }
}

# Frontend 테스트
function Run-FrontendTests {
    Write-Info "프론트엔드 테스트 실행 중..."

    if (-not (Test-Path "frontend")) {
        Write-Warning "frontend/ 디렉토리가 없습니다."
        return $true
    }

    Push-Location frontend
    if ($coverage) {
        npm run test:coverage 2>$null
    } else {
        npm run test 2>$null
    }
    $exitCode = $LASTEXITCODE
    Pop-Location

    if ($exitCode -eq 0) {
        Write-Success "프론트엔드 테스트 통과"
        return $true
    } else {
        Write-Error "프론트엔드 테스트 실패"
        return $false
    }
}

# 테스트 실행
switch ($mode) {
    "lint" {
        if (-not (Run-Lint)) { $failed = $true }
    }
    "unit" {
        if (-not (Run-BackendUnitTests)) { $failed = $true }
    }
    "integration" {
        if (-not (Run-BackendIntegrationTests)) { $failed = $true }
    }
    "frontend" {
        if (-not (Run-FrontendTests)) { $failed = $true }
    }
    default {
        if (-not (Run-Lint)) { $failed = $true }
        Write-Host ""
        if (-not (Run-BackendUnitTests)) { $failed = $true }
        Write-Host ""
        if (-not (Run-BackendIntegrationTests)) { $failed = $true }
        Write-Host ""
        if (-not (Run-FrontendTests)) { $failed = $true }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

if ($failed) {
    Write-Error "일부 테스트가 실패했습니다."
    exit 1
} else {
    Write-Success "모든 테스트가 통과했습니다!"

    if ($coverage) {
        Write-Host ""
        Write-Info "커버리지 리포트: backend\htmlcov\index.html"
    }

    exit 0
}
