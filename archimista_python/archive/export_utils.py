import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from docx import Document
from docx.shared import Pt

def generate_fond_pdf(fond):
    """Genera un PDF con l'inventario del fondo e delle sue unità."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Stili personalizzati
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#0d6efd")
    )
    
    header_style = styles['Heading2']
    body_style = styles['BodyText']
    
    elements = []
    
    # Titolo del Fondo
    elements.append(Paragraph(f"Inventario: {fond.name}", title_style))
    elements.append(Spacer(1, 12))
    
    # Metadati del Fondo
    if fond.abstract:
        elements.append(Paragraph("Abstract", header_style))
        elements.append(Paragraph(fond.abstract, body_style))
        elements.append(Spacer(1, 12))
        
    if fond.history:
        elements.append(Paragraph("Storia Archivistica", header_style))
        elements.append(Paragraph(fond.history, body_style))
        elements.append(Spacer(1, 12))
        
    # Unità collegate
    elements.append(Paragraph("Unità d'Archivio", header_style))
    elements.append(Spacer(1, 6))
    
    data = [["Segnatura", "Titolo", "Tipo"]]
    for unit in fond.units.all():
        data.append([
            unit.reference_number or "-",
            unit.title or "Senza Titolo",
            unit.unit_type or "Unità"
        ])
        
    table = Table(data, colWidths=[100, 300, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_fond_docx(fond):
    """Genera un file DOCX (RTF-compatible) con l'inventario del fondo."""
    doc = Document()
    
    # Titolo
    doc.add_heading(f"Inventario: {fond.name}", 0)
    
    # Metadati
    if fond.abstract:
        doc.add_heading('Abstract', level=1)
        doc.add_paragraph(fond.abstract)
        
    if fond.history:
        doc.add_heading('Storia Archivistica', level=1)
        doc.add_paragraph(fond.history)
        
    # Unità
    doc.add_heading("Unità d'Archivio", level=1)
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Segnatura'
    hdr_cells[1].text = 'Titolo'
    hdr_cells[2].text = 'Tipo'
    
    for unit in fond.units.all():
        row_cells = table.add_row().cells
        row_cells[0].text = unit.reference_number or "-"
        row_cells[1].text = unit.title or "Senza Titolo"
        row_cells[2].text = unit.unit_type or "Unità"
        
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
