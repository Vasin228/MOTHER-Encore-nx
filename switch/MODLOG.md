# MOTHER: Encore — Nintendo Switch Port (`d:\Anti\mother-encore-nx`)

## Milestone Summary

| Date | Stage | Artifact / Target | Status |
|---|---|---|---|
| 2026-11-27 | Initial Switch Port v0.4.1.2 | `build/mother_encore.nro` + `build/mother_encore.pck` | Built & Pushed (`1713fa2`), Black Screen on Switch |
| 2026-11-27 | Case-Sensitivity Fix + File Logging | `build/mother_encore.nro` + `build/mother_encore.pck` | Pushed (`f4b4fe9`), FW 22.5.0 `2001-0132` Crash |
| 2026-11-27 | Godot 3.5.2 `libnx` 2026 Rebuild + Fast Boot | `build/mother_encore.nro` + `build/mother_encore.pck` | Built, Verified & Deploying |

## Engine Rebuild & Startup Optimization (2026-11-27)
- **Root Cause of `2001-0132 (0x10801)` in `0100000000000013` (`hid`)**:
  - Prebuilt 2023 `switch_release.nro` used an outdated `libnx` ABI broken on Switch FW 22.5.0 (> 21.0.0 memory/service changes, `Stary2001/godot` #39), and `OS_Switch::run()` launched `swkbdInlineLaunchForLibraryApplet()` immediately after `main_loop->init()` (right when the title appeared).
- **Engine Rebuild (`Stary2001/godot` `3.5.2-stable_switch` + `devkitA64` 15.2.0 + `libnx` 2026-02-04)**:
  - Saved engine diff in `switch/godot_switch_engine.patch`:
    1. Disabled `swkbdInline` library applet & virtual keyboard hooks in `platform/switch/os_switch.cpp` (MOTHER: Encore uses its own in-game RPG naming grid).
    2. Added `R_FAILED(res)` checks and bounded the `audren` wait loop (`wait_tries >= 2000`) in `platform/switch/audio_driver_switch.cpp` (`Stary2001/godot` #40 Bluetooth audio hang fix).
  - Compiled `target=release tools=no` (`godot.switch.opt.64`) and packaged `build/mother_encore.nro` via `nacptool` + `elf2nro` with `icon_switch_256.jpg` and `applet_splash.rgba.gz`.
- **1–2 Minute Boot Freeze Fixes**:
  - `Scripts/global/uiManager.gd` + `Scripts/UI/Battle/BattleSystem.gd`: lazy-load the 50 `.bbg` battle backgrounds on demand on Switch instead of loading all 50 synchronously at startup.
  - `Scripts/global/cacheLoader.gd`: skipped unsafe background `Thread` (`add_child`/`yield` + `podunk.tscn` boot preload) on Switch, running only `_load_materials()` on main thread.
  - `project.godot`: removed 75 nonexistent `.translation` entries from `[locale]` (kept all 311 existing imported `.translation` files).
  - Local `.pck` smoke test: dropped from 412 error lines to 14 lines (`translation_errs=0`, `script_errs=0`).

## Verified Build Outputs (`build/`)
- `mother_encore.nro`: `38,695,105` B, `LastWriteTime = 2026-11-27 10:42:43`, `SHA256 = 2C328C9411D7E0CD87E4D521CCCA0B89B6289FD9C0ED686C9174B29F7748F28A`
- `mother_encore.pck`: `255,538,944` B, `LastWriteTime = 2026-11-27 10:33:09`, `SHA256 = C516D611C1AAF6650D9FC969DFF01376E2750E944922567E77D319E3B4323A97`

## Next Step
- Have user test launching `/switch/mother-encore/mother_encore.nro` via Title Override on Switch FW 22.5.0 and verify fast boot, title screen, audio, controls, and gameplay.
