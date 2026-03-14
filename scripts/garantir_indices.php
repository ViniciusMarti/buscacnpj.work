<?php
/**
 * Script para garantir a existência de índices vitais para performance.
 * Executa em todos os 32 shards.
 */
require_once __DIR__ . '/config/db.php';

echo "Iniciando verificação de Índices em 32 Shards...\n";
echo "------------------------------------------------\n";

$tasks = [
    ['table' => 'empresas', 'col' => 'cnpj_basico', 'index' => 'idx_cnpj_basico'],
    ['table' => 'estabelecimentos', 'col' => 'cnpj', 'index' => 'PRIMARY'], 
    ['table' => 'estabelecimentos', 'col' => 'cnpj_basico', 'index' => 'idx_cnpj_basico'],
    ['table' => 'socios', 'col' => 'cnpj_basico', 'index' => 'idx_cnpj_basico'],
];

for ($i = 1; $i <= 32; $i++) {
    $dbName = 'u582732852_buscacnpj' . $i;
    echo "Processando $dbName...\n";
    
    $db = getSpecificConnection($dbName);
    if (!$db) {
        echo "  [ERRO] Não foi possível conectar ao banco $dbName\n";
        continue;
    }

    foreach ($tasks as $task) {
        $table = $task['table'];
        $col = $task['col'];
        $indexName = $task['index'];

        try {
            // 1. Verifica se a tabela existe
            $stmtTable = $db->query("SHOW TABLES LIKE '$table'");
            if (!$stmtTable->fetch()) {
                echo "  [AVISO] Tabela $table não existe no banco $dbName. Pulando.\n";
                continue;
            }

            // 2. Verifica se a coluna existe
            $stmtCol = $db->query("SHOW COLUMNS FROM $table LIKE '$col'");
            if (!$stmtCol->fetch()) {
                echo "  [ERRO] Coluna $col não encontrada na tabela $table ($dbName).\n";
                continue;
            }

            // 3. Verifica o índice
            if ($indexName === 'PRIMARY') {
                $stmtIdx = $db->query("SHOW INDEX FROM $table WHERE Key_name = 'PRIMARY'");
                if (!$stmtIdx->fetch()) {
                    echo "  [!] AVISO: Tabela $table não possui PRIMARY KEY definida.\n";
                    // Geralmente não criamos PK via script automático se não soubermos o estado, 
                    // mas informamos.
                } else {
                    echo "  [OK] $table.$col (PRIMARY KEY detectada)\n";
                }
            } else {
                $stmtIdx = $db->query("SHOW INDEX FROM $table WHERE Key_name = '$indexName'");
                if (!$stmtIdx->fetch()) {
                    echo "  [INDEXANDO] Criando índice $indexName em $table($col)...\n";
                    $db->exec("CREATE INDEX $indexName ON $table($col)");
                    echo "    -> Sucesso!\n";
                } else {
                    echo "  [OK] Índice $indexName já existe em $table.$col\n";
                }
            }
        } catch (Exception $e) {
            echo "  [ERRO] Falha ao processar $table.$col em $dbName: " . $e->getMessage() . "\n";
        }
    }
    echo "------------------------------------------------\n";
}

echo "Processo de indexação concluído.\n";
