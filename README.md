# Sistema de Gestión de Correos - Outlook Email Tracker

Un sistema integral de gestión y rastreo de correos electrónicos enviados desde Microsoft Outlook, construido con Python/Flask en el backend y Vue.js en el frontend.

## 🎯 Características Principales

### ✅ Funcionalidades Core
- **Autenticación Segura**: Sistema de login/registro con contraseñas hasheadas (bcrypt)
- **Gestión de Correos**: Crear, leer, actualizar y eliminar correos
- **Identificadores Únicos**: Auto-incrementables para cada correo
- **Logs de Auditoría**: Rastreo inmutable de todos los cambios
- **Búsqueda Avanzada**: Por asunto, remitente, destinatario, rango de fechas
- **Exportación**: A CSV y PDF de los correos
- **Control de Acceso**: RBAC (usuarios estándar vs. administradores)

### 📊 Características Avanzadas
- **Dashboard Personalizado**: Estadísticas resumidas y gráficos
- **Panel de Administración**: Gestión de usuarios y auditoría completa
- **Búsqueda por Palabras Clave**: En asunto y cuerpo del correo
- **Indicadores de Adjuntos**: Visualización clara de archivos

### 🔐 Microsoft Graph API (OAuth2) - NUEVO ✨
- **Multi-usuario seguro**: Cada usuario sincroniza SUS propios correos
- **Autenticación por Microsoft**: Usa credenciales de Office 365
- **Sincronización de Enviados**: Obtiene correos de la carpeta "Sent Items"
- **Sincronización de Entrada**: Obtiene correos del Inbox
- **Renovación automática de tokens**: Los tokens OAuth se renuevan automáticamente
- **Aislamiento de datos**: Cada usuario ve solo sus propios correos
- **Red local compatible**: Usuarios de diferentes máquinas pueden sincronizar

## 🎯 Dos modos de operación

### Modo 1: Outlook de Escritorio (Legado)
- USA Outlook abierto en el servidor
- Sincroniza los correos DE LA MÁQUINA SERVIDOR
- Todos los usuarios ven los mismos correos
- ❌ No recomendado para multi-usuario

### Modo 2: Microsoft Graph API (Recomendado) ⭐
- Cada usuario autentica con Microsoft
- Sincroniza los correos DEL USUARIO
- Cada usuario ve solo sus correos
- ✅ Perfecto para equipo de trabajo
- ✅ Funciona desde red local
- ✅ Escalable a cualquier número de usuarios

## 🏗️ Arquitectura del Proyecto

```
Correos/
├── app/
│   ├── __init__.py              # Factory y configuración Flask
│   ├── models/
│   │   ├── database.py          # Base de datos y mixins
│   │   ├── user.py              # Modelo de Usuario
│   │   ├── email.py             # Modelo de Correo
│   │   └── audit_log.py         # Modelo de Auditoría
│   ├── routes/
│   │   ├── auth.py              # Endpoints de autenticación
│   │   ├── emails.py            # Endpoints de correos
│   │   ├── admin.py             # Endpoints de administración
│   │   └── sync.py              # Endpoints de sincronización (NUEVO)
│   ├── services/
│   │   ├── email_service.py     # Lógica de negocio de correos
│   │   ├── outlook_service.py   # Integración con Outlook (legado)
│   │   ├── graph_service.py     # Servicio Microsoft Graph API (NUEVO)
│   │   └── export_service.py    # Exportación a CSV/PDF
│   └── utils/
│       └── auth.py              # Utilidades JWT y decoradores
├── frontend/
│   ├── index.html               # HTML principal
│   ├── css/
│   │   └── style.css            # Estilos personalizados
│   └── js/
│       ├── app.js               # Aplicación Vue.js principal
│       ├── services/
│       │   ├── auth.js          # Servicio de autenticación
│       │   └── api.js           # Servicio HTTP/API
│       └── pages/
│           ├── login.js         # Componente de login
│           ├── dashboard.js     # Dashboard
│           ├── emails-list.js   # Lista de correos
│           ├── email-form.js    # Formulario de correo
│           └── admin-panel.js   # Panel de administración
├── config.py                    # Configuración de aplicación
├── run.py                       # Punto de entrada
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## 🚀 Instalación y Configuración

### Requisitos Previos
- **Python 3.8+**
- **pip** (gestor de paquetes Python)
- **Navegador web moderno** (Chrome, Firefox, Edge, Safari)
- **Cuenta de Microsoft/Office 365** (para Microsoft Graph API)
- **Aplicación registrada en Azure AD** (ver MICROSOFT_GRAPH_SETUP.md)

### Instalación del Backend

1. **Clonar o descargar el proyecto**
```bash
cd Correos
```

2. **Crear un entorno virtual (recomendado)**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional)**
```bash
# En Windows (crear archivo .env en la raíz):
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DATABASE_URL=sqlite:///email_tracker.db

