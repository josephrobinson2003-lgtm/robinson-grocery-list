#!/usr/bin/env python3
"""Build the Robinson Grocery List.

list.json         -> grocery data, grouped by food category (what the weekly job writes)
store_layout.json -> Schnucks Ballwin aisle map + walking order (applied here automatically)
template.html     -> app shell
Outputs: index.html (self-contained, data embedded), list.txt (plain text), sw.js VERSION stamp.
"""
import json, re, pathlib, hashlib, sys
here = pathlib.Path(__file__).parent
data = json.loads((here / "list.json").read_text())
layout = json.loads((here / "store_layout.json").read_text())

def slug(s):  # must match slug() in template.html (check-mark ids)
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", s.lower()))

deps = sorted(layout["departments"], key=lambda d: d["order"])
dep_by_key = {d["key"]: d for d in deps}
item_map = layout["items"]

def natkey(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s or "")]

def locate(name, category):
    hit = item_map.get(name.lower())
    if hit: return hit["dept"], hit.get("loc", ""), True
    low = name.lower()
    for kw, dep in layout.get("keywords", []):
        if kw in low: return dep, "", False
    return layout["category_fallback"].get(category, "other"), "", False

unmapped = []
out_data = {k: v for k, v in data.items() if k != "sections"}
out_data["store"] = layout["store"]
out_data["sections"] = []
for sec in data["sections"]:
    buckets = {d["key"]: [] for d in deps}
    for g in sec["groups"]:
        for i, it in enumerate(g["items"]):
            it = dict(it)
            # id keeps the ORIGINAL category so existing check marks survive the regrouping
            it["id"] = f"{sec['id']}|{slug(g['name'])}|{slug(it['n'])}"
            dep, loc, exact = locate(it["n"], g["name"])
            if not exact: unmapped.append(f"{sec['id']}: {it['n']} -> {dep} (guessed)")
            if loc: it["loc"] = loc
            buckets.setdefault(dep, []).append(it)
    groups = []
    for d in deps:
        items = buckets.get(d["key"]) or []
        if not items: continue
        if d["key"].startswith("aisle") or d["key"] == "dairy":
            items.sort(key=lambda x: natkey(x.get("loc", "")))
        groups.append({"name": d["header"], "short": d["short"], "items": items})
    s2 = {k: v for k, v in sec.items() if k != "groups"}; s2["groups"] = groups
    out_data["sections"].append(s2)

blob = json.dumps(out_data, ensure_ascii=False).replace("</", "<\\/")
tpl = (here / "template.html").read_text()
block = '<!-- GROCERY-DATA-START -->\n<script id="grocery-data" type="application/json">' + blob + '</script>\n<!-- GROCERY-DATA-END -->'
out = re.sub(r"<!-- GROCERY-DATA-START -->.*?<!-- GROCERY-DATA-END -->", lambda m: block, tpl, flags=re.S)
(here / "index.html").write_text(out)

# Stamp the service-worker version so installed phones refresh their cache on every rebuild.
ver = data["weekId"] + "-" + hashlib.sha1(out.encode()).hexdigest()[:8]
sw = here / "sw.js"
sw.write_text(re.sub(r"const VERSION = '[^']*';", f"const VERSION = '{ver}';", sw.read_text(), count=1))

# Sanity: PWA pieces must stay in place.
for f in ["manifest.webmanifest", "sw.js", "store_layout.json", "icons/icon-192.png", "icons/icon-512.png",
          "icons/icon-maskable-192.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"]:
    assert (here / f).exists(), f"missing {f}"
for needle in ['rel="manifest"', 'apple-touch-icon', 'name="theme-color"', "serviceWorker.register"]:
    assert needle in out, f"index.html lost {needle}"

# Plain-text list in store walking order
st = layout["store"]
lines = [f"{data['title']} — {data['range']}", f"Store order: {st['name']}, {st['address']}", data.get("legend", ""), ""]
for s in out_data["sections"]:
    lines += [s["name"].upper(), ""]
    for g in s["groups"]:
        lines.append(g["name"])
        for it in g["items"]:
            where = f" [{it['loc']}]" if it.get("loc") and it["loc"] != g["short"] else ""
            lines.append(f"- {it['n']}{' ★' if it.get('e') else ''}: {it['q']} ({it['m']}){where}")
        lines.append("")
(here / "list.txt").write_text("\n".join(lines))

n = sum(len(g["items"]) for s in out_data["sections"] for g in s["groups"])
print("built index.html, list.txt, sw.js version", ver, ";", n, "items")
if unmapped:
    print("\nNOT IN store_layout.json (placed by keyword/category guess; look up and add them):")
    for u in unmapped: print("  ", u)
