#!/usr/bin/env python3
"""
TUNG TUNG SAHUR — RUN!  ONLINE EDITION
Patches PlayerManager to sync with the online server.
Drop this file next to evil.py and run: python tung_online.py

Auto-updates evil.py and tung_online.py from GitHub on launch.
"""

import sys, os, json, urllib.request, urllib.parse, urllib.error
import time

# ── Version & update config ───────────────────────────────────────────
LAUNCHER_VERSION = "2.0.0"

# GitHub raw URLs — update GITHUB_REPO to your actual repo path
GITHUB_REPO      = "nelkux2/MainTungSahur"  # e.g. "YourUser/tung-tung-run"
GITHUB_BRANCH    = "main"
GITHUB_RAW       = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"

# Files to keep up to date (remote path -> local filename)
UPDATE_FILES = {
    "tung_online.py": "tung_online.py",
    "evil.py":        "evil.py",
}

# Version file on GitHub — should contain a single line like: 1.0.1
VERSION_FILE_URL = f"{GITHUB_RAW}/version.txt"

# ── Server configuration ──────────────────────────────────────────────
DEFAULT_SERVER_URL = "https://www.perspectiveproductions.uk/api"
CONFIG_FILE = "tung_config.json"


def _normalize_server_url(raw):
    """Return a normalized API URL or an empty string for offline mode."""
    value = (raw or "").strip()
    if not value:
        return ""
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    value = value.rstrip("/")
    if not value.endswith("/api"):
        value += "/api"
    return value


def _load_server_url():
    """Load the server URL from env/config, with sane defaults."""
    env_url = os.getenv("TUNG_SERVER_URL")
    if env_url is not None:
        return _normalize_server_url(env_url)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if isinstance(cfg, dict):
            return _normalize_server_url(cfg.get("server_url"))
    except Exception:
        pass

    return _normalize_server_url(DEFAULT_SERVER_URL)


def _save_server_url(server_url):
    """Persist the selected server URL for future launches."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"server_url": server_url}, f, indent=2)
    except Exception:
        pass


SERVER_URL = _load_server_url()

# ── Auto-updater ──────────────────────────────────────────────────────

def _fetch_text(url, timeout=8):
    """Fetch a URL and return the text body, or None on failure."""
    import ssl
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode("utf-8")
    except ssl.SSLError as e:
        print(f"[net] SSL error fetching {url}: {e}")
        # Retry without cert verification as fallback
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(url, timeout=timeout, context=ctx) as r:
                return r.read().decode("utf-8")
        except Exception as e2:
            print(f"[net] SSL fallback also failed: {e2}")
            return None
    except Exception as e:
        print(f"[net] Failed to fetch {url}: {e}")
        return None


def _version_tuple(v):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return (0,)


def check_and_update():
    """
    Checks GitHub for a newer version.
    If found, downloads updated files and restarts the launcher.
    Shows a simple Tkinter progress window while updating.
    """
    print("[updater] Checking for updates...")
    remote_ver_str = _fetch_text(VERSION_FILE_URL)
    if not remote_ver_str:
        print("[updater] Could not reach update server — skipping.")
        return

    remote_ver = _version_tuple(remote_ver_str)
    local_ver  = _version_tuple(LAUNCHER_VERSION)

    if remote_ver <= local_ver:
        print(f"[updater] Up to date (v{LAUNCHER_VERSION}).")
        return

    print(f"[updater] New version available: {remote_ver_str.strip()} (current: {LAUNCHER_VERSION})")
    _show_update_ui(remote_ver_str.strip())


def _show_update_ui(new_version):
    """Downloads updates, showing a Tkinter progress window."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        _do_update_silent(new_version)
        return

    root = tk.Tk()
    root.title("Tung Tung Run — Updating")
    root.geometry("380x140")
    root.resizable(False, False)

    tk.Label(root, text=f"Updating to v{new_version}…", font=("Arial", 13, "bold")).pack(pady=(18, 4))
    status_var = tk.StringVar(value="Starting…")
    tk.Label(root, textvariable=status_var, font=("Arial", 10)).pack()
    bar = ttk.Progressbar(root, length=320, mode="determinate")
    bar.pack(pady=12)

    files = list(UPDATE_FILES.items())
    errors = []

    def do_updates():
        for i, (remote_name, local_name) in enumerate(files):
            status_var.set(f"Downloading {local_name}…")
            bar["value"] = int((i / len(files)) * 90)
            root.update()

            url  = f"{GITHUB_RAW}/{remote_name}"
            data = _fetch_text(url)
            if data is None:
                errors.append(local_name)
                continue

            # Write to a temp file first, then replace atomically
            tmp = local_name + ".tmp"
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(data)
                os.replace(tmp, local_name)
            except Exception as e:
                errors.append(f"{local_name} ({e})")

        bar["value"] = 100
        root.update()

        if errors:
            status_var.set(f"Some files failed: {', '.join(errors)}")
            root.after(3000, root.destroy)
        else:
            status_var.set("Done! Restarting…")
            root.after(1200, lambda: _restart(root))

    root.after(100, do_updates)
    root.mainloop()


