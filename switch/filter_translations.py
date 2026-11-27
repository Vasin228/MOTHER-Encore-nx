import os, re, subprocess

src = r"d:\Anti\mother-encore-nx\src"
pg_path = os.path.join(src, "project.godot")

# Restore original translations line from HEAD so we filter from full 386 list
head_pg = subprocess.check_output(
    ["git", "-C", src, "show", "HEAD:project.godot"],
    text=True, encoding="utf-8", errors="ignore"
)
m_head = re.search(r'(translations=PoolStringArray\()(.*?)(\))', head_pg, re.S)
assert m_head, "translations=PoolStringArray(...) not found in HEAD:project.godot"

existing_list_path = r"d:\Anti\mother-encore-nx\build\existing_translations.txt"
existing = set(
    line.strip() for line in open(existing_list_path, "r", encoding="utf-8") if line.strip()
)
assert len(existing) >= 300, f"Expected >=300 imported translations, got {len(existing)}"

items = re.findall(r'"(res://[^"]+)"', m_head.group(2))
kept = []
removed = []
for item in items:
    fn = item.split("/")[-1]
    if fn in existing:
        kept.append(item)
    else:
        removed.append(item)

raw = open(pg_path, "rb").read()
use_crlf = b"\r\n" in raw
txt = raw.decode("utf-8")
m_cur = re.search(r'(translations=PoolStringArray\()(.*?)(\))', txt, re.S)
assert m_cur, "translations=PoolStringArray(...) not found in current project.godot"

new_inner = " " + ", ".join(f'"{k}"' for k in kept) + " "
new_txt = txt[:m_cur.start(2)] + new_inner + txt[m_cur.end(2):]
newline = "\r\n" if use_crlf else "\n"
with open(pg_path, "w", encoding="utf-8", newline=newline) as f:
    f.write(new_txt.replace("\r\n", "\n"))

print(f"Translations filtered: total={len(items)}, kept={len(kept)}, removed={len(removed)}")
