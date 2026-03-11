<?php
require_once __DIR__ . '/config/db.php';
try {
    $db = getDB();
    
    echo "\n=== TABELAS ===\n";
    if ($db->getAttribute(PDO::ATTR_DRIVER_NAME) == 'sqlite') {
        $tables = $db->query("SELECT name FROM sqlite_master WHERE type='table'")->fetchAll(PDO::FETCH_COLUMN);
    } else {
        $tables = $db->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
    }
    print_r($tables);

    if (in_array('dados_cnpj', $tables)) {
        echo "\n=== ÍNDICES (dados_cnpj) ===\n";
        if ($db->getAttribute(PDO::ATTR_DRIVER_NAME) == 'sqlite') {
            $indices = $db->query("PRAGMA index_list(dados_cnpj)")->fetchAll(PDO::FETCH_ASSOC);
            foreach ($indices as $idx) {
                echo "Index: {$idx['name']}\n";
                print_r($db->query("PRAGMA index_info({$idx['name']})")->fetchAll(PDO::FETCH_ASSOC));
            }
        } else {
            $indices = $db->query("SHOW INDEX FROM dados_cnpj")->fetchAll(PDO::FETCH_ASSOC);
            print_r($indices);
        }
        
        echo "\n=== CONTAGEM (SP) ===\n";
        $start = microtime(true);
        $count = $db->query("SELECT COUNT(*) FROM dados_cnpj WHERE sigla_uf = 'SP' AND situacao_cadastral = 'ATIVA'")->fetchColumn();
        $end = microtime(true);
        echo "Contagem SP: $count (Tempo: " . round($end - $start, 4) . "s)\n";
    }
} catch (Exception $e) {
    echo "Erro: " . $e->getMessage();
}
