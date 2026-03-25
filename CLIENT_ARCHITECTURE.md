# Cliente Outlook Sync Agent - Arquitectura Opción 1

## 📋 Descripción General

**Cliente Outlook Sync Agent** es una solución **Opción 1** que permite que **cada usuario en la red local sincronice su propio Outlook** al servidor centralizado. A diferencia del modo Outlook de escritorio (que sincroniza el Outlook del servidor), este cliente sincroniza:

- ✅ El Outlook **del usuario en su PC**
- ✅ Los correos **de su propia cuenta**
- ✅ Mantiene **aislamiento de datos** por usuario

## 🏗️ Arquitectura de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                    Red Local (LAN)                          │
├─────────────────────────────────────────────────────────────┤

PC Usuario 1                    PC Usuario 2              Servidor
├─ Windows                      ├─ Windows               ├─ Windows/Linux
├─ Outlook 2019+                ├─ Outlook 2019+         ├─ Flask (Puerto 5000)
├─ outlook_sync_agent.py        ├─ outlook_sync_agent.py ├─ Base de datos SQLite
│                               │                        └─ Todos los correos + usuarios
│     ↓ (Sync cada 15 min)     │     ↓ (Sync cada 15 min)
│ [Obtiene correos locales]    │ [Obtiene correos locales]
│ [Se autentica con JWT]       │ [Se autentica con JWT]
│     ↓                         │     ↓
├─────────────────────────────────────────────────────────────┤
│  POST /api/emails/sync/remote                              │
├─────────────────────────────────────────────────────────────┤
                                  ↓
                    ┌─────────────────────────┐
                    │     Servidor Flask      │
                    ├─────────────────────────┤
                    │ ✓ Valida JWT token      │
                    │ ✓ Evita duplicados      │
                    │ ✓ Registra en auditoría │
                    │ ✓ Asigna a usuario      │
                    └─────────────────────────┘
                                  ↓
                         Cada usuario ve SOLO
                      sus propios correos en:
                    http://192.168.1.100:5000
```

## 📂 Estructura de Archivos

**En la carpeta principal del servidor** (`/Correos/`):

```
outlook_sync_agent.py              # Script cliente (copiar a PC del usuario)
outlook_sync_config.json.example    # Configuración template
CLIENT_INSTALLATION.md              # Documentación detallada
QUICK_START_CLIENT.md               # Guía rápida
run_sync_client.bat                 # Ejecutable para Windows
install_client.bat                  # Instalador automático
client_architecture.md              # Este archivo
```

**En la PC del usuario** (después de copiar):

```
C:/Outlook-Sync-Client/
├── outlook_sync_agent.py
├── outlook_sync_config.json        # Creado por install_client.bat
├── outlook_sync_agent.log          # Logs de ejecución
├── run_sync_client.bat
├── install_client.bat
└── venv/                           # Virtual environment (creado por install)
    ├── Scripts/
    │   ├── python.exe
    │   ├── pip.exe
    │   └── activate.bat
    └── Lib/
        └── site-packages/
            ├── requests/
            ├── pywin32/
            └── ...
```

## 🔄 Flujo de Sincronización

### 1. Autenticación del Cliente

```python
# El cliente envía credenciales del servidor
POST /api/auth/login
{
    "username": "juan",
    "password": "MiContraseña123!"
}

# Servidor retorna JWT token válido a este usuario
Response:
{
    "token": "eyJhbGc...",
    "user": {"id": 5, "username": "juan"}
}
```

### 2. Obtención de Correos Locales

```python
# El cliente accede al Outlook local via COM (pywin32)
outlook = win32com.client.GetActiveObject('Outlook.Application')
sent_folder = outlook.GetNamespace('MAPI').GetDefaultFolder(5)  # Enviados

# Por cada correo en Outlook:
{
    "outlook_id": "ABC123DEF456",          # ID única de Outlook
    "subject": "Reunión Urgente",
    "sender": "juan@empresa.com",
    "recipients": "[{\"name\":\"María\", \"email\":\"maria@empresa.com\"}]",
    "sent_date": "2024-03-20T10:15:00",
    "body_snippet": "Necesito que revises...",
    "has_attachments": true,
    "attachment_count": 1,
    "importance": "High",
    "outlook_class": "IPM.Note"
}
```

### 3. Envío al Servidor

```python
# El cliente agrupa los correos y los envía
POST /api/emails/sync/remote
Headers:
    Authorization: Bearer eyJhbGc...

Body:
{
    "emails": [
        { /* correo 1 */ },
        { /* correo 2 */ },
        ...
    ],
    "source": "outlook_agent",
    "client_hostname": "PC-JUAN-001"
}

# Servidor responde
Response 201 Created:
{
    "message": "5 correos sincronizados exitosamente",
    "created": 5,
    "skipped": 0,
    "errors": null
}
```

### 4. Procesamiento en el Servidor

```python
# app/routes/emails.py - POST /api/emails/sync/remote

1. Valida JWT token → Obtiene user_id del usuario autenticado
2. Por cada correo recibido:
   a. Verifica que no exista (por email_id único + user_id)
   b. Si no existe: CREATE nuevo Email registro
   c. Asigna a user_id del usuario autenticado ← IMPORTANTE
   d. Registra en auditoría con hostname del cliente
   e. COMMIT en base de datos
