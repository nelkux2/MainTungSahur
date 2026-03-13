#!/bin/bash
echo "============================================"
echo "  TUNG TUNG SAHUR RUN - Launcher"
echo "============================================"
echo ""

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo ""
    echo "Mac users: Install from https://www.python.org/downloads/"
    echo "           or run: brew install python"
    echo ""
    echo "Linux users: run: sudo apt install python3 python3-pip"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""
echo "Installing/checking required packages..."
python3 -m pip install customtkinter pygame --quiet
echo "[OK] Packages ready."
echo ""
echo "Launching game..."
python3 tung_online.py
