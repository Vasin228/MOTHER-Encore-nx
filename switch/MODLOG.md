# MOTHER: Encore — Nintendo Switch Port (`d:\Anti\mother-encore-nx`)

## Milestone Summary

| Date | Stage | Artifact / Target | Status |
|---|---|---|---|
| 2026-11-27 | Initial Switch Port v0.4.1.2 | `build/mother_encore.nro` + `build/mother_encore.pck` | Built & Pushed (`1713fa2`), Black Screen on Switch |
| 2026-11-27 | Case-Sensitivity Fix + File Logging | `build/mother_encore.nro` + `build/mother_encore.pck` | Pushed (`f4b4fe9`), FW 22.5.0 `2001-0132` Crash |
| 2026-11-27 | Godot 3.5.2 `libnx` 2026 Rebuild + Fast Boot | `build/mother_encore.nro` + `build/mother_encore.pck` | Booted on Switch (`0d48e3ae`), Ninten's House translations + slow boot reported |
| 2026-11-27 | Translation Fix + SD I/O + Precompiled Boot Data | `build/mother_encore.nro` + `build/mother_encore.pck` | Fixed Ninten's House translations (`919b92d`), Podunk outdoor low FPS reported |
| 2026-11-27 | Overworld FPS Fix (YSort Cull + TileMap + GDScript) | `build/mother_encore.nro` + `build/mother_encore.pck` | Pushed (`e1cded3`), still slow until dialogue (`godot.log` un-flushed) |
| 2026-11-27 | Physics2D / Stepping Sounds Fix + Flushed Telemetry | `build/mother_encore.nro` + `build/mother_encore.pck` | Built, Verified & Deployed to Switch (`SHA256 MATCH`) |

## Physics2D Collision Mask & Telemetry Flush Fix (2026-11-27)
- **Why Dialogue Ran at 60 FPS**: During dialogue, `Player` disables Layer 1/8 collision masks (`_set_collision_masks(false)`), skips `_move_state()`, and pauses enemies. Outdoors when unpaused, `Stepping Sounds` (`mask=1`, `31` large polygons including a 371-vert polygon) paired in `BroadPhase2DHashGrid` with all Layer-1 bodies, `Player` ran two `move_and_slide()` sweeps every tick even when idle, and `Jump Area` updated 14 raycasts unconditionally.
- **Fixes Applied**:
  - `switch/godot_switch_engine.patch` (`drivers/unix/file_access_unix.cpp`): restrict 64 KB `setvbuf` under `HORIZON_ENABLED` to `p_mode_flags == READ` so `godot.log` writes are never trapped in a 64 KB buffer before HOME exit.
  - `Scripts/Main/Stepping Sounds.gd` & `Scripts/Main/party/Player.gd`: set `collision_mask = 0` on `Stepping Sounds`, keep bit 11 enabled on `Player`, and skip `move_and_slide()` when `_velocity == Vector2.ZERO` / `_knockback == Vector2.ZERO`.
  - `Scripts/Main/Jump Area.gd` & `Scripts/misc/dandelion spawner.gd`: short-circuit `_get_ray_to_player()` when `!_is_player_nearby`, and fix inverted despawn check (`if _current_dandelion:`).
  - `Scripts/global/uiManager.gd`: 3s `[PERF]` `printerr()` (immediate flush) logging `paused`, `fps`, `nodes`, `items2d`, `draws`, `proc_ms`, `phys_ms`, `active2d`, `pairs2d`.

## Verified Build & Switch Deploy Outputs
- `mother_encore.nro`: `38,711,489` B, `SHA256 = 4C5B6581C7DC0B50C22E588FF9E689AAFC850C5D2F16CB70A5D9DABB453CF0F8` (`HTTP 201`, `SHA256 MATCH`)
- `mother_encore.pck`: `255,737,920` B, `SHA256 = 324A49EA7A007886E42D7AF43674066441E504110C1385FF09ED4A0D2958BCA1` (`HTTP 201`, `SHA256 MATCH`)

