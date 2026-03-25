"""
Modelo de Usuario con autenticación segura
"""
from .database import db, TimestampMixin
import bcrypt
from datetime import datetime

class User(TimestampMixin, db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Microsoft Graph OAuth2 Integration
    microsoft_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    microsoft_email = db.Column(db.String(120), nullable=True)
    access_token = db.Column(db.Text, nullable=True)  # Token OAuth de Microsoft
    refresh_token = db.Column(db.Text, nullable=True)  # Refresh token para renovar
    token_expires_at = db.Column(db.DateTime, nullable=True)  # Fecha de expiración del token
    
    # Relaciones
    emails = db.relationship('Email', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hashea y almacena la contraseña de forma segura usando bcrypt
        
        Args:
            password (str): Contraseña en texto plano
        """
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """
        Verifica si la contraseña coincide con el hash almacenado
        
        Args:
            password (str): Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_emails=False):
        """
        Convierte el objeto a diccionario
        
        Args:
            include_emails (bool): Si incluir emails del usuario
            
        Returns:
            dict: Representación en diccionario del usuario
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
        if include_emails:
            data['email_count'] = self.emails.count()
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
