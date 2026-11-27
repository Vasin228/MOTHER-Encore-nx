#!/usr/bin/env bash
set -e
export DEVKITPRO=/opt/devkitpro
export PATH="/opt/devkitpro/portlibs/switch/bin:/opt/devkitpro/devkitA64/bin:/opt/devkitpro/tools/bin:$PATH"

cd "$HOME/godot-switch-src"
git checkout -- platform/switch/os_switch.cpp platform/switch/audio_driver_switch.cpp
python3 /mnt/d/Anti/mother-encore-nx/build/patch_engine.py
git diff > /mnt/d/Anti/mother-encore-nx/src/switch/godot_switch_engine.patch

echo "=== SCONS BUILD START ==="
scons -j4 platform=switch target=release tools=no \
  warnings=no werror=no debug_symbols=no \
  builtin_freetype=no builtin_libpng=no builtin_zlib=no \
  module_bullet_enabled=no module_visual_script_enabled=no \
  module_mobile_vr_enabled=no module_webxr_enabled=no \
  module_upnp_enabled=no module_webrtc_enabled=no \
  module_theora_enabled=no module_webm_enabled=no \
  module_enet_enabled=no module_gdnative_enabled=no \
  module_gridmap_enabled=no module_csg_enabled=no \
  module_vhacd_enabled=no module_xatlas_unwrap_enabled=no \
  module_assimp_enabled=no module_gltf_enabled=no

ls -lh bin/godot.switch.opt.64*
ELF=$(ls bin/godot.switch.opt.64* | grep -v '\.nro$' | head -n 1)
echo "Built ELF: $ELF"

/opt/devkitpro/tools/bin/nacptool --create "MOTHER: Encore" "Team Encore" "0.4.1.2" /tmp/mother_encore.nacp
rm -rf /tmp/me_romfs && mkdir -p /tmp/me_romfs
cp /mnt/d/Anti/mother-encore-nx/tools/switch-template/templates/switch_applet_splash.rgba.gz /tmp/me_romfs/applet_splash.rgba.gz

/opt/devkitpro/tools/bin/elf2nro "$ELF" /mnt/d/Anti/mother-encore-nx/build/mother_encore.nro \
  --icon=/mnt/d/Anti/mother-encore-nx/src/icon_switch_256.jpg \
  --nacp=/tmp/mother_encore.nacp \
  --romfsdir=/tmp/me_romfs

ls -lh /mnt/d/Anti/mother-encore-nx/build/mother_encore.nro
