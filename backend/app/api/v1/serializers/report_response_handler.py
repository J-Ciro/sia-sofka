"""Report response handler for different formats (JSON, PDF, HTML)."""

import json
from typing import Dict, Any
from fastapi import Response
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError


class ReportResponseHandler:
    """Handler for report responses in different formats."""

    @staticmethod
    def handle_response(
        report: Dict[str, Any],
        format: str,
        error: Exception | None = None,
        error_type: str | None = None,
    ) -> Response | Dict[str, Any]:
        """Handle report response based on format.
        
        Args:
            report: Report dictionary with 'content', 'content_type', and 'filename'
            format: Report format ('json', 'pdf', 'html')
            error: Exception that occurred (if any)
            error_type: Type of error ('not_found', 'forbidden', 'validation')
            
        Returns:
            Response object for PDF/HTML or dict for JSON
            
        Raises:
            NotFoundError: If error_type is 'not_found'
            ForbiddenError: If error_type is 'forbidden'
            ValidationError: If error_type is 'validation' or other error
        """
        # Handle errors first
        if error:
            error_msg = str(error).lower()
            if error_type == "not_found" or "not found" in error_msg:
                raise NotFoundError("Report", str(error))
            elif error_type == "forbidden" or "not assigned" in error_msg:
                raise ForbiddenError(str(error))
            else:
                raise ValidationError(str(error))

        format_lower = format.lower()

        # Handle JSON format
        if format_lower == "json":
            content = report["content"]
            if isinstance(content, bytes):
                result: Dict[str, Any] = json.loads(content.decode("utf-8"))
                return result
            else:
                result: Dict[str, Any] = json.loads(content)
                return result

        # Handle PDF and HTML formats
        content = report["content"]
        if isinstance(content, str):
            content = content.encode("utf-8")

        return Response(
            content=content,
            media_type=report["content_type"],
            headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'},
        )

