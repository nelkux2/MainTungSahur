"""
Tung Tung Sahur — RUN!  Launcher v1.0.0
========================================
Compile with PyInstaller (see TungTungRun.spec).

What this does:
  1. Shows a splash window
  2. Copies bundled game files to %APPDATA%/TungTungRun/ on first run
  3. Checks GitHub for newer evil.py / tung_online.py
  4. Downloads any updates silently
  5. Also checks GitHub Releases for a newer launcher exe
  6. Runs the game in-process (no subprocess, no cmd window)
"""

import sys
import os
import json
import shutil
import runpy
import threading
import time
import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.error
import ssl

# ── Build info ────────────────────────────────────────────────────────
LAUNCHER_VERSION   = "1.0.0"
GITHUB_REPO        = "nelkux2/MainTungSahur"
GITHUB_BRANCH      = "main"
GITHUB_RAW         = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"
GITHUB_API_RELEASES = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# ── Paths (user-writable, no admin needed) ────────────────────────────
_APPDATA   = os.environ.get("APPDATA") or os.path.expanduser("~")
GAME_DIR   = os.path.join(_APPDATA, "TungTungRun")
VER_CACHE  = os.path.join(GAME_DIR, ".ver_cache.json")
UPDATE_EXE = os.path.join(GAME_DIR, "_launcher_update.exe")

# ── Files managed on GitHub ───────────────────────────────────────────
SCRIPT_FILES = ["evil.py", "tung_online.py", "version.txt"]
ASSET_FILES  = ["tung.png", "Crown.png", "tung_jumpscare.png",
                "tung_config.json", "L_PLRDATA_LOCAL"]

# ── Helpers ───────────────────────────────────────────────────────────

def _bundled(filename: str) -> str:
    """Return path to a file bundled inside the PyInstaller exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def _fetch(url: str, timeout: int = 15) -> bytes | None:
    """Fetch raw bytes from a URL; return None on any failure."""
    ctx = ssl.create_default_context()
    for verify in (True, False):
        if not verify:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(url, timeout=timeout, context=ctx) as r:
                return r.read()
        except ssl.SSLError:
            continue          # retry without cert check
        except Exception:
            return None
    return None


def _ver(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return (0,)


def _load_cache() -> dict:
    try:
        with open(VER_CACHE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(data: dict):
    try:
        os.makedirs(GAME_DIR, exist_ok=True)
        with open(VER_CACHE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ── Setup: copy bundled files to GAME_DIR on first run ───────────────

def ensure_game_dir(status_cb=None):
    """Ensure GAME_DIR exists and all required files are present."""
    os.makedirs(GAME_DIR, exist_ok=True)

    for fname in SCRIPT_FILES + ASSET_FILES:
        dest = os.path.join(GAME_DIR, fname)
        if not os.path.exists(dest):
            src = _bundled(fname)
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dest)
                    if status_cb:
                        status_cb(f"Installing {fname}…")
                except Exception:
                    pass


# ── Script updater ────────────────────────────────────────────────────

def check_script_updates(status_cb=None) -> bool:
    """Download newer game scripts from GitHub if available. Returns True if updated."""
    if status_cb:
        status_cb("Checking for game updates…")

    raw = _fetch(f"{GITHUB_RAW}/version.txt")
    if not raw:
        if status_cb:
            status_cb("Offline — using cached files")
        return False

    remote_ver = raw.decode(errors="ignore").strip()
    cache = _load_cache()
    local_ver = cache.get("game_version", "0.0.0")

    if _ver(remote_ver) <= _ver(local_ver):
        if status_cb:
            status_cb(f"Game is up to date  (v{remote_ver})")
        return False

    if status_cb:
        status_cb(f"Updating game  v{local_ver} → v{remote_ver}…")

    updated = False
    for fname in SCRIPT_FILES:
        if status_cb:
            status_cb(f"Downloading {fname}…")
        data = _fetch(f"{GITHUB_RAW}/{fname}")
        if not data:
            continue
        dest = os.path.join(GAME_DIR, fname)
        tmp  = dest + ".tmp"
        try:
            with open(tmp, "wb") as fh:
                fh.write(data)
            os.replace(tmp, dest)
            updated = True
        except Exception:
            try:
                os.remove(tmp)
            except Exception:
                pass

    if updated:
        cache["game_version"] = remote_ver
        _save_cache(cache)
        if status_cb:
            status_cb(f"Game updated to v{remote_ver} ✓")
    return updated


# ── Launcher self-updater (downloads new exe from GitHub Releases) ────

def check_launcher_update(status_cb=None) -> str | None:
    """
    Returns path to a downloaded newer exe, or None.
    The caller is responsible for replacing + restarting.
    """
    if not hasattr(sys, "_MEIPASS"):
        return None   # running as plain script, skip

    if status_cb:
        status_cb("Checking for launcher update…")

    raw = _fetch(GITHUB_API_RELEASES)
    if not raw:
        return None

    try:
        info = json.loads(raw)
    except Exception:
        return None

    tag = info.get("tag_name", "").lstrip("v")
    if not tag or _ver(tag) <= _ver(LAUNCHER_VERSION):
        return None   # no newer release

    # Find the .exe asset
    exe_url = None
    for asset in info.get("assets", []):
        name = asset.get("name", "")
        if name.lower().endswith(".exe"):
            exe_url = asset.get("browser_download_url")
            break

    if not exe_url:
        return None

    if status_cb:
        status_cb(f"Downloading launcher update v{tag}…")
    data = _fetch(exe_url, timeout=120)
    if not data:
        return None

    os.makedirs(GAME_DIR, exist_ok=True)
    with open(UPDATE_EXE, "wb") as fh:
        fh.write(data)
    return UPDATE_EXE


def apply_launcher_update(new_exe: str):
    """
    Replace the running exe with the downloaded one and restart.
    Uses a tiny Python helper written to %TEMP% and launched via
    subprocess with a hidden window (no visible cmd/PowerShell).
    """
    import subprocess
    import tempfile

    current_exe = sys.executable
    helper = os.path.join(tempfile.gettempdir(), "_tung_updater.pyw")

    script = f"""
