<?php

class MySQLSharder {
    private $host = '193.203.175.195';
    private $password = 'qPMwBp#WW*BN6k';
    private $connections = [];
    private $dbPrefix = 'u582732852_buscacnpj';
    private $shardCount = 32;

    public function getShardId($cnpj_basico) {
        // shard = (cnpj_basico % 32) + 1
        return (intval($cnpj_basico) % $this->shardCount) + 1;
    }

    private $tableColumns = [];

    public function getConnection($shardId) {
        if (isset($this->connections[$shardId])) {
            return $this->connections[$shardId];
        }

        $dbName = $this->dbPrefix . $shardId;
        $user = $dbName;
        
        // Hostinger optimization: try IP then localhost
        $hosts = [$this->host, 'localhost', '127.0.0.1'];
        $lastException = null;

        foreach ($hosts as $h) {
            try {
                $dsn = "mysql:host={$h};dbname={$dbName};charset=utf8mb4";
                $options = [
                    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES   => false,
                ];
                $pdo = new PDO($dsn, $user, $this->password, $options);
                $this->connections[$shardId] = $pdo;
                return $pdo;
            } catch (PDOException $e) {
                $lastException = $e;
                continue;
            }
        }

        error_log("Connection failed for shard $shardId: " . $lastException->getMessage());
        throw $lastException;
    }

    private function getTableColumns($pdo, $table) {
        $cacheKey = $table;
        if (isset($this->tableColumns[$cacheKey])) return $this->tableColumns[$cacheKey];

        $stmt = $pdo->query("DESCRIBE $table");
        $columns = [];
        foreach ($stmt->fetchAll() as $row) {
            $columns[] = $row['Field'];
        }
        $this->tableColumns[$cacheKey] = $columns;
        return $columns;
    }

    public function batchInsert($table, $data, $shardId) {
        if (empty($data)) return;

        $pdo = $this->getConnection($shardId);
        $validColumns = $this->getTableColumns($pdo, $table);
        
        // Filtrar colunas do dado para bater com as do banco
        $filteredData = [];
        $dataColumns = array_keys($data[0]);
        $intersection = array_intersect($dataColumns, $validColumns);
        
        if (empty($intersection)) {
             throw new Exception("Nenhuma coluna compatível encontrada entre BigQuery e a tabela MySQL '$table'.");
        }

        foreach ($data as $row) {
            $newRow = [];
            foreach ($intersection as $col) {
                $newRow[$col] = $row[$col];
            }
            $filteredData[] = $newRow;
        }

        $columnList = implode(', ', $intersection);
        $placeholders = '(' . implode(', ', array_fill(0, count($intersection), '?')) . ')';
        $allPlaceholders = implode(', ', array_fill(0, count($filteredData), $placeholders));

        $sql = "INSERT IGNORE INTO $table ($columnList) VALUES $allPlaceholders";
        
        $flatValues = [];
        foreach ($filteredData as $row) {
            foreach ($intersection as $col) {
                $flatValues[] = $row[$col];
            }
        }

        $stmt = $pdo->prepare($sql);
        return $stmt->execute($flatValues);
    }
}
