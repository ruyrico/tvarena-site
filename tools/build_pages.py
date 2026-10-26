"""Gera as páginas estáticas do site a partir do index.html (para o Google indexar cada matéria).

Uso: python3 tools/build_pages.py

O que gera (tudo commitado no repositório e publicado junto com o index.html):
  /noticias/<id>/            uma página por matéria (plantão, notas, jogos e a matéria principal da home)
  /noticias/                 arquivo com todas as matérias
  /<esporte>/                últimas do esporte (futebol, volei, basquete, lutas, motor, tenis)
  /<esporte>/<slug>/         notícias de cada clube, equipe, atleta ou lutador
  /times/                    índice de clubes, equipes e atletas
  /quem-somos/ /contato/ /anuncie/ /politica-de-privacidade/ /termos-de-uso/
  /assets/site.css /assets/logo.png /assets/og.png
  /sitemap.xml /news-sitemap.xml /robots.txt

Rode depois de mexer no index.html e antes do tools/check.py. Nunca edite à mão os arquivos gerados:
eles são apagados e refeitos a cada execução (a lista fica em .generated).
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
SITE = "https://tvarenaesportes.com.br"
MANIFEST = os.path.join(ROOT, ".generated")
TZ = dt.timezone(dt.timedelta(hours=-3))
NOW = dt.datetime.now(TZ)

SPORTS = {"futebol": "Futebol", "volei": "Vôlei", "basquete": "Basquete",
          "lutas": "Lutas", "motor": "Motor", "tenis": "Tênis"}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
MIN_PARAGRAPHS = 3  # notas muito curtas não ganham página própria (conteúdo raso prejudica o site no Google)

esc = lambda s: html.escape(str(s or ""), quote=True)


def slugify(s, n=70):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].rstrip("-")


def parse_date(date, hora=None):
    """'14/10' + '07h20' -> datetime (ano inferido: datas 'no futuro' além de 2 meses são do ano anterior)."""
    m = re.match(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", date or "")
    if not m:
        return None
    d, mo, y = int(m[1]), int(m[2]), int(m[3] or NOW.year)
    if not m[3] and (mo - NOW.month) > 2:
        y -= 1
    h = mi = 0
    hm = re.match(r"(\d{1,2})h(\d{2})?", hora or "")
    if hm:
        h, mi = int(hm[1]), int(hm[2] or 0)
    try:
        return dt.datetime(y, mo, d, h, mi, tzinfo=TZ)
    except ValueError:
        return None


def nice_date(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}" if d else ""


# --------------------------------------------------------------------------- extração
def extract():
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file://" + INDEX)
        pg.wait_for_timeout(700)
        data = pg.evaluate("""()=>{var T=TVA;
          var eq={};Object.keys(T.EQ).forEach(function(sp){eq[sp]=T.EQ[sp].map(function(r){return [r[0],r[1]];});});
          return {
            teams:T.TEAMS.map(function(r){var t=T.TEAM[r[0]];return [t.slug,t.name];}),
            eq:eq,
            plantao:T.PLANTAO.map(function(p){return {id:p.id,sp:p.sp,quem:p.quem||[],k:p.k,t:p.t,d:p.d,date:p.date,hora:p.hora||'',body:p.body,src:p.src||[]};}),
            extra:T.EXTRA.map(function(e,i){return {id:e.id,i:i,sp:e.sport||'',teams:e.teams||[],k:e.k,t:e.t,d:e.d,date:e.date,body:e.body||[],src:e.src||[]};}),
            games:T.GAMES.map(function(g){return {id:g.id,teams:[g.g[0],g.g[2]],k:g.k,date:g.date,src:g.src||[],n:(g.ctx||[]).length+2};})
          };}""")
        out.update(data)

        # matéria principal da home (HTML fixo em #view-article)
        pg.evaluate("()=>{location.hash='materia'}")
        pg.wait_for_timeout(250)
        out["materia"] = pg.evaluate("""()=>{var a=document.querySelector('#view-article article');
          return {html:a.outerHTML,t:a.querySelector('h1').textContent.trim(),d:(a.querySelector('.dek')||{}).textContent||'',
                  k:(a.querySelector('.kicker')||{}).textContent||'',meta:a.querySelector('.meta').textContent,
                  n:a.querySelectorAll('.body p').length}}""")

        # renderiza cada matéria como o próprio site faz
        hrefs = [x["href"] for x in plan_items(out)]
        out["rendered"] = {}
        for h in hrefs:
            pg.evaluate("h=>{location.hash=h}", h)
            pg.wait_for_function("()=>document.querySelector('#teamsRoot article.article h1')", timeout=5000)
            pg.wait_for_timeout(30)
            out["rendered"][h] = pg.evaluate("""()=>{var a=document.querySelector('#teamsRoot article.article');
              return {html:a.outerHTML,t:a.querySelector('h1').textContent.trim(),d:(a.querySelector('.dek')||{}).textContent||''}}""")
            pg.evaluate("()=>{document.getElementById('teamsRoot').innerHTML=''}")
        b.close()
    if errs:
        print("ERROS de JavaScript ao ler o index.html:", *errs[:5], sep="\n  ")
        sys.exit(1)
    return out


def plan_items(data):
    """Lista canônica de matérias: uma URL por assunto (a mesma nota do plantão aparece em vários clubes)."""
    items, seen = [], set()
    team_ok = {s for s, _ in data["teams"]}
    eq_ok = {sp: {s for s, _ in rows} for sp, rows in data["eq"].items()}

    def valid(sp, sl):
        return sl in team_ok if sp == "futebol" else sl in eq_ok.get(sp, set())

    for p in data["plantao"]:
        if p["sp"] not in SPORTS:
            continue
        quem = [s for s in p["quem"] if valid(p["sp"], s)]
        href = f"#an-{p['sp']}-{quem[0]}-p-{p['id']}" if quem else f"#nota-p-{p['id']}"
        alias = [f"#an-{p['sp']}-{s}-p-{p['id']}" for s in quem] + [f"#nota-p-{p['id']}"]
        items.append(dict(kind="plantao", id=p["id"], href=href, alias=alias, sp=p["sp"], who=quem,
                          k=p["k"], date=parse_date(p["date"], p["hora"]), src=p["src"], n=len(p["body"])))
        seen.add("p-" + p["id"])
    for e in data["extra"]:
        if e["id"] and e["id"] in seen:
            continue
        key = e["id"] if e["id"] else str(e["i"])
        sp = e["sp"] or "futebol"
        items.append(dict(kind="nota", id=slugify(key), href=f"#nota-{key}", alias=[f"#nota-{key}"], sp=sp,
                          who=[t for t in e["teams"] if valid(sp, t)], k=e["k"],
                          date=parse_date("25/09" if e["date"] == "Hoje" else e["date"]), src=e["src"], n=len(e["body"])))
    for g in data["games"]:
        d = parse_date(g["date"])
        gid = f"jogo-{slugify(g['id'])}-{d.strftime('%d%m') if d else ''}".rstrip("-")
        items.append(dict(kind="jogo", id=gid, href=f"#jogo-{g['id']}", alias=[f"#jogo-{g['id']}"], sp="futebol",
                          who=[t for t in g["teams"] if valid("futebol", t)], k=g["k"], date=d, src=g["src"], n=g["n"]))
    items = [x for x in items if x["n"] >= MIN_PARAGRAPHS]
    ids = set()
    for x in items:  # ids únicos
        base, i = x["id"], 2
        while x["id"] in ids:
            x["id"] = f"{base}-{i}"; i += 1
        ids.add(x["id"])
    return items


# --------------------------------------------------------------------------- modelo de página
CSS_HEAD = ""
ANALYTICS = ""  # bloco <!-- analytics --> copiado do index.html


def page(path, title, desc, body, *, og_type="website", jsonld=None, extra_head="", noindex=False):
    url = SITE + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#C8361B">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="TV Arena Esportes">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
{extra_head}<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<style>[hidden]{{display:none!important}}body{{margin:0}}</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Big+Shoulders+Display:wght@700;800;900&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={CSS_HEAD}">
{ld}
{ANALYTICS}</head>
<body class="static">
<div class="topbar">
  <div class="wrap">
    <span id="today"></span>
    <nav>
      <a class="live" href="/"><span class="dot"></span>Plantão esportivo</a>
      <a href="/anuncie/">Anuncie</a>
      <a href="/contato/">Fale com a redação</a>
    </nav>
  </div>
</div>
<header class="site wrap">
  <div class="brandrow">
    <a class="logo" href="/" aria-label="TV Arena Esportes, página inicial">
      <b><span>TV ARENA</span><span>ESPORTES</span></b>
      <i>O esporte contado de perto.</i>
    </a>
    <div class="actions">
      <a class="btn solid" href="/#whatsapp">Receber no WhatsApp</a>
    </div>
  </div>
  <nav class="mainnav" aria-label="Editorias">
    <a href="/">Início</a>
    <a href="/times/">Times</a>
    <a href="/#classificacao">Classificação</a>
    <a href="/futebol/">Futebol</a>
    <a href="/basquete/">Basquete</a>
    <a href="/volei/">Vôlei</a>
    <a href="/lutas/">Lutas</a>
    <a href="/motor/">Motor</a>
    <a href="/tenis/">Tênis</a>
    <a href="/noticias/">Notícias</a>
  </nav>
</header>
<main>
{body}
</main>
{FOOTER}
<script>
try{{var s=new Date().toLocaleDateString('pt-BR',{{weekday:'long',day:'numeric',month:'long',year:'numeric'}});
document.getElementById('today').textContent=s.charAt(0).toUpperCase()+s.slice(1);}}catch(e){{}}
</script>
</body>
</html>
"""


