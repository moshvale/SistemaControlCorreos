"""
Modelo de Log de Auditoría - Inmutable e Autenticado
"""
from .database import db
from datetime import datetime
import json

class AuditLog(db.Model):
    """
    Modelo de Log de Auditoría para rastrear todos los cambios en correos
    Este modelo es esencialmente inmutable - no se actualiza, solo se crea
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Referencias
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False, index=True)
    
    # Tipo de operación
    action = db.Column(db.String(50), nullable=False, index=True)  # 'create', 'update', 'delete'
    
    # Detalles del cambio
    field_name = db.Column(db.String(100), nullable=True)  # Campo que se modificó
    old_value = db.Column(db.Text, nullable=True)  # Valor anterior
    new_value = db.Column(db.Text, nullable=True)  # Valor nuevo
    
    # Descripción legible
    description = db.Column(db.Text, nullable=True)
    
    # IP del usuario (si está disponible)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Índices para búsquedas frecuentes
    __table_args__ = (
        db.Index('idx_timestamp', 'timestamp'),
        db.Index('idx_email_timestamp', 'email_id', 'timestamp'),
        db.Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario
        
        Returns:
            dict: Representación en diccionario del log de auditoría
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'email_id': self.email_id,
            'action': self.action,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'description': self.description,
            'ip_address': self.ip_address
        }
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} - {self.timestamp}>'


class AuditedAction:
    """Clase ayudante para crear logs de auditoría"""
    
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    EXPORT = 'export'
    SYNC = 'sync'
    
    @staticmethod
    def log_action(user_id, email_id, action, description, 
                   field_name=None, old_value=None, new_value=None, ip_address=None):
        """
        Crea un log de auditoría
        
        Args:
            user_id (int): ID del usuario
            email_id (int): ID del correo
            action (str): Tipo de acción
            description (str): Descripción legible
            field_name (str, optional): Campo modificado
            old_value (str, optional): Valor anterior
            new_value (str, optional): Valor nuevo
            ip_address (str, optional): IP del usuario
            
        Returns:
            AuditLog: El log creado
        """
        log = AuditLog(
            user_id=user_id,
            email_id=email_id,
            action=action,
            field_name=field_name,
            old_value=str(old_value) if old_value else None,
            new_value=str(new_value) if new_value else None,
            description=description,
            ip_address=ip_address
        )
        db.session.add(log)
        return log
