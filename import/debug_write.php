<?php
$f = __DIR__ . '/status.json';
$data = json_decode(file_get_contents($f), true);
$data['debug_time'] = time();
$res = file_put_contents($f, json_encode($data), LOCK_EX);
if ($res) {
    echo "Sucesso ao escrever em $f. Bytes: $res";
} else {
    echo "ERRO ao escrever em $f";
}
