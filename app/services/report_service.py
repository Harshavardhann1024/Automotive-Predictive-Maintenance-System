import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

class ReportService:
    @staticmethod
    async def generate_fleet_report(data: dict, report_type: str) -> BytesIO:
        """Generate a PDF report for the fleet."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Fleet Report: {report_type}", styles['Title']))
        elements.append(Spacer(1, 12))

        # Metadata
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Summary Table
        table_data = [
            ["Metric", "Value"],
            ["Total Readings", str(data.get("total_readings", 0))],
            ["Total Anomalies", str(data.get("total_anomalies", 0))],
            ["Anomaly Rate", f"{data.get('anomaly_rate', 0)}%"]
        ]
        
        t = Table(table_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
