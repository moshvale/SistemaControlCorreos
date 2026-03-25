# Cliente Outlook Sync - Instrucciones Rápidas

## Para usuarios finales

### Instalación (primera vez)

1. Copia estos archivos a una carpeta en tu PC:
   - `outlook_sync_agent.py`
   - `outlook_sync_config.json.example`
   - `install_client.bat`
   - `run_sync_client.bat`

2. **Abre PowerShell como Administrador** y ejecuta:
   ```powershell
   cd C:\ruta\a\tu\carpeta
   .\install_client.bat
   ```

3. Edita el archivo `outlook_sync_config.json` que se creó:
   ```json
   {
       "server_url": "http://192.168.1.100:5000",
       "username": "tu_usuario",
       "password": "tu_contraseña",
       "limit": 10
   }
   ```
   - `server_url`: Preguntar al administrador (ej: `http://192.168.1.100:5000`)
   - `username`: Tu usuario en el servidor
   - `password`: Tu contraseña
   - `limit`: Cantidad de correos a sincronizar (default: 10)

### Uso diario

**Opción A: Sincronización manual**
- Haz doble clic en `run_sync_client.bat`
- Espera a que termine (mostrará "✓ Sincronización exitosa")

**Opción B: Sincronización automática cada 15 minutos**
- Abre PowerShell como Administrador
- Ejecuta:
  ```powershell
  cd C:\ruta\a\tu\carpeta
  .\venv\Scripts\Activate.ps1
  python outlook_sync_agent.py --daemon --interval 15
  ```

### Requisitos

- ✅ Windows con Outlook instalado
- ✅ Acceso a la red local del servidor
- ✅ Usuario y contraseña en el servidor

### Solución de problemas

**"Error de autenticación: 401"**
- Verifica usuario y contraseña en `outlook_sync_config.json`

**"Connection refused"**
- Verifica que `server_url` es correcto
- Verifica que el servidor está en línea

**"ModuleNotFoundError: No module named 'pywin32'"**
- Abre PowerShell como Administrador y ejecuta:
  ```powershell
  python -m pywin32_postinstall -install
  ```

**Los correos no aparecen**
- Abre Outlook en tu PC (es necesario que esté instalado)
- Verifica que tienes documentos en la carpeta "Enviados"

### Revisión de logs

El archivo `outlook_sync_agent.log` tiene detalles de cada sincronización. Ponlo en el servidor si hay problemas.
