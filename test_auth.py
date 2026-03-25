#!/usr/bin/env python
"""
Script de prueba para verificar el funcionamiento de autenticación
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def test_register():
    """Registrar un usuario de prueba"""
    print("\n=== Registrando usuario de prueba ===")
    response = requests.post(f'{BASE_URL}/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'full_name': 'Test User'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 201

def test_login():
    """Probar el login"""
    print("\n=== Probando login ===")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'testuser',
        'password': 'TestPassword123'
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response keys: {data.keys()}")
    
    if response.status_code == 200 and 'tokens' in data:
        tokens = data['tokens']
        print(f"Access Token: {tokens['access_token'][:50]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:50]}...")
        print(f"Expires In: {tokens['expires_in']} segundos")
        return tokens
    else:
        print(f"Error: {data}")
        return None

def test_refresh_token(tokens):
    """Probar el refresh de token"""
    print("\n=== Probando refresh de token ===")
    response = requests.post(f'{BASE_URL}/auth/refresh', json={
        'refresh_token': tokens['refresh_token']
    })
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        new_tokens = data['tokens']
        print(f"New Access Token: {new_tokens['access_token'][:50]}...")
        print(f"✓ Refresh exitoso!")
        return new_tokens
    else:
        print(f"✗ Error en refresh: {data}")
        return None

def test_verify_token(access_token):
    """Verificar que el token sea válido"""
    print("\n=== Verificando token ===")
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{BASE_URL}/auth/verify', headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"✓ Token válido!")
        print(f"User: {data['user']}")
        return True
    else:
        print(f"✗ Token inválido: {data}")
        return False

if __name__ == '__main__':
    print("Iniciando pruebas de autenticación...")
    print(f"Base URL: {BASE_URL}")
    
    # Intentar registrar (puede fallar si ya existe)
    test_register()
    
    # Hacer login
    tokens = test_login()
    
    if tokens:
        # Verificar el access token
        test_verify_token(tokens['access_token'])
        
        # Probar refresh
        new_tokens = test_refresh_token(tokens)
        
        if new_tokens:
            # Verificar el nuevo token
            test_verify_token(new_tokens['access_token'])
    
    print("\n=== Pruebas completadas ===")
