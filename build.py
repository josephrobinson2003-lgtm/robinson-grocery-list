#!/usr/bin/env python3
"""Inject list.json into template.html -> index.html, and write list.txt (plain-text list)."""
import json, re, pathlib
here = pathlib.Path(__file__).parent
data = json.loads((here / "list.json").read_text())
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
tpl = (here / "template.html").read_text()
block = '<!-- GROCERY-DATA-START -->\n<script id="grocery-data" type="application/json">' + blob + '</script>\n<!-- GROCERY-DATA-END -->'
out = re.sub(r"<!-- GROCERY-DATA-START -->.*?<!-- GROCERY-DATA-END -->", lambda m: block, tpl, flags=re.S)
(here / "index.html").write_text(out)
# Stamp the service-worker version so installed phones refresh their cache on every rebuild.
import hashlib
ver = data["weekId"] + "-" + hashlib.sha1(out.encode()).hexdigest()[:8]
sw = here / "sw.js"
sw.write_text(re.sub(r"const VERSION = '[^']*';", f"const VERSION = '{ver}';", sw.read_text(), count=1))
# Sanity: PWA pieces must stay in place.
for f in ["manifest.webmanifest", "sw.js", "icons/icon-192.png", "icons/icon-512.png",
          "icons/icon-maskable-192.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png"]:
    assert (here / f).exists(), f"missing {f}"
for needle in ['rel="manifest"', 'apple-touch-icon', 'name="theme-color"', "serviceWorker.register"]:
    assert needle in out, f"index.html lost {needle}"
lines = [f"{data['title']} — {data['range']}", data.get("legend", ""), ""]
for s in data["sections"]:
    lines += [s["name"].upper(), ""]
    for g in s["groups"]:
        if not g["items"]: continue
        lines.append(g["name"])
        for it in g["items"]:
            lines.append(f"- {it['n']}{' ★' if it.get('e') else ''}: {it['q']} ({it['m']})")
        lines.append("")
(here / "list.txt").write_text("\n".join(lines))
print("built index.html, list.txt, sw.js version", ver, ";", sum(len(g["items"]) for s in data["sections"] for g in s["groups"]), "items")