import time, os, shutil, subprocess
time.sleep(1.5)
try:
    shutil.copy2({new_exe!r}, {current_exe!r})
except Exception:
    pass
subprocess.Popen([{current_exe!r}])
"""
    with open(helper, "w") as fh:
        fh.write(script)

    # Run helper completely hidden — no console window
    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008
    try:
        # Try pythonw.exe first (guaranteed no window)
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = "pythonw.exe"
        subprocess.Popen(
            [pythonw, helper],
            creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
            close_fds=True,
        )
    except Exception:
        # Fallback: use .pyw association (Windows opens it with pythonw automatically)
        os.startfile(helper)  # type: ignore[attr-defined]

    sys.exit(0)


# ── Game launcher ─────────────────────────────────────────────────────

def launch_game():
    """Run tung_online.main() in this process — all deps already loaded."""
    os.chdir(GAME_DIR)
    if GAME_DIR not in sys.path:
        sys.path.insert(0, GAME_DIR)
    # Clear any previously cached game modules
    for mod in list(sys.modules.keys()):
        if mod in ("evil", "tung_online"):
            del sys.modules[mod]
    runpy.run_path(os.path.join(GAME_DIR, "tung_online.py"), run_name="__main__")


# ── Splash window ─────────────────────────────────────────────────────

class SplashWindow:
    BG   = "#07000f"
    PINK = "#ff1f6e"
    TEAL = "#00ddb4"
    TEXT = "#ede0ff"
    RED  = "#ff3030"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tung Tung Sahur — RUN!")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        self.root.overrideredirect(False)

        W, H = 460, 200
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

        tk.Label(
            self.root, text="TUNG TUNG SAHUR — RUN!",
            font=("Courier New", 17, "bold"), fg=self.PINK, bg=self.BG,
        ).pack(pady=(22, 4))

        self._status = tk.StringVar(value="Starting…")
        tk.Label(
            self.root, textvariable=self._status,
            font=("Courier New", 10), fg=self.TEAL, bg=self.BG,
        ).pack(pady=2)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Tung.Horizontal.TProgressbar",
            troughcolor=self.BG, background=self.PINK, bordercolor=self.BG,
        )
        self._bar = ttk.Progressbar(
            self.root, style="Tung.Horizontal.TProgressbar",
            length=380, mode="indeterminate",
        )
        self._bar.pack(pady=10)
        self._bar.start(12)

        self._err = tk.StringVar()
        tk.Label(
            self.root, textvariable=self._err,
            font=("Courier New", 9), fg=self.RED, bg=self.BG,
        ).pack()

    def status(self, msg: str):
        self._status.set(msg)
        try:
            self.root.update()
        except Exception:
            pass

    def error(self, msg: str):
        self._err.set(msg)
        try:
            self.root.update()
        except Exception:
            pass

    def close(self):
        try:
            self._bar.stop()
            self.root.destroy()
        except Exception:
            pass


# ── Entry point ───────────────────────────────────────────────────────

def main():
    splash = SplashWindow()
    error_msg = None
    new_exe = None

    def worker():
        nonlocal error_msg, new_exe
        try:
            splash.status("Installing game files…")
            ensure_game_dir(status_cb=splash.status)

            check_script_updates(status_cb=splash.status)

            new_exe = check_launcher_update(status_cb=splash.status)
            if new_exe:
                splash.status("Launcher update downloaded — restarting…")

            splash.status("Launching…")
            time.sleep(0.4)
        except Exception as exc:
            error_msg = str(exc)
        finally:
            try:
                splash.root.after(0, splash.close)
            except Exception:
                pass

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    splash.root.mainloop()
    t.join(timeout=60)

    if error_msg:
        # Show error in a simple messagebox if something went wrong
        try:
            import tkinter.messagebox as mb
            mb.showerror("Tung Tung Run — Error", error_msg)
        except Exception:
            pass
        return

    # Apply launcher self-update if one was downloaded
    if new_exe and os.path.exists(new_exe):
        apply_launcher_update(new_exe)
        return  # apply_launcher_update calls sys.exit

    launch_game()


if __name__ == "__main__":
    main()
