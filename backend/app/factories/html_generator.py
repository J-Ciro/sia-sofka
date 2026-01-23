"""HTML report generator."""

from typing import Dict, Any
from datetime import datetime
from jinja2 import Template
from app.factories.report_factory import ReportGenerator, ReportFactory


@ReportFactory.register('html')  # type: ignore[misc]
class HTMLReportGenerator(ReportGenerator):
    """HTML report generator implementation."""
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an HTML report from data.
        
        Args:
            data: Report data dictionary
        
        Returns:
            Dictionary with HTML content, filename, and content_type
        """
        # HTML template
        template_str = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte Académico</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a237e;
            border-bottom: 3px solid #1a237e;
            padding-bottom: 10px;
        }
        .info-section {
            margin: 20px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .info-row {
            display: flex;
            margin: 10px 0;
        }
        .info-label {
            font-weight: bold;
            width: 200px;
            color: #555;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background-color: #1a237e;
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 12px;
        }
        .average {
            font-weight: bold;
            color: #1a237e;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            {% if estudiante %}
                Reporte Académico - {{ estudiante.nombre }} {{ estudiante.apellido }}
            {% elif subject %}
                Reporte de Notas - {{ subject.nombre }}
            {% else %}
                Reporte Académico
            {% endif %}
        </h1>
        
        {% if estudiante %}
        <div class="info-section">
            <div class="info-row">
                <span class="info-label">Código Institucional:</span>
                <span>{{ estudiante.codigo_institucional }}</span>
            </div>
            {% if estudiante.programa_academico %}
            <div class="info-row">
                <span class="info-label">Programa Académico:</span>
                <span>{{ estudiante.programa_academico }}</span>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        {% if subjects %}
        <table>
            <thead>
                <tr>
                    <th>Materia</th>
                    <th>Código</th>
                    <th>Créditos</th>
                    <th>Promedio</th>
                </tr>
            </thead>
            <tbody>
                {% for subject_info in subjects %}
                <tr>
                    <td>{{ subject_info.subject.nombre }}</td>
                    <td>{{ subject_info.subject.codigo_institucional }}</td>
                    <td>{{ subject_info.subject.numero_creditos }}</td>
                    <td class="average">
                        {% if subject_info.average %}
                            {{ "%.2f"|format(subject_info.average) }}
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% elif students %}
        <table>
            <thead>
                <tr>
                    <th>Estudiante</th>
                    <th>Código</th>
                    <th>Promedio</th>
                </tr>
            </thead>
            <tbody>
                {% for student_info in students %}
                <tr>
                    <td>{{ student_info.estudiante.nombre }} {{ student_info.estudiante.apellido }}</td>
                    <td>{{ student_info.estudiante.codigo_institucional }}</td>
                    <td class="average">
                        {% if student_info.average %}
                            {{ "%.2f"|format(student_info.average) }}
                        {% else %}
                            N/A
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
        
        {% if general_average %}
        <div class="info-section" style="margin-top: 30px; background-color: #e3f2fd; border-left: 4px solid #1a237e;">
            <div class="info-row">
                <span class="info-label" style="font-size: 16px;">Promedio General del Semestre:</span>
                <span style="font-size: 18px; font-weight: bold; color: #1a237e;">{{ "%.2f"|format(general_average) }}</span>
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            Generado el {{ timestamp }}
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        html_content = template.render(
            estudiante=data.get("estudiante"),
            subject=data.get("subject"),
            subjects=data.get("subjects", []),
            students=data.get("students", []),
            timestamp=timestamp,
        )
        
        # Generate filename
        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
        if "estudiante" in data:
            codigo = data["estudiante"].get("codigo_institucional", "report")
            filename = f"reporte_estudiante_{codigo}_{timestamp_file}.html"
        elif "subject" in data:
            codigo = data["subject"].get("codigo_institucional", "report")
            filename = f"reporte_materia_{codigo}_{timestamp_file}.html"
        else:
            filename = f"reporte_{timestamp_file}.html"
        
        return {
            "content": html_content,
            "filename": filename,
            "content_type": "text/html",
        }


