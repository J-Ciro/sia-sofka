"""JSON report generator."""

import json
from typing import Dict, Any
from datetime import datetime
from app.factories.report_factory import ReportGenerator, ReportFactory


@ReportFactory.register('json')  # type: ignore[misc]
class JSONReportGenerator(ReportGenerator):
    """JSON report generator implementation."""
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a JSON report from data.
        
        Args:
            data: Report data dictionary
        
        Returns:
            Dictionary with JSON content, filename, and content_type
        """
        # Add metadata
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format": "json",
            },
            **data,
        }
        
        # Convert to JSON string
        json_content = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if "estudiante" in data:
            codigo = data["estudiante"].get("codigo_institucional", "report")
            filename = f"reporte_estudiante_{codigo}_{timestamp}.json"
        elif "subject" in data:
            codigo = data["subject"].get("codigo_institucional", "report")
            filename = f"reporte_materia_{codigo}_{timestamp}.json"
        else:
            filename = f"reporte_{timestamp}.json"
        
        return {
            "content": json_content,
            "filename": filename,
            "content_type": "application/json",
        }


