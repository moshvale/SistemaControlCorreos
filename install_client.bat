@echo off
REM Script de instalación del Cliente Outlook Sync Agent
REM Ejecutar con permisos de administrador

echo.
echo ========================================
echo   Instalador Cliente Outlook Sync Agent
echo ========================================
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "outlook_sync_agent.py" (
    echo Error: outlook_sync_agent.py no encontrado
    echo Este script debe ejecutarse en la misma carpeta que outlook_sync_agent.py
    pause
    exit /b 1
)

echo [1/4] Creando virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo Error creando venv. Verifica que Python está instalado
        pause
        exit /b 1
    )
) else (
    echo Virtual environment ya existe
)

echo.
echo [2/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install requests pywin32
if errorlevel 1 (
    echo Error instalando paquetes
    pause
    exit /b 1
)

echo.
echo [3/4] Registrando componentes pywin32...
python -m pywin32_postinstall -install
if errorlevel 1 (
    echo.
    echo Advertencia: pywin32_postinstall puede requerir ejecución como administrador
    echo Si ves este error, abre PowerShell como Administrador y ejecuta:
    echo   python -m pywin32_postinstall -install
)

echo.
echo [4/4] Creando archivo de configuración...
if not exist "outlook_sync_config.json" (
    if exist "outlook_sync_config.json.example" (
        copy outlook_sync_config.json.example outlook_sync_config.json
        echo Archivo outlook_sync_config.json creado
        echo.
        echo TE FALTA EDITAR outlook_sync_config.json CON:
        echo   - server_url: IP del servidor (ej: http://192.168.1.100:5000^)
        echo   - username: Tu usuario en el servidor
        echo   - password: Tu contraseña
        echo   - limit: Cantidad máxima de correos a sincronizar
    )
) else (
    echo outlook_sync_config.json ya existe
)

echo.
echo ========================================
echo   Instalación completada!
echo ========================================
echo.
echo Pasos siguientes:
echo 1. Edita outlook_sync_config.json con tus datos
echo 2. Ejecuta: run_sync_client.bat
echo.
pause
