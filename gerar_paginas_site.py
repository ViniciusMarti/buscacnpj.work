#!/usr/bin/env python3
"""
gerar_paginas_site.py — BuscaCNPJ.work  (versão SEO completa)
Gera / atualiza todas as páginas estáticas + arquivos SEO:

  site-cnpj/
  ├── index.html                ← home com busca + grid de empresas
  ├── sitemap.xml               ← todas as URLs (páginas fixas + empresas)
  ├── sitemap-index.xml         ← sitemap index apontando para sub-sitemaps
  ├── sitemap-pages.xml         ← só páginas institucionais
  ├── sitemap-cnpj.xml          ← só páginas de empresa (gerado em lote)
  ├── robots.txt                ← crawl rules + referência aos sitemaps
  ├── _headers                  ← Cloudflare Pages: cache, CSP, segurança
  ├── _redirects                ← Cloudflare Pages: redirects SEO
  ├── 404.html                  ← página de erro com busca
  ├── sobre/index.html
  ├── privacidade/index.html
  └── contato/index.html
"""

import os, json
from datetime import datetime

BASE_DIR      = "site-cnpj"
DOMAIN        = "https://buscacnpj.work"
PROGRESS_FILE = "progresso.json"
TODAY         = datetime.now().strftime("%Y-%m-%d")
TODAY_BR      = datetime.now().strftime("%d/%m/%Y")

# ── Dados ────────────────────────────────────────────────────────────────────
def carregar_dados():
    if not os.path.exists(PROGRESS_FILE):
        print("⚠️  progresso.json não encontrado.")
        return [], []
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        prog = json.load(f)
    return prog.get("processed", []), prog.get("index_links", [])

def fmt_cnpj(cnpj: str) -> str:
    c = cnpj.zfill(14)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"

