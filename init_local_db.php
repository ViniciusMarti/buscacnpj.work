<?php
require_once __DIR__ . '/config/db.php';

try {
    $db = getDB();

    // Cria a tabela caso não exista (deleta se já houver lixo)
    $db->exec("DROP TABLE IF EXISTS dados_cnpj");
    $sql = "CREATE TABLE IF NOT EXISTS dados_cnpj (
        cnpj TEXT PRIMARY KEY,
        razao_social TEXT,
        nome_fantasia TEXT,
        situacao_cadastral TEXT,
        data_inicio_atividade TEXT,
        sigla_uf TEXT,
        ddd_1 TEXT,
        telefone_1 TEXT,
        ddd_2 TEXT,
        telefone_2 TEXT,
        email TEXT,
        capital_social DECIMAL(18,2),
        cnae_fiscal_principal TEXT,
        cnae_principal_descricao TEXT,
        cnae_fiscal_secundaria TEXT,
        porte TEXT,
        socios_texto TEXT,
        natureza_juridica TEXT,
        opcao_simples TEXT,
        data_opcao_simples TEXT,
        opcao_mei TEXT,
        data_opcao_mei TEXT,
        id_municipio TEXT,
        municipio TEXT,
        bairro TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        cep TEXT
    )";
    $db->exec($sql);

    $stmt = $db->prepare("INSERT OR REPLACE INTO dados_cnpj (cnpj, razao_social, nome_fantasia, situacao_cadastral, data_inicio_atividade, sigla_uf, ddd_1, telefone_1, email, capital_social, cnae_fiscal_principal, cnae_principal_descricao, cnae_fiscal_secundaria, porte, socios_texto, municipio, bairro, logradouro, numero) VALUES (:cnpj, :razao_social, :nome_fantasia, :situacao, :data_abertura, :uf, :ddd_1, :telefone, :email, :capital_social, :cnae_principal_codigo, :cnae_principal_descricao, :cnaes_secundarios, :porte, :quadro_societario, :municipio, :bairro, :logradouro, :numero)");
    
    // Lista de empresas com vários estados para testar página e rankings
    $empresas = [
        [
            'cnpj' => '11465216000149', 'razao_social' => 'JUSSI INTENTION MARKETING LTDA',
            'nome_fantasia' => 'JUSSI', 'situacao' => 'ATIVA', 'logradouro' => 'RUA ALCEBIADES PLAGGE',
            'numero' => '42', 'complemento' => 'ANDAR 1 E 2', 'bairro' => 'VILA MARIANA',
            'municipio' => 'SAO PAULO', 'uf' => 'SP', 'telefone' => '(11) 3266-4001',
            'email' => 'financeiro@jussi.com.br', 'capital_social' => 50000.00, 'cnae_principal_codigo' => '73.11-4-00',
            'cnae_principal_descricao' => 'Agências de publicidade', 'cnaes_secundarios' => '62.01-5-01 - Desenvolvimento; 62.04-0-00 - Consultoria',
            'data_abertura' => '2010-01-05', 'porte' => 'MICRO EMPRESA', 'quadro_societario' => 'HENRIQUE BOSQUIER - Sócio; JOAO CUSTODIO - Sócio'
        ],
        [
            'cnpj' => '33000167000101', 'razao_social' => 'PETROLEO BRASILEIRO S A PETROBRAS',
            'nome_fantasia' => 'PETROBRAS', 'situacao' => 'ATIVA', 'logradouro' => 'AVENIDA REPUBLICA DO CHILE',
            'numero' => '65', 'complemento' => '', 'bairro' => 'CENTRO',
            'municipio' => 'RIO DE JANEIRO', 'uf' => 'RJ', 'telefone' => '(21) 3224-4477',
            'email' => 'contato@petrobras.com.br', 'capital_social' => 205431000000.00, 'cnae_principal_codigo' => '19.21-7-00',
            'cnae_principal_descricao' => 'Fabricação de produtos do refino de petróleo', 'cnaes_secundarios' => '',
            'data_abertura' => '1953-10-03', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ],
        [
            'cnpj' => '33592510000154', 'razao_social' => 'VALE S.A.',
            'nome_fantasia' => 'VALE', 'situacao' => 'ATIVA', 'logradouro' => 'PRAIA DE BOTAFOGO',
            'numero' => '186', 'complemento' => '', 'bairro' => 'BOTAFOGO',
            'municipio' => 'RIO DE JANEIRO', 'uf' => 'RJ', 'telefone' => '(21) 3814-4477',
            'email' => 'vale@vale.com', 'capital_social' => 77300000000.00, 'cnae_principal_codigo' => '07.11-6-00',
            'cnae_principal_descricao' => 'Extração de minério de ferro', 'cnaes_secundarios' => '',
            'data_abertura' => '1943-01-11', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ],
        [
            'cnpj' => '00000000000191', 'razao_social' => 'BANCO DO BRASIL SA',
            'nome_fantasia' => 'BANCO DO BRASIL', 'situacao' => 'ATIVA', 'logradouro' => 'SAUN QUADRA 5 LOTE B',
            'numero' => 'S/N', 'complemento' => 'TORRES I, II E III', 'bairro' => 'ASA NORTE',
            'municipio' => 'BRASILIA', 'uf' => 'DF', 'telefone' => '(61) 3493-9000',
            'email' => 'contato@bb.com.br', 'capital_social' => 90000000000.00, 'cnae_principal_codigo' => '64.22-1-00',
            'cnae_principal_descricao' => 'Bancos múltiplos', 'cnaes_secundarios' => '',
            'data_abertura' => '1966-08-01', 'porte' => 'DEMAIS', 'quadro_societario' => 'GOVERNO FEDERAL - Sócio'
        ],
        [
            'cnpj' => '15102288000182', 'razao_social' => 'BAHIA DESENVOLVIMENTO S.A',
            'nome_fantasia' => 'BAHIA TEC', 'situacao' => 'ATIVA', 'logradouro' => 'AVENIDA ANTONIO CARLOS MAGALHAES',
            'numero' => '1000', 'complemento' => 'SALA 501', 'bairro' => 'PITUBA',
            'municipio' => 'SALVADOR', 'uf' => 'BA', 'telefone' => '(71) 3333-4444',
            'email' => 'contato@bahiatec.br', 'capital_social' => 150000.00, 'cnae_principal_codigo' => '62.02-3-00',
            'cnae_principal_descricao' => 'Desenvolvimento de programas de computador', 'cnaes_secundarios' => '',
            'data_abertura' => '2012-05-10', 'porte' => 'EMPRESA DE PEQUENO PORTE', 'quadro_societario' => 'MARIA DA SILVA - Sócio'
        ],
        [
            'cnpj' => '13574594000196', 'razao_social' => 'COMERCIO DE ALIMENTOS BAIANA LTDA',
            'nome_fantasia' => 'MERCADINHO BAIANO', 'situacao' => 'ATIVA', 'logradouro' => 'RUA CONSELHEIRO FRANCO',
            'numero' => '45', 'complemento' => '', 'bairro' => 'CENTRO',
            'municipio' => 'FEIRA DE SANTANA', 'uf' => 'BA', 'telefone' => '(75) 3221-1234',
            'email' => 'vendas@mercadinhobaiano.com.br', 'capital_social' => 50000.00, 'cnae_principal_codigo' => '47.12-1-00',
            'cnae_principal_descricao' => 'Comércio varejista em geral', 'cnaes_secundarios' => '',
            'data_abertura' => '2011-09-01', 'porte' => 'MICRO EMPRESA', 'quadro_societario' => 'JOSE SANTOS - Sócio'
        ],
        [
            'cnpj' => '84429695000111', 'razao_social' => 'WEG EQUIPAMENTOS ELETRICOS S/A',
            'nome_fantasia' => 'WEG', 'situacao' => 'ATIVA', 'logradouro' => 'AVENIDA PREFEITO WALDEMAR GRUBBA',
            'numero' => '3000', 'complemento' => '', 'bairro' => 'VILA LALAU',
            'municipio' => 'JARAGUA DO SUL', 'uf' => 'SC', 'telefone' => '(47) 3276-4000',
            'email' => 'weg@weg.net', 'capital_social' => 5000000000.00, 'cnae_principal_codigo' => '27.10-4-02',
            'cnae_principal_descricao' => 'Fabricação de motores elétricos', 'cnaes_secundarios' => '',
            'data_abertura' => '1970-05-15', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ],
        [
            'cnpj' => '07526557000100', 'razao_social' => 'AMBEV S.A.',
            'nome_fantasia' => 'AMBEV', 'situacao' => 'ATIVA', 'logradouro' => 'RUA DR. RENATO PAES DE BARROS',
            'numero' => '1017', 'complemento' => 'ANDAR 4', 'bairro' => 'ITAIM BIBI',
            'municipio' => 'SAO PAULO', 'uf' => 'SP', 'telefone' => '(11) 2122-1234',
            'email' => 'contato@ambev.com.br', 'capital_social' => 58000000000.00, 'cnae_principal_codigo' => '11.13-5-02',
            'cnae_principal_descricao' => 'Fabricação de cervejas e chopes', 'cnaes_secundarios' => '',
            'data_abertura' => '2005-07-25', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ],
        [
            'cnpj' => '16670085000155', 'razao_social' => 'LOCALIZA RENT A CAR S.A',
            'nome_fantasia' => 'LOCALIZA', 'situacao' => 'ATIVA', 'logradouro' => 'AVENIDA BERNARDO MONTEIRO',
            'numero' => '1563', 'complemento' => '', 'bairro' => 'FUNCIONARIOS',
            'municipio' => 'BELO HORIZONTE', 'uf' => 'MG', 'telefone' => '(31) 3247-7000',
            'email' => 'investidores@localiza.com', 'capital_social' => 12000000000.00, 'cnae_principal_codigo' => '77.11-0-00',
            'cnae_principal_descricao' => 'Locação de automóveis', 'cnaes_secundarios' => '',
            'data_abertura' => '1973-10-18', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ],
        [
            'cnpj' => '61079117000105', 'razao_social' => 'ALPARGATAS S.A.',
            'nome_fantasia' => 'ALPARGATAS', 'situacao' => 'BAIXADA', 'logradouro' => 'AVENIDA DAS NACOES UNIDAS',
            'numero' => '14261', 'complemento' => 'ALA A', 'bairro' => 'VILA GERTRUDES',
            'municipio' => 'SAO PAULO', 'uf' => 'SP', 'telefone' => '(11) 3848-1234',
            'email' => 'contato@alpargatas.com.br', 'capital_social' => 3000000000.00, 'cnae_principal_codigo' => '15.20-4-01',
            'cnae_principal_descricao' => 'Fabricação de calçados', 'cnaes_secundarios' => '',
            'data_abertura' => '1966-10-21', 'porte' => 'DEMAIS', 'quadro_societario' => 'DIRETORIA - Administrador'
        ]
    ];

    foreach ($empresas as $empresa) {
        $stmt->execute([
            ':cnpj' => $empresa['cnpj'],
            ':razao_social' => $empresa['razao_social'],
            ':nome_fantasia' => $empresa['nome_fantasia'],
            ':situacao' => $empresa['situacao'],
            ':data_abertura' => $empresa['data_abertura'],
            ':uf' => $empresa['uf'],
            ':ddd_1' => '11',
            ':telefone' => $empresa['telefone'],
            ':email' => $empresa['email'],
            ':capital_social' => $empresa['capital_social'],
            ':cnae_principal_codigo' => $empresa['cnae_principal_codigo'],
            ':cnae_principal_descricao' => $empresa['cnae_principal_descricao'],
            ':cnaes_secundarios' => $empresa['cnaes_secundarios'],
            ':porte' => $empresa['porte'],
            ':quadro_societario' => $empresa['quadro_societario'],
            ':municipio' => $empresa['municipio'],
            ':bairro' => $empresa['bairro'],
            ':logradouro' => $empresa['logradouro'],
            ':numero' => $empresa['numero']
        ]);
    }

    echo "Banco de dados local populado com " . count($empresas) . " empresas para testes em multiplos estados (SP, RJ, SC, BA, MG, DF)!\n";

} catch (PDOException $e) {
    die("Erro ao iniciar DB: " . $e->getMessage());
}
