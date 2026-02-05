#!/usr/bin/env python3
"""
AI Coding Template - Development Server (Cross-platform)
백엔드와 프론트엔드 개발 서버를 실행합니다.
지원 OS: macOS, Linux, Windows
"""

import os
import sys
import subprocess
import platform
import signal
import time
import threading
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

def kill_port(port):
    """포트를 사용하는 프로세스 종료"""
    os_type = get_os()
    try:
        if os_type == "windows":
            # Windows: netstat + taskkill
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True,
                                      capture_output=True)
                info(f"포트 {port} 프로세스 종료됨")
        else:
            # macOS/Linux: lsof + kill
            result = subprocess.run(
                f'lsof -ti :{port}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(f'kill -9 {pid}', shell=True)
                info(f"포트 {port} 프로세스 종료됨")
    except Exception as e:
        pass  # 포트가 사용 중이 아닐 수 있음

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

def clear_logs():
    """로그 파일 초기화"""
    log_files = [
        Path("backend/debug.log"),
        Path("frontend/debug.log")
    ]
    for log_file in log_files:
        if log_file.exists():
            log_file.unlink()
    info("로그 파일 초기화 완료")

class ServerProcess:
    def __init__(self, name, cmd, cwd, port):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.port = port
        self.process = None
        self.thread = None

    def start(self):
        """서버 시작"""
        kill_port(self.port)
        time.sleep(0.5)

        info(f"{self.name} 서버 시작 중...")

        self.process = subprocess.Popen(
            self.cmd,
            shell=True,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # 로그 출력 스레드
        self.thread = threading.Thread(target=self._read_output, daemon=True)
        self.thread.start()

        success(f"{self.name} 서버 시작됨 (Port: {self.port})")

    def _read_output(self):
        """서버 출력 읽기"""
        try:
            for line in self.process.stdout:
                print(f"{Colors.CYAN}[{self.name}]{Colors.RESET} {line}", end='')
        except:
            pass

    def stop(self):
        """서버 종료"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            success(f"{self.name} 서버 종료")
        kill_port(self.port)

def main():
    print("=" * 50)
    print("AI Coding Template - Development Server")
    print("=" * 50)
    print()

    # 프로젝트 루트로 이동
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # 인자 파싱
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    # 가상환경 확인
    venv_path = Path("venv")
    if not venv_path.exists():
        error("가상환경이 없습니다. 먼저 python scripts/install.py를 실행하세요.")
        sys.exit(1)

    # 환경 변수 로드
    load_env()

    # 로그 파일 초기화
    clear_logs()

    venv_python = get_venv_python()
    servers = []

    try:
        # Backend 서버
        if mode in ["all", "backend"]:
            if not Path("backend").exists():
                error("backend/ 디렉토리가 없습니다.")
                sys.exit(1)

            backend = ServerProcess(
                name="Backend",
                cmd=f"{venv_python} -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
                cwd=project_root / "backend",
                port=8000
            )
            backend.start()
            servers.append(backend)
            print(f"   API 문서: http://localhost:8000/docs")

            if mode == "all":
                time.sleep(2)  # Backend 시작 대기

        # Frontend 서버
        if mode in ["all", "frontend"]:
            if not Path("frontend").exists():
                error("frontend/ 디렉토리가 없습니다.")
                sys.exit(1)

            frontend = ServerProcess(
                name="Frontend",
                cmd="npm run dev",
                cwd=project_root / "frontend",
                port=3000
            )
            frontend.start()
            servers.append(frontend)
            print(f"   브라우저: http://localhost:3000")

        print()
        print("=" * 50)
        print("개발 서버가 실행 중입니다.")
        print("종료하려면 Ctrl+C를 누르세요.")
        print("=" * 50)
        print()

        # 메인 스레드 대기
        while True:
            time.sleep(1)
            # 프로세스가 종료되었는지 확인
            for server in servers:
                if server.process and server.process.poll() is not None:
                    error(f"{server.name} 서버가 예기치 않게 종료되었습니다.")

    except KeyboardInterrupt:
        print()
        info("서버를 종료합니다...")
    finally:
        for server in servers:
            server.stop()

if __name__ == "__main__":
    main()