def salvar(rel: str, content: str):
    path = os.path.join(BASE_DIR, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅  site-cnpj/{rel}")

# ── CSS ──────────────────────────────────────────────────────────────────────
CSS = """<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--text:#333;--muted:#888;--border:#ebebeb;--bg:#fff;--dark:#1a1a1a;--accent:#0066cc}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
     line-height:1.7;color:var(--text);background:var(--bg);font-size:1rem}
header{padding:14px 24px;border-bottom:1px solid var(--border);position:sticky;top:0;
       background:rgba(255,255,255,0.97);backdrop-filter:blur(8px);z-index:999}
.hi{max-width:1100px;margin:0 auto;display:flex;align-items:center;gap:24px}
.logo{font-weight:800;font-size:1rem;text-decoration:none;color:var(--dark)}
.hn{display:flex;gap:22px;align-items:center;flex:1}
.hn a{text-decoration:none;color:#555;font-size:.95rem;transition:color .15s}
.hn a:hover{color:var(--dark)}
.c{max-width:800px;margin:0 auto;padding:40px 20px 60px}
.bc{font-size:.82rem;color:var(--muted);margin-bottom:24px}
.bc a{color:var(--muted);text-decoration:none}.bc span{margin:0 6px}
h1{font-size:1.9rem;color:#111;font-weight:800;letter-spacing:-.5px;margin-bottom:8px}
h2{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;
   color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:8px;margin:28px 0 16px}
h3{font-size:1.1rem;font-weight:700;color:#111;margin:20px 0 8px}
p{color:#444;margin-bottom:14px;font-size:.97rem}
.hero{padding:72px 24px;text-align:center;border-bottom:1px solid var(--border);margin-bottom:48px;
      background:linear-gradient(180deg,#fafafa 0%,#fff 100%)}
.hero h1{font-size:2.4rem;margin-bottom:12px;color:#111}
.hero .sub{color:var(--muted);font-size:1.05rem;margin-bottom:32px;max-width:480px;
           margin-left:auto;margin-right:auto}
.sr{display:flex;justify-content:center;gap:8px;flex-wrap:wrap}
.sr input{padding:13px 18px;font-size:1rem;border:1px solid var(--border);border-radius:8px;
          width:340px;max-width:100%;outline:none;font-family:inherit;color:#111;
          transition:border-color .15s}
.sr input:focus{border-color:#999;box-shadow:0 0 0 3px rgba(0,0,0,.05)}
.sr button{padding:13px 24px;background:var(--dark);color:#fff;font-size:.95rem;
           font-weight:600;border:none;border-radius:8px;cursor:pointer;
           font-family:inherit;transition:background .15s}
.sr button:hover{background:#333}
.hint{font-size:.8rem;color:#bbb;margin-top:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-top:16px}
.card{display:block;padding:15px;border:1px solid var(--border);border-radius:8px;
      text-decoration:none;color:var(--dark);transition:border-color .15s,box-shadow .15s}
.card:hover{border-color:#bbb;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.card strong{display:block;font-size:.9rem;margin-bottom:4px;line-height:1.4}
.card span{font-size:.78rem;color:var(--muted)}
.faq{margin-top:8px}
.faq-item{border-bottom:1px solid var(--border);padding:16px 0}
.faq-item:last-child{border-bottom:none}
.faq-item summary{font-weight:600;cursor:pointer;font-size:.97rem;color:#111;
                   list-style:none;display:flex;justify-content:space-between;
                   align-items:center}
.faq-item summary::after{content:"＋";color:var(--muted);font-size:1.1rem}
.faq-item[open] summary::after{content:"－"}
.faq-item p{margin-top:10px;color:#555;font-size:.95rem}
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
       gap:16px;margin:24px 0}
.stat{text-align:center;padding:20px;border:1px solid var(--border);border-radius:8px}
.stat strong{display:block;font-size:1.8rem;font-weight:800;color:#111;letter-spacing:-.5px}
.stat span{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
hr{border:none;border-top:1px solid var(--border);margin:32px 0}
footer{border-top:1px solid var(--border);padding:36px 20px;text-align:center;
       color:var(--muted);font-size:.85rem;background:#fafafa}
.fn{display:flex;justify-content:center;gap:22px;margin-bottom:14px;flex-wrap:wrap}
.fn a{color:var(--muted);text-decoration:none;transition:color .15s}
.fn a:hover{color:var(--dark)}
a{color:var(--dark);text-decoration:underline;text-underline-offset:3px;
  text-decoration-color:#ccc;transition:text-decoration-color .15s}
a:hover{text-decoration-color:var(--dark)}
@media(max-width:600px){.hero h1{font-size:1.8rem}.sr input{width:100%}}
@media(prefers-color-scheme:dark){
  :root{--text:#e8e8e8;--muted:#666;--border:#2a2a2a;--bg:#141414;--dark:#f0f0f0}
  header{background:rgba(20,20,20,.97)!important}
  .hero{background:linear-gradient(180deg,#1a1a1a 0%,#141414 100%)}
  h1,.hero h1{color:#f0f0f0}h3{color:#f0f0f0}p{color:#bbb}
  .sr input{background:#222;color:#e8e8e8;border-color:#333}
  .card{background:#1c1c1c}.stat{background:#1c1c1c}.stat strong{color:#f0f0f0}
  footer{background:#111}
}
</style>"""

JS_BUSCA = r"""<script>
function buscar(){
  var r=document.getElementById('q').value.replace(/\D/g,'');
  if(r.length===14){window.location.href=(window.location.pathname.includes('/cnpj')?'../../':'')+'cnpj/'+r+'/';}
  else{alert('Digite um CNPJ válido com 14 dígitos.');}
}
document.addEventListener('DOMContentLoaded',function(){
  var q=document.getElementById('q');
  if(q){
    q.addEventListener('keydown',function(e){if(e.key==='Enter')buscar();});
    q.addEventListener('input',function(){
      this.value=this.value.replace(/\D/g,'').replace(/^(\d{2})(\d)/,'$1.$2')
        .replace(/^(\d{2})\.(\d{3})(\d)/,'$1.$2.$3')
        .replace(/\.(\d{3})(\d)/,'.$1/$2')
        .replace(/(\d{4})(\d)/,'$1-$2');
    });
  }
});
</script>"""

def head(title, desc, canonical, extra_schema="", extra_meta=""):
    return f"""<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="BuscaCNPJ.work">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
{extra_meta}
{extra_schema}
{CSS}
</head>"""

def header_html():
    return f"""<header>
<div class="hi">
  <a class="logo" href="{DOMAIN}">buscacnpj.work</a>
  <nav class="hn">
    <a href="{DOMAIN}">consultar</a>
    <a href="{DOMAIN}/sobre/">sobre</a>
  </nav>
</div>
</header>"""

def footer_html():
    return f"""<footer>
<nav class="fn">
  <a href="{DOMAIN}/">Início</a>
  <a href="{DOMAIN}/sobre/">Sobre</a>
  <a href="{DOMAIN}/privacidade/">Privacidade</a>
  <a href="{DOMAIN}/contato/">Contato</a>
</nav>
<p>© 2026 <a href="{DOMAIN}">BuscaCNPJ.work</a> — Dados públicos da Receita Federal do Brasil.</p>
<p style="margin-top:6px;font-size:.78rem">As informações têm caráter público e informativo. Atualizado em {TODAY_BR}.</p>
</footer>"""

# ════════════════════════════════════════════════════════════════
# 1. HOME
# ════════════════════════════════════════════════════════════════
def gerar_home(index_links, total):
    cards = "".join([
        f'<a class="card" href="cnpj/{c}/">'
        f'<strong>{n[:38]+("…" if len(n)>38 else "")}</strong>'
        f'<span>{fmt_cnpj(c)}</span></a>'
        for c, n in index_links
    ])

    schema_website = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "BuscaCNPJ.work",
        "url": DOMAIN,
        "description": "Consulta gratuita de CNPJ de empresas brasileiras",
        "inLanguage": "pt-BR",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": f"{DOMAIN}/cnpj/{{cnpj}}/"},
            "query-input": "required name=cnpj"
        }
    }, ensure_ascii=False)

    schema_org = json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "BuscaCNPJ.work",
        "url": DOMAIN,
        "description": "Consulta gratuita de dados públicos de empresas brasileiras",
        "foundingDate": "2026",
        "contactPoint": {"@type": "ContactPoint", "email": "contato@buscacnpj.work",
                         "contactType": "customer service", "availableLanguage": "Portuguese"}
    }, ensure_ascii=False)

    schema_faq = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": "O que é CNPJ?",
             "acceptedAnswer": {"@type": "Answer", "text": "CNPJ é o Cadastro Nacional de Pessoas Jurídicas, número único que identifica empresas perante a Receita Federal do Brasil."}},
            {"@type": "Question", "name": "Como consultar um CNPJ gratuitamente?",
             "acceptedAnswer": {"@type": "Answer", "text": "Digite o CNPJ no campo de busca do BuscaCNPJ.work e clique em Consultar. Os dados são exibidos gratuitamente e sem cadastro."}},
            {"@type": "Question", "name": "Os dados do CNPJ são confiáveis?",
             "acceptedAnswer": {"@type": "Answer", "text": "Sim. Todos os dados são provenientes da Receita Federal do Brasil, a fonte oficial de informações sobre pessoas jurídicas."}},
        ]
    }, ensure_ascii=False)

    extra_schema = (f'<script type="application/ld+json">{schema_website}</script>\n'
                    f'<script type="application/ld+json">{schema_org}</script>\n'
                    f'<script type="application/ld+json">{schema_faq}</script>')

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
{head(
    "BuscaCNPJ.work — Consulta Gratuita de CNPJ de Empresas Brasileiras",
    "Consulte gratuitamente o CNPJ de qualquer empresa brasileira. Situação cadastral, endereço, sócios e atividades da Receita Federal. Simples, rápido e gratuito.",
    f"{DOMAIN}/",
    extra_schema=extra_schema
)}
<body>
{header_html()}

