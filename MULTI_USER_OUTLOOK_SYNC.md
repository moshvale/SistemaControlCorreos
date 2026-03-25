# 📋 Guía: Acceso a Correos desde Múltiples Equipos en Red Local

## Problema Identificado

Cuando múltiples usuarios acceden desde diferentes computadoras en la red local y sincronizan Outlook, **solo se sincronizan los correos de la cuenta del servidor**, porque la sincronización usaba COM (Outlook de escritorio instalado en el servidor).

## ✅ Solución: Microsoft Graph OAuth2 por Usuario

Cada usuario debe autenticar su **propia cuenta de Microsoft** usando OAuth2. Así, cada uno sincronizará solo sus correos.

---

## 🔧 Configuración Requerida

### 1️⃣ Credenciales de Microsoft Graph (Una sola vez en el servidor)

Ya debes tener en tu `.env` o `config.py`:
```python
MICROSOFT_CLIENT_ID = "tu-client-id"
MICROSOFT_CLIENT_SECRET = "tu-client-secret"
MICROSOFT_TENANT_ID = "common"
MICROSOFT_REDIRECT_URI = "http://tu-ip-local:5000/api/auth/callback/microsoft"
```

**⚠️ IMPORTANTE:** El `REDIRECT_URI` debe ser accesible desde los otros equipos. Si el servidor está en `192.168.1.100`, usa:
```
http://192.168.1.100:5000/api/auth/callback/microsoft
```

### 2️⃣ Flujo de Autenticación para Cada Usuario

#### Opción A: Desde otro equipo (Recomendado)

1. Usuario entra a la app desde su computadora: `http://192.168.1.100:5000`
2. Se autentica con usuario/contraseña local
3. En el Dashboard, hace clic en **"Conectar Outlook"** o **"Autenticar con Microsoft"**
4. Se abre ventana de Microsoft para que inicie sesión con su cuenta
5. Después, cuando sincroniza, usa su propia cuenta de correo

#### Opción B: Desde el servidor

```bash
# Abrir navegador y acceder a:
http://localhost:5000/api/auth/microsoft/login

# Esto devuelve una URL que debes copiar al navegador
# Luego accedes al callback que obtiene los tokens
```

---

## 📊 Flujo Técnico

```
Usuario en PC2
    ↓
Login en app (192.168.1.100:5000) → Autentica con usuario/contraseña
    ↓
Clic en "Conectar Outlook"
    ↓
GET /api/auth/microsoft/login → Devuelve URL de Microsoft
    ↓
Redirige a Microsoft login
    ↓
Usuario autoriza con su cuenta Microsoft
    ↓
Callback: POST /api/auth/callback/microsoft?code=XXX
    ↓
Servidor intercambia code por access_token + refresh_token
    ↓
Tokens se guardan en DB asociados a ese usuario
    ↓
Cuando sincroniza: POST /api/emails/sync/outlook
    ↓
Sistema detecta que tiene tokens de Microsoft
    ↓
Usa GraphService con TOKENS DEL USUARIO, no del servidor
    ↓
Descarga correos de la cuenta del usuario
    ↓
Se guardan en DB filtrados por user_id
```

---

## 🚀 Implementación

### Backend (Ya implementado)

- ✅ `POST /api/auth/microsoft/login` - Devuelve URL para autenticarse
- ✅ `GET /api/auth/callback/microsoft?code=XXX` - Procesa autenticación
- ✅ `POST /api/emails/sync/outlook` - Ahora prioriza GraphService (si usuario está autenticado) sobre COM

### Frontend (NECESITA AGREGAR)

Necesita botón en dashboard para iniciar flujo OAuth:

```html
<button onclick="authenticateMicrosoft()">Conectar Outlook</button>
```

```javascript
async function authenticateMicrosoft() {
    try {
        const response = await axios.get('/api/auth/microsoft/login');
        const authUrl = response.data.auth_url;
        
        // Abrir en ventana emergente o nueva pestaña
        const width = 500;
        const height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        
        window.open(authUrl, 'microsoft_auth', 
            `width=${width},height=${height},left=${left},top=${top}`);
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## 📋 Estados de Sincronización

Después de esta implementación:

### Escenario 1: Usuario autenticado con Microsoft
```
Usuario: "juan"
Microsoft Autenticado: ✅ Sí (juan@outlook.com)
Sincronizar → Descarga correos de juan@outlook.com
```

### Escenario 2: Usuario NO autenticado con Microsoft (Fallback)
```
Usuario: "maria"
Microsoft Autenticado: ❌ No
Fallback: Intenta usar Outlook COM del servidor
Resultado: Solo descarga si Outlook está abierto en el servidor
✓ Funciona: Solo si está en el mismo equipo del servidor
✗ No funciona: Desde otros equipos
```

---

## 🔄 Refresh Automático de Tokens

Los tokens de Microsoft expiran cada ~60 minutos. El sistema automáticamente:

1. Detecta si el token está próximo a expirar
2. Usa el `refresh_token` para obtener uno nuevo
3. Guarda el nuevo token en la BD

No requiere intervención del usuario.

---

## 🐛 Troubleshooting

### "Usuario no autenticado con Microsoft"
- **Solución:** Clic en "Conectar Outlook" y completa autenticación

### "Error: redirect_uri_mismatch"
- **Verificar:** En config.py, `MICROSOFT_REDIRECT_URI` debe ser la IP/puerto correctos
- **Ejemplo correcto:** `http://192.168.1.100:5000/api/auth/callback/microsoft`

### "Sincroniza correos del servidor, no del usuario"
- **Causa:** Usuario no autenticado con Microsoft, usando fallback COM
- **Solución:** Autenticar primero con Microsoft

### "No puedo acceder desde otro equipo"
- **Verificar:** Firewall permite puerto 5000
- **Ejecutar:** `New-NetFirewallRule -DisplayName "Allow Flask 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow`

---

## 📈 Próximos Pasos

1. ✅ Reinicia el servidor para que la nueva ruta funcione
2. ⏳ Agrega botón "Conectar Outlook" en el frontend (dashboard.js)
3. 👥 Cada usuario desde su equipo: autentica su propia cuenta
4. 🔄 Todos pueden sincronizar sus propios correos

---

## API Reference

### 1. Obtener URL de autenticación
```
GET /api/auth/microsoft/login
Response: { "auth_url": "https://login.microsoftonline.com/..." }
```

### 2. Callback automático
```
GET /api/auth/callback/microsoft?code=XXX&session_state=YYY
Response: { "user": {...}, "tokens": {...}, "microsoft_email": "..." }
```

### 3. Sincronizar
```
POST /api/emails/sync/outlook
Params: ?limit=50&source=auto
Response: { "message": "...", "count": N, "source": "microsoft_graph" }
```

### 4. Ver estado de autenticación
```
GET /api/auth/microsoft/status
Response: { "authenticated": true/false, "microsoft_email": "..." }
```

---

**Versión:** 1.0 | **Fecha:** 19/Mar/2026 | **Estado:** ✅ Implementado
