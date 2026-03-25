"""
Rutas de gestión de correos electrónicos
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from app.models import Email, db, User, AuditLog, AuditedAction
from app.services import EmailService, get_outlook_service
from app.services import ExportService
from app.utils import token_required, get_client_ip
from datetime import datetime
import json
import io

email_bp = Blueprint('emails', __name__, url_prefix='/api/emails')

@email_bp.route('/debug/test', methods=['GET'])
def debug_test():
    """
    Ruta de debug para ver qué se está recibiendo
    """
    try:
        return jsonify({
            'message': 'Debug endpoint funcionando',
            'status': 'ok'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@email_bp.route('/debug/create', methods=['POST'])
@token_required
def debug_create():
    """
    Debug endpoint para POST de creación de emails
    """
    try:
        from flask import current_app
        data = request.get_json()
        current_app.logger.error(f"DEBUG: Datos recibidos = {data}")
        current_app.logger.error(f"DEBUG: Usuario = {request.current_user.username}")
        
        return jsonify({
            'message': 'Debug POST funcionando',
            'received_data': data,
            'user': request.current_user.username
        }), 200
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"DEBUG POST Error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@email_bp.route('', methods=['GET'])
@token_required
def get_emails():
    """
    Obtiene los correos del usuario autenticado con paginación y filtros
    
    Query parameters:
        page: Número de página (default: 1)
        per_page: Items por página (default: 20)
        subject: Filtro por asunto
        sender: Filtro por remitente
        recipient: Filtro por destinatario
        date_from: Fecha desde (YYYY-MM-DD)
        date_to: Fecha hasta (YYYY-MM-DD)
        has_attachments: true/false
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Construir filtros
        filters = {}
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        if request.args.get('sender'):
            filters['sender'] = request.args.get('sender')
        if request.args.get('recipient'):
            filters['recipient'] = request.args.get('recipient')
        if request.args.get('date_from'):
            try:
                filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
            except:
                pass
        if request.args.get('date_to'):
            try:
                filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
            except:
                pass
        if request.args.get('has_attachments'):
            filters['has_attachments'] = request.args.get('has_attachments').lower() == 'true'
        
        emails, total = EmailService.get_user_emails(
            request.current_user.id, 
            page=page, 
            per_page=per_page,
            filters=filters
        )
        
        return jsonify({
            'emails': [email.to_dict(include_creator=True) for email in emails],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo correos: {str(e)}'}), 500

@email_bp.route('/shared/all', methods=['GET'])
@token_required
def get_all_emails_shared():
    """
    Obtiene TODOS los correos de TODOS los usuarios (Dashboard Compartido)
    Cualquier usuario autenticado puede ver todos los correos
    
    Query parameters:
        page: Número de página (default: 1)
        per_page: Items por página (default: 20)
        subject: Filtro por asunto
        sender: Filtro por remitente
        recipient: Filtro por destinatario
        date_from: Fecha desde (YYYY-MM-DD)
        date_to: Fecha hasta (YYYY-MM-DD)
        has_attachments: true/false
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Construir filtros
        filters = {}
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        if request.args.get('sender'):
            filters['sender'] = request.args.get('sender')
        if request.args.get('recipient'):
            filters['recipient'] = request.args.get('recipient')
        if request.args.get('date_from'):
            try:
                filters['date_from'] = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
            except:
                pass
        if request.args.get('date_to'):
            try:
                filters['date_to'] = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
            except:
                pass
        if request.args.get('has_attachments'):
            filters['has_attachments'] = request.args.get('has_attachments').lower() == 'true'
        
        # Obtener TODOS los correos (no filtrar por usuario)
        emails, total = EmailService.get_all_emails(
            page=page, 
            per_page=per_page,
            filters=filters
        )
        
        return jsonify({
            'emails': [email.to_dict(include_creator=True) for email in emails],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo correos: {str(e)}'}), 500

@email_bp.route('/<int:email_id>', methods=['GET'])
@token_required
def get_email(email_id):
    """
    Obtiene un correo específico por ID
    
    NOTA: Con dashboard compartido, cualquier usuario puede ver cualquier correo
    """
    try:
        # Obtener el correo sin filtro de usuario (dashboard compartido)
        email = EmailService.get_email(email_id)
        
        if not email:
            return jsonify({'error': 'Correo no encontrado'}), 404
        
        return jsonify({
            'email': email.to_dict(include_audit=True)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo correo: {str(e)}'}), 500

@email_bp.route('', methods=['POST'])
@token_required
def create_email():
    """
    Crea un nuevo correo manualmente
    
    Body JSON:
        {
            "subject": "Asunto",
            "sender": "remitente@example.com",
            "recipients": [{"email": "dest@example.com", "name": "Destianatrio"}],
            "sent_date": "2024-03-18T10:30:00",
            "body_snippet": "Contenido...",
            "has_attachments": false,
            "attachment_count": 0,
            "importance": "Normal"
        }
    """
    try:
        from flask import current_app
        data = request.get_json()
        print(f"\n=== CREATE EMAIL ===")
        print(f"Datos recibidos: {data}")
        
        if not all(k in data for k in ['subject', 'sender', 'recipients', 'sent_date']):
            print("ERROR: Falta campos requeridos")
            return jsonify({
                'error': 'Campos requeridos: subject, sender, recipients, sent_date'
            }), 400
        
        try:
            # Parsear la fecha (soporta ISO format y datetime-local)
            sent_date_str = data['sent_date']
            print(f"Parsing fecha: {sent_date_str}")
            if 'T' in sent_date_str and '+' not in sent_date_str and 'Z' not in sent_date_str:
                # Formato datetime-local: 2024-03-18T10:30
                sent_date = datetime.fromisoformat(sent_date_str)
            else:
                # Formato ISO con timezone
                sent_date = datetime.fromisoformat(sent_date_str.replace('Z', '+00:00'))
            print(f"Fecha parseada OK: {sent_date}")
        except Exception as e:
            print(f"ERROR parsing fecha: {str(e)}")
            return jsonify({'error': f'Formato de fecha inválido. Use formato ISO: {str(e)}'}), 400
        
        print(f"Creando correo para usuario {request.current_user.id}")
        email = EmailService.create_email(
            user_id=request.current_user.id,
            subject=data['subject'],
            sender=data['sender'],
            recipients=data['recipients'],
            sent_date=sent_date,
            body_snippet=data.get('body_snippet'),
            has_attachments=data.get('has_attachments', False),
            attachment_count=data.get('attachment_count', 0),
            importance=data.get('importance', 'Normal'),
            ip_address=get_client_ip()
        )
        
        print(f"Email retornado: {email}")
        if not email:
            print("ERROR: EmailService.create_email retornó None")
            return jsonify({'error': 'Error creando correo'}), 500
        
        print(f"Correo creado OK: {email.id}")
        return jsonify({
            'message': 'Correo creado exitosamente',
            'email': email.to_dict()
        }), 201
    
    except Exception as e:
        print(f"ERROR en create_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error creando correo: {str(e)}'}), 500

@email_bp.route('/<int:email_id>', methods=['PUT'])
@token_required
def update_email(email_id):
    """
    Actualiza un correo existente
    
    Body JSON:
        {
            "subject": "Nuevo asunto",
            "recipients": [...],
            "body_snippet": "...",
            "importance": "High"
        }
    """
    try:
        data = request.get_json()
        
        email = EmailService.update_email(
            email_id,
            request.current_user.id,
            data,
            ip_address=get_client_ip()
        )
        
        if not email:
            return jsonify({'error': 'Correo no encontrado'}), 404
        
        return jsonify({
            'message': 'Correo actualizado exitosamente',
            'email': email.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error actualizando correo: {str(e)}'}), 500

@email_bp.route('/<int:email_id>', methods=['DELETE'])
@token_required
def delete_email(email_id):
    """
    Elimina un correo
    """
    try:
        success = EmailService.delete_email(
            email_id,
            request.current_user.id,
            ip_address=get_client_ip()
        )
        
        if not success:
            return jsonify({'error': 'Correo no encontrado'}), 404
        
        return jsonify({
            'message': 'Correo eliminado exitosamente'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error eliminando correo: {str(e)}'}), 500

@email_bp.route('/search', methods=['POST'])
@token_required
def search_emails():
    """
    Busca correos por término (solo del usuario autenticado)
    
    Body JSON:
        {
            "search_term": "término",
            "page": 1,
            "per_page": 20
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'search_term' not in data:
            return jsonify({'error': 'search_term requerido'}), 400
        
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        emails, total = EmailService.search_emails(
            request.current_user.id,
            data['search_term'],
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'emails': [email.to_dict() for email in emails],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error buscando correos: {str(e)}'}), 500

@email_bp.route('/shared/search', methods=['POST'])
@token_required
def search_shared_emails():
    """
    Busca en TODOS los correos por término (Dashboard Compartido)
    Cualquier usuario autenticado puede buscar en todos los correos
    
    Body JSON:
        {
            "search_term": "término",
            "page": 1,
            "per_page": 20
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'search_term' not in data:
            return jsonify({'error': 'search_term requerido'}), 400
        
        page = data.get('page', 1)
        per_page = data.get('per_page', 20)
        
        # Buscar en TODOS los correos (no filtrar por usuario)
        emails, total = EmailService.search_all_emails(
            data['search_term'],
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'emails': [email.to_dict(include_creator=True) for email in emails],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error buscando correos compartidos: {str(e)}'}), 500

@email_bp.route('/sync/outlook', methods=['POST'])
@token_required
def sync_from_outlook():
    """
    Sincroniza correos desde Outlook/Microsoft Graph
    
    OPCIÓN 1 (Recomendado): Usa credenciales de Microsoft Graph del usuario
        - Requiere que el usuario esté autenticado con Microsoft (/api/auth/microsoft/login)
        - Funciona desde cualquier computadora en la red
        
    OPCIÓN 2 (Fallback): Usa Outlook de escritorio instalado en el servidor
        - Sincroniza solo correos del usuario del servidor
        - Requiere Outlook ABIERTO en el servidor
    
    Query parameters:
        - limit: Número máximo de correos a sincronizar (default: 1 para sincronizar solo el último)
        - source: 'graph' (defecto) o 'outlook' para forzar origen
    """
    try:
        from flask import current_app
        from app.services import GraphService
        
        user = request.current_user
        limit = request.args.get('limit', 1, type=int)
        source = request.args.get('source', 'auto').lower()
        
        current_app.logger.info(f"[SYNC] Iniciando sincronización para usuario {user.username} (source={source})")
        
        # ========== OPCIÓN 1: Microsoft Graph (Recomendado) ==========
        if source in ['auto', 'graph'] and user.access_token and user.microsoft_id:
            try:
                current_app.logger.info(f"[SYNC] Usando Microsoft Graph OAuth2 para {user.username}")
                graph_service = GraphService(user)
                
                # Obtener correos de entrada
                emails = graph_service.get_inbox_emails(limit=limit)
                
                if not emails:
                    return jsonify({
                        'message': 'No se encontraron correos en entrada',
                        'count': 0,
                        'emails': []
                    }), 200
                
                # Guardar correos en base de datos
                saved_count = 0
                errors = []
                
                for email_data in emails:
                    try:
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
                
                current_app.logger.info(f"[SYNC] Completada con Graph: {saved_count}/{len(emails)} correos guardados")
                
                return jsonify({
                    'message': f'Sincronización exitosa desde Microsoft Graph: {saved_count}/{len(emails)} correos',
                    'count': saved_count,
                    'total': len(emails),
                    'source': 'microsoft_graph',
                    'errors': errors if errors else None,
                    'user_email': user.microsoft_email
                }), 200
                
            except Exception as e:
                current_app.logger.warning(f"[SYNC] GraphService falló, intentando fallback: {str(e)}")
                if source == 'graph':  # Si se forzó graph, no continuar
                    return jsonify({
                        'error': f'Error usando Microsoft Graph: {str(e)}',
                        'hint': 'Asegúrate de haber autenticado con /api/auth/microsoft/login'
                    }), 400
                # Continuar con Outlook fallback
        
        # ========== OPCIÓN 2: Outlook de escritorio (Fallback) ==========
        if source in ['auto', 'outlook']:
            outlook_service = None
            try:
                current_app.logger.info(f"[SYNC] Usando Outlook COM para {user.username}")
                outlook_service = get_outlook_service()
                
                if not outlook_service.connect():
                    current_app.logger.error("[SYNC] Falló la conexión a Outlook")
                    return jsonify({
                        'error': 'No se pudo conectar a Outlook ni a Microsoft Graph.',
                        'details': 'Para usar desde otros equipos: /api/auth/microsoft/login',
                        'details_local': 'Para Outlook local: Asegúrate de que esté ABIERTO',
                        'help': 'Ejecuta: python fix_outlook.py'
                    }), 400
                
                current_app.logger.info(f"[SYNC] Sincronizando {limit} correo(s) desde Outlook COM")
                
                stats = EmailService.sync_from_outlook(
                    user.id,
                    outlook_service,
                    ip_address=get_client_ip(),
                    limit=limit
                )
                
                current_app.logger.info(f"[SYNC] Completada con Outlook: {stats}")
                
                return jsonify({
                    'message': f'Sincronización exitosa desde Outlook: {stats}',
                    'stats': stats,
                    'source': 'outlook_com',
                    'warning': '⚠️ Usando Outlook local. Para acceso remoto desde otros equipos, usa: /api/auth/microsoft/login'
                }), 200
                
            except Exception as e:
                current_app.logger.error(f"[SYNC] Error Outlook COM: {str(e)}", exc_info=True)
                return jsonify({
                    'error': f'Error sincronizando con Outlook: {str(e)}',
                    'hint': 'Para sincronizar desde otros equipos, auténtica primero con Microsoft: POST /api/auth/microsoft/login'
                }), 500
            finally:
                if outlook_service:
                    outlook_service.disconnect()
        
        # Si llegó aquí, fuente no reconocida
        return jsonify({
            'error': f'Fuente de sincronización no reconocida: {source}',
            'valid_sources': ['auto', 'graph', 'outlook']
        }), 400
    
    except Exception as e:
        current_app.logger.error(f"[SYNC] Error general: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error sincronizando: {str(e)}',
            'help': 'Intenta usar /api/auth/microsoft/login para autenticación remota'
        }), 500

@email_bp.route('/export/csv', methods=['POST'])
@token_required
def export_to_csv():
    """
    Exporta correos filtrados a CSV
    
    Body JSON:
        {
            email_ids: [1, 2, 3] // Si está vacío, exporta todos
        }
    """
    try:
        data = request.get_json() or {}
        
        if data.get('email_ids'):
            emails = Email.query.filter(
                Email.id.in_(data['email_ids']),
                Email.user_id == request.current_user.id
            ).all()
        else:
            emails = Email.query.filter_by(user_id=request.current_user.id).all()
        
        csv_data = ExportService.to_csv(emails)
        
        # Log de auditoría
        for email_id in [e.id for e in emails]:
            AuditedAction.log_action(
                user_id=request.current_user.id,
                email_id=email_id,
                action=AuditedAction.EXPORT,
                description='Correo exportado a CSV',
                ip_address=get_client_ip()
            )
        db.session.commit()
        
        return send_file(
            io.BytesIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'correos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error exportando a CSV: {str(e)}'}), 500

@email_bp.route('/export/pdf', methods=['POST'])
@token_required
def export_to_pdf():
    """
    Exporta correos filtrados a PDF
    
    Body JSON:
        {
            email_ids: [1, 2, 3] // Si está vacío, exporta todos
        }
    """
    try:
        data = request.get_json() or {}
        
        if data.get('email_ids'):
            emails = Email.query.filter(
                Email.id.in_(data['email_ids']),
                Email.user_id == request.current_user.id
            ).all()
        else:
            emails = Email.query.filter_by(user_id=request.current_user.id).all()
        
        pdf_data = ExportService.to_pdf(emails)
        
        # Log de auditoría
        for email_id in [e.id for e in emails]:
            AuditedAction.log_action(
                user_id=request.current_user.id,
                email_id=email_id,
                action=AuditedAction.EXPORT,
                description='Correo exportado a PDF',
                ip_address=get_client_ip()
            )
        db.session.commit()
        
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'correos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error exportando a PDF: {str(e)}'}), 500

@email_bp.route('/export/excel', methods=['POST'])
@token_required
def export_to_excel():
    """
    Exporta correos filtrados a Excel con información de auditoría
    
    Body JSON:
        {
            "email_ids": [1, 2, 3],  // Si está vacío, exporta todos
            "date_from": "2024-03-18",
            "date_to": "2024-03-20",
            "include_audit": true
        }
    """
    try:
        data = request.get_json() or {}
        email_ids = data.get('email_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        include_audit = data.get('include_audit', True)
        
        # Construir query
        query = Email.query.filter_by(user_id=request.current_user.id)
        
        # Filtrar por IDs si se proporcionan
        if email_ids:
            query = query.filter(Email.id.in_(email_ids))
        
        # Filtrar por rango de fechas de envío
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Email.sent_date >= from_date)
            except:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                # Agregar 1 día para incluir todo el día final
                to_date = to_date.replace(hour=23, minute=59, second=59)
                query = query.filter(Email.sent_date <= to_date)
            except:
                pass
        
        emails = query.order_by(Email.sent_date.desc()).all()
        
        if not emails:
            return jsonify({'error': 'No hay correos para exportar con los filtros especificados'}), 404
        
        # Exportar a Excel
        excel_data = ExportService.to_excel(emails, include_audit_info=include_audit)
        
        # Registrar auditoría
        for email in emails:
            AuditedAction.log_action(
                user_id=request.current_user.id,
                email_id=email.id,
                action=AuditedAction.EXPORT,
                description='Correo exportado a Excel',
                ip_address=get_client_ip()
            )
        db.session.commit()
        
        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'correos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        current_app.logger.error(f"Error exportando a Excel: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error exportando a Excel: {str(e)}'}), 500

@email_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def dashboard_stats():
    """
    Obtiene estadísticas del panel compartidas (TODOS los correos de todos los usuarios)
    """
    try:
        from sqlalchemy import func
        from sqlalchemy.sql import extract
        
        # Total de correos (DE TODOS LOS USUARIOS)
        total_emails = Email.query.count()
        
        # Correos con adjuntos (DE TODOS LOS USUARIOS)
        emails_with_attachments = Email.query.filter_by(
            has_attachments=True
        ).count()
        
        # Correos por mes (últimos 12 meses) - DE TODOS LOS USUARIOS
        emails_by_month = db.session.query(
            extract('year', Email.sent_date).label('year'),
            extract('month', Email.sent_date).label('month'),
            func.count(Email.id).label('count')
        ).group_by('year', 'month').all()
        
        # Top remitentes (DE TODOS LOS USUARIOS)
        top_senders = db.session.query(
            Email.sender,
            func.count(Email.id).label('count')
        ).group_by(
            Email.sender
        ).order_by(func.count(Email.id).desc()).limit(5).all()
        
        # Correos por importancia (DE TODOS LOS USUARIOS)
        by_importance = db.session.query(
            Email.importance,
            func.count(Email.id).label('count')
        ).group_by(
            Email.importance
        ).all()
        
        return jsonify({
            'total_emails': total_emails,
            'emails_with_attachments': emails_with_attachments,
            'emails_by_month': [
                {
                    'month': int(row[1]),
                    'year': int(row[0]),
                    'count': row[2]
                }
                for row in emails_by_month
            ],
            'top_senders': [
                {'sender': row[0], 'count': row[1]}
                for row in top_senders
            ],
            'by_importance': [
                {'importance': row[0], 'count': row[1]}
                for row in by_importance
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500


@email_bp.route('/sync/remote', methods=['POST'])
@token_required
def sync_from_remote_client():
    """
    Recibe sincronización de correos desde cliente remoto (Opción 1)
    Cada usuario ejecuta outlook_sync_agent.py en su equipo local
    
    Body JSON:
        {
            "emails": [
                {
                    "outlook_id": "...",
                    "subject": "...",
                    "sender": "...",
                    "recipients": "[...]",
                    "sent_date": "2024-03-20T...",
                    "body_snippet": "...",
                    "has_attachments": true,
                    "attachment_count": 0,
                    "importance": "Normal",
                    "outlook_class": "IPM.Note"
                }
            ],
            "source": "outlook_agent",
            "client_hostname": "PC-USER-001"
        }
    """
    try:
        data = request.get_json() or {}
        emails = data.get('emails', [])
        source = data.get('source', 'outlook_agent')
        client_hostname = data.get('client_hostname', 'unknown')
        
        if not emails:
            return jsonify({'error': 'No hay correos para sincronizar'}), 400
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        # Procesar cada correo
        for email_data in emails:
            try:
                # Validar datos requeridos
                if not email_data.get('subject') or not email_data.get('sender'):
                    skipped_count += 1
                    continue
                
                outlook_id = email_data.get('outlook_id')
                
                # Verificar si el correo ya existe (por email_id único)
                existing = Email.query.filter_by(
                    user_id=request.current_user.id,
                    email_id=outlook_id
                ).first()
                
                if existing:
                    skipped_count += 1
                    current_app.logger.debug(f"Correo {outlook_id} ya existe, omitido")
                    continue
                
                # Crear nuevo correo
                from datetime import datetime
                sent_date = email_data.get('sent_date')
                if sent_date and isinstance(sent_date, str):
                    try:
                        sent_date = datetime.fromisoformat(sent_date)
                    except:
                        sent_date = datetime.now()
                else:
                    sent_date = datetime.now()
                
                new_email = Email(
                    email_id=outlook_id,
                    user_id=request.current_user.id,
                    subject=email_data.get('subject', 'Sin asunto'),
                    sender=email_data.get('sender'),
                    recipients=email_data.get('recipients', '[]'),
                    sent_date=sent_date,
                    body_snippet=email_data.get('body_snippet', ''),
                    has_attachments=email_data.get('has_attachments', False),
                    attachment_count=email_data.get('attachment_count', 0),
                    importance=email_data.get('importance', 'Normal'),
                    outlook_class=email_data.get('outlook_class'),
                    is_synced=True,
                    sync_date=datetime.now()
                )
                
                db.session.add(new_email)
                db.session.flush()  # Obtener el ID antes de hacer commit
                
                # Registrar en auditoría
                AuditedAction.log_action(
                    user_id=request.current_user.id,
                    email_id=new_email.id,
                    action=AuditedAction.SYNC,
                    description=f'Correo sincronizado remotamente desde {client_hostname}',
                    ip_address=get_client_ip()
                )
                
                created_count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error sincronizando correo: {str(e)}", exc_info=True)
                errors.append(str(e))
                skipped_count += 1
        
        # Confirmar cambios
        db.session.commit()
        
        response = {
            'message': f'{created_count} correos sincronizados correctamente',
            'created': created_count,
            'skipped': skipped_count,
            'errors': errors if errors else None
        }
        
        current_app.logger.info(
            f"Sincronización remota desde {client_hostname}: "
            f"{created_count} creados, {skipped_count} omitidos"
        )
        
        if created_count > 0:
            return jsonify(response), 201
        else:
            return jsonify(response), 200
    
    except Exception as e:
        current_app.logger.error(f"Error en sincronización remota: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error sincronizando: {str(e)}'}), 500
