"""
build_local.py — Local Windows build helper
============================================
Run this on Windows to build TungTungRun.exe locally:

    python build_local.py

Requirements: pip install pyinstaller customtkinter pygame==2.5.2 cryptography
Output:       dist/TungTungRun.exe
"""

import subprocess
import sys
import os

REQUIRED = [
    "pyinstaller",
    "customtkinter",
    "pygame",
    "cryptography",
]

def main():
    print("=" * 60)
    print("  Tung Tung Sahur — RUN!  local build script")
    print("=" * 60)

    # Install deps
    print("\n[1/3] Installing / verifying dependencies…")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "pyinstaller", "customtkinter", "pygame==2.5.2", "cryptography",
        "--quiet",
    ])

    # Build
    print("\n[2/3] Running PyInstaller…")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "TungTungRun.spec",
        "--noconfirm",
    ])

    exe_path = os.path.join("dist", "TungTungRun.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / 1_048_576
        print(f"\n[3/3] ✓  Built successfully:  {exe_path}  ({size_mb:.1f} MB)")
        print("\nDouble-click dist\\TungTungRun.exe to run!")
    else:
        print("\n[ERROR] Build failed — dist/TungTungRun.exe not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
