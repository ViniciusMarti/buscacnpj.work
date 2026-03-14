<?php
set_time_limit(0);
ignore_user_abort(true);
require_once __DIR__ . '/config/db.php';

// Ativa o flush para output em tempo real
ob_implicit_flush(true);
while (ob_get_level()) ob_end_clean();

$password = DB_PASS;

echo "<!DOCTYPE html>
<html>
<head>
    <title>Super Cleaner CNPJ - Faxina Pesada</title>
    <style>
        body { background: #0f172a; color: #10b981; font-family: 'Courier New', monospace; padding: 20px; line-height: 1.5; }
        .log-line { border-bottom: 1px solid #1e293b; padding: 5px 0; }
        .error { color: #ef4444; font-weight: bold; }
        .success { color: #22c55e; font-weight: bold; }
        .info { color: #38bdf8; }
        .progress { position: sticky; top: 0; background: #1e293b; padding: 10px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }
        #scroll-anchor { height: 1px; }
    </style>
    <script>
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
        }
        setInterval(scrollToBottom, 500);
    </script>
</head>
<body>
<div class='progress' id='p-bar'>Iniciando Faxina Pesada nos 32 Shards...</div>";

function logMe($msg, $class = "") {
    echo "<div class='log-line $class'>[" . date("H:i:s") . "] $msg</div>";
    @flush();
}

$current = isset($_GET['shard']) ? (int)$_GET['shard'] : 1;
$max = 32;

if ($current > $max) {
    echo "<div class='success' style='font-size: 24px; margin-top: 40px;'>=== FAXINA COMPLETA EM TODOS OS 32 SHARDS! ===</div>";
    echo "<p><a href='painel/' style='color:#38bdf8'>Voltar para o Painel</a></p>";
    exit;
}

$db = "u582732852_buscacnpj" . $current;
echo "<script>document.getElementById('p-bar').innerText = 'Limpando Banco: $db ($current / $max)';</script>";

logMe("--- [SHARD $current / $max] Iniciando: $db ---", "info");

$conn = @new mysqli("localhost", $db, $password, $db);
if ($conn->connect_error) {
    logMe("ERRO DE CONEXÃO: " . $conn->connect_error, "error");
    // Se falhar a conexão, tenta o próximo em 3 segundos
    $next = $current + 1;
    echo "<script>setTimeout(() => { window.location.href='?shard=$next'; }, 3000);</script>";
} else {
    $tables = [
        'empresas' => 'cnpj_basico',
        'estabelecimento' => 'cnpj',
        'socio' => ['cnpj_basico', 'nome_socio', 'qualificacao_socio']
    ];

    foreach ($tables as $table => $pk) {
        logMe("Limpando tabela: [$table]...");
        
        $res = $conn->query("SHOW TABLES LIKE '$table'");
        if ($res->num_rows == 0) {
            logMe("Tabela [$table] inexistente. Pulando.", "error");
            continue;
        }

        // Check if already protected to skip and save time
        $isProtected = false;
        $idxRes = $conn->query("SHOW INDEX FROM $table WHERE Key_name = 'PRIMARY' OR Key_name = 'idx_unique_clean' OR Key_name = 'idx_unique_socio'");
        if ($idxRes && $idxRes->num_rows > 0) {
            logMe("Tabela [$table] JÁ ESTÁ PROTEGIDA. Pulando para ganhar tempo.", "success");
            continue;
        }

        $conn->query("DROP TABLE IF EXISTS {$table}_new");
        $conn->query("CREATE TABLE {$table}_new LIKE $table");
        
        if (is_array($pk)) {
            $pkItems = implode(",", $pk);
            $conn->query("ALTER TABLE {$table}_new ADD UNIQUE INDEX idx_unique_clean ($pkItems)");
        } else {
            $conn->query("ALTER TABLE {$table}_new ADD PRIMARY KEY ($pk)");
        }

        logMe("Removendo duplicatas... (Aguarde)");
        $conn->query("INSERT IGNORE INTO {$table}_new SELECT * FROM $table");
        $affected = $conn->affected_rows;

        $conn->query("DROP TABLE IF EXISTS {$table}_old");
        $conn->query("RENAME TABLE $table TO {$table}_old, {$table}_new TO $table");
        $conn->query("DROP TABLE {$table}_old");
        
        logMe("Tabela [$table] finalizada. [$affected] registros únicos.", "success");
    }

    $conn->close();
    logMe("Shard $current finalizado com sucesso!", "success");
    
    $next = $current + 1;
    echo "<div class='info'>Aguardando 2 segundos para o próximo Shard ($next)...</div>";
    echo "<script>setTimeout(() => { window.location.href='?shard=$next'; }, 2000);</script>";
}
echo "<div id='scroll-anchor'></div></body></html>";
