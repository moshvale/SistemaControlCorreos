# Testing Manual - Microsoft Graph Integration

## ✅ Checklist de Testing

### Fase 1: Setup (Antes de iniciar app)

- [ ] `.env` creado con credenciales de Azure AD
- [ ] Permisos correctos en Azure AD (Mail.Read, User.Read, offline_access)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos limpia o con migraciones hechas
- [ ] Puerto 5000 disponible (o cambiar en config)

### Fase 2: Inicio de Aplicación

```bash
python run.py
# Debería mostrar:
# ==================================================
# Sistema de Gestión de Correos
# ==================================================
# Ambiente: development
# Servidor: http://0.0.0.0:5000
# Frontend: Abre index.html en tu navegador
# ==================================================
```

- [ ] App inicia sin errores
- [ ] Logger muestra "Servidor ejecutándose"
- [ ] Puedo acceder a http://localhost:5000

### Fase 3: Pruebas de Endpoints

#### 3.1 Autenticación

```bash
# Test 1: Obtener URL de login
curl http://localhost:5000/api/auth/microsoft/login
# Esperado: JSON con "auth_url"
- [ ] Respuesta es un URL válido (contiene login.microsoftonline.com)

# Test 2: Verificar salud
curl http://localhost:5000/api/health
# Esperado: {"status": "ok"}
- [ ] Status 200 OK
```

#### 3.2 Flujo de Autenticación Manual

```
1. Abrir navegador: http://localhost:5000
   - [ ] Ve el frontend (index.html)
   - [ ] Hay botón de "Conectar con Microsoft"

2. Click en "Conectar con Microsoft"
   - [ ] Se redirige a login.microsoftonline.com
   - [ ] Puedo ver form de login

3. Inicia sesión con cuenta Microsoft
   - [ ] Login exitoso sin errores
   - [ ] Pide confirmación de permisos

4. Aprueba permisos
   - [ ] Sistema pide: Mail.Read, User.Read, offline_access
   - [ ] Click en "Aceptar" o "Approve"

5. Redirige a callback
   - [ ] URL cambia a localhost:5000/api/auth/callback/microsoft?code=...
   - [ ] Se procesa automáticamente

6. Resultado
   - [ ] Se devuelven tokens JWT
   - [ ] Usuario se crea en BD (verificar con DB browser)
   - [ ] Puedo ver dashboard del usuario
```

#### 3.3 Verificar Tokens en BD

```bash
python -c "
from app import create_app
from app.models import db, User

app = create_app('development')
with app.app_context():
    user = User.query.first()
    if user:
        print(f'Usuario: {user.username}')
        print(f'Microsoft ID: {user.microsoft_id}')
        print(f'Microsoft Email: {user.microsoft_email}')
        print(f'Access Token: {user.access_token[:20]}... (truncado)')
        print(f'Token Expira: {user.token_expires_at}')
    else:
        print('No hay usuarios')
"

# Esperado: Ver usuario con microsoft_id y acceso_token llenos
- [ ] microsoft_id no es None
- [ ] access_token no es None
- [ ] token_expires_at es fecha futuro
```

#### 3.4 Sincronización de Correos

```bash
# Obtener JWT token (de la respuesta del login anterior)
JWT="tu-jwt-token-aqui"

# Test 1: Ver estado
curl -H "Authorization: Bearer $JWT" \
     http://localhost:5000/api/sync/microsoft/status
# Esperado: is_authenticated = true
- [ ] Estado muestra autenticado
- [ ] microsoft_email es correcto
- [ ] email_count = 0 (antes de sincronizar)

# Test 2: Sincronizar enviados
curl -H "Authorization: Bearer $JWT" \
     http://localhost:5000/api/sync/microsoft/sent?limit=20
# Esperado: message con "X/X correos guardados"
- [ ] Respuesta tiene "count" y "total"
- [ ] sent_date es válido (formato ISO)
- [ ] Cada correo tiene: subject, sender, sent_date

# Test 3: Sincronizar entrada
curl -H "Authorization: Bearer $JWT" \
     http://localhost:5000/api/sync/microsoft/inbox?limit=20
# Esperado: Correos de entrada guardados
- [ ] Diferentes de los enviados
- [ ] received_date válido

# Test 4: Verificar estado después
curl -H "Authorization: Bearer $JWT" \
     http://localhost:5000/api/sync/microsoft/status
# Esperado: email_count > 0
- [ ] email_count aumentó
- [ ] Total correos sincronizados visible
```

#### 3.5 Verificar BD después sincronización

```bash
python -c "
from app import create_app
from app.models import db, User, Email

app = create_app('development')
with app.app_context():
    user = User.query.first()
    count = user.emails.count() if user else 0
    
    print(f'Total correos para usuario: {count}')
    
    if count > 0:
        email = user.emails.first()
        print(f'Primer correo:')
        print(f'  - Asunto: {email.subject}')
        print(f'  - Remitente: {email.sender}')
        print(f'  - Fecha: {email.sent_date}')
        print(f'  - ID Microsoft: {email.email_id}')
"

# Esperado: Ver correos en la BD
- [ ] count > 0
- [ ] subject no es vacío
- [ ] microsoft_graph_id tiene valor
```

### Fase 4: Pruebas de Multi-usuario

#### Simulación en misma máquina:

