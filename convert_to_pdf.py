#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir archivos Markdown a PDF
Utiliza reportlab para generación de PDFs de alta calidad
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
import re
from datetime import datetime

# Archivos a convertir
FILES_TO_CONVERT = [
    "MANUAL_COMPLETO_CLIENTE.md",
    "GUIA_ADMINISTRADOR_DISTRIBUCION.md",
    "CLIENT_INSTALLATION.md",
    "QUICK_START_CLIENT.md",
    "CLIENT_ARCHITECTURE.md"
]

class MarkdownToPDF:
    def __init__(self):
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Encabezados
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=4,
            spaceBefore=4,
            fontName='Helvetica-Bold'
        ))
        
        # Párrafos
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Código
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            fontName='Courier',
            fontSize=8,
            textColor=colors.HexColor('#c7254e'),
            leftIndent=20,
            spaceBefore=4,
            spaceAfter=4
        ))

    def parse_markdown(self, content):
        """Convertir contenido markdown a elementos de ReportLab"""
        elements = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Encabezado H1
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                elements.append(Paragraph(title, self.styles['CustomTitle']))
                elements.append(Spacer(1, 0.2*inch))
                i += 1
                
            # Encabezado H2
            elif line.startswith('## '):
                heading = line.replace('## ', '').strip()
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(heading, self.styles['CustomHeading2']))
                elements.append(Spacer(1, 0.1*inch))
                i += 1
                
            # Encabezado H3
            elif line.startswith('### '):
                heading = line.replace('### ', '').strip()
                elements.append(Paragraph(heading, self.styles['CustomHeading3']))
                elements.append(Spacer(1, 0.05*inch))
                i += 1
                
            # Bloque de código
            elif line.startswith('```'):
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                code_content = '\n'.join(code_lines).strip()
                if code_content:
                    # Escapar caracteres especiales
                    code_content = code_content.replace('<', '&lt;').replace('>', '&gt;')
                    code_text = code_content[:500]  # Limitar longitud
                    elements.append(Paragraph(f"<font face='Courier' size='8'>{code_text}</font>", 
                                            self.styles['CodeBlock']))
                i += 1
                
            # Separador
            elif line.startswith('---'):
                elements.append(Spacer(1, 0.1*inch))
                i += 1
                
            # Párrafo normal
            elif line.strip():
                # Limpiar caracteres especiales
                para_text = line.strip()
                para_text = para_text.replace('<', '&lt;').replace('>', '&gt;')
                
                # Reemplazar marcas markdown inline simples
                para_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', para_text)
                para_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', para_text)
                para_text = re.sub(r'`(.*?)`', r'<font face="Courier" size="9">\1</font>', para_text)
                
                try:
                    elements.append(Paragraph(para_text, self.styles['CustomBody']))
                except:
                    # Si hay error, agregar como texto plano
                    elements.append(Paragraph(line.strip(), self.styles['CustomBody']))
                i += 1
                
            else:
                i += 1
        
        return elements

    def convert_file(self, markdown_path, pdf_path):
        """Convertir un archivo markdown a PDF"""
        print(f"📄 Convirtiendo: {markdown_path}")
        
        try:
            # Leer archivo markdown
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Crear documento PDF
            self.story = []
            self.story.extend(self.parse_markdown(content))
            
            # Agregar pie de página con fecha
            self.story.append(Spacer(1, 0.3*inch))
            footer_text = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            self.story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Crear PDF
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=Path(markdown_path).stem
            )
            
            doc.build(self.story)
            print(f"✓ PDF creado: {pdf_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error convirtiendo {markdown_path}: {e}")
            return False

def main():
    """Función principal"""
    print("="*60)
    print("Convertidor de Markdown a PDF")
    print("="*60)
    
    # Obtener directorio actual
    current_dir = Path.cwd()
    
    converter = MarkdownToPDF()
    successful = 0
    failed = 0
    
    for markdown_file in FILES_TO_CONVERT:
        markdown_path = current_dir / markdown_file
        pdf_path = current_dir / f"{Path(markdown_file).stem}.pdf"
        
        if markdown_path.exists():
            if converter.convert_file(str(markdown_path), str(pdf_path)):
                successful += 1
            else:
                failed += 1
        else:
            print(f"✗ Archivo no encontrado: {markdown_path}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Resumen: {successful} exitosos, {failed} fallidos")
    print("="*60)
    
    # Listar archivos PDF generados
    print("\n📦 Archivos PDF generados:")
    for markdown_file in FILES_TO_CONVERT:
        pdf_file = current_dir / f"{Path(markdown_file).stem}.pdf"
        if pdf_file.exists():
            size_kb = pdf_file.stat().st_size / 1024
            print(f"  ✓ {pdf_file.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()
