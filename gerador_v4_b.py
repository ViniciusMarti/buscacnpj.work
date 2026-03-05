#!/usr/bin/env python3
"""
gerador_v4_b.py — BuscaCNPJ.work
Gera páginas HTML de empresa com o novo design (consistente com a home).
"""

import requests, os, json, time, logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

BASE_DIR      = "."           # raiz do projeto
DOMAIN        = "https://buscacnpj.work"
PROGRESS_FILE = "progresso.json"
MAX_WORKERS   = 8
SLEEP         = 0.4
SAVE_EVERY    = 50
API_BRASIL    = "https://brasilapi.com.br/api/cnpj/v1/"
API_MINHA_REC = "https://minhareceita.org/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gerador.log", encoding="utf-8"),
    ],
)
log  = logging.getLogger(__name__)
lock = Lock()

# ── Formatadores ──────────────────────────────────────────────────────────────
def fmt_cnpj(c):
    c = c.zfill(14)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"

def fmt_brl(v):
    try:
        return f"R$\u00a0{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except:
        return "R$\u00a00,00"

def fmt_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return d or "—"

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

# ── Normaliza dados da API ────────────────────────────────────────────────────
def norm(data):
    cnpj = "".join(x for x in data.get("cnpj","") if x.isdigit())
    return {
        "cnpj":             cnpj,
        "razao_social":     data.get("razao_social") or data.get("razão_social") or "N/A",
        "nome_fantasia":    data.get("nome_fantasia") or data.get("nome_comercial") or "",
        "situacao":         data.get("descricao_situacao_cadastral") or data.get("descrição_situação_cadastral") or "N/A",
        "data_abertura":    fmt_date(data.get("data_inicio_atividade","")),
        "porte":            data.get("porte") or "—",
        "natureza_juridica":data.get("natureza_juridica") or "—",
        "capital_social":   fmt_brl(data.get("capital_social", 0)),
        "email":            data.get("email") or "",
        "telefone":         data.get("ddd_telefone_1") or "",
        "logradouro":       data.get("logradouro") or "—",
        "numero":           data.get("numero") or "S/N",
        "complemento":      data.get("complemento") or "",
        "bairro":           data.get("bairro") or "—",
        "municipio":        data.get("municipio") or data.get("município") or "—",
        "uf":               data.get("uf") or "—",
        "cep":              data.get("cep") or "—",
        "cnae_principal":   data.get("cnae_fiscal_descricao") or data.get("cnae_fiscal_descrição") or "—",
        "cnae_codigo":      str(data.get("cnae_fiscal","") or ""),
        "cnaes_secundarios":data.get("cnaes_secundarios", []),
        "qsa":              data.get("qsa", []),
    }

