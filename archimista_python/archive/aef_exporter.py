"""
AEF Exporter — thin compatibility shim.

All logic has been moved into the aef_exporter/ package.
This module re-exports the AEFExporter class for backwards compatibility.
"""

from archimista_python.archive.aef_exporter import AEFExporter, APP_VERSION

__all__ = ['AEFExporter', 'APP_VERSION']
