#!/usr/bin/env bash
# MindBridge - One-Click Launcher for macOS & Linux (NSUK Case Study)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "   __  __ _           _ ____       _     _            "
echo "  |  \/  (_)_ __   __| | __ ) _ __(_) __| | __ _  ___ "
echo "  | |\/| | | '_ \ / _` |  _ \| '__| |/ _` |/ _` |/ _ \ "
echo "  | |  | | | | | | (_| | |_) | |  | | (_| | (_| |  __/ "
echo "  |_|  |_|_|_| |_|\__,_|____/|_|  |_|\__,_|\__, |\___| "
echo "                                           |___/      "
echo "  Mental Health Support Chatbot That Understands Your Context"
echo "  Case Study: Nasarawa State University, Keffi (NSUK)"
echo "========================================================================"
echo ""

# 1. Detect Python 3
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH."
    echo "Please install Python 3.10+ to continue."
    exit 1
fi

echo "[*] Using Python: $($PY_CMD --version)"

# 2. Setup .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[*] Copying .env.example to .env..."
        cp ".env.example" ".env"
        echo "[+] Created .env file."
    fi
else
    echo "[*] Found existing .env configuration."
fi

# 3. Setup Virtual Environment
if [ ! -f "venv/bin/python" ]; then
    echo "[*] Creating virtual environment at 'venv'..."
    $PY_CMD -m venv venv || {
        echo "[!] Could not create venv. Using system Python..."
        VENV_PY="$PY_CMD"
    }
    if [ -f "venv/bin/python" ]; then
        VENV_PY="venv/bin/python"
        echo "[+] Virtual environment created."
    fi
else
    echo "[*] Using existing virtual environment at venv/"
    VENV_PY="venv/bin/python"
fi

# 4. Install dependencies
echo "[*] Installing/verifying dependencies..."
"$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
"$VENV_PY" -m pip install -r requirements.txt || {
    echo "[!] Warning: Some dependencies could not be installed."
}

# 5. Apply migrations
echo "[*] Applying database migrations..."
"$VENV_PY" manage.py migrate --noinput

# 6. Open browser and launch server
URL="http://127.0.0.1:8000/"
echo ""
echo "========================================================================"
echo " MindBridge is launching on $URL"
echo " Case Study: Nasarawa State University, Keffi (NSUK)"
echo " Gemini AI Support: Active"
echo " Press Ctrl+C to stop the server at any time."
echo "========================================================================"
echo ""

# Open browser based on OS
if command -v xdg-open >/dev/null 2>&1; then
    (sleep 2 && xdg-open "$URL") &
elif command -v open >/dev/null 2>&1; then
    (sleep 2 && open "$URL") &
fi

"$VENV_PY" manage.py runserver 127.0.0.1:8000
