# TungTungRun.spec
import os, sys
from PyInstaller.utils.hooks import collect_data_files, collect_all
import glob

_py_dir = os.path.dirname(sys.executable)
_vc_dlls = glob.glob(os.path.join(_py_dir, "vcruntime*.dll"))
extra_binaries = [(dll, ".") for dll in _vc_dlls]


block_cipher = None

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")
pygame_datas   = collect_data_files("pygame")
certifi_datas  = collect_data_files("certifi")   # ← CA bundle

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

all_datas = ctk_datas + pygame_datas + certifi_datas + game_datas

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=ctk_binaries + extra_binaries,
    datas=all_datas,
    hiddenimports=[
        *ctk_hiddenimports,
        "runpy", "importlib", "importlib.util",
        "pygame", "pygame.font", "pygame.mixer", "pygame.image",
        "pygame.transform", "pygame.draw", "pygame.display",
        "customtkinter",
        "cryptography", "cryptography.fernet",
        "hashlib", "hmac",
        # network
        "ssl", "certifi",
        "urllib.request", "urllib.parse", "urllib.error",
        "email", "email.message", "email.parser", "email.feedparser",
        "email.header", "email.charset", "email.encoders",
        "http", "http.client", "http.cookiejar",
        "json", "threading",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["hook_ssl.py"],   # ← sets SSL_CERT_FILE before game code runs
    excludes=[
        "matplotlib", "numpy", "scipy", "pandas",
        "PIL", "Pillow", "xmlrpc",
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
    upx=False,
    upx_exclude=["python312.dll", "vcruntime140.dll"],
    runtime_tmpdir=".",
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