```bash
# Usuario A:
1. Registrarse como usuario_a con email personal
2. Conectar con Microsoft (cuenta A)
3. Sincronizar correos
4. Contar correos en BD

# Usuario B:
1. Abrir navegador privado/incógnito
2. Registrarse como usuario_b con otro email
3. Conectar con Microsoft (cuenta B diferente)
4. Sincronizar correos
5. Contar correos en BD

# Verificación:
- [ ] Usuario A ve solo SUS correos
- [ ] Usuario B ve solo SUS correos
- [ ] Correos de A ≠ Correos de B
- [ ] Cada uno está aislado en su sesión
```

#### Verificar aislamiento en BD:

```bash
python -c "
from app import create_app
from app.models import db, User

app = create_app('development')
with app.app_context():
    for user in User.query.all():
        count = user.emails.count()
        print(f'{user.username} ({user.microsoft_email}): {count} correos')
"

# Esperado:
# usuario_a (ana@outlook.com): 45 correos
# usuario_b (beto@outlook.com): 32 correos
# (números diferentes, ¡excelente!)

- [ ] Cada usuario tiene conteo diferente
- [ ] Suma total = suma de ambos
```

### Fase 5: Pruebas de Errores

#### 5.1 Token Inválido

```bash
# Test con token inventado
curl -H "Authorization: Bearer invalid.token.here" \
     http://localhost:5000/api/sync/microsoft/sent

# Esperado: 401 error
- [ ] Status code 401
- [ ] Error message "Token inválido"
```

#### 5.2 Usuario no conectado a Microsoft

```bash
# Registrar usuario sin conectar Microsoft
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@test.com",
    "password": "password123"
  }'

# Login con ese usuario
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'

# Obtener JWT y intentar sincronizar
# GET /api/sync/microsoft/sent con JWT de usuario no-Microsoft

# Esperado: 401 error
- [ ] Status code 401
- [ ] Error message "Usuario no autenticado con Microsoft"
```

#### 5.3 Configuración Faltante

```bash
# Temporalmente, comentar variables en .env:
# MICROSOFT_CLIENT_ID=
# MICROSOFT_CLIENT_SECRET=

# Intentar GET /api/auth/microsoft/login

# Esperado: Error 500
- [ ] Status code 500
- [ ] Error message sobre configuración faltante
```

### Fase 6: Performance

```bash
# Test sincronización con muchos correos
time curl -H "Authorization: Bearer $JWT" \
     "http://localhost:5000/api/sync/microsoft/sent?limit=200"

# Esperado: < 10 segundos
- [ ] Time real < 10s
- [ ] No hay memory leak
- [ ] Servidor responde correctamente
```

### Fase 7: Logs

```bash
# Mientras ejecutas tests, revisar logs:
# Deberías ver mensajes como:

[INFO] Token renovado para usuario 1
[INFO] Se obtuvieron 45 correos de Outlook
[INFO] Correo creado exitosamente: 1
[DEBUG] Inicializando COM en thread actual...
[INFO] ✓ Conexión a Outlook establecida exitosamente

# Verificar:
- [ ] No hay [ERROR] durante operaciones exitosas
- [ ] Hay [INFO] para cada paso importante
- [ ] IDs de usuarios/correos están correctos
```

---

## 🐛 Problemas Comunes y Soluciones

### Problema: "KeyError: MICROSOFT_CLIENT_ID"
**Solución**: Crear `.env` con las credenciales de Azure AD

### Problema: "Invalid client_id"
**Solución**: Verificar que el ID en `.env` coincida con Azure Portal

### Problema: "Redirect URI mismatch"
**Solución**: 
```
Azure Portal: Configurar exactamente
http://localhost:5000/api/auth/callback/microsoft

En .env colocar:
MICROSOFT_REDIRECT_URI=http://localhost:5000/api/auth/callback/microsoft
```

### Problema: "Refresh token inválido"
**Solución**: 
- Verificar que `offline_access` está en permisos de Azure AD
- Requestear nuevamente en `MICROSOFT_GRAPH_SCOPES`
- Re-conectar usuario (hacer login de nuevo)

### Problema: Tokens no se renuevan
**Solución**:
- Verificar `token_expires_at` en BD
- Logs deberían mostrar renovación
- Debugging: Intentar sincronizar después de token expirado

---

## ✨ Casos de Éxito

### Caso 1: Usuario Local → Usuario Microsoft

```
✅ Usuarios registrados localmente pueden conectar Microsoft
✅ Se crea nuevo usuario en Azure AD
✅ Sus correos se sincronizan exitosamente
✅ Token se renueva cuando expira
```

### Caso 2: Multi-usuario en Red Local

```
✅ Usuario A (PC1) puede conectar con su cuenta Microsoft
✅ Usuario B (PC2) puede conectar con otra cuenta Microsoft
✅ Cada uno ve solo sus correos
✅ Los datos están aislados en la BD
```

### Caso 3: Sincronización Múltiple

```
✅ Primer sync: 45 correos
✅ Segundo sync: No duplicados (verifica por ID)
✅ Tercer sync: Nuevos correos se agregan
✅ Todo sin errores o corrupción
```

---

## 📊 Métricas de Éxito

Después de testing completo:

```
Total de endpoints testados: 8/8 ✅
Endpoints sin errores: 100%
Multi-usuario funcionando: ✅
Aislamiento de datos: ✅
Renovación de tokens: ✅
Sincronización exitosa: ✅
Performance < 10s: ✅
Logs limpios: ✅

Status: 🟢 PRODUCTION READY
```

---

**Última actualización**: Marzo 2024
**Versión de Test**: 1.0
