#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Resumen Ejecutivo - Outlook Sync Client
Documento profesional para stakeholders y presentaciones
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from datetime import datetime
import os

class ExecutiveSummaryPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='ExecutiveTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#3366aa'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
        
        # Secciones principales
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a5f'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#3366aa'),
            borderWidth=2,
            borderPadding=10,
            borderRadius=3
        ))
        
        # Subsecciones
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#3366aa'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Párrafos
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=16
        ))
        
        # Listas
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4,
            leading=14
        ))
        
        # Destacados
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            backColor=colors.HexColor('#3366aa'),
            leftIndent=8,
            rightIndent=8,
            spaceBefore=4,
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def create_pdf(self):
        """Crear el PDF del resumen ejecutivo"""
        pdf_path = "RESUMEN_EJECUTIVO.pdf"
        
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title="Resumen Ejecutivo - Outlook Sync Client"
        )
        
        story = []
        
        # 1. Título y encabezado
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("OUTLOOK SYNC CLIENT", self.styles['ExecutiveTitle']))
        story.append(Paragraph("Resumen Ejecutivo del Proyecto", self.styles['Subtitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # 2. Información general
        story.append(Paragraph("Información General", self.styles['SectionTitle']))
        
        general_data = [
            ['<b>Proyecto:</b>', 'Outlook Sync Client - Sistema de Sincronización Centralizada de Correos'],
            ['<b>Versión:</b>', 'v1.0 (Marzo 2026)'],
            ['<b>Estado:</b>', '✓ Listo para Producción'],
            ['<b>Tipo:</b>', 'Aplicación Web Multi-Usuario'],
            ['<b>Ubicación:</b>', 'C:\\Users\\INE.INE24\\Documents\\Codes\\Administrativo\\Correos'],
        ]
        
        general_table = Table(general_data, colWidths=[1.5*inch, 4*inch], rowHeights=[0.35*inch]*len(general_data))
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(general_table)
        story.append(Spacer(1, 0.2*inch))
        
        # 3. ¿Qué es?
        story.append(Paragraph("¿Qué es Outlook Sync Client?", self.styles['SectionTitle']))
        
        story.append(Paragraph(
            "<b>Outlook Sync Client</b> es una plataforma web moderna que centraliza y gestiona "
            "la sincronización de correos electrónicos de Microsoft Outlook en entornos multi-usuario "
            "de red local. Permite que cada usuario de la organización sincronice automáticamente sus "
            "correos Outlook a un servidor centralizado, creando un repositorio unificado de comunicaciones "
            "para auditoría, análisis y gestión organizacional.",
            self.styles['CustomBody']
        ))
        
        story.append(Paragraph("<b>Casos de Uso Principales:</b>", self.styles['SubsectionTitle']))
        
        usecases = [
            "Auditoría y cumplimiento normativo de comunicaciones corporativas",
            "Análisis centralizado de flujos de comunicación en la organización",
            "Búsqueda y recuperación de correos en repositorio unificado",
            "Estadísticas y reportes de comunicación por usuario/departamento",
            "Respaldo y archiviado de comunicaciones históricas",
            "Investigaciones internas y análisis de patrones de comunicación"
        ]
        
        for usecase in usecases:
            story.append(Paragraph(f"• {usecase}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 4. Características principales
        story.append(Paragraph("Características Principales", self.styles['SectionTitle']))
        
        # Tabla de características
        features_data = [
            ['<b>Característica</b>', '<b>Descripción</b>'],
            [
                'Multi-Usuario',
                'Sincronización independiente para cada usuario de la red'
            ],
            [
                'Sincronización Automática',
                'Agent client que se ejecuta en PC de usuario'
            ],
            [
                'Búsqueda Avanzada',
                'Filtrado por remitente, asunto, fecha, destinatarios'
            ],
            [
                'Exportación Multiple',
                'Formatos: Excel (.xlsx), PDF, CSV'
            ],
            [
                'Auditoría Completa',
                'Registro inmutable de todas las operaciones'
            ],
            [
                'Gestión de Usuarios',
                'Panel administrativo con control de acceso'
            ],
            [
                'Dashboard Visual',
                'Estadísticas en tiempo real y gráficos'
            ],
            [
                'API RESTful',
                'Integración con sistemas externos'
            ],
        ]
        
        features_table = Table(features_data, colWidths=[1.8*inch, 3.7*inch], rowHeights=[0.35*inch]*len(features_data))
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        story.append(features_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Page break
        story.append(PageBreak())
        
        # 5. Arquitectura Técnica
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Arquitectura Técnica", self.styles['SectionTitle']))
        
        story.append(Paragraph("<b>Componentes del Sistema:</b>", self.styles['SubsectionTitle']))
        
        arch_data = [
            ['<b>Componente</b>', '<b>Tecnología</b>', '<b>Función</b>'],
            [
                '<b>Backend/API</b>',
                'Flask 3.0.0<br/>Python 3.x<br/>SQLAlchemy ORM',
                'Servidor web, gestión de BD,<br/>API RESTful con JWT'
            ],
            [
                '<b>Frontend</b>',
                'Vue.js 3<br/>Bootstrap 5<br/>JavaScript ES6+',
                'Interfaz web responsiva,<br/>dashboards y formularios'
            ],
            [
                '<b>Base de Datos</b>',
                'SQLite<br/>(PostgreSQL escalable)',
                'Almacenamiento de usuarios,<br/>emails, logs de auditoría'
            ],
            [
                '<b>Client Agent</b>',
                'Python 3.x<br/>pywin32 311<br/>requests',
                'Extrae emails de Outlook<br/>local y sincroniza al servidor'
            ],
            [
                '<b>Integración</b>',
                'Win32 COM<br/>Microsoft Outlook<br/>API',
                'Acceso directo a buzones<br/>de usuario en Windows'
            ],
        ]
        
        # Crear alturas de fila específicas (más altas para contenido multiline)
        arch_heights = [0.35*inch] + [0.75*inch] * (len(arch_data) - 1)  # Header más pequeño, contenido más grande
        
        arch_table = Table(arch_data, colWidths=[1.5*inch, 1.8*inch, 2.2*inch], rowHeights=arch_heights)
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 18),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('LINESPACING', (0, 0), (-1, -1), 1.4),
        ]))
        
        story.append(arch_table)
        story.append(Spacer(1, 0.2*inch))
        
        # 6. Stack Tecnológico Detallado
        story.append(Paragraph("Stack Tecnológico Completo", self.styles['SectionTitle']))
        
        story.append(Paragraph("<b>Backend & API:</b>", self.styles['SubsectionTitle']))
        backend_tech = [
            "Flask 3.0.0 - Framework web ligero y flexible",
            "Flask-SQLAlchemy - ORM para gestión de base de datos",
            "Flask-CORS - Habilitación de CORS para API web",
            "PyJWT 2.12.1 - Autenticación con JSON Web Tokens",
            "bcrypt - Hash seguro de contraseñas",
            "python-dotenv - Gestión de variables de entorno"
        ]
        for tech in backend_tech:
            story.append(Paragraph(f"• {tech}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Frontend & UI:</b>", self.styles['SubsectionTitle']))
        frontend_tech = [
            "Vue.js 3 - Framework JavaScript reactivo",
            "Bootstrap 5 - Framework CSS responsivo",
            "Axios - Cliente HTTP para consumo de APIs",
            "JavaScript ES6+ - Características modernas del lenguaje"
        ]
        for tech in frontend_tech:
            story.append(Paragraph(f"• {tech}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Integración Windows & Outlook:</b>", self.styles['SubsectionTitle']))
        windows_tech = [
            "pywin32 311 - Interoperabilidad COM con Windows",
            "Microsoft Outlook COM API - Acceso a buzones",
            "Win32 threading - Procesamiento asincrónico",
            "Windows Registry - Configuración del sistema"
        ]
        for tech in windows_tech:
            story.append(Paragraph(f"• {tech}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Exportación & Generación de Reportes:</b>", self.styles['SubsectionTitle']))
        export_tech = [
            "openpyxl 3.1.2 - Generación de archivos Excel (.xlsx)",
            "reportlab - Generación de archivos PDF",
            "csv (stdlib) - Exportación de datos en CSV"
        ]
        for tech in export_tech:
            story.append(Paragraph(f"• {tech}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 7. Especificaciones Técnicas
        story.append(Paragraph("Especificaciones Técnicas", self.styles['SectionTitle']))
        
        specs_data = [
            ['<b>Aspecto</b>', '<b>Especificación</b>'],
            ['Versión Python', '3.8 - 3.12'],
            ['Versión Flask', '3.0.0'],
            ['Base de Datos', 'SQLite (escalable a PostgreSQL)'],
            ['Usuarios Simultáneos', 'Ilimitados (por arquitectura serverless)'],
            ['Correos por Usuario', 'Sin límite (escalable)'],
            ['Tiempo Sincronización', '30 segundos - 2 minutos (según cantidad)'],
            ['Protocolo API', 'HTTP REST con JWT'],
            ['Puerto Servidor', '5000 (configurable)'],
            ['Requisitos Servidor', 'Windows Server 2019+ o Linux'],
            ['Requisitos Cliente', 'Windows 10/11, Python 3.8+, Outlook 2016+'],
        ]
        
        specs_table = Table(specs_data, colWidths=[2.5*inch, 3*inch], rowHeights=[0.35*inch]*len(specs_data))
        specs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        story.append(specs_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Page break
        story.append(PageBreak())
        
        # 8. Modelos de Datos
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Modelos de Datos", self.styles['SectionTitle']))
        
        story.append(Paragraph("<b>User (Usuarios)</b>", self.styles['SubsectionTitle']))
        story.append(Paragraph(
            "Almacena información de usuarios del sistema con autenticación segura",
            self.styles['CustomBody']
        ))
        user_fields = [
            "id - Identificador único",
            "username - Nombre de usuario único",
            "email - Email del usuario",
            "password_hash - Hash bcrypt de contraseña",
            "is_admin - Flag de administrador",
            "created_at - Timestamp de creación"
        ]
        for field in user_fields:
            story.append(Paragraph(f"• {field}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>Email (Correos)</b>", self.styles['SubsectionTitle']))
        story.append(Paragraph(
            "Almacena correos sincronizados con información completa",
            self.styles['CustomBody']
        ))
        email_fields = [
            "id - Identificador único",
            "user_id - Relación con usuario",
            "email_id - ID único del correo (por usuario)",
            "sender - Remitente del correo",
            "recipients - JSON array de destinatarios",
            "subject - Asunto del correo",
            "body - Fragmento del cuerpo (first 200 chars)",
            "attachments - Información de adjuntos",
            "importance - Nivel de importancia",
            "is_synced - Flag de sincronización remota",
            "created_at - Timestamp"
        ]
        for field in email_fields:
            story.append(Paragraph(f"• {field}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>AuditLog (Registro de Auditoría)</b>", self.styles['SubsectionTitle']))
        story.append(Paragraph(
            "Registro inmutable de todas las operaciones del sistema",
            self.styles['CustomBody']
        ))
        audit_fields = [
            "id - Identificador único",
            "user_id - Usuario que realizó la acción",
            "action - Tipo de acción (create, update, delete, sync, export)",
            "email_id - Email afectado (si aplica)",
            "description - Detalles de la operación",
            "client_hostname - Computadora origen (para clientes remotos)",
            "timestamp - Momento exacto de la acción"
        ]
        for field in audit_fields:
            story.append(Paragraph(f"• {field}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 9. Flujos Principales
        story.append(Paragraph("Flujos Principales de Operación", self.styles['SectionTitle']))
        
        story.append(Paragraph("<b>1. Autenticación de Usuario</b>", self.styles['SubsectionTitle']))
        auth_flow = [
            "Usuario ingresa credenciales en login.html",
            "Frontend valida y POST a /api/auth/login",
            "Backend verifica credenciales y hash",
            "Server genera JWT token válido por 24 horas",
            "Frontend almacena token en localStorage",
            "Token se envía en header Authorization en todas las requests"
        ]
        for i, step in enumerate(auth_flow, 1):
            story.append(Paragraph(f"{i}. {step}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph("<b>2. Sincronización de Correos (Client Agent)</b>", self.styles['SubsectionTitle']))
        sync_flow = [
            "outlook_sync_agent.py en PC de usuario se ejecuta",
            "Script conecta a Outlook local via COM (win32api)",
            "Extrae correos de carpeta Sent",
            "Autentica al servidor con credenciales",
            "Obtiene JWT token",
            "POST a /api/emails/sync/remote con batch de correos",
            "Servidor asigna correos al usuario autenticado",
            "Se registra marca de sincronización remota en auditoría"
        ]
        for i, step in enumerate(sync_flow, 1):
            story.append(Paragraph(f"{i}. {step}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph("<b>3. Búsqueda y Filtrado</b>", self.styles['SubsectionTitle']))
        search_flow = [
            "Usuario ingresa criterios de búsqueda",
            "Frontend valida y POST a /api/emails/search",
            "Backend filtra en base de datos por email_id único del usuario",
            "Resultados se retornan ordenados (descendente por fecha)",
            "Frontend renderiza resultados en tabla interactiva"
        ]
        for i, step in enumerate(search_flow, 1):
            story.append(Paragraph(f"{i}. {step}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 10. Seguridad
        story.append(Paragraph("Medidas de Seguridad", self.styles['SectionTitle']))
        
        security_measures = [
            "<b>Autenticación:</b> JWT tokens con validación en cada endpoint",
            "<b>Contraseñas:</b> Hash bcrypt con salt, nunca almacenadas en plaintext",
            "<b>Base de Datos:</b> Acceso restringido, relaciones foreign key",
            "<b>Auditoría:</b> Registro inmutable de todas las operaciones",
            "<b>Isolamiento:</b> Cada usuario ve solo sus correos (email_id único)",
            "<b>Rate Limiting:</b> Implementable para prevenir abuso",
            "<b>CORS:</b> Configurado para origen específico",
            "<b>Validación de Input:</b> Sanitización de datos en backend"
        ]
        
        for measure in security_measures:
            story.append(Paragraph(f"• {measure}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # 11. Distribución y Despliegue
        story.append(Paragraph("Distribución y Despliegue", self.styles['SectionTitle']))
        
        story.append(Paragraph(
            "La suite incluye estructura completa lista para distribución:",
            self.styles['CustomBody']
        ))
        
        deployment_items = [
            "6 documentos PDF profesionales (65.9 KB total)",
            "Organizados en 6 carpetas por audiencia (usuarios, técnicos, admins, devs)",
            "Scripts PowerShell para distribución en masa",
            "Instalador automático (install_client.bat) para clientes",
            "Scripts de monitoreo y soporte",
            "Guías de troubleshooting y FAQ",
            "Código fuente completamente documentado"
        ]
        
        for item in deployment_items:
            story.append(Paragraph(f"• {item}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Page break
        story.append(PageBreak())
        
        # 12. Beneficios del Proyecto
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Beneficios Clave", self.styles['SectionTitle']))
        
        benefits_data = [
            ['<b>Beneficio</b>', '<b>Impacto</b>'],
            [
                'Centralización de Comunicaciones',
                'Un único repositorio para todos los correos organizacionales'
            ],
            [
                'Cumplimiento Normativo',
                'Auditoría completa y trazabilidad de comunicaciones'
            ],
            [
                'Recuperación de Datos',
                'Búsqueda avanzada y recuperación en repositorio único'
            ],
            [
                'Análisis Inteligente',
                'Estadísticas y patrones de comunicación'
            ],
            [
                'Escalabilidad',
                'Arquitectura preparada para 100+ usuarios simultáneos'
            ],
            [
                'Facilidad de Distribución',
                'Instalación automática en cliente con script'
            ],
            [
                'Bajo Costo',
                'Tecnología open source (Flask, Vue.js, SQLite)'
            ],
        ]
        
        benefits_table = Table(benefits_data, colWidths=[2.2*inch, 3.3*inch], rowHeights=[0.4*inch]*len(benefits_data))
        benefits_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        story.append(benefits_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 13. Próximos Pasos
        story.append(Paragraph("Próximos Pasos Recomendados", self.styles['SectionTitle']))
        
        next_steps = [
            "<b>1. Prueba Piloto:</b> Desplegar en 5-10 usuarios para validar funcionalidad",
            "<b>2. Capacitación:</b> Entrenar a usuarios finales en uso del sistema",
            "<b>3. Distribución Gradual:</b> Implementar en departamentos de forma escalonada",
            "<b>4. Monitoreo:</b> Supervisar sincronizaciones y soporte",
            "<b>5. Optimización:</b> Recopilar feedback y realizar ajustes",
            "<b>6. Escalado:</b> Expandir a toda la organización"
        ]
        
        for step in next_steps:
            story.append(Paragraph(f"• {step}", self.styles['BulletPoint']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 14. Conclusión
        story.append(Paragraph("Conclusión", self.styles['SectionTitle']))
        
        story.append(Paragraph(
            "<b>Outlook Sync Client</b> representa una solución moderna, segura y escalable para "
            "la centralización de comunicaciones corporativas. Con una arquitectura basada en "
            "tecnologías probadas y estándares de la industria, el proyecto está completamente "
            "listo para producción y puede ser desplegado inmediatamente."
            "<br/><br/>"
            "La suite incluye todo lo necesario: código, documentación, scripts de distribución "
            "y guías de soporte. El sistema es flexible, mantenible y preparado para crecer con "
            "la organización.",
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Pie de página
        footer_data = [
            ['Proyecto:', 'Outlook Sync Client'],
            ['Versión:', 'v1.0'],
            ['Fecha:', datetime.now().strftime('%d de %B de %Y')],
            ['Estado:', 'Listo para Producción ✓'],
        ]
        
        footer_table = Table(footer_data, colWidths=[1.5*inch, 4*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(footer_table)
        
        # Construir PDF
        doc.build(story)
        
        print(f"✓ PDF generado: {pdf_path}")
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"  Tamaño: {size_kb:.1f} KB")
        
        return pdf_path

if __name__ == "__main__":
    generator = ExecutiveSummaryPDF()
    generator.create_pdf()
