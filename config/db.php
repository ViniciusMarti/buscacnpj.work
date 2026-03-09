<?php
// Configuração centralizada do banco de dados MySQL
// Banco e usuário: u501810552_buscacnpj
define('DB_HOST', 'localhost'); // Na Hostinger, o DB host geralmente é localhost
define('DB_NAME', 'u501810552_buscacnpj');
define('DB_USER', 'u501810552_buscacnpj');
// ATENÇÃO: Por favor, substitua a string abaixo pela senha real do banco MySQL criado
define('DB_PASS', 'qPMwBp#WW*BN6k'); 

function getDB(): PDO {
    static $pdo = null;
    if ($pdo === null) {
        try {
            $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
            $options = [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES   => false,
            ];
            $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
            
        } catch (PDOException $e) {
            die("Erro ao conectar com o banco de dados MySQL: " . $e->getMessage());
        }
    }
    return $pdo;
}

// Como você indicou o mesmo banco, estou assumindo que a tabela de CNAE ('cnaes')
// também foi exportada ou criada dentro deste banco MySQL. 
function getCNAEDB(): ?PDO {
    try {
        return getDB();
    } catch (Exception $e) {
        return null;
    }
}
