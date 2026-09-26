"""Lista os slugs (identificadores) de todos os clubes, equipes, atletas e lutadores do site.
Uso: python3 tools/slugs.py            (tudo)
     python3 tools/slugs.py lutas      (só um esporte)
"""
import os, sys
from playwright.sync_api import sync_playwright
HTML = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
only = sys.argv[1] if len(sys.argv) > 1 else None
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto("file://" + HTML); pg.wait_for_timeout(500)
    data = pg.evaluate("""()=>{var o={futebol:TVA.TEAMS.map(function(r){return [r[0],TVA.TEAM[r[0]].name]})};
      Object.keys(TVA.EQ).forEach(function(k){o[k]=TVA.EQ[k].map(function(r){return [r[0],r[1]]})});return o;}""")
    for sp, rows in data.items():
        if only and sp != only: continue
        print(f"## {sp} ({len(rows)})")
        for sl, name in rows: print(f"{sl}\t{name}")
    b.close()
