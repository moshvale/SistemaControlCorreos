# Guía de Instalación - Cliente Outlook Sync Agent

## Visión General

El **Outlook Sync Agent** es una solución **Opción 1** que permite que cada usuario en la red local sincronice **su propio Outlook** al servidor centralizado.

### Flujo de funcionamiento:

```
PC Usuario 1: outlook_sync_agent.py → Servidor Central (Puerto 5000)
    ↓
    Obtiene correos locales de su Outlook
    ↓
    Se autentica en el servidor
    ↓
    Envía correos al servidor (se asignan a su usuario)

PC Usuario 2: outlook_sync_agent.py → Servidor Central (Puerto 5000)
    ↓
    Obtiene correos locales de su Outlook
    ↓
    Se autentica en el servidor
    ↓
    Envía correos al servidor (se asignan a su usuario)
```

---

## Instalación en la PC del Usuario (Cliente)

### Paso 1: Copiar archivos

1. Copia estos archivos a la PC del usuario que sincronizará Outlook:
   - `outlook_sync_agent.py` - Script principal del cliente
   - `outlook_sync_config.json.example` - Archivo de ejemplo de configuración

### Paso 2: Instalar dependencias

En la PC del usuario, desde PowerShell (como Administrador):

```powershell
# Crear carpeta para el cliente
mkdir C:\Outlook-Sync-Client
cd C:\Outlook-Sync-Client

# Crear virtual environment
python -m venv venv

# Activar virtual environment
.\venv\Scripts\Activate.ps1

# Instalar dependencias requeridas
pip install requests pywin32

# Registrar componentes COM de pywin32 (importante!)
python -m pywin32_postinstall -install
```

### Paso 3: Configurar el cliente

1. Copia `outlook_sync_config.json.example` como `outlook_sync_config.json`:

```powershell
Copy-Item outlook_sync_config.json.example outlook_sync_config.json
```

2. Edita `outlook_sync_config.json` con los datos:

```json
{
    "server_url": "http://IP_DEL_SERVIDOR:5000",
    "username": "tu_usuario_en_servidor",
    "password": "tu_contraseña",
    "limit": 10
}
```

**Ejemplo para red local:**
```json
{
    "server_url": "http://192.168.1.100:5000",
    "username": "juan",
    "password": "MiContraseña123!",
    "limit": 20
}
```

---

## Uso del Cliente

### Opción A: Sincronización manual (una sola vez)

```powershell
cd C:\Outlook-Sync-Client
.\venv\Scripts\Activate.ps1
python outlook_sync_agent.py
```

**Salida esperada:**
```
2024-03-20 10:15:30 - INFO - ============================================================
2024-03-20 10:15:30 - INFO - Iniciando sincronización de Outlook
2024-03-20 10:15:30 - INFO - ============================================================
2024-03-20 10:15:31 - INFO - Conectando a Outlook...
2024-03-20 10:15:32 - INFO - ✓ Outlook conectado (GetActiveObject)
2024-03-20 10:15:32 - INFO - Autenticando en http://192.168.1.100:5000/api/auth/login...
2024-03-20 10:15:33 - INFO - ✓ Autenticación exitosa. Token obtenido.
2024-03-20 10:15:33 - INFO - Obteniendo últimos 10 correos de Outlook...
2024-03-20 10:15:35 - INFO - ✓ 5 correos obtenidos de Outlook
2024-03-20 10:15:35 - INFO - Enviando 5 correos al servidor...
2024-03-20 10:15:36 - INFO - ✓ Sincronización exitosa: 5 correos sincronizados correctamente
```

### Opción B: Sincronización automática (daemon/servicio)

Sincroniza automáticamente cada 15 minutos:

```powershell
cd C:\Outlook-Sync-Client
.\venv\Scripts\Activate.ps1
python outlook_sync_agent.py --daemon --interval 15
```

**O con argumentos de línea de comandos:**

```powershell
python outlook_sync_agent.py `
  --server http://192.168.1.100:5000 `
  --username juan `
  --password MiContraseña123! `
  --limit 20 `
  --daemon `
  --interval 10
```

### Parámetros de línea de comandos

```
--server, -s      URL del servidor (requerido o en config)
--username, -u    Usuario del servidor (requerido o en config)
--password, -p    Contraseña (requerido o en config)
--limit, -l       Número máximo de correos (default: 10)
--daemon, -d      Ejecutar en modo daemon (sincronización continua)
--interval, -i    Intervalo en minutos para daemon (default: 15)

