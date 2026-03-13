#!/usr/bin/env python3
"""
TUNG TUNG SAHUR — RUN!  v5
CustomTkinter menus  +  Pygame game engine
New: Ability Shop, Locker, Weekly Battle Pass
Fixed: Tung Tung no longer runs ahead of the player
"""

import customtkinter as ctk
import tkinter as tk
import pygame
import sys, time, random, math, json, os, hashlib
from typing import Optional, List, Tuple

# ══════════════════════════════════════════════════════════════════════
#  ENCRYPTION
# ══════════════════════════════════════════════════════════════════════
try:
    from cryptography.fernet import Fernet as _Fernet
    import base64 as _b64
    _KEY    = _b64.urlsafe_b64encode(hashlib.sha256(b"TUNG_APP_SECRET_2025_xK9").digest())
    _cipher = _Fernet(_KEY)
    def _encrypt(data): return _cipher.encrypt(data)
    def _decrypt(data): return _cipher.decrypt(data)
except ImportError:
    import base64 as _b64
    def _encrypt(data): return _b64.b64encode(data)
    def _decrypt(data): return _b64.b64decode(data)

# ══════════════════════════════════════════════════════════════════════
#  SHARED CONSTANTS
# ══════════════════════════════════════════════════════════════════════
WIN_W, WIN_H   = 1080, 720
PLRDATA_FILE   = "L_PLRDATA"

WEAPONS = {
    "sword":  {"name": "Sword",  "price":  50, "stun": 1.0, "cooldown": 5.0, "damage": 12,
               "color": (136, 170, 255), "pg_color": "#88aaff",
               "desc": "[F] Slash in movement direction — 0.5 s swing, 5 s cooldown"},
    "gun":    {"name": "Gun",    "price": 150, "stun": 1.5, "cooldown": 4.5, "damage": 20,
               "color": (255, 136, 136), "pg_color": "#ff8888",
               "desc": "Ranged [F] shot — 1.5 s stun"},
    "mallet": {"name": "Mallet", "price": 300, "stun": 2.5, "cooldown": 6.0, "damage": 34,
               "color": (136, 255, 170), "pg_color": "#88ffaa",
               "desc": "Heavy [F] blow — 2.5 s stun"},
}

ABILITIES = {
    "triple_jump": {
        "name": "Triple Jump", "price": 250,
        "color": (200, 136, 255), "pg_color": "#c888ff",
        "desc": "Passive — Grants a 3rd mid-air jump",
    },
    "speed_slam": {
        "name": "Speed Slam",  "price": 350,
        "color": (255, 150,  51), "pg_color": "#ff9633",
        "desc": "Slam + land gives a 3 s speed boost",
    },
    "balloon": {
        "name": "Balloon",     "price": 450,
        "color": (136, 221, 255), "pg_color": "#88ddff",
        "desc": "Press [G] — Float for 5 s  (20 s cooldown)",
    },
}

# Battle Pass: 10 tiers, resets every 7 days
BP_TIERS = [
    {"xp_needed":  200, "reward_type": "skin",    "reward_val": "neon",         "label": "Neon Skin"},
    {"xp_needed":  500, "reward_type": "coins",   "reward_val": 100,            "label": "100 Coins"},
    {"xp_needed":  900, "reward_type": "skin",    "reward_val": "crimson",      "label": "Crimson Skin"},
    {"xp_needed": 1400, "reward_type": "ability", "reward_val": "triple_jump",  "label": "Triple Jump"},
    {"xp_needed": 2000, "reward_type": "skin",    "reward_val": "ice",          "label": "Ice Skin"},
    {"xp_needed": 2700, "reward_type": "ability", "reward_val": "speed_slam",   "label": "Speed Slam"},
    {"xp_needed": 3500, "reward_type": "skin",    "reward_val": "ghost",        "label": "Ghost Skin"},
    {"xp_needed": 4500, "reward_type": "ability", "reward_val": "balloon",      "label": "Balloon"},
    {"xp_needed": 5500, "reward_type": "skin",    "reward_val": "toxic",        "label": "Toxic Skin"},
    {"xp_needed": 7000, "reward_type": "skin",    "reward_val": "golden",       "label": "Golden Skin"},
    {"xp_needed": 9000, "reward_type": "skin",    "reward_val": "shadow",       "label": "Shadow Skin"},
]

# ── Skins ─────────────────────────────────────────────────────
# color = fallback pygame color if PNG not cached
# glow  = glow color when not slamming
# pg_color = hex for UI
SKINS = {
    "default": {"name": "Default", "color": (255,  31, 110), "pg_color": "#ff1f6e"},
    "neon":    {"name": "Neon",    "color": ( 57, 255, 180), "pg_color": "#39ffb4"},
    "ghost":   {"name": "Ghost",   "color": (200, 200, 255), "pg_color": "#c8c8ff"},
    "golden":  {"name": "Golden",  "color": (255, 215,   0), "pg_color": "#ffd700"},
    "crimson": {"name": "Crimson", "color": (220,  20,  60), "pg_color": "#dc143c"},
    "ice":     {"name": "Ice",     "color": (135, 206, 250), "pg_color": "#87cefa"},
    "toxic":   {"name": "Toxic",   "color": (127, 255,   0), "pg_color": "#7fff00"},
    "shadow":  {"name": "Shadow",  "color": ( 80,  20, 120), "pg_color": "#501478"},
}

C = {
    "bg": "#07000f", "bg2": "#0d001e", "bg3": "#120028",
    "pink": "#ff1f6e", "teal": "#00ddb4", "gold": "#ffd93d",
    "purple": "#a020f0", "text": "#ede0ff", "danger": "#ff3030",
    "grey": "#334455", "btn_hover": "#200040", "entry_bg": "#0a0020",
    "shop_card": "#0d0028", "owned": "#003322", "equipped": "#002244",
    "rank_gold": "#ffd93d", "rank_silv": "#b0b8c8", "rank_bron": "#c87840",
    "ability_card": "#001428", "ability_owned": "#0a1a00", "ability_eq": "#001a10",
    "bp_locked": "#0a0018", "bp_done": "#001a0a", "bp_avail": "#1a0a00",
}

PG = {
    "bg":     (7,   0,  15), "bg2":     (13,   0,  30),
    "ground": (24,  5,  48), "gnd_top": (136,  51, 255),
    "pink":  (255, 31, 110), "teal":    (  0, 221, 180),
    "gold":  (255,217,  61), "purple":  (160,  32, 240),
    "player":(255, 31, 110), "p_slam":  (255, 136,   0),
    "tung":  (204,144,  64), "stun":    ( 51,  68, 102),
    "coin":  (255,217,  61), "plat":    ( 22,   6,  42),
    "t_plat":( 58, 21, 102), "danger":  (255,  48,  48),
    "grey":  ( 51, 68,  85), "star1":   (255, 255, 255),
    "star2": (153,102, 204), "white":   (255, 255, 255),
    "sword": (136,170, 255), "hud_bg":  ( 13,   0,  30),
    "bar_bg":( 30, 10,  60), "black":   (  0,   0,   0),
    "balloon_ring": (136, 221, 255),
    "boost":  (255, 160,  40),
}

ctk.set_appearance_mode("dark")

