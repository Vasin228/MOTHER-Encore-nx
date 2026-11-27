#!/usr/bin/env bash
set -u
SRC_WIN=/mnt/d/Anti/mother-encore-nx/src
SRC="$HOME/me-src"
GODOT="$HOME/godot3-switch"
OUT=/mnt/d/Anti/mother-encore-nx/build/mother_encore.nro
EXPLOG=/mnt/d/Anti/mother-encore-nx/build/export.log

cp "$SRC_WIN/Nodes/Ui/Inventory/ActionSelect.gd" "$SRC/Nodes/Ui/Inventory/ActionSelect.gd"
cp /mnt/d/Anti/mother-encore-nx/build/import_bbgs.gd /tmp/import_bbgs.gd
sed -i 's/\r$//' /tmp/import_bbgs.gd

echo "=== STEP 1: HEADLESS BBG IMPORT ==="
"$GODOT" --no-window --path "$SRC" --script /tmp/import_bbgs.gd
BBG_RC=$?
echo "BBG_RC=$BBG_RC"
echo "BBG .scn count: $(ls -1 "$SRC/.import/"*.bbg-*.scn 2>/dev/null | wc -l)"
if [ "$BBG_RC" -ne 0 ]; then
    exit "$BBG_RC"
fi

echo "=== STEP 2: RE-EXPORT SWITCH ==="
"$GODOT" --no-window --path "$SRC" --export "Nintendo Switch" "$OUT" > "$EXPLOG" 2>&1
EXP_RC=$?
echo "EXPORT_RC=$EXP_RC"
exit "$EXP_RC"
