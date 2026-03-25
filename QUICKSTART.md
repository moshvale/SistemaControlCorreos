# Guía de Inicio Rápido

## 🚀 Primeros Pasos

### 1. Instalar Dependencias

```bash
# Crear ambiente virtual (recomendado)
python -m venv venv

# Activar ambiente (Windows)
venv\Scripts\activate

# Instalar paquetes
pip install -r requirements.txt
```

### 2. Ejecutar el Backend

```bash
python run.py
```

Deberías ver:
```
==================================================
Sistema de Gestión de Correos
==================================================
Ambiente: development
Servidor: http://0.0.0.0:5000
Frontend: Abre index.html en tu navegador
==================================================
```

### 3. Abrir el Frontend

En tu navegador, abre:
```
frontend/index.html
```

O si quieres servir archivos estáticos:
```bash
cd frontend
python -m http.server 8000
```

Luego accede a: `http://localhost:8000`

### 4. Cuenta de Prueba

Usa estas credenciales:
- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Administrador

O crea una nueva cuenta en la pantalla de registro.

## 📝 Primeros Pasos en la Aplicación

1. **Login**: Inicia sesión con tus credenciales
2. **Dashboard**: Verás una página principal con estadísticas
3. **Sincronizar Outlook**: Haz clic en "Sincronizar Outlook" para importar correos
4. **Ver Correos**: Ve a "Mis Correos" para ver la lista
5. **Buscar/Filtrar**: Usa los filtros avanzados para buscar correos
6. **Exportar**: Selecciona correos y exporta a CSV o PDF
7. **Administración**: Si eres admin, accede al panel de administración

## 🔧 Configuración Adicional

### Cambiar Puerto
```bash
FLASK_PORT=5001 python run.py
```

### Usar PostgreSQL (Producción)
```bash
# Instalar postgresql
pip install psycopg2-binary

# Configurar variable de entorno
set DATABASE_URL=postgresql://usuario:password@localhost/email_tracker

# Ejecutar
python run.py
```

### Debug Mode
```bash
set FLASK_ENV=development
set FLASK_DEBUG=1
python run.py
```

## 📊 Características Clave a Probar

### ✅ Crear Correo Manualmente
1. Dashboard → "Nuevo Correo"
2. Completa los campos
3. Agrega múltiples destinatarios
4. Guarda

### ✅ Sincronizar Outlook
1. Dashboard → "Sincronizar Outlook"
2. Se importarán los correos enviados
3. Ver contador de "creados" vs "duplicados"

### ✅ Buscar y Filtrar
1. Mis Correos
2. Usa la búsqueda por keyword
3. O usa filtros por fecha, remitente, etc.

### ✅ Exportar Datos
1. Selecciona uno o más correos
2. Elige "Exportar CSV" o "Exportar PDF"
3. Descarga automática

### ✅ Panel Admin (solo admin)
1. Ve a "Administración"
2. Ve estadísticas del sistema
3. Gestiona usuarios
4. Revisa logs de auditoría

## 🐛 Solución de Problemas

### "Module not found" Error
```bash
# Asegúrate de estar en la carpeta correcta
cd Correos

# Y que el ambiente virtual esté activado
venv\Scripts\activate

# Reinstala dependencias
pip install --upgrade -r requirements.txt
```

### "Port 5000 already in use"
```bash
# Usa otro puerto
FLASK_PORT=5001 python run.py
```

### "Outlook not found"
- Asegúrate que Outlook esté instalado en Windows
- Outlook puede necesitar estar abierto
- Reinstala pywin32: `pip install --upgrade pywin32`

### "Database locked"
```bash
# Elimina y recrea
del email_tracker.db
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; db.create_all()"
```

## 📚 Documentación Completa

Para documentación más detallada, ver:
- **README.md** - Descripción general y características
- **DEVELOPMENT.md** - Guía técnica para desarrolladores
- **API Endpoints** - Ver sección en README.md

## ✨ Consejos

1. Asegúrate de usar un ambiente virtual para aislar dependencias
2. Guarda tus tokens JWT seguros (ya se guardan en localStorage)
3. Para producción, cambia las claves secretas en variables de entorno
4. Usa HTTPS en producción
5. Haz backups periódicos de la base de datos
6. Revisa los logs de auditoría regularmente

---

¡Listo! Ya tienes la aplicación funcionando. 🎉

Para preguntas o problemas, revisa los archivos de documentación.