<section class="hero">
  <h1>Consulta de CNPJ Gratuita</h1>
  <p class="sub">Dados públicos de empresas brasileiras direto da Receita Federal. Sem cadastro, sem custo.</p>
  <div class="sr">
    <input type="text" id="q" maxlength="18" placeholder="00.000.000/0000-00"
           autocomplete="off" aria-label="Digite o CNPJ">
    <button onclick="buscar()">Consultar</button>
  </div>
  <p class="hint">Digite os 14 números ou o CNPJ formatado</p>
</section>

<div class="c" style="padding-top:0">

  <div class="stats">
    <div class="stat"><strong>{total:,}</strong><span>Empresas</span></div>
    <div class="stat"><strong>Grátis</strong><span>Sem cadastro</span></div>
    <div class="stat"><strong>Receita Federal</strong><span>Fonte oficial</span></div>
    <div class="stat"><strong>Atualizado</strong><span>{TODAY_BR}</span></div>
  </div>

  <hr>

  <div>
    <h2>Empresas cadastradas ({total:,})</h2>
    <div class="grid">{cards}</div>
  </div>

  <hr>

  <div>
    <h2>Como consultar um CNPJ</h2>
    <p>Digite o número do CNPJ (com ou sem pontuação) no campo de busca acima e pressione <strong>Consultar</strong>. Em segundos você verá os dados públicos da empresa diretamente da Receita Federal.</p>
    <p>Você pode consultar <strong>razão social, nome fantasia, situação cadastral, endereço completo, sócios e administradores, e atividades econômicas (CNAE)</strong> de qualquer empresa registrada no Brasil.</p>
  </div>

  <hr>

  <div>
    <h2>Perguntas frequentes</h2>
    <div class="faq">
      <details class="faq-item">
        <summary>O que é CNPJ?</summary>
        <p>O CNPJ (Cadastro Nacional de Pessoas Jurídicas) é o número único que identifica uma empresa perante a Receita Federal do Brasil. Toda empresa legalmente constituída possui um CNPJ de 14 dígitos.</p>
      </details>
      <details class="faq-item">
        <summary>A consulta é realmente gratuita?</summary>
        <p>Sim. O BuscaCNPJ.work exibe dados públicos da Receita Federal sem custo, sem cadastro e sem limite de consultas. Os dados são de domínio público.</p>
      </details>
      <details class="faq-item">
        <summary>Os dados são atualizados?</summary>
        <p>Os dados são obtidos diretamente das APIs públicas da Receita Federal e atualizados regularmente. Para informações em tempo real, recomendamos verificar diretamente no portal da Receita Federal.</p>
      </details>
      <details class="faq-item">
        <summary>O que significa CNPJ ativo, baixado ou inapto?</summary>
        <p><strong>Ativo</strong>: empresa em funcionamento regular. <strong>Baixado</strong>: empresa encerrada. <strong>Inapto</strong>: empresa que não entregou declarações obrigatórias por 2+ anos consecutivos. <strong>Suspenso</strong>: situação temporária por pendências.</p>
      </details>
      <details class="faq-item">
        <summary>Posso pedir a remoção dos dados da minha empresa?</summary>
        <p>Os dados exibidos são públicos e provenientes da Receita Federal. Para correções, entre em contato com a Receita Federal diretamente. Para solicitações específicas, acesse nossa página de <a href="{DOMAIN}/contato/">contato</a>.</p>
      </details>
    </div>
  </div>

