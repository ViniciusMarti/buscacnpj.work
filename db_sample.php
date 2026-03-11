<?php
require_once __DIR__ . '/config/db.php';

echo "--- DATABASE STRUCTURE & DATA SAMPLES ---\n";

foreach (getAllConnections() as $name => $db) {
    echo "\nDatabase: $name\n";
    try {
        $stmt = $db->query("DESCRIBE dados_cnpj");
        $columns = $stmt->fetchAll(PDO::FETCH_ASSOC);
        echo "Columns:\n";
        foreach ($columns as $c) {
            echo "  " . $c['Field'] . " (" . $c['Type'] . ")\n";
        }
        
        echo "Sample data (1 row):\n";
        $stmt = $db->query("SELECT * FROM dados_cnpj LIMIT 1");
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($row) {
            foreach ($row as $k => $v) {
                echo "  $k: " . substr((string)$v, 0, 50) . (strlen((string)$v) > 50 ? '...' : '') . "\n";
            }
        } else {
            echo "  (Empty table)\n";
        }
    } catch (Exception $e) {
        echo "  [ERROR] " . $e->getMessage() . "\n";
    }
}
