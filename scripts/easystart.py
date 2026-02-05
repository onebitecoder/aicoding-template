#!/usr/bin/env python3
"""
AI Coding Template - Easy Start (Cross-platform)
대화형 인터페이스로 프로젝트 생성부터 배포까지 안내합니다.
지원 OS: macOS, Linux, Windows
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# 색상 코드
if platform.system() == "Windows":
    os.system("color")

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def success(msg): print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")
def warning(msg): print(f"{Colors.YELLOW}[!]{Colors.RESET} {msg}")
def error(msg): print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")
def info(msg): print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def print_header():
    """헤더 출력"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print(f"{Colors.CYAN}")
    print("=" * 60)
    print()
    print("        AI Coding Template - Easy Start")
    print()
    print("   비개발자도 쉽게 웹 앱을 만들고 배포할 수 있습니다")
    print()
    print("=" * 60)
    print(f"{Colors.RESET}")
    print()

def print_step(num, total, title):
    """단계 헤더 출력"""
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("-" * 60)
    print(f"  Step {num}/{total}: {title}")
    print("-" * 60)
    print(f"{Colors.RESET}")
    print()

def ask_yes_no(question):
    """예/아니오 질문"""
    while True:
        response = input(f"{Colors.CYAN}{question} (y/n): {Colors.RESET}").lower().strip()
        if response in ['y', 'yes', '예', 'ㅇ']:
            return True
        elif response in ['n', 'no', '아니오', 'ㄴ']:
            return False
        print("y 또는 n을 입력하세요.")

def press_enter():
    """계속하려면 Enter"""
    print()
    input(f"{Colors.YELLOW}계속하려면 Enter를 누르세요...{Colors.RESET}")

def run_command(cmd, cwd=None):
    """명령어 실행"""
    return subprocess.run(cmd, shell=True, cwd=cwd)

def command_exists(cmd):
    """명령어 존재 확인"""
    return shutil.which(cmd) is not None

def get_python_cmd():
    """Python 명령어 반환"""
    if command_exists("python3"):
        return "python3"
    elif command_exists("python"):
        result = subprocess.run("python --version", shell=True, capture_output=True, text=True)
        if "Python 3" in result.stdout:
            return "python"
    return None