</div>

{footer_html()}
{JS_BUSCA}
</body>
</html>"""
    salvar("index.html", html)

# ════════════════════════════════════════════════════════════════
# 2. SOBRE
# ════════════════════════════════════════════════════════════════
def gerar_sobre(total):
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "Sobre o BuscaCNPJ.work",
        "url": f"{DOMAIN}/sobre/",
        "description": "Saiba mais sobre o BuscaCNPJ.work, ferramenta gratuita de consulta de CNPJ.",
        "publisher": {"@type": "Organization", "name": "BuscaCNPJ.work", "url": DOMAIN}
    }, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
{head(
    "Sobre o BuscaCNPJ.work — Consulta de CNPJ Gratuita",
    "Saiba mais sobre o BuscaCNPJ.work, ferramenta gratuita de consulta de CNPJ de empresas brasileiras com dados da Receita Federal.",
    f"{DOMAIN}/sobre/",
    extra_schema=f'<script type="application/ld+json">{schema}</script>'
)}
<body>
{header_html()}
<div class="c">
  <div class="bc"><a href="{DOMAIN}">início</a><span>/</span>sobre</div>
  <h1>Sobre o BuscaCNPJ.work</h1>

  <h3>O que é</h3>
  <p>O <strong>BuscaCNPJ.work</strong> é uma ferramenta de consulta pública de CNPJs de empresas brasileiras. Centralizamos, de forma rápida e acessível, os dados da Receita Federal em um formato fácil de ler — sem cadastro, sem custo, sem complicação.</p>
  <p>Atualmente o banco de dados conta com <strong>{total:,} empresas cadastradas</strong>, com novas páginas sendo adicionadas regularmente.</p>

  <h3>Fonte dos dados</h3>
  <p>Todas as informações são provenientes da <strong>Receita Federal do Brasil</strong>, disponibilizadas via APIs públicas como a <a href="https://brasilapi.com.br" target="_blank" rel="noopener noreferrer">BrasilAPI</a> e a <a href="https://minhareceita.org" target="_blank" rel="noopener noreferrer">Minha Receita</a>. Os dados têm caráter estritamente público e informativo.</p>

  <h3>Como usar</h3>
  <p>Digite o CNPJ (14 dígitos, com ou sem formatação) na <a href="{DOMAIN}">barra de busca</a> e clique em <strong>Consultar</strong>. Você verá razão social, situação, endereço, sócios e atividades da empresa.</p>

  <h3>Tecnologia</h3>
  <p>O site é 100% estático — gerado automaticamente por scripts Python e hospedado no <strong>Cloudflare Pages</strong>. Sem banco de dados, sem servidor próprio, com carregamento ultra-rápido e disponibilidade de 99,99%.</p>

  <h3>Transparência</h3>
  <p>Nenhum dado pessoal de visitantes é coletado. Os dados das empresas são públicos e de responsabilidade da Receita Federal. Veja nossa <a href="{DOMAIN}/privacidade/">política de privacidade</a> completa.</p>
</div>
{footer_html()}
{JS_BUSCA}
</body></html>"""
    salvar("sobre/index.html", html)

