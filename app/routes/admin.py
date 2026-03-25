"""
Rutas de administración solo para administradores
"""
from flask import Blueprint, request, jsonify, send_file
from app.models import User, Email, AuditLog, db
from app.utils import token_required, admin_required
from datetime import datetime
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def list_users():
    """
    Lista todos los usuarios del sistema (solo para administradores)
    
    Query parameters:
        page: Número de página (default: 1)
        per_page: Items por página (default: 20)
        active: true/false/all (default: all)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        active_filter = request.args.get('active', 'all')
        
        query = User.query
        
        if active_filter == 'true':
            query = query.filter_by(is_active=True)
        elif active_filter == 'false':
            query = query.filter_by(is_active=False)
        
        total = query.count()
        users = query.paginate(page=page, per_page=per_page).items
        
        return jsonify({
            'users': [user.to_dict(include_emails=True) for user in users],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error listando usuarios: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(user_id):
    """
    Obtiene detalles de un usuario específico
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = user.to_dict(include_emails=True)
        data['email_count'] = Email.query.filter_by(user_id=user_id).count()
        
        return jsonify({'user': data}), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo usuario: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(user_id):
    """
    Actualiza información de usuario (solo admin)
    
    Body JSON:
        {
            "full_name": "Nuevo nombre",
            "is_active": true,
            "is_admin": false
        }
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        
        allowed_fields = ['full_name', 'is_active', 'is_admin']
        
        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario actualizado',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error actualizando usuario: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """
    Elimina un usuario (desactivación)
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if user.id == request.current_user.id:
            return jsonify({'error': 'No puede eliminarse a sí mismo'}), 400
        
        # Eliminación lógica
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Usuario desactivado'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error eliminando usuario: {str(e)}'}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@token_required
@admin_required
def get_audit_logs():
    """
    Obtiene todos los logs de auditoría del sistema
    
    Query parameters:
        page: Número de página (default: 1)
        per_page: Items por página (default: 50)
        user_id: Filtrar por usuario
        email_id: Filtrar por correo
        action: Filtrar por tipo de acción
        date_from: Fecha desde (YYYY-MM-DD)
        date_to: Fecha hasta (YYYY-MM-DD)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = AuditLog.query
        
        if request.args.get('user_id'):
            query = query.filter_by(user_id=int(request.args.get('user_id')))
        
        if request.args.get('email_id'):
            query = query.filter_by(email_id=int(request.args.get('email_id')))
        
        if request.args.get('action'):
            query = query.filter_by(action=request.args.get('action'))
        
        if request.args.get('date_from'):
            try:
                date_from = datetime.strptime(request.args.get('date_from'), '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= date_from)
            except:
                pass
        
        if request.args.get('date_to'):
            try:
                date_to = datetime.strptime(request.args.get('date_to'), '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp <= date_to)
            except:
                pass
        
        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page
        ).items
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo logs: {str(e)}'}), 500

@admin_bp.route('/audit-logs/export', methods=['POST'])
@token_required
@admin_required
def export_audit_logs():
    """
    Exporta logs de auditoría a CSV
    
    Body JSON:
        {
            "date_from": "2024-03-01",
            "date_to": "2024-03-18",
            "user_id": 1 // opcional
        }
    """
    try:
        data = request.get_json() or {}
        
        query = AuditLog.query
        
        if data.get('date_from'):
            try:
                date_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp >= date_from)
            except:
                pass
        
        if data.get('date_to'):
            try:
                date_to = datetime.strptime(data['date_to'], '%Y-%m-%d')
                query = query.filter(AuditLog.timestamp <= date_to)
            except:
                pass
        
        if data.get('user_id'):
            query = query.filter_by(user_id=int(data['user_id']))
        
        logs = query.order_by(AuditLog.timestamp.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            'ID',
            'Timestamp',
            'Usuario',
            'Correo ID',
            'Acción',
            'Campo',
            'Valor Anterior',
            'Valor Nuevo',
            'Descripción',
            'IP'
        ]
        writer.writerow(headers)
        
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user_id,
                log.email_id,
                log.action,
                log.field_name,
                log.old_value,
                log.new_value,
                log.description,
                log.ip_address
            ])
        
        csv_data = output.getvalue().encode('utf-8')
        
        return send_file(
            io.BytesIO(csv_data),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error exportando logs: {str(e)}'}), 500

@admin_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def admin_stats():
    """
    Obtiene estadísticas generales del sistema
    """
    try:
        from sqlalchemy import func
        
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_admins': User.query.filter_by(is_admin=True).count(),
            'total_emails': Email.query.count(),
            'total_audit_logs': AuditLog.query.count(),
            'emails_with_attachments': Email.query.filter_by(has_attachments=True).count(),
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500
