"""
Universal Financial Reporting Engine

A schema-agnostic system for automated financial analysis and reporting.
"""

__version__ = "2.0.0"
__author__ = "Financial Reporting Engine Contributors"
__license__ = "MIT"

# Core modules
from .input_adapter import InputAdapter
from .canonical_format import CanonicalConverter
from .metric_registry import MetricClassifier
from .generic_variance import calculate_variance
from .chart_generator import generate_charts
from .pdf_report_builder import build_pdf_report

__all__ = [
    'InputAdapter',
    'CanonicalConverter',
    'MetricClassifier',
    'calculate_variance',
    'generate_charts',
    'build_pdf_report',
]
