"""PDF report generator using ReportLab."""

from typing import Dict, Any
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from app.factories.report_factory import ReportGenerator, ReportFactory


@ReportFactory.register('pdf')  # type: ignore[misc]
class PDFReportGenerator(ReportGenerator):
    """PDF report generator implementation."""
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a PDF report from data.
        
        Args:
            data: Report data dictionary
        
        Returns:
            Dictionary with PDF content, filename, and content_type
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a237e"),
            spaceAfter=30,
        )
        
        # Add title
        if "estudiante" in data:
            estudiante = data["estudiante"]
            title_text = f"Reporte Académico - {estudiante.get('nombre', '')} {estudiante.get('apellido', '')}"
        elif "subject" in data:
            subject = data["subject"]
            title_text = f"Reporte de Notas - {subject.get('nombre', '')}"
        else:
            title_text = "Reporte Académico"
        
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Add student information if present
        if "estudiante" in data:
            estudiante = data["estudiante"]
            info_data = [
                ["Código Institucional:", estudiante.get("codigo_institucional", "N/A")],
                ["Programa Académico:", estudiante.get("programa_academico", "N/A")],
            ]
            info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
            info_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Add subjects/grades table
        if "subjects" in data:
            # Student report
            table_data = [["Materia", "Código", "Créditos", "Promedio"]]
            for subject_info in data["subjects"]:
                subject = subject_info.get("subject", {})
                average = subject_info.get("average")
                table_data.append([
                    subject.get("nombre", "N/A"),
                    subject.get("codigo_institucional", "N/A"),
                    str(subject.get("numero_creditos", "N/A")),
                    f"{average:.2f}" if average else "N/A",
                ])
        elif "students" in data:
            # Subject report
            table_data = [["Estudiante", "Código", "Promedio"]]
            for student_info in data["students"]:
                estudiante = student_info.get("estudiante", {})
                average = student_info.get("average")
                table_data.append([
                    f"{estudiante.get('nombre', '')} {estudiante.get('apellido', '')}",
                    estudiante.get("codigo_institucional", "N/A"),
                    f"{average:.2f}" if average else "N/A",
                ])
        else:
            table_data = [["No hay datos disponibles"]]
        
        table = Table(table_data, colWidths=[2.5 * inch, 2 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(table)
        
        # Add general average if present
        if "subjects" in data and "general_average" in data and data["general_average"] is not None:
            story.append(Spacer(1, 0.3 * inch))
            general_avg_style = ParagraphStyle(
                "GeneralAverage",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#1a237e"),
                spaceAfter=10,
            )
            general_avg_text = f"Promedio General del Semestre: {data['general_average']:.2f}"
            story.append(Paragraph(general_avg_text, general_avg_style))
        
        # Add footer
        story.append(Spacer(1, 0.3 * inch))
        footer_text = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        story.append(Paragraph(footer_text, styles["Normal"]))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if "estudiante" in data:
            codigo = data["estudiante"].get("codigo_institucional", "report")
            filename = f"reporte_estudiante_{codigo}_{timestamp}.pdf"
        elif "subject" in data:
            codigo = data["subject"].get("codigo_institucional", "report")
            filename = f"reporte_materia_{codigo}_{timestamp}.pdf"
        else:
            filename = f"reporte_{timestamp}.pdf"
        
        return {
            "content": buffer.getvalue(),
            "filename": filename,
            "content_type": "application/pdf",
        }


