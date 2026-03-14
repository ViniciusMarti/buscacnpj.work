<?php

header('Content-Type: application/json');

$statusFile = "../import/status.json";

if (!file_exists($statusFile)) {
    echo json_encode(["error" => "Status file not found"]);
    exit;
}

// No more 32 DB connections here. 
// The worker will update the sizes in the JSON occasionally.
$status = json_decode(file_get_contents($statusFile), true);

// Include last 15 lines of log
$logFile = "../import/import.log";
$logs = [];
if (file_exists($logFile)) {
    $file = file($logFile);
    $logs = array_slice($file, -15);
}
$status['logs'] = $logs;

echo json_encode($status);