# ── CSS (mesmo da home) ───────────────────────────────────────────────────────
CSS = """<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:#ffffff; --bg2:#f8f8f8; --bg3:#f0f0f0;
    --text:#1a1a1a; --text2:#555555; --muted:#999999; --border:#e8e8e8;
    --card-bg:#ffffff; --btn-bg:#111111; --btn-fg:#ffffff; --accent:#0055cc;
    --shadow:0 2px 12px rgba(0,0,0,0.07); --shadow2:0 8px 32px rgba(0,0,0,0.10);
    --green-bg:#f0fdf4; --green-tx:#166534; --green-bd:#bbf7d0;
    --red-bg:#fef2f2;   --red-tx:#991b1b;   --red-bd:#fecaca;
    --yellow-bg:#fffbeb;--yellow-tx:#92400e;--yellow-bd:#fde68a;
  }
  @media (prefers-color-scheme:dark) {
    :root {
      --bg:#0f0f0f; --bg2:#1a1a1a; --bg3:#222222;
      --text:#f0f0f0; --text2:#aaaaaa; --muted:#666666; --border:#2a2a2a;
      --card-bg:#1a1a1a; --btn-bg:#f0f0f0; --btn-fg:#111111; --accent:#6699ff;
      --shadow:0 2px 12px rgba(0,0,0,0.4); --shadow2:0 8px 32px rgba(0,0,0,0.5);
      --green-bg:#052e16; --green-tx:#86efac; --green-bd:#166534;
      --red-bg:#450a0a;   --red-tx:#fca5a5;   --red-bd:#991b1b;
      --yellow-bg:#451a03;--yellow-tx:#fcd34d;--yellow-bd:#92400e;
    }
  }
  html { scroll-behavior:smooth; }
  body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         line-height:1.7; color:var(--text); background:var(--bg); font-size:1rem; }
  header { padding:0 24px; height:60px; display:flex; align-items:center;
           border-bottom:1px solid var(--border); position:sticky; top:0;
           background:var(--bg); backdrop-filter:blur(12px);
           -webkit-backdrop-filter:blur(12px); z-index:999; }
  .hi { max-width:1100px; width:100%; margin:0 auto;
        display:flex; align-items:center; justify-content:space-between; }
  .logo { font-weight:800; font-size:1.05rem; text-decoration:none;
          color:var(--text); letter-spacing:-.3px; }
  .logo span { color:var(--accent); }
  nav { display:flex; gap:24px; align-items:center; }
  nav a { text-decoration:none; color:var(--text2); font-size:.9rem; transition:color .15s; }
  nav a:hover { color:var(--text); }
  .hs { display:flex; gap:6px; align-items:center; }
  .hs input { padding:7px 12px; font-size:.88rem; border:1.5px solid var(--border);
              border-radius:8px; background:var(--bg); color:var(--text);
              outline:none; font-family:inherit; width:200px; transition:border-color .15s; }
  .hs input:focus { border-color:var(--accent); }
  .hs input::placeholder { color:var(--muted); }
  .hs button { padding:7px 14px; background:var(--btn-bg); color:var(--btn-fg);
               border:none; border-radius:8px; font-size:.85rem; font-weight:700;
               cursor:pointer; font-family:inherit; white-space:nowrap; transition:opacity .15s; }
  .hs button:hover { opacity:.85; }
  @media(max-width:700px){.hs{display:none;}}
  .wrap { max-width:860px; margin:0 auto; padding:32px 20px 64px; }
  .bc { font-size:.8rem; color:var(--muted); margin-bottom:28px;
        display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
  .bc a { color:var(--muted); text-decoration:none; transition:color .15s; }
  .bc a:hover { color:var(--text); }
  .bc-sep { color:var(--border); }
  .badge { display:inline-flex; align-items:center; gap:6px; padding:4px 14px;
           border-radius:20px; font-size:.75rem; font-weight:700; letter-spacing:.5px;
           text-transform:uppercase; border:1px solid transparent; margin-bottom:20px; }
  .badge-ativa    { background:var(--green-bg);  color:var(--green-tx);  border-color:var(--green-bd); }
  .badge-baixada  { background:var(--red-bg);    color:var(--red-tx);    border-color:var(--red-bd); }
  .badge-inapta   { background:var(--yellow-bg); color:var(--yellow-tx); border-color:var(--yellow-bd); }
  .badge-suspensa { background:var(--yellow-bg); color:var(--yellow-tx); border-color:var(--yellow-bd); }
  h1 { font-size:clamp(1.5rem,4vw,2.1rem); font-weight:900; color:var(--text);
       letter-spacing:-.5px; line-height:1.2; margin-bottom:8px; }
  .cnpj-fmt { font-size:1rem; color:var(--muted); font-weight:400;
              margin-bottom:28px; letter-spacing:.5px; }
  .sec-label { font-size:.7rem; font-weight:700; text-transform:uppercase;
               letter-spacing:1.5px; color:var(--accent);
               border-bottom:1px solid var(--border);
               padding-bottom:10px; margin:36px 0 20px; }
  .fields { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
            gap:20px 32px; }
  .field label { display:block; font-size:.7rem; font-weight:700;
                 text-transform:uppercase; letter-spacing:.5px;
                 color:var(--muted); margin-bottom:4px; }
  .field p { font-size:.97rem; color:var(--text); margin:0; line-height:1.5; }
  .addr-card { background:var(--bg2); border:1px solid var(--border); border-radius:10px;
               padding:20px 24px; display:flex; gap:16px; align-items:flex-start; }
  .addr-icon { font-size:1.4rem; flex-shrink:0; margin-top:2px; }
  .addr-card p { margin:0; color:var(--text2); font-size:.95rem; line-height:1.7; }
  .addr-card strong { color:var(--text); }
  ul.cl { list-style:none; }
  ul.cl li { padding:13px 0; border-bottom:1px solid var(--border);
             display:flex; gap:12px; align-items:flex-start; }
  ul.cl li:last-child { border-bottom:none; }
  .li-icon { font-size:1rem; flex-shrink:0; margin-top:2px; }
  .li-body strong { display:block; font-size:.95rem; font-weight:700; color:var(--text); }
  .li-body span { font-size:.82rem; color:var(--muted); }
  .tag { display:inline-block; padding:2px 9px; border-radius:6px; font-size:.72rem;
         font-weight:600; background:var(--bg3); color:var(--text2);
         border:1px solid var(--border); }
  .fonte { margin-top:40px; padding:14px 18px; background:var(--bg2);
           border:1px solid var(--border); border-radius:8px;
           font-size:.82rem; color:var(--muted);
           display:flex; gap:10px; align-items:flex-start; }
  .fonte p { margin:0; color:var(--muted); font-size:.82rem; }
  .fonte a { color:var(--accent); }
  footer { background:var(--bg2); border-top:1px solid var(--border);
           padding:40px 24px; text-align:center; }
  .fn { display:flex; justify-content:center; gap:24px; flex-wrap:wrap; margin-bottom:16px; }
  .fn a { color:var(--muted); text-decoration:none; font-size:.87rem; transition:color .15s; }
  .fn a:hover { color:var(--text); }
  footer p { color:var(--muted); font-size:.82rem; }
  footer a { color:var(--muted); }
  @media(max-width:600px){.fields{grid-template-columns:1fr 1fr;}}
  @media(max-width:400px){.fields{grid-template-columns:1fr;}}
</style>"""

