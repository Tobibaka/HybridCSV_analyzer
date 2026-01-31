"""Utility functions for data processing and PDF generation."""
import pandas as pd
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def parse_csv_data(file):
    """
    Parse uploaded CSV file and return DataFrame.
    
    Args:
        file: Uploaded file object
        
    Returns:
        tuple: (DataFrame, error_message)
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read file content and decode
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        # Parse CSV from string
        df = pd.read_csv(StringIO(content))
        
        # Normalize column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Expected columns
        expected_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        
        # Check for required columns
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            return None, f"Missing required columns: {', '.join(missing_cols)}"
        
        # Convert numeric columns
        for col in ['Flowrate', 'Pressure', 'Temperature']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df, None
        
    except Exception as e:
        return None, str(e)


def calculate_summary(df):
    """
    Calculate summary statistics from DataFrame.
    
    Args:
        df: pandas DataFrame with equipment data
        
    Returns:
        dict: Summary statistics
    """
    # Convert numpy types to Python native types for JSON serialization
    def to_native(val):
        if hasattr(val, 'item'):
            return val.item()
        return val
    
    summary = {
        'total_count': int(len(df)),
        'averages': {
            'flowrate': float(round(df['Flowrate'].mean(), 2)),
            'pressure': float(round(df['Pressure'].mean(), 2)),
            'temperature': float(round(df['Temperature'].mean(), 2))
        },
        'max_values': {
            'flowrate': float(round(df['Flowrate'].max(), 2)),
            'pressure': float(round(df['Pressure'].max(), 2)),
            'temperature': float(round(df['Temperature'].max(), 2))
        },
        'min_values': {
            'flowrate': float(round(df['Flowrate'].min(), 2)),
            'pressure': float(round(df['Pressure'].min(), 2)),
            'temperature': float(round(df['Temperature'].min(), 2))
        },
        'type_distribution': {k: int(v) for k, v in df['Type'].value_counts().to_dict().items()},
        'type_averages': {}
    }
    
    # Calculate averages by type
    for eq_type in df['Type'].unique():
        type_df = df[df['Type'] == eq_type]
        summary['type_averages'][eq_type] = {
            'count': int(len(type_df)),
            'avg_flowrate': float(round(type_df['Flowrate'].mean(), 2)),
            'avg_pressure': float(round(type_df['Pressure'].mean(), 2)),
            'avg_temperature': float(round(type_df['Temperature'].mean(), 2))
        }
    
    return summary


def generate_pdf_report(dataset, records):
    """
    Generate PDF report for a dataset.
    
    Args:
        dataset: Dataset model instance
        records: QuerySet of EquipmentRecord
        
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Title
    elements.append(Paragraph("Chemical Equipment Parameter Report", title_style))
    elements.append(Paragraph(f"Dataset: {dataset.name}", heading_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Paragraph(f"Total Records: {dataset.total_records}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Summary section
    summary = dataset.get_summary()
    elements.append(Paragraph("Summary Statistics", heading_style))
    
    if 'averages' in summary:
        avg = summary['averages']
        elements.append(Paragraph(f"Average Flowrate: {avg.get('flowrate', 'N/A')}", normal_style))
        elements.append(Paragraph(f"Average Pressure: {avg.get('pressure', 'N/A')}", normal_style))
        elements.append(Paragraph(f"Average Temperature: {avg.get('temperature', 'N/A')}", normal_style))
    
    elements.append(Spacer(1, 20))
    
    # Type distribution table
    if 'type_distribution' in summary:
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in summary['type_distribution'].items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data, colWidths=[3*inch, 1.5*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(type_table)
    
    elements.append(Spacer(1, 20))
    
    # Equipment data table
    elements.append(Paragraph("Equipment Data", heading_style))
    
    table_data = [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
    for record in records[:50]:  # Limit to 50 records for PDF
        table_data.append([
            record.equipment_name,
            record.equipment_type,
            str(record.flowrate),
            str(record.pressure),
            str(record.temperature)
        ])
    
    # Create table with column widths
    col_widths = [2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch]
    data_table = Table(table_data, colWidths=col_widths)
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(data_table)
    
    if len(records) > 50:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Note: Showing 50 of {len(records)} records", normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
