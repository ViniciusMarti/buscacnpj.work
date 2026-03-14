<?php
require_once __DIR__ . '/config/db.php';
require_once __DIR__ . '/config/db.php';

for ($i = 1; $i <= 32; $i++) {
    $dbName = 'u582732852_buscacnpj' . $i;
    echo "Checking $dbName...\n";
    try {
        $db = getSpecificConnection($dbName);
        if (!$db) {
            echo "Failed to connect to $dbName\n";
            continue;
        }
        
        $tables = ['empresas', 'estabelecimentos', 'socios'];
        foreach ($tables as $table) {
            $stmt = $db->query("SHOW TABLES LIKE '$table'");
            if ($stmt->fetch()) {
                $count = $db->query("SELECT COUNT(*) FROM $table")->fetchColumn();
                echo "  [OK] $table ($count records)\n";
            } else {
                echo "  [MISSING] $table\n";
            }
        }
    } catch (Exception $e) {
        echo "  Error in $dbName: " . $e->getMessage() . "\n";
    }
    echo "-------------------\n";
}
