<?php
require_once __DIR__ . '/config/db.php';

$cnpjs = ['18236120000158', '50499508000154'];

foreach ($cnpjs as $cnpj) {
    echo "\nSearching for CNPJ: $cnpj\n";
    $found = false;
    foreach (getAllConnections() as $name => $db) {
        try {
            $stmt = $db->prepare("SELECT * FROM dados_cnpj WHERE cnpj = :cnpj LIMIT 1");
            $stmt->execute([':cnpj' => $cnpj]);
            $row = $stmt->fetch(PDO::FETCH_ASSOC);
            if ($row) {
                echo "Found in Database: $name\n";
                echo "Data snippet:\n";
                foreach ($row as $key => $val) {
                    echo "  $key => $val\n";
                }
                $found = true;
                // No break, check if it's duplicated (unlikely but good to know)
            }
        } catch (Exception $e) {
            echo "Error in $name: " . $e->getMessage() . "\n";
        }
    }
    if (!$found) echo "Not found in any database.\n";
}