## Previous Stage — Overworld FPS Optimization (2026-11-27)
- **Engine (`switch/godot_switch_engine.patch`)**:
  - `servers/visual/visual_server_canvas.cpp`: culled off-screen leaf items & empty-child containers in `_collect_ysort_children()` BEFORE `SortArray::sort()`.
  - `scene/2d/tile_map.h` & `scene/2d/tile_map.cpp`: horizontal row batching (`quadrant_size` × `1`) for square non-vertical-half-offset `y_sort_mode` TileMaps (`Objects`, `YSort2`, `AbovePlayer3`, etc.).
- **GDScript (`src/`)**:
  - `SpriteDataFetcher.gd`: replaced per-frame `_process` `FloorReflector` lookup with `scene_changed` callback.
  - `character_sprite.gd`: dirty checks in `blend_position()` and `travel()`.
  - `npc.gd`: deferred `_init_offscreen_cull()` + disable off-screen `animationTree.active` and `$RayCast2D.enabled`.
  - `birds.gd`: stopped off-screen `$AnimationPlayer` ticks in `_ready()` and `screen_exited`.
  - `uiManager.gd`: Switch-only 5s `[PERF]` logger (`FPS`, `nodes`, `items2d`, `draws`, `proc_ms`, `phys_ms`).

## Verified Build & Switch Deploy Outputs
- `mother_encore.nro`: `38,711,489` B, `SHA256 = 8EEBDD8996D1F7146263287E07F3A2161E0C612F9C804BED88E16CFB0542CDA3` (`HTTP 201`, `SHA256 MATCH`)
- `mother_encore.pck`: `255,737,408` B, `SHA256 = EA005A03B6840AE2E61A781D935B1D636ABB1F736410F696CD035049462FDA90` (`HTTP 201`, `SHA256 MATCH`)

## Previous Stage — Translation Fix & Boot Acceleration (2026-11-27)
- **Root Cause of Missing Ninten's House Text (`DIALOGUE_PODUNK_NON-PERSON_TEXT_NINTEN_S_HOUSE_*`)**:
  - `project.godot` uses escaped apostrophes (`Ninten\'s house - sheet.<lang>.translation`), whereas `build/filter_translations.py` checked unescaped `fn in existing`, accidentally stripping all 12 `Ninten's house` translation files.
  - Restored all 12 `Ninten\'s house` entries (`total=386`, `kept=323`, `removed=63`; verified `en` & `ru` message resolution directly from `.pck`).
- **Switch SD I/O & Boot Speed Optimizations**:
  - `switch/godot_switch_engine.patch`: added 64 KB stdio buffer (`setvbuf` in `drivers/unix/file_access_unix.cpp`) and persistent-handle `FILE*` single-read `mem_buf` cache (`<= 262 KB`) in `core/io/file_access_pack.cpp` under `HORIZON_ENABLED`.
  - Precompiled the 304 boot YAML files into `Data/precompiled_boot_data.bin` (`189 KB`), updated `globalData.gd::_init()` (`8 ms` local), converted `SmartFileReader` in `yaml_parser.gd` to single-read text splitting, and deferred 12 non-boot `uiManager.gd` scenes via lazy getters (`uiManager._ready: 3885 ms` local).

## Verified Build & Switch Deploy Outputs
- `mother_encore.nro`: `38,711,489` B, `SHA256 = 5AF74F2CB5A194BEB1F6B4196E01D633773F3F318C48346FF4368C9F671BF1CD` (`HTTP 201`, `SHA256 MATCH`)
- `mother_encore.pck`: `255,735,296` B, `SHA256 = 226F139EADECFC3F4690A1B0D9792A50A15EE4BC4BE5CB7B6D43B8A55DF4C5D3` (`HTTP 201`, `SHA256 MATCH`)

## Previous Stage — Engine Rebuild & Startup Optimization (2026-11-27)
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
