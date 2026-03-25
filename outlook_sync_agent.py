#!/usr/bin/env python3
"""
Cliente Outlook Sync Agent
Sincroniza correos locales de Outlook al servidor centralizado
Cada usuario ejecuta este script en su PC
"""

import requests
import json
import sys
import time
import argparse
from pathlib import Path
import win32com.client as win32
import pythoncom
from datetime import datetime, timedelta
import logging

# Configurar logging con encoding UTF-8 para Windows
import sys
import io

# Configurar salida estándar para manejar UTF-8 en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('outlook_sync_agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OutlookSyncAgent:
    """Agente para sincronizar Outlook local al servidor centralizado"""
    
    def __init__(self, server_url, username, password, limit=10):
        """
        Inicializar agente
        
        Args:
            server_url (str): URL del servidor (ej: http://192.168.1.100:5000)
            username (str): Usuario para autenticarse en servidor
            password (str): Contraseña para autenticarse en servidor
            limit (int): Número máximo de correos a sincronizar
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.limit = limit
        self.token = None
        self.outlook = None
        
    def connect_to_outlook(self):
        """Conectar a Outlook local"""
        try:
            pythoncom.CoInitialize()
            logger.info("Conectando a Outlook...")
            
            try:
                self.outlook = win32.GetActiveObject('Outlook.Application')
                logger.info("✓ Outlook conectado (GetActiveObject)")
            except:
                logger.info("Outlook no estaba activo, iniciando...")
                self.outlook = win32.Dispatch('Outlook.Application')
                logger.info("✓ Outlook iniciado (Dispatch)")
                
            return True
        except Exception as e:
            logger.error(f"✗ Error conectando a Outlook: {str(e)}")
            return False
    
    def disconnect_outlook(self):
        """Desconectar de Outlook"""
        try:
            if self.outlook:
                self.outlook = None
            pythoncom.CoUninitialize()
            logger.info("Desconectado de Outlook")
        except Exception as e:
            logger.error(f"Error desconectando de Outlook: {str(e)}")
    
    def authenticate(self):
        """Autenticar contra el servidor"""
        try:
            url = f"{self.server_url}/api/auth/login"
            payload = {
                'username': self.username,
                'password': self.password
            }
            
            logger.info(f"Autenticando en {url}...")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # El servidor retorna tokens.access_token, no token
                tokens = data.get('tokens', {})
                self.token = tokens.get('access_token')
                if self.token:
                    logger.info(f"✓ Autenticación exitosa. Token obtenido.")
                    return True
                else:
                    logger.error("✗ Token no encontrado en respuesta del servidor")
                    return False
            else:
                logger.error(f"✗ Error de autenticación: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error en autenticación: {str(e)}")
            return False
    
    def get_outlook_emails(self):
        """Obtener correos de Outlook"""
        try:
            if not self.outlook:
                logger.error("Outlook no conectado")
                return []
            
            logger.info(f"Obteniendo últimos {self.limit} correos de Outlook...")
            
            namespace = self.outlook.GetNamespace('MAPI')
            sent_folder = namespace.GetDefaultFolder(5)  # 5 = olFolderSentMail
            
            items = sent_folder.Items
            items.Sort('[SentOn]', False)  # Ordenar descendente por fecha
            
            emails = []
            count = 0
            
            for item in items:
                if count >= self.limit:
                    break
                
                try:
                    # Obtener destinatarios
                    recipients = []
                    for recipient in item.Recipients:
                        try:
                            # Intentar obtener email del destinatario
                            email = recipient.Address
                            
                            # Si es direccion SMTP, usarla directamente
                            if '@' in email:
                                recipient_email = email
                            else:
                                # Intentar obtener del Exchange User
                                try:
                                    ex_user = recipient.AddressEntry.GetExchangeUser()
                                    if ex_user:
                                        recipient_email = ex_user.PrimarySmtpAddress
                                    else:
                                        recipient_email = email
                                except:
                                    recipient_email = email
                            
                            recipients.append({
                                'name': recipient.Name,
                                'email': recipient_email
                            })
                        except:
                            # Si falla, usar solo el nombre
                            recipients.append({
                                'name': recipient.Name,
                                'email': recipient.Name
                            })
                    
                    email_data = {
                        'outlook_id': item.EntryID,
                        'subject': item.Subject,
                        'sender': item.SenderName or item.SenderEmailAddress,
                        'recipients': json.dumps(recipients),
                        'sent_date': item.SentOn.isoformat() if item.SentOn else datetime.now().isoformat(),
                        'body_snippet': item.Body[:500] if item.Body else '',
                        'has_attachments': item.Attachments.Count > 0,
                        'attachment_count': item.Attachments.Count,
                        'importance': ['Low', 'Normal', 'High'][item.Importance],
                        'outlook_class': item.Class
                    }
                    
                    emails.append(email_data)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Error procesando correo: {str(e)}")
                    continue
            
            logger.info(f"✓ {count} correos obtenidos de Outlook")
            return emails
            
        except Exception as e:
            logger.error(f"✗ Error obteniendo correos: {str(e)}")
            return []
    
    def send_emails_to_server(self, emails):
        """Enviar correos al servidor"""
        if not self.token:
            logger.error("No hay token de autenticación")
            return False
        
        if not emails:
            logger.info("No hay correos para sincronizar")
            return True
        
        try:
            url = f"{self.server_url}/api/emails/sync/remote"
            
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'emails': emails,
                'source': 'outlook_agent',
                'client_hostname': __import__('socket').gethostname()
            }
            
            logger.info(f"Enviando {len(emails)} correos al servidor...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Sincronización exitosa: {result.get('message')}")
                return True
            elif response.status_code == 201:
                result = response.json()
                logger.info(f"✓ {result.get('created')} correos creados, {result.get('skipped')} omitidos")
                return True
            else:
                logger.error(f"✗ Error del servidor: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error enviando correos: {str(e)}")
            return False
    
    def run_once(self):
        """Ejecutar sincronización una sola vez"""
        logger.info("=" * 60)
        logger.info("Iniciando sincronización de Outlook")
        logger.info("=" * 60)
        
        # Conectar a Outlook
        if not self.connect_to_outlook():
            return False
        
        try:
            # Autenticar en servidor
            if not self.authenticate():
                return False
            
            # Verificar que el token fue guardado
            if not self.token:
                logger.error("Error crítico: Token no fue asignado después de autenticación")
                return False
            
            # Obtener correos
            emails = self.get_outlook_emails()
            if not emails:
                logger.info("Sin correos nuevos para sincronizar")
                return True
            
            # Enviar al servidor
            success = self.send_emails_to_server(emails)
            
            return success
            
        finally:
            self.disconnect_outlook()
    
    def run_daemon(self, interval_minutes=15):
        """Ejecutar sincronización en modo daemon"""
        logger.info("=" * 60)
        logger.info(f"Iniciando daemon - Sincronización cada {interval_minutes} minutos")
        logger.info("=" * 60)
        
        try:
            while True:
                self.run_once()
                logger.info(f"Próxima sincronización en {interval_minutes} minutos...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("Daemon detenido por usuario")
        except Exception as e:
            logger.error(f"Error en daemon: {str(e)}")
        finally:
            self.disconnect_outlook()


def load_config():
    """Cargar configuración desde config.json"""
    config_file = Path('outlook_sync_config.json')
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo config: {str(e)}")
            return None
    
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Cliente Outlook Sync Agent - Sincroniza tu Outlook al servidor centralizado'
    )
    parser.add_argument('--server', '-s', help='URL del servidor (ej: http://192.168.1.100:5000)')
    parser.add_argument('--username', '-u', help='Usuario para servidor')
    parser.add_argument('--password', '-p', help='Contraseña para servidor')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Número máximo de correos (default: 10)')
    parser.add_argument('--daemon', '-d', action='store_true', help='Ejecutar en modo daemon (sincronización continua)')
    parser.add_argument('--interval', '-i', type=int, default=15, help='Intervalo en minutos para daemon (default: 15)')
    
    args = parser.parse_args()
    
    # Cargar configuración de archivo si existe
    config = load_config()
    
    # Usar argumentos de línea de comandos si se proporcionan, sino usar config
    server_url = args.server or (config.get('server_url') if config else None)
    username = args.username or (config.get('username') if config else None)
    password = args.password or (config.get('password') if config else None)
    limit = args.limit or (config.get('limit') if config else 10)
    
    # Validar parámetros requeridos
    if not server_url:
        print("Error: Se requiere URL del servidor (--server o en outlook_sync_config.json)")
        sys.exit(1)
    
    if not username:
        print("Error: Se requiere usuario (--username o en outlook_sync_config.json)")
        sys.exit(1)
    
    if not password:
        print("Error: Se requiere contraseña (--password o en outlook_sync_config.json)")
        sys.exit(1)
    
    # Crear agente
    agent = OutlookSyncAgent(server_url, username, password, limit)
    
    # Ejecutar
    if args.daemon:
        agent.run_daemon(args.interval)
    else:
        success = agent.run_once()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
