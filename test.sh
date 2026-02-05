#!/bin/bash

# AI Coding Template - Test Runner
# 유닛 테스트, 통합 테스트, E2E 테스트를 실행합니다
# 지원 OS: macOS, Linux, Windows (WSL/Git Bash)

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# OS 감지
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "linux"
    fi
}

OS=$(detect_os)

# 가상환경 활성화 (OS별 분기)
activate_venv() {
    if [ -d "venv" ]; then
        if [[ "$OS" == "windows" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
    else
        error "가상환경이 없습니다."
        echo ""
        echo "해결 방법:"
        if [[ "$OS" == "windows" ]]; then
            echo "  PowerShell: .\\install.ps1"
            echo "  Git Bash: ./install.sh"
        else
            echo "  ./install.sh"
        fi
        exit 1
    fi
}

activate_venv

# .env 파일 로드
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 함수: 백엔드 유닛 테스트
run_backend_unit_tests() {
    info "백엔드 유닛 테스트 실행 중..."

    # tests/backend 또는 backend/tests/unit 둘 다 지원
    TEST_PATH=""
    if [ -d "tests/backend" ]; then
        TEST_PATH="tests/backend"
    elif [ -d "backend/tests/unit" ]; then
        TEST_PATH="backend/tests/unit"
    fi

    if [ -z "$TEST_PATH" ]; then
        warning "백엔드 테스트 디렉토리가 없습니다."
        echo "   예상 경로: tests/backend/ 또는 backend/tests/unit/"
        echo "   테스트 파일을 추가하면 자동으로 실행됩니다."
        return 0
    fi

    cd backend

    if [ "$COVERAGE" = "true" ]; then
        pytest "../$TEST_PATH" -v --cov=app --cov-report=html --cov-report=term
    else
        pytest "../$TEST_PATH" -v
    fi

    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "백엔드 유닛 테스트 통과"
    else
        error "백엔드 유닛 테스트 실패"
        return 1
    fi
}

# 함수: 백엔드 통합 테스트
run_backend_integration_tests() {
    info "백엔드 통합 테스트 실행 중..."

    if [ ! -d "backend/tests/integration" ]; then
        warning "backend/tests/integration/ 디렉토리가 없습니다."
        echo "   통합 테스트가 필요하면 디렉토리를 생성하세요."
        return 0
    fi

    cd backend
    pytest tests/integration/ -v
    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "백엔드 통합 테스트 통과"
    else
        error "백엔드 통합 테스트 실패"
        return 1
    fi
}

# 함수: 프론트엔드 테스트
run_frontend_tests() {
    info "프론트엔드 테스트 실행 중..."

    if [ ! -d "frontend" ]; then
        warning "frontend/ 디렉토리가 없습니다."
        echo "   프로젝트 생성 후 다시 실행하세요."
        return 0
    fi

    if [ ! -f "frontend/package.json" ]; then
        warning "frontend/package.json이 없습니다."
        return 0
    fi

    # package.json에 test 스크립트가 있는지 확인
    if ! grep -q '"test"' frontend/package.json; then
        warning "프론트엔드 테스트 스크립트가 설정되지 않았습니다."
        echo "   package.json에 test 스크립트를 추가하세요."
        return 0
    fi

    cd frontend

    if [ "$COVERAGE" = "true" ]; then
        npm run test:coverage 2>/dev/null || npm run test -- --coverage
    else
        npm run test 2>/dev/null || true
    fi

    local EXIT_CODE=$?
    cd ..

    if [ $EXIT_CODE -eq 0 ]; then
        success "프론트엔드 테스트 통과"
    else
        error "프론트엔드 테스트 실패"
        return 1
    fi
}

# 함수: E2E 테스트
run_e2e_tests() {
    info "E2E 테스트 실행 중..."

    if [ ! -d "frontend/e2e" ]; then
        warning "E2E 테스트가 설정되지 않았습니다."
        echo "   frontend/e2e/ 디렉토리를 생성하고 Playwright 테스트를 추가하세요."
        return 0
    fi

    # 백엔드 서버 시작
    info "테스트용 백엔드 서버 시작 중..."
    cd backend
    uvicorn app.main:app --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    cd ..

    # 서버 시작 대기
    sleep 3

    # Playwright E2E 테스트 실행
    cd frontend
    npm run test:e2e
    local EXIT_CODE=$?
    cd ..

    # 테스트용 서버 종료
    kill $BACKEND_PID 2>/dev/null || true

    if [ $EXIT_CODE -eq 0 ]; then
        success "E2E 테스트 통과"
    else
        error "E2E 테스트 실패"
        return 1
    fi
}

# 함수: Lint 검사
run_lint() {
    info "코드 린트 검사 중..."

    local LINT_FAILED=false

    # Backend: Ruff/Flake8
    if [ -d "backend" ]; then
        cd backend
        if command -v ruff &> /dev/null; then
            info "Backend 린트 (ruff)..."
            ruff check . || LINT_FAILED=true
        elif command -v flake8 &> /dev/null; then
            info "Backend 린트 (flake8)..."
            flake8 app tests || LINT_FAILED=true
        else
            warning "Backend 린터(ruff/flake8)가 설치되어 있지 않습니다."
            echo "   설치: pip install ruff"
        fi
        cd ..
    fi

    # Frontend: ESLint
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        if grep -q '"lint"' frontend/package.json; then
            cd frontend
            info "Frontend 린트 (eslint)..."
            npm run lint || LINT_FAILED=true
            cd ..
        else
            warning "Frontend 린트 스크립트가 설정되지 않았습니다."
        fi
    fi

    if [ "$LINT_FAILED" = true ]; then
        error "린트 검사 실패"
        return 1
    else
        success "린트 검사 완료"
        return 0
    fi
}

# 메인 로직
echo "=========================================="
echo "AI Coding Template - Test Runner"
echo "=========================================="
echo ""

# 옵션 파싱
MODE=${1:-"all"}
COVERAGE=false

for arg in "$@"; do
    if [ "$arg" = "--coverage" ]; then
        COVERAGE=true
    fi
done

FAILED=false

case $MODE in
    "unit")
        run_backend_unit_tests || FAILED=true
        ;;
    "integration")
        run_backend_integration_tests || FAILED=true
        ;;
    "frontend")
        run_frontend_tests || FAILED=true
        ;;
    "e2e")
        run_e2e_tests || FAILED=true
        ;;
    "lint")
        run_lint || FAILED=true
        ;;
    "all"|*)
        run_lint || FAILED=true
        echo ""
        run_backend_unit_tests || FAILED=true
        echo ""
        run_backend_integration_tests || FAILED=true
        echo ""
        run_frontend_tests || FAILED=true
        ;;
esac

echo ""
echo "=========================================="

if [ "$FAILED" = false ]; then
    success "모든 테스트가 통과했습니다!"

    if [ "$COVERAGE" = "true" ]; then
        echo ""
        info "커버리지 리포트: backend/htmlcov/index.html"
    fi

    exit 0
else
    error "일부 테스트가 실패했습니다."
    echo ""
    echo "문제 해결 방법:"
    echo "  1. Claude Code에게 \"테스트 실패 해결해줘\"라고 요청"
    echo "  2. 에러 메시지를 확인하고 해당 파일 수정"
    exit 1
fi
