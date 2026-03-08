import sqlite3
import os
import unicodedata
import re

# Caminho para o banco de dados relativo a este script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database_cnpj.sqlite")
OUTPUT_DIR = os.path.join(BASE_DIR, "sitemaps")
INDEX_PATH = os.path.join(BASE_DIR, "sitemap.xml")

def gerar_sitemap():
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados {DB_PATH} não encontrado.")
        return

    # Garante que a pasta de sitemaps existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Busca todos os CNPJs ativos ou com razão social
    print("Buscando CNPJs no banco de dados...")
    cursor.execute("SELECT cnpj FROM dados_cnpj WHERE razao_social != ''")
    cnpjs = [row[0] for row in cursor.fetchall()]

    print("Gerando sitemap de rankings (Estados e Cidades)...")
    states_dict = {
        'acre': 'AC', 'alagoas': 'AL', 'amapa': 'AP', 'amazonas': 'AM', 
        'bahia': 'BA', 'ceara': 'CE', 'distrito-federal': 'DF', 'espirito-santo': 'ES', 
        'goias': 'GO', 'maranhao': 'MA', 'mato-grosso': 'MT', 'mato-grosso-do-sul': 'MS', 
        'minas-gerais': 'MG', 'para': 'PA', 'paraiba': 'PB', 'parana': 'PR', 
        'pernambuco': 'PE', 'piaui': 'PI', 'rio-de-janeiro': 'RJ', 'rio-grande-do-norte': 'RN', 
        'rio-grande-do-sul': 'RS', 'rondonia': 'RO', 'roraima': 'RR', 'santa-catarina': 'SC', 
        'sao-paulo': 'SP', 'sergipe': 'SE', 'tocantins': 'TO'
    }

    def slugify(text):
        text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('utf-8')
        text = text.lower().replace(' ', '-')
        return re.sub(r'[^a-z0-9-]', '', text)

    rankings_urls = ["https://buscacnpjgratis.com.br/rankings/"]
    
    for slug, uf in states_dict.items():
        state_url = f"https://buscacnpjgratis.com.br/rankings/estado/{slug}/"
        rankings_urls.append(state_url)
        
        # Buscar top 10 cidades
        cursor.execute("SELECT municipio FROM dados_cnpj WHERE uf = ? GROUP BY municipio ORDER BY COUNT(*) DESC LIMIT 10", (uf,))
        cities = cursor.fetchall()
        for city_row in cities:
            if city_row[0]:
                city_slug = slugify(city_row[0])
                if city_slug:
                    city_url = f"https://buscacnpjgratis.com.br/rankings/estado/{slug}/{city_slug}/"
                    rankings_urls.append(city_url)

    # Salva sitemap-rankings.xml
    path_rankings = os.path.join(OUTPUT_DIR, "sitemap-rankings.xml")
    with open(path_rankings, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in rankings_urls:
            f.write(f'  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n')
        f.write('</urlset>')

    
    if not cnpjs:
        print("Nenhum CNPJ com dados encontrado no banco.")
        return

    print(f"Gerando sitemaps para {len(cnpjs)} empresas...")

    # Limite de URLs por arquivo
    URLS_PER_FILE = 5000
    sitemaps = []

    for i in range(0, len(cnpjs), URLS_PER_FILE):
        chunk = cnpjs[i:i + URLS_PER_FILE]
        file_num = (i // URLS_PER_FILE) + 1
        filename = f"sitemap-cnpj-{file_num}.xml"
        path = os.path.join(OUTPUT_DIR, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for cnpj in chunk:
                f.write(f'  <url><loc>https://buscacnpjgratis.com.br/cnpj/{cnpj}/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>\n')
            f.write('</urlset>')
        
        sitemaps.append(filename)
        if file_num % 10 == 0:
            print(f"Gerados {file_num} sitemaps...")

    # Gera o Sitemap Index na RAIZ
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # Adiciona o sitemap principal
        f.write('  <sitemap><loc>https://buscacnpjgratis.com.br/sitemaps/sitemap-main.xml</loc></sitemap>\n')
        for s in sitemaps:
            f.write(f'  <sitemap><loc>https://buscacnpjgratis.com.br/sitemaps/{s}</loc></sitemap>\n')
        f.write('  <sitemap><loc>https://buscacnpjgratis.com.br/sitemaps/sitemap-rankings.xml</loc></sitemap>\n')
        f.write('</sitemapindex>')

    conn.close()
    print(f"Concluído! {len(sitemaps)} arquivos de sitemap criados na pasta /sitemaps/ e index na raiz.")

if __name__ == "__main__":
    gerar_sitemap()
