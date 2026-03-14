<?php
header('Content-Type: text/plain');
$logFile = __DIR__ . '/logs/import_errors.log';
$stateFile = __DIR__ . '/state.json';
$progressFile = __DIR__ . '/logs/import_progress.json';

echo "--- LOG DE ERROS ---\n";
if (file_exists($logFile)) {
    echo file_get_contents($logFile);
} else {
    echo "Arquivo de log não existe.\n";
}

echo "\n--- ESTADO ATUAL ---\n";
if (file_exists($stateFile)) {
    echo file_get_contents($stateFile);
}

echo "\n--- ÚLTIMO PROGRESSO ---\n";
if (file_exists($progressFile)) {
    echo file_get_contents($progressFile);
}

// Diagnostic: Sample Query
require_once 'bigquery_client.php';
$keyFile = __DIR__ . '/buscacnpj-490113-6da549c016bb.json';

try {
    $bq = new BigQueryClient($keyFile);
    echo "\n\n--- TESTE DE CONEXÃO BIGQUERY ---\n";
    $test = $bq->query("SELECT * FROM `basedosdados.br_me_cnpj.empresas` LIMIT 2");
    echo "TotalRows no BigQuery: " . ($test['totalRows'] ?? 'N/A') . "\n";
    $rows = $bq->parseRows($test);
    echo "Linhas parseadas: " . count($rows) . "\n";
    if (!empty($rows)) {
        echo "Amostra do primeiro CNPJ Básico: " . ($rows[0]['cnpj_basico'] ?? 'COLUNA NÃO ENCONTRADA') . "\n";
        print_r($rows[0]);
    }
} catch (Exception $e) {
    echo "Erro no teste: " . $e->getMessage();
}
