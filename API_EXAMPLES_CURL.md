# API Microsoft Graph - Ejemplos con cURL

## Autenticación (Obtener Tokens)

### 1. Obtener URL de Login

```bash
curl -X GET http://localhost:5000/api/auth/microsoft/login

# Respuesta:
{
  "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=xxx&..."
}

# Copia esta URL en tu navegador, inicia sesión, aprueba permisos
# Te redirigirá a: http://localhost:5000/api/auth/callback/microsoft?code=...
# El backend manejará automáticamente el callback
```

### 2. Verificar Autenticación

```bash
# Usa el JWT token que recibiste del login
JWT_TOKEN="tu-jwt-token-aqui"

curl -X GET http://localhost:5000/api/auth/microsoft/status \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta:
{
  "is_microsoft_authenticated": true,
  "microsoft_email": "usuario@outlook.com",
  "microsoft_id": "xxxxx-xxxxx-xxxxx",
  "token_expires_at": "2024-03-26T10:30:00"
}
```

### 3. Desconectar Microsoft

```bash
curl -X POST http://localhost:5000/api/auth/microsoft/disconnect \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta:
{
  "message": "Cuenta de Microsoft desconectada exitosamente"
}
```

---

## Sincronización de Correos

### 1. Sincronizar Correos ENVIADOS

```bash
JWT_TOKEN="tu-jwt-token-aqui"

# Sin parámetros (por defecto 50)
curl -X GET http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer $JWT_TOKEN"

# Con límite personalizado
curl -X GET "http://localhost:5000/api/sync/microsoft/sent?limit=100" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta:
{
  "message": "Sincronización completada: 45/45 correos guardados",
  "count": 45,
  "total": 45,
  "errors": null,
  "emails": [
    {
      "subject": "Reunión de proyecto",
      "sender": "jefe@empresa.com",
      "sent_date": "2024-03-15T09:30:00",
      "importance": "High"
    },
    ...
  ]
}
```

### 2. Sincronizar ENTRADA

```bash
curl -X GET "http://localhost:5000/api/sync/microsoft/inbox?limit=50" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta: Similar a enviados
{
  "message": "Sincronización completada: 50/50 correos guardados",
  "count": 50,
  "total": 50,
  ...
}
```

### 3. Ver Estado de Sincronización

```bash
curl -X GET http://localhost:5000/api/sync/microsoft/status \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta:
{
  "is_authenticated": true,
  "microsoft_email": "usuario@outlook.com",
  "microsoft_id": "xxxxx",
  "token_expires_at": "2024-03-26T10:30:00",
  "email_count": 95,
  "last_sync": null
}
```

---

## Flujo Completo (Paso a Paso)

### 1. Login Local (Crear usuario en app)

```bash
# Si no tienes usuario local, crear primero
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "email": "juan@midominio.com",
    "password": "password123",
    "full_name": "Juan Pérez"
  }'

# Respuesta:
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "username": "juan",
    "email": "juan@midominio.com",
    "full_name": "Juan Pérez",
    ...
  }
}
```

### 2. Conectar Microsoft

```bash
# Obtener URL de Microsoft
curl http://localhost:5000/api/auth/microsoft/login | jq .auth_url

# Resultado:
https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...

# Abrir en navegador, hacer login con cuenta Microsoft
# Se redirige automáticamente al callback
# El servidor crea usuario O actualiza si existe

# El navegador muestra tokens JWT
```

### 3. Guardar tokens

```bash
# Después del login, guardar en localStorage o cookies:
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Guardar estos tokens para usar en siguientes requests
```

### 4. Sincronizar Correos

```bash
# Sincronizar enviados
curl -X GET http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer $JWT_TOKEN"

# Ver trabajo de sincronización en logs del servidor
# Los correos se guardan en la BD bajo el usuario

# Sincronizar entrada
curl -X GET http://localhost:5000/api/sync/microsoft/inbox \
  -H "Authorization: Bearer $JWT_TOKEN"

# Verificar estado
curl http://localhost:5000/api/sync/microsoft/status \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### 5. Obtener Correos Guardados

```bash
# Después de sincronizar, los correos se hallan en:
curl -X GET http://localhost:5000/api/emails \
  -H "Authorization: Bearer $JWT_TOKEN"

# Respuesta:
{
  "items": [
    {
      "id": 1,
      "subject": "Reunión importante",
      "sender": "manager@empresa.com",
      "sent_date": "2024-03-15T09:30:00",
      "importance": "High",
      "has_attachments": false
    },
    ...
  ],
  "total": 95,
  "page": 1,
  ...
}
```

---

## Manejo de Errores

### Token Expirado

```bash
curl -X GET http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHA..."

# Respuesta si expiró:
{
  "error": "Token inválido",
  "status": 401
}

# Solución: Hacer login nuevamente
```

### Usuario no Autenticado con Microsoft

```bash
curl -X GET http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer $JWT_TOKEN_DE_USUARIO_LOCAL"

# Respuesta:
{
  "error": "Usuario no autenticado con Microsoft. Por favor conéctate primero.",
  "status": 401
}

# Solución: Ir a GET /api/auth/microsoft/login
```

### Variables de Entorno No Configuradas

```bash
curl http://localhost:5000/api/auth/microsoft/login

# Respuesta si falta config:
{
  "error": "Error obteniendo URL de autenticación: ...",
  "status": 500
}

# Verifica .env tiene MICROSOFT_CLIENT_ID, CLIENT_SECRET, TENANT_ID
```

---

## Scripts Útiles

### Script: Sincronizar Automáticamente

```bash
#!/bin/bash
JWT="tu-token-aqui"
API="http://localhost:5000"

echo "🔄 Sincronizando enviados..."
curl -s "$API/api/sync/microsoft/sent?limit=100" \
  -H "Authorization: Bearer $JWT" | jq .count

echo "🔄 Sincronizando entrada..."
curl -s "$API/api/sync/microsoft/inbox?limit=100" \
  -H "Authorization: Bearer $JWT" | jq .count

echo "✅ Sincronización completada"
```

### Script: Verificar Estado

```bash
#!/bin/bash
JWT="tu-token-aqui"

curl -H "Authorization: Bearer $JWT" \
  http://localhost:5000/api/sync/microsoft/status | jq '{
    authenticated: .is_authenticated,
    email: .microsoft_email,
    emails_saved: .email_count,
    expires: .token_expires_at
  }'
```

---

## Debugging

### Ver todos los headers

```bash
curl -v -X GET http://localhost:5000/api/sync/microsoft/status \
  -H "Authorization: Bearer $JWT_TOKEN"

# -v muestra headers request y response
```

### Guardar respuesta en archivo

```bash
curl http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer $JWT_TOKEN" > response.json

# Analizar con jq
jq '.emails | length' response.json
```

### Medir tiempo de respuesta

```bash
time curl http://localhost:5000/api/sync/microsoft/sent \
  -H "Authorization: Bearer $JWT_TOKEN" > /dev/null

# Muestra cuánto tiempo tardó
```

---

## Referencias

- [Curl Docs](https://curl.se/docs/)
- [jq - JSON Processor](https://stedolan.github.io/jq/)
- [Microsoft Graph REST API](https://learn.microsoft.com/en-us/graph/api/overview)
- [MSAL OAuth2 Flow](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
