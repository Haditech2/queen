@echo off
setlocal enabledelayedexpansion

title MindBridge - Mental Health Support Chatbot (NSUK Case Study)

echo ========================================================================
echo    __  __ _           _ ____       _     _            
echo   ^|  \/  (_)_ __   __^| ^| __ ) _ __(_) __^| ^| __ _  ___ 
echo   ^| ^|\/^| ^| ^| '_ \ / _` ^|  _ \^| '__^| ^|/ _` ^|/ _` ^|/ _ \
echo   ^| ^|  ^| ^| ^| ^| ^| ^| (_^| ^| ^|_) ^| ^|  ^| ^| (_^| ^| (_^| ^|  __/
echo   ^|_^|  ^|_^|_^|_^| ^|_^|\__,_^|____/^|_^|  ^|_^|\__,_^|\__, ^|\___^|
echo                                            ^|___/      
echo   Mental Health Support Chatbot That Understands Your Context
echo   Case Study: Nasarawa State University, Keffi (NSUK)
echo ========================================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    py --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Python is not installed or not in your system PATH.
        echo Please download and install Python from https://www.python.org/
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [*] Detected Python command: %PYTHON_CMD%
%PYTHON_CMD% --version

:: 2. Check or create .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [*] Initializing .env configuration from .env.example...
        copy ".env.example" ".env" >nul
        echo [+] Created .env file.
    ) else (
        echo [!] Warning: Neither .env nor .env.example found.
    )
) else (
    echo [*] Found existing .env configuration.
)

:: 3. Setup Virtual Environment (venv)
if not exist "venv\Scripts\python.exe" (
    echo [*] Virtual environment not found. Creating 'venv'...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Could not create venv. Using system Python...
        set VENV_PY=%PYTHON_CMD%
    ) else (
        echo [+] Virtual environment created successfully.
        set VENV_PY=venv\Scripts\python.exe
    )
) else (
    echo [*] Found existing virtual environment at venv\
    set VENV_PY=venv\Scripts\python.exe
)

:: 4. Install dependencies
echo [*] Installing/verifying dependencies from requirements.txt...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Some dependencies could not be installed. Continuing...
) else (
    echo [+] Dependencies are up to date.
)

:: 5. Run Database Migrations
echo [*] Applying database migrations...
"%VENV_PY%" manage.py migrate --noinput
if %ERRORLEVEL% neq 0 (
    echo [!] Database migration encountered an issue. Check settings.
) else (
    echo [+] Database is ready.
)

:: 6. Launch Browser and Server
echo.
echo ========================================================================
echo  MindBridge is starting on http://127.0.0.1:8000/
echo  Case Study: Nasarawa State University, Keffi (NSUK)
echo  Gemini AI Support: Active
echo  Press Ctrl+C to stop the server at any time.
echo ========================================================================
echo.

start "" "http://127.0.0.1:8000/"
"%VENV_PY%" manage.py runserver 127.0.0.1:8000

pause
