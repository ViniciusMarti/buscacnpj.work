import csv
import sqlite3
import os

CSV_FILE = "lista_cnpjs_atualizada-v1.csv"
DB_NAME = "dados.db"

def import_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Erro: Arquivo {CSV_FILE} não encontrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    count = 0
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        # Detecta o delimitador (pode ser ; ou ,)
        sample = f.read(2048)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample)
        reader = csv.DictReader(f, dialect=dialect)
        
        for row in reader:
            try:
                # Limpa o CNPJ (apenas números)
                cnpj = "".join(filter(str.isdigit, row["cnpj"]))
                
                # Trata capital social para float
                cap = row["capital_social"].replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    capital = float(cap) if cap else 0.0
                except:
                    capital = 0.0

                cursor.execute('''
                    INSERT OR REPLACE INTO empresas (
                        cnpj, razao_social, nome_fantasia, situacao, data_abertura, 
                        porte, capital_social, logradouro, numero, complemento, 
                        bairro, cep, municipio, uf, telefone, email, 
                        cnae_principal_codigo, cnae_principal_descricao, 
                        cnaes_secundarios, quadro_societario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cnpj, row["razao_social"], row["nome_fantasia"], row["situacao"],
                    row["data_abertura"], row["porte"], capital, row["logradouro"],
                    row["numero"], row["complemento"], row["bairro"], row["cep"],
                    row["municipio"], row["uf"], row["telefone"], row["email"],
                    row["cnae_principal_codigo"], row["cnae_principal_descricao"],
                    row["cnaes_secundarios"], row["quadro_societario"]
                ))
                count += 1
                if count % 1000 == 0:
                    print(f"Importados: {count}...")
            except Exception as e:
                print(f"Erro no CNPJ {row.get('cnpj')}: {e}")

    conn.commit()
    conn.close()
    print(f"Finalizado! {count} registros importados para o banco de dados.")

if __name__ == "__main__":
    import_csv()
