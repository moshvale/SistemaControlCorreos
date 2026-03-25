"""
Modelo de Correo Electrónico
"""
from .database import db, TimestampMixin
from datetime import datetime
from .user import User

class Email(TimestampMixin, db.Model):
    """Modelo de Correo Electrónico"""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(255), nullable=False, index=True)  # ID único de Outlook
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Información del correo
    subject = db.Column(db.String(500), nullable=False, index=True)
    sender = db.Column(db.String(255), nullable=False, index=True)
    recipients = db.Column(db.Text, nullable=False)  # JSON string de destinatarios
    sent_date = db.Column(db.DateTime, nullable=False, index=True)
    body_snippet = db.Column(db.Text, nullable=True)
    has_attachments = db.Column(db.Boolean, default=False)
    attachment_count = db.Column(db.Integer, default=0)
    
    # Metadatos
    outlook_class = db.Column(db.String(100), nullable=True)  # Clase de Outlook (IPM.Note, etc)
    importance = db.Column(db.String(20), default='Normal')  # Low, Normal, High
    
    # Control de cambios
    is_synced = db.Column(db.Boolean, default=True)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    audit_logs = db.relationship('AuditLog', backref='email', lazy='dynamic', cascade='all, delete-orphan')
    
    # Índices compuestos para búsquedas frecuentes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'email_id', name='uq_user_email_id'),  # Email único per usuario
        db.Index('idx_user_sent_date', 'user_id', 'sent_date'),
        db.Index('idx_user_subject', 'user_id', 'subject'),
        db.Index('idx_user_sender', 'user_id', 'sender'),
    )
    
    def to_dict(self, include_audit=False, include_creator=False):
        """
        Convierte el objeto a diccionario
        
        Args:
            include_audit (bool): Si incluir los logs de auditoría
            include_creator (bool): Si incluir información del usuario que creó/modificó
            
        Returns:
            dict: Representación en diccionario del correo
        """
        import json
        try:
            recipients_list = json.loads(self.recipients)
        except:
            recipients_list = []
        
        data = {
            'id': self.id,
            'email_id': self.email_id,
            'user_id': self.user_id,
            'subject': self.subject,
            'sender': self.sender,
            'recipients': recipients_list,
            'sent_date': self.sent_date.isoformat(),
            'body_snippet': self.body_snippet,
            'has_attachments': self.has_attachments,
            'attachment_count': self.attachment_count,
            'importance': self.importance,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_audit:
            data['audit_logs'] = [log.to_dict() for log in self.audit_logs]
        
        if include_creator:
            # Obtener el último cambio de auditoría
            from app.models.audit_log import AuditLog
            last_audit = self.audit_logs.order_by(AuditLog.timestamp.desc()).first()
            if last_audit:
                creator_user = User.query.filter_by(id=last_audit.user_id).first()
                if creator_user:
                    data['created_by_user'] = creator_user.username
                    data['created_by_email'] = creator_user.email
                    data['last_modified_by'] = last_audit.user_id
                    data['last_modified_date'] = last_audit.timestamp.isoformat()
        
        return data
    
    def __repr__(self):
        return f'<Email {self.id}: {self.subject[:50]}>'
