@echo off
echo ===================================================
echo     INICIANDO SERVIDOR LOCAL DO BUSCACNPJGRATIS
echo ===================================================
echo.
echo Testando existencia do PHP...
php -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O PHP nao foi encontrado! Tente reiniciar o seu computador ou terminal.
    pause
    exit
)

echo Preparando banco de dados local basico para testes...
php init_local_db.php
echo.
echo O acesso estara disponivel em: http://localhost:8000
echo.
echo Para desligar o servidor, feche esta janela ou pressione CTRL+C
echo.

echo Inicializando o Servidor da Web...
php -S localhost:8000 router.php
