<?php
/**
 * Utilitários globais para o portal BuscaCNPJ Grátis
 */

/**
 * Converte nomes para Title Case, respeitando preposições em português.
 * Útil para formatar nomes de cidades e empresas.
 */
function titleCase($string) {
    if (empty($string)) return '';
    $small_words = ['de', 'da', 'do', 'das', 'dos', 'e', 'em', 'para'];
    
    // Fallback caso a extensão mbstring do PHP não esteja disponível no Localhost Windows
    $str_lower = function_exists('mb_strtolower') ? mb_strtolower($string) : strtolower($string);
    $words = explode(' ', $str_lower);
    
    foreach ($words as $i => $word) {
        if ($i > 0 && in_array($word, $small_words)) {
            continue;
        }
        $words[$i] = function_exists('mb_convert_case') 
            ? mb_convert_case($word, MB_CASE_TITLE, "UTF-8") 
            : ucfirst($word);
    }
    
    return implode(' ', $words);
}

/**
 * Formata valores monetários de forma amigável (K, M, B, T)
 */
function format_money_friendly($val) {
    $val = (float)$val;
    if ($val >= 1000000000000) {
        return 'R$ ' . number_format($val / 1000000000000, 2, ',', '.') . ' Trilhões';
    } elseif ($val >= 1000000000) {
        return 'R$ ' . number_format($val / 1000000000, 2, ',', '.') . ' Bilhões';
    } elseif ($val >= 1000000) {
        return 'R$ ' . number_format($val / 1000000, 2, ',', '.') . ' Milhões';
    }
    return 'R$ ' . number_format($val, 2, ',', '.');
}

/**
 * Retorna a preposição correta para o estado.
 */
function get_estado_prep($uf) {
    if (!$uf) return 'de';
    $preps = [
        'AC'=>'do', 'AL'=>'de', 'AP'=>'do', 'AM'=>'do', 'BA'=>'da',
        'CE'=>'do', 'DF'=>'do', 'ES'=>'do', 'GO'=>'de', 'MA'=>'do',
        'MT'=>'de', 'MS'=>'de', 'MG'=>'de', 'PA'=>'do', 'PB'=>'da',
        'PR'=>'do', 'PE'=>'de', 'PI'=>'do', 'RJ'=>'do', 'RN'=>'do',
        'RS'=>'do', 'RO'=>'de', 'RR'=>'de', 'SC'=>'de', 'SP'=>'de',
        'SE'=>'de', 'TO'=>'do'
    ];
    return $preps[strtoupper($uf)] ?? 'de';
}