# ── Header / Footer reutilizáveis ─────────────────────────────────────────────
HEADER = f"""<header>
  <div class="hi">
    <a class="logo" href="{DOMAIN}/">busca<span>CNPJ</span>.work</a>
    <form class="hs" action="{DOMAIN}/"
          onsubmit="var v=this.qs.value.replace(/\\D/g,'');if(v.length===14){{window.location='{DOMAIN}/cnpj/'+v+'/';return false;}}alert('CNPJ inválido.');return false;">
      <input type="text" name="qs" maxlength="18" placeholder="Consultar outro CNPJ…"
             autocomplete="off" inputmode="numeric"
             oninput="var v=this.value.replace(/\\D/g,'').slice(0,14);
               if(v.length>12)v=v.slice(0,2)+'.'+v.slice(2,5)+'.'+v.slice(5,8)+'/'+v.slice(8,12)+'-'+v.slice(12);
               else if(v.length>8)v=v.slice(0,2)+'.'+v.slice(2,5)+'.'+v.slice(5,8)+'/'+v.slice(8);
               else if(v.length>5)v=v.slice(0,2)+'.'+v.slice(2,5)+'.'+v.slice(5);
               else if(v.length>2)v=v.slice(0,2)+'.'+v.slice(2);
               this.value=v;">
      <button type="submit">Consultar</button>
    </form>
    <nav>
      <a href="{DOMAIN}/">Início</a>
      <a href="{DOMAIN}/sobre/">Sobre</a>
    </nav>
  </div>
</header>"""

FOOTER = f"""<footer>
  <nav class="fn">
    <a href="{DOMAIN}/">Início</a>
    <a href="{DOMAIN}/sobre/">Sobre</a>
    <a href="{DOMAIN}/privacidade/">Privacidade</a>
    <a href="{DOMAIN}/contato/">Contato</a>
  </nav>
  <p>© 2026 <a href="{DOMAIN}/">BuscaCNPJ.work</a> — Dados públicos da Receita Federal do Brasil.</p>
</footer>"""

