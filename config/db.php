<?php
// Configuração centralizada do banco de dados SQLite
// O banco de dados fica na raiz da conta, fora do public_html para segurança e deploy Git
define('DB_PATH', dirname(__DIR__, 2) . '/database_cnpj.sqlite');
define('CNAE_DB_PATH', __DIR__ . '/../database/cnae.db');

function getDB(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        try {
            // Verificar se o arquivo existe (opcional, mas bom para debug)
            if (!file_exists(DB_PATH)) {
                // Caso não encontre no caminho padrão, tenta caminho relativo simples para o servidor
                // Tenta localizar na pasta raiz do domínio (comum na Hostinger)
                $path = dirname($_SERVER['DOCUMENT_ROOT']) . '/database_cnpj.sqlite';
                if (!file_exists($path)) {
                    // Fallback para o caminho definido
                    $path = DB_PATH;
                }
            } else {
                $path = DB_PATH;
            }

            $dsn = "sqlite:" . $path;
            $options = [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ];
            $pdo = new PDO($dsn, null, null, $options);
            
            // Habilitar performance em SQLite
            $pdo->exec("PRAGMA journal_mode = WAL;");
            $pdo->exec("PRAGMA synchronous = NORMAL;");
            
        } catch (PDOException $e) {
            die("Erro ao conectar com o banco de dados SQLite: " . $e->getMessage());
        }
    }
    return $pdo;
}

function getCNAEDB(): ?PDO {
    static $pdo_cnae = null;
    static $tried = false;
    if ($tried) return $pdo_cnae;
    $tried = true;
    try {
        // Tenta caminho relativo ao projeto (local e servidor dentro de public_html)
        $path = CNAE_DB_PATH;
        // Fallback: tenta ao lado do database_cnpj.sqlite na raiz da conta (servidor)
        if (!file_exists($path)) {
            $path = dirname($_SERVER['DOCUMENT_ROOT'] ?? __DIR__) . '/cnae.db';
        }
        if (!file_exists($path)) {
            return null; // Banco CNAE não encontrado — silencioso, não quebra a página
        }
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        $pdo_cnae = new PDO("sqlite:" . $path, null, null, $options);
    } catch (PDOException $e) {
        $pdo_cnae = null; // Silencioso
    }
    return $pdo_cnae;
}
