# Solución para Error de Sincronización de Outlook

## Problema
```
Error sincronizando: No se pudo conectar a Outlook. 
Asegúrese de tener Outlook instalado y abierto en este equipo.
```

## Causas Comunes

### ❌ Outlook en Navegador (Web)
Si estás usando **Outlook en el navegador** (outlook.com o outlook.office.com), **NO funcionará**.
- La sincronización requiere la **aplicación de escritorio de Outlook** (Outlook 2019, 2021, Office 365, etc.)

### ❌ Outlook Cerrado
La aplicación de Outlook debe estar **completamente abierta** en Windows.
- Solo minimizado no es suficiente; debe estar en ejecución

### ❌ Componentes COM no Registrados
`pywin32` fue instalado pero sus componentes COM no fueron registrados.

## Solución Paso a Paso

### Paso 1: Verifica que Outlook esté Abierto
1. **Abre Outlook** (versión de escritorio, NO web)
2. **Inicia sesión** si es necesario
3. **Espera** a que se carguen completamente los datos

### Paso 2: Registra los Componentes COM de pywin32

Ejecuta en PowerShell o CMD **COMO ADMINISTRADOR**:

```powershell
# Abre PowerShell Como Administrador:
# 1. Presiona Windows + X
# 2. Selecciona "Símbolo del sistema (Administrador)" o "PowerShell (Administrador)"

# Ve a la carpeta del proyecto:
cd C:\Users\INE.INE24\Documents\Codes\Administrativo\Correos

# Activa el entorno virtual:
.\venv\Scripts\Activate.ps1

# Ejecuta el script de reparación:
python fix_outlook.py
```

### Paso 3: Si el Paso 2 No Funciona
Intenta reinstalar `pywin32`:

```powershell
# En PowerShell con permisos de Administrador:
pip uninstall pywin32 -y
pip install pywin32==311

# Después, ejecuta:
python fix_outlook.py
```

### Paso 4: Reinicia Python/VS Code
Después de ejecutar `fix_outlook.py`, reinicia completamente:
1. Cierra VS Code
2. Abre VS Code nuevamente
3. Ejecuta el servidor: `python run.py`

## ¿Cómo sé si fue exitoso?

Ejecuta `python fix_outlook.py` y busca estos mensajes:

```
✓ Outlook.Application obtenida
✓ Namespace MAPI obtenido
✓ Carpeta de elementos enviados obtenida
✓ ¡CONEXIÓN A OUTLOOK EXITOSA!
```

Si ves "✓ ¡CONEXIÓN A OUTLOOK EXITOSA!", entonces ya puedes sincronizar.

## Requisitos Finales

Antes de sincronizar, asegúrate de:

✅ **Outlook está abierto** (versión de escritorio)
✅ **Has iniciado sesión** en tu cuenta de Outlook
✅ **Los componentes COM están registrados** (ejecutaste `python fix_outlook.py`)
✅ **Tienes conexión a internet** (Outlook necesita conectarse a los servidores)

## Probando la Sincronización

1. Mantén **Outlook abierto**
2. Ve al dashboard de la aplicación
3. Haz clic en **"Sincronizar Outlook"**
4. Debería sincronizar tu último correo enviado

## Si Aún No Funciona

1. **Abre los logs** del servidor Flask (terminal donde corre `python run.py`)
2. **Busca mensajes de error** que comiencen con `[SYNC]`
3. **Copia el mensaje de error** completo
4. **Intenta cerrar completamente Outlook** y abrirlo de nuevo
5. **Reinicia el servidor** (`python run.py`)

## Notas Importantes

- **No uses Outlook en navegador**: Solo funciona con la aplicación de escritorio
- **Outlook debe estar abierto**: No es suficiente tenerlo minimizado
- **Primera sincronización**: Puede tardar unos segundos mientras establece la conexión COM
- **Solo sincroniza el último correo**: Por defecto, solo obtiene el correo más reciente (para cambiar, usa `?limit=5`)

## ¿Necesitas Ayuda Adicional?

Si el error persiste después de seguir todos estos pasos, verifica:

1. **Versión de Outlook**: Asegúrate de tener una versión compatible (2019, 2021, Office 365, etc.)
2. **Permisos de Windows**: El usuario debe tener permiso para acceder a COM
3. **Antivirus/Firewall**: Algunos antivirus bloquean acceso COM a aplicaciones
4. **Actualiza Office**: Algunos incompatibilidades se resuelven actualizando Office
