import sqlite3
import os

DB_NAME = "dados.db"
DOMAIN = "https://buscacnpj.work"

def gerar_sitemap():
    if not os.path.exists(DB_NAME):
        print(f"Erro: Banco {DB_NAME} não encontrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT cnpj FROM empresas")
    cnpjs = [row[0] for row in cursor.fetchall()]
    conn.close()

    total = len(cnpjs)
    max_per_file = 10000
    num_files = (total + max_per_file - 1) // max_per_file

    sitemaps = []

    for i in range(num_files):
        filename = f"sitemap-cnpjs-{i+1}.xml"
        sitemaps.append(filename)
        start = i * max_per_file
        end = min(start + max_per_file, total)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
            for cnpj in cnpjs[start:end]:
                f.write(f'  <url><loc>{DOMAIN}/cnpj/{cnpj}/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>\n')
            f.write('</urlset>')
        print(f"Gerado: {filename} ({end-start} URLs)")

    # Gera o índice
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # Adiciona páginas estáticas se houver (opcional)
        for sm in sitemaps:
            f.write(f'  <sitemap><loc>{DOMAIN}/{sm}</loc></sitemap>\n')
        f.write('</sitemapindex>')
    
    print(f"Índice sitemap.xml gerado com sucesso.")

if __name__ == "__main__":
    gerar_sitemap()
