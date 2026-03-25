#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crear un PDF índice que sirva como puerta de entrada a toda la documentación
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import os

def create_index_pdf():
    """Crear PDF índice con tabla de contenidos"""
    
    pdf_path = "INDICE_DOCUMENTACION.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Índice de Documentación - Outlook Sync Client"
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    # Contenido
    story = []
    
    # Título
    story.append(Paragraph("OUTLOOK SYNC CLIENT", title_style))
    story.append(Paragraph("Suite Completa de Documentación", subtitle_style))
    
    # Información general
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Índice de Documentación", heading_style))
    
    story.append(Paragraph(
        "Este paquete contiene la documentación completa del cliente Outlook Sync para sincronización "
        "de correos en entornos multi-usuario de red local. Los documentos están ordenados por audiencia "
        "y caso de uso.",
        body_style
    ))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de documentos
    story.append(Paragraph("Documentos Incluidos", heading_style))
    
    # Datos de la tabla
    data = [
        ['Documento', 'Tamaño', 'Audiencia', 'Descripción'],
        [
            '<font size="10"><b>MANUAL_COMPLETO_CLIENTE.pdf</b></font>',
            '27.7 KB',
            '<font size="9">Usuarios Finales</font>',
            '<font size="9">Manual comprensivo en español con instrucciones de instalación, '
            'configuración, ejecución, troubleshooting y FAQs. Ideal para usuarios que instalarán '
            'el cliente en sus PCs.</font>'
        ],
        [
            '<font size="10"><b>GUIA_ADMINISTRADOR_DISTRIBUCION.pdf</b></font>',
            '11.4 KB',
            '<font size="9">Administradores TI</font>',
            '<font size="9">Guía para administradores sobre distribución en masa, instalación remota, '
            'monitoreo de clientes, gestión de soporte y configuración de sistemas de tickets.</font>'
        ],
        [
            '<font size="10"><b>CLIENT_INSTALLATION.pdf</b></font>',
            '9.0 KB',
            '<font size="9">Tecnicos/Administradores</font>',
            '<font size="9">Guía técnica detallada de instalación con pasos específicos, configuración '
            'de dependencias y troubleshooting técnico avanzado.</font>'
        ],
        [
            '<font size="10"><b>CLIENT_ARCHITECTURE.pdf</b></font>',
            '9.8 KB',
            '<font size="9">Desarrolladores/Arquitectos</font>',
            '<font size="9">Especificaciones técnicas de la arquitectura, flujos de comunicación, '
            'esquema de base de datos y detalles de implementación.</font>'
        ],
        [
            '<font size="10"><b>QUICK_START_CLIENT.pdf</b></font>',
            '4.3 KB',
            '<font size="9">Usuarios Avanzados</font>',
            '<font size="9">Guía rápida de inicio para usuarios que ya tienen conocimientos técnicos '
            'o experiencia previa con el sistema.</font>'
        ],
    ]
    
    # Estilo de tabla
    table = Table(data, colWidths=[2.0*inch, 0.9*inch, 1.3*inch, 1.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(table)
    
    # Sección de recomendaciones
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Guía de Lectura Recomendada", heading_style))
    
    story.append(Paragraph("<b>Para usuarios finales:</b>", body_style))
    story.append(Paragraph("1. Empezar con <b>QUICK_START_CLIENT.pdf</b> para una introducción rápida", body_style))
    story.append(Paragraph("2. Leer <b>MANUAL_COMPLETO_CLIENTE.pdf</b> para instrucciones detalladas", body_style))
    story.append(Paragraph("3. Consultar la sección de troubleshooting si encontrás problemas", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Para administradores TI:</b>", body_style))
    story.append(Paragraph("1. Leer <b>GUIA_ADMINISTRADOR_DISTRIBUCION.pdf</b> para estrategia de distribución", body_style))
    story.append(Paragraph("2. Usar <b>CLIENT_INSTALLATION.pdf</b> como referencia técnica", body_style))
    story.append(Paragraph("3. Implementar scripts de monitoreo y soporte según la guía", body_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Para desarrolladores:</b>", body_style))
    story.append(Paragraph("1. Consultar <b>CLIENT_ARCHITECTURE.pdf</b> para entender la arquitectura", body_style))
    story.append(Paragraph("2. Revisar <b>CLIENT_INSTALLATION.pdf</b> para detalles técnicos", body_style))
    
    # Pie de página
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        f"<font size='8' color='#666666'>Generado: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}<br/>"
        "Email Tracker - Sistema de Sincronización Outlook Multi-Usuario</font>",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8)
    ))
    
    # Crear PDF
    doc.build(story)
    print(f"✓ PDF índice creado: {pdf_path}")
    
    # Mostrar tamaño
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"  Tamaño: {size_kb:.1f} KB")

if __name__ == "__main__":
    create_index_pdf()
