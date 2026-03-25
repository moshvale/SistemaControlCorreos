# Guía de Desarrollo - Sistema de Gestión de Correos

## Arquitectura del Proyecto

### Backend (Flask)
- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Autenticación**: JWT (JSON Web Tokens)
- **Hashing**: Bcrypt

### Frontend (Vue.js)
- **Framework**: Vue.js 3
- **HTTP Client**: Axios
- **CSS**: Bootstrap 5
- **Icons**: Font Awesome 6

## Estructura de Carpetas - Explicación Detallada

### Backend (`app/`)

#### `models/`
Contiene las definiciones de modelos de base de datos.

- **`database.py`**: 
  - `TimestampMixin`: Agrega campos `created_at` y `updated_at` a los modelos
  - Configuración de SQLAlchemy

- **`user.py`**:
  - Modelo User con métodos de hashing de contraseña
  - `set_password()`: Hashear contraseña con bcrypt
  - `check_password()`: Verificar contraseña
  - `to_dict()`: Serialización a JSON

- **`email.py`**:
  - Modelo Email para almacenar detalles de correos
  - Campos: subject, sender, recipients (JSON), sent_date, etc.
  - Índices compuestos para búsquedas eficientes

- **`audit_log.py`**:
  - Modelo AuditLog inmutable
  - Registra: user_id, email_id, action, cambios específicos
  - Clase ayudante `AuditedAction` para crear logs

#### `routes/`
Endpoints REST API.

- **`auth.py`**: Autenticación
  - `/register`: Registro de usuarios
  - `/login`: Inicio de sesión
  - `/refresh`: Refrescar token JWT
  - `/verify`: Verificar token
  - `/change-password`: Cambiar contraseña

- **`emails.py`**: Gestión de correos
  - CRUD de correos
  - Búsqueda y filtrado
  - Sincronización con Outlook
  - Exportación a CSV/PDF
  - Estadísticas del dashboard

- **`admin.py`**: Funciones administrativas
  - Gestión de usuarios
  - Visualización de logs de auditoría
  - Estadísticas del sistema

#### `services/`
Lógica de negocio y servicios externos.

- **`email_service.py`**:
  - `create_email()`: Crear correo con log de auditoría
  - `update_email()`: Actualizar correo
  - `delete_email()`: Eliminar correo
  - `get_user_emails()`: Obtener correos con paginación
  - `search_emails()`: Búsqueda de correos
  - `sync_from_outlook()`: Sincronizar desde Outlook

- **`outlook_service.py`**:
  - Integración con Microsoft Outlook
  - `connect()`: Conectar con Outlook
  - `get_sent_emails()`: Obtener correos enviados
  - `_extract_email_data()`: Extraer datos del correo

- **`export_service.py`**:
  - `to_csv()`: Exportar a CSV
  - `to_pdf()`: Exportar a PDF (usando ReportLab)

#### `utils/`
Funciones auxiliares y utilidades.

- **`auth.py`**:
  - `generate_tokens()`: Generar JWT tokens
  - `verify_token()`: Verificar token
  - `@token_required`: Decorador para proteger rutas
  - `@admin_required`: Decorador para rutas de admin
  - `get_client_ip()`: Obtener IP del cliente

### Frontend (`frontend/`)

#### `index.html`
Página principal - contiene:
- Navbar con navegación
- Container para las páginas
- Scripts y librerías externas

#### `css/style.css`
Estilos personalizados:
- Variables de color
- Componentes (cards, botones, formularios)
- Animaciones
- Diseño responsivo

#### `js/services/`

- **`auth.js`**:
  - `login()`: Autenticar usuario
  - `register()`: Registrar usuario
  - `logout()`: Cerrar sesión
  - `getCurrentUser()`: Obtener usuario actual
  - `refreshToken()`: Refrescar token

- **`api.js`**:
  - `setupAxios()`: Configurar interceptores
  - Métodos para cada endpoint:
    - `getEmails()`, `createEmail()`, `updateEmail()`, `deleteEmail()`
    - `searchEmails()`, `syncOutlook()`
    - `exportToCSV()`, `exportToPDF()`
    - `getDashboardStats()`, `getAdminStats()`

#### `js/pages/`

- **`login.js`**: Componente de login/registro
  - Form de login
  - Form de registro
  - Gestión de errores

- **`dashboard.js`**: Dashboard
  - Tarjetas de estadísticas
  - Gráficos de información
  - Acciones rápidas

- **`emails-list.js`**: Lista de correos
  - Tabla de correos con paginación
  - Filtros avanzados
  - Búsqueda
  - Selección múltiple
  - Modal de detalles

- **`email-form.js`**: Formulario de correo
  - Crear/editar correo
  - Múltiples destinatarios
  - Validación de formulario

