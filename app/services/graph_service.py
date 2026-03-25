"""
Servicio de integración con Microsoft Graph API (OAuth2)
Permite que cada usuario sincronice sus propios correos con sus credenciales
"""
import requests
import json
from datetime import datetime, timedelta
from flask import current_app
from msal import ConfidentialClientApplication
import logging

logger = logging.getLogger(__name__)

class GraphService:
    """Servicio para interactuar con Microsoft Graph API"""
    
    def __init__(self, user=None):
        """
        Inicializa el servicio Graph
        
        Args:
            user: Objeto Usuario con tokens de autenticación
        """
        self.user = user
        self.access_token = user.access_token if user else None
        self.graph_endpoint = current_app.config['MICROSOFT_GRAPH_API_ENDPOINT']
        self.client_id = current_app.config['MICROSOFT_CLIENT_ID']
        self.client_secret = current_app.config['MICROSOFT_CLIENT_SECRET']
        self.tenant_id = current_app.config['MICROSOFT_TENANT_ID']
        self.redirect_uri = current_app.config['MICROSOFT_REDIRECT_URI']
    
    @staticmethod
    def get_msal_app():
        """
        Obtiene la aplicación MSAL configurada para autenticación OAuth2
        
        Returns:
            ConfidentialClientApplication: Instancia MSAL (para aplicación servidor)
        """
        return ConfidentialClientApplication(
            client_id=current_app.config['MICROSOFT_CLIENT_ID'],
            client_credential=current_app.config['MICROSOFT_CLIENT_SECRET'],
            authority=f"{current_app.config['MICROSOFT_AUTH_ENDPOINT']}/{current_app.config['MICROSOFT_TENANT_ID']}"
        )
    
    @staticmethod
    def get_auth_url():
        """
        Genera la URL de autenticación de Microsoft para que el usuario inicie sesión
        
        Returns:
            str: URL de autorización
        """
        app = GraphService.get_msal_app()
        auth_url = app.get_authorization_request_url(
            scopes=current_app.config['MICROSOFT_GRAPH_SCOPES'],
            redirect_uri=current_app.config['MICROSOFT_REDIRECT_URI']
        )
        return auth_url
    
    @staticmethod
    def acquire_token_by_auth_code(auth_code):
        """
        Intercambia el código de autorización por token de acceso
        
        Args:
            auth_code (str): Código de autorización de Microsoft
            
        Returns:
            dict: Token response con access_token, refresh_token, etc.
        """
        app = GraphService.get_msal_app()
        token_response = app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=current_app.config['MICROSOFT_GRAPH_SCOPES'],
            redirect_uri=current_app.config['MICROSOFT_REDIRECT_URI']
        )
        return token_response
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Renueva el access token usando el refresh token
        
        Args:
            refresh_token (str): Refresh token
            
        Returns:
            dict: Nuevo token response
        """
        app = GraphService.get_msal_app()
        token_response = app.acquire_token_by_refresh_token(
            refresh_token=refresh_token,
            scopes=current_app.config['MICROSOFT_GRAPH_SCOPES']
        )
        return token_response
    
    def _ensure_valid_token(self):
        """
        Verifica si el token es válido, lo renueva si es necesario
        
        Returns:
            bool: True si el token es válido o fue renovado exitosamente
        """
        if not self.user or not self.user.access_token:
            return False
        
        # Verificar si el token está próximo a expirar (5 minutos antes)
        if self.user.token_expires_at:
            time_buffer = datetime.utcnow() + timedelta(minutes=5)
            if self.user.token_expires_at <= time_buffer and self.user.refresh_token:
                # Intentar renovar el token
                token_response = self.refresh_access_token(self.user.refresh_token)
                
                if 'access_token' in token_response:
                    # Actualizar los tokens en el usuario
                    from app.models import db
                    self.user.access_token = token_response['access_token']
                    if 'refresh_token' in token_response:
                        self.user.refresh_token = token_response['refresh_token']
                    
                    # Calcular nueva fecha de expiración
                    expires_in = token_response.get('expires_in', 3600)
                    self.user.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    db.session.commit()
                    
                    self.access_token = token_response['access_token']
                    logger.info(f"Token renovado para usuario {self.user.id}")
                    return True
                else:
                    logger.error(f"Error renovando token para usuario {self.user.id}: {token_response}")
                    return False
        
        return True
    
    def get_user_info(self):
        """
        Obtiene información del usuario autenticado de Microsoft
        
        Returns:
            dict: Información del usuario (id, mail, displayName, etc.)
        """
        if not self._ensure_valid_token():
            return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f'{self.graph_endpoint}/me',
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo info del usuario: {str(e)}")
            return None
    
    def get_sent_emails(self, limit=50, filter_query=None):
        """
        Obtiene los correos ENVIADOS del usuario desde Microsoft Graph
        Utiliza la carpeta 'Sent Items' de Outlook
        
        Args:
            limit (int): Número máximo de correos a obtener
            filter_query (str, optional): Filtro OData (ej: "startsWith(subject, 'Test')")
            
        Returns:
            list: Lista de diccionarios con información de correos
        """
        if not self._ensure_valid_token():
            return []
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Obtener correos de la carpeta "Sent Items"
            # Usar /mailFolders/sentitems/messages para obtener solo enviados
            url = f'{self.graph_endpoint}/me/mailFolders/sentitems/messages'
            
            params = {
                '$top': limit,
                '$orderby': 'sentDateTime desc',  # Ordenar por fecha descendente
                '$select': 'id,subject,from,toRecipients,ccRecipients,sentDateTime,receivedDateTime,bodyPreview,hasAttachments,importance'
            }
            
            if filter_query:
                params['$filter'] = filter_query
            
            response = requests.get(
                url,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            emails = []
            
            for msg in data.get('value', []):
                email_data = self._extract_email_data(msg)
                emails.append(email_data)
            
            logger.info(f"Se obtuvieron {len(emails)} correos enviados para usuario {self.user.id if self.user else 'desconocido'}")
            return emails
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo correos: {str(e)}")
            return []
    
    def get_inbox_emails(self, limit=50, filter_query=None):
        """
        Obtiene los correos de la bandeja de entrada
        
        Args:
            limit (int): Número máximo de correos a obtener
            filter_query (str, optional): Filtro OData
            
        Returns:
            list: Lista de diccionarios con información de correos
        """
        if not self._ensure_valid_token():
            return []
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            url = f'{self.graph_endpoint}/me/mailFolders/inbox/messages'
            
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,from,toRecipients,ccRecipients,sentDateTime,receivedDateTime,bodyPreview,hasAttachments,importance'
            }
            
            if filter_query:
                params['$filter'] = filter_query
            
            response = requests.get(
                url,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            emails = []
            
            for msg in data.get('value', []):
                email_data = self._extract_email_data(msg, is_sent=False)
                emails.append(email_data)
            
            logger.info(f"Se obtuvieron {len(emails)} correos de entrada para usuario {self.user.id if self.user else 'desconocido'}")
            return emails
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo correos de entrada: {str(e)}")
            return []
    
    @staticmethod
    def _extract_email_data(msg, is_sent=True):
        """
        Extrae datos de un mensaje de Microsoft Graph
        
        Args:
            msg (dict): Objeto de mensaje de Microsoft Graph
            is_sent (bool): Si es correo enviado o recibido
            
        Returns:
            dict: Diccionario con datos del correo
        """
        # Obtener remitente
        from_addr = msg.get('from', {})
        sender_data = from_addr.get('emailAddress', {})
        sender = sender_data.get('address', 'Unknown')
        sender_name = sender_data.get('name', sender)
        
        # Obtener destinatarios
        recipients = []
        for rcpt in msg.get('toRecipients', []):
            rcpt_data = rcpt.get('emailAddress', {})
            recipients.append({
                'email': rcpt_data.get('address', ''),
                'name': rcpt_data.get('name', ''),
                'type': 'to'
            })
        
        # Agregar CC si existen
        for rcpt in msg.get('ccRecipients', []):
            rcpt_data = rcpt.get('emailAddress', {})
            recipients.append({
                'email': rcpt_data.get('address', ''),
                'name': rcpt_data.get('name', ''),
                'type': 'cc'
            })
        
        # Obtener fecha
        sent_date = msg.get('sentDateTime')
        received_date = msg.get('receivedDateTime', sent_date)
        
        # Convertir a datetime si es string
        if isinstance(sent_date, str):
            sent_date = datetime.fromisoformat(sent_date.replace('Z', '+00:00'))
        if isinstance(received_date, str):
            received_date = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
        
        return {
            'microsoft_graph_id': msg.get('id'),
            'subject': msg.get('subject', '(sin asunto)'),
            'sender': sender,
            'sender_name': sender_name,
            'recipients': recipients,
            'sent_date': sent_date,
            'received_date': received_date,
            'body_snippet': msg.get('bodyPreview', '')[:current_app.config.get('EMAIL_BODY_SNIPPET_LENGTH', 200)],
            'has_attachments': msg.get('hasAttachments', False),
            'importance': msg.get('importance', 'normal').capitalize(),
            'is_sent': is_sent
        }
    
    def get_email_by_id(self, email_id):
        """
        Obtiene un correo específico por ID
        
        Args:
            email_id (str): ID del correo en Microsoft Graph
            
        Returns:
            dict: Información del correo completa
        """
        if not self._ensure_valid_token():
            return None
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                f'{self.graph_endpoint}/me/messages/{email_id}',
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo correo {email_id}: {str(e)}")
            return None
    
    def send_email(self, to_recipients, subject, body, cc_recipients=None, attachments=None):
        """
        Envía un correo a través de Microsoft Graph
        
        Args:
            to_recipients (list): Lista de direcciones de correo destinatarios
            subject (str): Asunto del correo
            body (str): Cuerpo del correo
            cc_recipients (list, optional): Lista de CC
            attachments (list, optional): Lista de archivos adjuntos
            
        Returns:
            bool: True si se envió exitosamente
        """
        if not self._ensure_valid_token():
            return False
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Construir estructura de mensaje
        message = {
            'subject': subject,
            'body': {
                'contentType': 'HTML',
                'content': body
            },
            'toRecipients': [
                {'emailAddress': {'address': addr}} for addr in to_recipients
            ]
        }
        
        if cc_recipients:
            message['ccRecipients'] = [
                {'emailAddress': {'address': addr}} for addr in cc_recipients
            ]
        
        try:
            # Enviar el correo
            response = requests.post(
                f'{self.graph_endpoint}/me/sendMail',
                headers=headers,
                json={'message': message, 'saveToSentItems': True}
            )
            response.raise_for_status()
            logger.info(f"Correo enviado exitosamente por usuario {self.user.id if self.user else 'desconocido'}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando correo: {str(e)}")
            return False
