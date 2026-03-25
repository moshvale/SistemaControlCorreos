# Microsoft Graph API - Guía de Configuración

## Resumen de Cambios

Se ha implementado **Microsoft Graph API** con **OAuth2** para permitir que cada usuario sincronice sus propios correos usando sus credenciales de Microsoft/Office 365.

### ✅ Ventajas de esta solución:

- **Seguridad**: Cada usuario solo ve sus propios correos (autenticado por Microsoft)
- **Escalabilidad**: Funciona para cualquier número de usuarios
- **Multi-usuario en red**: Los usuarios de la red local pueden usar sus propias credenciales
- **Sin dependencias locales**: No requiere Outlook de escritorio abierto
- **Renovación automática de tokens**: Los tokens se renuevan automáticamente cuando expiran

---

## Paso 1: Registrar la Aplicación en Azure AD

### 1.1 Acceder a Azure Portal

1. Ve a https://portal.azure.com
2. Inicia sesión con tu cuenta de Microsoft

### 1.2 Registrar nueva aplicación

1. Ve a **Azure Active Directory** → **App registrations** (Registros de aplicaciones)
2. Haz clic en **+ New registration** (Nuevo registro)
3. Completa los datos:
   - **Name**: `Email Tracker App` (o el nombre que prefieras)
   - **Supported account types**: Selecciona "Accounts in any organizational directory and personal Microsoft accounts"
   - **Redirect URI**: Selecciona `Web` y coloca: `http://localhost:5000/api/auth/callback/microsoft`
   - **Haz clic en Register**

### 1.3 Configurar permisos

1. Ve a **API permissions** (Permisos de API)
2. Haz clic en **+ Add a permission** (Agregar permiso)
3. Selecciona **Microsoft Graph**
4. Selecciona **Delegated permissions** (Permisos delegados)
5. Busca y selecciona:
   - `Mail.Read` - Leer correos del usuario
   - `Mail.ReadWrite` - Leer y escribir correos
   - `User.Read` - Leer información básica del usuario
   - `offline_access` - Acceso offline (para refresh tokens)
6. Haz clic en **Add permissions**

### 1.4 Obtener credenciales

1. Ve a **Certificates & secrets** (Certificados y secretos)
2. Haz clic en **+ New client secret** (Nuevo secreto de cliente)
3. Completa:
   - **Description**: `Email Tracker Secret`
   - **Expires**: Selecciona un período (recomendado: 24 meses)
4. **Copia el Value** (lo necesitarás en el siguiente paso)
5. Ve a **Overview** y copia:
   - **Application (client) ID**
   - **Directory (tenant) ID**

---

## Paso 2: Configurar Variables de Entorno

Crea o edita el archivo `.env` en la raíz del proyecto:

```env
# Microsoft Graph Configuration
MICROSOFT_CLIENT_ID=xxxxx-xxxx-xxxx-xxxx-xxxxx
MICROSOFT_CLIENT_SECRET=tu_secret_aqui
MICROSOFT_TENANT_ID=xxxxx-xxxx-xxxx-xxxx-xxxxx
MICROSOFT_REDIRECT_URI=http://localhost:5000/api/auth/callback/microsoft

# Para producción (cambiar a tu URL real):
# MICROSOFT_REDIRECT_URI=https://tudominio.com/api/auth/callback/microsoft
```

**Reemplaza los valores con los obtenidos en Azure AD.**

### Nota importante:
- El `MICROSOFT_REDIRECT_URI` debe coincidir exactamente con el registrado en Azure AD
- Para desarrollo local usa `http://localhost:5000`
- Para producción usa `https://tudominio.com`

---

## Paso 3: Iniciar sesión con Microsoft

### Flujo de autenticación:

1. **El usuario solicita login de Microsoft**:
   ```
   GET /api/auth/microsoft/login
   ```
   Devuelve una URL de autenticación

2. **El usuario es redirigido a Microsoft**:
   - Inicia sesión con su correo de Microsoft
   - Aprueba los permisos solicitados

3. **Microsoft redirige de vuelta**:
   ```
   GET /api/auth/callback/microsoft?code=xxxxx
   ```
   - Se intercambia el código por tokens
   - Se crea el usuario en la base de datos
   - Se devuelven tokens JWT

---

## Rutas API Disponibles

### Autenticación Microsoft

```
GET /api/auth/microsoft/login
→ Obtiene URL de autenticación de Microsoft

GET /api/auth/callback/microsoft?code=xxxxx
→ Callback de Microsoft (automático)

GET /api/auth/microsoft/status
→ Verifica estado de autenticación de Microsoft

POST /api/auth/microsoft/disconnect
→ Desconecta la cuenta de Microsoft
```