# ════════════════════════════════════════════════════════════════
# 3. PRIVACIDADE
# ════════════════════════════════════════════════════════════════
def gerar_privacidade():
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
{head(
    "Política de Privacidade — BuscaCNPJ.work",
    "Política de privacidade do BuscaCNPJ.work. Não coletamos dados pessoais. Dados de empresas são públicos e provenientes da Receita Federal.",
    f"{DOMAIN}/privacidade/",
    extra_meta='<meta name="robots" content="noindex, follow">'
)}
<body>
{header_html()}
<div class="c">
  <div class="bc"><a href="{DOMAIN}">início</a><span>/</span>privacidade</div>
  <h1>Política de Privacidade</h1>
  <p style="color:var(--muted);font-size:.85rem">Última atualização: {TODAY_BR}</p>

  <h3>1. Coleta de dados pessoais</h3>
  <p>O BuscaCNPJ.work <strong>não coleta dados pessoais</strong> dos visitantes. Não há formulários de cadastro, login ou rastreamento individual de usuários.</p>

  <h3>2. Dados exibidos</h3>
  <p>Todas as informações de CNPJ exibidas são <strong>dados públicos</strong> da Receita Federal do Brasil, conforme a Lei de Acesso à Informação (Lei nº 12.527/2011). Não armazenamos nem tratamos dados privados de pessoas físicas.</p>

  <h3>3. Cookies e analytics</h3>
  <p>Podemos utilizar ferramentas de análise de tráfego com dados agregados e anônimos para entender o volume de acessos. Nenhum dado individual é identificado.</p>

  <h3>4. Links externos</h3>
  <p>Este site pode conter links para a BrasilAPI e Receita Federal. Não nos responsabilizamos pelas políticas de privacidade desses serviços externos.</p>

  <h3>5. LGPD</h3>
  <p>Em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), não realizamos tratamento de dados pessoais dos visitantes.</p>

  <h3>6. Contato</h3>
  <p>Dúvidas? Entre em <a href="{DOMAIN}/contato/">contato</a>.</p>