def main():
    # 프로젝트 루트로 이동
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    python_cmd = get_python_cmd()
    if not python_cmd:
        error("Python 3가 설치되어 있지 않습니다.")
        sys.exit(1)

    # ============================================
    # 시작
    # ============================================
    print_header()

    print(f"{Colors.BOLD}안녕하세요! AI Coding Template에 오신 것을 환영합니다.{Colors.RESET}")
    print()
    print("이 스크립트는 다음 과정을 단계별로 안내합니다:")
    print()
    print("  1. 환경 설치 (Node.js, Python 등)")
    print("  2. 프로젝트 설정 (SPEC.md)")
    print("  3. Claude Code로 프로젝트 구현")
    print("  4. 개발 서버 실행 및 확인")
    print("  5. 테스트 실행")
    print("  6. Git 저장")
    print("  7. Railway 배포")
    print()

    if not ask_yes_no("시작할까요?"):
        print("다음에 다시 만나요!")
        sys.exit(0)

    # ============================================
    # Step 1: 환경 설치
    # ============================================
    print_step(1, 7, "환경 설치")

    print("Node.js, Python, Git 등 필요한 도구를 설치합니다.")
    print("이미 설치된 도구는 건너뜁니다.")
    print()

    if ask_yes_no("환경 설치를 진행할까요?"):
        print()
        info("install.py 실행 중...")
        print()

        result = run_command(f"{python_cmd} scripts/install.py")

        if result.returncode == 0:
            success("환경 설치 완료!")
        else:
            error("환경 설치 중 오류가 발생했습니다.")
            print("문제를 해결한 후 다시 시도하세요.")
            sys.exit(1)
    else:
        warning("환경 설치를 건너뜁니다. (이미 설치되어 있다면 OK)")

    press_enter()

    # ============================================
    # Step 2: SPEC.md 설정
    # ============================================
    print_step(2, 7, "프로젝트 설정 (SPEC.md)")

    print("SPEC.md 파일에 만들고 싶은 프로젝트를 정의합니다.")
    print()
    print("현재 SPEC.md에는 예시 프로젝트(Stock Portfolio Tracker)가 있습니다.")
    print()

    print(f"{Colors.CYAN}어떻게 하시겠습니까?{Colors.RESET}")
    print("  1) 예시 프로젝트로 먼저 테스트하기")
    print("  2) SPEC.md를 직접 수정하기 (에디터 열기)")
    print("  3) 나중에 수정하기")
    print()

    spec_choice = input(f"{Colors.CYAN}선택 (1/2/3): {Colors.RESET}").strip()

    if spec_choice == "1":
        success("예시 프로젝트(Stock Portfolio Tracker)로 진행합니다.")
    elif spec_choice == "2":
        info("SPEC.md 파일을 엽니다...")

        if command_exists("code"):
            run_command("code SPEC.md")
        elif platform.system() == "Windows":
            run_command("notepad SPEC.md")
        elif platform.system() == "Darwin":
            run_command("open SPEC.md")
        else:
            run_command("xdg-open SPEC.md 2>/dev/null || nano SPEC.md")

        print()
        input(f"{Colors.YELLOW}SPEC.md 수정이 끝나면 Enter를 누르세요...{Colors.RESET}")
        success("SPEC.md 설정 완료!")
    else:
        warning("SPEC.md 수정을 나중에 진행합니다.")

    press_enter()

    # ============================================
    # Step 3: Claude Code로 프로젝트 구현
    # ============================================
    print_step(3, 7, "Claude Code로 프로젝트 구현")

    print("이제 Claude Code를 실행하여 프로젝트를 구현합니다.")
    print()
    print(f"{Colors.BOLD}Claude Code에게 이렇게 말하세요:{Colors.RESET}")
    print()
    print(f"  {Colors.GREEN}\"프로젝트 구현해줘\"{Colors.RESET}")
    print()
    print("또는:")
    print()
    print(f"  {Colors.GREEN}\"SPEC.md를 기반으로 프로젝트를 생성해줘\"{Colors.RESET}")
    print()

    if ask_yes_no("Claude Code를 실행할까요?"):
        if command_exists("claude"):
            info("Claude Code를 실행합니다...")
            info("프로젝트 구현이 완료되면 Claude Code를 종료하고 돌아오세요.")
            print()

            run_command("claude")

            success("Claude Code 세션 종료")
        else:
            warning("Claude Code가 설치되어 있지 않습니다.")
            print()
            print("설치 방법:")
            print("  npm install -g @anthropic-ai/claude-code")
            print()
            print("설치 후 터미널에서 'claude'를 실행하세요.")
    else:
        warning("Claude Code 실행을 건너뜁니다.")
        print("나중에 터미널에서 'claude'를 실행하세요.")

    press_enter()

    # ============================================
    # Step 4: 개발 서버 실행
    # ============================================
    print_step(4, 7, "개발 서버 실행")

    print("Frontend와 Backend 개발 서버를 실행합니다.")
    print()
    print("실행 후 브라우저에서 확인할 수 있습니다:")
    print("  - Frontend: http://localhost:3000")
    print("  - Backend API: http://localhost:8000")
    print("  - API 문서: http://localhost:8000/docs")
    print()

    if ask_yes_no("개발 서버를 실행할까요?"):
        info("개발 서버 실행 중... (종료: Ctrl+C)")
        print()

        run_command(f"{python_cmd} scripts/dev.py")

        success("개발 서버 종료")
    else:
        warning("개발 서버 실행을 건너뜁니다.")

    press_enter()

    # ============================================
    # Step 5: 테스트 실행
    # ============================================
    print_step(5, 7, "테스트 실행")

    print("린트 체크와 테스트를 실행하여 코드 품질을 확인합니다.")
    print()

    if ask_yes_no("테스트를 실행할까요?"):
        info("테스트 실행 중...")
        print()

        result = run_command(f"{python_cmd} scripts/test.py")

        if result.returncode == 0:
            success("모든 테스트 통과!")
        else:
            warning("일부 테스트가 실패했습니다.")
            print('Claude Code에게 "테스트 실패 해결해줘"라고 요청하세요.')
    else:
        warning("테스트 실행을 건너뜁니다.")

    press_enter()

    # ============================================
    # Step 6: Git 저장
    # ============================================
    print_step(6, 7, "Git 저장")

    print("변경사항을 Git에 저장합니다.")
    print()

    if Path(".git").exists():
        print("현재 Git 상태:")
        run_command("git status --short")
        print()

        if ask_yes_no("변경사항을 커밋할까요?"):
            print()
            commit_msg = input(f"{Colors.CYAN}커밋 메시지를 입력하세요 (기본: 'Update project'): {Colors.RESET}").strip()

            if not commit_msg:
                commit_msg = "Update project"

            run_command("git add .")
            run_command(f'git commit -m "{commit_msg}"')

            success(f"커밋 완료: {commit_msg}")

            print()
            if ask_yes_no("원격 저장소에 Push할까요?"):
                result = run_command("git push")

                if result.returncode == 0:
                    success("Push 완료!")
                else:
                    warning("Push 실패. 원격 저장소 설정을 확인하세요.")
    else:
        warning("Git 저장소가 초기화되어 있지 않습니다.")

        if ask_yes_no("Git 저장소를 초기화할까요?"):
            run_command("git init")
            run_command("git add .")
            run_command('git commit -m "Initial commit"')
            success("Git 저장소 초기화 완료!")

    press_enter()

    # ============================================
    # Step 7: Railway 배포
    # ============================================
    print_step(7, 7, "Railway 배포")

    print("프로젝트를 Railway에 배포하여 인터넷에 공개합니다.")
    print()

    if not command_exists("railway"):
        warning("Railway CLI가 설치되어 있지 않습니다.")
        print()

        if ask_yes_no("Railway CLI를 설치할까요?"):
            run_command("npm install -g @railway/cli")
            success("Railway CLI 설치 완료!")
        else:
            print("나중에 설치하려면: npm install -g @railway/cli")
            press_enter()

            # 완료 화면
            print_header()
            print(f"{Colors.GREEN}{Colors.BOLD}축하합니다! 프로젝트 설정이 완료되었습니다.{Colors.RESET}")
            print()
            print("Railway 배포는 나중에 다음 명령어로 진행하세요:")
            print("  railway login")
            print("  railway up")
            sys.exit(0)

    print()
    if ask_yes_no("Railway에 배포할까요?"):
        info("Railway 로그인 상태 확인 중...")

        result = subprocess.run("railway whoami", shell=True, capture_output=True)
        if result.returncode != 0:
            info("Railway 로그인이 필요합니다.")
            run_command("railway login")

        print()
        info("Railway 배포 중...")
        result = run_command("railway up")

        if result.returncode == 0:
            success("배포 완료!")
            print()
            info("배포된 URL을 확인하세요:")
            run_command("railway open")
        else:
            error("배포 중 오류가 발생했습니다.")
            print("railway logs 명령어로 로그를 확인하세요.")
    else:
        warning("Railway 배포를 건너뜁니다.")

    # ============================================
    # 완료
    # ============================================
    print()
    print(f"{Colors.CYAN}")
    print("=" * 60)
    print()
    print("          축하합니다! 모든 과정 완료!")
    print()
    print("=" * 60)
    print(f"{Colors.RESET}")
    print()
    print("다음에 할 수 있는 것들:")
    print()
    print('  - 기능 추가: Claude Code에게 "새 기능 추가해줘"라고 요청')
    print('  - 버그 수정: Claude Code에게 "버그 수정해줘"라고 요청')
    print("  - 재배포: railway up")
    print()
    print("도움이 필요하면 Claude Code에게 물어보세요!")
    print()

if __name__ == "__main__":
    main()
