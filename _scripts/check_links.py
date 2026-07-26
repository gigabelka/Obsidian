import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from convert_react_docs import extract_headings, FENCE_RE

# target directory to validate: argv[1] or the React docs by default
DST = sys.argv[1] if len(sys.argv) > 1 else os.path.join("Docs", "React")
DST = os.path.normpath(DST)
if not os.path.isdir(DST):
    sys.exit("Directory not found: %s" % DST)

heading_cache = {}


def headings_for(rel):
    if rel not in heading_cache:
        path = os.path.join(DST, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            heading_cache[rel] = None
        else:
            with open(path, encoding="utf-8") as f:
                heading_cache[rel] = extract_headings(f.read())
    return heading_cache[rel]


broken_files = {}
broken_links = []

# anchor links: [x](file.md#anchor) and [x](#anchor)
ANCHOR_RE = re.compile(r"\]\(([^)#\s]+\.md)?#([^)\s]+)\)")
# plain relative links: [x](file.md) — no scheme, no anchor, no leading slash
PLAIN_RE = re.compile(r"\]\((?!https?://|/|#)([^)#\s]+\.md)\)")

for root, _dirs, names in os.walk(DST):
    for name in names:
        if not name.endswith(".md"):
            continue
        path = os.path.join(root, name)
        rel = os.path.relpath(path, DST).replace("\\", "/")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        for m in re.finditer(ANCHOR_RE, text):
            target, anchor = m.group(1), m.group(2)
            if target and target.startswith(("http://", "https://")):
                continue
            if "%28" in anchor or "%29" in anchor:
                continue  # already rewritten by the converter
            if target:
                t_rel = os.path.normpath(os.path.join(os.path.dirname(rel), target)).replace("\\", "/")
            else:
                t_rel = rel
            heads = headings_for(t_rel)
            decoded = anchor.replace("%28", "(").replace("%29", ")")
            if heads is None:
                broken_links.append((rel, m.group(0), "missing file " + t_rel))
                broken_files.setdefault(rel, 0)
                broken_files[rel] += 1
            elif (anchor.lower() not in heads and anchor not in heads
                    and decoded not in heads.values()
                    and decoded.replace("`", "") not in [h.replace("`", "") for h in heads.values()]):
                broken_links.append((rel, m.group(0), "no heading"))
                broken_files.setdefault(rel, 0)
                broken_files[rel] += 1
        for m in re.finditer(PLAIN_RE, text):
            target = m.group(1)
            t_rel = os.path.normpath(os.path.join(os.path.dirname(rel), target)).replace("\\", "/")
            if headings_for(t_rel) is None:
                broken_links.append((rel, m.group(0), "missing file " + t_rel))
                broken_files.setdefault(rel, 0)
                broken_files[rel] += 1

for item in broken_links[:25]:
    print(item)
print("files with broken links:", len(broken_files), "total broken:", len(broken_links))
