# TungTungRun.spec
# ─────────────────────────────────────────────────────────────────────────────
# Build command (run from the repo root):
#
#   pip install pyinstaller customtkinter pygame cryptography
#   pyinstaller TungTungRun.spec
#
# Output:  dist/TungTungRun.exe  (single-file, no console window)
# ─────────────────────────────────────────────────────────────────────────────

import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

# ── Collect all data for bundled packages ────────────────────────────────────
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")
pygame_datas = collect_data_files("pygame")

# ── Game assets & scripts to bundle ─────────────────────────────────────────
game_datas = [
    ("tung.png",            "."),
    ("Crown.png",           "."),
    ("tung_jumpscare.png",  "."),
    ("tung_config.json",    "."),
    ("L_PLRDATA_LOCAL",     "."),
    ("evil.py",             "."),
    ("tung_online.py",      "."),
    ("version.txt",         "."),
]

all_datas = ctk_datas + pygame_datas + game_datas

# ── Analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=ctk_binaries,
    datas=all_datas,
    hiddenimports=[
        # customtkinter
        *ctk_hiddenimports,
        # stdlib used dynamically
        "runpy", "importlib", "importlib.util",
        # game deps
        "pygame", "pygame.font", "pygame.mixer", "pygame.image",
        "pygame.transform", "pygame.draw", "pygame.display",
        "customtkinter",
        "cryptography", "cryptography.fernet",
        "hashlib", "hmac",
        # network — urllib.request depends on email & http internally
        "ssl", "urllib.request", "urllib.parse", "urllib.error",
        "email", "email.message", "email.parser", "email.feedparser",
        "email.header", "email.charset", "email.encoders",
        "http", "http.client", "http.cookiejar",
        # json / threading
        "json", "threading",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude things with no stdlib dependents
        "matplotlib", "numpy", "scipy", "pandas",
        "PIL", "Pillow",
        "xmlrpc",
        "unittest", "doctest", "pdb",
        "tkinter.test",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="TungTungRun",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # No console / cmd window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="tung.ico",    # uncomment + add tung.ico to use a custom icon
)
