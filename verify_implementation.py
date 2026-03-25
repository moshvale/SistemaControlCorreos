#!/usr/bin/env python
"""
Script de verificación de implementación Microsoft Graph API
Valida que todo está correctamente configurado antes de ejecutar la app
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_file_exists(path, description):
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - FALTA: {path}")
        return False

def check_imports():
    print("Verificando imports...")
    try:
        import requests
        print("✅ requests instalado")
    except ImportError:
        print("❌ requests NO instalado")
        return False
    
    try:
        import msal
        print("✅ msal instalado")
    except ImportError:
        print("❌ msal NO instalado")
        return False
    
    try:
        from flask import Flask
        print("✅ Flask instalado")
    except ImportError:
        print("❌ Flask NO instalado")
        return False
    
    return True

def check_env_vars():
    print("\nVerificando variables de entorno...")
    from dotenv import load_dotenv
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Archivo .env encontrado")
        load_dotenv()
    else:
        print(f"⚠️  Archivo .env NO encontrado (usar .env.example como template)")
        return False
    
    required_vars = [
        'MICROSOFT_CLIENT_ID',
        'MICROSOFT_CLIENT_SECRET',
        'MICROSOFT_TENANT_ID',
        'MICROSOFT_REDIRECT_URI'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mostrar solo primeros 10 caracteres
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} - NO CONFIGURADO")
            all_present = False
    
    return all_present

def check_database():
    print("\nVerificando base de datos...")
    from app import create_app
    from app.models import db, User, Email
    
    try:
        app = create_app('development')
        with app.app_context():
            # Intentar consulta simple
            user_count = User.query.count()
            email_count = Email.query.count()
            print(f"✅ Base de datos accesible")
            print(f"   - Usuarios: {user_count}")
            print(f"   - Correos: {email_count}")
        return True
    except Exception as e:
        print(f"❌ Error accediendo BD: {str(e)}")
        return False

def check_blueprints():
    print("\nVerificando blueprints...")
    try:
        from app import create_app
        app = create_app('development')
        
        required_blueprints = ['auth', 'emails', 'admin', 'sync']
        registered = list(app.blueprints.keys())
        
        all_present = True
        for bp_name in required_blueprints:
            if bp_name in registered:
                print(f"✅ Blueprint '{bp_name}' registrado")
            else:
                print(f"❌ Blueprint '{bp_name}' NO registrado")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"❌ Error verificando blueprints: {str(e)}")
        return False

def check_services():
    print("\nVerificando servicios...")
    try:
        from app.services import GraphService, EmailService
        print(f"✅ GraphService importable")
        print(f"✅ EmailService importable")
        return True
    except Exception as e:
        print(f"❌ Error importando servicios: {str(e)}")
        return False

def check_routes():
    print("\nVerificando rutas...")
    try:
        from app import create_app
        app = create_app('development')
        
        required_routes = [
            '/api/auth/microsoft/login',
            '/api/auth/microsoft/status',
            '/api/auth/microsoft/disconnect',
            '/api/sync/microsoft/sent',
            '/api/sync/microsoft/inbox',
            '/api/sync/microsoft/status',
        ]
        
        # Obtener todas las rutas
        routes = set()
        for rule in app.url_map.iter_rules():
            routes.add(str(rule.rule))
        
        all_present = True
        for route in required_routes:
            if any(route in r for r in routes):
                print(f"✅ Ruta {route}")
            else:
                print(f"❌ Ruta {route} NO encontrada")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"❌ Error verificando rutas: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("    VERIFICACIÓN DE IMPLEMENTACIÓN - MICROSOFT GRAPH API")
    print("="*70)
    
    checks = []
    
    # Check 1: Archivos
    print_header("1. VERIFICANDO ARCHIVOS REQUERIDOS")
    checks.append(check_file_exists("app/services/graph_service.py", "GraphService"))
    checks.append(check_file_exists("app/routes/sync.py", "Rutas de sincronización"))
    checks.append(check_file_exists("MICROSOFT_GRAPH_SETUP.md", "Documentación de setup"))
    checks.append(check_file_exists("QUICK_START_MICROSOFT_GRAPH.md", "Guía de inicio rápido"))
    checks.append(check_file_exists(".env.example", "Archivo .env.example"))
    
    # Check 2: Dependencias
    print_header("2. VERIFICANDO DEPENDENCIAS")
    checks.append(check_imports())
    
    # Check 3: Variables de Entorno
    print_header("3. VERIFICANDO CONFIGURACIÓN")
    checks.append(check_env_vars())
    
    # Check 4: Base de Datos
    print_header("4. VERIFICANDO BASE DE DATOS")
    checks.append(check_database())
    
    # Check 5: Blueprints
    print_header("5. VERIFICANDO BLUEPRINTS")
    checks.append(check_blueprints())
    
    # Check 6: Servicios
    print_header("6. VERIFICANDO SERVICIOS")
    checks.append(check_services())
    
    # Check 7: Rutas
    print_header("7. VERIFICANDO RUTAS API")
    checks.append(check_routes())
    
    # Resumen
    print_header("RESUMEN")
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Verificaciones pasadas: {passed}/{total} ({percentage:.0f}%)\n")
    
    if percentage == 100:
        print("🎉 ¡TODO ESTÁ LISTO!")
        print("\n  Puedes ejecutar: python run.py")
        print("  Recuerda que necesitas configurar .env con las credenciales de Azure AD")
        print("\n  Guía: QUICK_START_MICROSOFT_GRAPH.md")
        return 0
    else:
        print("⚠️  HAY PROBLEMAS QUE RESOLVER:")
        print("  - Verifica los archivos faltantes")
        print("  - Instala las dependencias: pip install -r requirements.txt")
        print("  - Configura .env con credenciales de Azure AD")
        return 1

if __name__ == '__main__':
    sys.exit(main())
