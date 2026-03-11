<?php
require_once __DIR__ . '/config/db.php';

try {
    $db = getDB();

    // Recria a tabela local com a estrutura exata do servidor (incluindo o CEP)
    $db->exec("DROP TABLE IF EXISTS dados_cnpj");
    $sql = "CREATE TABLE dados_cnpj (
        cnpj TEXT PRIMARY KEY,
        razao_social TEXT,
        nome_fantasia TEXT,
        situacao_cadastral TEXT,
        data_inicio_atividade TEXT,
        porte TEXT,
        capital_social DECIMAL(18,2),
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cep TEXT,
        municipio TEXT,
        sigla_uf TEXT,
        email TEXT,
        telefone_1 TEXT,
        cnae_fiscal_principal TEXT,
        cnae_principal_descricao TEXT,
        cnae_fiscal_secundaria TEXT,
        socios_texto TEXT
    )";
    $db->exec($sql);

    // Otimizações para importação rápida no SQLite
    $db->exec("PRAGMA synchronous = OFF");
    $db->exec("PRAGMA journal_mode = MEMORY");

    // Prepara a query
    $stmt = $db->prepare("INSERT OR REPLACE INTO dados_cnpj (cnpj, razao_social, nome_fantasia, situacao_cadastral, data_inicio_atividade, porte, capital_social, logradouro, numero, complemento, bairro, cep, municipio, sigla_uf, email, telefone_1, cnae_fiscal_principal, cnae_principal_descricao, cnae_fiscal_secundaria, socios_texto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

    $dir = __DIR__ . '/database/csv_final';
    $arquivos = glob("$dir/*.csv");
    
    if (empty($arquivos)) {
        die("Nenhum CSV encontrado em $dir\n");
    }

    $totalGeral = 0;
    foreach ($arquivos as $arquivo) {
        echo "Lendo: " . basename($arquivo) . "...\n";
        
        if (($handle = fopen($arquivo, "r")) !== FALSE) {
            fgetcsv($handle); // Pula cabeçalho
            
            $db->beginTransaction();
            $count = 0;
            
            while (($data = fgetcsv($handle, 0, ",")) !== FALSE) {
                if (count($data) == 20) {
                    $stmt->execute($data);
                    $count++;
                    $totalGeral++;
                    
                    if ($count >= 50000) {
                        $db->commit();
                        $db->beginTransaction();
                        $count = 0;
                    }
                }
            }
            $db->commit();
            fclose($handle);
        }
    }
    
    // Volta pragma para normal
    $db->exec("PRAGMA synchronous = NORMAL");
    $db->exec("PRAGMA journal_mode = WAL");
    
    // Cria índices cruciais para a página do Ranking funcionar perfeitamente
    echo "Criando indices para acelerar o banco local...\n";
    $db->exec("CREATE INDEX IF NOT EXISTS idx_uf_situacao ON dados_cnpj(sigla_uf, situacao_cadastral)");
    $db->exec("CREATE INDEX IF NOT EXISTS idx_municipio ON dados_cnpj(municipio)");
    $db->exec("CREATE INDEX IF NOT EXISTS idx_cnae ON dados_cnpj(cnae_principal_descricao)");
    $db->exec("CREATE INDEX IF NOT EXISTS idx_capital_soc ON dados_cnpj(capital_social)");

    echo "\nConcluido! $totalGeral empresas re-importadas para o banco de dados oficial.\n";

} catch (PDOException $e) {
    die("Erro ao conectar com o banco de dados: " . $e->getMessage());
}
