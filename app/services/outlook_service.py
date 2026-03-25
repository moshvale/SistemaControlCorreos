"""
Servicio de integración con Outlook usando win32com.client
"""
import win32com.client as win32
import pythoncom  # IMPORTANTE: Necesario para inicializar COM en threads
from datetime import datetime
import json
from flask import current_app
import traceback
import sys

class OutlookService:
    """Servicio para interactuar con Outlook"""
    
    def __init__(self):
        """Inicializa la conexión con Outlook"""
        self.outlook = None
        self.namespace = None
        self.sent_folder = None
        self.com_initialized = False
    
    def connect(self):
        """
        Conecta con Outlook
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # PASO CRÍTICO: Inicializar COM en este thread
            # Esto es necesario porque Flask maneja peticiones en threads separados
            try:
                current_app.logger.debug("Inicializando COM en thread actual...")
                pythoncom.CoInitialize()
                self.com_initialized = True
                current_app.logger.debug("✓ COM inicializado")
            except Exception as e:
                current_app.logger.debug(f"COM ya estaba inicializado o error: {str(e)}")
                self.com_initialized = True  # Continuar de todas formas
            
            current_app.logger.debug("Intentando conectar con Outlook...")
            
            # Paso 1: Obtener la aplicación de Outlook
            try:
                current_app.logger.debug("Paso 1: Dispatching Outlook.Application...")
                self.outlook = win32.Dispatch("Outlook.Application")
                current_app.logger.debug("✓ Outlook.Application obtenida")
            except Exception as e:
                current_app.logger.error(f"✗ No se pudo obtener Outlook.Application: {str(e)}")
                current_app.logger.error("  Asegúrate de que Outlook esté ABIERTO (no solo minimizado)")
                current_app.logger.error("  Nota: Outlook en navegador (web) NO funciona. Necesitas la versión de escritorio.")
                raise
            
            # Paso 2: Obtener el namespace
            try:
                current_app.logger.debug("Paso 2: Obteniendo namespace MAPI...")
                self.namespace = self.outlook.GetNamespace("MAPI")
                current_app.logger.debug("✓ Namespace MAPI obtenido")
            except Exception as e:
                current_app.logger.error(f"✗ No se pudo obtener namespace MAPI: {str(e)}")
                raise
            
            # Paso 3: Obtener carpeta de elementos enviados
            try:
                current_app.logger.debug("Paso 3: Obteniendo carpeta de elementos enviados...")
                # 5 es el índice para la carpeta de elementos enviados (SentMail)
                # Nota: El índice 11 en algunas configuraciones puede estar vacío
                self.sent_folder = self.namespace.GetDefaultFolder(5)
                current_app.logger.debug("✓ Carpeta de elementos enviados obtenida")
            except Exception as e:
                current_app.logger.error(f"✗ No se pudo obtener carpeta de enviados: {str(e)}")
                raise
            
            current_app.logger.info("✓ Conexión a Outlook establecida exitosamente")
            return True
            
        except Exception as e:
            current_app.logger.error(f"\n{'='*60}")
            current_app.logger.error(f"ERROR CONECTANDO A OUTLOOK: {str(e)}")
            current_app.logger.error(f"{'='*60}")
            current_app.logger.error("SOLUCIÓN:")
            current_app.logger.error("1. Abre Outlook (aplicación de escritorio, NO la versión web)")
            current_app.logger.error("2. Inicia sesión si es necesario")
            current_app.logger.error("3. Mantén Outlook abierto mientras usas la sincronización")
            current_app.logger.error("4. Si es la primera vez, ejecuta: python fix_outlook.py")
            current_app.logger.error(f"{'='*60}\n")
            
            traceback.print_exc()
            return False
    
    def get_sent_emails(self, limit=None):
        """
        Obtiene los correos enviados de Outlook
        
        Args:
            limit (int, optional): Número máximo de correos a obtener (default: 1 para el último)
            
        Returns:
            list: Lista de diccionarios con información de los correos
        """
        if not self.sent_folder:
            if not self.connect():
                return []
        
        if limit is None:
            limit = 1
        
        emails = []
        try:
            items = self.sent_folder.Items
            items.Sort("[ReceivedTime]", True)  # Ordenar por fecha de recepción descendente (más recientes primero)
            
            current_app.logger.debug(f"Total de correos en carpeta enviados: {items.Count}")
            
            count = 0
            for item in items:
                if limit and count >= limit:
                    break
                
                # Filtrar solo MailItems (excluir otras clases de elementos)
                if item.Class != 43:  # 43 es MailItem
                    continue
                
                try:
                    email_data = self._extract_email_data(item)
                    emails.append(email_data)
                    count += 1
                    current_app.logger.debug(f"Email extrado: {email_data['subject'][:50]}")
                except Exception as e:
                    current_app.logger.warning(f"Error extrayendo datos del correo: {str(e)}")
                    continue
        
        except Exception as e:
            current_app.logger.error(f"Error obteniendo correos enviados: {str(e)}", exc_info=True)
        
        current_app.logger.info(f"Se obtuvieron {len(emails)} correos de Outlook")
        return emails
    
    def _extract_email_data(self, outlook_item):
        """
        Extrae datos de un elemento de Outlook
        
        Args:
            outlook_item: Objeto MailItem de Outlook
            
        Returns:
            dict: Diccionario con datos del correo
        """
        # Obtener remitente SMTP (no formato X.500)
        sender_email = self._resolve_smtp_address(outlook_item.Sender)
        sender_name = outlook_item.SenderName or "Unknown"
        sender = sender_email or sender_name
        
        # Obtener destinatarios
        recipients = []
        try:
            for recipient in outlook_item.Recipients:
                recipient_email = self._resolve_smtp_address(recipient)
                recipient_name = recipient.Name
                recipients.append({
                    'email': recipient_email or recipient.Address,
                    'name': recipient_name,
                    'type': 'to'  # Podría ser 'cc' o 'bcc' pero Outlook generalmente muestra 'to'
                })
        except:
            pass
        
        # Obtener fragmento del cuerpo
        body_snippet = outlook_item.Body[:current_app.config['EMAIL_BODY_SNIPPET_LENGTH']] \
            if outlook_item.Body else None
        
        # Obtener información de archivos adjuntos
        has_attachments = bool(outlook_item.Attachments.Count)
        attachment_count = outlook_item.Attachments.Count
        
        return {
            'outlook_id': outlook_item.EntryID,
            'subject': outlook_item.Subject,
            'sender': sender,
            'recipients': recipients,
            'sent_date': outlook_item.SentOn,
            'received_date': outlook_item.ReceivedTime,  # Para sincronización
            'body_snippet': body_snippet,
            'has_attachments': has_attachments,
            'attachment_count': attachment_count,
            'importance': self._map_importance(outlook_item.Importance),
            'outlook_class': outlook_item.Class
        }
    
    @staticmethod
    def _resolve_smtp_address(outlook_recipient):
        """
        Resuelve la dirección SMTP de un objeto de Outlook (Sender o Recipient)
        Convierte formato X.500 a dirección SMTP cuando es necesario
        
        Args:
            outlook_recipient: Objeto Sender o Recipient de Outlook
            
        Returns:
            str: Dirección SMTP o None si no se puede resolver
        """
        try:
            # Primero intentar obtener la dirección directa
            if hasattr(outlook_recipient, 'Address'):
                address = outlook_recipient.Address
                # Si no es formato X.500, es directamente el email SMTP
                if address and not address.startswith('/'):
                    return address
            
            # Intentar obtener a través de AddressEntry (mejor para Exchange)
            if hasattr(outlook_recipient, 'AddressEntry'):
                try:
                    addr_entry = outlook_recipient.AddressEntry
                    if addr_entry:
                        # Intentar obtener la dirección SMTP del AddressEntry
                        if hasattr(addr_entry, 'Address'):
                            smtp_addr = addr_entry.Address
                            if smtp_addr and not smtp_addr.startswith('/'):
                                return smtp_addr
                        
                        # Intentar extraer email de las propiedades del usuario
                        if hasattr(addr_entry, 'GetExchangeUser'):
                            try:
                                ex_user = addr_entry.GetExchangeUser()
                                if ex_user and hasattr(ex_user, 'PrimarySmtpAddress'):
                                    primary_smtp = ex_user.PrimarySmtpAddress
                                    if primary_smtp:
                                        return primary_smtp
                            except:
                                pass
                except Exception as e:
                    current_app.logger.debug(f"Error accessing AddressEntry: {str(e)}")
            
            # Si todo falla, retornar el nombre como fallback
            if hasattr(outlook_recipient, 'Name'):
                name = outlook_recipient.Name
                if name:
                    return name
            
            return None
        except Exception as e:
            current_app.logger.debug(f"Error resolviendo direccion SMTP: {str(e)}")
            return None
    
    @staticmethod
    def _map_importance(outlook_importance):
        """
        Mapea la importancia de Outlook a valores legibles
        
        Args:
            outlook_importance (int): Importancia de Outlook (0=bajo, 1=normal, 2=alto)
            
        Returns:
            str: Importancia legible
        """
        importance_map = {
            0: 'Low',
            1: 'Normal',
            2: 'High'
        }
        return importance_map.get(outlook_importance, 'Normal')
    
    def get_email_by_id(self, item_id):
        """
        Obtiene un correo específico por su ID de Outlook
        
        Args:
            item_id (str): ID del elemento en Outlook (EntryID)
            
        Returns:
            dict or None: Datos del correo o None si no se encuentra
        """
        if not self.namespace:
            if not self.connect():
                return None
        
        try:
            item = self.namespace.GetItemFromID(item_id)
            return self._extract_email_data(item)
        except Exception as e:
            current_app.logger.error(f"Error obteniendo correo {item_id}: {str(e)}")
            return None
    
    def disconnect(self):
        """Cierra la conexión con Outlook y limpia COM si fue inicializado"""
        self.outlook = None
        self.namespace = None
        self.sent_folder = None
        
        # Limpiar COM si fue inicializado en este thread
        if self.com_initialized:
            try:
                pythoncom.CoUninitialize()
                current_app.logger.debug("✓ COM desincializado")
            except Exception as e:
                current_app.logger.debug(f"Error desincializando COM: {str(e)}")


def get_outlook_service():
    """
    Obtiene una instancia del servicio de Outlook
    
    Returns:
        OutlookService: Instancia del servicio
    """
    return OutlookService()
