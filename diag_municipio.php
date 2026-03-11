<?php
require_once __DIR__ . '/config/db.php';

$connections = getAllConnections();
echo "Checking 'municipio' column in all databases:\n";

foreach ($connections as $name => $db) {
    echo "Database: $name ";
    try {
        $stmt = $db->query("DESCRIBE dados_cnpj");
        $columns = $stmt->fetchAll(PDO::FETCH_COLUMN);
        if (in_array('municipio', $columns)) {
            echo "[OK]\n";
        } else {
            echo "[MISSING]\n";
            // Check if it's called 'cidade' or something else
            echo "  Columns: " . implode(', ', $columns) . "\n";
        }
    } catch (Exception $e) {
        echo "[ERROR] " . $e->getMessage() . "\n";
    }
}
