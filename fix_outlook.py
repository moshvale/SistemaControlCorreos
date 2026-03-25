#!/usr/bin/env python
"""
Script para registrar pywin32 y verificar la conexión con Outlook
Ejecutar con: python fix_outlook.py
"""
import sys
import os
import subprocess

def register_pywin32():
    """Registra los componentes COM de pywin32"""
    print("=" * 60)
    print("REGISTRANDO COMPONENTES COM DE PYWIN32")
    print("=" * 60)
    
    try:
        # Estrategia 1: Obtener la ubicación de pywin32
        import pywin32_postinstall  # type: ignore
        script_path = os.path.join(os.path.dirname(pywin32_postinstall.__file__), 'pywin32_postinstall.py')
        
        if os.path.exists(script_path):
            print(f"Encontrado script en: {script_path}")
            result = subprocess.run([sys.executable, script_path, '-install'], capture_output=True, text=True)
            print(result.stdout)
            if result.returncode == 0:
                print("✓ Componentes COM registrados exitosamente (Estrategia 1)")
                return True
            else:
                print(f"Estrategia 1 falló: {result.stderr}")
    except ImportError as e:
        print(f"pywin32_postinstall no disponible: {e}")
    except Exception as e:
        print(f"Error en Estrategia 1: {e}")
    
    # Estrategia 2: Usar pip para reinstalar pywin32
    try:
        print("\nIntentando Estrategia 2: pip install --force-reinstall pywin32...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'pywin32==311'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Componentes COM registrados exitosamente (Estrategia 2)")
            return True
        else:
            print(f"Estrategia 2 falló: {result.stderr}")
    except Exception as e:
        print(f"Error en Estrategia 2: {e}")
    
    print("✗ No se pudieron registrar los componentes COM")
    return False

def test_outlook_connection():
    """Prueba la conexión con Outlook"""
    print("\n" + "=" * 60)
    print("PROBANDO CONEXIÓN CON OUTLOOK")
    print("=" * 60)
    
    try:
        print("1. Verificando importación de win32com...")
        import win32com.client as win32
        print("   ✓ win32com.client importado correctamente")
        
        print("\n2. Intentando obtener aplicación de Outlook...")
        outlook = win32.Dispatch("Outlook.Application")
        print("   ✓ Outlook.Application obtenida")
        
        print("\n3. Obteniendo namespace MAPI...")
        namespace = outlook.GetNamespace("MAPI")
        print("   ✓ Namespace MAPI obtenido")
        
        print("\n4. Obteniendo carpeta de elementos enviados...")
        sent_folder = namespace.GetDefaultFolder(6)
        print("   ✓ Carpeta de elementos enviados obtenida")
        
        print("\n5. Contando elementos en carpeta enviados...")
        items_count = sent_folder.Items.Count
        print(f"   ✓ Total de elementos: {items_count}")
        
        print("\n" + "=" * 60)
        print("✓ ¡CONEXIÓN A OUTLOOK EXITOSA!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("SOLUCIÓN SUGERIDA:")
        print("=" * 60)
        print("1. Asegúrate de que Outlook está ABIERTO (versión de escritorio)")
        print("2. Si es la primera vez, ejecuta: pip install --no-cache pywin32==311")
        print("3. Luego reinicia Python/VS Code")
        print("4. Si aún no funciona, intenta:")
        print("   - Cerrar completamente Outlook")
        print("   - Abrir Outlook de nuevo")
        print("   - Volver a ejecutar este script")
        print("=" * 60)
        return False

if __name__ == '__main__':
    print("\nSCRIPT DE VERIFICACIÓN Y REPARACIÓN DE OUTLOOK")
    print("=" * 60)
    
    # Intenta registrar pywin32
    register_pywin32()
    
    # Prueba la conexión
    success = test_outlook_connection()
    
    sys.exit(0 if success else 1)
