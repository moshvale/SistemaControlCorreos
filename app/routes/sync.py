"""
Rutas para sincronización de correos con Microsoft Graph
"""
from flask import Blueprint, request, jsonify
from app.models import User, Email, db
from app.services import GraphService, EmailService
from app.utils import token_required, get_client_ip
from datetime import datetime
from flask import current_app

sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')


@sync_bp.route('/microsoft/sent', methods=['GET'])
@token_required
def sync_microsoft_sent():
    """
    Sincroniza los correos ENVIADOS del usuario desde Microsoft Graph
    Requiere que el usuario esté autenticado con Microsoft
    
    Query params:
        - limit: Máximo número de correos a obtener (default: 50)
        - skip: Número de correos a saltar para paginación (default: 0)
    
    Returns:
        dict: Correos sincronizados
    """
    try:
        user = request.current_user
        
        # Verificar que el usuario esté autenticado con Microsoft
        if not user.access_token or not user.microsoft_id:
            return jsonify({
                'error': 'Usuario no autenticado con Microsoft. Por favor conéctate primero.'
            }), 401
        
        # Crear servicio de Graph con tokens del usuario
        graph_service = GraphService(user)
        
        # Obtener correos enviados
        limit = request.args.get('limit', 50, type=int)
        emails = graph_service.get_sent_emails(limit=limit)
        
        if not emails:
            return jsonify({
                'message': 'No se encontraron correos enviados',
                'count': 0,
                'emails': []
            }), 200
        
        # Guardar correos en base de datos
        saved_count = 0
        errors = []
        
        for email_data in emails:
            try:
                # Crear registro en base de datos
                email = EmailService.create_email(
                    user_id=user.id,
                    subject=email_data['subject'],
                    sender=email_data['sender'],
                    recipients=email_data['recipients'],
                    sent_date=email_data['sent_date'],
                    body_snippet=email_data['body_snippet'],
                    has_attachments=email_data['has_attachments'],
                    importance=email_data['importance'],
                    outlook_id=email_data['microsoft_graph_id'],  # Usar ID de Microsoft Graph
                    ip_address=get_client_ip()
                )
                
                if email:
                    saved_count += 1
            except Exception as e:
                errors.append({
                    'subject': email_data.get('subject'),
                    'error': str(e)
                })
                current_app.logger.error(f"Error guardando correo {email_data.get('subject')}: {str(e)}")
        
        return jsonify({
            'message': f'Sincronización completada: {saved_count}/{len(emails)} correos guardados',
            'count': saved_count,
            'total': len(emails),
            'errors': errors if errors else None,
            'emails': [
                {
                    'subject': e['subject'],
                    'sender': e['sender'],
                    'sent_date': e['sent_date'].isoformat(),
                    'importance': e['importance']
                } for e in emails[:10]  # Devolver info de primeros 10
            ]
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error sincronizando correos enviados: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error en sincronización: {str(e)}'}), 500


@sync_bp.route('/microsoft/inbox', methods=['GET'])
@token_required
def sync_microsoft_inbox():
    """
    Sincroniza los correos de ENTRADA del usuario desde Microsoft Graph
    Requiere que el usuario esté autenticado con Microsoft
    
    Query params:
        - limit: Máximo número de correos a obtener (default: 50)
    
    Returns:
        dict: Correos sincronizados de entrada
    """
    try:
        user = request.current_user
        
        # Verificar que el usuario esté autenticado con Microsoft
        if not user.access_token or not user.microsoft_id:
            return jsonify({
                'error': 'Usuario no autenticado con Microsoft. Por favor conéctate primero.'
            }), 401
        
        # Crear servicio de Graph con tokens del usuario
        graph_service = GraphService(user)
        
        # Obtener correos de entrada
        limit = request.args.get('limit', 50, type=int)
        emails = graph_service.get_inbox_emails(limit=limit)
        
        if not emails:
            return jsonify({
                'message': 'No se encontraron correos de entrada',
                'count': 0,
                'emails': []
            }), 200
        
        # Guardar correos en base de datos
        saved_count = 0
        errors = []
        
        for email_data in emails:
            try:
                # Crear registro en base de datos
                email = EmailService.create_email(
                    user_id=user.id,
                    subject=email_data['subject'],
                    sender=email_data['sender'],
                    recipients=email_data['recipients'],
                    sent_date=email_data['received_date'],
                    body_snippet=email_data['body_snippet'],
                    has_attachments=email_data['has_attachments'],
                    importance=email_data['importance'],
                    outlook_id=email_data['microsoft_graph_id'],
                    ip_address=get_client_ip()
                )
                
                if email:
                    saved_count += 1
            except Exception as e:
                errors.append({
                    'subject': email_data.get('subject'),
                    'error': str(e)
                })
                current_app.logger.error(f"Error guardando correo {email_data.get('subject')}: {str(e)}")
        
        return jsonify({
            'message': f'Sincronización completada: {saved_count}/{len(emails)} correos guardados',
            'count': saved_count,
            'total': len(emails),
            'errors': errors if errors else None,
            'emails': [
                {
                    'subject': e['subject'],
                    'sender': e['sender'],
                    'received_date': e['received_date'].isoformat(),
                    'importance': e['importance']
                } for e in emails[:10]
            ]
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error sincronizando correos de entrada: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error en sincronización: {str(e)}'}), 500


@sync_bp.route('/microsoft/status', methods=['GET'])
@token_required
def sync_status():
    """
    Obtiene el estado de sincronización y configuración de Microsoft Graph
    
    Returns:
        dict: Información de autenticación y estado
    """
    try:
        user = request.current_user
        
        is_authenticated = bool(user.access_token and user.microsoft_id)
        
        return jsonify({
            'is_authenticated': is_authenticated,
            'microsoft_email': user.microsoft_email if is_authenticated else None,
            'microsoft_id': user.microsoft_id if is_authenticated else None,
            'token_expires_at': user.token_expires_at.isoformat() if user.token_expires_at else None,
            'email_count': user.emails.count(),
            'last_sync': None  # TODO: Implementar tracking de última sincronización
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estado: {str(e)}'}), 500
