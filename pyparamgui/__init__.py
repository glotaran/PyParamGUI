"""Top-level package for PyParamGUI."""

from __future__ import annotations

__author__ = """Anmol Bhatia"""
__email__ = "anmolbhatia05@gmail.com"
__version__ = "0.0.1"

from pyparamgui.widget import Widget

__all__ = ["Widget"]
"""
Package Usage:
    %env ANYWIDGET_HMR=1
    from pyparamgui import Widget

    widget = Widget()
    widget
"""
