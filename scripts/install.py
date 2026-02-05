#!/usr/bin/env python3
"""
AI Coding Template - Installation Script (Cross-platform)
비개발자도 사용할 수 있도록 모든 의존성을 자동 설치합니다.
지원 OS: macOS, Linux, Windows
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# 색상 코드 (Windows 지원)
if platform.system() == "Windows":
    os.system("color")  # Windows 콘솔 색상 활성화

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
    """현재 운영체제 반환"""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    else:
        return "linux"

def run_command(cmd, check=True, capture_output=False):
    """명령어 실행"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e

def command_exists(cmd):
    """명령어가 존재하는지 확인"""
    return shutil.which(cmd) is not None

def get_python_cmd():
    """Python 실행 명령어 반환"""
    if command_exists("python3"):
        return "python3"
    elif command_exists("python"):
        # Python 버전 확인
        result = run_command("python --version", capture_output=True)
        if result.returncode == 0 and "Python 3" in result.stdout:
            return "python"
    return None

def get_pip_cmd():
    """pip 실행 명령어 반환"""
    if command_exists("pip3"):
        return "pip3"
    elif command_exists("pip"):
        return "pip"
    return None

def get_venv_activate_cmd():
    """가상환경 활성화 명령어 반환"""
    os_type = get_os()
    if os_type == "windows":
        return str(Path("venv/Scripts/activate"))
    else:
        return "source venv/bin/activate"

def get_venv_python():
    """가상환경 Python 경로 반환"""
    os_type = get_os()
    if os_type == "windows":
        return str(Path("venv/Scripts/python.exe"))
    else:
        return str(Path("venv/bin/python"))

def get_venv_pip():
    """가상환경 pip 경로 반환"""
    os_type = get_os()
    if os_type == "windows":
        return str(Path("venv/Scripts/pip.exe"))
    else:
        return str(Path("venv/bin/pip"))