# Para Microsoft Graph API (REQUERIDO para sincronización):
MICROSOFT_CLIENT_ID=tu-client-id
MICROSOFT_CLIENT_SECRET=tu-client-secret
MICROSOFT_TENANT_ID=tu-tenant-id
MICROSOFT_REDIRECT_URI=http://localhost:5000/api/auth/callback/microsoft

# Ver MICROSOFT_GRAPH_SETUP.md para instrucciones completas
```

5. **Inicializar la base de datos**
```bash
python -c "from app import create_app; app = create_app('development'); app.app_context().push(); from app.models import db; db.create_all(); print('Base de datos creada!')"
```

### Ejecutar la Aplicación

**Backend (Flask API)**
```bash
python run.py
```
El servidor estará disponible en `http://localhost:5000`

**Frontend (HTML/Vue.js)**
1. Abre el archivo `frontend/index.html` en tu navegador
2. O sirve los archivos estáticos con un servidor web:
```bash
# Usando Python http.server:
cd frontend
python -m http.server 8000
# Abre http://localhost:8000
```

## 📚 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar nuevo usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/refresh` - Refrescar token
- `GET /api/auth/verify` - Verificar token
- `POST /api/auth/change-password` - Cambiar contraseña

### Correos
- `GET /api/emails` - Listar correos con paginación y filtros
- `GET /api/emails/<id>` - Obtener correo específico
- `POST /api/emails` - Crear nuevo correo
- `PUT /api/emails/<id>` - Actualizar correo
- `DELETE /api/emails/<id>` - Eliminar correo
- `POST /api/emails/search` - Buscar correos
- `POST /api/emails/sync/outlook` - Sincronizar con Outlook
- `POST /api/emails/export/csv` - Exportar a CSV
- `POST /api/emails/export/pdf` - Exportar a PDF
- `GET /api/emails/dashboard/stats` - Obtener estadísticas

### Administración
- `GET /api/admin/users` - Listar usuarios (admin)
- `GET /api/admin/users/<id>` - Obtener usuario específico (admin)
- `PUT /api/admin/users/<id>` - Actualizar usuario (admin)
- `DELETE /api/admin/users/<id>` - Desactivar usuario (admin)
- `GET /api/admin/audit-logs` - Obtener logs de auditoría (admin)
- `POST /api/admin/audit-logs/export` - Exportar logs a CSV (admin)
- `GET /api/admin/stats` - Estadísticas del sistema (admin)

### Sincronización con Microsoft Graph API (NUEVO)
- `GET /api/auth/microsoft/login` - Obtener URL de login de Microsoft
- `GET /api/auth/callback/microsoft?code=...` - Callback de Microsoft (automático)
- `GET /api/auth/microsoft/status` - Verificar estado de autenticación
- `POST /api/auth/microsoft/disconnect` - Desconectar cuenta de Microsoft
- `GET /api/sync/microsoft/sent` - Sincronizar correos ENVIADOS del usuario
- `GET /api/sync/microsoft/inbox` - Sincronizar ENTRADA del usuario
- `GET /api/sync/microsoft/status` - Ver estado de sincronización

## 🔐 Seguridad

