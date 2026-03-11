<?php
require_once __DIR__ . '/config/db.php';

$cnpjs = ['18236120000158', '50499508000154'];

echo "--- DEEP INSPECTION ---\n";

foreach ($cnpjs as $cnpj) {
    echo "\nCNPJ: $cnpj\n";
    $found_any = false;
    foreach (getAllConnections() as $name => $db) {
        try {
            // Check if table exists and columns
            $stmt = $db->query("DESCRIBE dados_cnpj");
            $cols = $stmt->fetchAll(PDO::FETCH_COLUMN);
            
            $stmt = $db->prepare("SELECT * FROM dados_cnpj WHERE cnpj = :cnpj LIMIT 1");
            $stmt->execute([':cnpj' => $cnpj]);
            $row = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($row) {
                echo "  [FOUND] Database: $name\n";
                foreach ($row as $k => $v) {
                    echo "    $k: $v\n";
                }
                $found_any = true;
            } else {
                // Check if maybe it's without formatting?
                $clean = preg_replace('/\D/', '', $cnpj);
                $stmt->execute([':cnpj' => $clean]);
                $row = $stmt->fetch(PDO::FETCH_ASSOC);
                if ($row) {
                    echo "  [FOUND CLEAN] Database: $name\n";
                    echo "    cnpj in DB is: " . $row['cnpj'] . "\n";
                    $found_any = true;
                }
            }
        } catch (Exception $e) {
            echo "  [ERROR] Database $name: " . $e->getMessage() . "\n";
        }
    }
    if (!$found_any) echo "  [NOT FOUND] across all databases.\n";
}
