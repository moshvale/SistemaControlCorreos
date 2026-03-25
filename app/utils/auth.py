"""
Utilidades de autenticación con JWT
"""
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from time import time
from app.models import User

def generate_tokens(user_id):
    """
    Genera tokens JWT de acceso y refresco
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        dict: Diccionario con access_token y refresh_token
    """
    # Usar timestamps Unix en lugar de datetime objects
    current_time = int(time())
    access_expires_in = int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
    refresh_expires_in = int(current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds())
    
    access_token_payload = {
        'user_id': user_id,
        'type': 'access',
        'iat': current_time,
        'exp': current_time + access_expires_in
    }
    
    refresh_token_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'iat': current_time,
        'exp': current_time + refresh_expires_in
    }
    
    access_token = jwt.encode(
        access_token_payload, 
        current_app.config['JWT_SECRET_KEY'], 
        algorithm='HS256'
    )
    
    refresh_token = jwt.encode(
        refresh_token_payload, 
        current_app.config['JWT_SECRET_KEY'], 
        algorithm='HS256'
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': access_expires_in
    }

def verify_token(token):
    """
    Verifica y decodifica un token JWT
    
    Args:
        token (str): Token JWT
        
    Returns:
        dict or None: Payload del token si es válido, None si es inválido
    """
    try:
        payload = jwt.decode(
            token, 
            current_app.config['JWT_SECRET_KEY'], 
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    Decorador para proteger rutas que requieren autenticación JWT
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Buscar el token en los headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        if payload.get('type') != 'access':
            return jsonify({'error': 'Tipo de token incorrecto'}), 401
        
        request.current_user = User.query.get(payload['user_id'])
        if not request.current_user or not request.current_user.is_active:
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    Decorador para proteger rutas que requieren rol de administrador
    Debe usarse junto con token_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        if not request.current_user.is_admin:
            return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_client_ip():
    """
    Obtiene la dirección IP del cliente
    
    Returns:
        str: Dirección IP del cliente
    """
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.environ.get('REMOTE_ADDR', 'unknown')
