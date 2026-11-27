# MOTHER: Encore — Nintendo Switch Port (`d:\Anti\mother-encore-nx`)

## Milestone Summary

| Date | Stage | Artifact / Target | Status |
|---|---|---|---|
| 2026-11-27 | Initial Switch Port v0.4.1.2 | `build/mother_encore.nro` + `build/mother_encore.pck` | Built & Pushed (`1713fa2`), Black Screen on Switch |
| 2026-11-27 | Case-Sensitivity Fix + File Logging | `build/mother_encore.nro` + `build/mother_encore.pck` | Verified 0-Error Local PCK Boot, Deploying |

## Root-Cause Fix (2026-11-27)
- **Black Screen Root Cause**: `Nodes/Ui/StatsMenuUI.tscn` referenced 12 `Graphics/UI/Ailments/*.png` icons in lowercase (`mushroomized.png`, etc.) while actual files in Git / `.pck` are capitalized (`Mushroomized.png`, etc.). On case-sensitive `.pck` (`DirAccessPack`) / Switch, `StatsMenuUI.tscn` failed -> `Pause menu.tscn` failed -> `uiManager.gd` autoload failed (`uiManager == Nil`), breaking `global.gd`, `GameCamera`, and `phone.gd`.
- **Repo-Wide Case Audit (`build/fix_case.py`)**: Fixed all **22** case-sensitivity mismatches across `Nodes/Ui/StatsMenuUI.tscn` (12), `project.godot` (19 Ailments + `Credits.gd`), `.godot/global_script_class_cache.cfg` (`Credits.gd`), `Maps/Cutscenes/credits_act_1.tscn` (`Credits.gd`), and `Maps/Cutscenes/credits_full.tscn` (`Credits.gd`). Re-audit confirmed `TOTAL CASE MISMATCHES: 0`.
- **Switch Logging**: Enabled `[logging]` (`file_logging/enable_file_logging=true`, `file_logging/log_path="user://godot.log"`) in `project.godot`.
- **Local PCK Smoke Test**: `godot3-switch --path /tmp/pck_test --main-pack build/mother_encore.pck` ran with **0** `Can't autoload`, **0** `SCRIPT ERROR`, **0** `StatsMenuUI`/`Pause menu`/`podunk.tscn` parse errors, and reached `Respawn: Disclaimer (0, 0)`.

## Verified Build Outputs (`build/`)
- `mother_encore.nro`: `45,191,361` B, `LastWriteTime = 2026-11-27 10:14:31`, `SHA256 = 63996BE18939400488A8E79BA68039C440C838F48AF173808F0CB41911B3314D`
- `mother_encore.pck`: `255,545,264` B, `LastWriteTime = 2026-11-27 10:14:31`, `SHA256 = 5BBD55F564C7048D756A2D58A98BDFF813D310D4013F506B815BCB47A224FA53`

## Switch Compatibility Patches (`src/`)
- `project.godot`, `Scripts/global/global.gd`, `addons/integer_resolution_handler/integer_resolution_handler.gd`, `Scripts/UI/Options/OptionsUI.gd`, `Scripts/Main/AoOni.gd`, `Nodes/Ui/Inventory/ActionSelect.gd`, `Nodes/Ui/StatsMenuUI.tscn`, `Maps/Cutscenes/credits_act_1.tscn`, `Maps/Cutscenes/credits_full.tscn`, `.godot/global_script_class_cache.cfg`, `icon_switch_256.jpg`, `export_presets.cfg`, and `switch/` tooling.

## Next Step
- Have user relaunch `/switch/mother-encore/mother_encore.nro` via Title Override on Switch and verify visual boot (and inspect `/switch/mother-encore/userdata/godot.log` if needed).