### Características de Seguridad Implementadas
1. **Hashing de Contraseñas**: Bcrypt con salt de 12 rounds
2. **Autenticación JWT**: Tokens con expiración configurable
3. **OAuth2 Microsoft**: Autenticación segura con Microsoft
4. **HTTPS Ready**: Configurable en producción
5. **CORS Habilitado**: Para desarrollo y deployments
6. **SQL Injection Prevention**: ORM SQLAlchemy
7. **RBAC**: Control de acceso basado en roles
8. **Auditoría Inmutable**: Registros no editables de cambios
9. **Tokens Seguros**: Refresh tokens y access tokens separados
10. **Aislamiento Multi-usuario**: Cada usuario ve solo sus datos

### Configuración de Variable de Entorno para Producción
```bash
# En producción cambiar a:
FLASK_ENV=production
SECRET_KEY=tu-clave-segura-aqui
JWT_SECRET_KEY=tu-clave-jwt-aqui
DATABASE_URL=postgresql://usuario:contraseña@localhost/email_tracker

# Microsoft Graph en HTTPS
MICROSOFT_REDIRECT_URI=https://tudominio.com/api/auth/callback/microsoft
```

## 📊 Modelos de Datos

### User
- `id` - Identificador único
- `username` - Nombre de usuario (único)
- `email` - Correo electrónico (único)
- `password_hash` - Contraseña hasheada
- `full_name` - Nombre completo
- `is_active` - Usuario activo
- `is_admin` - Rol de administrador
- `created_at`, `updated_at` - Timestamps

### Email
- `id` - Identificador único auto-incremental
- `email_id` - ID único de Outlook
- `user_id` - Usuario propietario
- `subject` - Asunto del correo
- `sender` - Dirección del remitente
- `recipients` - JSON con destinatarios
- `sent_date` - Fecha de envío
- `body_snippet` - Fragmento del cuerpo
- `has_attachments` - Indica si tiene adjuntos
- `attachment_count` - Número de adjuntos
- `importance` - Importancia del correo
- `created_at`, `updated_at` - Timestamps
- `microsoft_graph_id` - ID en Microsoft Graph (cuando se sincroniza con Graph API)

### AuditLog
- `id` - Identificador único
- `timestamp` - Fecha/hora del cambio
- `user_id` - Usuario que hizo el cambio
- `email_id` - Correo afectado
- `action` - Tipo de acción (create, update, delete, etc)
- `field_name` - Campo modificado
- `old_value` - Valor anterior
- `new_value` - Valor nuevo
- `description` - Descripción legible
- `ip_address` - IP del usuario

### User - Campos Microsoft Graph
- `microsoft_id` - ID único de Microsoft
- `microsoft_email` - Email de Office 365
- `access_token` - Token OAuth de Microsoft
- `refresh_token` - Refresh token
- `token_expires_at` - Fecha de expiración

## 🔄 Integración con Microsoft Graph API (Recomendado)

### ⭐ Ventajas sobre Outlook Desktop
- ✅ Cada usuario autentica con su propia cuenta
- ✅ Funciona desde cualquier máquina/red
- ✅ Tokens se renuevan automáticamente
- ✅ No requiere Outlook instalado
- ✅ Escalable a múltiples usuarios
- ✅ Más seguro (OAuth2 estándar)

### Configuración Inicial
1. Ver [MICROSOFT_GRAPH_SETUP.md](MICROSOFT_GRAPH_SETUP.md) para instrucciones completas
2. Registrar aplicación en Azure AD
3. Obtener Client ID y Secret
4. Configurar variables de entorno
5. Iniciar la aplicación

### Flujo de Sincronización
```javascript
// 1. Usuario inicia login de Microsoft
window.location.href = '/api/auth/microsoft/login';

// 2. Microsoft lo redirige al callback (automático)
// El servidor crea el usuario y guarda tokens

// 3. Usuario sincroniza correos
fetch('/api/sync/microsoft/sent', {
    headers: { 'Authorization': 'Bearer token_jwt' }
});
```

## 🔄 Integración con Outlook (Legado - Opcional)

