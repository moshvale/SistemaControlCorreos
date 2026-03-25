"""
Rutas (paquete)
"""
from .auth import auth_bp
from .emails import email_bp
from .admin import admin_bp
from .sync import sync_bp

__all__ = ['auth_bp', 'email_bp', 'admin_bp', 'sync_bp']
