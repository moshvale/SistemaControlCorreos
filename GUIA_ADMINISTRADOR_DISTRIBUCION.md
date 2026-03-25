# Guía para Administradores: Distribución del Cliente Outlook Sync

**Objetivo**: Guía para TI/Administradores que distribuirán el cliente Outlook Sync a usuarios finales en la red local.

---

## 📋 Tabla de Contenidos

1. [Preparación Inicial](#preparación-inicial)
2. [Empaquetamiento de Archivos](#empaquetamiento-de-archivos)
3. [Métodos de Distribución](#métodos-de-distribución)
4. [Distribución en Masa (Script)](#distribución-en-masa-script)
5. [Verificación de Instalación](#verificación-de-instalación)
6. [Soporte a Usuarios](#soporte-a-usuarios)
7. [Reporte de Problemas](#reporte-de-problemas)

---

## Preparación Inicial

### 1. Verificar que el Servidor está funcionando

```powershell
# Verificar que Flask está corriendo
curl http://localhost:5000/api/emails/debug/test

# Respuesta esperada:
# HTTP/1.1 200 OK
# {"message": "Debug endpoint funcionando", "status": "ok"}
```

### 2. Crear carpeta de distribución

```powershell
mkdir C:\Outlook-Sync-Distribution
cd C:\Outlook-Sync-Distribution
```

### 3. Copiar archivos necesarios

```powershell
# Desde la carpeta del servidor
Copy-Item -Path C:\Outlook-Sync-Client\outlook_sync_agent.py -Destination C:\Outlook-Sync-Distribution\
Copy-Item -Path C:\Outlook-Sync-Client\outlook_sync_config.json.example -Destination C:\Outlook-Sync-Distribution\
Copy-Item -Path C:\Outlook-Sync-Client\run_sync_client.bat -Destination C:\Outlook-Sync-Distribution\
Copy-Item -Path C:\Outlook-Sync-Client\install_client.bat -Destination C:\Outlook-Sync-Distribution\

# Copiar documentación
Copy-Item -Path C:\Outlook-Sync-Client\MANUAL_COMPLETO_CLIENTE.md -Destination C:\Outlook-Sync-Distribution\
Copy-Item -Path C:\Outlook-Sync-Client\QUICK_START_CLIENT.md -Destination C:\Outlook-Sync-Distribution\
```

---

## Empaquetamiento de Archivos

### Opción A: Crear ZIP para distribución

```powershell
# Instalar módulo de compresión si no lo tienes
Add-Type -AssemblyName System.IO.Compression.FileSystem

# Crear ZIP
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    'C:\Outlook-Sync-Distribution',
    'C:\Outlook-Sync-Distribution-v1.0.zip'
)

# Resultado:
# C:\Outlook-Sync-Distribution-v1.0.zip (listo para distribuir)
```

### Opción B: Crear en carpeta compartida de red

```powershell
# Crear carpeta compartida
mkdir \\servidor\compartido\Outlook-Sync-Client-Setup
icacls \\servidor\compartido\Outlook-Sync-Client-Setup /grant "Domain Users:F"

# Copiar archivos
Copy-Item C:\Outlook-Sync-Distribution\* -Destination \\servidor\compartido\Outlook-Sync-Client-Setup -Recurse
```

### Contenido del empaquete

```
📦 Outlook-Sync-Distribution/
├── 📄 outlook_sync_agent.py                 (Script principal)
├── 📄 outlook_sync_config.json.example      (Configuración template)
├── 📄 install_client.bat                    (Instalador)
├── 📄 run_sync_client.bat                   (Ejecutable)
├── 📄 MANUAL_COMPLETO_CLIENTE.md            (Documentación completa)
├── 📄 QUICK_START_CLIENT.md                 (Guía rápida)
└── 📄 README_DISTRIBUCION.txt               (instrucciones de distribución)
```

---

## Métodos de Distribución

### Método 1: Por Email

```
Asunto: Instalación Outlook Sync Client - Acción Requerida

Cuerpo:

Estimado usuario,

Se ha implementado un nuevo sistema de sincronización centralizada de correos Outlook.

ACCIÓN REQUERIDA:
1. Descargar el archivo: Outlook-Sync-Distribution-v1.0.zip (adjunto)
2. Extraer en: C:\Outlook-Sync-Client\
3. Seguir MANUAL_COMPLETO_CLIENTE.md para instalación

INFORMACIÓN DEL SERVIDOR:
- URL: http://[IP_SERVIDOR]:5000
- Usuario: [tu_usuario_en_servidor]
- Contraseña: [tu_contraseña]

SOPORTE:
- Manual: MANUAL_COMPLETO_CLIENTE.md
- Contacto: [email_admin]@empresa.com

Atentamente,
Administrador TI
```

### Método 2: Por Carpeta Compartida

1. **Crear carpeta en servidor**:
   ```powershell
   mkdir \\servidor\compartido\Software\Outlook-Sync-Setup
   ```

2. **Compartir y asignar permisos**:
   ```powershell
   net share "Outlook-Sync" ="\\servidor\compartido\Software\Outlook-Sync-Setup" /grant:"Domain Users",FULL
   ```

3. **Notificar a usuarios**:
   - Enviar correo con instrucción de copiar desde `\\servidor\compartido\Software\Outlook-Sync-Setup`

### Método 3: Por USB o Medios Físicos

1. **Crear estructura en USB**:
   ```
   E:\ (USB)
   └── Outlook-Sync-Setup/
       ├── outlook_sync_agent.py
       ├── outlook_sync_config.json.example
       ├── install_client.bat
       ├── run_sync_client.bat
       ├── MANUAL_COMPLETO_CLIENTE.md
       └── QUICK_START_CLIENT.md
   ```

2. **Distribuir físicamente** o permitir que usuarios copien

### Método 4: Script de Instalación Remota (Avanzado)

Para instalación en masa en múltiples PCs de la red:

```powershell
# Script: deploy_outlook_sync_to_users.ps1

param(
    [string[]]$ComputerNames = @(),
    [string]$SourcePath = "C:\Outlook-Sync-Distribution",
    [string]$TargetPath = "C:\Outlook-Sync-Client"
)

# Si no se especifican computadoras, obtener todas las de AD
if ($ComputerNames.Count -eq 0) {
    $ComputerNames = (Get-ADComputer -Filter * -SearchBase "OU=Usuarios,DC=empresa,DC=local").Name
}

foreach ($Computer in $ComputerNames) {
    Write-Host "Distribuyendo a: $Computer" -ForegroundColor Green
    
    try {
        # Crear carpeta remota
        $RemotePath = "\\$Computer\C$\Outlook-Sync-Client"
        if ((Test-Path $RemotePath) -eq $false) {
            New-Item -Path $RemotePath -ItemType Directory -Force | Out-Null
        }
        
        # Copiar archivos
        Copy-Item -Path "$SourcePath\*" -Destination $RemotePath -Recurse -Force
        
        # Ejecutar instalador remotamente
        Invoke-Command -ComputerName $Computer -ScriptBlock {
            cd C:\Outlook-Sync-Client
            .\install_client.bat
        }
        
        Write-Host "✓ $Computer - Instalación completada" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ $Computer - Error: $_" -ForegroundColor Red
    }
}

Write-Host "Distribución completada" -ForegroundColor Green
```

**Ejecutar**:
```powershell
.\deploy_outlook_sync_to_users.ps1 -ComputerNames @("PC-USER1", "PC-USER2", "PC-USER3")
```

---

## Verificación de Instalación

### Verificación Local en una PC

```powershell
# Verificar que la carpeta fue creada
Test-Path C:\Outlook-Sync-Client

# Verificar que los archivos están presentes
Get-ChildItem C:\Outlook-Sync-Client

# Verificar que Python está instalado
& "C:\Outlook-Sync-Client\venv\Scripts\python.exe" --version

# Verificar que las dependencias están instaladas
& "C:\Outlook-Sync-Client\venv\Scripts\python.exe" -c "import requests; import win32com.client; print('Dependencias OK')"

# Hacer prueba de sincronización
cd C:\Outlook-Sync-Client
.\run_sync_client.bat
```

### Verificación Remota (en la red)

```powershell
function Test-OutlookSyncSetup {
    param([string]$ComputerName)
    
    $RemotePath = "\\$ComputerName\C$\Outlook-Sync-Client"
    
    Write-Host "Verificando: $ComputerName"
    
    # Verificar carpeta
    if ((Test-Path $RemotePath)) {
        Write-Host "  ✓ Carpeta existe" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Carpeta NO existe" -ForegroundColor Red
        return $false
    }
    
    # Verificar archivos
    $RequiredFiles = @(
        "outlook_sync_agent.py",
        "outlook_sync_config.json.example",
        "install_client.bat",
        "run_sync_client.bat",
        "venv"
    )
    
    foreach ($File in $RequiredFiles) {
        if ((Test-Path "$RemotePath\$File")) {
            Write-Host "  ✓ $File presente" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $File NO encontrado" -ForegroundColor Red
        }
    }
    
    return $true
}

# Ejecutar verificación
Test-OutlookSyncSetup -ComputerName "PC-USER1"
```

---

## Soporte a Usuarios

### Crear Sistema de Tickets

Preparar un canal de soporte:

```
Nombre: Outlook Sync Client Support
Email: outlook-sync-support@empresa.com
Canal Teams: #outlook-sync-support
Horario: 8:00 AM - 5:00 PM

Proceso:
1. Usuario reporta problema
2. Admin pide logs y detalles
3. Admin revisa archivos en: \\computadora\C$\Outlook-Sync-Client\outlook_sync_agent.log
4. Admin proporciona solución
```

### Crear FAQ Interna

Documento para usuarios frecuentes:

```
P: ¿Dónde están los archivos de cliente?
R: En C:\Outlook-Sync-Client\

P: ¿Cómo veo si está sincronizando?
R: Abre C:\Outlook-Sync-Client\outlook_sync_agent.log

P: ¿Qué pasa si Outlook está cerrado?
R: La sincronización fallará. Abre Outlook antes de sincronizar.

P: ¿Cuánto tarda en sincronizar?
R: 30 segundos a 2 minutos dependiendo de cantidad de correos.
```

### Template de Email para Soporte

```
Asunto: Re: Problema Outlook Sync - Necesito más información

Estimado usuario,

Para ayudarte con el problema, necesito que me proporciones:

1. Tu nombre de usuario y PC:
   [ ] Completado

2. El mensaje de error exacto que ves:
   [ ] Completado

3. El archivo de log (outlook_sync_agent.log):
   - Ubicación: C:\Outlook-Sync-Client\outlook_sync_agent.log
   - Envía como adjunto
   [ ] Completado

4. Resultado de este comando en PowerShell:
   ```
   ping 192.168.1.100
   Test-NetConnection -ComputerName 192.168.1.100 -Port 5000
   ```
   [ ] Completado

Una vez reciba esta información, podré diagnosticar el problema.

Atentamente,
Admin TI
```

---

## Reporte de Problemas

### Crear Base de Datos de Incidentes

```powershell
# Script: logear_problema_cliente.ps1

param(
    [string]$ComputerName,
    [string]$Usuario,
    [string]$Problema,
    [string]$LogosPath = "C:\Admin\Outlook-Sync-Logs"
)

# Crear carpeta de logs si no existe
if ((Test-Path $LogosPath) -eq $false) {
    New-Item -Path $LogosPath -ItemType Directory -Force | Out-Null
}

# Obtener archivo de log remoto
$RemoteLog = "\\$ComputerName\C$\Outlook-Sync-Client\outlook_sync_agent.log"
$LocalLog = "$LogosPath\$ComputerName-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

Copy-Item -Path $RemoteLog -Destination $LocalLog -ErrorAction SilentlyContinue

# Registrar problema en CSV
$IncidentFile = "$LogosPath\incidentes.csv"

$Incident = [PSCustomObject]@{
    Timestamp = Get-Date
    ComputerName = $ComputerName
    Usuario = $Usuario
    Problema = $Problema
    LogGuardado = $LocalLog
}

if ((Test-Path $IncidentFile) -eq $false) {
    $Incident | Export-Csv -Path $IncidentFile -NoTypeInformation
} else {
    $Incident | Export-Csv -Path $IncidentFile -Append -NoTypeInformation
}

Write-Host "Incidente registrado: $($Incident.Timestamp) - $ComputerName"
```

**Ejecutar**:
```powershell
.\logear_problema_cliente.ps1 -ComputerName "PC-USER1" -Usuario "juan.perez" -Problema "Outlook no sincroniza"
```

---

## Monitoreo en Masa

### Dashboard de Estado

Script para ver estado de sincronización en todas las PCs:

```powershell
# Script: monitorear_clientes.ps1

param([string[]]$ComputerNames = @())

if ($ComputerNames.Count -eq 0) {
    $ComputerNames = (Get-ADComputer -Filter * -SearchBase "OU=Usuarios,DC=empresa,DC=local").Name
}

$Results = @()

foreach ($Computer in $ComputerNames) {
    $LogPath = "\\$Computer\C$\Outlook-Sync-Client\outlook_sync_agent.log"
    
    if ((Test-Path $LogPath)) {
        $LastSync = (Get-Item $LogPath).LastWriteTime
        $LastLines = Get-Content $LogPath -Tail 3
        
        $Status = if ($LastSync -gt (Get-Date).AddHours(-1)) {
            "✓ Activo"
        } else {
            "⚠ Inactivo por >1 hora"
        }
        
        $Results += [PSCustomObject]@{
            Computadora = $Computer
            Estado = $Status
            UltimaSincronizacion = $LastSync
            UltimaActividad = $LastLines[0]
        }
    } else {
        $Results += [PSCustomObject]@{
            Computadora = $Computer
            Estado = "✗ No instalado"
            UltimaSincronizacion = "N/A"
            UltimaActividad = "N/A"
        }
    }
}

# Mostrar resultados
$Results | Format-Table -AutoSize
$Results | Export-Csv -Path "C:\Admin\reporte-clientes-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

**Ejecutar**:
```powershell
.\monitorear_clientes.ps1 | Out-GridView
```

---

## Checklist para Administrador

Antes de distribuir a usuarios:

```
PREPARACIÓN DEL SERVIDOR:
□ Servidor Flask corriendo en http://localhost:5000
□ Base de datos inicializada
□ Usuario admin creado
□ Firewall permite puerto 5000 desde red local
□ Endpoint /api/emails/sync/remote probado

PREPARACIÓN DE ARCHIVOS:
□ outlook_sync_agent.py copiado
□ outlook_sync_config.json.example copiado
□ Instaladores (BAT) copiados
□ Documentación copiada
□ ZIP o carpeta compartida creada

PRUEBAS:
□ Instalación probada en una PC de prueba
□ Sincronización manual ejecutada exitosamente
□ Correos aparecen en dashboard
□ Logs verificados

DISTRIBUCIÓN:
□ Comunicación a usuarios enviada
□ Método de distribución elegido
□ Acceso a recursos compartidos verificado
□ Fecha de deadline establecida

SOPORTE:
□ Canal de soporte creado
□ FAQ preparada
□ Template de tickets creado
□ Scripts de monitoreo probados

POST-DISTRIBUCIÓN:
□ Chequeo de instalaciones completadas
□ Soporte a problemas iniciales
□ Reporte de incidentes registrado
□ Documentación de lecciones aprendidas
```

---

## Variables de Ambiente Útiles

Para facilitar la distribución, puedes crear un archivo `.env`:

```
# .env
SERVER_URL=http://192.168.1.100:5000
SYNC_INTERVAL=15
SYNC_LIMIT=20
LOG_PATH=C:\Outlook-Sync-Client\outlook_sync_agent.log
```

---

## Información de Versión

```
Versión Cliente: 1.0
Fecha Lanzamiento: Marzo 2026
Compatible con: 
  - Windows 10/11/Server 2019+
  - Python 3.8+
  - Outlook 2016+

Archivos:
  - outlook_sync_agent.py (v1.0)
  - outlook_sync_config.json.example (v1.0)
  - Dependencias: requests, pywin32

Cambios Recientes:
  - Fijo: Manejo de destinatarios con Exchange User
  - Mejorado: Logging con soporte UTF-8
  - Agregado: Endpoint /api/emails/sync/remote
  - Agregado: Auditoría de sincronizaciones remotas
```

---

**Fin de Guía para Administradores**

Para preguntas o soporte técnico, contacta al equipo de desarrollo.
