"""
Rutas de autenticación
"""
from flask import Blueprint, request, jsonify
from app.models import User, db
from app.utils import generate_tokens, verify_token, get_client_ip
from app.services import GraphService
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra un nuevo usuario
    
    Body JSON:
        {
            "username": "usuario",
            "email": "usuario@example.com",
            "password": "contraseña",
            "full_name": "Nombre completo"
        }
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Campos requeridos: username, email, password'}), 400
        
        # Verificar que username y email sean únicos
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El correo electrónico ya está registrado'}), 409
        
        # Crear nuevo usuario
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', data['username'])
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error en registro: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión de un usuario
    
    Body JSON:
        {
            "username": "usuario",
            "password": "contraseña"
        }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Se requiere username y password'}), 400
        
        # Buscar usuario
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Actualizar última vez de login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generar tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Login exitoso',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error en login: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresca el token de acceso usando el refresh token
    
    Body JSON:
        {
            "refresh_token": "token_aqui"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'refresh_token' not in data:
            return jsonify({'error': 'Refresh token requerido'}), 400
        
        payload = verify_token(data['refresh_token'])
        
        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Refresh token inválido o expirado'}), 401
        
        # Verificar que el usuario siga siendo válido
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'Usuario no válido'}), 401
        
        # Generar nuevos tokens
        tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Token refrescado',
            'tokens': tokens
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error refrescando token: {str(e)}'}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_user():
    """
    Verifica si el token es válido y devuelve información del usuario
    Requiere header Authorization: Bearer <token>
    """
    try:
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 401
        
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token inválido'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'Usuario no válido'}), 401
        
        return jsonify({
            'valid': True,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error verificando token: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    Cambia la contraseña del usuario autenticado
    Requiere header Authorization: Bearer <token>
    
    Body JSON:
        {
            "old_password": "contraseña_actual",
            "new_password": "nueva_contraseña"
        }
    """
    try:
        # Obtener token del header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 401
        
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token inválido'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        
        # Procesar cambio de contraseña
        data = request.get_json()
        
        if not data or not all(k in data for k in ['old_password', 'new_password']):
            return jsonify({'error': 'Se requieren old_password y new_password'}), 400
        
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401
        
        if len(data['new_password']) < 8:
            return jsonify({'error': 'La nueva contraseña debe tener al menos 8 caracteres'}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'message': 'Contraseña cambiad exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error cambiando contraseña: {str(e)}'}), 500


# ===================== MICROSOFT GRAPH OAUTH2 ROUTES =====================

@auth_bp.route('/microsoft/login', methods=['GET'])
def microsoft_login():
    """
    Inicia el flujo de autenticación OAuth2 de Microsoft
    Redirige al usuario a la página de login de Microsoft
    
    Returns:
        redirect: URL de Microsoft para autenticación
    """
    try:
        auth_url = GraphService.get_auth_url()
        return jsonify({'auth_url': auth_url}), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo URL de autenticación: {str(e)}'}), 500


@auth_bp.route('/callback/microsoft', methods=['GET'])
def microsoft_callback():
    """
    Callback de Microsoft después de que el usuario se autentica
    Intercambia el código de autorización por tokens
    
    Query params:
        - code: Código de autorización de Microsoft
        - session_state: Estado de sesión de Microsoft
        - error (opcional): Código de error si falla la autenticación
    """
    try:
        # Verificar si hay error en la respuesta
        error = request.args.get('error')
        if error:
            return jsonify({'error': f'Error de Microsoft: {error}'}), 400
        
        # Obtener código de autorización
        auth_code = request.args.get('code')
        if not auth_code:
            return jsonify({'error': 'No se recibió código de autorización'}), 400
        
        # Intercambiar código por tokens
        token_response = GraphService.acquire_token_by_auth_code(auth_code)
        
        if 'error' in token_response:
            return jsonify({'error': f"Error obteniendo tokens: {token_response.get('error_description', 'Unknown error')}"}), 400
        
        # Obtener información del usuario de Microsoft
        graph_service = GraphService()
        graph_service.access_token = token_response['access_token']
        user_info = graph_service.get_user_info()
        
        if not user_info:
            return jsonify({'error': 'No se pudo obtener información del usuario'}), 400
        
        microsoft_id = user_info.get('id')
        microsoft_email = user_info.get('mail') or user_info.get('userPrincipalName')
        display_name = user_info.get('displayName', '')
        
        # Buscar usuario existente por microsoft_id
        user = User.query.filter_by(microsoft_id=microsoft_id).first()
        
        if not user:
            # Crear nuevo usuario con credenciales de Microsoft
            user = User(
                microsoft_id=microsoft_id,
                microsoft_email=microsoft_email,
                email=microsoft_email,
                username=microsoft_email.split('@')[0],  # Usar parte antes del @ como username
                full_name=display_name,
                is_active=True
            )
            # Generar contraseña aleatoria (no se usará, pero es requerida en el modelo)
            import secrets
            user.set_password(secrets.token_urlsafe(32))
            db.session.add(user)
        else:
            # Actualizar información si el usuario ya existe
            user.microsoft_email = microsoft_email
            user.full_name = display_name
        
        # Guardar tokens OAuth de Microsoft
        user.access_token = token_response['access_token']
        user.refresh_token = token_response.get('refresh_token')
        
        # Calcular fecha de expiración del token
        expires_in = token_response.get('expires_in', 3600)
        user.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Generar JWT tokens para la aplicación
        app_tokens = generate_tokens(user.id)
        
        return jsonify({
            'message': 'Autenticación exitosa',
            'user': user.to_dict(),
            'tokens': app_tokens,
            'microsoft_email': microsoft_email
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error en callback: {str(e)}'}), 500


@auth_bp.route('/microsoft/status', methods=['GET'])
def microsoft_auth_status():
    """
    Obtiene el estado de autenticación de Microsoft del usuario
    Requiere header Authorization: Bearer <token>
    
    Returns:
        dict: Estado de autenticación y información de Microsoft
    """
    try:
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 401
        
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token inválido'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        
        return jsonify({
            'is_microsoft_authenticated': bool(user.microsoft_id and user.access_token),
            'microsoft_email': user.microsoft_email,
            'microsoft_id': user.microsoft_id,
            'token_expires_at': user.token_expires_at.isoformat() if user.token_expires_at else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error verificando estado: {str(e)}'}), 500


@auth_bp.route('/microsoft/disconnect', methods=['POST'])
def microsoft_disconnect():
    """
    Desconecta la cuenta de Microsoft del usuario
    Requiere header Authorization: Bearer <token>
    
    Returns:
        dict: Confirmación de desconexión
    """
    try:
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'error': 'Token no encontrado'}), 401
        
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token inválido'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 401
        
        # Limpiar tokens de Microsoft
        user.microsoft_id = None
        user.microsoft_email = None
        user.access_token = None
        user.refresh_token = None
        user.token_expires_at = None
        db.session.commit()
        
        return jsonify({
            'message': 'Cuenta de Microsoft desconectada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error desconectando: {str(e)}'}), 500


from datetime import timedelta
