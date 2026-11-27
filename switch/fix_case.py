import os, re

src = r"d:\Anti\mother-encore-nx\src"

ailment_map = {
    "Graphics/UI/Ailments/asthma.png": "Graphics/UI/Ailments/Asthma.png",
    "Graphics/UI/Ailments/asthma_monospace.png": "Graphics/UI/Ailments/Asthma_monospace.png",
    "Graphics/UI/Ailments/blinded.png": "Graphics/UI/Ailments/Blinded.png",
    "Graphics/UI/Ailments/blinded_monospace.png": "Graphics/UI/Ailments/Blinded_monospace.png",
    "Graphics/UI/Ailments/burned.png": "Graphics/UI/Ailments/Burned.png",
    "Graphics/UI/Ailments/cold.png": "Graphics/UI/Ailments/Cold.png",
    "Graphics/UI/Ailments/confused.png": "Graphics/UI/Ailments/Confused.png",
    "Graphics/UI/Ailments/confused_monospace.png": "Graphics/UI/Ailments/Confused_monospace.png",
    "Graphics/UI/Ailments/forgetful.png": "Graphics/UI/Ailments/Forgetful.png",
    "Graphics/UI/Ailments/forgetful_monospace.png": "Graphics/UI/Ailments/Forgetful_monospace.png",
    "Graphics/UI/Ailments/mushroomized.png": "Graphics/UI/Ailments/Mushroomized.png",
    "Graphics/UI/Ailments/nausea.png": "Graphics/UI/Ailments/Nausea.png",
    "Graphics/UI/Ailments/nausea_monospace.png": "Graphics/UI/Ailments/Nausea_monospace.png",
    "Graphics/UI/Ailments/numb.png": "Graphics/UI/Ailments/Numb.png",
    "Graphics/UI/Ailments/numb_monospace.png": "Graphics/UI/Ailments/Numb_monospace.png",
    "Graphics/UI/Ailments/poisoned.png": "Graphics/UI/Ailments/Poisoned.png",
    "Graphics/UI/Ailments/poisoned_monospace.png": "Graphics/UI/Ailments/Poisoned_monospace.png",
    "Graphics/UI/Ailments/sleeping.png": "Graphics/UI/Ailments/Sleeping.png",
    "Graphics/UI/Ailments/sleeping_monospace.png": "Graphics/UI/Ailments/Sleeping_monospace.png",
    "Graphics/UI/Ailments/sunstroked.png": "Graphics/UI/Ailments/Sunstroked.png",
    "Graphics/UI/Ailments/sunstroked_monospace.png": "Graphics/UI/Ailments/Sunstroked_monospace.png",
    "Scripts/UI/Credits/credits.gd": "Scripts/UI/Credits/Credits.gd",
}

targets = [
    r"Nodes\Ui\StatsMenuUI.tscn",
    r"project.godot",
    r".godot\global_script_class_cache.cfg",
    r"Maps\Cutscenes\credits_act_1.tscn",
    r"Maps\Cutscenes\credits_full.tscn",
]

for rel in targets:
    p = os.path.join(src, rel)
    raw = open(p, "rb").read()
    use_crlf = b"\r\n" in raw
    txt = raw.decode("utf-8")
    count = 0
    for bad, good in ailment_map.items():
        if bad in txt:
            c = txt.count(bad)
            txt = txt.replace(bad, good)
            count += c
    if rel == "project.godot" and "[logging]" not in txt:
        log_block = '\n[logging]\n\nfile_logging/enable_file_logging=true\nfile_logging/log_path="user://godot.log"\n'
        txt = txt.replace("[network]", log_block + "\n[network]", 1)
    newline = "\r\n" if use_crlf else "\n"
    txt_norm = txt.replace("\r\n", "\n")
    with open(p, "w", encoding="utf-8", newline=newline) as f:
        f.write(txt_norm)
    print(f"Updated {rel}: {count} replacements (crlf={use_crlf})")

# Re-audit all case mismatches across entire repo
exact = set()
lower_map = {}
for root, dirs, files in os.walk(src):
    if ".git" in dirs:
        dirs.remove(".git")
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), src).replace("\\", "/")
        exact.add(rel)
        lower_map[rel.lower()] = rel

pat = re.compile(r'res://([^"\r\n\)\]]+)')
mismatches = {}
for root, dirs, files in os.walk(src):
    if ".git" in dirs:
        dirs.remove(".git")
    for fn in files:
        if not fn.endswith((".tscn", ".tres", ".gd", ".godot", ".cfg", ".shader", ".gdshader", ".bbg")):
            continue
        p = os.path.join(root, fn)
        rel_src = os.path.relpath(p, src).replace("\\", "/")
        txt = open(p, "r", encoding="utf-8", errors="ignore").read()
        for m in pat.finditer(txt):
            raw_t = m.group(1)
            target = re.sub(r":[a-zA-Z_]+$", "", raw_t)
            if target.startswith(".import/") or "%" in target or "{" in target or target.endswith("/"):
                continue
            if "'" in target and target not in exact and target.lower() not in lower_map:
                target = target.split("'")[0]
            if target not in exact and target.lower() in lower_map:
                mismatches.setdefault((target, lower_map[target.lower()]), set()).add(rel_src)

print(f"TOTAL CASE MISMATCHES: {len(mismatches)}")
for (bad, good), refs in sorted(mismatches.items()):
    print(f"  {bad} --> {good} | {sorted(refs)}")
