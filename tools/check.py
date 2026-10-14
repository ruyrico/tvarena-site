"""Checagem do site antes de publicar.

Uso: python3 tools/check.py
Antes de checar, refaz as páginas estáticas (tools/build_pages.py): cada matéria com endereço próprio.
Sai com código 1 se encontrar erro de JavaScript, página quebrada ou rolagem lateral no celular.
"""
import functools, http.server, os, re, subprocess, sys, tempfile, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
ROUTES = ["", "#materia", "#futebol", "#volei", "#basquete", "#lutas", "#motor", "#tenis",
          "#times", "#time-flamengo", "#time-palmeiras", "#classificacao", "#videos", "#quem-somos"]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    # 0) refaz as páginas estáticas
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_pages.py")], capture_output=True, text=True)
    print(r.stdout.strip()[-600:])
    if r.returncode:
        print("ERRO ao gerar as páginas estáticas:\n" + (r.stderr or r.stdout)[-1500:])
        print("FALHOU — corrija antes de publicar."); sys.exit(1)

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
        # 3) páginas estáticas, servidas como no site de verdade
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=ROOT))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        news = sorted(os.listdir(os.path.join(ROOT, "noticias")))
        news = [n for n in news if os.path.isdir(os.path.join(ROOT, "noticias", n))]
        pages = ["/noticias/", "/times/", "/futebol/", "/futebol/flamengo/", "/politica-de-privacidade/", "/termos-de-uso/",
                 "/quem-somos/", "/sitemap.xml", "/robots.txt"] + [f"/noticias/{n}/" for n in news[:3] + news[-3:]]
        for w, h in ((1440, 900), (390, 844)):
            pg = b.new_page(viewport={"width": w, "height": h})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            for u in pages:
                if not os.path.exists(os.path.join(ROOT, u.strip("/"), "" if "." in u else "index.html")):
                    continue
                resp = pg.goto(base + u)
                if not resp or resp.status != 200:
                    print(f"ERRO página estática {u}: {resp.status if resp else 'sem resposta'}"); ok = False; continue
                if u.endswith("/"):
                    sw = pg.evaluate("document.documentElement.scrollWidth")
                    if sw > w + 1:
                        print(f"AVISO rolagem lateral {sw}px em {w}px: '{u}'"); ok = False
            if errs:
                print(f"ERROS de JavaScript nas páginas estáticas ({w}px):", *errs[:10], sep="\n  "); ok = False
        srv.shutdown()
        b.close()

    print("OK — site sem erros." if ok else "FALHOU — corrija antes de publicar.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
