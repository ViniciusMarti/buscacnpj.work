<?php
echo "<pre>";
$pastas = ['empresas', 'estabelecimentos', 'socios'];
foreach ($pastas as $p) {
    echo "Pasta: $p\n";
    $arquivos = glob(__DIR__ . "/export-cnpj-bd/$p/*.gz");
    if (empty($arquivos)) {
        echo "  Nenhum arquivo .gz encontrado em ../export-cnpj-bd/$p/\n";
        continue;
    }
    
    $file = $arquivos[0];
    echo "  Lendo cabecalho de: " . basename($file) . "\n";
    $gz = gzopen($file, "r");
    if ($gz) {
        $header = gzgets($gz);
        echo "  Header: " . $header;
        $firstRow = gzgets($gz);
        echo "  Data  : " . $firstRow;
        gzclose($gz);
    } else {
        echo "  Erro ao abrir arquivo.\n";
    }
    echo "\n";
}
echo "</pre>";