Ejemplos:
python outlook_sync_agent.py --server http://192.168.1.100:5000 --username juan --password pass123
python outlook_sync_agent.py --daemon --interval 5
python outlook_sync_agent.py -s http://192.168.1.100:5000 -u juan -p pass123 -l 50 -d -i 10
```

---

## Ejecutar como servicio de Windows (Opcional)

Para ejecutar automáticamente al iniciar Windows:

### Opción 1: NSSM (Non-Sucking Service Manager)

```powershell
# Descargar NSSM desde: https://nssm.cc/download
# O instalar con Chocolatey:
choco install nssm

# Luego registrar el servicio:
nssm install OutlookSyncAgent "C:\Outlook-Sync-Client\venv\Scripts\python.exe" "C:\Outlook-Sync-Client\outlook_sync_agent.py --daemon --interval 15"

# Iniciar servicio
net start OutlookSyncAgent

# Detener servicio
net stop OutlookSyncAgent

# Desinstalar servicio
nssm remove OutlookSyncAgent confirm
```

### Opción 2: Task Scheduler de Windows

1. Abre Task Scheduler (`taskschd.msc`)
2. Crea una nueva tarea
3. **Desencadenador**: "Al iniciar" o "Cada 15 minutos"
4. **Acción**: 
   - Programa: `C:\Outlook-Sync-Client\venv\Scripts\python.exe`
   - Argumentos: `C:\Outlook-Sync-Client\outlook_sync_agent.py --daemon --interval 15`
   - Iniciar en: `C:\Outlook-Sync-Client`
5. **Configuración**: Marcar "Ejecutar con permisos más altos"

---

## Monitoreo y Logs

El cliente registra todos los eventos en `outlook_sync_agent.log`:

```
tail -f outlook_sync_agent.log
```

**Errores comunes:**

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError: No module named 'pywin32'` | Ejecutar: `pip install pywin32` y `python -m pywin32_postinstall -install` |
| `GetActiveObject('Outlook.Application')` failed | Asegúrate que Outlook esté abierto o ejecutar con `--daemon` |
| `Error de autenticación: 401` | Verifica usuario/contraseña en `outlook_sync_config.json` |
| `Connection refused` | Verifica que el servidor está ejecutándose en `http://IP:5000` |

---

## Flujo de datos en detalle

### Lado del Cliente:

1. Se conecta a Outlook local via COM (pywin32)
2. Obtiene los últimos N correos de la carpeta "Enviados"
3. Extrae: Asunto, Remitente, Destinatarios, Fecha, Adjuntos, etc.
4. Se autentica contra el servidor (obtiene JWT token)
5. Envía los correos en JSON al endpoint `/api/emails/sync/remote`

### Lado del Servidor:

1. Recibe solicitud en `/api/emails/sync/remote`
2. Valida JWT token del usuario autenticado
3. Por cada correo recibido:
   - Verifica que no exista duplicado (por `email_id` único)
   - Lo crea en la base de datos
   - Lo asocia al usuario autenticado
   - Registra la acción en auditoría
4. Retorna conteo de correos creados/omitidos

---

## Preguntas frecuentes

**P: ¿Qué correos sincroniza?**
R: Los últimos N correos de la carpeta **"Enviados"** del Outlook local. El límite predeterminado es 10, configurable con `--limit`.

**P: ¿Se sincroniza solo una vez?**
R: Sin `--daemon` se sincroniza una sola vez. Con `--daemon --interval 15` se sincroniza cada 15 minutos indefinidamente.

**P: ¿Puedo sincronizar correos recibidos?**
R: Actualmente sincroniza solo "Enviados". Para incluir otras carpetas, edita la línea en `outlook_sync_agent.py`:
```python
sent_folder = namespace.GetDefaultFolder(5)  # 5 = olFolderSentMail
# Cambiar a:
# 6 = olFolderInbox (Bandeja de entrada)
# 7 = olFolderDeletedItems (Papelera)
```

**P: ¿Qué pasa si está abierto por 2 usuarios a la vez?**
R: Cada usuario accede a su propio Outlook local en su PC, luego se autentica en el servidor con su usuario individual. Los correos se asignan correctamente a cada usuario.

**P: ¿Necesito cambio en el servidor?**
R: No. El servidor ya tiene el endpoint `/api/emails/sync/remote` para recibir sincronizaciones remotas.

---

## Soporte técnico

Si hay problemas:

1. Revisa `outlook_sync_agent.log` en la PC del cliente
2. Revisa los logs del servidor Flask en la consola
3. Verifica conectividad: `ping IP_DEL_SERVIDOR`
4. Verifica que Outlook esté instalado y funcionando
