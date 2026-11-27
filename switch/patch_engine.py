import os

root = os.path.expanduser("~/godot-switch-src/platform/switch")

# 1. Patch os_switch.cpp: disable swkbdInline library applet & virtual keyboard
os_path = os.path.join(root, "os_switch.cpp")
os_txt = open(os_path, "r", encoding="utf-8").read()

repls_os = [
    (
        "\tswkbdInlineLaunchForLibraryApplet(&inline_keyboard, SwkbdInlineMode_AppletDisplay, 0);\n"
        "\tswkbdInlineSetChangedStringCallback(&inline_keyboard, keyboard_string_changed_callback);\n"
        "\tswkbdInlineSetMovedCursorCallback(&inline_keyboard, keyboard_moved_cursor_callback);\n"
        "\tswkbdInlineSetDecidedEnterCallback(&inline_keyboard, keyboard_decided_enter_callback);\n"
        "\tswkbdInlineSetDecidedCancelCallback(&inline_keyboard, keyboard_decided_cancel_callback);",
        "\t// Disabled swkbdInline library applet for HOS 21+/22.5.0 compatibility"
    ),
    (
        "\t\tswkbdInlineUpdate(&inline_keyboard, NULL);",
        "\t\t// swkbdInline disabled"
    ),
    (
        "\tswkbdInlineClose(&inline_keyboard);",
        "\t// swkbdInline disabled"
    ),
    (
        "bool OS_Switch::has_virtual_keyboard() const {\n\treturn true;\n}",
        "bool OS_Switch::has_virtual_keyboard() const {\n\treturn false;\n}"
    ),
    (
        "void OS_Switch::show_virtual_keyboard(const String &p_existing_text, const Rect2 &p_screen_rect, int p_max_input_length) {\n"
        "\tif (!g_swkbd_open) {\n"
        "\t\tg_swkbd_open = true;\n\n"
        "\t\tSwkbdAppearArg appear_arg;\n"
        "\t\tswkbdInlineMakeAppearArg(&appear_arg, SwkbdType_Normal);\n"
        "\t\tswkbdInlineSetInputText(&inline_keyboard, p_existing_text.utf8().get_data());\n"
        "\t\tswkbdInlineSetCursorPos(&inline_keyboard, p_existing_text.size() - 1);\n\n"
        "\t\tg_eat_string_events = 2;\n\n"
        "\t\tswkbdInlineAppear(&inline_keyboard, &appear_arg);\n"
        "\t}\n"
        "}",
        "void OS_Switch::show_virtual_keyboard(const String &p_existing_text, const Rect2 &p_screen_rect, int p_max_input_length) {\n"
        "\t// Disabled swkbdInline\n"
        "}"
    ),
    (
        "void OS_Switch::hide_virtual_keyboard() {\n"
        "\tprintf(\"Hiding kbd!\\n\");\n"
        "\tg_swkbd_open = false;\n"
        "\tswkbdInlineDisappear(&inline_keyboard);\n"
        "}",
        "void OS_Switch::hide_virtual_keyboard() {\n"
        "\tg_swkbd_open = false;\n"
        "}"
    ),
    (
        "\tswkbdInlineCreate(&inline_keyboard);",
        "\t// swkbdInline disabled"
    ),
]

for old, new in repls_os:
    assert old in os_txt, f"Pattern not found in os_switch.cpp:\n{old}"
    os_txt = os_txt.replace(old, new, 1)

open(os_path, "w", encoding="utf-8", newline="\n").write(os_txt)
print("Patched os_switch.cpp cleanly")

# 2. Patch audio_driver_switch.cpp: check audren/audrv results + bound wait loop
aud_path = os.path.join(root, "audio_driver_switch.cpp")
aud_txt = open(aud_path, "r", encoding="utf-8").read()

repls_aud = [
    (
        "\tResult res = audrenInitialize(&arConfig);\n"
        "\tprintf(\"audrenInitialize: %x\\n\", res);\n"
        "\tres = audrvCreate(&audren_driver, &arConfig, 2);\n"
        "\tprintf(\"audrenInitialize: %x\\n\", res);",
        "\tResult res = audrenInitialize(&arConfig);\n"
        "\tprintf(\"audrenInitialize: %x\\n\", res);\n"
        "\tif (R_FAILED(res)) return ERR_CANT_OPEN;\n"
        "\tres = audrvCreate(&audren_driver, &arConfig, 2);\n"
        "\tprintf(\"audrvCreate: %x\\n\", res);\n"
        "\tif (R_FAILED(res)) { audrenExit(); return ERR_CANT_OPEN; }"
    ),
    (
        "\tres = audrvUpdate(&audren_driver);\n"
        "\tprintf(\"audrvUpdate: %x\\n\", res);\n\n"
        "\tres = audrenStartAudioRenderer();\n"
        "\tprintf(\"audrenStartAudioRenderer: %x\\n\", res);",
        "\tres = audrvUpdate(&audren_driver);\n"
        "\tprintf(\"audrvUpdate: %x\\n\", res);\n"
        "\tif (R_FAILED(res)) { audrvClose(&audren_driver); audrenExit(); return ERR_CANT_OPEN; }\n\n"
        "\tres = audrenStartAudioRenderer();\n"
        "\tprintf(\"audrenStartAudioRenderer: %x\\n\", res);\n"
        "\tif (R_FAILED(res)) { audrvClose(&audren_driver); audrenExit(); return ERR_CANT_OPEN; }"
    ),
    (
        "\t\t\twhile (ad->audren_buffers[free_buffer].state != AudioDriverWaveBufState_Playing) {\n"
        "\t\t\t\taudrvUpdate(&ad->audren_driver);\n"
        "\t\t\t}",
        "\t\t\tint wait_tries = 0;\n"
        "\t\t\twhile (ad->audren_buffers[free_buffer].state != AudioDriverWaveBufState_Playing) {\n"
        "\t\t\t\taudrvUpdate(&ad->audren_driver);\n"
        "\t\t\t\tif (++wait_tries >= 2000) break;\n"
        "\t\t\t}"
    ),
]

for old, new in repls_aud:
    assert old in aud_txt, f"Pattern not found in audio_driver_switch.cpp:\n{old}"
    aud_txt = aud_txt.replace(old, new, 1)

open(aud_path, "w", encoding="utf-8", newline="\n").write(aud_txt)
print("Patched audio_driver_switch.cpp cleanly")
