@echo off
REM Cliente Outlook Sync Agent - Arrancador para Windows

echo.
echo ========================================
echo   Outlook Sync Agent - Client
echo ========================================
echo.

REM Verificar si está en la carpeta correcta
if not exist "outlook_sync_agent.py" (
    echo Error: outlook_sync_agent.py no encontrado en esta carpeta
    echo Asegúrate de copiar todos los archivos en la misma carpeta
    pause
    exit /b 1
)

if not exist "venv" (
    echo Error: Virtual environment no está creado
    echo Ejecuta primero:
    echo   python -m venv venv
    echo   .\venv\Scripts\Activate.ps1
    echo   pip install requests pywin32
    echo   python -m pywin32_postinstall -install
    pause
    exit /b 1
)

REM Activar venv y ejecutar
call venv\Scripts\activate.bat
python outlook_sync_agent.py %*

pause
