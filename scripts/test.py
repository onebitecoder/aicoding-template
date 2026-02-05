#!/usr/bin/env python3
"""
AI Coding Template - Test Runner (Cross-platform)
유닛 테스트, 린트, 통합 테스트를 실행합니다.
지원 OS: macOS, Linux, Windows
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path

# 색상 코드
if platform.system() == "Windows":
    os.system("color")

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def success(msg): print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")
def warning(msg): print(f"{Colors.YELLOW}[!]{Colors.RESET} {msg}")
def error(msg): print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")
def info(msg): print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def get_os():
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    return "linux"

def get_venv_python():
    """가상환경 Python 경로 반환"""
    os_type = get_os()
    if os_type == "windows":
        return str(Path("venv/Scripts/python.exe"))
    return str(Path("venv/bin/python"))

def load_env():
    """환경 변수 로드"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def run_command(cmd, cwd=None):
    """명령어 실행"""
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode == 0

def run_lint():
    """린트 검사 실행"""
    info("코드 린트 검사 중...")

    all_passed = True
    venv_python = get_venv_python()

    # Backend 린트 (ruff 또는 flake8)
    if Path("backend").exists():
        info("Backend 린트 검사...")

        # ruff 사용 시도
        ruff_result = subprocess.run(
            f"{venv_python} -m ruff check .",
            shell=True, cwd="backend", capture_output=True
        )

        if ruff_result.returncode == 0:
            success("Backend 린트 통과 (ruff)")
        elif b"No module named ruff" in ruff_result.stderr:
            # flake8 시도
            flake8_result = subprocess.run(
                f"{venv_python} -m flake8 app",
                shell=True, cwd="backend", capture_output=True
            )
            if flake8_result.returncode == 0:
                success("Backend 린트 통과 (flake8)")
            elif b"No module named flake8" in flake8_result.stderr:
                warning("Backend 린터가 설치되지 않음 (pip install ruff)")
            else:
                error("Backend 린트 실패")
                print(flake8_result.stdout.decode() if flake8_result.stdout else "")
                all_passed = False
        else:
            error("Backend 린트 실패")
            print(ruff_result.stdout.decode() if ruff_result.stdout else "")
            all_passed = False

    # Frontend 린트 (ESLint)
    if Path("frontend/package.json").exists():
        info("Frontend 린트 검사...")

        # package.json에 lint 스크립트가 있는지 확인
        with open("frontend/package.json") as f:
            if '"lint"' in f.read():
                if run_command("npm run lint", cwd="frontend"):
                    success("Frontend 린트 통과")
                else:
                    error("Frontend 린트 실패")
                    all_passed = False
            else:
                warning("Frontend 린트 스크립트가 설정되지 않음")

    return all_passed

def run_backend_tests(coverage=False):
    """Backend 테스트 실행"""
    info("Backend 테스트 실행 중...")

    venv_python = get_venv_python()

    # 테스트 경로 찾기 (tests/backend 또는 backend/tests)
    test_path = None
    if Path("tests/backend").exists():
        test_path = "tests/backend"
    elif Path("backend/tests").exists():
        test_path = "backend/tests"

    if not test_path:
        warning("Backend 테스트 디렉토리가 없습니다.")
        print("   예상 경로: tests/backend/ 또는 backend/tests/")
        return True  # 테스트가 없으면 통과로 처리

    # pytest 실행
    if coverage:
        cmd = f"{venv_python} -m pytest {test_path} -v --cov=backend/app --cov-report=html --cov-report=term"
    else:
        cmd = f"{venv_python} -m pytest {test_path} -v"

    if run_command(cmd):
        success("Backend 테스트 통과")
        return True
    else:
        error("Backend 테스트 실패")
        return False

def run_frontend_tests(coverage=False):
    """Frontend 테스트 실행"""
    info("Frontend 테스트 실행 중...")

    if not Path("frontend/package.json").exists():
        warning("frontend/package.json이 없습니다.")
        return True

    # package.json에 test 스크립트가 있는지 확인
    with open("frontend/package.json") as f:
        content = f.read()
        if '"test"' not in content:
            warning("Frontend 테스트 스크립트가 설정되지 않음")
            return True

    if coverage:
        cmd = "npm run test:coverage"
    else:
        cmd = "npm run test"

    result = subprocess.run(cmd, shell=True, cwd="frontend")

    if result.returncode == 0:
        success("Frontend 테스트 통과")
        return True
    else:
        error("Frontend 테스트 실패")
        return False

def print_results(results):
    """결과 테이블 출력"""
    print()
    print("=" * 50)
    print("테스트 결과")
    print("=" * 50)
    print()
    print("| 구분 | 결과 |")
    print("|------|------|")

    for name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"| {name} | {status} |")

    print()

    all_passed = all(results.values())
    if all_passed:
        print(f"{Colors.GREEN}최종 결과: PASS{Colors.RESET}")
    else:
        print(f"{Colors.RED}최종 결과: FAIL{Colors.RESET}")

    return all_passed

def main():
    parser = argparse.ArgumentParser(description="AI Coding Template Test Runner")
    parser.add_argument("mode", nargs="?", default="all",
                       choices=["all", "lint", "backend", "frontend"],
                       help="테스트 모드 (default: all)")
    parser.add_argument("--coverage", action="store_true",
                       help="커버리지 리포트 생성")

    args = parser.parse_args()

    print("=" * 50)
    print("AI Coding Template - Test Runner")
    print("=" * 50)
    print()

    # 프로젝트 루트로 이동
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # 가상환경 확인
    if not Path("venv").exists():
        error("가상환경이 없습니다. 먼저 python scripts/install.py를 실행하세요.")
        sys.exit(1)

    # 환경 변수 로드
    load_env()

    results = {}

    if args.mode == "lint":
        results["Lint"] = run_lint()
    elif args.mode == "backend":
        results["Backend"] = run_backend_tests(args.coverage)
    elif args.mode == "frontend":
        results["Frontend"] = run_frontend_tests(args.coverage)
    else:  # all
        results["Lint"] = run_lint()
        print()
        results["Backend"] = run_backend_tests(args.coverage)
        print()
        results["Frontend"] = run_frontend_tests(args.coverage)

    all_passed = print_results(results)

    if args.coverage:
        print()
        info("커버리지 리포트: backend/htmlcov/index.html")

    if not all_passed:
        print()
        print("문제 해결 방법:")
        print('  1. Claude Code에게 "테스트 실패 해결해줘"라고 요청')
        print("  2. 에러 메시지를 확인하고 해당 파일 수정")
        sys.exit(1)

if __name__ == "__main__":
    main()