FOOTER = """<footer id="rodape">
  <div class="wrap">
    <div class="fgrid">
      <div class="fbrand">
        <b>TV ARENA <span>ESPORTES</span></b>
        <p>Jornalismo esportivo independente. Notícias, vídeos e transmissões do esporte local e nacional.</p>
      </div>
      <div class="fcol"><strong>EDITORIAS</strong><a href="/futebol/">Futebol</a><a href="/basquete/">Basquete</a><a href="/volei/">Vôlei</a><a href="/lutas/">Lutas</a><a href="/motor/">Motor</a><a href="/tenis/">Tênis</a><a href="/times/">Times</a><a href="/noticias/">Todas as notícias</a></div>
      <div class="fcol"><strong>INSTITUCIONAL</strong><a href="/quem-somos/">Quem somos</a><a href="/quem-somos/#expediente">Expediente</a><a href="/anuncie/">Anuncie</a><a href="/politica-de-privacidade/">Política de privacidade</a><a href="/termos-de-uso/">Termos de uso</a></div>
      <div class="fcol"><strong>SIGA</strong><a href="/#whatsapp">Canal no WhatsApp</a></div>
      <div class="fcol"><strong>REDAÇÃO</strong><a class="mail" href="mailto:tvarenaesportes@gmail.com">tvarenaesportes@gmail.com</a><span>São Paulo (SP)</span><a href="/contato/">Contato</a></div>
    </div>
    <div class="legal"><span>© {year} TV Arena Esportes · CNPJ 53.743.776/0001-68</span><span>Todos os direitos reservados</span></div>
  </div>
</footer>""".replace("{year}", str(NOW.year))

