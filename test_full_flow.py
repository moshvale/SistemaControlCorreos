#!/usr/bin/env python
"""
Script de prueba verificando que el servidor está funcionando correctamente
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

def test_frontend_loads():
    """Verificar que el frontend carga correctamente"""
    print("\n=== Verificando que el frontend carga ===")
    response = requests.get(BASE_URL)
    if response.status_code == 200 and 'html' in response.text:
        print("✓ Frontend cargado correctamente")
        return True
    else:
        print("✗ Error cargando frontend")
        return False

def test_health():
    """Verificar que el servidor está en línea"""
    print("\n=== Verificando salud del servidor ===")
    response = requests.get(f'{API_URL}/health')
    if response.status_code == 200:
        print(f"✓ Servidor en línea: {response.json()}")
        return True
    else:
        print("✗ Error en health check")
        return False

def test_login_flow():
    """Probar el flujo completo de login"""
    print("\n=== Prueba completa del flujo de login ===")
    
    # 1. Registrar usuario
    print("\n1. Registrando usuario...")
    user_data = {
        'username': 'logintest',
        'email': 'logintest@example.com',
        'password': 'LoginTest123',
        'full_name': 'Login Test User'
    }
    
    response = requests.post(f'{API_URL}/auth/register', json=user_data)
    if response.status_code == 201:
        print("   ✓ Usuario registrado")
    elif response.status_code == 409:
        print("   ✓ Usuario ya existe (esperado)")
    else:
        print(f"   ✗ Error: {response.json()}")
        return False
    
    # 2. Hacer login
    print("\n2. Haciendo login...")
    login_data = {
        'username': user_data['username'],
        'password': user_data['password']
    }
    
    response = requests.post(f'{API_URL}/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"   ✗ Error en login: {response.json()}")
        return False
    
    data = response.json()
    if 'tokens' not in data or 'access_token' not in data['tokens']:
        print("   ✗ No hay tokens en la respuesta")
        return False
    
    tokens = data['tokens']
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    
    print(f"   ✓ Login exitoso")
    print(f"   ✓ Access Token generado: {access_token[:40]}...")
    print(f"   ✓ Refresh Token generado: {refresh_token[:40]}...")
    
    # 3. Verificar que el tokens son válidos
    print("\n3. Verificando tokens...")
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{API_URL}/auth/verify', headers=headers)
    
    if response.status_code != 200:
        print(f"   ✗ Token no válido: {response.json()}")
        return False
    
    verified_user = response.json()
    print(f"   ✓ Token válido para usuario: {verified_user['user']['username']}")
    
    # 4. Probar refresh token
    print("\n4. Probando refresh de token...")
    refresh_data = {'refresh_token': refresh_token}
    response = requests.post(f'{API_URL}/auth/refresh', json=refresh_data)
    
    if response.status_code != 200:
        print(f"   ✗ Error refrescando token: {response.json()}")
        return False
    
    new_tokens = response.json()['tokens']
    print(f"   ✓ Token refrescado correctamente")
    print(f"   ✓ Nuevo Access Token: {new_tokens['access_token'][:40]}...")
    
    # 5. Verificar el nuevo token
    print("\n5. Verificando nuevo token...")
    headers = {'Authorization': f'Bearer {new_tokens["access_token"]}'}
    response = requests.get(f'{API_URL}/auth/verify', headers=headers)
    
    if response.status_code != 200:
        print(f"   ✗ Nuevo token no válido: {response.json()}")
        return False
    
    print(f"   ✓ Nuevo token válido")
    
    print("\n✅ Flujo de login completamente exitoso")
    return True

if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              Pruebas Completas del Sistema                 ║")
    print("║          Email Tracker - Sistema de Gestión de Correos     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"\nServidor: {BASE_URL}")
    print(f"API Base: {API_URL}")
    
    all_passed = True
    
    # Ejecutar pruebas
    all_passed &= test_health()
    all_passed &= test_frontend_loads()
    all_passed &= test_login_flow()
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    if all_passed:
        print("║              ✅ TODAS LAS PRUEBAS PASARON ✅             ║")
    else:
        print("║              ❌ ALGUNAS PRUEBAS FALLARON ❌              ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
