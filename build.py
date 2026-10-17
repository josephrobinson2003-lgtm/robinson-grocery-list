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
print("built index.html and list.txt;", sum(len(g["items"]) for s in data["sections"] for g in s["groups"]), "items")
