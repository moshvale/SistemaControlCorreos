"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///email_tracker.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Microsoft Graph Configuration (Azure AD OAuth2)
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')
    MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI', 'http://localhost:5000/api/auth/callback/microsoft')
    # Nota: 'offline_access' se agrega automáticamente por MSAL, no incluir aquí
    MICROSOFT_GRAPH_SCOPES = ['Mail.Read', 'Mail.ReadWrite', 'User.Read']
    
    # Microsoft Graph API endpoints
    MICROSOFT_GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    MICROSOFT_AUTH_ENDPOINT = 'https://login.microsoftonline.com'
    
    # Email Configuration
    EMAIL_BODY_SNIPPET_LENGTH = 200  # Caracteres del cuerpo del correo a guardar
    MAX_RECIPIENTS_DISPLAY = 10  # Máximo de destinatarios a mostrar
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB máximo
    
    # Pagination
    ITEMS_PER_PAGE = 20

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
