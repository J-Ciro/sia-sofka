"""Report factory for creating report generators using Registry Pattern.

This implementation follows the Open/Closed Principle (OCP) by allowing
new report formats to be registered without modifying the factory.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Type, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from app.factories.pdf_generator import PDFReportGenerator
    from app.factories.html_generator import HTMLReportGenerator
    from app.factories.json_generator import JSONReportGenerator


class ReportFormat(str, Enum):
    """Report format enumeration."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"


class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a report from data.
        
        Args:
            data: Report data dictionary
        
        Returns:
            Dictionary with 'content', 'filename', and 'content_type'
        """
        pass


class ReportFactory:
    """Factory for creating report generators using Registry Pattern.
    
    New generators can be registered using the @register decorator
    without modifying this class.
    """
    
    _registry: Dict[str, Type[ReportGenerator]] = {}
    _instances: Dict[str, ReportGenerator] = {}  # Cache for singleton instances
    
    @classmethod
    def register(cls, format_name: str) -> Callable[[Type[ReportGenerator]], Type[ReportGenerator]]:
        """Decorator to register a report generator class.
        
        Args:
            format_name: Format name (e.g., 'pdf', 'html', 'json')
        
        Usage:
            @ReportFactory.register('pdf')
            class PDFReportGenerator(ReportGenerator):
                ...
        """
        def decorator(generator_class: Type[ReportGenerator]) -> Type[ReportGenerator]:
            cls._registry[format_name.lower()] = generator_class
            return generator_class
        return decorator
    
    @classmethod
    def create_generator(cls, format: str | ReportFormat) -> "ReportGenerator":
        """Create a report generator based on format.
        
        Uses registry pattern to look up generator class dynamically.
        Implements singleton pattern to reuse generator instances.
        
        Args:
            format: Report format (pdf, html, json)
        
        Returns:
            Report generator instance
        
        Raises:
            ValueError: If format is not supported
        """
        format_str = format.value if isinstance(format, ReportFormat) else format.lower()
        
        # Check if format is registered
        if format_str not in cls._registry:
            raise ValueError(
                f"Unsupported report format: {format_str}. "
                f"Available formats: {', '.join(cls._registry.keys())}"
            )
        
        # Return cached instance if available (singleton pattern)
        if format_str not in cls._instances:
            generator_class = cls._registry[format_str]
            cls._instances[format_str] = generator_class()
        
        return cls._instances[format_str]
    
    @classmethod
    def get_registered_formats(cls) -> list[str]:
        """Get list of all registered report formats.
        
        Returns:
            List of format names
        """
        return list(cls._registry.keys())