# ══════════════════════════════════════════════════════════════════════
#  PLAYER MANAGER
# ══════════════════════════════════════════════════════════════════════
def _hash_pw(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def _new_salt():
    return os.urandom(16).hex()


class PlayerManager:
    _DEF = {
        "pw_hash": "", "salt": "",
        "high_score": 0, "total_score": 0, "coins": 0,
        "current_weapon": "none",  "owned_weapons":   [],
        "current_ability": "slam", "owned_abilities": [],
        "current_skin": "default", "owned_skins":     [],
        "battle_pass": None,
    }

    def __init__(self):
        self.current_user = None
        self._db = {"players": {}}
        self._load()

    def _load(self):
        if not os.path.exists(PLRDATA_FILE): return
        try:
            with open(PLRDATA_FILE, "rb") as f:
                self._db = json.loads(_decrypt(f.read()).decode())
        except Exception:
            self._db = {"players": {}}

    def _save(self):
        try:
            with open(PLRDATA_FILE, "wb") as f:
                f.write(_encrypt(json.dumps(self._db).encode()))
        except Exception:
            pass

    def login(self, username, password):
        u = username.strip().lower()
        if u not in self._db["players"]: return "Username not found."
        rec = self._db["players"][u]
        if rec["pw_hash"] != _hash_pw(password, rec["salt"]): return "Incorrect password."
        self.current_user = u
        return None

    def signup(self, username, password):
        u = username.strip().lower()
        if len(u) < 3:   return "Username must be >= 3 characters."
        if len(password) < 4: return "Password must be >= 4 characters."
        if u in self._db["players"]: return "Username already taken."
        salt = _new_salt()
        self._db["players"][u] = {
            **self._DEF, "salt": salt,
            "pw_hash": _hash_pw(password, salt),
            "owned_weapons": [], "owned_abilities": [],
        }
        self._save()
        self.current_user = u
        return None

    def logout(self):
        self.current_user = None

    def current(self):
        rec = self._db["players"][self.current_user]
        rec.setdefault("owned_abilities", [])
        rec.setdefault("current_ability", "slam")
        rec.setdefault("battle_pass", None)
        return rec

    # ── Battle Pass ──────────────────────────────────────────────────
    def get_or_init_bp(self):
        rec = self.current()
        now = time.time()
        if rec["battle_pass"] is None:
            rec["battle_pass"] = {"week_start": now, "xp": 0, "claimed_tiers": []}
            self._save()
        else:
            bp = rec["battle_pass"]
            if now - bp.get("week_start", now) > 7 * 24 * 3600:
                bp["week_start"] = now
                bp["xp"]          = 0
                bp["claimed_tiers"] = []
                self._save()
        return rec["battle_pass"]

    def claim_bp_tier(self, tier_idx):
        bp  = self.get_or_init_bp()
        rec = self.current()
        tier = BP_TIERS[tier_idx]
        if tier_idx in bp["claimed_tiers"]:      return False, "Already claimed."
        if bp["xp"] < tier["xp_needed"]:         return False, "Not enough XP."
        bp["claimed_tiers"].append(tier_idx)
        if tier["reward_type"] == "coins":
            rec["coins"] = rec.get("coins", 0) + tier["reward_val"]
        elif tier["reward_type"] == "ability":
            key = tier["reward_val"]
            if key not in rec["owned_abilities"]:
                rec["owned_abilities"].append(key)
        elif tier["reward_type"] == "skin":
            key = tier["reward_val"]
            if key not in rec.get("owned_skins", []):
                rec.setdefault("owned_skins", []).append(key)
        self._save()
        return True, tier["label"]

    # ── Weapons ──────────────────────────────────────────────────────
    def add_run_result(self, score, coins_earned):
        rec = self.current()
        if score > rec["high_score"]:
            rec["high_score"] = score
        rec["total_score"]  = rec.get("total_score", 0) + score
        rec["coins"]        = rec.get("coins", 0) + coins_earned
        bp  = self.get_or_init_bp()
        xp  = max(1, score // 10)
        bp["xp"] = bp.get("xp", 0) + xp
        self._save()
        return xp

    def buy_weapon(self, key):
        rec = self.current()
        if key in rec["owned_weapons"] or rec.get("coins", 0) < WEAPONS[key]["price"]:
            return False
        rec["coins"] -= WEAPONS[key]["price"]
        rec["owned_weapons"].append(key)
        rec["current_weapon"] = key
        self._save()
        return True

    def equip_weapon(self, key):
        rec = self.current()
        if key in rec["owned_weapons"] or key == "none":
            rec["current_weapon"] = key
            self._save()

    # ── Abilities ────────────────────────────────────────────────────
    def buy_ability(self, key):
        rec = self.current()
        if key in rec["owned_abilities"] or rec.get("coins", 0) < ABILITIES[key]["price"]:
            return False
        rec["coins"] -= ABILITIES[key]["price"]
        rec["owned_abilities"].append(key)
        rec["current_ability"] = key
        self._save()
        return True

    def equip_ability(self, key):
        rec = self.current()
        if key == "slam" or key in rec["owned_abilities"]:
            rec["current_ability"] = key
            self._save()

    def equip_skin(self, key):
        rec = self.current()
        if key == "default" or key in rec.get("owned_skins", []):
            rec["current_skin"] = key
            self._save()

    def leaderboard(self):
        rows = [
            (n, r.get("high_score", 0), r.get("total_score", 0))
            for n, r in self._db["players"].items()
        ]
        rows.sort(key=lambda r: r[1], reverse=True)
        return rows

    def get_friends(self):
        return {"friends": [], "sent": [], "received": []}
    def send_friend_request(self, u): return False, "Friends require an online connection."
    def accept_friend(self, u):       return False, "Offline."
    def decline_friend(self, u):      return False, "Offline."
    def remove_friend(self, u):       return False, "Offline."
    def get_messages(self, u):        return []
    def send_message(self, u, t):     return False, "Offline."
    def duel_create(self):            return None
    def duel_join(self, i):           return None
    def duel_get(self, i):            return None
    def duel_set_role(self, i, r):    return False, {}
    def duel_start(self, i):          return False
    def duel_push_state(self, i, s):  pass
    def duel_get_state(self, i):      return None
    def duel_push_input(self, i, inp):pass
    def duel_get_input(self, i):      return {"left": False, "right": False, "jump": False}


# ══════════════════════════════════════════════════════════════════════
#  PYGAME CONSTANTS
# ══════════════════════════════════════════════════════════════════════
HUD_H      = 76
PLAY_W     = WIN_W
PLAY_H     = WIN_H - HUD_H

SCROLL_SPD = 240.0
LEAN_SLOW  = 0.55
LEAN_FAST  = 1.45
GRAVITY    = 1900.0
SLAM_G     = 1400.0
JUMP_V     = -640.0
JUMP2_V    = -520.0
JUMP3_V    = -460.0
MAX_FALL   = 950.0
GROUND_Y   = PLAY_H - 64
PLAYER_SX  = 210

TUNG_START_WX = -380.0
TUNG_BASE_SPD = 290.0
TUNG_MAX_SPD  = 620.0
TUNG_ACCEL    = 3.5
TUNG_GAP_IDL  = 170.0
TUNG_GAP_K    = 0.85
TUNG_MAX_SX   = PLAYER_SX - 22  # Tung can NEVER go ahead of player on screen

PLAT_COOLDOWN  = 1.5
TEMP_PLAT_LIFE = 1.3
COIN_SCORE     = 10
STOMP_SCORE    = 50
DIST_BONUS_S   = 2.0

SPEED_SLAM_MULT = 1.9
SPEED_SLAM_DUR  = 3.0
BALLOON_DUR     = 5.0
BALLOON_CD      = 20.0
BALLOON_GRAV    = 0.04   # fraction of normal gravity while floating

PLAYER_W, PLAYER_H = 28, 28
TUNG_W,   TUNG_H   = 58, 76
COIN_R             = 10
PLAT_H             = 16

_SWORD_PTS = [
    (36, 0), (16, 4), (8, 10), (0, 6), (-14, 6),
    (-20, 0), (-14, -6), (0, -6), (8, -10), (16, -4),
]
SWORD_ANGS  = {"w": -90, "a": 180, "s": 90, "d": 0}
SWORD_RANGE = 80.0
SWORD_ARC   = 68.0
SWORD_SWING_DUR = 0.5
TUNG_MAX_HP = 100


def _rot_pts(pts, angle_deg, cx, cy):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


# ══════════════════════════════════════════════════════════════════════
#  WORLD OBJECTS
# ══════════════════════════════════════════════════════════════════════
class Platform:
    __slots__ = ("world_x", "y", "half_w", "is_temp", "expiry")
    def __init__(self, world_x, y, half_w, is_temp=False, expiry=0.0):
        self.world_x = float(world_x)
        self.y       = float(y)
        self.half_w  = int(half_w)
        self.is_temp = is_temp
        self.expiry  = expiry
    def sx(self, cam_x):   return self.world_x - cam_x
    def rect(self, cam_x):
        return pygame.Rect(int(self.sx(cam_x)) - self.half_w, int(self.y),
                           self.half_w * 2, PLAT_H)


class Coin:
    __slots__ = ("world_x", "y", "alive")
    def __init__(self, world_x, y):
        self.world_x = float(world_x)
        self.y       = float(y)
        self.alive   = True


class StarField:
    def __init__(self, count):
        self._s = [self._rand() for _ in range(count)]
    @staticmethod
    def _rand():
        return [random.uniform(0, PLAY_W), random.uniform(0, PLAY_H - 80),
                random.uniform(0.12, 0.55), random.randint(1, 2),
                random.choice([PG["star1"], PG["star2"]])]
    def update(self, dx):
        for s in self._s:
            s[0] -= dx * s[2]
            if s[0] < 0:
                s[0] += PLAY_W
                s[1] = random.uniform(0, PLAY_H - 80)
    def draw(self, surf):
        for x, y, _, size, color in self._s:
            pygame.draw.circle(surf, color, (int(x), int(y)), size)


# ══════════════════════════════════════════════════════════════════════
#  PYGAME GAME
# ══════════════════════════════════════════════════════════════════════
class PygameGame:
    def __init__(self, weapon_key, ability_key, skin_key="default", is_rank1=False):
        self.weapon_key  = weapon_key
        self.ability_key = ability_key
        self.skin_key    = skin_key
        self._is_rank1   = is_rank1
        self.score       = 0
        self.coins_col   = 0
        self.elapsed     = 0.0
        self._nxt_bonus  = DIST_BONUS_S
        self.dead        = False
        self.camera_x    = 0.0

        # Player physics
        self.p_y      = float(GROUND_Y - PLAYER_H)
        self.p_vy     = 0.0
        self.p_jumps  = 0
        self.p_on_gnd = True
        self.p_lean   = 0
        self.p_slam   = False
        self._prev_slam = False

        # Sword
        self._sk              = []
        self._sword_last      = -999.0
        self._sword_swing_end = 0.0
        self._sword_dir       = "d"
        self._sword_hit_done  = False

        # Projectile
        self._proj     = False
        self._proj_x   = 0.0
        self._proj_y   = 0.0
        self._proj_tx  = 0.0
        self._proj_ty  = 0.0
        self._wpn_last = -999.0

        # Ability state
        self.balloon_active  = False
        self.balloon_end     = 0.0
        self.balloon_cd_end  = 0.0
        self.speed_boost_end = 0.0

        # Tung
        self.tung_wx      = float(TUNG_START_WX)
        self.tung_y       = float(GROUND_Y - TUNG_H)
        self.tung_vy      = 0.0
        self.tung_jc      = 0
        self.tung_on_gnd  = True
        self.tung_spd     = TUNG_BASE_SPD
        self.tung_stun    = 0.0
        self.tung_apex    = False
        self.tung_hp      = TUNG_MAX_HP

        self.plat_last_t  = -PLAT_COOLDOWN
        self.platforms    = []
        self.coins        = []
        self.stars        = StarField(90)
        self._gen_world()

    # ── World gen ────────────────────────────────────────────────────
    def _gen_world(self):
        for i in range(9):
            wx = PLAYER_SX + 220 + i * random.randint(190, 310)
            self._add_plat(wx, random.randint(GROUND_Y - 190, GROUND_Y - 45),
                           random.randint(60, 150))
        for _ in range(12):
            self._add_coin(random.randint(260, 900),
                           random.randint(GROUND_Y - 200, GROUND_Y - 55))

    def _add_plat(self, wx, y, hw, is_temp=False, expiry=0.0):
        self.platforms.append(Platform(wx, y, hw, is_temp, expiry))

    def _add_coin(self, wx, y):
        self.coins.append(Coin(wx, y))

    # ── Helpers ──────────────────────────────────────────────────────
    @property
    def p_rect(self):
        return pygame.Rect(PLAYER_SX - PLAYER_W // 2, int(self.p_y), PLAYER_W, PLAYER_H)

    @property
    def tung_sx(self):
        return self.tung_wx - self.camera_x

    @property
    def tung_rect(self):
        return pygame.Rect(int(self.tung_sx) - TUNG_W // 2, int(self.tung_y), TUNG_W, TUNG_H)

    # ── Physics ──────────────────────────────────────────────────────
    def _resolve(self, sx, sy, vy, jc, ew, eh):
        on_gnd = False
        bottom = sy + eh
        hw_e   = ew // 2
        for plat in self.platforms:
            psx = plat.sx(self.camera_x)
            if abs(sx - psx) > plat.half_w + hw_e: continue
            pt = plat.y
            pb = plat.y + PLAT_H
            if vy >= 0 and bottom > pt and bottom < pb + 4 and sy < pt + 4:
                sy = pt - eh; vy = 0.0; jc = 0; on_gnd = True; break
            elif vy < 0 and sy < pb and sy > pt - 6:
                sy = pb; vy = 0.0; break
        if sy + eh >= GROUND_Y:
            sy = float(GROUND_Y - eh); vy = 0.0; jc = 0; on_gnd = True
        return sy, vy, jc, on_gnd

    # ── Input ────────────────────────────────────────────────────────
    def key_down(self, k):
        if k in (pygame.K_w, pygame.K_SPACE):
            max_j = 3 if self.ability_key == "triple_jump" else 2
            if self.p_jumps < max_j:
                if   self.p_jumps == 0: self.p_vy = JUMP_V
                elif self.p_jumps == 1: self.p_vy = JUMP2_V
                else:                   self.p_vy = JUMP3_V
                self.p_jumps += 1
                self.balloon_active = False  # cancel balloon on jump
            self._sk_push("w")
        elif k == pygame.K_a:
            self.p_lean = -1; self._sk_push("a")
        elif k == pygame.K_d:
            self.p_lean =  1; self._sk_push("d")
        elif k == pygame.K_s:
            self._sk_push("s")
            if not self.p_on_gnd:
                self.p_slam = True
        elif k == pygame.K_e:
            self._drop_plat()
        elif k == pygame.K_f:
            self._fire()
        elif k == pygame.K_g:
            self._activate_balloon()

    def key_up(self, k):
        if k == pygame.K_w:   self._sk_pop("w")
        elif k == pygame.K_a: self.p_lean = 0; self._sk_pop("a")
        elif k == pygame.K_d: self.p_lean = 0; self._sk_pop("d")
        elif k == pygame.K_s: self._sk_pop("s"); self.p_slam = False

    def _sk_push(self, k):
        if k in self._sk: self._sk.remove(k)
        self._sk.append(k)

    def _sk_pop(self, k):
        if k in self._sk: self._sk.remove(k)

    def _drop_plat(self):
        now = time.time()
        if now - self.plat_last_t < PLAT_COOLDOWN: return
        self.plat_last_t = now
        wx = self.camera_x + PLAYER_SX + random.uniform(-20, 20)
        self._add_plat(wx, self.p_y + PLAYER_H + 8, 82,
                       is_temp=True, expiry=now + TEMP_PLAT_LIFE)

    def _fire(self):
        now = time.time()

        if self.weapon_key == "sword":
            if now - self._sword_last < WEAPONS["sword"]["cooldown"]: return
            move_keys = [k for k in reversed(self._sk) if k in SWORD_ANGS]
            if not move_keys: return
            self._sword_dir = move_keys[0]
            self._sword_last = now
            self._sword_swing_end = now + SWORD_SWING_DUR
            self._sword_hit_done = False
            return

        if self.weapon_key not in ("gun", "mallet"): return
        if now - self._wpn_last < WEAPONS[self.weapon_key]["cooldown"]: return
        gap = PLAYER_SX - self.tung_sx
        if gap > 720 or gap < -70: return
        self._wpn_last = now
        self._proj     = True
        self._proj_x   = float(PLAYER_SX)
        self._proj_y   = self.p_y + PLAYER_H / 2
        self._proj_tx  = self.tung_sx
        self._proj_ty  = self.tung_y + TUNG_H / 2

    def _activate_balloon(self):
        if self.ability_key != "balloon": return
        now = time.time()
        if now < self.balloon_cd_end: return
        self.balloon_active = True
        self.balloon_end    = now + BALLOON_DUR
        self.balloon_cd_end = now + BALLOON_CD
        self.p_vy = min(self.p_vy, -60.0)  # gentle initial lift

    # ── Tung AI ──────────────────────────────────────────────────────
    def _tung_ai(self, dt, now):
        if now < self.tung_stun: return
        # Duel mode: human controls Tung
        duel_inp = getattr(self, "_duel_inp", None)
        if duel_inp:
            if duel_inp.get("left") and not duel_inp.get("right"):
                self.tung_wx -= TUNG_BASE_SPD * 1.1 * dt
            elif duel_inp.get("right") and not duel_inp.get("left"):
                self.tung_wx += TUNG_BASE_SPD * 1.1 * dt
            if duel_inp.get("jump") and self.tung_on_gnd and self.tung_jc == 0:
                self.tung_vy = JUMP_V * 0.88
                self.tung_jc = 1
            return
        gap   = PLAYER_SX - self.tung_sx
        extra = max(0.0, (gap - TUNG_GAP_IDL) * TUNG_GAP_K)
        spd   = min(TUNG_MAX_SPD, self.tung_spd + extra)
        self.tung_wx += spd * dt

        # ── TUNG POSITION CAP: never let Tung pass the player ────────
        max_wx = self.camera_x + TUNG_MAX_SX
        if self.tung_wx > max_wx:
            self.tung_wx = max_wx

        p_cy = self.p_y    + PLAYER_H / 2
        t_cy = self.tung_y + TUNG_H   / 2
        diff = p_cy - t_cy

        if self.tung_jc == 0 and diff < -45 and self.tung_on_gnd:
            self.tung_vy  = JUMP_V * 0.88
            self.tung_jc  = 1
            self.tung_apex = False

        if self.tung_jc == 1 and not self.tung_apex and self.tung_vy >= 0:
            self.tung_apex = True
            if diff < -80:
                self.tung_vy = JUMP_V * 0.78
                self.tung_jc = 2

        if self.tung_on_gnd:
            self.tung_apex = False

    # ── Main update ──────────────────────────────────────────────────
    def update(self, dt, now):
        boost = SPEED_SLAM_MULT if (self.ability_key == "speed_slam"
                                    and now < self.speed_boost_end) else 1.0
        scroll = SCROLL_SPD * boost * (
            LEAN_FAST if self.p_lean ==  1 else
            LEAN_SLOW if self.p_lean == -1 else 1.0)
        self.camera_x += scroll * dt
        self.elapsed  += dt
        self.tung_spd  = min(TUNG_MAX_SPD, TUNG_BASE_SPD + TUNG_ACCEL * self.elapsed)

        if self.elapsed >= self._nxt_bonus:
            self.score     += 5
            self._nxt_bonus += DIST_BONUS_S

        # ── Player physics ───────────────────────────────────────────
        self._prev_slam = self.p_slam

        # Balloon: override gravity when floating
        if self.balloon_active:
            if now >= self.balloon_end:
                self.balloon_active = False
            else:
                # Dampen vertical speed, apply a tiny residual gravity
                self.p_vy = self.p_vy * 0.88 + GRAVITY * BALLOON_GRAV * dt
                self.p_vy = max(-40.0, min(self.p_vy, 40.0))

        if not self.balloon_active:
            grav = GRAVITY + (SLAM_G if self.p_slam else 0.0)
            self.p_vy = min(self.p_vy + grav * dt, MAX_FALL)

        self.p_y += self.p_vy * dt
        self.p_y, self.p_vy, self.p_jumps, self.p_on_gnd = self._resolve(
            PLAYER_SX, self.p_y, self.p_vy, self.p_jumps, PLAYER_W, PLAYER_H)

        # Speed Slam trigger: slam landed this frame
        if self._prev_slam and self.p_on_gnd and not self.p_slam:
            self.p_slam = False
            if self.ability_key == "speed_slam":
                self.speed_boost_end = now + SPEED_SLAM_DUR
                self.score += 15  # small speed-slam landing bonus

        if self.p_on_gnd:
            self.p_slam = False

        # ── Tung physics ─────────────────────────────────────────────
        self._tung_ai(dt, now)
        self.tung_vy = min(self.tung_vy + GRAVITY * dt, MAX_FALL)
        self.tung_y += self.tung_vy * dt
        tsx = self.tung_sx
        self.tung_y, self.tung_vy, self.tung_jc, self.tung_on_gnd = self._resolve(
            tsx, self.tung_y, self.tung_vy, self.tung_jc, TUNG_W, TUNG_H)

        if self.tung_y > PLAY_H + 100:
            self.tung_wx  = self.camera_x + PLAYER_SX - 400
            self.tung_y   = float(GROUND_Y - TUNG_H)
            self.tung_vy  = 0.0; self.tung_jc = 0

        # Stars
        self.stars.update(scroll * dt)

        # Platforms
        alive = []
        for p in self.platforms:
            if p.is_temp and now > p.expiry: continue
            if p.sx(self.camera_x) + p.half_w < -100:
                if not p.is_temp:
                    nwx = self.camera_x + PLAY_W + random.randint(160, 360)
                    self._add_plat(nwx,
                                   random.randint(GROUND_Y - 190, GROUND_Y - 45),
                                   random.randint(60, 150))
                continue
            alive.append(p)
        self.platforms = alive

        # Coins
        alive_c = []
        for c in self.coins:
            if not c.alive: continue
            csx = c.world_x - self.camera_x
            if (abs(csx - PLAYER_SX) < PLAYER_W + COIN_R and
                    abs(c.y - (self.p_y + PLAYER_H / 2)) < PLAYER_H + COIN_R):
                c.alive = False
                self.score      += COIN_SCORE
                self.coins_col  += 1
                nwx = self.camera_x + PLAY_W + random.randint(80, 520)
                self._add_coin(nwx, random.randint(GROUND_Y - 200, GROUND_Y - 55))
                continue
            if csx < -60:
                c.world_x = self.camera_x + PLAY_W + random.randint(80, 450)
                c.y       = random.randint(GROUND_Y - 200, GROUND_Y - 55)
            alive_c.append(c)
        self.coins = alive_c

        # Sword hit
        if self.weapon_key == "sword" and now <= self._sword_swing_end and not self._sword_hit_done:
            ang  = SWORD_ANGS[self._sword_dir]
            t_cx = self.tung_sx
            t_cy = self.tung_y  + TUNG_H   / 2
            p_cy = self.p_y     + PLAYER_H  / 2
            dist = math.hypot(t_cx - PLAYER_SX, t_cy - p_cy)
            if dist <= SWORD_RANGE:
                a2t  = math.degrees(math.atan2(t_cy - p_cy, t_cx - PLAYER_SX))
                diff = abs((a2t - ang + 180) % 360 - 180)
                if diff <= SWORD_ARC:
                    self._sword_hit_done = True
                    self.tung_stun = now + WEAPONS["sword"]["stun"]
                    self.tung_hp = max(0, self.tung_hp - WEAPONS["sword"]["damage"])

        # Projectile
        if self._proj:
            dx = self._proj_tx - self._proj_x
            dy = self._proj_ty - self._proj_y
            d  = math.hypot(dx, dy)
            if d < 12:
                self._proj     = False
                self.tung_stun = now + WEAPONS[self.weapon_key]["stun"]
                self.tung_hp = max(0, self.tung_hp - WEAPONS[self.weapon_key]["damage"])
            else:
                step = 640.0 * dt
                frac = min(1.0, step / d)
                self._proj_x += dx * frac
                self._proj_y += dy * frac

        # Slam stomp
        if (self.p_slam and self.p_vy > 0 and now > self.tung_stun and
                self.p_rect.colliderect(self.tung_rect)):
            self.tung_stun = now + 2.5
            self.p_vy      = JUMP_V * 0.5
            self.p_slam    = False
            self.score    += STOMP_SCORE

        # Tung KO — 5 second stun, full HP restore, game continues
        if self.tung_hp <= 0:
            self.score += 250
            self.tung_hp   = TUNG_MAX_HP
            self.tung_stun = now + 5.0
            # knock Tung back so they don't immediately re-collide
            self.tung_wx   = self.camera_x + PLAYER_SX - 420
        if self.p_y > PLAY_H + 60:
            self.dead = True; return
        if (not self.p_slam and now > self.tung_stun and
                self.p_rect.colliderect(self.tung_rect)):
            self.dead = True

    # ── Draw ─────────────────────────────────────────────────────────
    def draw(self, surf, assets, now):
        surf.fill(PG["bg"])
        self.stars.draw(surf)

        # Ground
        pygame.draw.rect(surf, PG["ground"], (0, GROUND_Y, PLAY_W, PLAY_H - GROUND_Y + 2))
        pygame.draw.line(surf, PG["gnd_top"], (0, GROUND_Y), (PLAY_W, GROUND_Y), 3)

        # Platforms
        for p in self.platforms:
            r = p.rect(self.camera_x)
            if -300 < r.x < PLAY_W + 300:
                clr = PG["t_plat"] if p.is_temp else PG["plat"]
                pygame.draw.rect(surf, clr, r, border_radius=4)
                pygame.draw.rect(surf, PG["gnd_top"],
                                 pygame.Rect(r.x, r.y, r.width, 3), border_radius=2)

        # Coins
        for c in self.coins:
            if not c.alive: continue
            csx = int(c.world_x - self.camera_x)
            if -30 < csx < PLAY_W + 30:
                pulse = int(COIN_R * (0.82 + 0.18 * math.sin(now * 6 + c.world_x * 0.01)))
                pygame.draw.circle(surf, PG["coin"], (csx, int(c.y)), pulse)
                pygame.draw.circle(surf, PG["bg"],   (csx, int(c.y)), max(1, pulse - 4))

        # Sword
        if self.weapon_key == "sword" and now <= self._sword_swing_end:
            ang  = SWORD_ANGS[self._sword_dir]
            swng = math.degrees(math.sin(now * 18) * 0.38)
            pts  = _rot_pts(_SWORD_PTS, ang + swng,
                            float(PLAYER_SX), self.p_y + PLAYER_H / 2)
            pygame.draw.polygon(surf, PG["sword"], pts)
            pygame.draw.polygon(surf, PG["white"], pts, 1)

        # Projectile
        if self._proj:
            wclr = WEAPONS.get(self.weapon_key, {}).get("color", PG["teal"])
            pygame.draw.circle(surf, wclr, (int(self._proj_x), int(self._proj_y)), 9)

        # Balloon rings (ability visual)
        if self.balloon_active and now < self.balloon_end:
            rem  = self.balloon_end - now
            frac = rem / BALLOON_DUR
            for i in range(3):
                ring_r = int(22 + i * 12 + math.sin(now * 5 + i) * 4)
                alpha  = int(140 * frac * (1.0 - i * 0.3))
                rsu = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(rsu, (*PG["balloon_ring"], alpha),
                                   (ring_r, ring_r), ring_r, 2)
                surf.blit(rsu, (PLAYER_SX - ring_r, int(self.p_y + PLAYER_H / 2) - ring_r))

        # Speed boost aura
        if self.ability_key == "speed_slam" and now < self.speed_boost_end:
            rem = self.speed_boost_end - now
            gsu = pygame.Surface((60, 60), pygame.SRCALPHA)
            a   = int(100 * (rem / SPEED_SLAM_DUR))
            pygame.draw.ellipse(gsu, (*PG["boost"], a), gsu.get_rect())
            surf.blit(gsu, (PLAYER_SX - 30, int(self.p_y + PLAYER_H / 2) - 30))

        # Player glow
        pcx = PLAYER_SX
        pcy = int(self.p_y + PLAYER_H / 2)
        _skin = SKINS.get(self.skin_key, SKINS["default"])
        _skin_clr = _skin["color"]
        gcl = PG["p_slam"] if self.p_slam else _skin_clr
        gr  = int((PLAYER_W + 12) * (0.85 + 0.15 * math.sin(now * 9)))
        gsu = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(gsu, (*gcl, 75), gsu.get_rect())
        surf.blit(gsu, (pcx - gr, pcy - gr))

        # Player body — colored rect using current skin
        bcl = PG["p_slam"] if self.p_slam else _skin_clr
        pygame.draw.rect(surf, bcl, self.p_rect, border_radius=5)

        # Crown — drawn on top of player if they are #1 on leaderboard
        if assets.get("crown") and getattr(self, "_is_rank1", False):
            crown = assets["crown"]
            cx = PLAYER_SX - crown.get_width() // 2
            cy = int(self.p_y) - crown.get_height() - 2
            surf.blit(crown, (cx, cy))

        # Tung
        stun_now = now < self.tung_stun
        tsx_i = int(self.tung_sx)
        tsy_i = int(self.tung_y)

        if "tung" in assets:
            img = assets.get("tung_stun") if stun_now else assets["tung"]
            surf.blit(img, (tsx_i - TUNG_W // 2, tsy_i))
        else:
            clr = PG["stun"] if stun_now else PG["tung"]
            pygame.draw.rect(surf, clr,
                             (tsx_i - TUNG_W // 2, tsy_i, TUNG_W, TUNG_H),
                             border_radius=6)

        # Tung eyes
        if not stun_now:
            for ox in (-12, 12):
                ex = tsx_i + ox; ey = tsy_i + 20
                pygame.draw.circle(surf, PG["white"], (ex, ey), 6)
                dx = PLAYER_SX - ex
                dy = int(self.p_y + PLAYER_H / 2) - ey
                dl = max(1.0, math.hypot(dx, dy))
                pygame.draw.circle(surf, PG["black"],
                                   (ex + int(dx / dl * 3), ey + int(dy / dl * 3)), 3)
            a3  = now * 300 % 360
            sx3 = tsx_i + 26; sy3 = tsy_i + 22
            ex3 = sx3 + int(math.cos(math.radians(a3)) * 20)
            ey3 = sy3 + int(math.sin(math.radians(a3)) * 10)
            pygame.draw.line(surf, (212, 168, 85), (sx3, sy3), (ex3, ey3), 3)
            pygame.draw.circle(surf, (245, 224, 160), (ex3, ey3), 4)

        self._draw_hud(surf, assets, now)

    def _draw_hud(self, surf, assets, now):
        hy = PLAY_H
        pygame.draw.rect(surf, PG["hud_bg"], (0, hy, WIN_W, HUD_H))
        pygame.draw.line(surf, PG["gnd_top"], (0, hy), (WIN_W, hy), 2)

        fh = assets["font_hud"]
        sm = assets["font_sm"]
        x  = 18

        def blt(text, color, fnt=None):
            nonlocal x
            s = (fnt or fh).render(text, True, color)
            surf.blit(s, (x, hy + 16)); x += s.get_width() + 24

        blt(f"SCORE  {self.score:,}", PG["pink"])
        blt(f"COINS  {self.coins_col}", PG["coin"])
        dist_m = int(self.elapsed * SCROLL_SPD / 100)
        blt(f"DIST  {dist_m} m", PG["teal"])
        blt(f"TUNG HP  {self.tung_hp}/{TUNG_MAX_HP}", PG["danger"] if self.tung_hp < 30 else PG["gold"], sm)

        # Platform bar
        lbl = sm.render("[E]", True, PG["grey"])
        surf.blit(lbl, (x, hy + 18)); x += lbl.get_width() + 6
        ratio = min(1.0, (now - self.plat_last_t) / PLAT_COOLDOWN)
        bw, bh = 76, 10
        pygame.draw.rect(surf, PG["bar_bg"], (x, hy + 24, bw, bh), border_radius=4)
        if ratio > 0:
            bc = PG["teal"] if ratio >= 1.0 else PG["pink"]
            pygame.draw.rect(surf, bc, (x, hy + 24, int(bw * ratio), bh), border_radius=4)
        x += bw + 22

        # Weapon
        if self.weapon_key in WEAPONS:
            wpn = WEAPONS[self.weapon_key]
            cd  = max(0.0, (self._sword_last if self.weapon_key == "sword"
                            else self._wpn_last) + wpn["cooldown"] - now)
            rdy = cd <= 0
            blt(f"[F] {wpn['name'].upper()}  {'READY' if rdy else f'{cd:.1f}s'}",
                PG["teal"] if rdy else PG["grey"])
        else:
            blt("[F] NO WEAPON", PG["grey"])

        # Ability HUD
        if self.ability_key == "triple_jump":
            max_j = 3
            jleft = max_j - self.p_jumps
            blt(f"3-JUMP ({jleft} left)", PG["purple"])
        elif self.ability_key == "speed_slam":
            if now < self.speed_boost_end:
                blt(f"BOOST  {self.speed_boost_end - now:.1f}s", PG["boost"])
            else:
                blt("SPEED SLAM", PG["grey"])
        elif self.ability_key == "balloon":
            if self.balloon_active and now < self.balloon_end:
                blt(f"[G] FLOAT  {self.balloon_end - now:.1f}s", PG["balloon_ring"])
            elif now < self.balloon_cd_end:
                blt(f"[G] BALLOON  cd {self.balloon_cd_end - now:.0f}s", PG["grey"])
            else:
                blt("[G] BALLOON  READY", PG["teal"])
        else:
            blt("[S+Air] SLAM", PG["grey"])

        if self.p_slam:
            blt("▼ SLAM", PG["p_slam"])

        hint = sm.render(
            "WASD Move/Aim  S+Air Slam  E Platform  F Weapon  G Ability  ESC Pause  Q Quit",
            True, PG["grey"])
        surf.blit(hint, (WIN_W - hint.get_width() - 14, hy + 52))


# ══════════════════════════════════════════════════════════════════════
#  ASSET LOADER
# ══════════════════════════════════════════════════════════════════════
def _load_assets():
    assets = {}
    for fname in ("tung.png", "tung.gif"):
        if os.path.exists(fname):
            try:
                raw = pygame.image.load(fname).convert_alpha()
                assets["tung"] = pygame.transform.smoothscale(raw, (TUNG_W, TUNG_H))
                stunned = assets["tung"].copy()
                tint    = pygame.Surface((TUNG_W, TUNG_H), pygame.SRCALPHA)
                tint.fill((51, 68, 102, 160))
                stunned.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                assets["tung_stun"] = stunned
                break
            except Exception:
                pass

    # Crown for #1 player
    for crown_name in ("Crown.png", "crown.png", "Crown.PNG"):
        if os.path.exists(crown_name):
            try:
                raw = pygame.image.load(crown_name).convert_alpha()
                assets["crown"] = pygame.transform.smoothscale(raw, (36, 24))
                break
            except Exception:
                pass

    for k, sz, bold in [("font_lg", 30, True), ("font_md", 20, True),
                        ("font_hud", 16, True), ("font_sm", 13, False)]:
        for fam in ("Courier New", "Courier", "monospace", None):
            try:
                assets[k] = (pygame.font.SysFont(fam, sz, bold=bold) if fam
                             else pygame.font.Font(None, sz + 4))
                break
            except Exception:
                continue
    return assets


def _draw_pause(surf, assets):
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 155)); surf.blit(ov, (0, 0))
    bx = WIN_W // 2 - 230; by = WIN_H // 2 - 120
    pygame.draw.rect(surf, (13, 0, 30),  (bx, by, 460, 210), border_radius=16)
    pygame.draw.rect(surf, PG["teal"],    (bx, by, 460, 210), 2, border_radius=16)
    t  = assets["font_lg"].render("P A U S E D", True, PG["teal"])
    t2 = assets["font_md"].render("ESC  resume   ·   Q  quit to menu", True, (180, 160, 220))
    surf.blit(t,  (WIN_W // 2 - t.get_width()  // 2, by + 40))
    surf.blit(t2, (WIN_W // 2 - t2.get_width() // 2, by + 108))


def run_pygame_game(weapon_key, ability_key, skin_key="default", is_rank1=False, duel_sync=None):
    pygame.init()
    pygame.display.set_caption("Tung Tung Sahur — RUN!")
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock  = pygame.time.Clock()
    assets = _load_assets()
    game   = PygameGame(weapon_key, ability_key, skin_key, is_rank1=is_rank1)
    paused = False
    _last_net = 0.0

    while True:
        dt  = min(clock.tick(60) / 1000.0, 0.05)
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return game.score, game.coins_col, int(game.elapsed * SCROLL_SPD / 100)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                elif event.key == pygame.K_q and paused:
                    pygame.quit()
                    return game.score, game.coins_col, int(game.elapsed * SCROLL_SPD / 100)
                elif not paused:
                    game.key_down(event.key)
            elif event.type == pygame.KEYUP:
                if not paused:
                    game.key_up(event.key)

        if not paused:
            # Duel: apply Tung inputs from network and push game state
            if duel_sync and now - _last_net > 0.033:
                inp = duel_sync.get_input()
                game._duel_inp = inp
                plat_data = [[p.world_x - game.camera_x, p.y, p.half_w, p.is_temp]
                             for p in game.platforms[-12:]]
                duel_sync.push_state({
                    "cam_x":    game.camera_x,
                    "p_y":      game.p_y,
                    "tung_sx":  game.tung_sx,
                    "tung_y":   game.tung_y,
                    "score":    game.score,
                    "dead":     game.dead,
                    "plats":    plat_data,
                })
                _last_net = now
            game.update(dt, now)
            if game.dead:
                if duel_sync:
                    duel_sync.push_state({"dead": True, "tung_won": False,
                                          "cam_x":0,"p_y":0,"tung_sx":0,"tung_y":0,"score":game.score,"plats":[]})
                pygame.quit()
                return game.score, game.coins_col, int(game.elapsed * SCROLL_SPD / 100)

        game.draw(screen, assets, now)
        if paused: _draw_pause(screen, assets)
        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════
#  CTk UI HELPERS
# ══════════════════════════════════════════════════════════════════════
def _font(size, weight="normal"):
    return ctk.CTkFont(family="Courier New", size=size, weight=weight)

def _rule(parent, color, height=3, row=0):
    ctk.CTkFrame(parent, fg_color=color, height=height, corner_radius=0).grid(
        row=row, column=0, columnspan=10, sticky="ew")

def _entry(parent, placeholder, show=None, width=320):
    e = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width, height=44,
                     font=_font(15), corner_radius=6, fg_color=C["entry_bg"],
                     border_color=C["purple"], border_width=1,
                     text_color=C["text"], placeholder_text_color=C["grey"])
    if show: e.configure(show=show)
    return e

def _btn_primary(parent, text, cmd, width=280, height=52):
    return ctk.CTkButton(parent, text=text, font=_font(19, "bold"),
                         fg_color=C["pink"], hover_color="#cc1050", text_color="#ffffff",
                         width=width, height=height, corner_radius=8, command=cmd)

def _btn_ghost(parent, text, cmd, width=180, height=38, border_color=None):
    return ctk.CTkButton(parent, text=text, font=_font(13),
                         fg_color="transparent", hover_color=C["btn_hover"],
                         text_color=C["text"], border_width=1,
                         border_color=border_color or C["purple"],
                         width=width, height=height, corner_radius=6, command=cmd)


# ══════════════════════════════════════════════════════════════════════
#  CTk FRAMES
# ══════════════════════════════════════════════════════════════════════
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, pm, on_success, on_signup, on_quit):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm; self._ok = on_success
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="TUNG TUNG SAHUR", font=_font(50, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(42, 2))
        ctk.CTkLabel(self, text="— R U N ! —", font=_font(20),
                     text_color=C["teal"]).grid(row=2, column=0, pady=(0, 28))
        self._ue = _entry(self, "Username"); self._ue.grid(row=3, column=0, pady=6)
        self._pe = _entry(self, "Password", show="●"); self._pe.grid(row=4, column=0, pady=6)
        self._err = ctk.CTkLabel(self, text="", font=_font(13), text_color=C["danger"])
        self._err.grid(row=5, column=0, pady=4)
        _btn_primary(self, "LOG IN", self._go).grid(row=6, column=0, pady=8)
        ctk.CTkLabel(self, text="No account?", font=_font(12),
                     text_color=C["grey"]).grid(row=7, column=0, pady=(10, 2))
        _btn_ghost(self, "SIGN UP", on_signup, width=200).grid(row=8, column=0, pady=4)
        _btn_ghost(self, "QUIT", on_quit, width=120,
                   border_color=C["danger"]).grid(row=9, column=0, pady=(16, 4))
        _rule(self, C["purple"], height=2, row=13)
        self._pe.bind("<Return>", lambda e: self._go())
        self._ue.bind("<Return>", lambda e: self._pe.focus())

    def _go(self):
        err = self.pm.login(self._ue.get(), self._pe.get())
        if err: self._err.configure(text=err)
        else:   self._ok()


class SignupFrame(ctk.CTkFrame):
    def __init__(self, parent, pm, on_success, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm; self._ok = on_success
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["teal"], row=0)
        ctk.CTkLabel(self, text="CREATE ACCOUNT", font=_font(40, "bold"),
                     text_color=C["teal"]).grid(row=1, column=0, pady=(42, 18))
        self._ue = _entry(self, "Username  (min 3 chars)"); self._ue.grid(row=2, column=0, pady=6)
        self._pe = _entry(self, "Password  (min 4 chars)", show="●"); self._pe.grid(row=3, column=0, pady=6)
        self._ce = _entry(self, "Confirm password", show="●"); self._ce.grid(row=4, column=0, pady=6)
        self._err = ctk.CTkLabel(self, text="", font=_font(13), text_color=C["danger"])
        self._err.grid(row=5, column=0, pady=4)
        _btn_primary(self, "SIGN UP", self._go).grid(row=6, column=0, pady=8)
        _btn_ghost(self, "BACK TO LOGIN", on_back, width=200).grid(row=7, column=0, pady=6)
        _rule(self, C["purple"], height=2, row=13)
        self._ce.bind("<Return>", lambda e: self._go())

    def _go(self):
        pw = self._pe.get()
        if pw != self._ce.get(): self._err.configure(text="Passwords do not match."); return
        err = self.pm.signup(self._ue.get(), pw)
        if err: self._err.configure(text=err)
        else:   self._ok()


class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, pm, on_play, on_shop, on_locker, on_bp, on_lb, on_friends, on_messages, on_duel, on_logout, on_quit):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.columnconfigure(0, weight=1)
        for r in range(18): self.rowconfigure(r, weight=1)
        rec = pm.current()
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="TUNG TUNG SAHUR", font=_font(50, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(30, 2))
        ctk.CTkLabel(self, text="— R U N ! —", font=_font(20),
                     text_color=C["teal"]).grid(row=2, column=0, pady=(0, 4))
        ctk.CTkLabel(self, text=f"Logged in as  {pm.current_user}", font=_font(12),
                     text_color=C["grey"]).grid(row=3, column=0, pady=(0, 10))

        # Stats panel
        sf = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=10)
        sf.grid(row=4, column=0, padx=100, pady=4, sticky="ew")
        sf.columnconfigure((0, 1, 2, 3), weight=1)
        wpn = WEAPONS.get(rec["current_weapon"], {}).get("name", "None")
        abl = ABILITIES.get(rec.get("current_ability", "slam"),
                            {"name": "Slam"})["name"] if rec.get("current_ability") != "slam" else "Slam"
        for col, (lbl, val, clr) in enumerate([
            ("HIGH SCORE", f"{rec['high_score']:,}", C["pink"]),
            ("COINS",      str(rec["coins"]),        C["gold"]),
            ("WEAPON",     wpn,                      C["teal"]),
            ("ABILITY",    abl,                      C["purple"]),
        ]):
            ctk.CTkLabel(sf, text=lbl, font=_font(10), text_color=C["grey"]).grid(
                row=0, column=col, padx=20, pady=(12, 2))
            ctk.CTkLabel(sf, text=val, font=_font(17, "bold"), text_color=clr).grid(
                row=1, column=col, padx=20, pady=(0, 12))

        _btn_primary(self, "PLAY", on_play).grid(row=5, column=0, pady=8)

        # Secondary buttons row
        br1 = ctk.CTkFrame(self, fg_color="transparent")
        br1.grid(row=6, column=0, pady=4)
        for text, cmd, clr in [
            ("WEAPON SHOP", on_shop,   C["gold"]),
            ("LOCKER",      on_locker, C["teal"]),
            ("BATTLE PASS", on_bp,     C["purple"]),
        ]:
            ctk.CTkButton(br1, text=text, font=_font(13, "bold"),
                          fg_color=C["bg3"], hover_color=C["btn_hover"],
                          text_color=clr, border_width=1, border_color=clr,
                          width=190, height=42, corner_radius=8,
                          command=cmd).pack(side="left", padx=6)

        # Pending friend requests badge
        fd = pm.get_friends()
        pending = len(fd.get("received", []))
        friends_txt = f"FRIENDS  [{pending}]" if pending else "FRIENDS"

        br_lb = ctk.CTkFrame(self, fg_color="transparent")
        br_lb.grid(row=7, column=0, pady=4)
        ctk.CTkButton(br_lb, text="LEADERBOARD", font=_font(13, "bold"),
                      fg_color=C["bg3"], hover_color=C["btn_hover"],
                      text_color="#9040c0", border_width=1, border_color="#9040c0",
                      width=170, height=40, corner_radius=8,
                      command=on_lb).pack(side="left", padx=4)
        ctk.CTkButton(br_lb, text=friends_txt, font=_font(13, "bold"),
                      fg_color=C["bg3"], hover_color=C["btn_hover"],
                      text_color=C["gold"] if pending else C["teal"],
                      border_width=1, border_color=C["gold"] if pending else C["teal"],
                      width=160, height=40, corner_radius=8,
                      command=on_friends).pack(side="left", padx=4)

        br_lb2 = ctk.CTkFrame(self, fg_color="transparent")
        br_lb2.grid(row=8, column=0, pady=2)
        ctk.CTkButton(br_lb2, text="MESSAGES", font=_font(13, "bold"),
                      fg_color=C["bg3"], hover_color=C["btn_hover"],
                      text_color=C["purple"], border_width=1, border_color=C["purple"],
                      width=160, height=38, corner_radius=8,
                      command=on_messages).pack(side="left", padx=4)
        ctk.CTkButton(br_lb2, text="⚔ DUEL", font=_font(13, "bold"),
                      fg_color=C["bg3"], hover_color=C["btn_hover"],
                      text_color=C["pink"], border_width=1, border_color=C["pink"],
                      width=140, height=38, corner_radius=8,
                      command=on_duel).pack(side="left", padx=4)

        ctk.CTkLabel(self,
            text="WASD+Sword  ·  S+Air Slam  ·  E Platform  ·  F Gun/Mallet  ·  G Ability  ·  ESC Pause",
            font=_font(11), text_color=C["grey"]).grid(row=9, column=0, pady=(10, 2))

        br2 = ctk.CTkFrame(self, fg_color="transparent")
        br2.grid(row=10, column=0, pady=4)
        _btn_ghost(br2, "LOG OUT", on_logout, width=150, border_color=C["teal"]).pack(side="left", padx=8)
        _btn_ghost(br2, "QUIT",    on_quit,   width=120, border_color=C["danger"]).pack(side="left", padx=8)
        _rule(self, C["purple"], height=2, row=17)


class ShopFrame(ctk.CTkFrame):
    """Weapon Shop + Ability Shop in one tabbed frame."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.columnconfigure(0, weight=1)
        for r in range(12): self.rowconfigure(r, weight=1)
        _rule(self, C["gold"], row=0)
        ctk.CTkLabel(self, text="SHOP", font=_font(44, "bold"),
                     text_color=C["gold"]).grid(row=1, column=0, pady=(24, 4))
        self._wlbl = ctk.CTkLabel(self, text=self._wtxt(), font=_font(17, "bold"),
                                   text_color=C["teal"])
        self._wlbl.grid(row=2, column=0, pady=(0, 8))

        # Tabs
        self._tabs = ctk.CTkTabview(self, width=WIN_W - 100, height=380,
                                    fg_color=C["bg2"],
                                    segmented_button_fg_color=C["bg3"],
                                    segmented_button_selected_color=C["gold"],
                                    segmented_button_selected_hover_color="#bb8800",
                                    segmented_button_unselected_hover_color=C["btn_hover"],
                                    text_color=C["text"])
        self._tabs.grid(row=3, column=0, padx=50, pady=4)
        self._tabs.add("  Weapons  ")
        self._tabs.add("  Abilities  ")
        self._weapon_tab  = self._tabs.tab("  Weapons  ")
        self._ability_tab = self._tabs.tab("  Abilities  ")
        self._weapon_tab.columnconfigure((0, 1, 2), weight=1)
        self._ability_tab.columnconfigure((0, 1, 2), weight=1)

        self._wcards = {}; self._acards = {}
        self._rebuild_weapons()
        self._rebuild_abilities()

        _btn_ghost(self, "BACK", on_back, width=180).grid(row=4, column=0, pady=14)
        _rule(self, C["purple"], height=2, row=11)

    def _wtxt(self):
        return f"Wallet:  {self.pm.current().get('coins', 0)} coins"

    # ── Weapons ──────────────────────────────────────────────────────
    def _rebuild_weapons(self):
        for w in self._wcards.values(): w.destroy()
        self._wcards.clear()
        for col, (key, wpn) in enumerate(WEAPONS.items()):
            self._wcards[key] = self._weapon_card(key, wpn, col)

    def _weapon_card(self, key, wpn, col):
        rec   = self.pm.current()
        owned = key in rec["owned_weapons"]
        eq    = rec["current_weapon"] == key
        bg    = C["equipped"] if eq else C["owned"] if owned else C["shop_card"]
        card  = ctk.CTkFrame(self._weapon_tab, fg_color=bg, corner_radius=12,
                             border_width=2, border_color=wpn["pg_color"])
        card.grid(row=0, column=col, padx=14, pady=10, sticky="nsew")
        card.columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=wpn["name"].upper(), font=_font(19, "bold"),
                     text_color=wpn["pg_color"]).grid(row=0, column=0, pady=(18, 4))
        ctk.CTkLabel(card, text=wpn["desc"], font=_font(12),
                     text_color=C["text"], wraplength=155).grid(row=1, column=0, padx=8, pady=4)
        ctk.CTkLabel(card, text=f"Stun {wpn['stun']:.0f}s  CD {wpn['cooldown']:.1f}s",
                     font=_font(11), text_color=C["grey"]).grid(row=2, column=0, pady=4)
        if eq:
            ctk.CTkLabel(card, text="[ EQUIPPED ]", font=_font(13, "bold"),
                         text_color=C["teal"]).grid(row=3, column=0, pady=(6, 16))
        elif owned:
            ctk.CTkButton(card, text="EQUIP", font=_font(13, "bold"),
                          fg_color=C["teal"], hover_color="#00aa88", text_color="#000000",
                          width=120, height=32, corner_radius=6,
                          command=lambda k=key: self._equip_wpn(k)).grid(row=3, column=0, pady=(6, 16))
        else:
            ctk.CTkLabel(card, text=f"{wpn['price']} coins",
                         font=_font(13, "bold"), text_color=C["gold"]).grid(row=3, column=0, pady=(4, 2))
            can = rec.get("coins", 0) >= wpn["price"]
            ctk.CTkButton(card, text="BUY", font=_font(13, "bold"),
                          fg_color=C["gold"] if can else C["grey"],
                          hover_color="#ccaa00" if can else C["grey"],
                          text_color="#000000", state="normal" if can else "disabled",
                          width=120, height=32, corner_radius=6,
                          command=lambda k=key: self._buy_wpn(k)).grid(row=4, column=0, pady=(0, 16))
        return card

    def _buy_wpn(self, k):
        if self.pm.buy_weapon(k):
            self._wlbl.configure(text=self._wtxt()); self._rebuild_weapons()

    def _equip_wpn(self, k):
        self.pm.equip_weapon(k); self._rebuild_weapons()

    # ── Abilities ────────────────────────────────────────────────────
    def _rebuild_abilities(self):
        for w in self._acards.values(): w.destroy()
        self._acards.clear()
        # Default slam card
        self._acards["slam"] = self._slam_card()
        for col, (key, abl) in enumerate(ABILITIES.items(), start=1):
            self._acards[key] = self._ability_card(key, abl, col)

    def _slam_card(self):
        rec = self.pm.current()
        eq  = rec.get("current_ability", "slam") == "slam"
        bg  = C["ability_eq"] if eq else C["ability_owned"]
        card = ctk.CTkFrame(self._ability_tab, fg_color=bg, corner_radius=12,
                            border_width=2, border_color=C["pink"])
        card.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")
        card.columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="SLAM", font=_font(19, "bold"),
                     text_color=C["pink"]).grid(row=0, column=0, pady=(18, 4))
        ctk.CTkLabel(card, text="S + Air  →  ground pound", font=_font(12),
                     text_color=C["text"], wraplength=155).grid(row=1, column=0, padx=8, pady=4)
        ctk.CTkLabel(card, text="Default · FREE", font=_font(11),
                     text_color=C["gold"]).grid(row=2, column=0, pady=4)
        if eq:
            ctk.CTkLabel(card, text="[ EQUIPPED ]", font=_font(13, "bold"),
                         text_color=C["teal"]).grid(row=3, column=0, pady=(6, 16))
        else:
            ctk.CTkButton(card, text="EQUIP", font=_font(13, "bold"),
                          fg_color=C["teal"], hover_color="#00aa88", text_color="#000000",
                          width=120, height=32, corner_radius=6,
                          command=lambda: self._equip_abl("slam")).grid(row=3, column=0, pady=(6, 16))
        return card

    def _ability_card(self, key, abl, col):
        rec   = self.pm.current()
        owned = key in rec.get("owned_abilities", [])
        eq    = rec.get("current_ability") == key
        bg    = C["ability_eq"] if eq else C["ability_owned"] if owned else C["ability_card"]
        card  = ctk.CTkFrame(self._ability_tab, fg_color=bg, corner_radius=12,
                             border_width=2, border_color=abl["pg_color"])
        card.grid(row=0, column=col, padx=12, pady=10, sticky="nsew")
        card.columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=abl["name"].upper(), font=_font(17, "bold"),
                     text_color=abl["pg_color"]).grid(row=0, column=0, pady=(18, 4))
        ctk.CTkLabel(card, text=abl["desc"], font=_font(12),
                     text_color=C["text"], wraplength=155).grid(row=1, column=0, padx=8, pady=4)
        if eq:
            ctk.CTkLabel(card, text="[ EQUIPPED ]", font=_font(13, "bold"),
                         text_color=C["teal"]).grid(row=2, column=0, pady=(6, 16))
        elif owned:
            ctk.CTkButton(card, text="EQUIP", font=_font(13, "bold"),
                          fg_color=C["teal"], hover_color="#00aa88", text_color="#000000",
                          width=120, height=32, corner_radius=6,
                          command=lambda k=key: self._equip_abl(k)).grid(row=2, column=0, pady=(6, 16))
        else:
            ctk.CTkLabel(card, text=f"{abl['price']} coins",
                         font=_font(13, "bold"), text_color=C["gold"]).grid(row=2, column=0, pady=(4, 2))
            bp_unlock = next((t["label"] for t in BP_TIERS if t.get("reward_val") == key), None)
            if bp_unlock:
                ctk.CTkLabel(card, text=f"Battle Pass: {bp_unlock}",
                             font=_font(10), text_color=C["purple"]).grid(row=3, column=0, pady=(0, 2))
            can = rec.get("coins", 0) >= abl["price"]
            ctk.CTkButton(card, text="BUY", font=_font(13, "bold"),
                          fg_color=C["gold"] if can else C["grey"],
                          hover_color="#ccaa00" if can else C["grey"],
                          text_color="#000000", state="normal" if can else "disabled",
                          width=120, height=32, corner_radius=6,
                          command=lambda k=key: self._buy_abl(k)).grid(row=4, column=0, pady=(0, 16))
        return card

    def _buy_abl(self, k):
        if self.pm.buy_ability(k):
            self._wlbl.configure(text=self._wtxt()); self._rebuild_abilities()

    def _equip_abl(self, k):
        self.pm.equip_ability(k); self._rebuild_abilities()


class LockerFrame(ctk.CTkFrame):
    """Equip loadout: one weapon + one ability."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["teal"], row=0)
        ctk.CTkLabel(self, text="LOCKER", font=_font(44, "bold"),
                     text_color=C["teal"]).grid(row=1, column=0, pady=(24, 4))
        ctk.CTkLabel(self, text="Equip your loadout — one weapon, one ability",
                     font=_font(13), text_color=C["grey"]).grid(row=2, column=0, pady=(0, 8))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=3, column=0, padx=60, sticky="ew")
        body.columnconfigure((0, 1, 2), weight=1)

        # ── Left: Weapons ────────────────────────────────────────────
        wf = ctk.CTkFrame(body, fg_color=C["bg3"], corner_radius=12)
        wf.grid(row=0, column=0, padx=12, pady=8, sticky="nsew")
        wf.columnconfigure(0, weight=1)
        ctk.CTkLabel(wf, text="WEAPON", font=_font(18, "bold"),
                     text_color=C["gold"]).grid(row=0, column=0, pady=(18, 8), padx=20, sticky="w")
        self._wpn_frame = wf
        self._rebuild_wpn()

        # ── Middle: Abilities ────────────────────────────────────────
        af = ctk.CTkFrame(body, fg_color=C["bg3"], corner_radius=12)
        af.grid(row=0, column=1, padx=12, pady=8, sticky="nsew")
        af.columnconfigure(0, weight=1)
        ctk.CTkLabel(af, text="ABILITY", font=_font(18, "bold"),
                     text_color=C["purple"]).grid(row=0, column=0, pady=(18, 8), padx=20, sticky="w")
        self._abl_frame = af
        self._rebuild_abl()

        # ── Right: Skins ─────────────────────────────────────────────
        sf = ctk.CTkFrame(body, fg_color=C["bg3"], corner_radius=12)
        sf.grid(row=0, column=2, padx=12, pady=8, sticky="nsew")
        sf.columnconfigure(0, weight=1)
        ctk.CTkLabel(sf, text="SKIN", font=_font(18, "bold"),
                     text_color=C["pink"]).grid(row=0, column=0, pady=(18, 8), padx=20, sticky="w")
        self._skn_frame = sf
        self._rebuild_skn()

        _btn_ghost(self, "BACK", on_back, width=180).grid(row=4, column=0, pady=16)
        _rule(self, C["pink"], height=2, row=13)

    def _rebuild_wpn(self):
        for w in self._wpn_frame.winfo_children():
            if isinstance(w, ctk.CTkFrame): w.destroy()
        rec = self.pm.current()
        equipped = rec.get("current_weapon", "none")
        # "None" option
        self._locker_row(self._wpn_frame, 1, "none", "No Weapon",
                         C["grey"], equipped == "none",
                         lambda: self._set_wpn("none"))
        for ri, key in enumerate(WEAPONS, start=2):
            owned = key in rec["owned_weapons"]
            eq    = equipped == key
            wpn   = WEAPONS[key]
            txt   = wpn["name"] + ("" if owned else " 🔒")
            self._locker_row(self._wpn_frame, ri, key, txt,
                             wpn["pg_color"], eq,
                             (lambda k=key: self._set_wpn(k)) if owned else None)

    def _rebuild_abl(self):
        for w in self._abl_frame.winfo_children():
            if isinstance(w, ctk.CTkFrame): w.destroy()
        rec = self.pm.current()
        equipped = rec.get("current_ability", "slam")
        # Slam always available
        self._locker_row(self._abl_frame, 1, "slam", "Slam (default)",
                         C["pink"], equipped == "slam",
                         lambda: self._set_abl("slam"))
        for ri, key in enumerate(ABILITIES, start=2):
            owned = key in rec.get("owned_abilities", [])
            eq    = equipped == key
            abl   = ABILITIES[key]
            txt   = abl["name"] + ("" if owned else " 🔒")
            self._locker_row(self._abl_frame, ri, key, txt,
                             abl["pg_color"], eq,
                             (lambda k=key: self._set_abl(k)) if owned else None)

    def _locker_row(self, parent, row, key, name, color, is_eq, cmd):
        bg  = C["equipped"] if is_eq else C["bg2"]
        row_f = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8)
        row_f.grid(row=row, column=0, padx=16, pady=3, sticky="ew")
        row_f.columnconfigure(1, weight=1)
        dot = ctk.CTkFrame(row_f, fg_color=color if is_eq else C["grey"],
                           width=10, height=10, corner_radius=5)
        dot.grid(row=0, column=0, padx=(12, 8), pady=10)
        ctk.CTkLabel(row_f, text=name, font=_font(14), text_color=color if is_eq else C["text"]).grid(
            row=0, column=1, sticky="w")
        if is_eq:
            ctk.CTkLabel(row_f, text="EQUIPPED", font=_font(11, "bold"),
                         text_color=C["teal"]).grid(row=0, column=2, padx=12)
        elif cmd:
            ctk.CTkButton(row_f, text="EQUIP", font=_font(11, "bold"),
                          fg_color=C["bg3"], hover_color=C["btn_hover"],
                          text_color=C["teal"], border_width=1, border_color=C["teal"],
                          width=72, height=28, corner_radius=5,
                          command=cmd).grid(row=0, column=2, padx=8)
        else:
            ctk.CTkLabel(row_f, text="LOCKED", font=_font(11),
                         text_color=C["grey"]).grid(row=0, column=2, padx=12)

    def _rebuild_skn(self):
        for w in self._skn_frame.winfo_children():
            if isinstance(w, ctk.CTkFrame): w.destroy()
        rec = self.pm.current()
        equipped = rec.get("current_skin", "default")
        for ri, (key, skn) in enumerate(SKINS.items(), start=1):
            owned = key == "default" or key in rec.get("owned_skins", [])
            eq    = equipped == key
            txt   = skn["name"] + ("" if owned else " 🔒")
            clr   = skn["pg_color"]
            self._locker_row(self._skn_frame, ri, key, txt, clr, eq,
                             (lambda k=key: self._set_skn(k)) if owned else None)

    def _set_wpn(self, k):
        self.pm.equip_weapon(k); self._rebuild_wpn()

    def _set_abl(self, k):
        self.pm.equip_ability(k); self._rebuild_abl()

    def _set_skn(self, k):
        self.pm.equip_skin(k); self._rebuild_skn()


class BattlePassFrame(ctk.CTkFrame):
    """Weekly Battle Pass — 10 tiers, resets every 7 days."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["purple"], row=0)
        ctk.CTkLabel(self, text="BATTLE PASS", font=_font(44, "bold"),
                     text_color=C["purple"]).grid(row=1, column=0, pady=(22, 2))

        bp   = pm.get_or_init_bp()
        xp   = bp.get("xp", 0)
        max_xp = BP_TIERS[-1]["xp_needed"]
        secs_left = max(0, int(bp.get("week_start", time.time()) + 7 * 24 * 3600 - time.time()))
        days  = secs_left // 86400
        hours = (secs_left % 86400) // 3600

        ctk.CTkLabel(self, text=f"Weekly XP: {xp:,}  ·  Resets in {days}d {hours}h",
                     font=_font(13), text_color=C["grey"]).grid(row=2, column=0, pady=(0, 4))

        # Progress bar
        pf = ctk.CTkFrame(self, fg_color="transparent")
        pf.grid(row=3, column=0, padx=80, pady=4, sticky="ew")
        pf.columnconfigure(0, weight=1)
        ctk.CTkProgressBar(pf, progress_color=C["purple"], fg_color=C["bg3"],
                           height=16, corner_radius=8,
                           width=WIN_W - 160).grid(row=0, column=0, pady=6)
        pf.winfo_children()[0].set(min(1.0, xp / max_xp))

        # Tier grid
        sc = ctk.CTkScrollableFrame(self, fg_color=C["bg3"], corner_radius=12, height=330)
        sc.grid(row=4, column=0, padx=50, pady=6, sticky="ew")
        for col, (hdr, clr) in enumerate([("TIER", C["grey"]), ("REWARD", C["text"]),
                                           ("XP NEEDED", C["teal"]), ("STATUS", C["gold"])]):
            sc.columnconfigure(col, weight=1)
            ctk.CTkLabel(sc, text=hdr, font=_font(12, "bold"),
                         text_color=clr).grid(row=0, column=col, padx=14, pady=(10, 4))

        for i, tier in enumerate(BP_TIERS):
            claimed  = i in bp.get("claimed_tiers", [])
            can_claim = (not claimed) and xp >= tier["xp_needed"]
            clr_row  = C["bp_done"] if claimed else C["bp_avail"] if can_claim else C["bp_locked"]
            tclr     = C["gold"] if can_claim else (C["teal"] if claimed else C["grey"])

            tier_type = tier["reward_type"]
            if tier_type == "ability":
                reward_name = ABILITIES.get(tier["reward_val"], {}).get("name", tier["label"])
                rlabel = f"⚡ {reward_name}"
            else:
                rlabel = f"💰 {tier['label']}"

            ctk.CTkLabel(sc, text=f"#{i+1}", font=_font(13, "bold"),
                         text_color=tclr).grid(row=i+1, column=0, padx=14, pady=4)
            ctk.CTkLabel(sc, text=rlabel, font=_font(13),
                         text_color=tclr).grid(row=i+1, column=1, padx=14, pady=4)
            ctk.CTkLabel(sc, text=f"{tier['xp_needed']:,} XP", font=_font(13),
                         text_color=C["teal"]).grid(row=i+1, column=2, padx=14, pady=4)

            if claimed:
                ctk.CTkLabel(sc, text="✓ CLAIMED", font=_font(12, "bold"),
                             text_color=C["teal"]).grid(row=i+1, column=3, padx=14, pady=4)
            elif can_claim:
                ctk.CTkButton(sc, text="CLAIM!", font=_font(12, "bold"),
                              fg_color=C["gold"], hover_color="#ccaa00",
                              text_color="#000000", width=100, height=28, corner_radius=6,
                              command=lambda idx=i: self._claim(idx)).grid(
                                  row=i+1, column=3, padx=14, pady=4)
            else:
                need = max(0, tier["xp_needed"] - xp)
                ctk.CTkLabel(sc, text=f"{need:,} XP away", font=_font(11),
                             text_color=C["grey"]).grid(row=i+1, column=3, padx=14, pady=4)

        _btn_ghost(self, "BACK", on_back, width=180).grid(row=5, column=0, pady=12)
        _rule(self, C["pink"], height=2, row=13)

    def _claim(self, idx):
        ok, label = self.pm.claim_bp_tier(idx)
        if ok:
            # Reload the frame to reflect changes
            parent = self.master
            self.destroy()
            # We need the app to re-show this frame – use event
            parent.event_generate("<<BPRefresh>>")



# ── DuelNetSync — background thread for network I/O during duel ──────
import threading as _threading

class DuelNetSync:
    """Runs network calls on a background thread to avoid blocking the game loop."""
    def __init__(self, pm, lobby_id, role):
        self._pm       = pm
        self._id       = lobby_id
        self._role     = role          # "player" or "tung"
        self._lock     = _threading.Lock()
        self._state    = None          # latest game state (tung reads this)
        self._inp      = {"left": False, "right": False, "jump": False}
        self._pending_state = None     # player sets this to push
        self._pending_inp   = None     # tung sets this to push
        self._running  = True
        t = _threading.Thread(target=self._loop, daemon=True)
        t.start()

    def push_state(self, s):
        with self._lock: self._pending_state = dict(s)

    def push_input(self, inp):
        with self._lock: self._pending_inp = dict(inp)

    def get_state(self):
        with self._lock: return self._state

    def get_input(self):
        with self._lock: return dict(self._inp)

    def stop(self):
        self._running = False

    def _loop(self):
        import time as _time
        while self._running:
            try:
                if self._role == "player":
                    with self._lock:
                        s = self._pending_state; self._pending_state = None
                    if s: self._pm.duel_push_state(self._id, s)
                    inp = self._pm.duel_get_input(self._id)
                    with self._lock: self._inp = inp or self._inp
                else:
                    with self._lock:
                        inp = self._pending_inp; self._pending_inp = None
                    if inp: self._pm.duel_push_input(self._id, inp)
                    st = self._pm.duel_get_state(self._id)
                    if st:
                        with self._lock: self._state = st
            except Exception:
                pass
            _time.sleep(0.033)


class FriendsFrame(ctk.CTkFrame):
    """Friends list — view friends, send/accept/decline requests."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.columnconfigure(0, weight=1)
        for r in range(16): self.rowconfigure(r, weight=1)
        _rule(self, C["teal"], row=0)
        ctk.CTkLabel(self, text="FRIENDS", font=_font(44, "bold"),
                     text_color=C["teal"]).grid(row=1, column=0, pady=(24, 4))
        add_row = ctk.CTkFrame(self, fg_color="transparent")
        add_row.grid(row=2, column=0, pady=(4, 6))
        self._add_entry = ctk.CTkEntry(add_row, placeholder_text="Enter username…",
                                       width=240, height=38, font=_font(13),
                                       fg_color=C["entry_bg"], border_color=C["teal"], border_width=1)
        self._add_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(add_row, text="ADD FRIEND", font=_font(13, "bold"),
                      fg_color=C["teal"], hover_color="#009980", text_color=C["bg"],
                      width=130, height=38, corner_radius=8,
                      command=self._send_request).pack(side="left")
        self._status_lbl = ctk.CTkLabel(self, text="", font=_font(11), text_color=C["gold"])
        self._status_lbl.grid(row=3, column=0)
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=360)
        self._scroll.grid(row=4, column=0, padx=60, sticky="ew")
        self._scroll.columnconfigure(0, weight=1)
        _btn_ghost(self, "BACK", on_back, width=180).grid(row=5, column=0, pady=10)
        _rule(self, C["pink"], height=2, row=15)
        self._refresh()

    def _refresh(self):
        for w in self._scroll.winfo_children(): w.destroy()
        data = self.pm.get_friends()
        row = 0
        if data.get("received"):
            ctk.CTkLabel(self._scroll, text="FRIEND REQUESTS", font=_font(12, "bold"),
                         text_color=C["gold"]).grid(row=row, column=0, sticky="w", pady=(8,2))
            row += 1
            for u in data["received"]: self._request_row(row, u); row += 1
        friends = data.get("friends", [])
        lbl = f"FRIENDS ({len(friends)})" if friends else "No friends yet — add one above!"
        ctk.CTkLabel(self._scroll, text=lbl, font=_font(12, "bold"),
                     text_color=C["teal"]).grid(row=row, column=0, sticky="w", pady=(10,2))
        row += 1
        for entry in friends: self._friend_row(row, entry); row += 1
        if data.get("sent"):
            ctk.CTkLabel(self._scroll, text="PENDING (SENT)", font=_font(12, "bold"),
                         text_color=C["grey"]).grid(row=row, column=0, sticky="w", pady=(10,2))
            row += 1
            for u in data["sent"]:
                f = ctk.CTkFrame(self._scroll, fg_color=C["bg2"], corner_radius=8)
                f.grid(row=row, column=0, sticky="ew", pady=2); row += 1
                f.columnconfigure(1, weight=1)
                ctk.CTkLabel(f, text="⏳", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
                ctk.CTkLabel(f, text=u, font=_font(14), text_color=C["grey"]).grid(row=0, column=1, sticky="w")
                ctk.CTkLabel(f, text="Waiting…", font=_font(11), text_color=C["grey"]).grid(row=0, column=2, padx=12)

    def _friend_row(self, row, entry):
        u  = entry["username"] if isinstance(entry, dict) else entry
        hs = entry.get("highScore", 0) if isinstance(entry, dict) else 0
        f  = ctk.CTkFrame(self._scroll, fg_color=C["bg3"], corner_radius=8)
        f.grid(row=row, column=0, sticky="ew", pady=2)
        f.columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="👤", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
        ctk.CTkLabel(f, text=u, font=_font(14, "bold"), text_color=C["text"]).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(f, text=f"🏆 {hs:,}", font=_font(12), text_color=C["pink"]).grid(row=0, column=2, padx=8)
        ctk.CTkButton(f, text="REMOVE", font=_font(10), fg_color="transparent",
                      hover_color=C["btn_hover"], text_color=C["danger"],
                      border_width=1, border_color=C["danger"], width=70, height=26, corner_radius=5,
                      command=lambda u=u: self._remove(u)).grid(row=0, column=3, padx=8)

    def _request_row(self, row, username):
        f = ctk.CTkFrame(self._scroll, fg_color=C["bg2"], corner_radius=8)
        f.grid(row=row, column=0, sticky="ew", pady=2)
        f.columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="📨", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
        ctk.CTkLabel(f, text=username, font=_font(14), text_color=C["gold"]).grid(row=0, column=1, sticky="w")
        ctk.CTkButton(f, text="ACCEPT", font=_font(10, "bold"), fg_color=C["teal"],
                      hover_color="#009980", text_color=C["bg"], width=74, height=26, corner_radius=5,
                      command=lambda u=username: self._accept(u)).grid(row=0, column=2, padx=4)
        ctk.CTkButton(f, text="DECLINE", font=_font(10), fg_color="transparent",
                      hover_color=C["btn_hover"], text_color=C["danger"],
                      border_width=1, border_color=C["danger"], width=74, height=26, corner_radius=5,
                      command=lambda u=username: self._decline(u)).grid(row=0, column=3, padx=(0,8))

    def _send_request(self):
        target = self._add_entry.get().strip().lower()
        if not target: return
        ok, msg = self.pm.send_friend_request(target)
        self._add_entry.delete(0, "end")
        if ok:
            self._status_lbl.configure(text=f"✓ Request sent to {target}!", text_color=C["teal"])
        else:
            self._status_lbl.configure(text=f"✗ {msg}", text_color=C["danger"])
        self.after(3000, lambda: self._status_lbl.configure(text=""))
        self._refresh()

    def _accept(self, u): self.pm.accept_friend(u); self._refresh()
    def _decline(self, u): self.pm.decline_friend(u); self._refresh()
    def _remove(self, u): self.pm.remove_friend(u); self._refresh()


class MessagesFrame(ctk.CTkFrame):
    """DM system — friends list on left, chat on right."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self._other = None
        self._poll_id = None
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        for r in range(20): self.rowconfigure(r, weight=1)
        _rule(self, C["purple"], row=0)
        ctk.CTkLabel(self, text="MESSAGES", font=_font(36, "bold"),
                     text_color=C["purple"]).grid(row=1, column=0, columnspan=2, pady=(18, 4))

        # Left: friend list
        lf = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=10)
        lf.grid(row=2, column=0, rowspan=16, padx=(40,8), pady=8, sticky="nsew")
        lf.columnconfigure(0, weight=1)
        ctk.CTkLabel(lf, text="FRIENDS", font=_font(12, "bold"),
                     text_color=C["grey"]).grid(row=0, column=0, pady=(10,4), padx=12, sticky="w")
        self._friend_list = ctk.CTkScrollableFrame(lf, fg_color="transparent", width=160, height=320)
        self._friend_list.grid(row=1, column=0, padx=4, pady=4)
        self._friend_list.columnconfigure(0, weight=1)
        self._populate_friends()

        # Right: chat area
        self._chat_area = ctk.CTkScrollableFrame(self, fg_color=C["bg3"],
                                                  corner_radius=10, height=340)
        self._chat_area.grid(row=2, column=1, rowspan=14, padx=(8,40), pady=8, sticky="nsew")
        self._chat_area.columnconfigure(0, weight=1)
        self._empty_lbl = ctk.CTkLabel(self._chat_area,
                                        text="Select a friend to start chatting",
                                        font=_font(13), text_color=C["grey"])
        self._empty_lbl.grid(row=0, column=0, pady=40)

        # Input row
        inp_row = ctk.CTkFrame(self, fg_color="transparent")
        inp_row.grid(row=16, column=1, padx=(8,40), pady=(0,6), sticky="ew")
        inp_row.columnconfigure(0, weight=1)
        self._msg_entry = ctk.CTkEntry(inp_row, placeholder_text="Type a message…",
                                       height=40, font=_font(13), fg_color=C["entry_bg"],
                                       border_color=C["purple"], border_width=1)
        self._msg_entry.grid(row=0, column=0, padx=(0,8), sticky="ew")
        self._msg_entry.bind("<Return>", lambda e: self._send())
        ctk.CTkButton(inp_row, text="SEND", font=_font(13, "bold"),
                      fg_color=C["purple"], hover_color="#7010b0", text_color="white",
                      width=80, height=40, corner_radius=8,
                      command=self._send).grid(row=0, column=1)

        _btn_ghost(self, "BACK", on_back, width=160).grid(row=17, column=0, columnspan=2, pady=8)

    def _populate_friends(self):
        for w in self._friend_list.winfo_children(): w.destroy()
        data = self.pm.get_friends()
        for i, entry in enumerate(data.get("friends", [])):
            u = entry["username"] if isinstance(entry, dict) else entry
            bg = C["equipped"] if u == self._other else C["bg3"]
            btn = ctk.CTkButton(self._friend_list, text=u, font=_font(12),
                                 fg_color=bg, hover_color=C["btn_hover"],
                                 text_color=C["text"], anchor="w",
                                 width=150, height=34, corner_radius=6,
                                 command=lambda u=u: self._open_chat(u))
            btn.grid(row=i, column=0, pady=2, padx=4, sticky="ew")

    def _open_chat(self, username):
        self._other = username
        self._populate_friends()
        if self._poll_id:
            self.after_cancel(self._poll_id)
        self._load_messages()

    def _load_messages(self):
        if not self._other: return
        for w in self._chat_area.winfo_children(): w.destroy()
        msgs = self.pm.get_messages(self._other)
        if not msgs:
            ctk.CTkLabel(self._chat_area, text="No messages yet — say hi!",
                         font=_font(12), text_color=C["grey"]).grid(row=0, column=0, pady=20)
        for i, m in enumerate(msgs):
            is_me = m.get("from") == self.pm.current_user
            align = "e" if is_me else "w"
            clr   = C["teal"] if is_me else C["text"]
            bg    = C["equipped"] if is_me else C["bg2"]
            bubble = ctk.CTkFrame(self._chat_area, fg_color=bg, corner_radius=10)
            bubble.grid(row=i, column=0, sticky=align, padx=12, pady=2)
            ctk.CTkLabel(bubble, text=m.get("text",""), font=_font(13),
                         text_color=clr, wraplength=320).pack(padx=12, pady=6)
        # Auto-poll every 3s
        self._poll_id = self.after(3000, self._load_messages)

    def _send(self):
        if not self._other: return
        text = self._msg_entry.get().strip()
        if not text: return
        ok, err_msg = self.pm.send_message(self._other, text)
        if ok:
            self._msg_entry.delete(0, "end")
            self._load_messages()
        else:
            self._msg_entry.delete(0, "end")
            self._msg_entry.configure(placeholder_text=f"Error: {err_msg}")


class DuelFrame(ctk.CTkFrame):
    """Create or join a duel lobby."""
    def __init__(self, parent, pm, on_back, on_lobby):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.on_lobby = on_lobby
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="DUELS", font=_font(50, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(28, 4))
        ctk.CTkLabel(self, text="Challenge a friend — one plays as Tung!",
                     font=_font(14), text_color=C["grey"]).grid(row=2, column=0, pady=(0, 16))

        # Create lobby
        cf = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=12)
        cf.grid(row=3, column=0, padx=160, pady=8, sticky="ew")
        cf.columnconfigure(0, weight=1)
        ctk.CTkLabel(cf, text="CREATE LOBBY", font=_font(18, "bold"),
                     text_color=C["teal"]).grid(row=0, column=0, pady=(16,4))
        ctk.CTkLabel(cf, text="Share the code with a friend to start a duel.",
                     font=_font(12), text_color=C["grey"]).grid(row=1, column=0, pady=(0,10))
        ctk.CTkButton(cf, text="CREATE", font=_font(15, "bold"),
                      fg_color=C["teal"], hover_color="#009980", text_color=C["bg"],
                      width=200, height=44, corner_radius=8,
                      command=self._create).grid(row=2, column=0, pady=(0,16))

        # Join lobby
        jf = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=12)
        jf.grid(row=4, column=0, padx=160, pady=8, sticky="ew")
        jf.columnconfigure(0, weight=1)
        ctk.CTkLabel(jf, text="JOIN LOBBY", font=_font(18, "bold"),
                     text_color=C["gold"]).grid(row=0, column=0, pady=(16,4))
        self._code_entry = ctk.CTkEntry(jf, placeholder_text="Enter lobby code…",
                                        width=220, height=40, font=_font(14),
                                        fg_color=C["entry_bg"], border_color=C["gold"], border_width=1)
        self._code_entry.grid(row=1, column=0, pady=4)
        ctk.CTkButton(jf, text="JOIN", font=_font(15, "bold"),
                      fg_color=C["gold"], hover_color="#ccaa00", text_color=C["bg"],
                      width=200, height=44, corner_radius=8,
                      command=self._join).grid(row=2, column=0, pady=(4,16))

        self._err_lbl = ctk.CTkLabel(self, text="", font=_font(11), text_color=C["danger"])
        self._err_lbl.grid(row=5, column=0)
        _btn_ghost(self, "BACK", on_back, width=180).grid(row=6, column=0, pady=8)
        _rule(self, C["purple"], height=2, row=13)

    def _create(self):
        lobby_id = self.pm.duel_create()
        if lobby_id:
            self.on_lobby(lobby_id, is_host=True)
        else:
            self._err_lbl.configure(text="Could not create lobby — are you online?")

    def _join(self):
        code = self._code_entry.get().strip().lower()
        if not code:
            self._err_lbl.configure(text="Enter a lobby code first.")
            return
        lobby = self.pm.duel_join(code)
        if lobby:
            # Override server default role — let guest choose explicitly
            self.pm.duel_set_role(code, "player")
            self.on_lobby(code, is_host=False, initial_lobby=lobby)
        else:
            self._err_lbl.configure(text="Lobby not found or full.")


class DuelLobbyFrame(ctk.CTkFrame):
    """Waiting room — choose roles, start when both ready."""
    def __init__(self, parent, pm, lobby_id, is_host, on_back, on_start, initial_lobby=None):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.lobby_id = lobby_id
        self.is_host  = is_host
        self.on_start = on_start
        self._poll_id = None
        self._my_user = pm.current_user  # cache so guest can always find themselves
        self.columnconfigure(0, weight=1)
        for r in range(16): self.rowconfigure(r, weight=1)
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="DUEL LOBBY", font=_font(44, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(24, 2))

        # Code display
        code_f = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=10)
        code_f.grid(row=2, column=0, padx=300, pady=4, sticky="ew")
        ctk.CTkLabel(code_f, text="LOBBY CODE", font=_font(10), text_color=C["grey"]).pack(pady=(8,0))
        ctk.CTkLabel(code_f, text=lobby_id.upper(), font=_font(28, "bold"),
                     text_color=C["teal"]).pack(pady=(0,8))

        # Players panel
        self._players_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._players_frame.grid(row=3, column=0, padx=80, pady=8, sticky="ew")
        self._players_frame.columnconfigure((0,1), weight=1)

        self._status_lbl = ctk.CTkLabel(self, text="Waiting for opponent…",
                                         font=_font(13), text_color=C["grey"])
        self._status_lbl.grid(row=4, column=0, pady=4)

        self._start_btn = ctk.CTkButton(self, text="START DUEL", font=_font(17, "bold"),
                                         fg_color=C["pink"], hover_color="#cc0055",
                                         text_color="white", width=220, height=50,
                                         corner_radius=10, command=self._start,
                                         state="disabled")
        if is_host:
            self._start_btn.grid(row=5, column=0, pady=8)

        _btn_ghost(self, "LEAVE", on_back, width=180, border_color=C["danger"]).grid(row=6, column=0, pady=4)
        _rule(self, C["purple"], height=2, row=15)
        # Render initial lobby immediately (avoids blank flash on join)
        if initial_lobby:
            self._render_lobby(initial_lobby)
        self._poll()

    def _poll(self):
        lobby = self.pm.duel_get(self.lobby_id)
        if lobby:
            self._render_lobby(lobby)
            if lobby.get("status") == "playing":
                if self._poll_id: self.after_cancel(self._poll_id)
                my_role = (lobby["host_role"] if self._my_user == lobby["host"]
                           else lobby.get("guest_role", "player"))
                self.on_start(self.lobby_id, my_role)
                return
        self._poll_id = self.after(800, self._poll)

    def _render_lobby(self, lobby):
        for w in self._players_frame.winfo_children(): w.destroy()
        my_user = self._my_user
        # If we are the guest, inject ourselves into the lobby data so we
        # always appear in slot 2 even if the server hasn't echoed us back yet
        guest_name = lobby.get("guest") or (my_user if not self.is_host else None)
        guest_role = lobby.get("guest_role") or "player"
        for col, (uname, role) in enumerate([
            (lobby["host"],  lobby["host_role"]),
            (guest_name,     guest_role),
        ]):
            pf = ctk.CTkFrame(self._players_frame, fg_color=C["bg3"], corner_radius=10)
            pf.grid(row=0, column=col, padx=12, pady=4, sticky="nsew")
            pf.columnconfigure(0, weight=1)
            label = "HOST" if col == 0 else "GUEST"
            ctk.CTkLabel(pf, text=label, font=_font(10), text_color=C["grey"]).grid(row=0, column=0, pady=(10,0))
            ctk.CTkLabel(pf, text=uname or "Waiting…", font=_font(16, "bold"),
                         text_color=C["text"]).grid(row=1, column=0, pady=2)
            role_clr = C["danger"] if role == "tung" else C["teal"]
            ctk.CTkLabel(pf, text=role.upper() if role else "—",
                         font=_font(13, "bold"), text_color=role_clr).grid(row=2, column=0, pady=2)
            if uname == my_user and uname:
                btns = ctk.CTkFrame(pf, fg_color="transparent")
                btns.grid(row=3, column=0, pady=(4,10))
                for r, clr in [("PLAYER", C["teal"]), ("TUNG", C["danger"])]:
                    ctk.CTkButton(btns, text=r, font=_font(11, "bold"),
                                  fg_color=clr if role == r.lower() else C["bg2"],
                                  hover_color=C["btn_hover"], text_color="white",
                                  width=80, height=30, corner_radius=6,
                                  command=lambda r=r: self._set_role(r.lower())).pack(side="left", padx=3)
        # Enable start if both present and roles set
        has_guest = bool(lobby.get("guest"))
        if self.is_host:
            state = "normal" if has_guest else "disabled"
            self._start_btn.configure(state=state)
        self._status_lbl.configure(
            text="Both players connected! Host can start." if has_guest
            else "Waiting for opponent to join…")

    def _set_role(self, role):
        ok, _ = self.pm.duel_set_role(self.lobby_id, role)
        if ok:
            lobby = self.pm.duel_get(self.lobby_id)
            if lobby: self._render_lobby(lobby)

    def _start(self):
        if self.pm.duel_start(self.lobby_id):
            lobby = self.pm.duel_get(self.lobby_id)
            if lobby:
                my_role = (lobby["host_role"] if self._my_user == lobby["host"]
                           else lobby.get("guest_role", "player"))
                if self._poll_id: self.after_cancel(self._poll_id)
                self.on_start(self.lobby_id, my_role)


# ── DuelNetSync — background thread for network I/O during duel ──────
import threading as _threading

class DuelNetSync:
    """Runs network calls on a background thread to avoid blocking the game loop."""
    def __init__(self, pm, lobby_id, role):
        self._pm       = pm
        self._id       = lobby_id
        self._role     = role          # "player" or "tung"
        self._lock     = _threading.Lock()
        self._state    = None          # latest game state (tung reads this)
        self._inp      = {"left": False, "right": False, "jump": False}
        self._pending_state = None     # player sets this to push
        self._pending_inp   = None     # tung sets this to push
        self._running  = True
        t = _threading.Thread(target=self._loop, daemon=True)
        t.start()

    def push_state(self, s):
        with self._lock: self._pending_state = dict(s)

    def push_input(self, inp):
        with self._lock: self._pending_inp = dict(inp)

    def get_state(self):
        with self._lock: return self._state

    def get_input(self):
        with self._lock: return dict(self._inp)

    def stop(self):
        self._running = False

    def _loop(self):
        import time as _time
        while self._running:
            try:
                if self._role == "player":
                    with self._lock:
                        s = self._pending_state; self._pending_state = None
                    if s: self._pm.duel_push_state(self._id, s)
                    inp = self._pm.duel_get_input(self._id)
                    with self._lock: self._inp = inp or self._inp
                else:
                    with self._lock:
                        inp = self._pending_inp; self._pending_inp = None
                    if inp: self._pm.duel_push_input(self._id, inp)
                    st = self._pm.duel_get_state(self._id)
                    if st:
                        with self._lock: self._state = st
            except Exception:
                pass
            _time.sleep(0.033)


class FriendsFrame(ctk.CTkFrame):
    """Friends list — view friends, send/accept/decline requests."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.columnconfigure(0, weight=1)
        for r in range(16): self.rowconfigure(r, weight=1)
        _rule(self, C["teal"], row=0)
        ctk.CTkLabel(self, text="FRIENDS", font=_font(44, "bold"),
                     text_color=C["teal"]).grid(row=1, column=0, pady=(24, 4))
        add_row = ctk.CTkFrame(self, fg_color="transparent")
        add_row.grid(row=2, column=0, pady=(4, 6))
        self._add_entry = ctk.CTkEntry(add_row, placeholder_text="Enter username…",
                                       width=240, height=38, font=_font(13),
                                       fg_color=C["entry_bg"], border_color=C["teal"], border_width=1)
        self._add_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(add_row, text="ADD FRIEND", font=_font(13, "bold"),
                      fg_color=C["teal"], hover_color="#009980", text_color=C["bg"],
                      width=130, height=38, corner_radius=8,
                      command=self._send_request).pack(side="left")
        self._status_lbl = ctk.CTkLabel(self, text="", font=_font(11), text_color=C["gold"])
        self._status_lbl.grid(row=3, column=0)
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=360)
        self._scroll.grid(row=4, column=0, padx=60, sticky="ew")
        self._scroll.columnconfigure(0, weight=1)
        _btn_ghost(self, "BACK", on_back, width=180).grid(row=5, column=0, pady=10)
        _rule(self, C["pink"], height=2, row=15)
        self._refresh()

    def _refresh(self):
        for w in self._scroll.winfo_children(): w.destroy()
        data = self.pm.get_friends()
        row = 0
        if data.get("received"):
            ctk.CTkLabel(self._scroll, text="FRIEND REQUESTS", font=_font(12, "bold"),
                         text_color=C["gold"]).grid(row=row, column=0, sticky="w", pady=(8,2))
            row += 1
            for u in data["received"]: self._request_row(row, u); row += 1
        friends = data.get("friends", [])
        lbl = f"FRIENDS ({len(friends)})" if friends else "No friends yet — add one above!"
        ctk.CTkLabel(self._scroll, text=lbl, font=_font(12, "bold"),
                     text_color=C["teal"]).grid(row=row, column=0, sticky="w", pady=(10,2))
        row += 1
        for entry in friends: self._friend_row(row, entry); row += 1
        if data.get("sent"):
            ctk.CTkLabel(self._scroll, text="PENDING (SENT)", font=_font(12, "bold"),
                         text_color=C["grey"]).grid(row=row, column=0, sticky="w", pady=(10,2))
            row += 1
            for u in data["sent"]:
                f = ctk.CTkFrame(self._scroll, fg_color=C["bg2"], corner_radius=8)
                f.grid(row=row, column=0, sticky="ew", pady=2); row += 1
                f.columnconfigure(1, weight=1)
                ctk.CTkLabel(f, text="⏳", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
                ctk.CTkLabel(f, text=u, font=_font(14), text_color=C["grey"]).grid(row=0, column=1, sticky="w")
                ctk.CTkLabel(f, text="Waiting…", font=_font(11), text_color=C["grey"]).grid(row=0, column=2, padx=12)

    def _friend_row(self, row, entry):
        u  = entry["username"] if isinstance(entry, dict) else entry
        hs = entry.get("highScore", 0) if isinstance(entry, dict) else 0
        f  = ctk.CTkFrame(self._scroll, fg_color=C["bg3"], corner_radius=8)
        f.grid(row=row, column=0, sticky="ew", pady=2)
        f.columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="👤", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
        ctk.CTkLabel(f, text=u, font=_font(14, "bold"), text_color=C["text"]).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(f, text=f"🏆 {hs:,}", font=_font(12), text_color=C["pink"]).grid(row=0, column=2, padx=8)
        ctk.CTkButton(f, text="REMOVE", font=_font(10), fg_color="transparent",
                      hover_color=C["btn_hover"], text_color=C["danger"],
                      border_width=1, border_color=C["danger"], width=70, height=26, corner_radius=5,
                      command=lambda u=u: self._remove(u)).grid(row=0, column=3, padx=8)

    def _request_row(self, row, username):
        f = ctk.CTkFrame(self._scroll, fg_color=C["bg2"], corner_radius=8)
        f.grid(row=row, column=0, sticky="ew", pady=2)
        f.columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text="📨", font=_font(14)).grid(row=0, column=0, padx=(12,6), pady=8)
        ctk.CTkLabel(f, text=username, font=_font(14), text_color=C["gold"]).grid(row=0, column=1, sticky="w")
        ctk.CTkButton(f, text="ACCEPT", font=_font(10, "bold"), fg_color=C["teal"],
                      hover_color="#009980", text_color=C["bg"], width=74, height=26, corner_radius=5,
                      command=lambda u=username: self._accept(u)).grid(row=0, column=2, padx=4)
        ctk.CTkButton(f, text="DECLINE", font=_font(10), fg_color="transparent",
                      hover_color=C["btn_hover"], text_color=C["danger"],
                      border_width=1, border_color=C["danger"], width=74, height=26, corner_radius=5,
                      command=lambda u=username: self._decline(u)).grid(row=0, column=3, padx=(0,8))

    def _send_request(self):
        target = self._add_entry.get().strip().lower()
        if not target: return
        ok, msg = self.pm.send_friend_request(target)
        self._add_entry.delete(0, "end")
        if ok:
            self._status_lbl.configure(text=f"✓ Request sent to {target}!", text_color=C["teal"])
        else:
            self._status_lbl.configure(text=f"✗ {msg}", text_color=C["danger"])
        self.after(3000, lambda: self._status_lbl.configure(text=""))
        self._refresh()

    def _accept(self, u): self.pm.accept_friend(u); self._refresh()
    def _decline(self, u): self.pm.decline_friend(u); self._refresh()
    def _remove(self, u): self.pm.remove_friend(u); self._refresh()


class MessagesFrame(ctk.CTkFrame):
    """DM system — friends list on left, chat on right."""
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self._other = None
        self._poll_id = None
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        for r in range(20): self.rowconfigure(r, weight=1)
        _rule(self, C["purple"], row=0)
        ctk.CTkLabel(self, text="MESSAGES", font=_font(36, "bold"),
                     text_color=C["purple"]).grid(row=1, column=0, columnspan=2, pady=(18, 4))

        # Left: friend list
        lf = ctk.CTkFrame(self, fg_color=C["bg2"], corner_radius=10)
        lf.grid(row=2, column=0, rowspan=16, padx=(40,8), pady=8, sticky="nsew")
        lf.columnconfigure(0, weight=1)
        ctk.CTkLabel(lf, text="FRIENDS", font=_font(12, "bold"),
                     text_color=C["grey"]).grid(row=0, column=0, pady=(10,4), padx=12, sticky="w")
        self._friend_list = ctk.CTkScrollableFrame(lf, fg_color="transparent", width=160, height=320)
        self._friend_list.grid(row=1, column=0, padx=4, pady=4)
        self._friend_list.columnconfigure(0, weight=1)
        self._populate_friends()

        # Right: chat area
        self._chat_area = ctk.CTkScrollableFrame(self, fg_color=C["bg3"],
                                                  corner_radius=10, height=340)
        self._chat_area.grid(row=2, column=1, rowspan=14, padx=(8,40), pady=8, sticky="nsew")
        self._chat_area.columnconfigure(0, weight=1)
        self._empty_lbl = ctk.CTkLabel(self._chat_area,
                                        text="Select a friend to start chatting",
                                        font=_font(13), text_color=C["grey"])
        self._empty_lbl.grid(row=0, column=0, pady=40)

        # Input row
        inp_row = ctk.CTkFrame(self, fg_color="transparent")
        inp_row.grid(row=16, column=1, padx=(8,40), pady=(0,6), sticky="ew")
        inp_row.columnconfigure(0, weight=1)
        self._msg_entry = ctk.CTkEntry(inp_row, placeholder_text="Type a message…",
                                       height=40, font=_font(13), fg_color=C["entry_bg"],
                                       border_color=C["purple"], border_width=1)
        self._msg_entry.grid(row=0, column=0, padx=(0,8), sticky="ew")
        self._msg_entry.bind("<Return>", lambda e: self._send())
        ctk.CTkButton(inp_row, text="SEND", font=_font(13, "bold"),
                      fg_color=C["purple"], hover_color="#7010b0", text_color="white",
                      width=80, height=40, corner_radius=8,
                      command=self._send).grid(row=0, column=1)

        _btn_ghost(self, "BACK", on_back, width=160).grid(row=17, column=0, columnspan=2, pady=8)

    def _populate_friends(self):
        for w in self._friend_list.winfo_children(): w.destroy()
        data = self.pm.get_friends()
        for i, entry in enumerate(data.get("friends", [])):
            u = entry["username"] if isinstance(entry, dict) else entry
            bg = C["equipped"] if u == self._other else C["bg3"]
            btn = ctk.CTkButton(self._friend_list, text=u, font=_font(12),
                                 fg_color=bg, hover_color=C["btn_hover"],
                                 text_color=C["text"], anchor="w",
                                 width=150, height=34, corner_radius=6,
                                 command=lambda u=u: self._open_chat(u))
            btn.grid(row=i, column=0, pady=2, padx=4, sticky="ew")

    def _open_chat(self, username):
        self._other = username
        self._populate_friends()
        if self._poll_id:
            self.after_cancel(self._poll_id)
        self._load_messages()

    def _load_messages(self):
        if not self._other: return
        for w in self._chat_area.winfo_children(): w.destroy()
        msgs = self.pm.get_messages(self._other)
        if not msgs:
            ctk.CTkLabel(self._chat_area, text="No messages yet — say hi!",
                         font=_font(12), text_color=C["grey"]).grid(row=0, column=0, pady=20)
        for i, m in enumerate(msgs):
            is_me = m.get("from") == self.pm.current_user
            align = "e" if is_me else "w"
            clr   = C["teal"] if is_me else C["text"]
            bg    = C["equipped"] if is_me else C["bg2"]
            bubble = ctk.CTkFrame(self._chat_area, fg_color=bg, corner_radius=10)
            bubble.grid(row=i, column=0, sticky=align, padx=12, pady=2)
            ctk.CTkLabel(bubble, text=m.get("text",""), font=_font(13),
                         text_color=clr, wraplength=320).pack(padx=12, pady=6)
        # Auto-poll every 3s
        self._poll_id = self.after(3000, self._load_messages)

    def _send(self):
        if not self._other: return
        text = self._msg_entry.get().strip()
        if not text: return
        ok, err_msg = self.pm.send_message(self._other, text)
        if ok:
            self._msg_entry.delete(0, "end")
            self._load_messages()
        else:
            self._msg_entry.delete(0, "end")
            self._msg_entry.configure(placeholder_text=f"Error: {err_msg}")


class DuelFrame(ctk.CTkFrame):
    """Create or join a duel lobby."""
    def __init__(self, parent, pm, on_back, on_lobby):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.on_lobby = on_lobby
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="DUELS", font=_font(50, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(28, 4))
        ctk.CTkLabel(self, text="Challenge a friend — one plays as Tung!",
                     font=_font(14), text_color=C["grey"]).grid(row=2, column=0, pady=(0, 16))

        # Create lobby
        cf = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=12)
        cf.grid(row=3, column=0, padx=160, pady=8, sticky="ew")
        cf.columnconfigure(0, weight=1)
        ctk.CTkLabel(cf, text="CREATE LOBBY", font=_font(18, "bold"),
                     text_color=C["teal"]).grid(row=0, column=0, pady=(16,4))
        ctk.CTkLabel(cf, text="Share the code with a friend to start a duel.",
                     font=_font(12), text_color=C["grey"]).grid(row=1, column=0, pady=(0,10))
        ctk.CTkButton(cf, text="CREATE", font=_font(15, "bold"),
                      fg_color=C["teal"], hover_color="#009980", text_color=C["bg"],
                      width=200, height=44, corner_radius=8,
                      command=self._create).grid(row=2, column=0, pady=(0,16))

        # Join lobby
        jf = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=12)
        jf.grid(row=4, column=0, padx=160, pady=8, sticky="ew")
        jf.columnconfigure(0, weight=1)
        ctk.CTkLabel(jf, text="JOIN LOBBY", font=_font(18, "bold"),
                     text_color=C["gold"]).grid(row=0, column=0, pady=(16,4))
        self._code_entry = ctk.CTkEntry(jf, placeholder_text="Enter lobby code…",
                                        width=220, height=40, font=_font(14),
                                        fg_color=C["entry_bg"], border_color=C["gold"], border_width=1)
        self._code_entry.grid(row=1, column=0, pady=4)
        ctk.CTkButton(jf, text="JOIN", font=_font(15, "bold"),
                      fg_color=C["gold"], hover_color="#ccaa00", text_color=C["bg"],
                      width=200, height=44, corner_radius=8,
                      command=self._join).grid(row=2, column=0, pady=(4,16))

        self._err_lbl = ctk.CTkLabel(self, text="", font=_font(11), text_color=C["danger"])
        self._err_lbl.grid(row=5, column=0)
        _btn_ghost(self, "BACK", on_back, width=180).grid(row=6, column=0, pady=8)
        _rule(self, C["purple"], height=2, row=13)

    def _create(self):
        lobby_id = self.pm.duel_create()
        if lobby_id:
            self.on_lobby(lobby_id, is_host=True)
        else:
            self._err_lbl.configure(text="Could not create lobby — are you online?")

    def _join(self):
        code = self._code_entry.get().strip().lower()
        if not code:
            self._err_lbl.configure(text="Enter a lobby code first.")
            return
        lobby = self.pm.duel_join(code)
        if lobby:
            # Override server default role — let guest choose explicitly
            self.pm.duel_set_role(code, "player")
            self.on_lobby(code, is_host=False, initial_lobby=lobby)
        else:
            self._err_lbl.configure(text="Lobby not found or full.")


