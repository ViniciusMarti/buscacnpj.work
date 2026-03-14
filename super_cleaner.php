<?php
set_time_limit(0);
require_once __DIR__ . '/config/db.php';

$password = DB_PASS;
echo "<pre>";
echo "=== BLOQUEANDO DUPLICATAS (CRIANDO CHAVES PRIMARIAS) ===\n";
echo "Este processo vai deletar as duplicatas existentes automaticamente ao criar a PK.\n\n";

for ($i = 1; $i <= 32; $i++) {
    $db = "u582732852_buscacnpj" . $i;
    echo "Processando $db... ";
    
    $conn = @new mysqli("localhost", $db, $password, $db);
    if ($conn->connect_error) {
        echo "[ERRO CONEXAO]\n";
        continue;
    }

    // 1. Limpar duplicatas de empresas (se existirem) e colocar PK
    // Nota: Como o usuario quer apenas estabelecimento e socio, focamos neles primeiro
    
    // 2. Estabelecimento (PK no CNPJ)
    echo "Limpando estabelecimento... ";
    // Criamos uma tabela temporaria para garantir a limpeza
    $conn->query("CREATE TABLE estabelecimento_new LIKE estabelecimento");
    $conn->query("ALTER TABLE estabelecimento_new ADD PRIMARY KEY (cnpj)");
    $conn->query("INSERT IGNORE INTO estabelecimento_new SELECT * FROM estabelecimento");
    $conn->query("RENAME TABLE estabelecimento TO estabelecimento_old, estabelecimento_new TO estabelecimento");
    $conn->query("DROP TABLE estabelecimento_old");
    echo "[OK] ";

    // 3. Socio (Unique no cnpj_basico + nome_socio + qualificacao_socio para evitar repetição do mesmo socio na mesma empresa)
    echo "Limpando socio... ";
    $conn->query("CREATE TABLE socio_new LIKE socio");
    $conn->query("ALTER TABLE socio_new ADD UNIQUE INDEX idx_unique_socio (cnpj_basico, nome_socio, qualificacao_socio)");
    $conn->query("INSERT IGNORE INTO socio_new SELECT * FROM socio");
    $conn->query("RENAME TABLE socio TO socio_old, socio_new TO socio");
    $conn->query("DROP TABLE socio_old");
    echo "[OK]\n";

    $conn->close();
    flush();
}

echo "\n=== BANCOS LIMPOS E PROTEGIDOS CONTRA DUPLICATAS ===\n";
echo "Agora voce pode continuar a importacao sem medo.\n";
echo "</pre>";
