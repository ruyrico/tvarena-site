"""Capa própria de cada matéria (1200x630), usada no Google, no Discover e no compartilhamento (WhatsApp, redes).

Chamado pelo build_pages.py. As capas ficam em assets/capas/<id>.jpg e são fixas no repositório:
só são refeitas quando título, editoria, autor ou placar da matéria mudam (controle em assets/capas/.versao.json).
Arte 100% própria: fontes livres (licença OFL, em tools/fonts), escudos desenhados pelo próprio site e fotos dos jornalistas.
"""
import base64
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "assets", "capas")
VERSAO = os.path.join(DIR, ".versao.json")
FONTS = os.path.join(ROOT, "tools", "fonts")
LAYOUT = "3"  # mude para refazer todas as capas depois de alterar o desenho
AUT = {"ruy-avila": "Ruy Ávila", "andre-veras": "Andre Veras", "joao-marcelo": "João Marcelo"}
esc = lambda s: html.escape(str(s or ""), quote=True)


def _font_css():
    out = []
    for fam, base, ws in (("Big Shoulders Display", "big-shoulders-display", (800, 900)), ("Archivo", "archivo", (600, 700))):
        for w in ws:
            with open(os.path.join(FONTS, f"{base}-latin-{w}-normal.woff2"), "rb") as f:
                b = base64.b64encode(f.read()).decode()
            out.append("@font-face{font-family:'%s';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam, w, b))
    return "".join(out)


CSS = """
body{margin:0}
.c{width:1200px;height:630px;background:#15171B;color:#EFEFEA;position:relative;box-sizing:border-box;padding:56px 80px 46px 90px;
   font-family:'Big Shoulders Display',Impact,sans-serif;display:flex;flex-direction:column;overflow:hidden}
.bar{position:absolute;left:0;top:0;bottom:0;width:22px;background:#C8361B}
.top{display:flex;justify-content:space-between;align-items:center;gap:30px;white-space:nowrap;font-family:Archivo,Arial,sans-serif;
     font-weight:700;font-size:24px;letter-spacing:2px;text-transform:uppercase;color:#C8361B}
.top>span:first-child{overflow:hidden;text-overflow:ellipsis}
.brand{flex:none;font-family:'Big Shoulders Display';font-weight:900;font-size:34px;letter-spacing:0;color:#EFEFEA}
.brand span{color:#C8361B}
.score{display:flex;align-items:center;gap:30px;margin-top:30px}
.score svg{width:92px;height:108px}
.score b{font-size:104px;font-weight:900;line-height:1}
.score i{font-style:normal;font-size:56px;color:#9C988F;font-weight:800}
.score .nm{font-family:Archivo,Arial,sans-serif;font-weight:700;font-size:25px;color:#D9D5CB;text-transform:uppercase;letter-spacing:1px}
.t{margin-top:auto;font-weight:900;line-height:.98;text-transform:uppercase;letter-spacing:-.5px}
.foot{margin-top:24px;display:flex;justify-content:space-between;align-items:flex-end;font-family:Archivo,Arial,sans-serif;font-weight:600;font-size:22px;color:#9C988F}
.au{display:flex;align-items:center;gap:14px;color:#EFEFEA;font-size:24px}
.au img{width:58px;height:58px;border-radius:50%;border:3px solid #C8361B;object-fit:cover}
.au small{display:block;color:#9C988F;font-size:18px}
"""


def autor_de(x):
    m = re.search(r'data-autor="([a-z-]+)"', x.get("html", ""))
    return m.group(1) if m and m.group(1) in AUT else None


def placar_de(x, season):
    """Placar só em matéria de RESULTADO de jogo de futebol entre dois clubes (nunca na prévia):
    o placar tem de estar no título ou no id da matéria, ou ser a matéria do próprio jogo."""
    if x["sp"] != "futebol" or len(x["who"]) < 2 or not x.get("date"):
        return None
    if x.get("score"):
        return x["score"]
    a, b = x["who"][:2]
    d = x["date"].strftime("%d/%m")
    txt = (x.get("t", "") + " " + x["id"].replace("-", " ")).lower()
    def citado(g1, g2):
        return any(p in txt for p in (f"{g1} a {g2}", f"{g2} a {g1}", f"{g1}x{g2}", f"{g2}x{g1}", f"{g1} x {g2}", f"{g2} x {g1}"))
    for r in season.get("sa", []) + season.get("sb", []):
        if r[3] is not None and r[1] == d and {r[2], r[5]} == {a, b} and citado(r[3], r[4]):
            return (r[2], r[3], r[4], r[5])
    m = re.search(r"-(\d{1,2})x(\d{1,2})-", x["id"])
    if m and x["kind"] == "plantao" and x["id"].find(a.split("-")[0]) < m.start() < x["id"].find(b.split("-")[0]):
        return (a, int(m.group(1)), int(m.group(2)), b)
    return None


def _html(x, badges, season, fonts):
    au = autor_de(x)
    sc = placar_de(x, season)
    t = x["t"]
    n = len(t)
    size = 92 if n < 70 else 80 if n < 100 else 70 if n < 130 else 62 if n < 160 else 54
    mid = ""
    if sc and sc[0] in badges and sc[3] in badges:
        mid = (f'<div class="score">{badges[sc[0]][0]}<div class="nm">{esc(badges[sc[0]][1])}</div><b>{sc[1]}</b><i>x</i>'
               f'<b>{sc[2]}</b><div class="nm">{esc(badges[sc[3]][1])}</div>{badges[sc[3]][0]}</div>')
        size = min(size, 70)
    d = x.get("date")
    when = (d.strftime("%d/%m/%Y") + ("" if (d.hour, d.minute) in ((0, 0), (6, 0)) else d.strftime(" · %Hh%M"))) if d else ""
    if au:
        with open(os.path.join(ROOT, "assets", "autores", f"{au}.jpg"), "rb") as f:
            ph = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
        left = f'<span class="au"><img src="{ph}"><span>Por {esc(AUT[au])}<small>{when}</small></span></span>'
    else:
        left = f"<span>{when}</span>"
    return (f'<html><head><meta charset="utf-8"><style>{fonts}{CSS}</style></head><body><div class="c"><div class="bar"></div>'
            f'<div class="top"><span>{esc(x["k"])}</span><span class="brand">TV ARENA <span>ESPORTES</span></span></div>{mid}'
            f'<div class="t" style="font-size:{size}px">{esc(t)}</div>'
            f'<div class="foot">{left}<span>tvarenaesportes.com.br</span></div></div></body></html>'), (au, sc)


def render_covers(items, badges, season):
    """Gera/atualiza as capas. Devolve {id: '/assets/capas/<id>.jpg?v=<hash>'}."""
    from playwright.sync_api import sync_playwright
    os.makedirs(DIR, exist_ok=True)
    try:
        ver = json.load(open(VERSAO, encoding="utf-8"))
    except Exception:
        ver = {}
    fonts = _font_css()
    out, todo = {}, []
    for x in items:
        doc, sig = _html(x, badges, season, fonts)
        h = hashlib.md5((LAYOUT + "|" + x["t"] + "|" + x["k"] + "|" + json.dumps(sig) + "|" + (x["date"].isoformat() if x.get("date") else "")).encode()).hexdigest()[:10]
        path = os.path.join(DIR, x["id"] + ".jpg")
        out[x["id"]] = f"/assets/capas/{x['id']}.jpg?v={h}"
        if ver.get(x["id"]) != h or not os.path.exists(path):
            todo.append((x["id"], doc, h, path))
    if todo:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1200, "height": 630})
            for cid, doc, h, path in todo:
                pg.set_content(doc)
                pg.evaluate("document.fonts.ready")
                pg.screenshot(path=path, type="jpeg", quality=80)
                ver[cid] = h
            b.close()
        with open(VERSAO, "w", encoding="utf-8") as f:
            json.dump(ver, f, ensure_ascii=False, indent=0, sort_keys=True)
    print(f"Capas: {len(todo)} geradas/atualizadas, {len(out)} no total.")
    return out