STATIC_CSS = """
/* páginas estáticas (geradas por tools/build_pages.py) */
.static .sx-page{padding-block:28px 64px}
.static .sx-page h1{font-size:clamp(40px,7vw,76px);margin:6px 0 10px}
.static .sx-page .sx-lead{font-family:var(--serif);font-size:19px;color:var(--ink-2);max-width:760px;margin:0 0 28px;line-height:1.5}
.static .sx-list{list-style:none;margin:0;padding:0;border-top:2px solid var(--ink)}
.static .sx-list li{border-bottom:1px solid var(--rule)}
.static .sx-list a{display:grid;grid-template-columns:96px 1fr;gap:4px 18px;padding:16px 0}
.static .sx-list time{font-size:13px;font-weight:700;color:var(--muted);padding-top:3px}
.static .sx-list .k{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--accent)}
.static .sx-list b{display:block;font-size:19px;line-height:1.25;margin:2px 0 4px}
.static .sx-list a:hover b{color:var(--accent)}
.static .sx-list p{margin:0;color:var(--muted);font-size:15px;line-height:1.45}
@media(max-width:620px){.static .sx-list a{grid-template-columns:1fr}}
.static .sx-chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 32px;padding:0;list-style:none}
.static .sx-chips a{display:inline-block;border:1px solid var(--rule);background:var(--card);padding:8px 12px;font-size:14px;font-weight:600}
.static .sx-chips a:hover{border-color:var(--accent);color:var(--accent)}
.static .sx-chips small{color:var(--muted);font-weight:500;margin-left:4px}
.static h2.sx-sec{font-family:var(--display);text-transform:uppercase;font-size:32px;margin:36px 0 12px}
.static .sx-legal{max-width:760px;font-family:var(--serif);font-size:18px;line-height:1.6;color:var(--ink-2)}
.static .sx-legal h2{font-family:var(--sans);font-size:20px;color:var(--ink);margin:32px 0 8px}
.static .sx-legal a{color:var(--accent);text-decoration:underline}
.static .sx-legal ul{padding-left:22px}
.static .sx-more{margin-top:28px}
.static .sx-related{padding-top:0;border-top:1px solid var(--rule);margin-top:8px}
"""