class DuelLobbyFrame(ctk.CTkFrame):
    """Waiting room — choose roles, start when both ready."""
    def __init__(self, parent, pm, lobby_id, is_host, on_back, on_start, initial_lobby=None):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.pm = pm
        self.lobby_id = lobby_id
        self.is_host  = is_host
        self.on_start = on_start
        self._poll_id = None
        self._my_user = pm.current_user  # cache so guest can always find themselves
        self.columnconfigure(0, weight=1)
        for r in range(16): self.rowconfigure(r, weight=1)
        _rule(self, C["pink"], row=0)
        ctk.CTkLabel(self, text="DUEL LOBBY", font=_font(44, "bold"),
                     text_color=C["pink"]).grid(row=1, column=0, pady=(24, 2))

        # Code display
        code_f = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=10)
        code_f.grid(row=2, column=0, padx=300, pady=4, sticky="ew")
        ctk.CTkLabel(code_f, text="LOBBY CODE", font=_font(10), text_color=C["grey"]).pack(pady=(8,0))
        ctk.CTkLabel(code_f, text=lobby_id.upper(), font=_font(28, "bold"),
                     text_color=C["teal"]).pack(pady=(0,8))

        # Players panel
        self._players_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._players_frame.grid(row=3, column=0, padx=80, pady=8, sticky="ew")
        self._players_frame.columnconfigure((0,1), weight=1)

        self._status_lbl = ctk.CTkLabel(self, text="Waiting for opponent…",
                                         font=_font(13), text_color=C["grey"])
        self._status_lbl.grid(row=4, column=0, pady=4)

        self._start_btn = ctk.CTkButton(self, text="START DUEL", font=_font(17, "bold"),
                                         fg_color=C["pink"], hover_color="#cc0055",
                                         text_color="white", width=220, height=50,
                                         corner_radius=10, command=self._start,
                                         state="disabled")
        if is_host:
            self._start_btn.grid(row=5, column=0, pady=8)

        _btn_ghost(self, "LEAVE", on_back, width=180, border_color=C["danger"]).grid(row=6, column=0, pady=4)
        _rule(self, C["purple"], height=2, row=15)
        # Render initial lobby immediately (avoids blank flash on join)
        if initial_lobby:
            self._render_lobby(initial_lobby)
        self._poll()

    def _poll(self):
        lobby = self.pm.duel_get(self.lobby_id)
        if lobby:
            self._render_lobby(lobby)
            if lobby.get("status") == "playing":
                if self._poll_id: self.after_cancel(self._poll_id)
                my_role = (lobby["host_role"] if self._my_user == lobby["host"]
                           else lobby.get("guest_role", "player"))
                self.on_start(self.lobby_id, my_role)
                return
        self._poll_id = self.after(800, self._poll)

    def _render_lobby(self, lobby):
        for w in self._players_frame.winfo_children(): w.destroy()
        my_user = self._my_user
        # If we are the guest, inject ourselves into the lobby data so we
        # always appear in slot 2 even if the server hasn't echoed us back yet
        guest_name = lobby.get("guest") or (my_user if not self.is_host else None)
        guest_role = lobby.get("guest_role") or "player"
        for col, (uname, role) in enumerate([
            (lobby["host"],  lobby["host_role"]),
            (guest_name,     guest_role),
        ]):
            pf = ctk.CTkFrame(self._players_frame, fg_color=C["bg3"], corner_radius=10)
            pf.grid(row=0, column=col, padx=12, pady=4, sticky="nsew")
            pf.columnconfigure(0, weight=1)
            label = "HOST" if col == 0 else "GUEST"
            ctk.CTkLabel(pf, text=label, font=_font(10), text_color=C["grey"]).grid(row=0, column=0, pady=(10,0))
            ctk.CTkLabel(pf, text=uname or "Waiting…", font=_font(16, "bold"),
                         text_color=C["text"]).grid(row=1, column=0, pady=2)
            role_clr = C["danger"] if role == "tung" else C["teal"]
            ctk.CTkLabel(pf, text=role.upper() if role else "—",
                         font=_font(13, "bold"), text_color=role_clr).grid(row=2, column=0, pady=2)
            if uname == my_user and uname:
                btns = ctk.CTkFrame(pf, fg_color="transparent")
                btns.grid(row=3, column=0, pady=(4,10))
                for r, clr in [("PLAYER", C["teal"]), ("TUNG", C["danger"])]:
                    ctk.CTkButton(btns, text=r, font=_font(11, "bold"),
                                  fg_color=clr if role == r.lower() else C["bg2"],
                                  hover_color=C["btn_hover"], text_color="white",
                                  width=80, height=30, corner_radius=6,
                                  command=lambda r=r: self._set_role(r.lower())).pack(side="left", padx=3)
        # Enable start if both present and roles set
        has_guest = bool(lobby.get("guest"))
        if self.is_host:
            state = "normal" if has_guest else "disabled"
            self._start_btn.configure(state=state)
        self._status_lbl.configure(
            text="Both players connected! Host can start." if has_guest
            else "Waiting for opponent to join…")

    def _set_role(self, role):
        ok, _ = self.pm.duel_set_role(self.lobby_id, role)
        if ok:
            lobby = self.pm.duel_get(self.lobby_id)
            if lobby: self._render_lobby(lobby)

    def _start(self):
        if self.pm.duel_start(self.lobby_id):
            lobby = self.pm.duel_get(self.lobby_id)
            if lobby:
                my_role = (lobby["host_role"] if self._my_user == lobby["host"]
                           else lobby.get("guest_role", "player"))
                if self._poll_id: self.after_cancel(self._poll_id)
                self.on_start(self.lobby_id, my_role)

