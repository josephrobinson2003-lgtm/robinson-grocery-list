# Robinson Grocery List

Phone-friendly, no-build grocery checklist for the Robinson family meal plan.
Live: https://josephrobinson2003-lgtm.github.io/robinson-grocery-list/
Repo: https://github.com/josephrobinson2003-lgtm/robinson-grocery-list (GitHub Pages, `main` branch, root)

## Files
- `list.json`   – the grocery data (the ONLY thing to change each week)
- `template.html` – the app (HTML/CSS/JS). Has a `GROCERY-DATA-START/END` placeholder.
- `build.py`    – injects `list.json` into `template.html` -> `index.html` (self-contained) and writes `list.txt` (plain-text list to paste in chat)
- `index.html`  – generated, what GitHub Pages serves. Don't hand-edit; run `build.py`.
- `.nojekyll`   – tells Pages to serve files as-is.

## Weekly refresh
1. Read the Family calendar (`family17195563696193731746@group.calendar.google.com`, user-Google-calendar
   connector `list_events`, America/Chicago) for the new week's menu events (dinner recipes have an
   "Ingredients:" list; weekend events name BREAKFAST/LUNCH by name only).
2. Rewrite `list.json`:
   - `weekId`: the first date of the new list (e.g. `2026-10-24`). **Changing it makes every phone start
     with a fresh, unchecked list** (checkmarks are stored in localStorage under `robinson-grocery:<weekId>`;
     old weeks' keys are deleted automatically).
   - `range`, `updated`, and `sections[]` -> `groups[]` (Meat, Produce, Dairy & Eggs, Bakery/Bread,
     Pantry/Canned/Dry, Spices & Sauces, Frozen, Other) -> `items[]` with
     `n` (name), `q` (combined quantity), `m` (which meals, short form, e.g. "Mon D, Thu D"), `e: true` if estimated.
   - Combine duplicate ingredients and add up quantities. Empty groups can be omitted.
3. Build and publish:
   ```bash
   cd /workspace/robinson-grocery-list
   python3 build.py
   git add -A && git commit -m "Grocery list for week of <date>" && git push
   ```
   Pages redeploys in ~1 minute. Check: `curl -s https://josephrobinson2003-lgtm.github.io/robinson-grocery-list/ | grep -o '"weekId": *"[^"]*"'`
4. Paste `list.txt` to the user if they want the list in chat.

`gh` on the box is logged in as `josephrobinson2003-lgtm` (git uses `gh auth setup-git` for HTTPS pushes).
