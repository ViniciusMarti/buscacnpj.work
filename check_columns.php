<?php
require_once __DIR__ . '/config/db.php';
$db = getDB();
$tables = ['empresas', 'estabelecimentos', 'socios'];
echo "<pre>";
foreach ($tables as $t) {
    echo "Tabela: $t\n";
    try {
        $q = $db->query("DESCRIBE $t");
        if ($q) {
            while ($r = $q->fetch(PDO::FETCH_ASSOC)) {
                echo "  {$r['Field']} ({$r['Type']})\n";
            }
        } else {
            echo "  Nao foi possivel descrever a tabela.\n";
        }
    } catch (Exception $e) {
        echo "  Erro: " . $e->getMessage() . "\n";
    }
    echo "\n";
}
echo "</pre>";
