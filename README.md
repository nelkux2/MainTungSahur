# Tung Tung Sahur — RUN!

## Playing the game

**Download `TungTungRun.exe` from the [Releases page](../../releases/latest) and double-click it.**

No Python to install. No dependencies. No command prompt. Just double-click.

---

### What happens on first launch

1. A small splash window appears (~5 seconds).
2. Game files are installed to `%APPDATA%\TungTungRun\` — no admin required.
3. Latest game code is downloaded from GitHub.
4. The game opens.

### Automatic updates

Every time you launch `TungTungRun.exe`:

| What | How |
|---|---|
| **Game scripts** (`evil.py`, `tung_online.py`) | Silently downloaded on every launch if GitHub has a newer version |
| **Launcher exe itself** | Checks GitHub Releases; self-replaces if a newer `.exe` is published |

---

## For developers

### Pushing a game update

Commit and push to `main`. GitHub Actions will:
1. Auto-build a new `TungTungRun.exe` (~3 minutes)
2. Publish it to GitHub Releases tagged with the version in `version.txt`
3. All existing launchers detect and apply the update on next launch

**To bump the version:** edit `version.txt` before pushing.

### Building locally (Windows)

```
python build_local.py
```

Output: `dist\TungTungRun.exe`

### Structure

```
evil.py                         core game engine  (auto-updated from GitHub)
tung_online.py                  online layer + entry point
launcher.py                     compiled into the exe  (rarely changes)
TungTungRun.spec                PyInstaller build config
build_local.py                  local Windows build helper
version.txt                     single version number e.g. 2.5.6
.github/workflows/
  build-release.yml             triggers auto-build + release on push
```

---

## Controls

`W`/`Space` jump · `A`/`D` lean · `S`+air slam · `E` platform · `F` weapon · `G` ability · `ESC` pause