def main():
    print("=" * 50)
    print("AI Coding Template - Installation")
    print("=" * 50)
    print()

    os_type = get_os()
    info(f"감지된 OS: {os_type} ({platform.system()} {platform.release()})")
    print()

    # 프로젝트 루트 디렉토리로 이동
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    info(f"프로젝트 디렉토리: {project_root}")
    print()

    # ============================================
    # 1. Node.js 확인
    # ============================================
    print("1. Node.js 확인 중...")

    if command_exists("node"):
        result = run_command("node -v", capture_output=True)
        success(f"Node.js {result.stdout.strip()} 이미 설치됨")
    else:
        error("Node.js가 설치되어 있지 않습니다.")
        print()
        print("Node.js 설치 방법:")
        if os_type == "macos":
            print("  brew install node")
        elif os_type == "windows":
            print("  1. https://nodejs.org 에서 LTS 버전 다운로드")
            print("  2. 또는: winget install OpenJS.NodeJS.LTS")
        else:
            print("  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
            print("  sudo apt-get install -y nodejs")
        sys.exit(1)

    if not command_exists("npm"):
        error("npm이 설치되어 있지 않습니다.")
        sys.exit(1)

    print()

    # ============================================
    # 2. Python 확인
    # ============================================
    print("2. Python 확인 중...")

    python_cmd = get_python_cmd()
    if python_cmd:
        result = run_command(f"{python_cmd} --version", capture_output=True)
        success(f"{result.stdout.strip()} 이미 설치됨")
    else:
        error("Python 3가 설치되어 있지 않습니다.")
        print()
        print("Python 설치 방법:")
        if os_type == "macos":
            print("  brew install python@3.11")
        elif os_type == "windows":
            print("  1. https://python.org 에서 다운로드")
            print("  2. 설치 시 'Add Python to PATH' 체크 필수!")
            print("  3. 또는: winget install Python.Python.3.11")
        else:
            print("  sudo apt-get install -y python3 python3-pip python3-venv")
        sys.exit(1)

    print()

    # ============================================
    # 3. Git 확인
    # ============================================
    print("3. Git 확인 중...")

    if command_exists("git"):
        result = run_command("git --version", capture_output=True)
        success(f"{result.stdout.strip()} 이미 설치됨")
    else:
        warning("Git이 설치되어 있지 않습니다.")
        print("Git 설치 방법:")
        if os_type == "macos":
            print("  brew install git")
        elif os_type == "windows":
            print("  https://git-scm.com 에서 다운로드")
        else:
            print("  sudo apt-get install -y git")

    print()

    # ============================================
    # 4. Python 가상환경 생성
    # ============================================
    print("4. Python 가상환경 생성 중...")

    venv_path = Path("venv")
    if not venv_path.exists():
        run_command(f"{python_cmd} -m venv venv")
        success("가상환경 생성 완료")
    else:
        warning("가상환경이 이미 존재합니다. 건너뜁니다.")

    print()

    # ============================================
    # 5. Backend 의존성 설치
    # ============================================
    print("5. Backend 의존성 설치 중...")

    venv_pip = get_venv_pip()
    requirements_path = Path("backend/requirements.txt")

    if requirements_path.exists():
        # pip 업그레이드
        run_command(f"{venv_pip} install --upgrade pip", check=False)
        # 패키지 설치
        result = run_command(f"{venv_pip} install -r {requirements_path}")
        if result.returncode == 0:
            success("Backend 패키지 설치 완료")
        else:
            error("Backend 패키지 설치 실패")
    else:
        warning("backend/requirements.txt가 없습니다.")
        info("프로젝트 생성 후 다시 install.py를 실행하세요.")

    print()

    # ============================================
    # 6. Frontend 의존성 설치
    # ============================================
    print("6. Frontend 의존성 설치 중...")

    package_json = Path("frontend/package.json")
    if package_json.exists():
        os.chdir("frontend")
        result = run_command("npm install")
        os.chdir(project_root)
        if result.returncode == 0:
            success("Frontend 패키지 설치 완료")
        else:
            error("Frontend 패키지 설치 실패")
    else:
        warning("frontend/package.json이 없습니다.")
        info("프로젝트 생성 후 다시 install.py를 실행하세요.")

    print()

    # ============================================
    # 7. 환경 변수 파일 생성
    # ============================================
    print("7. 환경 변수 파일 확인 중...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            success(".env 파일 생성 완료")
            warning(".env 파일을 열어서 필요한 값을 설정하세요!")
        else:
            warning(".env.example 파일이 없습니다.")
    else:
        success(".env 파일이 이미 존재합니다.")

    print()

    # ============================================
    # 8. 설치 완료
    # ============================================
    print("=" * 50)
    print(f"{Colors.GREEN}설치가 완료되었습니다!{Colors.RESET}")
    print("=" * 50)
    print()
    print("설치된 도구:")

    # Node.js 버전
    result = run_command("node -v", capture_output=True, check=False)
    node_ver = result.stdout.strip() if result.returncode == 0 else "미설치"
    print(f"  - Node.js: {node_ver}")

    # npm 버전
    result = run_command("npm -v", capture_output=True, check=False)
    npm_ver = result.stdout.strip() if result.returncode == 0 else "미설치"
    print(f"  - npm: {npm_ver}")

    # Python 버전
    result = run_command(f"{python_cmd} --version", capture_output=True, check=False)
    py_ver = result.stdout.strip() if result.returncode == 0 else "미설치"
    print(f"  - Python: {py_ver}")

    # Git 버전
    result = run_command("git --version", capture_output=True, check=False)
    git_ver = result.stdout.strip().replace("git version ", "") if result.returncode == 0 else "미설치"
    print(f"  - Git: {git_ver}")

    print()
    print("다음 단계:")
    print("  1. 개발 서버 실행: python scripts/dev.py")
    print("  2. 테스트 실행: python scripts/test.py")
    print()
    print("문제가 있으면 Claude Code에게 물어보세요:")
    print('  "에러 해결해줘: [에러 메시지]"')
    print()

if __name__ == "__main__":
    main()
