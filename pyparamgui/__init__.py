"""Top-level package for PyParamGUI."""

from __future__ import annotations

__author__ = """Anmol Bhatia"""
__email__ = "anmolbhatia05@gmail.com"
__version__ = "0.0.1"

from pyparamgui.widget import setup_widget_observer
from pyparamgui.widget import widget

__all__ = ["widget", "setup_widget_observer"]

"""
Package Usage:
    # considering that each command is run in a separate jupyter notebook cell

    %env ANYWIDGET_HMR=1

    from pyparamgui import widget, setup_widget_observer

    widget

    setup_widget_observer()
"""
