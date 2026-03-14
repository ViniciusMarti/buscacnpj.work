<?php
set_time_limit(0);
require_once __DIR__ . '/config/db.php';

$bancos = [];
for($i=1;$i<=32;$i++){
    $bancos[]="u582732852_buscacnpj".$i;
}

$password = DB_PASS;

echo "<pre>";
echo "=== CRIANDO TABELAS FALTANTES NOS 32 SHARDS ===\n\n";

foreach ($bancos as $db) {
    echo "Processando $db... ";
    $conn = @new mysqli("localhost", $db, $password, $db);
    if ($conn->connect_error) {
        echo "[ERRO CONEXAO]\n";
        continue;
    }

    // 1. Tabela estabelecimentos
    $sql_est = "CREATE TABLE IF NOT EXISTS estabelecimentos (
        ano INT,
        mes INT,
        data DATE,
        cnpj VARCHAR(14) PRIMARY KEY,
        cnpj_basico VARCHAR(8),
        cnpj_ordem VARCHAR(4),
        cnpj_dv VARCHAR(2),
        identificador_matriz_filial INT,
        nome_fantasia VARCHAR(255),
        situacao_cadastral INT,
        data_situacao_cadastral DATE,
        motivo_situacao_cadastral INT,
        nome_cidade_exterior VARCHAR(255),
        id_pais INT,
        data_inicio_atividade DATE,
        cnae_fiscal_principal VARCHAR(10),
        cnae_fiscal_secundaria TEXT,
        sigla_uf VARCHAR(2),
        id_municipio VARCHAR(10),
        id_municipio_rf VARCHAR(10),
        tipo_logradouro VARCHAR(50),
        logradouro VARCHAR(255),
        numero VARCHAR(50),
        complemento VARCHAR(255),
        bairro VARCHAR(150),
        cep VARCHAR(8),
        ddd_1 VARCHAR(5),
        telefone_1 VARCHAR(20),
        ddd_2 VARCHAR(5),
        telefone_2 VARCHAR(20),
        ddd_fax VARCHAR(5),
        fax VARCHAR(20),
        email VARCHAR(255),
        situacao_especial VARCHAR(255),
        data_situacao_especial DATE,
        INDEX idx_basico (cnpj_basico),
        INDEX idx_uf (sigla_uf)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";

    if (!$conn->query($sql_est)) {
        echo "[ERRO estabelecimentos: " . $conn->error . "] ";
    } else {
        echo "[EST OK] ";
    }

    // 2. Tabela socios
    $sql_soc = "CREATE TABLE IF NOT EXISTS socios (
        ano INT,
        mes INT,
        data DATE,
        cnpj_basico VARCHAR(8),
        tipo INT,
        nome_socio VARCHAR(255),
        documento VARCHAR(20),
        qualificacao_socio INT,
        data_entrada_sociedade DATE,
        id_pais INT,
        cpf_representante_legal VARCHAR(15),
        nome_representante_legal VARCHAR(255),
        qualificacao_representante_legal INT,
        faixa_etaria INT,
        INDEX idx_basico_socio (cnpj_basico)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";

    if (!$conn->query($sql_soc)) {
        echo "[ERRO socios: " . $conn->error . "] ";
    } else {
        echo "[SOC OK] ";
    }

    $conn->close();
    echo "\n";
}

echo "\n=== OPERACAO CONCLUIDA ===\n";
echo "</pre>";