def _do_update_silent(new_version):
    """Fallback updater with no UI."""
    print("[updater] Downloading updates…")
    for remote_name, local_name in UPDATE_FILES.items():
        url  = f"{GITHUB_RAW}/{remote_name}"
        data = _fetch_text(url)
        if data is None:
            print(f"[updater] Failed to download {remote_name}")
            continue
        tmp = local_name + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, local_name)
        print(f"[updater] Updated {local_name}")
    print("[updater] Restarting…")
    _restart(None)


def _restart(root=None):
    if root:
        root.destroy()
    os.execv(sys.executable, [sys.executable] + sys.argv)


# ── HTTP helpers ──────────────────────────────────────────────────────
def _api(method, path, data=None, params=None):
    """Make an HTTP request to the server. Returns (ok, body_dict)."""
    import ssl
    if not SERVER_URL:
        return False, {"error": "No server URL configured (offline mode)."}
    url = SERVER_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method=method)
    req.add_header("User-Agent", "Mozilla/5.0 (compatible; TungTungClient/1.0)")
    # Only set Content-Type for requests that send a body
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")

    def _do_request(context=None):
        kwargs = {"timeout": 8}
        if context:
            kwargs["context"] = context
        with urllib.request.urlopen(req, body, **kwargs) as resp:
            return True, json.loads(resp.read())

    try:
        return _do_request()
    except ssl.SSLError as e:
        print(f"[net] SSL error on {method} {path}: {e} — retrying without cert check")
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return _do_request(context=ctx)
        except Exception as e2:
            return False, {"error": f"SSL fallback failed: {e2}"}
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read())
        except Exception:
            err_body = {"error": str(e)}
        print(f"[net] HTTP {e.code} on {method} {path}: {err_body}")
        return False, err_body
    except urllib.error.URLError as e:
        print(f"[net] Connection error on {method} {path}: {e.reason}")
        return False, {"error": str(e.reason)}
    except Exception as e:
        print(f"[net] Unexpected error on {method} {path}: {e}")
        return False, {"error": str(e)}