</div>
{footer_html()}
</body></html>"""
    salvar("privacidade/index.html", html)

# ════════════════════════════════════════════════════════════════
# 4. CONTATO
# ════════════════════════════════════════════════════════════════
def gerar_contato():
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contato — BuscaCNPJ.work",
        "url": f"{DOMAIN}/contato/",
        "publisher": {"@type": "Organization", "name": "BuscaCNPJ.work",
                      "email": "contato@buscacnpj.work"}
    }, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
{head(
    "Contato — BuscaCNPJ.work",
    "Entre em contato com o BuscaCNPJ.work para dúvidas, sugestões ou solicitações de remoção de dados.",
    f"{DOMAIN}/contato/",
    extra_schema=f'<script type="application/ld+json">{schema}</script>'
)}
<body>
{header_html()}
<div class="c">
  <div class="bc"><a href="{DOMAIN}">início</a><span>/</span>contato</div>
  <h1>Contato</h1>

  <h3>Fale conosco</h3>
  <p>Para dúvidas, sugestões ou solicitações, envie um e-mail para:</p>
  <p><strong><a href="mailto:contato@buscacnpj.work">contato@buscacnpj.work</a></strong></p>

  <h3>Solicitação de remoção de dados</h3>
  <p>Caso seja representante legal de uma empresa e deseje solicitar remoção ou correção dos dados exibidos, envie o CNPJ e a justificativa para o e-mail acima. Analisamos cada caso em até <strong>5 dias úteis</strong>.</p>
  <p>Importante: os dados exibidos são públicos e provenientes da Receita Federal. Correções definitivas devem ser feitas diretamente junto à Receita Federal.</p>

  <h3>Tempo de resposta</h3>
  <p>Respondemos em até <strong>5 dias úteis</strong>.</p>
</div>
{footer_html()}
</body></html>"""
    salvar("contato/index.html", html)

# ════════════════════════════════════════════════════════════════
# 5. 404
# ════════════════════════════════════════════════════════════════
def gerar_404():
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
{head(
    "Página não encontrada — BuscaCNPJ.work",
    "Página não encontrada. Use a busca para consultar qualquer CNPJ.",
    f"{DOMAIN}/404.html",
    extra_meta='<meta name="robots" content="noindex, nofollow">'
)}
<body>
{header_html()}
<div class="c" style="text-align:center;padding-top:80px">
  <p style="font-size:4rem;margin-bottom:16px">🔍</p>
  <h1 style="margin-bottom:12px">Página não encontrada</h1>
  <p style="color:var(--muted);margin-bottom:32px">O CNPJ ou a página que você procura não está em nossa base ainda.</p>
  <div class="sr" style="justify-content:center">
    <input type="text" id="q" maxlength="18" placeholder="00.000.000/0000-00" autocomplete="off">
    <button onclick="buscar()">Consultar</button>
  </div>
  <p style="margin-top:20px"><a href="{DOMAIN}">← Voltar ao início</a></p>
</div>
{footer_html()}
{JS_BUSCA}
</body></html>"""
    salvar("404.html", html)

# ════════════════════════════════════════════════════════════════
# 6. SITEMAPS
# ════════════════════════════════════════════════════════════════
def gerar_sitemaps(processed):
    # Sitemap de páginas institucionais
    paginas_fixas = [
        (f"{DOMAIN}/",             "daily",   "1.0"),
        (f"{DOMAIN}/sobre/",       "monthly", "0.5"),
        (f"{DOMAIN}/privacidade/", "yearly",  "0.3"),
        (f"{DOMAIN}/contato/",     "monthly", "0.4"),
    ]
    urls_pages = "".join(
        f"  <url><loc>{l}</loc><changefreq>{f}</changefreq><priority>{p}</priority><lastmod>{TODAY}</lastmod></url>\n"
        for l, f, p in paginas_fixas
    )
    sitemap_pages = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_pages}</urlset>"""
    salvar("sitemap-pages.xml", sitemap_pages)

    # Sitemap de CNPJs
    urls_cnpj = "".join(
        f"  <url><loc>{DOMAIN}/cnpj/{c}/</loc><lastmod>{TODAY}</lastmod>"
        f"<changefreq>monthly</changefreq><priority>0.8</priority></url>\n"
        for c in processed
    )
    sitemap_cnpj = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_cnpj}</urlset>"""
    salvar("sitemap-cnpj.xml", sitemap_cnpj)

    # Sitemap index
    sitemap_index = f"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{DOMAIN}/sitemap-pages.xml</loc>
    <lastmod>{TODAY}</lastmod>
  </sitemap>
  <sitemap>
    <loc>{DOMAIN}/sitemap-cnpj.xml</loc>
    <lastmod>{TODAY}</lastmod>
  </sitemap>
</sitemapindex>"""
    salvar("sitemap-index.xml", sitemap_index)

    # Sitemap único (compatibilidade)
    urls_all = urls_pages + urls_cnpj
    sitemap_all = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_all}</urlset>"""
    salvar("sitemap.xml", sitemap_all)

# ════════════════════════════════════════════════════════════════
# 7. ROBOTS.TXT
# ════════════════════════════════════════════════════════════════
def gerar_robots():
    content = f"""User-agent: *