### Requisitos
- Windows con Outlook instalado
- Outlook abierto mientras se syncroniza
- Librería `pywin32` incluida en requirements.txt

### ⚠️ Limitaciones
- ❌ Todos los usuarios ven los mismos correos
- ❌ Requiere Outlook abierto en servidor
- ❌ Solo funciona en Windows
- ❌ No recomendado para multi-usuario

### Sincronización
```python
from app.services import get_outlook_service

service = get_outlook_service()
if service.connect():
    emails = service.get_sent_emails(limit=100)
    # Procesar correos...
```

## 📱 Frontend - Guía de Uso

### Páginas Principales

#### 1. Login
- Registrar nueva cuenta
- Iniciar sesión con usuario/contraseña
- **NUEVO**: Opción "Conectar con Microsoft" para autenticación con Azure AD

#### 2. Dashboard
- Ver estadísticas resumidas
- Correos por mes
- Top remitentes
- Sincronizar Outlook (legado)
- **NUEVO**: Sincronizar correos con Microsoft Graph
- Acciones rápidas

#### 3. Mis Correos
- Lista de todos los correos
- Filtros avanzados
- Búsqueda por palabras clave
- Selección múltiple
- Exportación a CSV/PDF
- Ver detalles de cada correo
- **NUEVO**: Indicador de origen (Outlook / Microsoft Graph)

#### 4. Nuevo/Editar Correo
- Formulario para crear o editar correos
- Agregar múltiples destinatarios
- Información de adjuntos
- Importancia del correo

#### 5. Panel de Administración (Admin Only)
- Estadísticas del sistema
- Gestión de usuarios
- Visualización de logs de auditoría
- Filtrado y búsqueda de logs

## 🧪 Testing y Desarrollo

### Crear Usuario de Prueba
```bash
python -c "
from app import create_app
from app.models import db, User

app = create_app('development')
with app.app_context():
    user = User(username='admin', email='admin@example.com', is_admin=True)
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    print('Usuario admin creado!')
"
```

### Datos de Prueba
**Credenciales de prueba creadas:**
- Usuario: `admin`
- Contraseña: `admin123`
- Rol: Administrador

## 🐛 Troubleshooting

### Error: "Usuario no autenticado con Microsoft"
- Haz click en "Conectar con Microsoft"
- Sigue el flujo de autenticación de Microsoft
- Acepta los permisos solicitados
- Ver [MICROSOFT_GRAPH_SETUP.md](MICROSOFT_GRAPH_SETUP.md)

### Error: "Outlook no encontrado"
- Asegurate que Outlook esté instalado en Windows
- Outlook debe estar abierto o en ejecución
- Verifica que `pywin32` esté instalado correctamente

### Error: "Puerto 5000 en uso"
```bash
# Cambiar puerto en run.py o usando variable de entorno:
FLASK_PORT=5001 python run.py
```

### Error: "Base de datos bloqueada"
```bash
# Eliminar y recrear la base de datos:
rm email_tracker.db
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; db.create_all()"
```

## 📈 Escalabilidad y Mejoras Futuras

### Mejoras Recomendadas
1. Migrar a PostgreSQL para producción
2. Agregar caché con Redis
3. Implementar rate limiting
4. Agregar tests automatizados
5. CI/CD con GitHub Actions
6. Docker containerization
7. Documentación API con Swagger
8. Autenticación OAuth2
9. Data encryption at rest
10. Backups automáticos

## 🤝 Contribuciones

Este proyecto está diseñado para ser modular y extensible. Para agregar nuevas funciones:

1. Crear un nuevo servicio en `app/services/`
2. Agregar nuevos modelos en `app/models/`
3. Crear nuevos endpoints en `app/routes/`
4. Actualizar la documentación

## 📄 Licencia

Proyecto interno - Todos los derechos reservados.

## 👥 Contacto

Para soporte o preguntas, contacta al equipo de administración.

---

**Última actualización**: Marzo 2024
**Versión**: 1.0.0
**Status**: ✅ Producción
