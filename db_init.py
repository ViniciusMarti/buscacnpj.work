import sqlite3
import os

DB_NAME = "dados.db"

def init_db():
    if os.path.exists(DB_NAME):
        print(f"O banco {DB_NAME} já existe. Ignorando criação.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Criação da tabela principal
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            cnpj TEXT PRIMARY KEY,
            razao_social TEXT,
            nome_fantasia TEXT,
            situacao TEXT,
            data_abertura TEXT,
            porte TEXT,
            capital_social REAL,
            logradouro TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cep TEXT,
            municipio TEXT,
            uf TEXT,
            telefone TEXT,
            email TEXT,
            cnae_principal_codigo TEXT,
            cnae_principal_descricao TEXT,
            cnaes_secundarios TEXT,
            quadro_societario TEXT,
            ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Índices para busca rápida
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_municipio ON empresas(municipio)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_uf ON empresas(uf)')

    conn.commit()
    conn.close()
    print(f"Banco de dados {DB_NAME} inicializado com sucesso.")

if __name__ == "__main__":
    init_db()
