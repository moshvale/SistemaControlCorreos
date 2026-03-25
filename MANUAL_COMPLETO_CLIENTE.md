# Manual Completo: Configuración del Cliente Outlook Sync en Red Local

**Versión**: 1.0  
**Fecha**: Marzo 2026  
**Objetivo**: Sincronizar correos de Outlook de equipos locales a servidor centralizado

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura General](#arquitectura-general)
3. [Descarga de Archivos](#descarga-de-archivos)
4. [Instalación Paso a Paso](#instalación-paso-a-paso)
5. [Configuración del Cliente](#configuración-del-cliente)
6. [Métodos de Ejecución](#métodos-de-ejecución)
7. [Instalación como Servicio Windows](#instalación-como-servicio-windows)
8. [Monitoreo y Logs](#monitoreo-y-logs)
9. [Troubleshooting](#troubleshooting)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Requisitos Previos

### En cada equipo cliente:

- ✅ **Sistema Operativo**: Windows 10/11/Server 2019+
- ✅ **Microsoft Outlook**: 2016, 2019, Office 365 o versiones posteriores (INSTALADO y FUNCIONANDO)
- ✅ **Python**: 3.8 o superior
  - Verificar: `python --version`
  - Si no lo tiene: Descargar desde https://www.python.org/downloads/
- ✅ **Acceso a la Red**: Conectado a la misma red del servidor
- ✅ **Permisos**: Acceso de administrador para instalar servicios (opcional)

### En el servidor:

- ✅ **Servidor Outlook Sync**: Ejecutándose en `http://IP_SERVIDOR:5000`
- ✅ **Usuario y contraseña**: Credenciales válidas en el servidor
- ✅ **Conectividad**: Acceso de red desde clientes al servidor

### Información requerida:

Recopilar esta información ANTES de comenzar:

```
Servidor:
  - IP o nombre: __________________ (ej: 192.168.1.100 o correos.empresa.local)
  - Puerto: 5000
  - URL completa: http://________________:5000

Usuario:
  - Username: __________________ (tu usuario en el servidor)
  - Contraseña: __________________ (tu contraseña)

Cliente:
  - Nombre del equipo: __________________ (Windows + R → wmic computersystem get name)
  - Ubicación: __________________
```

---

## Arquitectura General

### Flujo de Sincronización

```
┌─────────────────────────────────────────────┐
│  Equipo Local del Usuario                   │
├─────────────────────────────────────────────┤
│                                              │
│  Microsoft Outlook instalado                │
│  └─> Carpeta "Enviados"                     │
│      └─> 10-50 correos recientes            │
│                                              │
│  outlook_sync_agent.py                      │
│  └─> Se ejecuta diariamente/automáticamente │
│      └─> Obtiene correos de Outlook         │
│          └─> Se autentica en servidor       │
│              └─> Envía correos al servidor  │
│                                              │
└─────────────────────────────────────────────┘
                    │
                    │ (HTTP + JWT Token)
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  Servidor Centralizado                      │
├─────────────────────────────────────────────┤
│                                              │
│  Flask API (Puerto 5000)                    │
│  ├─ /api/auth/login                         │
│  ├─ /api/emails/sync/remote                 │
│  └─ /api/emails (Dashboard)                 │
│                                              │
│  Base de Datos SQLite                       │
│  ├─ Todos los correos                       │
│  ├─ Usuarios                                │
│  └─ Auditoría                               │
│                                              │
└─────────────────────────────────────────────┘
```

### Flujo de Autenticación

```
Cliente                              Servidor
  │                                    │
  ├─ POST /api/auth/login              │
  │  { username, password }            │
  ├───────────────────────────────────>│
  │                                    │
  │                              Valida credenciales
  │                                    │
  │<─────────────────────────────────┤
  │  { access_token, refresh_token }   │
  │                                    │
  ├─ POST /api/emails/sync/remote      │
  │  { Authorization: Bearer TOKEN }   │
  ├───────────────────────────────────>│
  │                                    │
  │                        Valida token y recibe correos
  │                                    │
  │<─────────────────────────────────┤
  │  { created: 10, skipped: 0 }       │
  │                                    │
```

---

## Descarga de Archivos

### Opción 1: Desde el Servidor (mediante USB, Email o Compartido)

El administrador debe proporcionar estos archivos:

```
📂 Outlook-Sync-Client-Setup/
  ├─ outlook_sync_agent.py           (Script principal - 12 KB)
  ├─ outlook_sync_config.json.example (Configuración - 0.3 KB)
  ├─ install_client.bat               (Instalador - 2 KB)
  ├─ run_sync_client.bat              (Ejecutable - 1 KB)
  └─ CLIENT_INSTALLATION.md           (Guía - 10 KB)
```

### Opción 2: Copiar de un Equipo Configurado

Si otro usuario ya lo tiene instalado:

```powershell
# En equipo que ya está configurado:
Copy-Item -Path C:\Outlook-Sync-Client\outlook_sync_agent.py -Destination \\tu-pc\C$\Outlook-Sync-Client\
Copy-Item -Path C:\Outlook-Sync-Client\outlook_sync_config.json.example -Destination \\tu-pc\C$\Outlook-Sync-Client\
```

---

## Instalación Paso a Paso

### PASO 1: Crear Carpeta de Instalación

**En tu PC:**

1. Presiona **Windows + E** (abre Explorador)
2. Ve a **C:\** (unidad principal)
3. Clic derecho → **Nuevo** → **Carpeta**
4. Nombre: `Outlook-Sync-Client`

**Resultado:** `C:\Outlook-Sync-Client\`

---

### PASO 2: Copiar Archivos de Instalación

1. Obtén los archivos del administrador (USB, email, o carpeta compartida)
2. Copia estos 4 archivos en `C:\Outlook-Sync-Client\`:
   - `outlook_sync_agent.py`
   - `outlook_sync_config.json.example`
   - `install_client.bat`
   - `run_sync_client.bat`

**Verificar:** Abre Explorador y confirma que todos están en `C:\Outlook-Sync-Client\`

---

### PASO 3: Ejecutar Instalador

1. **Abre PowerShell como Administrador**:
   - Presiona **Windows**
   - Escribe: `powershell`
   - Clic derecho en PowerShell → **Ejecutar como administrador**
   - Presiona **Sí** si te pide confirmación

2. **Navega a la carpeta**:
   ```powershell
   cd C:\Outlook-Sync-Client
   ```

3. **Ejecuta el instalador**:
   ```powershell
   .\install_client.bat
   ```

**Qué hace el instalador:**

```
[1/4] Creando virtual environment...
      ✓ Crea aislamiento de Python
      
[2/4] Instalando dependencias...
      ✓ Instala 'requests' (para conectar al servidor)
      ✓ Instala 'pywin32' (para acceder a Outlook)
      
[3/4] Registrando componentes pywin32...
      ✓ Habilita acceso COM a Outlook
      
[4/4] Creando archivo de configuración...
      ✓ Crea archivo outlook_sync_config.json
```

**Espera a que termine (2-5 minutos)**

---

### PASO 4: Verificar Instalación

Después de que termine el instalador, verifica que existan:

```
C:\Outlook-Sync-Client\
├─ venv\                    (NUEVA - carpeta de entorno)
├─ outlook_sync_agent.py
├─ outlook_sync_config.json.example
├─ outlook_sync_config.json (NUEVA - se creó)
├─ install_client.bat
└─ run_sync_client.bat
```

**Si ves error sobre pywin32_postinstall:**

Abre PowerShell como Administrador y ejecuta:

```powershell
cd C:\Outlook-Sync-Client
.\venv\Scripts\Activate.ps1
python -m pywin32_postinstall -install
```

---

## Configuración del Cliente

### PASO 5: Editar el Archivo de Configuración

1. **Abre el archivo de configuración**:
   ```powershell
   cd C:\Outlook-Sync-Client
   notepad outlook_sync_config.json
   ```

2. **Verás algo como esto**:
   ```json
   {
       "server_url": "http://192.168.1.100:5000",
       "username": "tu_usuario_en_servidor",
       "password": "tu_contraseña",
       "limit": 10
   }
   ```

3. **Reemplaza los valores**:

   **server_url**: URL del servidor
   ```json
   "server_url": "http://192.168.1.100:5000"
   ```
   - Reemplaza `192.168.1.100` con la IP/nombre de tu servidor
   - Si no sabes, pregunta al administrador
   - Ejemplo si el servidor es local: `http://localhost:5000`

   **username**: Tu usuario en el servidor
   ```json
   "username": "armando.valeriano"
   ```
   - Usa el mismo usuario que usas para iniciar sesión en el dashboard web

   **password**: Tu contraseña
   ```json
   "password": "miContraseña123!"
   ```
   - La misma contraseña que usas en el dashboard web
   - ⚠️ SEGURIDAD: No compartas este archivo

   **limit**: Cantidad de correos a sincronizar
   ```json
   "limit": 10
   ```
   - Valores comunes: 5-50
   - Menos = más rápido, Más = carga más histórico

4. **Ejemplo completo**:
   ```json
   {
       "server_url": "http://192.168.1.100:5000",
       "username": "armando.valeriano",
       "password": "MiPassword123!",
       "limit": 20
   }
   ```

5. **Guarda el archivo**:
   - Presiona **Ctrl + S**
   - Cierra Notepad

---

## Métodos de Ejecución

### MÉTODO A: Sincronización Manual (Una sola vez)

**Uso**: Para probar que funciona, o cuando quieras sincronizar manualmente

1. **Desde Explorador** (más fácil):
   - Abre `C:\Outlook-Sync-Client\`
   - Haz doble clic en `run_sync_client.bat`
   - Se abrirá una ventana que mostrará el progreso

2. **Desde PowerShell**:
   ```powershell
   cd C:\Outlook-Sync-Client
   .\run_sync_client.bat
   ```

**Salida esperada**:
```
============================================================
Iniciando sincronización de Outlook
============================================================
Conectando a Outlook...
✓ Outlook conectado (GetActiveObject)
Autenticando en http://192.168.1.100:5000/api/auth/login...
✓ Autenticación exitosa. Token obtenido.
Obteniendo últimos 20 correos de Outlook...
✓ 15 correos obtenidos de Outlook
Enviando 15 correos al servidor...
✓ Sincronización exitosa: 15 correos sincronizados correctamente

Presiona una tecla para continuar...
```

---

### MÉTODO B: Sincronización Automática (Cada X minutos)

**Uso**: Para sincronización continua sin intervención

1. **Abre PowerShell como Administrador**:
   ```powershell
   cd C:\Outlook-Sync-Client
   ```

2. **Activa el entorno Python**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Ejecuta en modo daemon** (cada 15 minutos):
   ```powershell
   python outlook_sync_agent.py --daemon --interval 15
   ```

   **O con intervalo diferente** (cada 5 minutos):
   ```powershell
   python outlook_sync_agent.py --daemon --interval 5
   ```

   **O con intervalo de 30 minutos** (menos tráfico de red):
   ```powershell
   python outlook_sync_agent.py --daemon --interval 30
   ```

4. **Salida esperada**:
   ```
   2026-03-20 10:15:30 - INFO - ============================================================
   2026-03-20 10:15:30 - INFO - Iniciando daemon - Sincronización cada 15 minutos
   2026-03-20 10:15:30 - INFO - ============================================================
   2026-03-20 10:15:32 - INFO - ✓ Outlook conectado
   2026-03-20 10:15:33 - INFO - ✓ Autenticación exitosa
   2026-03-20 10:15:35 - INFO - ✓ 10 correos sincronizados correctamente
   2026-03-20 10:15:35 - INFO - Próxima sincronización en 15 minutos...
   ```

5. **Para detener**:
   - Presiona **Ctrl + C** en la ventana de PowerShell

---

### MÉTODO C: Sincronización Programada con Windows Task Scheduler

**Uso**: Ejecutar automáticamente en horarios específicos

1. **Abre Task Scheduler**:
   - Presiona **Windows + R**
   - Escribe: `taskschd.msc`
   - Presiona Enter

2. **Crear nueva tarea**:
   - Panel derecho → **Create Basic Task...**
   - Nombre: `Outlook Sync Agent`
   - Descripción: `Sincroniza Outlook cada mañana`
   - Presiona **Next**

3. **Configurar disparador**:
   - Selecciona: **Daily** (diario)
   - Hora: `08:00:00` (a las 8 AM, por ejemplo)
   - Presiona **Next**

4. **Configurar acción**:
   - Selecciona: **Start a program**
   - Program: `C:\Outlook-Sync-Client\venv\Scripts\python.exe`
   - Arguments: `C:\Outlook-Sync-Client\outlook_sync_agent.py`
   - Start in: `C:\Outlook-Sync-Client`
   - Presiona **Next**

5. **Resumen**:
   - Revisa la configuración
   - Marca: **Open the Properties dialog when I click Finish**
   - Presiona **Finish**

6. **En las propiedades**:
   - Pestaña **General**:
     - Marca: **Run with highest privileges**
   - Pestaña **Conditions**:
     - Desmarca: **Start the task only if the computer is on AC power**
   - Presiona **OK**

7. **Verificar**:
   - En Task Scheduler, busca **Outlook Sync Agent**
   - Clic derecho → **Run** para probar
   - Verifica que se ejecute correctamente

---

## Instalación como Servicio Windows

**Uso**: Ejecutar automáticamente al iniciar Windows, sin intervención de usuario

### Prerequisito: NSSM (Non-Sucking Service Manager)

1. **Descargar NSSM**:
   - Ve a: https://nssm.cc/download
   - Descarga la versión más reciente (nssm-X.XX-win64.zip)
   - Extrae en: `C:\Program Files\nssm\`

   **O instalar con Chocolatey** (si lo tienes):
   ```powershell
   choco install nssm
   ```

### Crear el Servicio

1. **Abre PowerShell como Administrador**:
   ```powershell
   cd "C:\Program Files\nssm\win64"
   ```

2. **Instala el servicio**:
   ```powershell
   .\nssm install OutlookSyncAgent "C:\Outlook-Sync-Client\venv\Scripts\python.exe" "C:\Outlook-Sync-Client\outlook_sync_agent.py --daemon --interval 15"
   ```

3. **Configura usuario que ejecuta servicio**:
   ```powershell
   .\nssm set OutlookSyncAgent AppDirectory "C:\Outlook-Sync-Client"
   ```

4. **Inicia el servicio**:
   ```powershell
   net start OutlookSyncAgent
   ```

5. **Verifica que está ejecutándose**:
   - Presiona **Windows + R**
   - Escribe: `services.msc`
   - Busca **OutlookSyncAgent** en la lista
   - Estado debe ser **Running**

### Comandos útiles para el Servicio

```powershell
# Ver estado
net start | findstr OutlookSyncAgent

# Detener
net stop OutlookSyncAgent

# Reiniciar
net stop OutlookSyncAgent
net start OutlookSyncAgent

# Desinstalar (si quieres quitarlo)
nssm remove OutlookSyncAgent confirm
```

---

## Monitoreo y Logs

### Ver Logs en Tiempo Real

Los logs se guardan en: `C:\Outlook-Sync-Client\outlook_sync_agent.log`

1. **En Notepad** (actualización manual):
   ```powershell
   notepad C:\Outlook-Sync-Client\outlook_sync_agent.log
   ```

2. **En PowerShell** (actualización en tiempo real):
   ```powershell
   Get-Content C:\Outlook-Sync-Client\outlook_sync_agent.log -Wait
   ```

3. **Ver últimas 20 líneas**:
   ```powershell
   Get-Content C:\Outlook-Sync-Client\outlook_sync_agent.log -Tail 20
   ```

4. **Ver logs filtrados**:
   ```powershell
   # Solo errores
   Select-String "ERROR" C:\Outlook-Sync-Client\outlook_sync_agent.log
   
   # Solo sincronizaciones exitosas
   Select-String "exitosa" C:\Outlook-Sync-Client\outlook_sync_agent.log
   ```

### Ejemplo de Logs Correctos

```
2026-03-20 08:00:15,342 - INFO - ============================================================
2026-03-20 08:00:15,342 - INFO - Iniciando sincronización de Outlook
2026-03-20 08:00:15,342 - INFO - ============================================================
2026-03-20 08:00:15,342 - INFO - Conectando a Outlook...
2026-03-20 08:00:15,701 - INFO - ✓ Outlook conectado (GetActiveObject)
2026-03-20 08:00:15,702 - INFO - Autenticando en http://192.168.1.100:5000/api/auth/login...
2026-03-20 08:00:17,977 - INFO - ✓ Autenticación exitosa. Token obtenido.
2026-03-20 08:00:17,978 - INFO - Obteniendo últimos 20 correos de Outlook...
2026-03-20 08:00:39,116 - INFO - ✓ 15 correos obtenidos de Outlook
2026-03-20 08:00:39,118 - INFO - Enviando 15 correos al servidor...
2026-03-20 08:00:41,155 - INFO - ✓ 15 correos creados, 0 omitidos
2026-03-20 08:00:41,158 - INFO - Desconectado de Outlook
```

### Verificar Sincronización en el Dashboard

Después de sincronizar, puedes ver los correos en:

1. Abre navegador
2. Ve a: `http://192.168.1.100:5000` (reemplaza con IP de tu servidor)
3. Inicia sesión con tu usuario
4. Deberías ver los correos sincronizados en el dashboard

---

## Troubleshooting

### PROBLEMA 1: "ModuleNotFoundError: No module named 'pywin32'"

**Síntoma**:
```
ModuleNotFoundError: No module named 'pywin32'
```

**Solución**:
```powershell
cd C:\Outlook-Sync-Client
.\venv\Scripts\Activate.ps1
pip install pywin32
python -m pywin32_postinstall -install
```

---

### PROBLEMA 2: "Error conectando a Outlook"

**Síntoma**:
```
Error conectando a Outlook: GetActiveObject('Outlook.Application') failed
```

**Causas posibles**:
- Outlook NO está abierto
- Outlook se cerró inesperadamente

**Solución**:
1. Abre Microsoft Outlook manualmente
2. Déjalo abierto mientras se sincroniza
3. Intenta nuevamente

---

### PROBLEMA 3: "Error de autenticación: 401"

**Síntoma**:
```
Error de autenticación: 401 - Usuario o contraseña incorrectos
```

**Causas posibles**:
- Usuario incorrecto en `outlook_sync_config.json`
- Contraseña incorrecta
- El usuario no existe en el servidor

**Solución**:
1. Verifica tu usuario/contraseña en el dashboard del servidor
2. Edita `outlook_sync_config.json` con los datos correctos
3. Intenta nuevamente

**Comando para editar**:
```powershell
notepad C:\Outlook-Sync-Client\outlook_sync_config.json
```

---

### PROBLEMA 4: "Connection refused" o "No se puede conectar al servidor"

**Síntoma**:
```
Error enviando correos: Connection refused
```

**Causas posibles**:
- IP del servidor incorrecta
- Servidor no está en línea
- Firewall bloquea la conexión
- Puerto 5000 no es accesible

**Solución**:

1. **Verifica la IP del servidor**:
   ```powershell
   ping 192.168.1.100  # Reemplaza con IP del servidor
   ```
   - Si dice "unreachable" → El servidor está apagado o IP es incorrecta
   - Si funciona → Continúa

2. **Prueba conectividad al puerto 5000**:
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.100 -Port 5000
   ```
   - Debe decir "TcpTestSucceeded: True"
   - Si falla → El servidor no está ejecutando en ese puerto

3. **Verifica el archivo de configuración**:
   ```powershell
   notepad C:\Outlook-Sync-Client\outlook_sync_config.json
   ```
   - Asegúrate que `server_url` es correcto
   - No debe tener espacios en blanco extras

4. **Reinicia el servidor**:
   - Avisa al administrador para reiniciar el servidor Flask
   - Espera 30 segundos
   - Intenta nuevamente

---

### PROBLEMA 5: "Sin correos para sincronizar" (después de primera sincronización)

**Síntoma**:
```
Sin correos nuevos para sincronizar
```

**Causa**:
- Los mismos correos ya fueron sincronizados anteriormente
- No hay correos "nuevos" en Outlook desde la última sincronización

**Solución**:
- Esto es NORMAL después de la primera sincronización
- Solo se sincronizan correos nuevos
- Cada vez que envíes un correo nuevo en Outlook, se sincronizará automáticamente

---

### PROBLEMA 6: "Operación no disponible" (Outlook error)

**Síntoma**:
```
com_error: (-2147221021, 'Operación no disponible', None, None)
```

**Causa**:
- Outlook está cerrado

**Solución**:
```powershell
# Abre Outlook manualmente
# Espera a que esté completamente cargado
# Intenta sincronizar nuevamente
```

---

### PROBLEMA 7: Sincronización lenta (tarda más de 1 minuto)

**Causa posible**:
- Red lenta
- Demasiados correos siendo procesados
- Servidor sobrecargado

**Solución**:
1. Reduce el límite de correos:
   ```json
   "limit": 5
   ```

2. Aumenta el intervalo de sincronización:
   ```powershell
   python outlook_sync_agent.py --daemon --interval 30
   ```

---

## Preguntas Frecuentes

### P1: ¿Necesito Outlook abierto todo el tiempo?

**R**: 
- **Para sincronización manual**: Outlook debe estar abierto
- **Para sincronización automática daemon**: Outlook debe estar abierto
- **Para Task Scheduler**: Outlook debe estar abierto al momento de la sincronización

**Recomendación**: Ten Outlook abierto durante tu horario de trabajo

---

### P2: ¿Puedo sincronizar correos de otras carpetas (no solo "Enviados")?

**R**: Por defecto sincroniza la carpeta "Enviados". 

Para cambiar, edita `outlook_sync_agent.py` en línea ~135:

```python
sent_folder = namespace.GetDefaultFolder(5)  # 5 = olFolderSentMail

# Cambiar a:
# 3 = olFolderDeletedItems (Papelera)
# 6 = olFolderInbox (Bandeja de entrada)
# 7 = olFolderJunk (Correo no deseado)
```

Guarda el archivo y reinicia la sincronización.

---

### P3: ¿Qué información se sincroniza?

**R**: Se sincroniza:
- ✓ Asunto
- ✓ Remitente
- ✓ Destinatarios
- ✓ Fecha de envío
- ✓ Primeras 500 caracteres del cuerpo
- ✓ Indicador de adjuntos (sí/no) y cantidad
- ✓ Importancia (Baja, Normal, Alta)

**NO se sincroniza**:
- ✗ Cuerpo completo del correo
- ✗ Archivos adjuntos (solo se registra que existen)
- ✗ Etiquetas o categorías personalizadas

---

### P4: ¿Cuánto espacio usa la sincronización?

**R**:
- Cada correo usa ~2-5 KB en la base de datos
- 100 correos = ~400 KB
- 1000 correos = ~4 MB

Prácticamente nada en comparación con cualquier PC moderna.

---

### P5: ¿Qué pasa si interrumpo la sincronización?

**R**:
- Los correos que YA se enviaron, quedan guardados
- Los correos que NO se enviaron, se intentarán en la próxima sincronización
- Sin riesgo de pérdida de datos

---

### P6: ¿Puedo usar la misma configuración en varias PCs?

**R**: 
- **SI**: La configuración es igual en todos los equipos, si:
  - Todos usan el mismo usuario y contraseña
  - Todos apuntan al mismo servidor
- **NO**: Si cada usuario tiene su propia cuenta, debe ser su propia configuración

---

### P7: ¿Cómo cambio la contraseña?

**R**:
1. Cambia tu contraseña en el servidor (Dashboard)
2. Edita `outlook_sync_config.json`:
   ```powershell
   notepad C:\Outlook-Sync-Client\outlook_sync_config.json
   ```
3. Actualiza la contraseña:
   ```json
   "password": "nueva_contraseña"
   ```
4. Guarda y cierra
5. Intenta sincronizar nuevamente

---

### P8: ¿Se ven mis correos en otras PCs?

**R**:
- **Si sincronizas con el mismo usuario**: Sí, verás todos los correos de ese usuario
- **Si sincronizas con tu usuario único**: Solo tú ves tus correos
- Cada usuario ve SOLO sus propios correos sincronizados

---

### P9: ¿Qué pasa si el servidor está apagado?

**R**:
- La sincronización fallará
- Se registrará en los logs
- Se reintentará automáticamente en la próxima sincronización programada
- **Sin riesgo**: Los correos quedan en Outlook, se sincronizan cuando el servidor esté disponible

---

### P10: ¿Cómo elimino la sincronización?

**R**:
```powershell
# Si es un servicio:
net stop OutlookSyncAgent
nssm remove OutlookSyncAgent confirm

# Luego puedes eliminar la carpeta:
Remove-Item -Path C:\Outlook-Sync-Client -Recurse
```

---

## Soporte Técnico

### Contactar al Administrador

Cuando reportes un problema, incluye:

1. **Archivo de log**:
   ```powershell
   Copy-Item C:\Outlook-Sync-Client\outlook_sync_agent.log -Destination C:\log_para_enviar.log
   ```

2. **Información del equipo**:
   ```powershell
   # Copia estos datos:
   wmic computersystem get name                    # Nombre equipo
   systeminfo | findstr /B /C:"OS Name"           # Sistema operativo
   python --version                               # Versión Python
   Get-Content C:\Outlook-Sync-Client\outlook_sync_config.json | findstr server_url  # URL servidor
   ```

3. **Screenshot del error**:
   - Presiona **Windows + Shift + S** para captura
   - Adjunta al reporte

4. **Descripción del problema**:
   - Qué estabas haciendo
   - Cuándo ocurrió
   - Qué mensaje de error viste
   - Qué pasos tomaste para resolver

---

## Resumen de Comandos Importantes

```powershell
# ========== INSTALACIÓN ==========
cd C:\Outlook-Sync-Client
.\install_client.bat

# ========== EJECUCIÓN MANUAL ==========
.\run_sync_client.bat

# ========== EJECUCIÓN AUTOMÁTICA (DAEMON) ==========
.\venv\Scripts\Activate.ps1
python outlook_sync_agent.py --daemon --interval 15

# ========== CONFIGURACIÓN ==========
notepad outlook_sync_config.json

# ========== LOGS ==========
Get-Content outlook_sync_agent.log -Wait        # En tiempo real
Get-Content outlook_sync_agent.log -Tail 20     # Últimas 20 líneas
Select-String "ERROR" outlook_sync_agent.log    # Solo errores

# ========== SERVICIO ==========
net start OutlookSyncAgent                      # Iniciar
net stop OutlookSyncAgent                       # Detener
net start | findstr OutlookSyncAgent            # Ver estado

# ========== DIAGNÓSTICO ==========
ping 192.168.1.100                              # Ping al servidor
Test-NetConnection -ComputerName 192.168.1.100 -Port 5000  # Conectividad
```

---

## Checklist de Instalación Completa

Marca cada paso conforme lo completes:

```
□ Python 3.8+ instalado
□ Outlook instalado y funcionando
□ Carpeta C:\Outlook-Sync-Client\ creada
□ Archivos copiados en la carpeta
□ install_client.bat ejecutado
□ outlook_sync_config.json editado correctamente
□ Prueba manual: .\run_sync_client.bat ejecutada
□ Resultados mostrados en el dashboard
□ Logs verificados (outlook_sync_agent.log)
□ Método de ejecución elegido (manual/daemon/servicio)
□ Sistema en producción y funcionando
```

---

## Información de Contacto del Administrador

```
Nombre del Administrador: _____________________
Correo: _____________________
Teléfono: _____________________
Horario de disponibilidad: _____________________
Servidor IP: _____________________
URL Dashboard: _____________________
```

---

**Fin del Manual**

Versión 1.0 | Marzo 2026 | Outlook Sync Client Setup
Para actualizaciones, contacta al administrador de TI