def news_list(items, limit=None):
    rows = []
    for x in items[:limit] if limit else items:
        rows.append(f'<li><a href="/noticias/{x["id"]}/"><time datetime="{x["date"].isoformat() if x["date"] else ""}">{esc(x["date"].strftime("%d/%m/%Y") if x["date"] else "")}</time>'
                    f'<span><span class="k">{esc(x["k"])}</span><b>{esc(x["t"])}</b><p>{esc(x["d"])}</p></span></a></li>')
    return '<ul class="sx-list">' + "".join(rows) + "</ul>"


def crumbs_ld(parts):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                                for i, (n, u) in enumerate(parts)]}


ORG = {"@type": "NewsMediaOrganization", "name": "TV Arena Esportes", "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png", "width": 600, "height": 120},
       "email": "tvarenaesportes@gmail.com"}


# --------------------------------------------------------------------------- build
def main():
    global CSS_HEAD, ANALYTICS
    src = open(INDEX, encoding="utf-8").read()
    m = re.search(r"<!-- analytics.*?<!-- /analytics -->\n?", src, re.S)
    ANALYTICS = m.group(0) if m else ""
    data = extract()
    items = plan_items(data)

    # matéria principal da home
    mat = data["materia"]
    mdate = None
    mm = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", mat["meta"])
    if mm and mm[2] in MESES:
        mdate = dt.datetime(int(mm[3]), MESES.index(mm[2]) + 1, int(mm[1]), 6, 0, tzinfo=TZ)
    if mat["n"] >= MIN_PARAGRAPHS:
        mid = f"{mdate.strftime('%d%m') if mdate else 'materia'}-{slugify(mat['t'], 60)}"
        items.insert(0, dict(kind="materia", id=mid, href="#materia", alias=["#materia"], sp="futebol", who=[],
                             k=mat["k"], date=mdate, src=[], n=mat["n"], html=mat["html"], t=mat["t"], d=mat["d"]))

    for x in items:
        if x["kind"] != "materia":
            r = data["rendered"][x["href"]]
            x.update(html=r["html"], t=r["t"], d=r["d"])
    items.sort(key=lambda x: x["date"] or dt.datetime(2000, 1, 1, tzinfo=TZ), reverse=True)

    names = {("futebol", s): n for s, n in data["teams"]}
    for sp, rows in data["eq"].items():
        for s, n in rows:
            names[(sp, s)] = n
    by_who = {}
    for x in items:
        for s in x["who"]:
            by_who.setdefault((x["sp"], s), []).append(x)

    # mapa de links internos (#hash do app -> URL estática)
    hmap = {}
    for x in items:
        for a in x["alias"]:
            hmap[a] = f"/noticias/{x['id']}/"
    for (sp, s) in by_who:
        hmap[f"#time-{s}" if sp == "futebol" else f"#eq-{sp}-{s}"] = f"/{sp}/{s}/"
    for sp in SPORTS:
        hmap["#" + sp] = f"/{sp}/"
    hmap["#times"] = "/times/"
    hmap["#inicio"] = "/"

    def fix_links(h):
        def sub(m):
            href = html.unescape(m[1])
            if href.startswith("#"):
                return f'href="{esc(hmap.get(href, "/" + href))}"'
            return m[0]
        return re.sub(r'href="([^"]*)"', sub, h)

    # limpa o que foi gerado antes
    if os.path.exists(MANIFEST):
        for rel in open(MANIFEST, encoding="utf-8").read().split():
            pth = os.path.join(ROOT, rel)
            if os.path.isfile(pth):
                os.remove(pth)
        for d in sorted({os.path.dirname(r) for r in open(MANIFEST, encoding="utf-8").read().split()}, key=len, reverse=True):
            try:
                while d and os.path.isdir(os.path.join(ROOT, d)) and not os.listdir(os.path.join(ROOT, d)):
                    os.rmdir(os.path.join(ROOT, d)); d = os.path.dirname(d)
            except OSError:
                pass
    written, smap = [], []

    def write(rel, content, mode="w"):
        pth = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(pth), exist_ok=True)
        with open(pth, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
            f.write(content)
        written.append(rel)

    # assets
    css = re.findall(r"<style>(.*?)</style>", src, re.S)[1] + STATIC_CSS
    CSS_HEAD = hashlib.md5(css.encode()).hexdigest()[:8]
    write("assets/site.css", css)
    write("assets/icon.svg", "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='12' fill='#C8361B'/>"
          "<text x='32' y='44' font-family='Arial Black,Arial' font-weight='900' font-size='30' text-anchor='middle' fill='#fff'>TVA</text></svg>")
    render_images()

    # matérias
    for x in items:
        path = f"/noticias/{x['id']}/"
        when = x["date"]
        art = fix_links(x["html"]).replace('class="wrap article"', 'class="article"')
        sp_name = SPORTS.get(x["sp"], "Esportes")
        ld = [{"@context": "https://schema.org", "@type": "NewsArticle", "headline": x["t"][:110],
               "description": x["d"], "mainEntityOfPage": SITE + path, "inLanguage": "pt-BR",
               "datePublished": when.isoformat() if when else None, "dateModified": when.isoformat() if when else None,
               "image": [SITE + "/assets/og.png"], "articleSection": sp_name,
               "author": {"@type": "Organization", "name": "Redação TV Arena Esportes", "url": SITE + "/quem-somos/"},
               "publisher": ORG,
               "isBasedOn": [u for _, u in x["src"]] or None},
              crumbs_ld([("Início", "/"), (sp_name, f"/{x['sp']}/"), (x["t"][:80], path)])]
        ld[0] = {k: v for k, v in ld[0].items() if v is not None}
        head = (f'<meta property="article:published_time" content="{when.isoformat()}">\n' if when else "") + \
               f'<meta property="article:section" content="{esc(sp_name)}">\n'
        title = f"{x['t']} | TV Arena Esportes"
        rel = [y for s in x["who"] for y in by_who.get((x["sp"], s), []) if y is not x]
        rel += [y for y in items if y["sp"] == x["sp"] and y is not x]
        seen_rel, rel5 = set(), []
        for y in rel:
            if y["id"] not in seen_rel:
                seen_rel.add(y["id"]); rel5.append(y)
            if len(rel5) == 5:
                break
        who_chips = "".join(f'<li><a href="/{x["sp"]}/{s}/">{esc(names.get((x["sp"], s), s))}</a></li>' for s in x["who"])
        more = (f'<section class="wrap sx-page sx-related"><h2 class="sx-sec">Leia também</h2>'
                + (f'<ul class="sx-chips">{who_chips}</ul>' if who_chips else "") + news_list(rel5) + "</section>")
        write(path.strip("/") + "/index.html",
              page(path, title, x["d"] or x["t"], f'<section class="wrap teams-page">{art}</section>{more}',
                   og_type="article", jsonld=ld, extra_head=head))
        smap.append((path, when, x))

    # páginas de clube / equipe / atleta
    for (sp, s), lst in sorted(by_who.items()):
        n = names.get((sp, s), s)
        path = f"/{sp}/{s}/"
        app = f"/#time-{s}" if sp == "futebol" else f"/#eq-{sp}-{s}"
        body = (f'<section class="wrap sx-page"><span class="kicker">{esc(SPORTS[sp])}</span>'
                f'<h1 class="display">{esc(n)}</h1><p class="sx-lead">Notícias sobre {esc(n)} na TV Arena Esportes: '
                f'{len(lst)} {"matéria" if len(lst) == 1 else "matérias"}, da mais recente para a mais antiga.</p>'
                + news_list(lst) +
                f'<p class="sx-more"><a class="btn" href="{app}">Tabela, jogos e calendário de {esc(n)}</a></p></section>')
        desc = f"Últimas notícias de {n}: " + "; ".join(x["t"] for x in lst[:2])
        write(path.strip("/") + "/index.html",
              page(path, f"{n}: notícias | TV Arena Esportes", desc[:300], body,
                   jsonld=[crumbs_ld([("Início", "/"), (SPORTS[sp], f"/{sp}/"), (n, path)])]))
        smap.append((path, lst[0]["date"], None))

    # editorias
    for sp, spn in SPORTS.items():
        lst = [x for x in items if x["sp"] == sp]
        who = sorted([(names.get((sp, s), s), s, len(v)) for (q, s), v in by_who.items() if q == sp])
        chips = "".join(f'<li><a href="/{sp}/{s}/">{esc(n)}<small>{c}</small></a></li>' for n, s, c in who)
        body = (f'<section class="wrap sx-page"><span class="kicker">Editoria</span><h1 class="display">{esc(spn)}</h1>'
                f'<p class="sx-lead">As últimas notícias de {esc(spn.lower())} na TV Arena Esportes.</p>'
                + (f'<ul class="sx-chips">{chips}</ul>' if chips else "")
                + (news_list(lst, 60) if lst else '<p class="sx-lead">Nenhuma matéria publicada nesta editoria ainda.</p>')
                + f'<p class="sx-more"><a class="btn" href="/#{sp}">Placares e calendário de {esc(spn.lower())}</a></p></section>')
        write(f"{sp}/index.html", page(f"/{sp}/", f"{spn}: notícias | TV Arena Esportes",
                                       f"Últimas notícias de {spn.lower()}: resultados, bastidores e o que vem a seguir, com fontes.", body,
                                       noindex=not lst))
        if lst:
            smap.append((f"/{sp}/", lst[0]["date"], None))

    # arquivo de notícias
    body = ('<section class="wrap sx-page"><span class="kicker">Arquivo</span><h1 class="display">Todas as notícias</h1>'
            f'<p class="sx-lead">{len(items)} matérias publicadas pela redação da TV Arena Esportes, da mais recente para a mais antiga.</p>'
            + news_list(items) + "</section>")
    write("noticias/index.html", page("/noticias/", "Todas as notícias | TV Arena Esportes",
                                      "Arquivo com todas as matérias da TV Arena Esportes: futebol, vôlei, basquete, lutas, automobilismo e tênis.", body))
    smap.append(("/noticias/", items[0]["date"] if items else None, None))

    # índice de times
    blocks = ""
    for sp, spn in SPORTS.items():
        who = sorted([(names.get((sp, s), s), s, len(v)) for (q, s), v in by_who.items() if q == sp])
        if who:
            blocks += f'<h2 class="sx-sec">{esc(spn)}</h2><ul class="sx-chips">' + "".join(
                f'<li><a href="/{sp}/{s}/">{esc(n)}<small>{c}</small></a></li>' for n, s, c in who) + "</ul>"
    write("times/index.html", page("/times/", "Times, equipes e atletas | TV Arena Esportes",
                                   "Notícias de cada clube das Séries A e B, equipes de vôlei, basquete e automobilismo, lutadores e tenistas.",
                                   '<section class="wrap sx-page"><span class="kicker">Times</span><h1 class="display">Times, equipes e atletas</h1>'
                                   '<p class="sx-lead">Escolha um clube, equipe ou atleta para ver todas as notícias publicadas sobre ele.</p>'
                                   + blocks + '<p class="sx-more"><a class="btn" href="/#times">Escudos, tabelas e calendários</a></p></section>'))
    smap.append(("/times/", NOW, None))

    # institucionais
    from institucional import PAGES
    for slug, (title, desc, html_body) in PAGES.items():
        write(f"{slug}/index.html", page(f"/{slug}/", f"{title} | TV Arena Esportes", desc,
                                         f'<section class="wrap sx-page"><span class="kicker">TV Arena Esportes</span><h1 class="display">{esc(title)}</h1>'
                                         f'<div class="sx-legal">{html_body}</div></section>'))
        smap.append((f"/{slug}/", None, None))

    # sitemaps e robots
    urls = [f"  <url><loc>{SITE}/</loc><lastmod>{NOW.date().isoformat()}</lastmod><changefreq>hourly</changefreq><priority>1.0</priority></url>"]
    for path, when, _ in smap:
        lm = f"<lastmod>{when.date().isoformat()}</lastmod>" if when else ""
        urls.append(f"  <url><loc>{SITE}{path}</loc>{lm}</url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    recent = [(p, w, x) for p, w, x in smap if x and w and (NOW - w).total_seconds() < 2 * 86400]
    news = [f"  <url><loc>{SITE}{p}</loc><news:news><news:publication><news:name>TV Arena Esportes</news:name><news:language>pt</news:language>"
            f"</news:publication><news:publication_date>{w.isoformat()}</news:publication_date><news:title>{esc(x['t'])}</news:title></news:news></url>"
            for p, w, x in recent]
    write("news-sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + "\n".join(news) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /data/\n\nSitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/news-sitemap.xml\n")

    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(written)) + "\n")
    print(f"OK — {len(items)} matérias, {len(by_who)} páginas de clubes/equipes/atletas, "
          f"{len(news)} no news-sitemap, {len(written)} arquivos gerados.")


