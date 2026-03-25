"""
Inicia la aplicación Flask
"""
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from config import config
import os
import logging

def create_app(config_name='development'):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración ('development', 'production', 'testing')
        
    Returns:
        Flask: Instancia de la aplicación
    """
    # Obtener ruta del directorio raíz del proyecto
    basedir = os.path.abspath(os.path.dirname(__file__))
    frontend_dir = os.path.join(basedir, '..', 'frontend')
    
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    from app.models import db
    db.init_app(app)
    
    # Habilitar CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Registrar blueprints
    from app.routes import auth_bp, email_bp, admin_bp, sync_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(sync_bp)
    
    # Configurar logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # Crear tabla de base de datos si no existe
    with app.app_context():
        db.create_all()
    
    # Ruta raíz - servir index.html
    @app.route('/')
    def index():
        return send_file(os.path.join(frontend_dir, 'index.html'))
    
    # Ruta de salud
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Aplicación funcionando correctamente'}), 200
    
    # Manejo de errores
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ruta no encontrada'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return app

# Crear aplicación
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
