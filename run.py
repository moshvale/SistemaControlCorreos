"""
Punto de entrada de la aplicación
Ejecutar con: python run.py
"""
import os
from app import create_app

if __name__ == '__main__':
    # Obtener el ambiente (development, production, testing)
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Crear la aplicación
    app = create_app(env)
    
    # Variables de configuración
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = env == 'development'
    
    print(f"\n{'='*50}")
    print(f"Sistema de Gestión de Correos")
    print(f"{'='*50}")
    print(f"Ambiente: {env}")
    print(f"Servidor: http://{host}:{port}")
    print(f"Frontend: Abre index.html en tu navegador")
    print(f"Documentación: Ver README.md")
    print(f"{'='*50}\n")
    
    # Iniciar el servidor
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
