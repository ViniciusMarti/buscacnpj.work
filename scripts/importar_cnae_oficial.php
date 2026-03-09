<?php
/**
 * Script para converter o arquivo CNAECSV oficial da Receita Federal em um banco SQLite (cnae.db)
 */

$csvFile = __DIR__ . '/../database/F.K03200$Z.D60214.CNAECSV';
$dbFile = __DIR__ . '/../database/cnae.db';

if (!file_exists($csvFile)) {
    die("Erro: Arquivo CSV não encontrado em $csvFile\n");
}

try {
    // Se o banco já existir, vamos recriá-lo para garantir que os dados sejam os oficiais
    if (file_exists($dbFile)) {
        unlink($dbFile);
    }

    $db = new PDO("sqlite:$dbFile");
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Criar tabela
    $db->exec("CREATE TABLE cnaes (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )");

    $stmt = $db->prepare("INSERT INTO cnaes (codigo, descricao) VALUES (?, ?)");

    $handle = fopen($csvFile, "r");
    $count = 0;

    $db->beginTransaction();

    while (($line = fgets($handle)) !== false) {
        // O formato é "0111301";"Cultivo de arroz"
        // CSV da Receita costuma usar ponto e vírgula e aspas, codificado em ISO-8859-1
        $data = str_getcsv($line, ";", '"');
        
        if (count($data) >= 2) {
            $codigo = trim($data[0]);
            // Converter de ISO-8859-1 para UTF-8 para o banco de dados
            $descricao = utf8_encode(trim($data[1]));
            
            $stmt->execute([$codigo, $descricao]);
            $count++;
        }
    }

    $db->commit();
    fclose($handle);

    echo "Sucesso! $count registros importados para $dbFile.\n";

} catch (Exception $e) {
    if (isset($db) && $db->inTransaction()) {
        $db->rollBack();
    }
    die("Erro: " . $e->getMessage() . "\n");
}
