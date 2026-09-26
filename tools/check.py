"""Checagem do site antes de publicar.

Uso: python3 tools/check.py
Sai com código 1 se encontrar erro de JavaScript, página quebrada ou rolagem lateral no celular.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
ROUTES = ["", "#materia", "#futebol", "#volei", "#basquete", "#lutas", "#motor", "#tenis",
          "#times", "#time-flamengo", "#time-palmeiras", "#classificacao", "#videos", "#quem-somos"]

def main():
    src = open(HTML, encoding="utf-8").read()
    ok = True

    # 1) sintaxe de cada <script> inline
    for i, js in enumerate(re.findall(r"<script>(.*?)</script>", src, re.S)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(js)
        r = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
        if r.returncode:
            print(f"ERRO de sintaxe no script {i}:\n{r.stderr[:1500]}"); ok = False

    # 2) abre as páginas no navegador (computador e celular)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h in ((1440, 900), (390, 844)):
            pg = b.new_page(viewport={"width": w, "height": h})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            for r in ROUTES:
                pg.goto("file://" + HTML + r)
                pg.wait_for_timeout(350)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                if sw > w + 1:
                    print(f"AVISO rolagem lateral {sw}px em {w}px: '{r}'"); ok = False
            # abre algumas matérias e notas
            for sel in ["a[href^='#jogo-']", "a[href^='#nota-']", "a[href^='#an-']"]:
                hrefs = pg.eval_on_selector_all(sel, "els=>els.slice(0,4).map(e=>e.getAttribute('href'))")
                for hr in hrefs:
                    pg.goto("file://" + HTML + hr); pg.wait_for_timeout(250)
            if errs:
                print(f"ERROS de JavaScript ({w}px):", *errs[:10], sep="\n  "); ok = False
        b.close()

    print("OK — site sem erros." if ok else "FALHOU — corrija antes de publicar.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