# ── Online PlayerManager ──────────────────────────────────────────────
class OnlinePlayerManager:
    """
    Drop-in replacement for the original PlayerManager.
    Stores data on the server instead of the local L_PLRDATA file.
    Falls back to local file when offline.
    """

    _DEF = {
        "pw_hash": "", "salt": "",
        "high_score": 0, "total_score": 0, "coins": 0,
        "current_weapon": "none",  "owned_weapons":   [],
        "current_ability": "slam", "owned_abilities": [],
        "battle_pass": None,
    }

    def __init__(self):
        self.current_user = None
        self._token = None
        self._cache = {}
        self._offline_db = {"players": {}}
        self._is_online = bool(SERVER_URL)
        self._load_offline()

    def _load_offline(self):
        local_file = "L_PLRDATA_LOCAL"
        if os.path.exists(local_file):
            try:
                with open(local_file) as f:
                    self._offline_db = json.load(f)
            except Exception:
                pass

    def _save_offline(self):
        try:
            with open("L_PLRDATA_LOCAL", "w") as f:
                json.dump(self._offline_db, f)
        except Exception:
            pass

    def login(self, username, password):
        u = username.strip().lower()
        if self._is_online:
            ok, body = _api("POST", "/auth/login", {"username": u, "password": password})
            if ok:
                self._token = body["token"]
                self.current_user = u
                self._sync_cache()
                if u not in self._offline_db["players"]:
                    self._offline_db["players"][u] = dict(self._DEF)
                    self._offline_db["players"][u].update(self._cache)
                    self._save_offline()
                return None
            else:
                return body.get("error", "Server error.")
        else:
            if u not in self._offline_db["players"]:
                return "Username not found."
            self.current_user = u
            return None

    def signup(self, username, password):
        u = username.strip().lower()
        if len(u) < 3:
            return "Username must be >= 3 characters."
        if len(password) < 4:
            return "Password must be >= 4 characters."
        if self._is_online:
            ok, body = _api("POST", "/auth/signup", {"username": u, "password": password})
            if ok:
                self._token = body["token"]
                self.current_user = u
                self._cache = {
                    "high_score": 0, "total_score": 0, "coins": 0,
                    "current_weapon": "none", "owned_weapons": [],
                    "current_ability": "slam", "owned_abilities": [],
                    "battle_pass": None,
                }
                self._offline_db["players"][u] = dict(self._DEF)
                self._save_offline()
                return None
            else:
                return body.get("error", "Server error.")
        else:
            if u in self._offline_db["players"]:
                return "Username already taken."
            self._offline_db["players"][u] = dict(self._DEF)
            self._save_offline()
            self.current_user = u
            return None

    def logout(self):
        self.current_user = None
        self._token = None
        self._cache = {}

    def _load(self):
        if self._is_online and self._token:
            self._sync_cache()
        else:
            self._load_offline()

    def _sync_cache(self):
        if not self._token:
            return
        ok, body = _api("GET", "/players/me/data", params={"token": self._token})
        if ok:
            self._cache = {
                "high_score":       body.get("highScore", 0),
                "total_score":      body.get("totalScore", 0),
                "coins":            body.get("coins", 0),
                "current_weapon":   body.get("currentWeapon", "none"),
                "owned_weapons":    body.get("ownedWeapons", []),
                "current_ability":  body.get("currentAbility", "slam"),
                "owned_abilities":  body.get("ownedAbilities", []),
                "battle_pass":      body.get("battlePass", None),
            }

    def _push_cache(self):
        if not self._token:
            return
        payload = {
            "coins":           self._cache.get("coins", 0),
            "currentWeapon":   self._cache.get("current_weapon", "none"),
            "ownedWeapons":    self._cache.get("owned_weapons", []),
            "currentAbility":  self._cache.get("current_ability", "slam"),
            "ownedAbilities":  self._cache.get("owned_abilities", []),
            "battlePass":      self._cache.get("battle_pass", None),
        }
        _api("PUT", "/players/me/data", data=payload, params={"token": self._token})

    def current(self):
        if self._is_online and self._cache:
            rec = dict(self._cache)
        elif self.current_user and self.current_user in self._offline_db["players"]:
            rec = self._offline_db["players"][self.current_user]
        else:
            rec = dict(self._DEF)
        rec.setdefault("owned_abilities", [])
        rec.setdefault("current_ability", "slam")
        rec.setdefault("battle_pass", None)
        rec.setdefault("owned_weapons", [])
        rec.setdefault("current_weapon", "none")
        rec.setdefault("coins", 0)
        rec.setdefault("high_score", 0)
        rec.setdefault("total_score", 0)
        return rec

    def add_run_result(self, score, coins_earned):
        xp = max(1, score // 10)
        if self._is_online and self._token:
            ok, body = _api("POST", "/game/score", data={
                "token": self._token,
                "score": score,
                "coins": coins_earned,
                "xpEarned": xp,
            })
            if ok:
                self._sync_cache()
                return xp
        rec = self.current()
        if score > rec.get("high_score", 0):
            rec["high_score"] = score
        rec["total_score"] = rec.get("total_score", 0) + score
        rec["coins"] = rec.get("coins", 0) + coins_earned
        bp = self.get_or_init_bp()
        bp["xp"] = bp.get("xp", 0) + xp
        if self._is_online:
            self._cache.update(rec)
        elif self.current_user:
            self._offline_db["players"][self.current_user] = rec
            self._save_offline()
        return xp

    def get_or_init_bp(self):
        rec = self.current()
        now = time.time()
        bp = rec.get("battle_pass")
        if bp is None:
            bp = {"week_start": now, "xp": 0, "claimed_tiers": []}
        else:
            if now - bp.get("week_start", now) > 7 * 24 * 3600:
                bp = {"week_start": now, "xp": 0, "claimed_tiers": []}
        if self._is_online:
            self._cache["battle_pass"] = bp
        elif self.current_user:
            self._offline_db["players"][self.current_user]["battle_pass"] = bp
            self._save_offline()
        return bp

    def claim_bp_tier(self, tier_idx):
        from evil import BP_TIERS  # type: ignore
        bp = self.get_or_init_bp()
        rec = self.current()
        tier = BP_TIERS[tier_idx]
        if tier_idx in bp.get("claimed_tiers", []):
            return False, "Already claimed."
        if bp.get("xp", 0) < tier["xp_needed"]:
            return False, "Not enough XP."
        bp.setdefault("claimed_tiers", []).append(tier_idx)
        if tier["reward_type"] == "coins":
            rec["coins"] = rec.get("coins", 0) + tier["reward_val"]
        elif tier["reward_type"] == "ability":
            key = tier["reward_val"]
            if key not in rec.get("owned_abilities", []):
                rec.setdefault("owned_abilities", []).append(key)
        if self._is_online:
            self._cache.update(rec)
            self._cache["battle_pass"] = bp
            self._push_cache()
        elif self.current_user:
            self._offline_db["players"][self.current_user] = rec
            self._save_offline()
        return True, tier["label"]

    def buy_weapon(self, key):
        from evil import WEAPONS  # type: ignore
        rec = self.current()
        if key in rec.get("owned_weapons", []) or rec.get("coins", 0) < WEAPONS[key]["price"]:
            return False
        rec["coins"] -= WEAPONS[key]["price"]
        rec.setdefault("owned_weapons", []).append(key)
        rec["current_weapon"] = key
        if self._is_online:
            self._cache.update(rec)
            self._push_cache()
        elif self.current_user:
            self._offline_db["players"][self.current_user] = rec
            self._save_offline()
        return True

    def equip_weapon(self, key):
        rec = self.current()
        if key in rec.get("owned_weapons", []) or key == "none":
            rec["current_weapon"] = key
            if self._is_online:
                self._cache["current_weapon"] = key
                self._push_cache()
            elif self.current_user:
                self._offline_db["players"][self.current_user]["current_weapon"] = key
                self._save_offline()

    def buy_ability(self, key):
        from evil import ABILITIES  # type: ignore
        rec = self.current()
        if key in rec.get("owned_abilities", []) or rec.get("coins", 0) < ABILITIES[key]["price"]:
            return False
        rec["coins"] -= ABILITIES[key]["price"]
        rec.setdefault("owned_abilities", []).append(key)
        rec["current_ability"] = key
        if self._is_online:
            self._cache.update(rec)
            self._push_cache()
        elif self.current_user:
            self._offline_db["players"][self.current_user] = rec
            self._save_offline()
        return True

    def equip_ability(self, key):
        rec = self.current()
        if key == "slam" or key in rec.get("owned_abilities", []):
            rec["current_ability"] = key
            if self._is_online:
                self._cache["current_ability"] = key
                self._push_cache()
            elif self.current_user:
                self._offline_db["players"][self.current_user]["current_ability"] = key
                self._save_offline()

    def leaderboard(self):
        if self._is_online:
            ok, body = _api("GET", "/leaderboard", params={"limit": 20})
            if ok and isinstance(body, list):
                return [
                    (entry["username"], entry["highScore"], entry["totalScore"])
                    for entry in body
                ]
        rows = [
            (n, r.get("high_score", 0), r.get("total_score", 0))
            for n, r in self._offline_db["players"].items()
        ]
        rows.sort(key=lambda r: r[1], reverse=True)
        return rows


# ── Patch and launch ──────────────────────────────────────────────────
def main():
    # Check for updates before launching
    check_and_update()

    # Test server connection.
    # Any HTTP response (even 404) means the server is reachable.
    # Only network-level errors (DNS, refused, timeout) mean truly offline.
    if SERVER_URL:
        print(f"[net] Connecting to {SERVER_URL} ...")
        ok, body = _api("GET", "/leaderboard")
        err = body.get("error", "") if isinstance(body, dict) else ""
        network_fail = any(k in err.lower() for k in
                           ("resolve", "refused", "timed out", "timeout", "network unreachable", "errno"))
        if ok or not network_fail:
            print(f"[OK] Connected to server.")
            _save_server_url(SERVER_URL)
        else:
            print(f"[WARNING] Cannot reach server: {err}")
            print("          Tip: set TUNG_SERVER_URL or edit tung_config.json with a working server.")
            print("          Playing offline.")
    else:
        print("[INFO] No server URL configured — playing offline.")

    # Monkey-patch evil.py's PlayerManager with OnlinePlayerManager
    import evil  # type: ignore
    evil.PlayerManager = OnlinePlayerManager

    # Launch the game
    app = evil.App()
    app.mainloop()


if __name__ == "__main__":
    main()