3. Retorna cuántos creados vs omitidos
```

## 🔐 Seguridad

### Aislamiento de Datos
- **JWT Token**: Solo usuarios autenticados pueden sincronizar
- **user_id**: Cada correo está vinculado al usuario que lo sincronizó
- **Auditoría**: Se registra qué cliente envió cada correo

### Validaciones
- Rechazo de solicitudes sin token válido
- Verificación de duplicados (usa `email_id` como clave única)
- Validación de datos obligatorios (subject, sender, etc)

### COM Security
- pywin32 se conecta solo a Outlook LOCAL
- No expone credenciales entre cliente-servidor
- JWT token se usa para autenticación en servidor

## 🛠️ Instalación Cliente

### Opción A: Instalador Automático (Recomendado)

```powershell
# En PowerShell como Administrador
cd C:\Outlook-Sync-Client

# Ejecutar instalador
.\install_client.bat

# Editar configuración
notepad outlook_sync_config.json
```

### Opción B: Instalación Manual

```powershell
# Crear carpeta y venv
mkdir C:\Outlook-Sync-Client
cd C:\Outlook-Sync-Client
python -m venv venv

# Activar venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install requests pywin32
python -m pywin32_postinstall -install

# Crear config
copy outlook_sync_config.json.example outlook_sync_config.json
```

## ▶️ Ejecución

### Modo Manual (Una sola vez)

```powershell
.\venv\Scripts\Activate.ps1
python outlook_sync_agent.py
```

**Salida:**
```
2024-03-20 10:15:30 - INFO - Iniciando sincronización de Outlook
2024-03-20 10:15:32 - INFO - ✓ Outlook conectado
2024-03-20 10:15:33 - INFO - ✓ Autenticación exitosa
2024-03-20 10:15:35 - INFO - ✓ 5 correos obtenidos de Outlook
2024-03-20 10:15:36 - INFO - ✓ Sincronización exitosa
```

### Modo Daemon (Automático cada 15 minutos)

```powershell
python outlook_sync_agent.py --daemon --interval 15
```

## 📊 Comparativa: Métodos de Sincronización

| Aspecto | Outlook de Servidor | Cliente Agent (Opción 1) |
|---------|-------------------|----------------------------|
| **Qué sincroniza** | Correos DEL SERVIDOR | Correos DEL USUARIO |
| **Multi-usuario** | ❌ No | ✅ Sí |
| **Aislamiento** | ❌ Todos ven igual | ✅ Cada uno ve sus correos |
| **Instalación cliente** | ❌ No necesaria | ✅ Necesaria (5 min) |
| **Outlook en servidor** | ✅ Obligatorio | ❌ Solo en cliente |
| **Red local** | ✅ Compatible | ✅ Compatible |
| **Escalabilidad** | ⭐ Baja (1 persona) | ⭐⭐⭐⭐⭐ Alta (N usuarios) |
| **Complejidad** | Baja | Media |

## 🐛 Troubleshooting

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Outlook no encontrado | `GetActiveObject failed` | Abre Outlook en la PC del usuario |
| Autenticación fallida | `Error 401: Unauthorized` | Verifica usuario/contraseña en config |
| No sincroniza | Ejecuta pero no crea correos | Verifica que los correos exisen en Outlook Enviados |
| Pywin32 error | `ModuleNotFoundError` | `python -m pywin32_postinstall -install` |
| Firewall bloquea | `Connection refused` | Abre puerto 5000 en firewall del servidor |

## 📈 Monitoreo

### Logs

El archivo `outlook_sync_agent.log` en la PC del usuario contiene:

```log
2024-03-20 10:15:30 - INFO - Conectando a Outlook...
2024-03-20 10:15:32 - INFO - ✓ Outlook conectado (GetActiveObject)
2024-03-20 10:15:33 - INFO - Autenticando en http://192.168.1.100:5000/api/auth/login...
2024-03-20 10:15:33 - INFO - ✓ Autenticación exitosa. Token obtenido.
2024-03-20 10:15:35 - INFO - Obteniendo últimos 10 correos de Outlook...
2024-03-20 10:15:36 - INFO - ✓ 5 correos obtenidos de Outlook
2024-03-20 10:15:36 - INFO - Enviando 5 correos al servidor...
2024-03-20 10:15:37 - INFO - ✓ Sincronización exitosa: 5 correos sincronizados correctamente
```

### Dashboard (Servidor)

En `http://192.168.1.100:5000/#/admin`:
- Ver quién sincronizó qué correos
- Ver hostname del cliente origen
- Ver timestamp de cada sincronización
- Ver logs de auditoría completos

## 🎯 Casos de Uso

### ✅ Recomendado para:
- Equipo de ventas sincronizando correos de clientes
- Departamento administrativo centralizando documentación
- Supervisores monitoreando actividad de equipo
- Auditoría y compliance
- Multi-usuario en red local

### ❌ No recomendado para:
- Usuario único (usar Outlook normal)
- Sincronizar TO do el historial (configurable con `limit`)
- Usuarios fuera de la red (ver Microsoft Graph API)

## 🔗 Enlaces Relacionados

- [CLIENT_INSTALLATION.md](CLIENT_INSTALLATION.md) - Documentación completa
- [QUICK_START_CLIENT.md](QUICK_START_CLIENT.md) - Guía rápida
- [app/routes/emails.py](app/routes/emails.py) - Endpoint `/api/emails/sync/remote`
