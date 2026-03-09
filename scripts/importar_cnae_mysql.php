<?php
/**
 * Script para converter o arquivo CNAECSV oficial da Receita Federal para o MySQL
 */

require_once __DIR__ . '/../config/db.php';

$csvFile = __DIR__ . '/../database/F.K03200$Z.D60214.CNAECSV';

if (!file_exists($csvFile)) {
    die("Erro: Arquivo CSV não encontrado em $csvFile\n");
}

try {
    $db = getDB();
    
    echo "Iniciando importação de CNAEs para o MySQL...\n";

    // Criar tabela se não existir (no padrão que o cnpj.php espera)
    $db->exec("CREATE TABLE IF NOT EXISTS lista_cnae (
        CNAE VARCHAR(20) PRIMARY KEY,
        `Descrição` TEXT
    )");

    // Limpar dados anteriores para garantir que os oficiais sejam os únicos
    $db->exec("TRUNCATE TABLE lista_cnae");

    $stmt = $db->prepare("INSERT INTO lista_cnae (CNAE, `Descrição`) VALUES (?, ?)");

    $handle = fopen($csvFile, "r");
    $count = 0;

    $db->beginTransaction();

    while (($line = fgets($handle)) !== false) {
        $data = str_getcsv($line, ";", '"');
        
        if (count($data) >= 2) {
            $codigo = trim($data[0]);
            // Tenta converter de ISO-8859-1 para UTF-8. Se mbstring não existir, usa utf8_encode
            $descricao_raw = trim($data[1]);
            if (function_exists('mb_convert_encoding')) {
                $descricao = mb_convert_encoding($descricao_raw, "UTF-8", "ISO-8859-1");
            } else {
                $descricao = utf8_encode($descricao_raw);
            }
            
            $stmt->execute([$codigo, $descricao]);
            $count++;
            
            if ($count % 500 == 0) {
                echo "Importados $count registros...\n";
            }
        }
    }

    $db->commit();
    fclose($handle);

    echo "Sucesso! $count registros oficiais importados para a tabela 'lista_cnae' no MySQL.\n";

} catch (Exception $e) {
    if (isset($db) && $db->inTransaction()) {
        $db->rollBack();
    }
    die("Erro: " . $e->getMessage() . "\n");
}
