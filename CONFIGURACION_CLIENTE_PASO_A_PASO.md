# 📋 Configuración del Equipo Cliente - Guía Paso a Paso Detallada

**Versión:** 1.0  
**Fecha:** Marzo 2026  
**Sistema:** Windows + Outlook 2019+  

---

## 📌 Índice
1. [Requisitos Previos](#requisitos-previos)
2. [Preparación en el Servidor](#preparacion-en-el-servidor)
3. [Preparación del Equipo Cliente](#preparacion-del-equipo-cliente)
4. [Instalación de Dependencias](#instalacion-de-dependencias)
5. [Configuración del Cliente](#configuracion-del-cliente)
6. [Primera Sincronización](#primera-sincronizacion)
7. [Configurar Sincronización Automática](#configurar-sincronizacion-automatica)
8. [Verificación de Funcionamiento](#verificacion-de-funcionamiento)
9. [Solución de Problemas](#solucion-de-problemas)
10. [Mantenimiento Continuo](#mantenimiento-continuo)

---

## 1. Requisitos Previos

### 1.1 En el Equipo Cliente (PC del Usuario)

Antes de instalar, verifica que tu computadora cumple con:

#### Hardware
- ✅ Procesador: Intel Core i5 o superior / AMD Ryzen 5 o superior
- ✅ RAM: Mínimo 4GB
- ✅ Disco duro: Mínimo 500MB libres
- ✅ Conexión de red: Ethernet o WiFi (velocidad mínima 1Mbps)

#### Software
- ✅ **Sistema Operativo:** Windows 10, Windows 11, o Windows Server 2019+
- ✅ **Outlook:** Versión 2019, Microsoft 365, o superior (INSTALADO Y FUNCIONANDO)
- ✅ **Python:** Versión 3.8 o superior
- ✅ **PowerShell:** Versión 5.0 o superior (incluido en Windows 10+)
- ✅ **Permisos:** Acceso de Administrador en el equipo

#### Verificar Requisitos

**Verificar versión de Windows:**
```powershell
# Ejecuta en PowerShell normal
[System.Environment]::OSVersion.VersionString
# Debe ser: Microsoft Windows 10.0.xxxxx o Windows 11.0.xxxxx
```

**Verificar si Outlook está instalado:**
```powershell
# Ejecuta en PowerShell normal
Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | 
Select-Object DisplayName | 
Where-Object DisplayName -like "*Outlook*"
# Debe mostrar Microsoft Office Outlook
```

**Verificar versión de Python:**
```powershell
# Ejecuta en PowerShell normal
python --version
# Debe ser: Python 3.8.0 o superior
# Si no está instalado, descárgalo de: https://www.python.org/downloads/
```

**Verificar PowerShell:**
```powershell
$PSVersionTable.PSVersion
# Debe ser: 5.1 o superior (en Windows 11 es 7+)
```

**Verificar conectividad de red:**
```powershell
# Prueba ping al servidor (reemplaza IP)
ping 192.168.1.100
# Debe responder sin timeout
```

### 1.2 Información que Necesitas del Servidor

Obtén estos datos del administrador del servidor:

| Dato | Ejemplo | Nota |
|------|---------|------|
| **IP/Hostname del servidor** | `192.168.1.100` o `servidor.local` | Dirección en la red local |
| **Puerto del servidor** | `5000` | Generalmente es 5000 |
| **Tu usuario en el servidor** | `juan.lopez` | El que creaste en el registro |
| **Tu contraseña en el servidor** | `MiContraseña123!` | Segura y con mayúsculas |
| **Límite de correos a sincronizar** | `10`, `20`, `50` | Cantidad inicial (puedes cambiar) |

---

## 2. Preparación en el Servidor

### 2.1 Antes de Empezar (Lado del Administrador)

**El administrador debe asegurarse de:**

- ✅ El servidor está en línea y escuchando en puerto 5000
- ✅ Tu usuario está creado en el sistema
- ✅ Tu contraseña está configurada correctamente
- ✅ La base de datos del servidor está inicializada
- ✅ El firewall permite conexiones entrantes en puerto 5000

**Prueba de conectividad (ejecuta desde tu PC cliente):**

```powershell
# Prueba latencia al servidor
ping 192.168.1.100

# Prueba acceso al puerto HTTP 5000
Test-NetConnection -ComputerName 192.168.1.100 -Port 5000

# Debería mostrar: TcpTestSucceeded : True
```

---

## 3. Preparación del Equipo Cliente

### 3.1 Crear Carpeta para el Cliente

**Paso 1:** Abre **File Explorer** (Explorador de Archivos)

**Paso 2:** Navega a una ubicación clara, por ejemplo:
- Opción A: `C:\Usuarios\TuNombre\Desktop` (Escritorio)
- Opción B: `C:\Programas\Outlook-Sync` (Recomendado)
- Opción C: `D:\Datos\Sync-Outlook` (Si tienes otra partición)

**Paso 3:** Crea una carpeta nueva con nombre descriptivo:
```
Outlook-Sync-Client
```

**Paso 4:** Anota la ruta completa, ejemplo:
```
C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client
```

### 3.2 Asegurar que Outlook está Funcionando

**Paso 1:** Abre Outlook normalmente (no en Outlook Web)

**Paso 2:** Espera a que cargue completamente (15-30 segundos)

**Paso 3:** Verifica que tu cuenta está autenticada:
- Deberías ver tu bandeja de entrada
- Tu nombre debería aparecer en la esquina inferior izquierda

**Paso 4:** Mantén Outlook ABIERTO durante toda la instalación

**Paso 5:** Crea un correo de prueba:
- Redacta un nuevo correo dirigido a ti mismo
- Envíalo (esto lo coloca en "Elementos enviados")
- Cierra el correo

---

## 4. Instalación de Dependencias

### 4.1 Obtener los Archivos del Cliente

**Paso 1:** Pide al administrador estos 4 archivos:
```
1. outlook_sync_agent.py
2. outlook_sync_config.json.example
3. install_client.bat
4. run_sync_client.bat
```

**Paso 2:** Si los recibes comprimidos en ZIP:
- Descomprime usando: Clic derecho → Extraer todo
- Selecciona tu carpeta `Outlook-Sync-Client`
- Extrae aquí

**Paso 3:** Verifica que los 4 archivos estén en tu carpeta:
```
C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client\
├── outlook_sync_agent.py
├── outlook_sync_config.json.example
├── install_client.bat
└── run_sync_client.bat
```

### 4.2 Abrir PowerShell como Administrador

**IMPORTANTE:** Estos pasos REQUIEREN permisos de administrador

**Paso 1:** Abre el menú Inicio de Windows

**Paso 2:** Escribe: `PowerShell`

**Paso 3:** **HAZ CLIC DERECHO** en "Windows PowerShell"

**Paso 4:** Selecciona: "Ejecutar como administrador"

**Paso 5:** Si pide confirmación, haz clic en "Sí"

**Paso 6:** Deberías ver en el title de la ventana: "Administrator: Windows PowerShell"

### 4.3 Navegar a la Carpeta del Cliente

En la ventana de PowerShell que abriste como administrador:

```powershell
# Navega a tu carpeta (reemplaza la ruta)
cd C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client

# Verifica que estás en la carpeta correcta
ls

# Deberías ver los 4 archivos
```

**Resultado esperado:**
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          3/23/2026  10:30 AM           5478 outlook_sync_agent.py
-a---          3/23/2026  10:25 AM           1234 outlook_sync_config.json.example
-a---          3/23/2026  10:20 AM            893 install_client.bat
-a---          3/23/2026  10:15 AM            456 run_sync_client.bat
```

### 4.4 Crear Virtual Environment

Un "virtual environment" es una carpeta aislada con Python y librerías independientes.

**Paso 1:** Ejecuta en PowerShell:
```powershell
python -m venv venv
```

**Paso 2:** Espera a que termine (1-2 minutos)

**Paso 3:** Una nueva carpeta `venv` se creará

### 4.5 Activar Virtual Environment

**Paso 1:** Ejecuta en PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

**Paso 2:** Deberías ver esto al inicio de cada línea en PowerShell:
```
(venv) PS C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client>
```

**Nota:** La palabra `(venv)` indica que el virtual environment está activo

### 4.6 Instalar Librerías Necesarias

**Paso 1:** Ejecuta en PowerShell (con venv activo):
```powershell
pip install --upgrade pip
```

**Paso 2:** Espera a que termine (puede tomar 1-2 minutos)

**Paso 3:** Instala las librerías requeridas:
```powershell
pip install requests pywin32
```

**Paso 4:** Espera a que termine

**Resultado esperado:**
```
Successfully installed requests-2.31.0 urllib3-2.0.7 certifi-2023.7.22 charset-normalizer-3.3.2 idna-2.10 pywin32-305
```

### 4.7 Registrar Componentes de pywin32

**ESTE PASO ES CRÍTICO - No lo omitas**

**Paso 1:** Ejecuta en PowerShell (con venv activo):
```powershell
python -m pywin32_postinstall -install
```

**Paso 2:** Espera a que complete (15-30 segundos)

**Resultado esperado:**
```
Finished processing
```

**Paso 3:** Si ves errores, DETENTE e informa al administrador

---

## 5. Configuración del Cliente

### 5.1 Crear Archivo de Configuración

**Paso 1:** En PowerShell (con venv activo), ejecuta:
```powershell
Copy-Item outlook_sync_config.json.example outlook_sync_config.json
```

**Paso 2:** Verifica que se creó:
```powershell
ls outlook_sync_config.json
```

**Paso 3:** Abre el archivo con editor de texto:
```powershell
notepad outlook_sync_config.json
```

### 5.2 Editar el Archivo de Configuración

Se abrirá el Bloc de Notas con contenido similar a:
```json
{
    "server_url": "http://192.168.1.100:5000",
    "username": "usuario_ejemplo",
    "password": "contraseña_ejemplo",
    "limit": 10
}
```

**Paso 1:** Reemplaza `192.168.1.100` con la **IP real de tu servidor**

**Paso 2:** Reemplaza `usuario_ejemplo` con **tu usuario real**

**Paso 3:** Reemplaza `contraseña_ejemplo` con **tu contraseña real**

**Paso 4:** Opcionalmente, cambia `limit` (cantidad de correos):
- `10` = sincroniza los últimos 10 correos (recomendado para prueba)
- `20` = últimos 20 correos
- `50` = últimos 50 correos
- `100` = todos los que tengas

**Ejemplo completo:**
```json
{
    "server_url": "http://192.168.1.100:5000",
    "username": "juan.lopez",
    "password": "Mi$eguraPassword2026!",
    "limit": 20
}
```

**Paso 5:** Haz clic en Archivo → Guardar

**Paso 6:** Cierra el Bloc de Notas

### 5.3 Verificar Formato del Archivo

**Paso 1:** En PowerShell, ejecuta:
```powershell
cat outlook_sync_config.json
```

**Paso 2:** Verifica que:
- No haya caracteres especiales raros
- Las comillas sean derechas `"` (no curvas `"`)
- Haya comas entre los campos
- La estructura sea igual al ejemplo

---

## 6. Primera Sincronización

### 6.1 Prueba Manual (Recomendado)

**Paso 1:** Asegurate que:
- PowerShell está abierto como administrador
- Virtual environment está activo (ves `(venv)` al inicio)
- Estás en la carpeta correcta

**Paso 2:** Ejecuta tu primer sincronismo:
```powershell
python outlook_sync_agent.py
```

**Paso 3:** Espera a que termine (30 segundos - 2 minutos)

### 6.2 Interpretar la Salida

**Salida exitosa esperada:**
```
2026-03-23 14:30:15 - INFO - ============================================================
2026-03-23 14:30:15 - INFO - Iniciando sincronización de Outlook
2026-03-23 14:30:15 - INFO - ============================================================
2026-03-23 14:30:16 - INFO - Conectando a Outlook...
2026-03-23 14:30:17 - INFO - ✓ Outlook conectado (GetActiveObject)
2026-03-23 14:30:17 - INFO - Autenticando en http://192.168.1.100:5000/api/auth/login...
2026-03-23 14:30:18 - INFO - ✓ Autenticación exitosa. Token obtenido.
2026-03-23 14:30:18 - INFO - Obteniendo últimos 20 correos de Outlook...
2026-03-23 14:30:20 - INFO - ✓ 5 correos obtenidos de Outlook
2026-03-23 14:30:20 - INFO - Enviando 5 correos al servidor...
2026-03-23 14:30:21 - INFO - ✓ Sincronización exitosa: 5 correos sincronizados correctamente
```

**Lo que significa cada línea:**
1. Inicio del proceso
2. Conecta a Outlook en tu PC
3. Se autentica contra el servidor (hace login)
4. Obtiene tus correos locales
5. Los envía al servidor

### 6.3 Verificar en el Servidor Web

**Paso 1:** Abre un navegador (Chrome, Edge, Firefox)

**Paso 2:** Ve a la dirección del servidor:
```
http://192.168.1.100:5000
```

**Paso 3:** Haz login con tus credenciales:
- Usuario: `juan.lopez`
- Contraseña: `Mi$eguraPassword2026!`

**Paso 4:** Haz clic en "Correos"

**Paso 5:** Deberías ver tus correos sincronizados en la lista

---

## 7. Configurar Sincronización Automática

### 7.1 Opción A: Sincronización Automática Simple (Recomendado)

Sincroniza automáticamente cada 15 minutos mientras PowerShell está abierto.

**Paso 1:** En PowerShell (con venv activo), ejecuta:
```powershell
python outlook_sync_agent.py --daemon --interval 15
```

**Paso 2:** Verás esta salida:
```
2026-03-23 14:35:00 - INFO - Iniciando daemon de sincronización...
2026-03-23 14:35:00 - INFO - Intervalo: 15 minutos
2026-03-23 14:35:01 - INFO - [SYNC #1] Sincronización iniciada...
```

**Paso 3:** El proceso continuará sincronizando cada 15 minutos

**Paso 4:** Para detener, presiona: `Ctrl + C`

### 7.2 Opción B: Sincronización Automática Avanzada (Con Script Batch)

Usa el archivo `run_sync_client.bat` que ya tienes.

**Paso 1:** Abre el archivo `run_sync_client.bat` con Bloc de Notas:
```powershell
notepad run_sync_client.bat
```

**Paso 2:** Modificalo para incluir el intervalo deseado:
```batch
@echo off
cd C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client
call venv\Scripts\Activate.ps1
python outlook_sync_agent.py --daemon --interval 15
pause
```

**Paso 3:** Guarda y cierra

**Paso 4:** Haz doble clic en `run_sync_client.bat` desde File Explorer

**Paso 5:** Se abrirá PowerShell automáticamente

### 7.3 Opción C: Ejecutar al Iniciar Windows (Avanzado)

Para que se sincronice automáticamente al encender tu PC:

**Paso 1:** Presiona `Win + R` (Ejecutar)

**Paso 2:** Escribe:
```
shell:startup
```

**Paso 3:** Se abrirá la carpeta de Inicio

**Paso 4:** Copia tu archivo `run_sync_client.bat` aquí

**Paso 5:** Cada vez que enciendas Windows, ejecutará automáticamente

### 7.4 Opción D: Programador de Tareas de Windows (Profesional)

Para máximo control sobre horarios y frecuencia.

**Paso 1:** Presiona `Win + R`

**Paso 2:** Escribe: `TaskScheduler`

**Paso 3:** Haz clic derecho → "Crear Tarea Básica"

**Paso 4:** Rellena:
- Nombre: `Sincronización Outlook`
- Descripción: `Sincroniza Outlook cada 15 minutos`

**Paso 5:** En "Desencadenador": Selecciona "Al iniciar" y agrega otro "Cada 15 minutos"

**Paso 6:** En "Acción": 
- Programa: `powershell.exe`
- Argumentos: `-ExecutionPolicy Bypass -File "C:\Usuarios\TuNombre\Desktop\Outlook-Sync-Client\run_sync.ps1"`

**Paso 7:** Marca "Ejecutar con mayores privilegios"

**Paso 8:** Haz clic en Aceptar

---

## 8. Verificación de Funcionamiento

### 8.1 Primera Verificación (Inmediata)

**En la PC Cliente:**
1. Abre el archivo `outlook_sync_agent.log` con Bloc de Notas
2. Busca la última línea
3. Debe decir: "✓ Sincronización exitosa"

**En el Servidor Web:**
1. Entra a `http://192.168.1.100:5000`
2. Ve a "Correos"
3. Deberías ver tus correos listados

### 8.2 Verificación de Continuidad (Cada Día)

**Cada mañana, verifica:**
1. PowerShell sigue corriendo (si usas modo daemon)
2. El archivo `log` tiene nuevas entradas
3. Las estadísticas del servidor aumentaron

### 8.3 Prueba de Correos Nuevos

**Paso 1:** Envía un correo a ti mismo desde Outlook

**Paso 2:** Espera 1 minuto (o dispara un sync manual)

**Paso 3:** Entra al servidor web y recarga

**Paso 4:** Deberías ver el correo nuevo

---

## 9. Solución de Problemas

### 9.1 "Error de Autenticación: 401"

**Causa:** Usuario o contraseña incorrectos

**Solución:**
```powershell
# 1. Abre el archivo de configuración
notepad outlook_sync_config.json

# 2. Verifica que:
# - username está correcto (sin espacios extras)
# - password está correcta (mayúsculas/minúsculas importan)
# - Guarda el archivo

# 3. Intenta sincronizar nuevamente
python outlook_sync_agent.py
```

### 9.2 "Connection Refused" / "El servidor no responde"

**Causa:** Servidor no está disponible o IP es incorrecta

**Solución:**
```powershell
# 1. Verifica la IP/Hostname del servidor
ping 192.168.1.100

# 2. Si no responde:
#    - Verifica que escribiste la IP correcta
#    - Verifica que el servidor está en línea
#    - Pregunta al administrador

# 3. Verifica el puerto
Test-NetConnection -ComputerName 192.168.1.100 -Port 5000

# 4. Si falla:
#    - El servidor no está escuchando en ese puerto
#    - Avisa al administrador
```

### 9.3 "ModuleNotFoundError: No module named 'requests' o 'pywin32'"

**Causa:** Las librerías no se instalaron correctamente

**Solución:**
```powershell
# 1. Verifica que virtual environment está activo
#    (debes ver (venv) al inicio)

# 2. Si no, actívalo:
.\venv\Scripts\Activate.ps1

# 3. Reinstala las librerías:
pip install --upgrade pip
pip install requests pywin32
python -m pywin32_postinstall -install

# 4. Intenta sincronizar nuevamente
python outlook_sync_agent.py
```

### 9.4 "Outlook no se conecta" / "Error conectando a Outlook"

**Causa:** Outlook no está abierto o no se inicializó correctamente

**Solución:**
1. Cierra completamente Outlook (Alt+F4)
2. Espera 10 segundos
3. Abre Outlook nuevamente
4. Espera a que cargue completamente (30 segundos)
5. Intenta sincronizar nuevamente

### 9.5 "Los correos no aparecen en el servidor"

**Causa:** Tal vez no tienes correos en "Elementos Enviados"

**Solución:**
1. Abre Outlook en tu PC
2. Envía un correo a ti mismo (File → New Email)
3. Cárgate a ti mismo en el campo "Para"
4. Escribe "Prueba" en el asunto
5. Haz clic en "Enviar"
6. Ve a "Elementos Enviados"
7. Verifica que el correo está ahí
8. Sincroniza nuevamente

### 9.6 "ExecutionPolicy" Error en PowerShell

**Causa:** Las políticas de ejecución están muy restringidas

**Solución:**
```powershell
# 1. En PowerShell como Administrador, ejecuta:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Presiona 'Y' y Enter para confirmar

# 3. Intenta nuevamente
python outlook_sync_agent.py
```

### 9.7 "CRITICAL ERROR durante postinstall de pywin32"

**Causa:** Permisos insuficientes o Windows Defender bloqueó algo

**Solución:**
```powershell
# 1. Cierra todo excepto PowerShell Administrador

# 2. Ejecuta:
python -m pywin32_postinstall -install -silent

# 3. Espera sin hacer nada

# 4. Si sigue fallando, ejecuta:
pip uninstall pywin32
pip install pywin32
python -m pywin32_postinstall -install

# 5. Si aún falla, desactiva temporalmente Windows Defender
#    (consulta con el administrador)
```

---

## 10. Mantenimiento Continuo

### 10.1 Revisión Diaria

**Cada día, revisa:**

1. PowerShell está abierto en segundo plano (si usas daemon)
2. El archivo `.log` tiene registro de sincronizaciones
3. En el servidor web, tus correos más nuevos están visibles

### 10.2 Limpieza Mensual

**Una vez al mes:**

1. Abre archivo de log:
   ```powershell
   notepad outlook_sync_agent.log
   ```

2. Si tiene más de 10,000 líneas, recórtalo:
   - Selecciona todo (Ctrl+A)
   - Presiona Delete
   - Guarda
   - PowerShell volverá a crear el log

### 10.3 Actualización de Configuración

**Si cambian tus credenciales:**

```powershell
# 1. Edita el archivo:
notepad outlook_sync_config.json

# 2. Cambia username/password

# 3. Guarda

# 4. La próxima sincronización usará las nuevas credenciales
```

### 10.4 Cambio de Intervalo de Sincronización

**Si quieres sincronizar más frequentemente:**

```powershell
# Cambiar de 15 a 5 minutos:
python outlook_sync_agent.py --daemon --interval 5

# Cambiar de 15 a 30 minutos:
python outlook_sync_agent.py --daemon --interval 30
```

### 10.5 Sincronizar Más Correos Históricos

**Si necesitas más correos antiguos:**

```powershell
# Edita el archivo:
notepad outlook_sync_config.json

# Cambia "limit" de 10 a 100:
"limit": 100

# Guarda

# Sincroniza:
python outlook_sync_agent.py
```

### 10.6 Resetear Completamente

**Si algo se daña y necesitas empezar de cero:**

```powershell
# 1. Detén cualquier proceso (Ctrl+C)

# 2. Desactiva el entorno:
deactivate

# 3. Elimina la carpeta venv:
Remove-Item -Recurse -Force venv

# 4. Elimina el log:
Remove-Item outlook_sync_agent.log

# 5. Empieza nuevamente desde paso 4.4
python -m venv venv
.\venv\Scripts\Activate.ps1
# ... etc
```

---

## 🎓 Referencia Rápida de Comandos

### PowerShell Básico

```powershell
# Navegar a carpeta
cd C:\ruta\completa

# Listar archivos
ls
# o
dir

# Crear carpeta
mkdir nombre_carpeta

# Ver contenido de archivo
cat nombre_archivo.json
# o
notepad nombre_archivo.json

# Crear virtual environment
python -m venv venv

# Activar virtual environment
.\venv\Scripts\Activate.ps1

# Desactivar virtual environment
deactivate

# Instalar paquete
pip install nombre_paquete

# Ver versión Python
python --version

# Ejecutar script
python nombre_script.py

# Detener proceso
Ctrl + C
```

### Comandos Especiales del Cliente

```powershell
# Sincronización manual (una sola vez)
python outlook_sync_agent.py

# Sincronización automática cada 15 minutos
python outlook_sync_agent.py --daemon --interval 15

# Sincronización automática con argumentos en línea
python outlook_sync_agent.py -s http://192.168.1.100:5000 -u juan -p password -l 50 -d -i 10

# Ver los logs
cat outlook_sync_agent.log

# Última línea del log
tail -n 5 outlook_sync_agent.log
```

---

## 📞 Soporte y Escalación

**Si después de seguir esta guía encuntras problemas:**

1. **Anota el error exacto** que ves en PowerShell
2. **Toma una captura de pantalla** del error
3. **Mira el archivo `outlook_sync_agent.log`** y copia las líneas rojas
4. **Contacta al administrador** con esta información:
   - Tu usuario
   - IP del servidor que usas
   - El error exacto
   - El contenido del log (últimas 20 líneas)

---

## ✅ Checklist de Verificación Final

Antes de dar por completada la configuración:

- [ ] PowerShell está abierto como Administrador
- [ ] Virtual environment está activo (ves `(venv)`)
- [ ] El archivo `outlook_sync_config.json` existe y está correcto
- [ ] El archivo `outlook_sync_agent.log` existe y muestra SUCCESS
- [ ] Outlook está abierto en tu PC
- [ ] Al menos 1 correo está en "Elementos Enviados"
- [ ] Puedes hacer ping al servidor
- [ ] En el servidor web, puedes ver tus correos
- [ ] El cliente sincroniza automáticamente (si usas daemon)

Si TODAS estas verificaciones son ✅, **tu cliente está correctamente configurado.**

---

**Última Actualización:** Marzo 23, 2026  
**Versión:** 1.0  
**Documentación Completa SHA:** 5a8d9c2f