class LeaderboardFrame(ctk.CTkFrame):
    def __init__(self, parent, pm, on_back):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        _rule(self, C["purple"], row=0)
        ctk.CTkLabel(self, text="LEADERBOARD", font=_font(44, "bold"),
                     text_color=C["purple"]).grid(row=1, column=0, pady=(32, 4))
        ctk.CTkLabel(self, text="All-time best single-run scores", font=_font(13),
                     text_color=C["grey"]).grid(row=2, column=0, pady=(0, 12))
        sc = ctk.CTkScrollableFrame(self, fg_color=C["bg3"], corner_radius=12, height=350)
        sc.grid(row=3, column=0, padx=90, pady=6, sticky="ew")
        sc.columnconfigure((0, 1, 2, 3), weight=1)
        for ci, (hdr, clr) in enumerate([("#", C["grey"]), ("PLAYER", C["text"]),
                                          ("BEST", C["pink"]), ("TOTAL", C["gold"])]):
            ctk.CTkLabel(sc, text=hdr, font=_font(12, "bold"),
                         text_color=clr).grid(row=0, column=ci, padx=18, pady=(12, 4))
        medals = ["1st", "2nd", "3rd"]
        for rank, (name, hs, total) in enumerate(pm.leaderboard(), 1):
            clr   = [C["rank_gold"], C["rank_silv"], C["rank_bron"]][rank-1] if rank <= 3 else C["text"]
            mrk   = medals[rank-1] if rank <= 3 else str(rank)
            is_me = name == pm.current_user
            ctk.CTkLabel(sc, text=mrk, font=_font(15, "bold"),
                         text_color=clr).grid(row=rank, column=0, padx=18, pady=4)
            ctk.CTkLabel(sc, text=name + (" ◀" if is_me else ""),
                         font=_font(15, "bold"),
                         text_color=C["teal"] if is_me else clr).grid(
                             row=rank, column=1, padx=18, pady=4)
            ctk.CTkLabel(sc, text=f"{hs:,}", font=_font(15),
                         text_color=C["pink"]).grid(row=rank, column=2, padx=18, pady=4)
            ctk.CTkLabel(sc, text=f"{total:,}", font=_font(13),
                         text_color=C["gold"]).grid(row=rank, column=3, padx=18, pady=4)
        if not pm.leaderboard():
            ctk.CTkLabel(sc, text="No scores yet — play a game!", font=_font(14),
                         text_color=C["grey"]).grid(row=1, column=0, columnspan=4, pady=30)
        _btn_ghost(self, "BACK", on_back, width=180).grid(row=4, column=0, pady=16)
        _rule(self, C["pink"], height=2, row=13)


