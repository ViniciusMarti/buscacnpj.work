<?php
set_time_limit(0);
ini_set('memory_limit', '512M');

// Force immediate output to browser
ob_implicit_flush(true);
while (ob_get_level()) ob_end_clean();

require_once __DIR__ . '/config/db.php';

$shard_start = isset($_GET['start']) ? intval($_GET['start']) : 1;
$shard_end = isset($_GET['end']) ? intval($_GET['end']) : 32;

echo "<pre>";
echo "=== INICIANDO FAXINA DE DUPLICATAS (Shards $shard_start ate $shard_end) ===\n";
echo "Este processo pode demorar. Nao feche esta aba.\n\n";

$bancos = [];
for($i=$shard_start;$i<=$shard_end;$i++){
    $bancos[]="u582732852_buscacnpj".$i;
}

$password = DB_PASS;

foreach ($bancos as $db) {
    echo "Processando $db... " . date('H:i:s') . "\n";
    flush(); 

    $conn = @new mysqli("localhost", $db, $password, $db);
    if ($conn->connect_error) {
        echo "  [ERRO] Falha na conexao: " . $conn->connect_error . "\n";
        continue;
    }

    // 1. Empresas
    echo "  - Verificando 'empresas'... "; flush();
    $conn->query("ALTER TABLE empresas ADD PRIMARY KEY (cnpj_basico)");
    if ($conn->errno == 1062) {
         echo "Limpando duplicatas... "; flush();
         $conn->query("CREATE TABLE IF NOT EXISTS empresas_new LIKE empresas");
         $conn->query("ALTER TABLE empresas_new ADD PRIMARY KEY (cnpj_basico)");
         $conn->query("INSERT IGNORE INTO empresas_new SELECT * FROM empresas");
         $conn->query("RENAME TABLE empresas TO empresas_old, empresas_new TO empresas");
         $conn->query("DROP TABLE empresas_old");
         echo "OK.\n";
    } elseif ($conn->errno == 0) {
         echo "PK adicionada.\n";
    } else {
         echo "Ja possui PK ou erro: " . $conn->error . "\n";
    }
    flush();

    // 2. Estabelecimentos
    echo "  - Verificando 'estabelecimentos'... "; flush();
    $conn->query("ALTER TABLE estabelecimentos ADD PRIMARY KEY (cnpj)");
    if ($conn->errno == 1062) {
         echo "Limpando duplicatas... "; flush();
         $conn->query("CREATE TABLE IF NOT EXISTS estabelecimentos_new LIKE estabelecimentos");
         $conn->query("ALTER TABLE estabelecimentos_new ADD PRIMARY KEY (cnpj)");
         $conn->query("INSERT IGNORE INTO estabelecimentos_new SELECT * FROM estabelecimentos");
         $conn->query("RENAME TABLE estabelecimentos TO estabelecimentos_old, estabelecimentos_new TO estabelecimentos");
         $conn->query("DROP TABLE estabelecimentos_old");
         echo "OK.\n";
    } elseif ($conn->errno == 0) {
         echo "PK adicionada.\n";
    } else {
         echo "Ja possui PK ou erro.\n";
    }
    flush();

    // 3. Socios
    echo "  - Verificando 'socios'... "; flush();
    $conn->query("ALTER TABLE socios ADD UNIQUE INDEX idx_socio_unique (cnpj_basico, nome_socio(191), qualificacao_socio)");
    if ($conn->errno == 1062) {
         echo "Limpando duplicatas... "; flush();
         $conn->query("CREATE TABLE IF NOT EXISTS socios_new LIKE socios");
         $conn->query("ALTER TABLE socios_new ADD UNIQUE INDEX idx_socio_unique (cnpj_basico, nome_socio(191), qualificacao_socio)");
         $conn->query("INSERT IGNORE INTO socios_new SELECT * FROM socios");
         $conn->query("RENAME TABLE socios TO socios_old, socios_new TO socios");
         $conn->query("DROP TABLE socios_old");
         echo "OK.\n";
    } elseif ($conn->errno == 0) {
         echo "Indice unico adicionado.\n";
    } else {
         echo "Ja possui indice ou erro.\n";
    }
    
    $conn->close();
    echo "Finalizado $db.\n\n";
    flush();
}

echo "=== OPERACAO CONCLUIDA COM SUCESSO ===\n";
if ($shard_end < 32) {
    $next = $shard_end + 1;
    echo "Proximo lote recomendável: ?start=$next&end=" . ($next + 4) . "\n";
}
echo "</pre>";