def render_images():
    """Logo (para o Google) e imagem padrão de compartilhamento (WhatsApp, redes)."""
    from playwright.sync_api import sync_playwright
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=Archivo:wght@600&display=swap">'
    logo = f"""<html><head>{fonts}<style>body{{margin:0}}div{{width:600px;height:120px;display:flex;align-items:center;justify-content:center;gap:14px;
      background:#fff;font-family:'Big Shoulders Display',Impact,sans-serif;font-weight:900;font-size:78px;letter-spacing:-1px;color:#15171B}}
      span{{color:#C8361B}}</style></head><body><div>TV ARENA <span>ESPORTES</span></div></body></html>"""
    og = f"""<html><head>{fonts}<style>body{{margin:0}}.c{{width:1200px;height:630px;background:#15171B;color:#EFEFEA;display:flex;flex-direction:column;
      justify-content:center;padding:0 90px;box-sizing:border-box;font-family:'Big Shoulders Display',Impact,sans-serif;position:relative}}
      b{{font-size:150px;line-height:.9;font-weight:900}} b span{{color:#C8361B;display:block}}
      i{{font-family:Archivo,Arial,sans-serif;font-style:normal;font-weight:600;font-size:34px;margin-top:30px;color:#D9D5CB}}
      .bar{{position:absolute;left:0;top:0;bottom:0;width:22px;background:#C8361B}}</style></head>
      <body><div class="c"><div class="bar"></div><b>TV ARENA<span>ESPORTES</span></b><i>O esporte contado de perto.</i></div></body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, markup, w, h in (("logo.png", logo, 600, 120), ("og.png", og, 1200, 630)):
            if os.path.exists(os.path.join(ROOT, "assets", name)):
                continue  # imagens fixas: geradas uma vez e mantidas no repositório
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.set_content(markup)
            try:
                pg.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            pg.wait_for_timeout(300)
            os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
            with open(os.path.join(ROOT, "assets", name), "wb") as f:
                f.write(pg.screenshot())
        b.close()


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
