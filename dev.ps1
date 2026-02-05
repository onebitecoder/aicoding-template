# AI Coding Template - Development Server (Windows PowerShell)
# 백엔드와 프론트엔드 개발 서버를 실행합니다

$ErrorActionPreference = "SilentlyContinue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI Coding Template - Development Server"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }

# 포트 사용 중인 프로세스 종료
function Stop-ProcessOnPort {
    param($Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Info "포트 $Port 사용 중인 프로세스 발견: $($process.Name) (PID: $($process.Id))"
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                Write-Success "프로세스 종료됨"
            }
        }
        Start-Sleep -Seconds 1
    }
}

# 가상환경 확인
if (-not (Test-Path "venv")) {
    Write-Error "가상환경이 없습니다. 먼저 .\install.ps1을 실행하세요."
    exit 1
}

# 가상환경 활성화
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
}

# .env 파일 로드
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

# 로그 파일 초기화
if (Test-Path "backend\debug.log") { Remove-Item "backend\debug.log" }
if (Test-Path "frontend\debug.log") { Remove-Item "frontend\debug.log" }
Write-Info "로그 파일 초기화 완료"

$mode = if ($args[0]) { $args[0] } else { "all" }

$backendJob = $null
$frontendJob = $null

try {
    switch ($mode) {
        "backend" {
            Stop-ProcessOnPort 8000

            if (-not (Test-Path "backend")) {
                Write-Error "backend/ 디렉토리가 없습니다."
                exit 1
            }

            Write-Info "백엔드 서버 시작 중..."
            $backendJob = Start-Job -ScriptBlock {
                Set-Location $using:PWD
                & ".\venv\Scripts\Activate.ps1"
                Set-Location backend
                uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            }
            Write-Success "백엔드 서버 시작됨 (Port: 8000)"
            Write-Host "   API 문서: http://localhost:8000/docs"
        }
        "frontend" {
            Stop-ProcessOnPort 3000

            if (-not (Test-Path "frontend")) {
                Write-Error "frontend/ 디렉토리가 없습니다."
                exit 1
            }

            Write-Info "프론트엔드 서버 시작 중..."
            $frontendJob = Start-Job -ScriptBlock {
                Set-Location $using:PWD\frontend
                npm run dev
            }
            Write-Success "프론트엔드 서버 시작됨 (Port: 3000)"
            Write-Host "   브라우저: http://localhost:3000"
        }
        default {
            # Backend
            Stop-ProcessOnPort 8000

            if (-not (Test-Path "backend")) {
                Write-Error "backend/ 디렉토리가 없습니다."
                exit 1
            }

            Write-Info "백엔드 서버 시작 중..."
            $backendJob = Start-Job -ScriptBlock {
                Set-Location $using:PWD
                & ".\venv\Scripts\Activate.ps1"
                Set-Location backend
                uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            }
            Write-Success "백엔드 서버 시작됨 (Port: 8000)"
            Write-Host "   API 문서: http://localhost:8000/docs"

            Start-Sleep -Seconds 2

            # Frontend
            Stop-ProcessOnPort 3000

            if (-not (Test-Path "frontend")) {
                Write-Error "frontend/ 디렉토리가 없습니다."
                exit 1
            }

            Write-Info "프론트엔드 서버 시작 중..."
            $frontendJob = Start-Job -ScriptBlock {
                Set-Location $using:PWD\frontend
                npm run dev
            }
            Write-Success "프론트엔드 서버 시작됨 (Port: 3000)"
            Write-Host "   브라우저: http://localhost:3000"
        }
    }

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "개발 서버가 실행 중입니다."
    Write-Host "종료하려면 Ctrl+C를 누르세요."
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    # 서버 로그 출력
    while ($true) {
        if ($backendJob) {
            Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        }
        if ($frontendJob) {
            Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host ""
    Write-Info "서버를 종료합니다..."

    if ($backendJob) {
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
        Write-Success "백엔드 서버 종료"
    }
    if ($frontendJob) {
        Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
        Write-Success "프론트엔드 서버 종료"
    }

    # 포트 정리
    Stop-ProcessOnPort 8000
    Stop-ProcessOnPort 3000
}
