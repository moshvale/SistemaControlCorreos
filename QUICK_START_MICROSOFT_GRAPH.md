# 🚀 Inicio Rápido - Microsoft Graph API

## Pasos Inmediatos (Antes de usar)

### 1️⃣ Registra tu aplicación en Azure AD (5-10 minutos)

```
1. Ve a https://portal.azure.com
2. Inicia sesión con tu cuenta Microsoft
3. Ve a: Azure Active Directory → App registrations
4. Haz click en: "+ New registration"

Completa:
├── Name: "Email Tracker" (o el nombre que quieras)
├── Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
├── Redirect URI:
│   └── http://localhost:5000/api/auth/callback/microsoft
└── Haz click en "Register"
```

### 2️⃣ Configura Permisos (3 minutos)

En la página de tu app registrada:

```
API permissions → "+ Add a permission" → Microsoft Graph → Delegated permissions

Busca y selecciona:
✓ Mail.Read
✓ Mail.ReadWrite
✓ User.Read
✓ offline_access

Click en "Add permissions"
```

### 3️⃣ Obtén Credenciales (1 minuto)

**Para Client Secret:**
```
Certificates & secrets → "+ New client secret"
├── Description: "Email Tracker Secret"
├── Expires: "24 months"
└── Copia el Value (lo necesitarás en el paso 5)
```

**Para Client ID y Tenant ID:**
```
Vuelve a Overview y copia:
├── Application (client) ID = MICROSOFT_CLIENT_ID
└── Directory (tenant) ID = MICROSOFT_TENANT_ID
```

### 4️⃣ Crea archivo .env (1 minuto)

En la raíz del proyecto, crea `.env`:

```
FLASK_ENV=development
MICROSOFT_CLIENT_ID=tu-client-id-aqui
MICROSOFT_CLIENT_SECRET=tu-secret-aqui
MICROSOFT_TENANT_ID=tu-tenant-id-aqui
MICROSOFT_REDIRECT_URI=http://localhost:5000/api/auth/callback/microsoft
```

### 5️⃣ Instala paquetes (1 minuto)

```bash
pip install -r requirements.txt
```

Ya están instalados `requests` y `msal`, pero mejor actualizar todo.

### 6️⃣ Inicia la aplicación

```bash
python run.py
```

La app estará en: http://localhost:5000

---

## 🧪 Prueba Rápida

### Desde el navegador:

1. Ve a http://localhost:5000
2. Haz click en "Conectar con Microsoft"
3. Inicia sesión con tu cuenta Microsoft
4. Aprueba los permisos
5. ¡Listo! Ahora puedes sincronizar tus correos

### Desde la API (con curl):

```bash
# 1. Obtener login URL
curl http://localhost:5000/api/auth/microsoft/login

# Respuesta:
# {"auth_url": "https://login.microsoftonline.com/..."}

# 2. (Abrir la URL en navegador, hacer login)
# 3. Después de autenticarse, obtendrás tokens JWT

# 4. Sincronizar correos:
curl -H "Authorization: Bearer tu-jwt-token" \
     http://localhost:5000/api/sync/microsoft/sent
```

---

## 📚 Documentación Completa

- **MICROSOFT_GRAPH_SETUP.md** - Guía paso-a-paso detallada
- **MICROSOFT_GRAPH_FRONTEND_EXAMPLE.js** - Ejemplos de código
- **IMPLEMENTACION_COMPLETADA.md** - Resumen de cambios
- **README.md** - Documentación general

---

## ⚠️ ¿Problemas?

### "Error: Client ID inválido"
→ Verifica los valores en `.env` contra Azure Portal

### "Error: Redirect URI no coincide"
→ El MICROSOFT_REDIRECT_URI en `.env` debe coincidir EXACTAMENTE con Azure AD

### "Error: offline_access no permitido"
→ Agrega `offline_access` a los permisos en Azure AD

### "Error de CORS"
→ La app tiene CORS habilitado, pero verifica la URL

---

## 🎯 Flujo Típico de Usuario

```
Usuario A (cuenta: ana@empresa.com)
    ↓
    Abre: http://tu-ip:5000
    ↓
    Click en "Conectar con Microsoft"
    ↓
    Inicia sesión con ana@empresa.com
    ↓
    Aprueba permisos
    ↓
    Se redirige a Dashboard
    ↓
    Click en "Sincronizar Enviados"
    ↓
    ✅ Se guardan SOLO los correos de ana@
    ↓
    Click en "Sincronizar Entrada"
    ↓
    ✅ Se guardan SOLO los de entrada de ana@
```

---

## 📋 Checklist

- [ ] Registré app en Azure AD
- [ ] Agregué permisos (Mail.Read, User.Read, offline_access)
- [ ] Copié Client ID, Secret, Tenant ID
- [ ] Creé archivo `.env` con las credenciales
- [ ] Instalé dependencias (`pip install -r requirements.txt`)
- [ ] Inicié la aplicación (`python run.py`)
- [ ] Probé desde el navegador (http://localhost:5000)
- [ ] Conecté con Microsoft exitosamente
- [ ] Sincronicé correos exitosamente
- [ ] Verifiqué que cada usuario ve solo sus correos

---

## 🔒 Importante para Producción

Si vas a poner esto en producción:

1. Cambiar `FLASK_ENV=production`
2. Cambiar a HTTPS en MICROSOFT_REDIRECT_URI
3. Usar base de datos PostgreSQL en lugar de SQLite
4. **Encriptar los tokens en la BD** (importante!)
5. Usar variables de entorno (no hardcodear)
6. Implementar rate limiting
7. Agregar tests unitarios
8. Usar WSGI (Gunicorn/uWSGI)

---

**¡Ya estás listo para sincronizar correos de forma segura!** ✅
