<?php
require_once __DIR__ . '/config/db.php';
$DB_NAMES = [
    'u582732852_buscacnpj6',
    'u582732852_buscacnpj5',
    'u582732852_buscacnpj4',
    'u582732852_buscacnpj3',
    'u582732852_buscacnpj2',
    'u582732852_buscacnpj1'
];

foreach ($DB_NAMES as $dbName) {
    echo "Checking $dbName...\n";
    try {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . $dbName . ";charset=utf8mb4";
        $db = new PDO($dsn, $dbName, DB_PASS);
        $stmt = $db->query("DESCRIBE dados_cnpj");
        $cols = $stmt->fetchAll(PDO::FETCH_COLUMN);
        echo "Columns in $dbName: " . implode(', ', $cols) . "\n";
    } catch (Exception $e) {
        echo "Error in $dbName: " . $e->getMessage() . "\n";
    }
    echo "-------------------\n";
}