### Sincronización de Correos

```
GET /api/sync/microsoft/sent
→ Sincroniza correos ENVIADOS del usuario
  Parámetros: ?limit=50

GET /api/sync/microsoft/inbox
→ Sincroniza correos de ENTRADA del usuario
  Parámetros: ?limit=50

GET /api/sync/microsoft/status
→ Obtiene estado de sincronización
```

---

## Paso 4: Usar desde el Frontend

### Ejemplo de flujo completo:

```javascript
// 1. Solicitar URL de login de Microsoft
const response = await fetch('/api/auth/microsoft/login');
const { auth_url } = await response.json();

// 2. Redirigir al usuario a Microsoft
window.location.href = auth_url;

// 3. Después de autenticarse, el usuario vuelve al frontend
// El callback se maneja automáticamente

// 4. Sincronizar correos enviados
const syncResponse = await fetch('/api/sync/microsoft/sent', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const { count, emails } = await syncResponse.json();

// 5. Sincronizar correos de entrada
const inboxResponse = await fetch('/api/sync/microsoft/inbox', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

---

## Paso 5: Base de Datos

Se han añadido nuevos campos al modelo `User`:

```python
microsoft_id           # ID único de Microsoft
microsoft_email        # Email de Microsoft del usuario
access_token          # Token OAuth para Microsoft Graph
refresh_token         # Token para renovar access_token
token_expires_at      # Fecha de expiración del token
```

Para actualizar la base de datos (se hace automáticamente al iniciar):

```bash
python run.py
```

---

## Flujo Multi-usuario (Red Local)

### Usuario A (desde otra máquina de la red):

1. Abre: `http://tu-ip:5000` (donde tu-ip es la IP del servidor)
2. Hace click en "Conectar con Microsoft"
3. Inicia sesión con su cuenta de Microsoft
4. Sus tokens la se guardan en la BD bajo su usuario
5. Sincroniza SUS correos con `GET /api/sync/microsoft/sent`

### Usuario B (desde otra máquina):

1. Abre: `http://tu-ip:5000`
2. Hace click en "Conectar con Microsoft"
3. Inicia sesión con SU cuenta de Microsoft (diferente a A)
4. Sus tokens se guardan bajo su usuario (diferente)
5. Sincroniza SUS correos

**Resultado**: Cada usuario ve solo SUS correos, de forma segura y aislada.

---

## Seguridad

### Tokens:
- Los **access tokens** se guardan en la BD (deben estar protegidos)
- Se usan HTTPS en producción
- Los tokens expiran automáticamente y se renuevan
- Si el token no se puede renovar, el usuario debe reconectarse

### Aislamiento:
- Cada usuario solo puede acceder a sus propios correos
- La autenticación de Microsoft garantiza la identidad
- Los permisos solo permiten leer Mail (y User.Read básico)

---

## Solución de Problemas

### Error: "Usuario no autenticado con Microsoft"
→ El usuario necesita conectar su cuenta de Microsoft primero

### Error: "Refresh token inválido"
→ Los permisos en Azure AD no incluyen `offline_access`

### Error: "CORS error"
→ Asegurate que la URL de redirect URI en Azure AD coincida con tu dominio

### Tokens que no se renuevan
→ Verifica que `offline_access` esté en los permisos solicitados

---

## Cambios en el Código

### Nuevos archivos:
- `app/services/graph_service.py` - Servicio de Microsoft Graph API
- `app/routes/sync.py` - Rutas de sincronización

### Archivos modificados:
- `app/models/user.py` - Nuevos campos para Microsoft OAuth
- `app/routes/auth.py` - Nuevas rutas para Microsoft login
- `config.py` - Configuración de Microsoft Graph
- `app/__init__.py` - Registro de nuevas rutas
- `requirements.txt` - Nuevas dependencias (requests, msal)

---

## Próximos Pasos Opcionales

1. **Refresh token automático**: Implementar job para renovar tokens antes de que expiren
2. **Sincronización automática**: Programar sincronizaciones periódicas
3. **Caché de correos**: Guardar estado de última sincronización
4. **Carpetas personalizadas**: Permitir sincronizar cualquier carpeta de Outlook
5. **Búsqueda avanzada**: Filtros OData personalizados en Microsoft Graph

---

## Recursos Útiles

- [Microsoft Graph API Docs](https://learn.microsoft.com/es-es/graph/api/overview)
- [MSAL Python Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Azure AD App Registration](https://learn.microsoft.com/es-es/azure/active-directory/develop/quickstart-register-app)