- **`admin-panel.js`**: Panel de administración
  - Tabs para estadísticas, usuarios, auditoría
  - Tablas de datos
  - Filtrado

## Flujo de Autenticación

```
1. Usuario registra/inicia sesión
   ↓
2. Backend verifica credenciales
   ↓
3. Backend genera JWT tokens (access + refresh)
   ↓
4. Frontend almacena tokens en localStorage
   ↓
5. Cada petición incluye JWT en header Authorization
   ↓
6. Backend verifica token en decorador @token_required
   ↓
7. Si token expira, frontend usa refresh_token para obtener nuevo access_token
```

## Flujo de Creación de Correo

```
1. Usuario llena formulario y envía
   ↓
2. Frontend valida datos
   ↓
3. POST a /api/emails con datos
   ↓
4. Backend verifica autenticación
   ↓
5. EmailService.create_email() crea el registro
   ↓
6. Se crea log de auditoría automáticamente
   ↓
7. Base de datos se actualiza
   ↓
8. Respuesta JSON con el correo creado
   ↓
9. Frontend actualiza lista de correos
```

## Flujo de Sincronización Outlook

```
1. Usuario hace clic en "Sincronizar Outlook"
   ↓
2. Frontend envía POST a /api/emails/sync/outlook
   ↓
3. OutlookService.connect() abre Outlook
   ↓
4. OutlookService.get_sent_emails() obtiene correos
   ↓
5. Para cada correo:
   - Verifica si ya existe (por outlook_id)
   - Si no existe, crea nuevo registro
   - Crea log de auditoría
   ↓
6. Devuelve estadísticas (creados, duplicados, errores)
   ↓
7. Frontend muestra resultados
```

## Variables de Entorno

```bash
# Desarrollo
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DATABASE_URL=sqlite:///email_tracker.db

# Producción
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-fuerte
JWT_SECRET_KEY=tu-clave-jwt-fuerte
DATABASE_URL=postgresql://usuario:contra@host/db
```

## Comandos Útiles

### Crear Usuario Admin
```bash
python -c "
from app import create_app
from app.models import db, User
app = create_app()
app.app_context().push()
user = User(username='admin', email='admin@test.com', is_admin=True)
user.set_password('admin123')
db.session.add(user)
db.session.commit()
print('Admin creado!')
"
```

### Ejecutar en Modo Debug
```bash
FLASK_ENV=development FLASK_DEBUG=1 python run.py
```

### Generar Datos de Prueba
```bash
python -c "
from app import create_app
from app.models import db, User, Email
from datetime import datetime, timedelta
import json

app = create_app()
app.app_context().push()

# Crear usuario
user = User(username='test', email='test@test.com')
user.set_password('test123')
db.session.add(user)
db.session.flush()

# Crear emails de prueba
for i in range(10):
    email = Email(
        email_id=f'test_{i}',
        user_id=user.id,
        subject=f'Test email {i}',
        sender='test@gmail.com',
        recipients=json.dumps([{'email': 'dest@email.com', 'name': 'Destinatario'}]),
        sent_date=datetime.utcnow() - timedelta(days=i),
        importance='Normal'
    )
    db.session.add(email)

db.session.commit()
print('Datos de prueba creados!')
"
```

## Mejores Prácticas

### Backend
1. Siempre validar input en el backend
2. Usar try/except para operaciones de BD
3. Loguear errores importantes
4. Usar decoradores para validaciones comunes
5. Separar lógica en servicios

### Frontend
1. Usar componentes reutilizables
2. Validar antes de enviar datos
3. Manejar errores apropiadamente
4. Mostrar estados de carga/error
5. Usar localStorage para tokens
6. Refrescar datos cuando sea necesario

## Debugging

### Backend
```python
# En app/__init__.py agregar:
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.debug("Mensaje de debug")
```

### Frontend
```javascript
// En la consola del navegador:
// Ver tokens guardados
localStorage.getItem('access_token')

// Ver usuario actual
localStorage.getItem('user')

// Hacer petición de prueba
fetch('/api/health')
```

## Testing

### Petición de Prueba con Curl
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Obtener correos (reemplazar TOKEN)
curl http://localhost:5000/api/emails \
  -H "Authorization: Bearer TOKEN"
```

## Performance

### Optimizaciones Implementadas
1. **Índices de BD**: En user_id, sent_date, subject, sender
2. **Paginación**: Por defecto 20 items por página
3. **Lazy loading**: Relaciones con lazy='dynamic'
4. **Caché**: Estadísticas se cargan bajo demanda

### Mejoras Recomendadas
1. Agregar Redis para caché de estadísticas
2. Usar pagination en todas las listas
3. Agregar database connection pooling
4. Comprimir respuestas JSON
5. Minificar CSS/JS en producción

---

**Documento actualizado**: Marzo 2024
