"""
Servicio de gestión de correos electrónicos
"""
from app.models import db, Email, AuditLog, AuditedAction
from datetime import datetime
import json
from flask import current_app

class EmailService:
    """Servicio para gestionar operaciones de correos"""
    
    @staticmethod
    def create_email(user_id, subject, sender, recipients, sent_date, 
                    body_snippet=None, has_attachments=False, attachment_count=0,
                    importance='Normal', outlook_id=None, ip_address=None):
        """
        Crea un nuevo registro de correo en la base de datos
        
        Args:
            user_id (int): ID del usuario propietario del correo
            subject (str): Asunto del correo
            sender (str): Dirección de correo del remitente
            recipients (list o str): Lista de destinatarios
            sent_date (datetime): Fecha de envío
            body_snippet (str, optional): Fragmento del cuerpo
            has_attachments (bool): Si tiene archivos adjuntos
            attachment_count (int): Número de adjuntos
            importance (str): Importancia del correo
            outlook_id (str, optional): ID único de Outlook
            ip_address (str, optional): IP del usuario
            
        Returns:
            Email: El objeto Email creado o None si hay error
        """
        try:
            # Convertir recipients a JSON si es lista
            if isinstance(recipients, list):
                recipients_json = json.dumps(recipients)
            else:
                recipients_json = recipients
            
            # Crear ID único para el correo si no se proporciona
            if not outlook_id:
                outlook_id = f"{user_id}_{sent_date.timestamp()}_{hash(subject) % 10000}"
            
            # Verificar que no exista un correo con el mismo outlook_id para ESTE usuario
            existing = Email.query.filter_by(user_id=user_id, email_id=outlook_id).first()
            if existing:
                current_app.logger.info(f"Correo {outlook_id} ya existe para usuario {user_id}, ignorando duplicado")
                return existing
            
            email = Email(
                email_id=outlook_id,
                user_id=user_id,
                subject=subject,
                sender=sender,
                recipients=recipients_json,
                sent_date=sent_date,
                body_snippet=body_snippet,
                has_attachments=has_attachments,
                attachment_count=attachment_count,
                importance=importance,
                outlook_class='IPM.Note'
            )
            
            db.session.add(email)
            db.session.flush()  # Obtener el ID sin hacer commit aún
            
            # Crear log de auditoría
            AuditedAction.log_action(
                user_id=user_id,
                email_id=email.id,
                action=AuditedAction.CREATE,
                description=f"Correo creado: {subject}",
                ip_address=ip_address
            )
            
            db.session.commit()
            current_app.logger.info(f"Correo creado exitosamente: {email.id}")
            
            return email
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creando correo: {str(e)}")
            return None
    
    @staticmethod
    def update_email(email_id, user_id, updates, ip_address=None):
        """
        Actualiza un correo existente
        
        NOTA: Con dashboard compartido, cualquier usuario puede editar cualquier correo
        El parámetro user_id se usa solo para el log de auditoría
        
        Args:
            email_id (int): ID del correo a actualizar
            user_id (int): ID del usuario que solicita la actualización (para auditoría)
            updates (dict): Diccionario con campos a actualizar
            ip_address (str, optional): IP del usuario
            
        Returns:
            Email: El objeto actualizado o None si hay error
        """
        try:
            # Buscar el correo sin filtro de usuario (dashboard compartido)
            email = Email.query.filter_by(id=email_id).first()
            if not email:
                current_app.logger.warning(f"Correo {email_id} no encontrado para actualización")
                return None
            
            # Campos permitidos para actualizar
            allowed_fields = ['subject', 'recipients', 'body_snippet', 'importance']
            
            for field, value in updates.items():
                if field not in allowed_fields:
                    continue
                
                old_value = getattr(email, field)
                setattr(email, field, value)
                
                # Crear log de auditoría para cada cambio
                AuditedAction.log_action(
                    user_id=user_id,
                    email_id=email_id,
                    action=AuditedAction.UPDATE,
                    field_name=field,
                    old_value=old_value,
                    new_value=value,
                    description=f"Campo '{field}' actualizado",
                    ip_address=ip_address
                )
            
            db.session.commit()
            current_app.logger.info(f"Correo {email_id} actualizado por usuario {user_id}")
            
            return email
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error actualizando correo: {str(e)}")
            return None
            current_app.logger.info(f"Correo {email_id} actualizado")
            
            return email
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error actualizando correo: {str(e)}")
            return None
    
    @staticmethod
    def delete_email(email_id, user_id, ip_address=None):
        """
        Elimina un correo (eliminación lógica con log de auditoría)
        
        NOTA: Con dashboard compartido, cualquier usuario puede eliminar cualquier correo
        El parámetro user_id se usa solo para el log de auditoría
        
        Args:
            email_id (int): ID del correo a eliminar
            user_id (int): ID del usuario que solicita la eliminación (para auditoría)
            ip_address (str, optional): IP del usuario
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            # Buscar el correo sin filtro de usuario (dashboard compartido)
            email = Email.query.filter_by(id=email_id).first()
            if not email:
                current_app.logger.warning(f"Correo {email_id} no encontrado para eliminación")
                return False
            
            # Crear log de auditoría antes de eliminar
            AuditedAction.log_action(
                user_id=user_id,
                email_id=email_id,
                action=AuditedAction.DELETE,
                old_value=email.subject,
                description=f"Correo eliminado: {email.subject}",
                ip_address=ip_address
            )
            
            db.session.delete(email)
            db.session.commit()
            current_app.logger.info(f"Correo {email_id} eliminado por usuario {user_id}")
            
            return True
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error eliminando correo: {str(e)}")
            return False
    
    @staticmethod
    def get_email(email_id, user_id=None):
        """
        Obtiene un correo por ID
        
        Args:
            email_id (int): ID del correo
            user_id (int, optional): Si se proporciona, verifica que el correo pertenezca al usuario
            
        Returns:
            Email or None: El objeto Email o None si no existe
        """
        query = Email.query.filter_by(id=email_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def get_user_emails(user_id, page=1, per_page=20, filters=None):
        """
        Obtiene los correos de un usuario con paginación y filtros opcionales
        
        Args:
            user_id (int): ID del usuario
            page (int): Número de página
            per_page (int): Items por página
            filters (dict, optional): Diccionario con filtros (subject, sender, recipient, date_from, date_to)
            
        Returns:
            tuple: (lista de correos, total de items)
        """
        query = Email.query.filter_by(user_id=user_id)
        
        if filters:
            if filters.get('subject'):
                query = query.filter(Email.subject.ilike(f"%{filters['subject']}%"))
            
            if filters.get('sender'):
                query = query.filter(Email.sender.ilike(f"%{filters['sender']}%"))
            
            if filters.get('recipient'):
                query = query.filter(Email.recipients.ilike(f"%{filters['recipient']}%"))
            
            if filters.get('date_from'):
                query = query.filter(Email.sent_date >= filters['date_from'])
            
            if filters.get('date_to'):
                query = query.filter(Email.sent_date <= filters['date_to'])
            
            if filters.get('has_attachments') is not None:
                query = query.filter_by(has_attachments=filters['has_attachments'])
        
        # Ordenar por fecha descendente
        query = query.order_by(Email.sent_date.desc())
        
        total = query.count()
        emails = query.paginate(page=page, per_page=per_page).items
        
        return emails, total
    
    @staticmethod
    def get_all_emails(page=1, per_page=20, filters=None):
        """
        Obtiene TODOS los correos de todos los usuarios (para dashboard compartido)
        
        Args:
            page (int): Número de página
            per_page (int): Items por página
            filters (dict, optional): Diccionario con filtros (subject, sender, recipient, date_from, date_to)
            
        Returns:
            tuple: (lista de correos, total de items)
        """
        query = Email.query
        
        if filters:
            if filters.get('subject'):
                query = query.filter(Email.subject.ilike(f"%{filters['subject']}%"))
            
            if filters.get('sender'):
                query = query.filter(Email.sender.ilike(f"%{filters['sender']}%"))
            
            if filters.get('recipient'):
                query = query.filter(Email.recipients.ilike(f"%{filters['recipient']}%"))
            
            if filters.get('date_from'):
                query = query.filter(Email.sent_date >= filters['date_from'])
            
            if filters.get('date_to'):
                query = query.filter(Email.sent_date <= filters['date_to'])
            
            if filters.get('has_attachments') is not None:
                query = query.filter_by(has_attachments=filters['has_attachments'])
        
        # Ordenar por fecha descendente
        query = query.order_by(Email.sent_date.desc())
        
        total = query.count()
        emails = query.paginate(page=page, per_page=per_page).items
        
        return emails, total
    
    @staticmethod
    def search_emails(user_id, search_term, page=1, per_page=20):
        """
        Busca correos por término en asunto, remitente o destinatarios
        
        Args:
            user_id (int): ID del usuario
            search_term (str): Término de búsqueda
            page (int): Número de página
            per_page (int): Items por página
            
        Returns:
            tuple: (lista de correos, total de items)
        """
        from sqlalchemy import or_
        
        query = Email.query.filter_by(user_id=user_id).filter(
            or_(
                Email.subject.ilike(f"%{search_term}%"),
                Email.sender.ilike(f"%{search_term}%"),
                Email.recipients.ilike(f"%{search_term}%"),
                Email.body_snippet.ilike(f"%{search_term}%")
            )
        )
        
        total = query.count()
        emails = query.order_by(Email.sent_date.desc()).paginate(
            page=page, per_page=per_page
        ).items
        
        return emails, total
    
    @staticmethod
    def search_all_emails(search_term, page=1, per_page=20):
        """
        Busca en TODOS los correos por término (Dashboard Compartido)
        
        Args:
            search_term (str): Término de búsqueda
            page (int): Número de página
            per_page (int): Items por página
            
        Returns:
            tuple: (lista de correos, total de items)
        """
        from sqlalchemy import or_
        
        query = Email.query.filter(
            or_(
                Email.subject.ilike(f"%{search_term}%"),
                Email.sender.ilike(f"%{search_term}%"),
                Email.recipients.ilike(f"%{search_term}%"),
                Email.body_snippet.ilike(f"%{search_term}%")
            )
        )
        
        total = query.count()
        emails = query.order_by(Email.sent_date.desc()).paginate(
            page=page, per_page=per_page
        ).items
        
        return emails, total
    
    @staticmethod
    def sync_from_outlook(user_id, outlook_service, ip_address=None, limit=1):
        """
        Sincroniza correos desde Outlook a la base de datos
        
        Args:
            user_id (int): ID del usuario
            outlook_service: Instancia del servicio de Outlook
            ip_address (str, optional): IP del usuario
            limit (int): Número máximo de correos a sincronizar (default: 1)
            
        Returns:
            dict: Estadísticas de la sincronización
        """
        stats = {
            'created': 0,
            'duplicates': 0,
            'errors': 0
        }
        
        try:
            emails_from_outlook = outlook_service.get_sent_emails(limit=limit)
            
            for email_data in emails_from_outlook:
                try:
                    # Verificar si ya existe para ESTE usuario
                    existing = Email.query.filter_by(
                        user_id=user_id,
                        email_id=email_data['outlook_id']
                    ).first()
                    
                    if existing:
                        stats['duplicates'] += 1
                        continue
                    
                    # Crear nuevo correo
                    email = EmailService.create_email(
                        user_id=user_id,
                        subject=email_data['subject'],
                        sender=email_data['sender'],
                        recipients=email_data['recipients'],
                        sent_date=email_data['sent_date'],
                        body_snippet=email_data.get('body_snippet'),
                        has_attachments=email_data['has_attachments'],
                        attachment_count=email_data['attachment_count'],
                        importance=email_data['importance'],
                        outlook_id=email_data['outlook_id'],
                        ip_address=ip_address
                    )
                    
                    if email:
                        stats['created'] += 1
                    else:
                        stats['errors'] += 1
                
                except Exception as e:
                    current_app.logger.error(f"Error sincronizando correo: {str(e)}")
                    stats['errors'] += 1
                    continue
            
            # Log de sincronización general
            if stats['created'] > 0:
                AuditedAction.log_action(
                    user_id=user_id,
                    email_id=user_id,  # Usar user_id como placeholder
                    action=AuditedAction.SYNC,
                    description=f"Sincronización completada: {stats['created']} correos creados",
                    ip_address=ip_address
                )
                db.session.commit()
            
            return stats
        
        except Exception as e:
            current_app.logger.error(f"Error en sincronización: {str(e)}")
            return stats
