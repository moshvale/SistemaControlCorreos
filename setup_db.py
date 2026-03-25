from app import create_app
from app.models import db
from app.models.user import User

app = create_app()
with app.app_context():
    # Crear tablas
    db.create_all()
    print("✅ Base de datos creada exitosamente")
    
    # Crear usuario admin
    admin = User.query.filter_by(username='armando').first()
    if not admin:
        admin = User(
            username='armando',
            email='armando@admin.com',
            full_name='Armando Admin',
            is_admin=True,
            is_active=True
        )
        admin.set_password('5#2HRk@t')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario administrador creado:")
        print("   Usuario: armando")
        print("   Contraseña: 5#2HRk@t")
    else:
        print("⚠️  El usuario 'armando' ya existe")
