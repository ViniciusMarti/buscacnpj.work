<?php
// Configuração centralizada do banco de dados SQLite
define('DB_PATH', __DIR__ . '/../database/csv_final/database_cnpj.sqlite');

function getDB(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        try {
            // Verificar se o arquivo existe (opcional, mas bom para debug)
            if (!file_exists(DB_PATH)) {
                // Caso não encontre no caminho padrão, tenta caminho relativo simples para o servidor
                $path = $_SERVER['DOCUMENT_ROOT'] . '/database/csv_final/database_cnpj.sqlite';
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