class GameOverFrame(ctk.CTkFrame):
    def __init__(self, parent, score, coins, dist, xp_earned, pm, on_restart, on_menu):
        super().__init__(parent, fg_color=C["bg"], corner_radius=0)
        self.columnconfigure(0, weight=1)
        for r in range(14): self.rowconfigure(r, weight=1)
        rec    = pm.current()
        new_hs = score >= rec["high_score"] and score > 0
        _rule(self, C["danger"], row=0)
        ctk.CTkLabel(self, text="C A U G H T.", font=_font(60, "bold"),
                     text_color=C["danger"]).grid(row=1, column=0, pady=(32, 4))
        ctk.CTkLabel(self, text="TUNG TUNG SAHUR GOT YOU.", font=_font(17),
                     text_color=C["pink"]).grid(row=2, column=0, pady=(0, 16))

        pnl = ctk.CTkFrame(self, fg_color=C["bg3"], corner_radius=12)
        pnl.grid(row=3, column=0, padx=70, pady=6, sticky="ew")
        pnl.columnconfigure((0, 1, 2, 3, 4), weight=1)
        for col, (lbl, val, clr) in enumerate([
            ("SCORE",       f"{score:,}",     C["pink"]),
            ("COINS EARNED",str(coins),       C["gold"]),
            ("DISTANCE",    f"{dist} m",      C["teal"]),
            ("BATTLE XP",   f"+{xp_earned}",  C["purple"]),
            ("WALLET",      str(rec["coins"]), C["grey"]),
        ]):
            ctk.CTkLabel(pnl, text=lbl, font=_font(10),
                         text_color=C["grey"]).grid(row=0, column=col, padx=16, pady=(16, 4))
            ctk.CTkLabel(pnl, text=val, font=_font(22, "bold"),
                         text_color=clr).grid(row=1, column=col, padx=16, pady=(0, 16))

        ctk.CTkLabel(self,
            text="NEW HIGH SCORE!" if new_hs else f"High Score:  {rec['high_score']:,}",
            font=_font(16, "bold"),
            text_color=C["gold"] if new_hs else C["grey"]).grid(row=4, column=0, pady=10)

        _btn_primary(self, "PLAY AGAIN", on_restart).grid(row=5, column=0, pady=8)
        _btn_ghost(self, "MAIN MENU", on_menu, width=180).grid(row=6, column=0, pady=6)
        _rule(self, C["purple"], height=2, row=13)


