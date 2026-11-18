#!/usr/bin/env python3
"""
MindBridge - Cross-Platform One-Click Setup & Server Launcher
Works on Windows, macOS, and Linux.

Usage:
    python run.py
"""

import os
import sys
import subprocess
import webbrowser
import time
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")

def print_banner():
    banner = r"""
========================================================================
   __  __ _           _ ____       _     _            
  |  \/  (_)_ __   __| | __ ) _ __(_) __| | __ _  ___ 
  | |\/| | | '_ \ / _` |  _ \| '__| |/ _` |/ _` |/ _ \
  | |  | | | | | | (_| | |_) | |  | | (_| | (_| |  __/
  |_|  |_|_|_| |_|\__,_|____/|_|  |_|\__,_|\__, |\___|
                                           |___/      
  Mental Health Support Chatbot That Understands Your Context
  Nasarawa State University, Keffi (NSUK) Case Study
========================================================================
"""
    print(banner)

def get_python_executable():
    """Returns the python executable for the current environment or virtualenv."""
    if os.name == "nt":
        venv_py = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        venv_py = os.path.join(VENV_DIR, "bin", "python")
    
    if os.path.exists(venv_py):
        return venv_py
    return sys.executable

def get_pip_executable():
    """Returns the pip executable for the virtualenv or system."""
    if os.name == "nt":
        venv_pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        venv_pip = os.path.join(VENV_DIR, "bin", "pip")
    
    if os.path.exists(venv_pip):
        return venv_pip
    return f"{sys.executable} -m pip"

def check_python_version():
    print(f"[*] Detecting Python runtime: {sys.version.split()[0]} ({sys.executable})")
    if sys.version_info < (3, 10):
        print("[!] Warning: Python 3.10+ is recommended for MindBridge.")

def setup_virtualenv():
    """Sets up a virtual environment if one does not exist."""
    # Check if already running inside a virtualenv
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        print("[*] Running inside active virtual environment.")
        return sys.executable

    venv_python = get_python_executable()
    if not os.path.exists(venv_python):
        print("[*] Virtual environment not found. Creating 'venv'...")
        try:
            import venv
            venv.create(VENV_DIR, with_pip=True)
            print("[+] Virtual environment created successfully.")
        except Exception as e:
            print(f"[!] Could not create venv automatically: {e}")
            print("[*] Continuing with system Python environment...")
            return sys.executable
    else:
        print("[*] Found existing virtual environment at 'venv/'.")

    return get_python_executable()

def install_dependencies(py_exec):
    req_file = os.path.join(BASE_DIR, "requirements.txt")
    if not os.path.exists(req_file):
        print("[!] requirements.txt not found. Skipping dependency installation.")
        return

    print("[*] Checking and installing dependencies from requirements.txt...")
    cmd = [py_exec, "-m", "pip", "install", "-r", req_file]
    try:
        subprocess.check_call(cmd, cwd=BASE_DIR)
        print("[+] Dependencies verified and up to date.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error installing dependencies: {e}")
        print("[*] Attempting to continue anyway...")

def setup_env_file():
    env_file = os.path.join(BASE_DIR, ".env")
    example_file = os.path.join(BASE_DIR, ".env.example")
    if not os.path.exists(env_file):
        if os.path.exists(example_file):
            print("[*] Creating .env file from .env.example...")
            shutil.copyfile(example_file, env_file)
            print("[+] .env file initialized.")
        else:
            print("[*] Generating default .env file...")
            default_env = """# MindBridge Environment Variables
SECRET_KEY=mindbridge-secure-django-secret-key-change-in-production-2026-ng
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,[::1],testserver
DATABASE_URL=sqlite:///mindbridge.sqlite3

AI_PROVIDER=gemini
AI_MODEL=gemini-3.6-flash
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
AI_API_KEY=your-gemini-api-key
GEMINI_API_KEY=your-gemini-api-key

TIME_ZONE=Africa/Lagos
LANGUAGE_CODE=en-us
"""
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(default_env)
            print("[+] Default .env file generated.")
    else:
        print("[*] Found existing .env configuration.")

def run_migrations(py_exec):
    print("[*] Applying database migrations...")
    manage_py = os.path.join(BASE_DIR, "manage.py")
    try:
        subprocess.check_call([py_exec, manage_py, "migrate", "--noinput"], cwd=BASE_DIR)
        print("[+] Database schema is up to date.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Migration error: {e}")

def create_default_superuser_if_needed(py_exec):
    manage_py = os.path.join(BASE_DIR, "manage.py")
    script = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.accounts.models import CustomUser

if not CustomUser.objects.filter(is_superuser=True).exists():
    u = CustomUser.objects.create_superuser(
        email='admin@mindbridge.africa',
        password='AdminPassword2026!',
        full_name='MindBridge Administrator',
        user_type='ADMINISTRATOR'
    )
    print('[+] Created default admin user: admin@mindbridge.africa / AdminPassword2026!')
else:
    print('[*] Admin user already exists.')
"""
    try:
        subprocess.run([py_exec, "-c", script], cwd=BASE_DIR, check=False)
    except Exception:
        pass

def start_server(py_exec, port="8000"):
    manage_py = os.path.join(BASE_DIR, "manage.py")
    url = f"http://127.0.0.1:{port}/"

    print("\n" + "=" * 60)
    print(f"[*] MindBridge is launching on {url}")
    print("[*] Case Study: Nasarawa State University, Keffi (NSUK)")
    print("[*] Gemini AI Integration: Enabled & Direct")
    print("[*] Press Ctrl+C at any time in this window to stop the server.")
    print("=" * 60 + "\n")

    # Open browser automatically after a short delay
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    import threading
    t = threading.Thread(target=open_browser, daemon=True)
    t.start()

    # Launch Django runserver
    try:
        subprocess.check_call([py_exec, manage_py, "runserver", f"127.0.0.1:{port}"], cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\n[*] MindBridge server stopped. Have a wonderful day!")

def main():
    print_banner()
    check_python_version()
    setup_env_file()
    py_exec = setup_virtualenv()
    install_dependencies(py_exec)
    run_migrations(py_exec)
    create_default_superuser_if_needed(py_exec)
    
    port = "8000"
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = sys.argv[1]
    
    start_server(py_exec, port=port)

if __name__ == "__main__":
    main()