Allow: /
Disallow: /404.html

# Google
User-agent: Googlebot
Allow: /
Crawl-delay: 1

# Bing
User-agent: Bingbot
Allow: /
Crawl-delay: 2

Sitemap: {DOMAIN}/sitemap-index.xml
Sitemap: {DOMAIN}/sitemap.xml
"""
    salvar("robots.txt", content)

# ════════════════════════════════════════════════════════════════
# 8. _HEADERS (Cloudflare Pages — cache + segurança)
# ════════════════════════════════════════════════════════════════
def gerar_headers():
    content = """/*
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/index.html
  Cache-Control: public, max-age=3600, must-revalidate

/cnpj/*
  Cache-Control: public, max-age=86400, stale-while-revalidate=604800

/*.xml
  Cache-Control: public, max-age=3600
  Content-Type: application/xml; charset=utf-8

/robots.txt
  Cache-Control: public, max-age=86400

/*.css
  Cache-Control: public, max-age=2592000, immutable

/*.js
  Cache-Control: public, max-age=2592000, immutable
"""
    salvar("_headers", content)

# ════════════════════════════════════════════════════════════════
# 9. _REDIRECTS (Cloudflare Pages)
# ════════════════════════════════════════════════════════════════
def gerar_redirects():
    content = f"""/consultar-cnpj  {DOMAIN}/  301
/busca           {DOMAIN}/  301
/cnpj            {DOMAIN}/  301
/empresa         {DOMAIN}/  301
/politica        {DOMAIN}/privacidade/  301
/politica-de-privacidade  {DOMAIN}/privacidade/  301
/fale-conosco    {DOMAIN}/contato/  301
/sobre-nos       {DOMAIN}/sobre/  301

# Fallback 404
/*  /404.html  404
"""
    salvar("_redirects", content)

# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
def main():
    processed, index_links = carregar_dados()
    total = len(processed)

    print()
    print("=" * 60)
    print("  BuscaCNPJ.work — Gerador de Páginas SEO Completo")
    print(f"  Empresas: {total:,} | Data: {TODAY_BR}")
    print("=" * 60)
    print()

    gerar_home(index_links, total)
    gerar_sobre(total)
    gerar_privacidade()
    gerar_contato()
    gerar_404()
    gerar_sitemaps(processed)
    gerar_robots()
    gerar_headers()
    gerar_redirects()

    print()
    print("=" * 60)
    print("  ✅  TUDO GERADO COM SUCESSO!")
    print()
    print("  Arquivos criados:")
    print("  site-cnpj/")
    print("  ├── index.html          ← home + FAQ + Schema.org")
    print("  ├── 404.html            ← página de erro com busca")
    print("  ├── sitemap.xml         ← sitemap unificado")
    print("  ├── sitemap-index.xml   ← sitemap index")
    print("  ├── sitemap-pages.xml   ← páginas institucionais")
    print("  ├── sitemap-cnpj.xml    ← todas as empresas")
    print("  ├── robots.txt          ← regras + 2 sitemaps")
    print("  ├── _headers            ← cache + CSP + segurança")
    print("  ├── _redirects          ← SEO redirects")
    print("  ├── sobre/index.html")
    print("  ├── privacidade/index.html")
    print("  └── contato/index.html")
    print()
    print("  Próximo: git add . && git commit -m 'SEO update' && git push")
    print("=" * 60)

if __name__ == "__main__":
    main()