# ══════════════════════════════════════════════════════════════════════
#  APP
# ══════════════════════════════════════════════════════════════════════
def run_duel_as_tung(duel_sync):
    """Game loop for the Tung player — renders server state, sends inputs."""
    pygame.init()
    pygame.display.set_caption("Tung Tung Sahur — YOU ARE TUNG!")
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock  = pygame.time.Clock()
    assets = _load_assets()
    font_big = assets["font_lg"]
    font_sm  = assets["font_sm"]
    _last_inp  = 0.0
    state      = None
    prev_jump  = False
    jump_until = 0.0   # keeps jump=True for 150ms so the network thread reliably picks it up

    hint_surf = font_sm.render("A/D = move   W/SPACE = jump   Catch the player!", True, (180,160,220))

    while True:
        dt  = min(clock.tick(60) / 1000.0, 0.05)
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return -99, 0, 0

        keys = pygame.key.get_pressed()
        jump_now = keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]
        # Sticky jump: on a new press, hold jump=True for 150ms so the
        # network thread (running every 33ms) is guaranteed to catch it
        if jump_now and not prev_jump:
            jump_until = now + 0.15
        prev_jump = jump_now

        inp = {
            "left":  bool(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            "right": bool(keys[pygame.K_d] or keys[pygame.K_RIGHT]),
            "jump":  now < jump_until,
        }

        if now - _last_inp > 0.033:
            duel_sync.push_input(inp)
            _last_inp = now

        new_state = duel_sync.get_state()
        if new_state: state = new_state

        # Check game over
        if state and state.get("dead"):
            pygame.quit()
            return -2, 0, 0  # tung wins
        if state and state.get("tung_won"):
            pygame.quit()
            return -1, 0, 0  # player wins (shouldn't happen on tung client)

        # ── Render ──────────────────────────────────────────────────
        screen.fill(PG["bg"])
        # Stars (static)
        for i in range(0, WIN_W, 60):
            for j in range(0, WIN_H, 60):
                if (i * 31 + j * 17) % 13 == 0:
                    pygame.draw.circle(screen, PG["star1"], (i,j), 1)

        if state:
            # Ground
            pygame.draw.rect(screen, PG["ground"], (0, GROUND_Y, WIN_W, WIN_H - GROUND_Y))
            pygame.draw.line(screen, PG["gnd_top"], (0, GROUND_Y), (WIN_W, GROUND_Y), 3)

            # Platforms
            for (sx, py, hw, is_temp) in state.get("plats", []):
                clr = PG["t_plat"] if is_temp else PG["plat"]
                r = pygame.Rect(int(sx), int(py), int(hw * 2), 14)
                pygame.draw.rect(screen, clr, r, border_radius=4)
                pygame.draw.rect(screen, PG["gnd_top"], pygame.Rect(r.x, r.y, r.width, 3), border_radius=2)

            # Player
            p_y   = int(state["p_y"])
            p_rect = pygame.Rect(PLAYER_SX, p_y, PLAYER_W, PLAYER_H)
            pygame.draw.rect(screen, PG["player"], p_rect, border_radius=5)

            # Tung
            tsx = int(state["tung_sx"])
            tsy = int(state["tung_y"])
            if "tung" in assets:
                screen.blit(assets["tung"], (tsx - TUNG_W // 2, tsy))
            else:
                pygame.draw.rect(screen, PG["tung"],
                                 (tsx - TUNG_W // 2, tsy, TUNG_W, TUNG_H), border_radius=6)
            # YOU ARE HERE arrow
            arrow_surf = font_sm.render("▼ YOU", True, PG["danger"])
            screen.blit(arrow_surf, (tsx - arrow_surf.get_width()//2, tsy - 24))

            # HUD
            pygame.draw.rect(screen, PG["hud_bg"], (0, PLAY_H, WIN_W, HUD_H))
            pygame.draw.line(screen, PG["gnd_top"], (0, PLAY_H), (WIN_W, PLAY_H), 2)
            score_s = font_sm.render(f"Player score: {int(state.get('score',0)):,}", True, PG["pink"])
            screen.blit(score_s, (18, PLAY_H + 10))
            screen.blit(hint_surf, (WIN_W//2 - hint_surf.get_width()//2, PLAY_H + 10))
        else:
            # Waiting for game state
            wait_s = font_big.render("Waiting for game to start…", True, PG["teal"])
            screen.blit(wait_s, (WIN_W//2 - wait_s.get_width()//2, WIN_H//2 - 20))

        pygame.display.flip()



class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tung Tung Sahur - RUN!")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color=C["bg"])
        self.pm   = PlayerManager()
        self._fr  = None
        self.bind("<<BPRefresh>>", lambda e: self._show_bp())
        self.show_login()

    def _set(self, frame):
        if self._fr: self._fr.destroy()
        frame.pack(fill="both", expand=True)
        self._fr = frame

    def show_login(self):
        self._set(LoginFrame(self, self.pm,
                             on_success=self.show_main_menu,
                             on_signup=self.show_signup,
                             on_quit=self.quit))

    def show_signup(self):
        self._set(SignupFrame(self, self.pm,
                              on_success=self.show_main_menu,
                              on_back=self.show_login))

    def show_main_menu(self):
        self.pm._load()
        self._set(MainMenuFrame(self, self.pm,
                                on_play=self._start_game,
                                on_shop=self._show_shop,
                                on_locker=self._show_locker,
                                on_bp=self._show_bp,
                                on_lb=self._show_lb,
                                on_friends=self._show_friends,
                                on_messages=self._show_messages,
                                on_duel=self._show_duel,
                                on_logout=self._logout,
                                on_quit=self.quit))

    def _show_shop(self):
        self._set(ShopFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_locker(self):
        self._set(LockerFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_bp(self):
        self._set(BattlePassFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_lb(self):
        self._set(LeaderboardFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_friends(self):
        self._set(FriendsFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_messages(self):
        self._set(MessagesFrame(self, self.pm, on_back=self.show_main_menu))

    def _show_duel(self):
        self._set(DuelFrame(self, self.pm,
                            on_back=self.show_main_menu,
                            on_lobby=self._show_duel_lobby))

    def _show_duel_lobby(self, lobby_id, is_host, initial_lobby=None):
        self._set(DuelLobbyFrame(self, self.pm, lobby_id, is_host,
                                 on_back=self._show_duel,
                                 on_start=self._start_duel,
                                 initial_lobby=initial_lobby))

    def _start_duel(self, lobby_id, role):
        if self._fr: self._fr.destroy(); self._fr = None
        self.after(80, lambda: self._run_duel(lobby_id, role))

    def _run_duel(self, lobby_id, role):
        self.withdraw()
        try:
            rec = self.pm.current()
            wpn = rec.get("current_weapon", "none")
            abl = rec.get("current_ability", "slam")
            skn = rec.get("current_skin", "default")
            sync = DuelNetSync(self.pm, lobby_id, role)
            if role == "player":
                score, coins, dist = run_pygame_game(wpn, abl, skn, duel_sync=sync)
            else:
                score, coins, dist = run_duel_as_tung(sync)
            sync.stop()
        finally:
            self.deiconify()
        import customtkinter as _ctk
        over_f = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        over_f.pack(fill="both", expand=True)
        if self._fr: self._fr.destroy()
        self._fr = over_f
        over_f.columnconfigure(0, weight=1)
        winner_txt = "YOU WIN! 🏆" if score == -1 else "TUNG WINS! 💀" if score == -2 else f"Score: {score:,}"
        clr = C["teal"] if score == -1 else C["danger"] if score == -2 else C["pink"]
        ctk.CTkLabel(over_f, text="DUEL OVER", font=_font(44, "bold"),
                     text_color=C["pink"]).pack(pady=(60,4))
        ctk.CTkLabel(over_f, text=winner_txt, font=_font(28, "bold"),
                     text_color=clr).pack(pady=8)
        ctk.CTkLabel(over_f, text="No coins or XP earned in duels.",
                     font=_font(12), text_color=C["grey"]).pack(pady=4)
        _btn_primary(over_f, "BACK TO MENU", self.show_main_menu).pack(pady=24)

    def _logout(self):
        self.pm.logout(); self.show_login()

    def _start_game(self):
        rec = self.pm.current()
        wpn = rec.get("current_weapon", "none")
        abl = rec.get("current_ability", "slam")
        skn = rec.get("current_skin", "default")
        if self._fr: self._fr.destroy(); self._fr = None
        self.after(80, lambda: self._run(wpn, abl, skn))

    def _run(self, wpn, abl, skn="default"):
        self.withdraw()
        try:
            lb = self.pm.leaderboard()
            rank1_user = lb[0][0] if lb else None
            is_rank1 = (rank1_user is not None and rank1_user == self.pm.current_user)
            score, coins, dist = run_pygame_game(wpn, abl, skn, is_rank1=is_rank1)
        finally:
            self.deiconify()
        xp_earned = self.pm.add_run_result(score, coins)
        self._set(GameOverFrame(self, score, coins, dist, xp_earned, self.pm,
                                on_restart=self._start_game,
                                on_menu=self.show_main_menu))


if __name__ == "__main__":
    app = App()
    app.mainloop()#!/usr/bin/env python3
