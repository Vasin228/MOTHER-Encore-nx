# MOTHER: Encore — Nintendo Switch Port (`d:\Anti\mother-encore-nx`)

## Milestone Summary

| Date | Stage | Artifact / Target | Status |
|---|---|---|---|
| 2026-11-27 | Initial Switch Port v0.4.1.2 | `build/mother_encore.nro` + `build/mother_encore.pck` | Built & Deployed |

## Build Environment & Source
- **Upstream Source**: `motherencore/MOTHER-Encore-Source-Code` (`main` @ `90ba526`, v0.4.1.2, Godot 3.x GLES2, pure GDScript, 6357 packed files).
- **Engine / Export Template**: `Stary2001/godot` `v3.5.1-stable_switch_fixed` (`godot.x11.opt.tools.64` in WSL + `switch_release.nro` / `switch_applet_splash.rgba.gz` in `~/.local/share/godot/templates/3.5.1.stable/`). Note: Windows editor `godot.windows.opt.tools.64.exe` failed on host with `0xC0000142`; Linux editor from the same release ran cleanly in WSL.

## Switch Compatibility Patches (`src/`)
- `project.godot`: set `config/use_custom_user_dir=true` and `config/custom_user_dir_name="mother-encore/userdata"` (`sdmc:/switch/mother-encore/userdata/`, avoiding FAT32-illegal `:` in `"MOTHER: Encore"`); swapped Joypad `ui_accept` (`button_index=1`, Switch A) and `ui_cancel` (`button_index=0`, Switch B).
- `Scripts/global/global.gd`: forced `globaldata.GAMEPAD` and `BtnStyles.NINTENDO` on Switch (`OS_Switch` reports `"pad0"`), guarded `toggle_fullscreen()` / `set_win_size()` / `_set_localized_default_inputs()`, added `_ensure_user_dir()` before `user://` writes (`os_switch.cpp` has `_ensure_user_data_dir()` commented out).
- `addons/integer_resolution_handler/integer_resolution_handler.gd`: skipped `OS.min_window_size` on Switch and pinned `video_mode = Vector2(1280, 720)` (exact 4x integer scale of `320x180`).
- `Scripts/UI/Options/OptionsUI.gd`: hid `OPTN_SETTINGS_RESOLUTION` and `OPTN_SETTINGS_FULLSCREEN` on Switch and clamped `_get_resolutions()` fallback to `["1280×720"]` (`OS.get_screen_size()` returns zero on `OS_Switch`).
- `Scripts/Main/AoOni.gd`: guarded `OS.shell_open(...)` on Switch.
- `Nodes/Ui/Inventory/ActionSelect.gd`: replaced post-3.5.1 `is_node_ready()` with `_is_ready` flag set in `_ready()` (eliminated the sole GDScript parse error).
- `icon_switch_256.jpg` & `export_presets.cfg`: generated 256x256 baseline RGB JPEG icon and added `[preset.10]` (`Nintendo Switch`, `application/fused_build=false`).
- Headless `.bbg` import (`build/import_bbgs.gd`, `extends MainLoop`): converted all 50 `Graphics/Battle BGS/*.bbg` backgrounds to `.import/*.bbg-*.scn` (`ok=50 fail=0`, smoke-tested via `load("res://Graphics/Battle BGS/antoid.bbg")`).

## Verified Build Outputs (`build/`)
- `mother_encore.nro`: `45,191,361` B, `LastWriteTime = 2026-11-27 10:03:59`, `SHA256 = 63996BE18939400488A8E79BA68039C440C838F48AF173808F0CB41911B3314D` (`NRO0` + `ASET` + `NACP` + baseline JPEG icon).
- `mother_encore.pck`: `255,545,152` B, `LastWriteTime = 2026-11-27 10:03:59`, `SHA256 = EFC30C0786F4AD4CF5DBF9B1BA48E90790F3874416747DF10145FD40069C7DEE` (`GDPC` v1, 6357 files, 0 `SCRIPT ERROR` / `Parse Error` / `.bbg` errors in `export.log`).

## Next Step
- Have user test `/switch/mother-encore/mother_encore.nro` on Nintendo Switch via **Title Override** (hold `R` on an installed title -> `hbmenu` -> `MOTHER: Encore`) for boot, audio, inputs, battle backgrounds, and saves.
