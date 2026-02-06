#!/usr/bin/env python3
"""
AI Coding Template - Installation Script (Cross-platform)
비개발자도 사용할 수 있도록 모든 의존성을 자동 설치합니다.
지원 OS: macOS, Linux, Windows

설치 흐름:
1. OS 감지
2. Node.js 확인/자동 설치
3. Python 확인/자동 설치
4. Git 확인/자동 설치 + git config 확인
5. MCP CLI 도구 설치 (uvx, markitdown-mcp)
6. Python 가상환경 생성
7. Backend 의존성 설치
8. Frontend 의존성 설치
9. 환경 변수 파일 생성
10. 최종 상태 테이블 출력
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
    BOLD = "\033[1m"
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

# ============================================
# 자동 설치 관련 함수
# ============================================

def ensure_homebrew():
    """macOS에서 Homebrew 설치 확인/설치"""
    if command_exists("brew"):
        return True
    info("Homebrew가 설치되어 있지 않습니다. 설치를 시도합니다...")
    result = run_command(
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        check=False
    )
    if result.returncode == 0:
        success("Homebrew 설치 완료")
        return True
    else:
        error("Homebrew 설치 실패")
        print("  수동 설치: https://brew.sh")
        return False

def install_tool(tool_name, os_type):
    """도구 미설치 시 OS별 자동 설치 시도. 성공 여부 반환."""
    install_cmds = {
        "node": {
            "macos": ("brew install node", ensure_homebrew),
            "linux": (
                'curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs',
                None,
            ),
            "windows": ("winget install OpenJS.NodeJS.LTS", None),
        },
        "python3": {
            "macos": ("brew install python@3.11", ensure_homebrew),
            "linux": ("sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv", None),
            "windows": ("winget install Python.Python.3.11", None),
        },
        "git": {
            "macos": ("brew install git", ensure_homebrew),
            "linux": ("sudo apt-get update && sudo apt-get install -y git", None),
            "windows": ("winget install Git.Git", None),
        },
    }

    fallback_urls = {
        "node": "https://nodejs.org",
        "python3": "https://python.org",
        "git": "https://git-scm.com",
    }

    if tool_name not in install_cmds:
        error(f"알 수 없는 도구: {tool_name}")
        return False

    entry = install_cmds[tool_name].get(os_type)
    if not entry:
        error(f"{os_type}에서 {tool_name} 자동 설치를 지원하지 않습니다.")
        return False

    cmd, prerequisite_fn = entry

    # 사전 조건 확인 (예: macOS에서 Homebrew)
    if prerequisite_fn:
        if not prerequisite_fn():
            error(f"{tool_name} 설치를 위한 사전 조건(Homebrew)을 충족하지 못했습니다.")
            print(f"  수동 설치: {fallback_urls.get(tool_name, '')}")
            return False

    info(f"{tool_name} 자동 설치를 시도합니다...")
    print(f"  실행: {cmd}")
    result = run_command(cmd, check=False)

    if result.returncode == 0:
        success(f"{tool_name} 설치 완료")
        return True
    else:
        error(f"{tool_name} 자동 설치 실패")
        url = fallback_urls.get(tool_name, "")
        if url:
            print(f"  수동 설치: {url}")
        return False

def install_mcp_tools(pip_cmd):
    """MCP CLI 도구 설치 (uvx, markitdown-mcp)"""
    results = {}

    # npx는 Node.js에 포함 - 확인만
    if command_exists("npx"):
        result = run_command("npx --version", capture_output=True, check=False)
        ver = result.stdout.strip() if result.returncode == 0 else "?"
        success(f"npx {ver} (Node.js에 포함)")
        results["npx"] = ("OK", ver)
    else:
        warning("npx를 찾을 수 없습니다. Node.js가 올바르게 설치되었는지 확인하세요.")
        results["npx"] = ("FAIL", "-")

    # uvx (pip install uv)
    if command_exists("uvx"):
        result = run_command("uvx --version", capture_output=True, check=False)
        ver = result.stdout.strip() if result.returncode == 0 else "?"
        success(f"uvx 이미 설치됨 ({ver})")
        results["uvx"] = ("OK", ver)
    else:
        info("uvx 설치 중 (pip install uv)...")
        result = run_command(f"{pip_cmd} install uv", check=False)
        if result.returncode == 0:
            # 설치 후 버전 확인
            ver_result = run_command("uvx --version", capture_output=True, check=False)
            ver = ver_result.stdout.strip() if ver_result.returncode == 0 else "설치됨"
            success(f"uvx 설치 완료 ({ver})")
            results["uvx"] = ("OK", ver)
        else:
            warning("uvx 설치 실패 (pip install uv). serena MCP 서버를 사용할 수 없습니다.")
            results["uvx"] = ("FAIL", "-")

    # markitdown-mcp
    if command_exists("markitdown-mcp"):
        success("markitdown-mcp 이미 설치됨")
        results["markitdown-mcp"] = ("OK", "-")
    else:
        info("markitdown-mcp 설치 중...")
        result = run_command(f"{pip_cmd} install markitdown-mcp", check=False)
        if result.returncode == 0:
            success("markitdown-mcp 설치 완료")
            results["markitdown-mcp"] = ("OK", "-")
        else:
            warning("markitdown-mcp 설치 실패. markitdown MCP 서버를 사용할 수 없습니다.")
            results["markitdown-mcp"] = ("FAIL", "-")

    return results

def check_git_config():
    """git config user.name/email 확인 및 경고"""
    if not command_exists("git"):
        return

    name_result = run_command("git config user.name", capture_output=True, check=False)
    email_result = run_command("git config user.email", capture_output=True, check=False)

    name = name_result.stdout.strip() if name_result.returncode == 0 else ""
    email = email_result.stdout.strip() if email_result.returncode == 0 else ""

    if name:
        success(f"git user.name: {name}")
    else:
        warning("git user.name이 설정되지 않았습니다.")
        print("  설정 방법: git config --global user.name \"Your Name\"")

    if email:
        success(f"git user.email: {email}")
    else:
        warning("git user.email이 설정되지 않았습니다.")
        print("  설정 방법: git config --global user.email \"your@email.com\"")

def print_status_table(results):
    """최종 상태 테이블 출력

    results: dict[str, tuple[str, str]]
        키: 항목 이름, 값: (상태, 버전) 튜플
    """
    # 컬럼 너비 계산
    name_width = max(len(name) for name in results.keys())
    name_width = max(name_width, 6)  # 최소 "항목" 헤더 너비

    status_width = 8  # "상태" 컬럼
    ver_width = 12  # "버전" 컬럼

    header = f"| {'항목'.ljust(name_width)} | {'상태'.ljust(status_width)} | {'버전'.ljust(ver_width)} |"
    separator = f"|{'-' * (name_width + 2)}|{'-' * (status_width + 2)}|{'-' * (ver_width + 2)}|"

    print()
    print(f"{Colors.BOLD}설치 상태 요약{Colors.RESET}")
    print(separator)
    print(header)
    print(separator)

    for name, (status, version) in results.items():
        if status == "OK":
            status_colored = f"{Colors.GREEN}{status.ljust(status_width)}{Colors.RESET}"
        elif status == "SKIP":
            status_colored = f"{Colors.YELLOW}{status.ljust(status_width)}{Colors.RESET}"
        else:
            status_colored = f"{Colors.RED}{status.ljust(status_width)}{Colors.RESET}"
        print(f"| {name.ljust(name_width)} | {status_colored} | {version.ljust(ver_width)} |")

    print(separator)

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

    # 최종 상태 수집
    status_results = {}

    # ============================================
    # 1. Node.js 확인 / 자동 설치
    # ============================================
    print("1. Node.js 확인 중...")

    if command_exists("node"):
        result = run_command("node -v", capture_output=True)
        node_ver = result.stdout.strip()
        success(f"Node.js {node_ver} 이미 설치됨")
        status_results["Node.js"] = ("OK", node_ver)
    else:
        warning("Node.js가 설치되어 있지 않습니다.")
        if install_tool("node", os_type):
            result = run_command("node -v", capture_output=True, check=False)
            node_ver = result.stdout.strip() if result.returncode == 0 else "설치됨"
            status_results["Node.js"] = ("OK", node_ver)
        else:
            error("Node.js 설치에 실패했습니다. 수동으로 설치 후 다시 실행하세요.")
            status_results["Node.js"] = ("FAIL", "-")
            sys.exit(1)

    if command_exists("npm"):
        result = run_command("npm -v", capture_output=True, check=False)
        npm_ver = result.stdout.strip() if result.returncode == 0 else "?"
        status_results["npm"] = ("OK", npm_ver)
    else:
        error("npm이 설치되어 있지 않습니다. Node.js를 재설치하세요.")
        status_results["npm"] = ("FAIL", "-")
        sys.exit(1)

    print()

    # ============================================
    # 2. Python 확인 / 자동 설치
    # ============================================
    print("2. Python 확인 중...")

    python_cmd = get_python_cmd()
    if python_cmd:
        result = run_command(f"{python_cmd} --version", capture_output=True)
        py_ver = result.stdout.strip()
        success(f"{py_ver} 이미 설치됨")
        status_results["Python"] = ("OK", py_ver.replace("Python ", ""))
    else:
        warning("Python 3가 설치되어 있지 않습니다.")
        if install_tool("python3", os_type):
            python_cmd = get_python_cmd()
            if python_cmd:
                result = run_command(f"{python_cmd} --version", capture_output=True, check=False)
                py_ver = result.stdout.strip() if result.returncode == 0 else "설치됨"
                status_results["Python"] = ("OK", py_ver.replace("Python ", ""))
            else:
                error("Python 설치 후에도 명령어를 찾을 수 없습니다. PATH를 확인하세요.")
                status_results["Python"] = ("FAIL", "-")
                sys.exit(1)
        else:
            error("Python 설치에 실패했습니다. 수동으로 설치 후 다시 실행하세요.")
            status_results["Python"] = ("FAIL", "-")
            sys.exit(1)

    print()

    # ============================================
    # 3. Git 확인 / 자동 설치 + git config 확인
    # ============================================
    print("3. Git 확인 중...")

    if command_exists("git"):
        result = run_command("git --version", capture_output=True)
        git_ver = result.stdout.strip().replace("git version ", "")
        success(f"Git {git_ver} 이미 설치됨")
        status_results["Git"] = ("OK", git_ver)
    else:
        warning("Git이 설치되어 있지 않습니다.")
        if install_tool("git", os_type):
            result = run_command("git --version", capture_output=True, check=False)
            git_ver = result.stdout.strip().replace("git version ", "") if result.returncode == 0 else "설치됨"
            status_results["Git"] = ("OK", git_ver)
        else:
            warning("Git 설치에 실패했습니다. 버전 관리 기능이 제한됩니다.")
            status_results["Git"] = ("FAIL", "-")

    # git config 확인
    check_git_config()

    print()

    # ============================================
    # 4. MCP CLI 도구 설치
    # ============================================
    print("4. MCP CLI 도구 확인/설치 중...")

    pip_cmd = get_pip_cmd() or f"{python_cmd} -m pip"
    mcp_results = install_mcp_tools(pip_cmd)

    status_results["npx (MCP)"] = mcp_results.get("npx", ("SKIP", "-"))
    status_results["uvx (MCP)"] = mcp_results.get("uvx", ("SKIP", "-"))
    status_results["markitdown (MCP)"] = mcp_results.get("markitdown-mcp", ("SKIP", "-"))

    print()

    # ============================================
    # 5. Python 가상환경 생성
    # ============================================
    print("5. Python 가상환경 생성 중...")

    venv_path = Path("venv")
    if not venv_path.exists():
        result = run_command(f"{python_cmd} -m venv venv", check=False)
        if result.returncode == 0:
            success("가상환경 생성 완료")
            status_results["venv"] = ("OK", "-")
        else:
            error("가상환경 생성 실패")
            if os_type == "linux":
                info("python3-venv 패키지가 필요할 수 있습니다:")
                print("  sudo apt-get install -y python3-venv")
            status_results["venv"] = ("FAIL", "-")
    else:
        warning("가상환경이 이미 존재합니다. 건너뜁니다.")
        status_results["venv"] = ("OK", "기존")

    print()

    # ============================================
    # 6. Backend 의존성 설치
    # ============================================
    print("6. Backend 의존성 설치 중...")

    venv_pip = get_venv_pip()
    requirements_path = Path("backend/requirements.txt")

    if requirements_path.exists():
        # pip 업그레이드
        run_command(f"{venv_pip} install --upgrade pip", check=False)
        # 패키지 설치
        result = run_command(f"{venv_pip} install -r {requirements_path}", check=False)
        if result.returncode == 0:
            success("Backend 패키지 설치 완료")
            status_results["Backend 의존성"] = ("OK", "-")
        else:
            error("Backend 패키지 설치 실패")
            status_results["Backend 의존성"] = ("FAIL", "-")
    else:
        warning("backend/requirements.txt가 없습니다.")
        info("프로젝트 생성 후 다시 install.py를 실행하세요.")
        status_results["Backend 의존성"] = ("SKIP", "-")

    print()

    # ============================================
    # 7. Frontend 의존성 설치
    # ============================================
    print("7. Frontend 의존성 설치 중...")

    package_json = Path("frontend/package.json")
    if package_json.exists():
        os.chdir("frontend")
        result = run_command("npm install", check=False)
        os.chdir(project_root)
        if result.returncode == 0:
            success("Frontend 패키지 설치 완료")
            status_results["Frontend 의존성"] = ("OK", "-")
        else:
            error("Frontend 패키지 설치 실패")
            status_results["Frontend 의존성"] = ("FAIL", "-")
    else:
        warning("frontend/package.json이 없습니다.")
        info("프로젝트 생성 후 다시 install.py를 실행하세요.")
        status_results["Frontend 의존성"] = ("SKIP", "-")

    print()

    # ============================================
    # 8. 환경 변수 파일 생성
    # ============================================
    print("8. 환경 변수 파일 확인 중...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            success(".env 파일 생성 완료")
            warning(".env 파일을 열어서 필요한 값을 설정하세요!")
            status_results[".env"] = ("OK", "생성됨")
        else:
            warning(".env.example 파일이 없습니다.")
            status_results[".env"] = ("SKIP", "-")
    else:
        success(".env 파일이 이미 존재합니다.")
        status_results[".env"] = ("OK", "기존")

    print()

    # ============================================
    # 9. 최종 상태 테이블 출력
    # ============================================
    print("=" * 50)
    print_status_table(status_results)
    print()

    # 실패 항목 확인
    failed = [name for name, (status, _) in status_results.items() if status == "FAIL"]
    if failed:
        warning(f"다음 항목이 실패했습니다: {', '.join(failed)}")
        print("  문제를 해결한 후 다시 실행하세요: python scripts/install.py")
    else:
        print(f"{Colors.GREEN}설치가 완료되었습니다!{Colors.RESET}")

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
