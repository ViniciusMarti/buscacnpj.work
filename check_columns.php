<?php
require_once __DIR__ . '/config/db.php';
try {
    $db = getDB();
    echo "<h1>Database: " . $db->query('SELECT DATABASE()')->fetchColumn() . "</h1>";
    $stmt = $db->query("DESCRIBE dados_cnpj");
    echo "<table border='1'>";
    while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<tr>";
        foreach($row as $key => $val) {
            echo "<td>$key: $val</td>";
        }
        echo "</tr>";
    }
    echo "</table>";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