# ── Gerador de HTML da empresa ────────────────────────────────────────────────
def gerar_html(data):
    d       = norm(data)
    nome    = esc(d["nome_fantasia"] or d["razao_social"])
    razao   = esc(d["razao_social"])
    cnpj_f  = fmt_cnpj(d["cnpj"])
    today   = datetime.now().strftime("%d/%m/%Y")

    # Badge de situação
    sit = d["situacao"].upper()
    if "ATIVA" in sit:
        badge_cls, badge_icon, badge_txt = "badge-ativa",    "✅", "Ativa"
    elif any(x in sit for x in ("BAIXADA","CANCELADA")):
        badge_cls, badge_icon, badge_txt = "badge-baixada",  "🔴", d["situacao"].title()
    elif "INAPTA" in sit:
        badge_cls, badge_icon, badge_txt = "badge-inapta",   "⚠️", "Inapta"
    else:
        badge_cls, badge_icon, badge_txt = "badge-suspensa",  "🟡", d["situacao"].title()

    # Sócios
    socios_html = ""
    if d["qsa"]:
        itens = ""
        for s in d["qsa"]:
            nm  = esc(s.get("nome_socio") or s.get("nome") or "—")
            qual = esc(s.get("qualificacao_socio") or s.get("qualificação_socio") or "")
            since = s.get("data_entrada_sociedade","")
            since_fmt = fmt_date(since) if since else ""
            det = " · ".join(filter(None, [qual, f"Desde {since_fmt}" if since_fmt else ""]))
            itens += f"""<li>
          <div class="li-icon">👤</div>
          <div class="li-body">
            <strong>{nm}</strong>
            {f'<span>{det}</span>' if det else ''}
          </div>
        </li>\n"""
        socios_html = f"""
  <p class="sec-label">Quadro de Sócios e Administradores</p>
  <ul class="cl">{itens}</ul>"""

    # CNAE Principal
    cnae_p = ""
    if d["cnae_principal"] and d["cnae_principal"] != "—":
        cod = f' <span class="tag">{esc(d["cnae_codigo"])}</span>' if d["cnae_codigo"] else ""
        cnae_p = f"""
  <p class="sec-label">Atividade Econômica Principal</p>
  <ul class="cl">
    <li>
      <div class="li-icon">📊</div>
      <div class="li-body">
        <strong>{esc(d["cnae_principal"])}</strong>
        <span>CNAE {esc(d["cnae_codigo"])}</span>
      </div>
    </li>
  </ul>"""

    # CNAEs Secundários
    cnae_s = ""
    if d["cnaes_secundarios"]:
        itens = ""
        for c in d["cnaes_secundarios"][:10]:
            desc = esc(c.get("descricao") or c.get("descrição") or "—")
            cod  = esc(str(c.get("codigo") or c.get("código") or ""))
            itens += f"""<li>
          <div class="li-icon">📋</div>
          <div class="li-body">
            <strong>{desc}</strong>
            {f'<span>CNAE {cod}</span>' if cod else ''}
          </div>
        </li>\n"""
        cnae_s = f"""
  <p class="sec-label">Atividades Secundárias</p>
  <ul class="cl">{itens}</ul>"""

    # Endereço
    end_linha1 = esc(d["logradouro"])
    if d["numero"] and d["numero"] != "S/N":
        end_linha1 += f', {esc(d["numero"])}'
    if d["complemento"]:
        end_linha1 += f' — {esc(d["complemento"])}'

    # Campos opcionais
    tel_html   = f'<div class="field"><label>Telefone</label><p>{esc(d["telefone"])}</p></div>' if d["telefone"] else ""
    email_html = f'<div class="field"><label>E-mail</label><p>{esc(d["email"])}</p></div>'      if d["email"]    else ""

    # Schema.org
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": d["razao_social"],
        "legalName": d["razao_social"],
        "taxID": cnpj_f,
        "url": f"{DOMAIN}/cnpj/{d['cnpj']}/",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": f'{d["logradouro"]}, {d["numero"]}',
            "addressLocality": d["municipio"],
            "addressRegion": d["uf"],
            "postalCode": d["cep"],
            "addressCountry": "BR"
        }
    }
    if d["nome_fantasia"]:
        schema["alternateName"] = d["nome_fantasia"]

    desc_meta = (f'Dados do CNPJ {cnpj_f} — {d["razao_social"]}. '
                 f'Situação: {d["situacao"]}. '
                 f'Endereço: {d["logradouro"]}, {d["municipio"]} - {d["uf"]}. '
                 f'Consulta gratuita da Receita Federal.')

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nome} — CNPJ {cnpj_f} | BuscaCNPJ.work</title>
  <meta name="description" content="{esc(desc_meta)}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
  <link rel="canonical" href="{DOMAIN}/cnpj/{d['cnpj']}/">
  <meta property="og:type"        content="website">
  <meta property="og:title"       content="{nome} — CNPJ {cnpj_f}">
  <meta property="og:description" content="{esc(desc_meta)}">
  <meta property="og:url"         content="{DOMAIN}/cnpj/{d['cnpj']}/">
  <meta property="og:site_name"   content="BuscaCNPJ.work">
  <meta property="og:locale"      content="pt_BR">
  <meta name="twitter:card"        content="summary">
  <meta name="twitter:title"       content="{nome} — CNPJ {cnpj_f}">
  <meta name="twitter:description" content="{esc(desc_meta)}">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
  {CSS}
</head>
<body>
{HEADER}

<div class="wrap">

  <div class="bc">
    <a href="{DOMAIN}/">Início</a>
    <span class="bc-sep">/</span>
    <a href="{DOMAIN}/">CNPJ</a>
    <span class="bc-sep">/</span>
    <span>{cnpj_f}</span>
  </div>

  <div class="badge {badge_cls}">{badge_icon} {badge_txt}</div>
  <h1>{razao}</h1>
  <p class="cnpj-fmt">CNPJ {cnpj_f}</p>

  <p class="sec-label">Dados Gerais</p>
  <div class="fields">
    <div class="field"><label>Razão Social</label><p>{razao}</p></div>
    <div class="field"><label>Nome Fantasia</label><p>{esc(d["nome_fantasia"]) or "—"}</p></div>
    <div class="field"><label>Situação Cadastral</label><p>{esc(d["situacao"])}</p></div>
    <div class="field"><label>Data de Abertura</label><p>{esc(d["data_abertura"])}</p></div>
    <div class="field"><label>Porte</label><p>{esc(d["porte"])}</p></div>
    <div class="field"><label>Natureza Jurídica</label><p>{esc(d["natureza_juridica"])}</p></div>
    <div class="field"><label>Capital Social</label><p>{esc(d["capital_social"])}</p></div>
    <div class="field"><label>CNPJ</label><p>{cnpj_f}</p></div>
    {tel_html}
    {email_html}
  </div>

  <p class="sec-label">Endereço</p>
  <div class="addr-card">
    <div class="addr-icon">📍</div>
    <div>
      <p>
        <strong>{end_linha1}</strong><br>
        {esc(d["bairro"])} — {esc(d["municipio"])} / {esc(d["uf"])}<br>
        CEP {esc(d["cep"])}
      </p>
    </div>
  </div>

  {cnae_p}
  {cnae_s}
  {socios_html}

  <div class="fonte">
    <span>ℹ️</span>
    <p>Dados públicos provenientes da <strong>Receita Federal do Brasil</strong>.
    Atualizado em {today}.
    Para correções, acesse o <a href="https://www.gov.br/receitafederal" target="_blank" rel="noopener">portal da Receita Federal</a>
    ou <a href="{DOMAIN}/contato/">entre em contato</a>.</p>
  </div>

</div>

{FOOTER}
</body>
</html>"""

# ── API ────────────────────────────────────────────────────────────────────────
def buscar_api(cnpj: str):
    for url in [f"{API_BRASIL}{cnpj}", f"{API_MINHA_REC}{cnpj}"]:
        try:
            r = requests.get(url, timeout=15,
                             headers={"User-Agent": "BuscaCNPJ.work/1.0"})
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(SLEEP)
    return None

# ── Salvar página ─────────────────────────────────────────────────────────────
def salvar_pagina(cnpj: str, html: str):
    path = os.path.join(BASE_DIR, "cnpj", cnpj, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

# ── Processar um CNPJ ─────────────────────────────────────────────────────────
def processar(cnpj: str, prog: dict):
    path = os.path.join(BASE_DIR, "cnpj", cnpj, "index.html")
    if os.path.exists(path):
        return "skip"
    data = buscar_api(cnpj)
    if not data:
        log.warning("⚠️  Sem dados: %s", cnpj)
        return "erro"
    try:
        html = gerar_html(data)
        salvar_pagina(cnpj, html)
        d = norm(data)
        nome = d["nome_fantasia"] or d["razao_social"]
        with lock:
            if cnpj not in prog.get("processed", []):
                prog.setdefault("processed", []).append(cnpj)
            links = prog.setdefault("index_links", [])
            if not any(c == cnpj for c, _ in links):
                links.append((cnpj, nome))
        log.info("✅  %s — %s", fmt_cnpj(cnpj), nome[:40])
        return "ok"
    except Exception as e:
        log.error("💥  %s — %s", cnpj, e)
        return "erro"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(PROGRESS_FILE):
        log.error("progresso.json não encontrado.")
        return

    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        prog = json.load(f)

    todos     = prog.get("seeds", []) + prog.get("queue", [])
    todos     = list(dict.fromkeys(todos))
    pendentes = [c for c in todos
                 if not os.path.exists(os.path.join(BASE_DIR, "cnpj", c, "index.html"))]

    log.info("=" * 60)
    log.info("  BuscaCNPJ — Gerador v4b (novo design)")
    log.info("  Total: %d  |  Pendentes: %d  |  Workers: %d",
             len(todos), len(pendentes), MAX_WORKERS)
    log.info("=" * 60)

    if not pendentes:
        log.info("✅  Tudo já gerado!")
        return

    ok = erros = pulados = 0
    contador = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(processar, c, prog): c for c in pendentes}
        for fut in as_completed(futs):
            res = fut.result()
            if res == "ok":      ok      += 1
            elif res == "erro":  erros   += 1
            elif res == "skip":  pulados += 1
            contador += 1
            if contador % SAVE_EVERY == 0:
                with lock:
                    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
                        json.dump(prog, f, ensure_ascii=False, indent=2)
                log.info("💾  Progresso salvo — %d/%d", contador, len(pendentes))

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

    log.info("=" * 60)
    log.info("  ✅  Gerados : %d", ok)
    log.info("  ⏭️   Pulados : %d", pulados)
    log.info("  ❌  Erros   : %d", erros)
    log.info("=" * 60)

if __name__ == "__main__":
    main()
